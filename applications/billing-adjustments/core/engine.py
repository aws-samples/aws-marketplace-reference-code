#!/usr/bin/env python3
"""
Core billing adjustment processing logic - refactored for UI/background use.

Key differences from the CLI scripts:
- Credentials passed in directly (access key / secret key / optional session token)
- Supports dry-run (validation only, no submission)
- Writes each record incrementally (JSONL + CSV) as it is processed/completed,
  rather than writing everything at the end
- Reports progress via a callback so a UI can show live status
"""

import csv
import json
import uuid
import time
import re
import os
from datetime import datetime
from collections import defaultdict

import boto3
from botocore.config import Config
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session as _get_botocore_session

# Defaults (can be overridden via AdjustmentConfig)
BATCH_SIZE = 5

# Per-operation request rates, from the AWS Marketplace Agreement service quotas
# (per AWS account). Each API call path is paced to its OWN documented limit instead
# of a single global rate, so the read paths are not throttled down to the slowest
# (write) limit.
# https://docs.aws.amazon.com/marketplace/latest/developerguide/agreement-service-quotas.html
BATCH_CREATE_CALLS_PER_SECOND = 2               # BatchCreateBillingAdjustmentRequest
GET_CALLS_PER_SECOND = 5                         # GetBillingAdjustmentRequest
LIST_BILLING_ADJUSTMENTS_CALLS_PER_SECOND = 5   # ListBillingAdjustmentRequests
LIST_INVOICE_LINE_ITEMS_CALLS_PER_SECOND = 10   # ListAgreementInvoiceLineItems

# Backwards-compatible global default = the most restrictive path (the write/submit).
# Kept because core/__init__.py re-exports these names and CLI scripts import them.
CALLS_PER_SECOND = BATCH_CREATE_CALLS_PER_SECOND
DELAY_BETWEEN_BATCHES = 1.0 / CALLS_PER_SECOND   # submit pacing (2/s -> 0.5s)

# Per-operation inter-call delays (seconds), derived from the quotas above.
SUBMIT_DELAY = 1.0 / BATCH_CREATE_CALLS_PER_SECOND                                 # 0.50s
GET_DELAY = 1.0 / GET_CALLS_PER_SECOND                                             # 0.20s
LIST_BILLING_ADJUSTMENTS_DELAY = 1.0 / LIST_BILLING_ADJUSTMENTS_CALLS_PER_SECOND   # 0.20s
VALIDATE_DELAY = 1.0 / LIST_INVOICE_LINE_ITEMS_CALLS_PER_SECOND                    # 0.10s

# Status polling. The total budget SCALES with the number of pending requests so a
# large batch is not falsely timed out: one status sweep of N requests already costs
# ~ N / GET_CALLS_PER_SECOND seconds in pacing alone. We allow up to MAX_POLL_SWEEPS
# full sweeps (each followed by a POLL_INTERVAL idle wait), bounded by a floor (so
# small batches behave as before) and an absolute ceiling. See _compute_poll_budget().
POLL_INTERVAL = 60
MIN_POLL_TIME = 600          # floor in seconds (small batches)
MAX_POLL_SWEEPS = 5          # number of full status sweeps to allow
MAX_POLL_TIME_CAP = 7200     # absolute ceiling in seconds (2 hours)
# Back-compat alias; the effective budget is computed per-run in _wait_and_record.
MAX_POLL_TIME = MIN_POLL_TIME
CURRENCY_CODE = "USD"
ADJUSTMENT_REASON = "OTHER"
ENDPOINT_URL = "https://agreement-marketplace.us-east-1.amazonaws.com"
REGION = "us-east-1"

# Required CSV columns (header must contain these)
REQUIRED_COLUMNS = [
    "seller_id",
    "aws_account_id",
    "invoice_id",
    "product_code",
    "month_id",
    "agreement_id",
]
# Amount column may use either of these names
AMOUNT_COLUMN_OPTIONS = ["refund_amount", "SUM of Calculated Refund (T-Y)"]

# Maximum number of digits allowed after the decimal point in a refund amount.
# The billing-adjustment backend rejects amounts with more precision than this
# (USD carries 2 minor-unit digits), so the tool validates it up front instead of
# letting the submission fail server-side.
MAX_AMOUNT_DECIMALS = 2

COL_AGREEMENT_ID = "agreement_id"
COL_INVOICE_ID = "invoice_id"
REVIEW_REASON_COL = "review_reason"

# Values that look like data but are really blanks/errors from exports. Treated as
# missing for agreement_id / invoice_id.
NA_PLACEHOLDERS = {"", "#N/A", "N/A", "NA", "NULL", "NONE", "#REF!", "#VALUE!", "-"}

CLIENT_TOKEN_NAMESPACE = uuid.UUID('12345678-1234-5678-1234-567812345678')

# Error codes / messages that indicate expired or invalid credentials.
# NOTE: AccessDenied/AccessDeniedException is deliberately NOT here. An
# authorization/compliance denial (e.g. "Current identity is not KYC compliant")
# is a per-request rejection, not a credentials problem — re-entering credentials
# can never resolve it. Treating it as a credential error caused an infinite
# "enter fresh credentials" pause loop and hid the real reason. Such errors are
# now surfaced per invoice as VALIDATION_FAILED with the real API message.
CREDENTIAL_ERROR_CODES = [
    'ExpiredTokenException',
    'ExpiredToken',
    'InvalidIdentityToken',
    'InvalidClientTokenId',
    'UnrecognizedClientException',
]
CREDENTIAL_ERROR_MESSAGES = [
    'security token included in the request is invalid',
    'security token included in the request is expired',
    'token has expired',
    'credentials have expired',
    'the security token included in the request is expired',
]


class CredentialsCancelled(Exception):
    """Raised when a job is cancelled while waiting for fresh credentials."""
    pass


def is_credential_error(error):
    """True if an exception looks like an expired/invalid-credentials error."""
    error_code = getattr(error, 'response', {}).get('Error', {}).get('Code', '')
    if error_code in CREDENTIAL_ERROR_CODES:
        return True
    msg = str(error).lower()
    return any(m in msg for m in CREDENTIAL_ERROR_MESSAGES)


def extract_api_error(error):
    """Return (code, message) from a botocore ClientError-style exception, falling
    back to str(error) for the message when the structured fields are absent."""
    err = getattr(error, 'response', {}).get('Error', {})
    return err.get('Code', ''), err.get('Message', '') or str(error)


def is_access_denied(error):
    """True for an authorization/compliance denial (e.g. seller not KYC compliant).
    These are per-request rejections, not credential problems."""
    code, _ = extract_api_error(error)
    return code in ('AccessDenied', 'AccessDeniedException')


def generate_client_token(agreement_id, invoice_id):
    """Deterministic client token for idempotency, built from agreement_id +
    invoice_id only. The same invoice on the same agreement always produces the
    same token, so a refund that has already been submitted will not be created
    again (the API treats the repeated token as the same request). The tool issues
    at most one refund per invoice+agreement."""
    key = f"{agreement_id}:{invoice_id}"
    return str(uuid.uuid5(CLIENT_TOKEN_NAMESPACE, key))


def format_amount(amount_str):
    """Convert '$1,341.70 ' to '1341.70'."""
    return re.sub(r'[$,\s]', '', str(amount_str))


def count_decimal_places(amount_str):
    """Number of digits after the decimal point in a cleaned amount string
    (e.g. '1341.7012' -> 4, '150.00' -> 2, '150' -> 0). Assumes `$`, commas, and
    spaces have already been stripped by format_amount."""
    s = str(amount_str).strip()
    if '.' not in s:
        return 0
    return len(s.split('.', 1)[1])


def build_header_map(headers):
    """Map a normalized (stripped + lowercased) column name to the actual header as
    written in the file, so columns can be matched case-insensitively (e.g. both
    `refund_amount` and `Refund_amount` resolve to the same column). When two
    headers normalize to the same name, the first occurrence wins."""
    header_map = {}
    for h in (headers or []):
        if h is None:
            continue
        key = h.strip().lower()
        if key not in header_map:
            header_map[key] = h
    return header_map


def resolve_amount_column(header_map):
    """Return the actual header matching one of AMOUNT_COLUMN_OPTIONS
    case-insensitively, or None if none is present."""
    for option in AMOUNT_COLUMN_OPTIONS:
        actual = header_map.get(option.strip().lower())
        if actual is not None:
            return actual
    return None


def get_field(row, header_map, name, default=''):
    """Read a value from a csv.DictReader row by canonical column name, matching the
    file's header case-insensitively."""
    actual = header_map.get((name or '').strip().lower())
    if actual is None:
        return default
    return row.get(actual, default)


def validate_file_format(filepath):
    """
    Validate that the uploaded CSV has the required columns and at least one data row.
    Returns (is_valid, message, details_dict).
    """
    details = {
        "required_columns": REQUIRED_COLUMNS,
        "amount_column_options": AMOUNT_COLUMN_OPTIONS,
        "found_columns": [],
        "missing_columns": [],
        "amount_column_found": None,
        "row_count": 0,
        "row_issues": [],
    }

    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            details["found_columns"] = headers

            if not headers:
                return False, "File is empty or has no header row.", details

            header_map = build_header_map(headers)

            # Check required columns (case-insensitive)
            missing = [c for c in REQUIRED_COLUMNS if c.strip().lower() not in header_map]
            details["missing_columns"] = missing

            # Check amount column (case-insensitive)
            amount_col = resolve_amount_column(header_map)
            details["amount_column_found"] = amount_col

            if missing:
                return False, f"Missing required column(s): {', '.join(missing)}", details
            if not amount_col:
                return False, (
                    f"Missing amount column. Expected one of: "
                    f"{', '.join(AMOUNT_COLUMN_OPTIONS)}"
                ), details

            # Validate rows
            row_count = 0
            for i, row in enumerate(reader, start=2):  # line 2 = first data row
                if not any((v or '').strip() for v in row.values()):
                    continue  # skip blank lines
                row_count += 1
                issues = []
                if not (get_field(row, header_map, COL_AGREEMENT_ID) or '').strip():
                    issues.append("missing agreement_id")
                if not (get_field(row, header_map, COL_INVOICE_ID) or '').strip():
                    issues.append("missing invoice_id")
                amt = format_amount(row.get(amount_col, '0'))
                try:
                    if float(amt) <= 0:
                        issues.append(f"amount must be > 0 (got '{row.get(amount_col)}')")
                    elif count_decimal_places(amt) > MAX_AMOUNT_DECIMALS:
                        issues.append(
                            f"amount has more than {MAX_AMOUNT_DECIMALS} decimal places "
                            f"(got '{row.get(amount_col)}')"
                        )
                except ValueError:
                    issues.append(f"invalid amount '{row.get(amount_col)}'")
                if issues:
                    details["row_issues"].append({"line": i, "issues": issues})

            details["row_count"] = row_count

            if row_count == 0:
                return False, "File has headers but no data rows.", details

            if details["row_issues"]:
                n = len(details["row_issues"])
                return False, f"Found {n} row(s) with issues. See details.", details

        return True, f"File is valid. {row_count} data row(s) ready to process.", details

    except Exception as e:
        return False, f"Could not read file: {e}", details


def load_csv(filepath):
    """Load and parse CSV file into normalized row dicts."""
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        header_map = build_header_map(headers)
        amount_col = resolve_amount_column(header_map)
        if not amount_col:
            raise ValueError(
                f"Could not find amount column. Expected one of: {AMOUNT_COLUMN_OPTIONS}"
            )
        for row in reader:
            if not (get_field(row, header_map, COL_INVOICE_ID) or '').strip():
                continue
            rows.append({
                'agreement_id': (get_field(row, header_map, COL_AGREEMENT_ID) or '').strip(),
                'invoice_id': (get_field(row, header_map, COL_INVOICE_ID) or '').strip(),
                'amount': format_amount(row.get(amount_col, '0')),
                'aws_account_id': (get_field(row, header_map, 'aws_account_id') or '').strip(),
                'seller_id': (get_field(row, header_map, 'seller_id') or '').strip(),
                'month': (get_field(row, header_map, 'month_id') or '').strip(),
                'product_code': (get_field(row, header_map, 'product_code') or '').strip(),
            })
    return rows


def _is_missing_value(value):
    """True if a value is blank or a known placeholder (e.g. #N/A)."""
    return (value or "").strip().upper() in NA_PLACEHOLDERS


def classify_input_rows(filepath):
    """Split an input refund CSV (same format as the submit file) into rows that are
    safe to process and rows that need human review, preserving the original columns.

    Returns (valid_records, review_rows, original_columns, amount_col):
      - valid_records: normalized dicts ready to process. Each has agreement_id,
        invoice_id, amount, aws_account_id, seller_id, month, product_code, and
        'original' (the untouched input row). Only the FIRST occurrence of a given
        <agreement_id, invoice_id> combination is included here.
      - review_rows: the original input row dicts for anything that should NOT be
        submitted, each with an added 'review_reason' column explaining why:
          * missing or invalid agreement_id (blank or a placeholder like #N/A)
          * missing or invalid invoice_id
          * invalid or non-positive amount
          * duplicate <agreement, invoice> (a later repeat of a combo already kept)
      - original_columns: the header from the input file (order preserved).
      - amount_col: which amount column was detected.

    Raises ValueError if no recognized amount column is present.
    """
    valid_records, review_rows = [], []
    seen_combos = set()
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        header_map = build_header_map(columns)
        amount_col = resolve_amount_column(header_map)
        if not amount_col:
            raise ValueError(
                f"Could not find amount column. Expected one of: {AMOUNT_COLUMN_OPTIONS}"
            )
        for row in reader:
            if not any((v or '').strip() for v in row.values()):
                continue  # skip fully blank lines

            agreement_id = (get_field(row, header_map, COL_AGREEMENT_ID) or '').strip()
            invoice_id = (get_field(row, header_map, COL_INVOICE_ID) or '').strip()
            raw_amount = row.get(amount_col, '')
            amount = format_amount(raw_amount)

            reasons = []
            if _is_missing_value(agreement_id):
                reasons.append("missing or invalid agreement_id")
            if _is_missing_value(invoice_id):
                reasons.append("missing or invalid invoice_id")
            try:
                if float(amount) <= 0:
                    reasons.append(f"amount must be > 0 (got '{raw_amount}')")
                elif count_decimal_places(amount) > MAX_AMOUNT_DECIMALS:
                    reasons.append(
                        f"amount has more than {MAX_AMOUNT_DECIMALS} decimal places "
                        f"(got '{raw_amount}')"
                    )
            except (ValueError, TypeError):
                reasons.append(f"invalid amount '{raw_amount}'")

            if not reasons:
                combo = (agreement_id, invoice_id)
                if combo in seen_combos:
                    reasons.append("duplicate <agreement, invoice> (kept the first occurrence)")
                else:
                    seen_combos.add(combo)

            if reasons:
                rr = dict(row)
                rr[REVIEW_REASON_COL] = "; ".join(reasons)
                review_rows.append(rr)
            else:
                valid_records.append({
                    'agreement_id': agreement_id,
                    'invoice_id': invoice_id,
                    'amount': amount,
                    'aws_account_id': (get_field(row, header_map, 'aws_account_id') or '').strip(),
                    'seller_id': (get_field(row, header_map, 'seller_id') or '').strip(),
                    'month': (get_field(row, header_map, 'month_id') or '').strip(),
                    'product_code': (get_field(row, header_map, 'product_code') or '').strip(),
                    'original': dict(row),
                })
    return valid_records, review_rows, columns, amount_col


def find_duplicate_invoices(rows):
    """Find invoice IDs that appear in multiple agreements."""
    invoice_agreements = defaultdict(list)
    for row in rows:
        invoice_agreements[row['invoice_id']].append(row['agreement_id'])
    return {inv: agmts for inv, agmts in invoice_agreements.items() if len(agmts) > 1}


def group_rows_by_invoice_occurrence(rows):
    """Group rows into phases based on invoice occurrence order."""
    invoice_count = defaultdict(int)
    phases = defaultdict(list)
    for row in rows:
        invoice_id = row['invoice_id']
        invoice_count[invoice_id] += 1
        phases[invoice_count[invoice_id]].append(row)
    max_phase = max(phases.keys()) if phases else 0
    return [phases[i] for i in range(1, max_phase + 1)]


def group_by_agreement(rows):
    grouped = defaultdict(list)
    for row in rows:
        if row['agreement_id']:
            grouped[row['agreement_id']].append(row)
    return grouped


def create_batches(grouped_rows, batch_size):
    batches = []
    for agreement_id, entries in grouped_rows.items():
        for i in range(0, len(entries), batch_size):
            batches.append({'agreement_id': agreement_id, 'entries': entries[i:i + batch_size]})
    return batches


def _compute_poll_budget(n_pending):
    """Total seconds to wait for `n_pending` requests to reach a terminal status.

    The budget scales with the batch so large runs are not falsely timed out: a single
    status sweep of N requests costs ~ N / GET_CALLS_PER_SECOND seconds of pacing
    alone, so we budget MAX_POLL_SWEEPS sweeps plus their inter-sweep idle waits,
    bounded by MIN_POLL_TIME (floor) and MAX_POLL_TIME_CAP (ceiling)."""
    sweep_cost = n_pending / GET_CALLS_PER_SECOND
    budget = MAX_POLL_SWEEPS * (sweep_cost + POLL_INTERVAL)
    return min(MAX_POLL_TIME_CAP, max(MIN_POLL_TIME, int(budget)))


class _AmountTally:
    """Wraps a record writer to also accumulate dollar totals by outcome, so the
    run summary can report $ submitted / completed / failed alongside the counts.
    Delegates .write() to the wrapped writer unchanged."""

    def __init__(self, inner):
        self._inner = inner
        self._submitted = 0.0
        self._completed = 0.0
        self._failed = 0.0

    def write(self, record):
        status = record.get("status")
        try:
            amt = float(record.get("amount") or 0)
        except (TypeError, ValueError):
            amt = 0.0
        if status in ("COMPLETED", "ERROR", "TIMEOUT"):
            self._submitted += amt
        if status == "COMPLETED":
            self._completed += amt
        if status in ("VALIDATION_FAILED", "SUBMIT_FAILED"):
            self._failed += amt
        self._inner.write(record)

    def summary(self):
        return {
            "currency": CURRENCY_CODE,
            "submitted": round(self._submitted, 2),
            "completed": round(self._completed, 2),
            "failed": round(self._failed, 2),
        }


class RecordWriter:
    """Writes each processed record incrementally to JSONL and CSV."""

    CSV_FIELDS = [
        "timestamp", "phase", "agreement_id", "invoice_id", "amount",
        "status", "billing_adjustment_request_id", "message"
    ]

    def __init__(self, jsonl_path, csv_path):
        self.jsonl_path = jsonl_path
        self.csv_path = csv_path
        # Initialize CSV with header
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
        # Touch JSONL
        open(self.jsonl_path, 'w', encoding='utf-8').close()

    def write(self, record):
        """Append a single record to both JSONL and CSV, flushing immediately."""
        record = {**record}
        record.setdefault("timestamp", datetime.now().isoformat())

        with open(self.jsonl_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())

        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_FIELDS)
            writer.writerow({k: record.get(k, "") for k in self.CSV_FIELDS})
            f.flush()
            os.fsync(f.fileno())


class AdjustmentProcessor:
    """
    Processes billing adjustments with credentials supplied directly.
    Supports dry-run and incremental record writing with progress callbacks.
    """

    def __init__(self, access_key=None, secret_key=None, session_token=None,
                 endpoint_url=ENDPOINT_URL, region=REGION,
                 progress_cb=None, log_cb=None, cancel_check=None,
                 request_credentials=None, managed_credentials=False,
                 assume_role_arn=None, assume_role_external_id=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.endpoint_url = endpoint_url
        self.region = region
        self.progress_cb = progress_cb or (lambda **kw: None)
        self.log_cb = log_cb or (lambda msg: None)
        self.cancel_check = cancel_check or (lambda: False)
        # Callback that BLOCKS until the user supplies fresh credentials.
        # Should return a dict {access_key, secret_key, session_token} or None
        # if the job was cancelled while waiting.
        self.request_credentials = request_credentials
        # When True, credentials come from the default AWS provider chain
        # (e.g. an IAM instance/task role). No keys are supplied or requested;
        # the role's credentials are refreshed automatically by AWS.
        self.managed_credentials = managed_credentials
        # When set, assume this IAM role (in another account) and use its
        # temporary credentials. Auto-refreshed before expiry. The base
        # credentials (to call STS) come from the default provider chain.
        self.assume_role_arn = assume_role_arn
        self.assume_role_external_id = assume_role_external_id
        self.client = self._create_client()

    def _assumed_role_session(self):
        """Build a boto3 Session backed by auto-refreshing assume-role creds."""
        base = boto3.Session()  # base creds from default chain (e.g. task role)
        sts = base.client('sts', region_name=self.region)

        assume_kwargs = {
            'RoleArn': self.assume_role_arn,
            'RoleSessionName': 'billing-adjustments',
        }
        if self.assume_role_external_id:
            assume_kwargs['ExternalId'] = self.assume_role_external_id

        def _refresh():
            resp = sts.assume_role(**assume_kwargs)
            c = resp['Credentials']
            return {
                'access_key': c['AccessKeyId'],
                'secret_key': c['SecretAccessKey'],
                'token': c['SessionToken'],
                'expiry_time': c['Expiration'].isoformat(),
            }

        creds = RefreshableCredentials.create_from_metadata(
            metadata=_refresh(),
            refresh_using=_refresh,
            method='sts-assume-role',
        )
        botocore_session = _get_botocore_session()
        botocore_session._credentials = creds
        botocore_session.set_config_variable('region', self.region)
        return boto3.Session(botocore_session=botocore_session)

    def _create_client(self):
        config = Config(retries={'max_attempts': 3, 'mode': 'adaptive'})
        if self.assume_role_arn:
            # Cross-account: assume a role (in the account that owns the
            # agreements) and use its auto-refreshing temporary credentials.
            session = self._assumed_role_session()
            return session.client(
                'marketplace-agreement',
                config=config,
                endpoint_url=self.endpoint_url,
                region_name=self.region,
            )
        if self.managed_credentials:
            # Default credential chain (IAM role attached to the compute).
            return boto3.client(
                'marketplace-agreement',
                config=config,
                endpoint_url=self.endpoint_url,
                region_name=self.region,
            )
        kwargs = {
            'aws_access_key_id': self.access_key,
            'aws_secret_access_key': self.secret_key,
            'config': config,
            'endpoint_url': self.endpoint_url,
            'region_name': self.region,
        }
        if self.session_token:
            kwargs['aws_session_token'] = self.session_token
        return boto3.client('marketplace-agreement', **kwargs)

    def _apply_credentials(self, creds):
        """Swap in fresh credentials and rebuild the client."""
        self.access_key = creds.get('access_key', self.access_key)
        self.secret_key = creds.get('secret_key', self.secret_key)
        self.session_token = creds.get('session_token')
        self.client = self._create_client()

    def _call(self, operation_name, **kwargs):
        """
        Invoke a client operation. Handles credential errors two ways:
        - managed_credentials (IAM role): rebuild the client (the role's
          credentials refresh automatically) and retry a bounded number of times.
        - user-supplied credentials: pause via request_credentials, rebuild with
          the fresh keys, and retry.
        Other errors propagate to the caller.
        """
        managed_retries = 0
        while True:
            try:
                return getattr(self.client, operation_name)(**kwargs)
            except Exception as e:
                if is_credential_error(e):
                    if self.managed_credentials:
                        if managed_retries < 3:
                            managed_retries += 1
                            time.sleep(2)
                            self.client = self._create_client()
                            continue
                        raise
                    if self.request_credentials is not None:
                        self.log_cb("AWS credentials appear to be expired or invalid. "
                                    "Waiting for fresh credentials...")
                        new_creds = self.request_credentials()
                        if not new_creds:
                            raise CredentialsCancelled()
                        self._apply_credentials(new_creds)
                        self.log_cb("Fresh credentials received. Resuming...")
                        continue
                raise

    def _log(self, msg):
        self.log_cb(msg)

    def validate_invoice(self, agreement_id, invoice_id, requested_amount):
        """Validate invoice via ListAgreementInvoiceLineItems with pagination."""
        try:
            summaries = []
            next_token = None
            while True:
                params = {
                    'agreementId': agreement_id,
                    'groupBy': 'INVOICE_ID',
                    'invoiceId': invoice_id,
                }
                if next_token:
                    params['nextToken'] = next_token
                response = self._call('list_agreement_invoice_line_items', **params)
                summaries.extend(response.get('agreementInvoiceLineItemGroupSummaries', []))
                if summaries:
                    break
                next_token = response.get('nextToken')
                if not next_token:
                    break

            if not summaries:
                return False, None, f"Invoice {invoice_id} not found for agreement {agreement_id}"

            summary = summaries[0]
            max_amount = summary.get('pricingCurrencyAmount', {}).get('maxAdjustmentAmount')
            if max_amount is None:
                invoice_type = summary.get('invoiceType', 'UNKNOWN')
                return False, None, f"Invoice {invoice_id} is type {invoice_type} (no maxAdjustmentAmount)"
            if float(requested_amount) > float(max_amount):
                return False, max_amount, f"Requested {requested_amount} exceeds max {max_amount}"
            return True, max_amount, None
        except CredentialsCancelled:
            raise
        except Exception as e:
            return False, None, str(e)

    def _create_batch_entries(self, entries):
        return [
            {
                'agreementId': e['agreement_id'],
                'originalInvoiceId': e['invoice_id'],
                'adjustmentAmount': e['amount'],
                'currencyCode': CURRENCY_CODE,
                'adjustmentReasonCode': ADJUSTMENT_REASON,
                'clientToken': generate_client_token(e['agreement_id'], e['invoice_id']),
            }
            for e in entries
        ]

    def get_adjustment_status(self, agreement_id, request_id):
        try:
            response = self._call(
                'get_billing_adjustment_request',
                billingAdjustmentRequestId=request_id,
                agreementId=agreement_id,
            )
            return response.get('status'), response.get('statusMessage')
        except CredentialsCancelled:
            raise
        except Exception as e:
            return 'ERROR', str(e)

    def get_adjustment_detail(self, agreement_id, request_id):
        """GetBillingAdjustmentRequest — full detail for one request."""
        response = self._call(
            'get_billing_adjustment_request',
            billingAdjustmentRequestId=request_id,
            agreementId=agreement_id,
        )
        return {k: v for k, v in response.items() if k != 'ResponseMetadata'}

    def list_adjustment_requests(self, agreement_ids, statuses=None,
                                 catalog='AWSMarketplace',
                                 created_after=None, created_before=None,
                                 max_results=None):
        """Query ListBillingAdjustmentRequests across one or more agreement IDs and
        one or more statuses. The API takes a single agreementId and a single status
        per call, so we loop over the combinations and aggregate (de-duplicated).

        Note: this operation lists requests for a specific agreement, and the service
        does NOT support an `agreementType` filter here (it returns a
        "combination of filters is not supported" error), so it is not sent.

        created_after / created_before are datetime objects (boto3 serializes them to
        the epoch number the API expects). Returns (items, errors)."""
        statuses = statuses or [None]      # None => no status filter
        seen, items, errors = set(), [], []
        for aid in agreement_ids:
            for st in statuses:
                token = None
                while True:
                    params = {'agreementId': aid}
                    if catalog:
                        params['catalog'] = catalog
                    if st:
                        params['status'] = st
                    if created_after:
                        params['createdAfter'] = created_after
                    if created_before:
                        params['createdBefore'] = created_before
                    if max_results:
                        params['maxResults'] = max_results
                    if token:
                        params['nextToken'] = token
                    try:
                        resp = self._call('list_billing_adjustment_requests', **params)
                    except CredentialsCancelled:
                        raise
                    except Exception as e:
                        errors.append({'agreementId': aid, 'status': st, 'error': str(e)})
                        break
                    for it in resp.get('items', []):
                        key = (it.get('agreementId'), it.get('billingAdjustmentRequestId'))
                        if key in seen:
                            continue
                        seen.add(key)
                        items.append(it)
                    token = resp.get('nextToken')
                    if not token or max_results:
                        break
                    time.sleep(LIST_BILLING_ADJUSTMENTS_DELAY)
        return items, errors

    def reconcile_refunds(self, records):
        """Reconcile a refund input file against what the service actually has.

        `records` is a list of dicts, each with:
            - 'agreement_id'  : the agreement id from the input row
            - 'invoice_id'    : the original invoice id from the input row
            - 'original'      : the original input row (dict) preserved verbatim

        For each distinct agreement id we call ListBillingAdjustmentRequests (all
        statuses, no created/status filter) and build a map of
        originalInvoiceId -> [request items]. For each input row:
          - if its invoice id is present in that agreement's list, we call
            GetBillingAdjustmentRequest for each matching request id and add the
            full detail(s) to `processed`.
          - otherwise the original row is added to `not_processed` unchanged.

        If ListBillingAdjustmentRequests fails for an agreement, every input row
        for that agreement is treated as not processed and the error is recorded.

        Returns (processed_details, not_processed_rows, errors) where:
          - processed_details : list of dicts (GetBillingAdjustmentRequest output,
            with an extra 'matchedInvoiceId' echoing the input invoice id)
          - not_processed_rows: list of the original input row dicts
          - errors            : list of {'agreementId', 'error'} (and per-row
            'invoiceId' when a Get call fails)
        """
        processed, not_processed, errors = [], [], []

        # Group input rows by agreement id (preserve order of first appearance).
        by_agreement = defaultdict(list)
        order = []
        for rec in records:
            aid = (rec.get('agreement_id') or '').strip()
            if aid not in by_agreement:
                order.append(aid)
            by_agreement[aid].append(rec)

        for aid in order:
            rows = by_agreement[aid]
            if not aid:
                # No agreement id on these rows -> cannot reconcile.
                for rec in rows:
                    not_processed.append(rec.get('original', {}))
                errors.append({'agreementId': '', 'error': 'Missing agreement_id on input row(s)'})
                continue

            self._log(f"Listing adjustment requests for agreement {aid}...")
            items, list_errors = self.list_adjustment_requests([aid], statuses=None)
            time.sleep(LIST_BILLING_ADJUSTMENTS_DELAY)  # pace per-agreement list calls to quota
            if list_errors:
                # List failed for this agreement -> all its rows are not processed.
                for le in list_errors:
                    errors.append({'agreementId': aid, 'error': le.get('error')})
                for rec in rows:
                    not_processed.append(rec.get('original', {}))
                continue

            # Map originalInvoiceId -> [request items] for this agreement.
            invoice_map = defaultdict(list)
            for it in items:
                inv = str(it.get('originalInvoiceId') or '').strip()
                if inv:
                    invoice_map[inv].append(it)

            for rec in rows:
                invoice_id = str(rec.get('invoice_id') or '').strip()
                matches = invoice_map.get(invoice_id, [])
                if not matches:
                    not_processed.append(rec.get('original', {}))
                    continue
                # Invoice found in the list -> confirm with GetBillingAdjustmentRequest.
                matched_any = False
                for it in matches:
                    req_id = it.get('billingAdjustmentRequestId')
                    if not req_id:
                        continue
                    try:
                        detail = self.get_adjustment_detail(aid, req_id)
                    except CredentialsCancelled:
                        raise
                    except Exception as e:
                        errors.append({'agreementId': aid, 'invoiceId': invoice_id, 'error': str(e)})
                        continue
                    detail['matchedInvoiceId'] = invoice_id
                    processed.append(detail)
                    matched_any = True
                    time.sleep(GET_DELAY)  # pace GetBillingAdjustmentRequest calls to quota
                if not matched_any:
                    # Listed but could not be confirmed via Get -> not processed.
                    not_processed.append(rec.get('original', {}))

        return processed, not_processed, errors

    def find_already_processed(self, rows, block_statuses=('COMPLETED', 'PENDING'), cache=None):
        """Live pre-submission guard against duplicate refunds.

        For each `<agreement, invoice>` in `rows`, check the service for an existing
        billing adjustment request. A row is treated as **already processed** (and must
        NOT be resubmitted) when a request exists for its invoice with a status in
        `block_statuses` (default `COMPLETED`/`PENDING`). Rows whose only existing
        request(s) are `VALIDATION_FAILED` (no refund actually happened) are still
        submittable.

        This matters because the deterministic client token only de-duplicates within
        the API's 8-hour idempotency window; once a run spans or follows that window,
        this live check is what prevents a second refund.

        Returns (to_submit, already, errors):
          - to_submit: rows safe to submit (no blocking request found)
          - already:   rows that already have a blocking request; each is the original
                       row dict plus 'existing_request_id' and 'existing_status'
          - errors:    list of {'agreementId', 'error'} for agreements that could not be
                       verified. Their rows are placed in `to_submit` so a transient
                       listing failure does not block the run (the client token still
                       guards within 8h); the caller should surface the warning.
        """
        cache = cache if cache is not None else {}
        to_submit, already, errors = [], [], []
        by_agreement = defaultdict(list)
        for r in rows:
            by_agreement[r['agreement_id']].append(r)
        for aid, agrows in by_agreement.items():
            if aid in cache:
                invoice_map, list_failed = cache[aid]
            else:
                items, list_errors = self.list_adjustment_requests([aid], statuses=None)
                list_failed = bool(list_errors)
                invoice_map = defaultdict(list)
                if not list_failed:
                    for it in items:
                        inv = str(it.get('originalInvoiceId') or '').strip()
                        if inv:
                            invoice_map[inv].append(it)
                cache[aid] = (invoice_map, list_failed)
                if list_failed:
                    for le in list_errors:
                        errors.append({'agreementId': aid, 'error': le.get('error')})
                # Pace successive ListBillingAdjustmentRequests calls (one per agreement)
                # to the operation's quota; list_adjustment_requests only paces between
                # pages, not between agreements.
                time.sleep(LIST_BILLING_ADJUSTMENTS_DELAY)
            if list_failed:
                # Could not verify this agreement -> do not block; rely on the token.
                to_submit.extend(agrows)
                continue
            for r in agrows:
                existing = invoice_map.get(str(r['invoice_id']).strip(), [])
                blocking = [it for it in existing if it.get('status') in block_statuses]
                if blocking:
                    chosen = next((it for it in blocking if it.get('status') == 'COMPLETED'),
                                  blocking[0])
                    r2 = dict(r)
                    r2['existing_request_id'] = chosen.get('billingAdjustmentRequestId')
                    r2['existing_status'] = chosen.get('status')
                    already.append(r2)
                else:
                    to_submit.append(r)
        return to_submit, already, errors

    def run(self, rows, writer, dry_run=False, counters=None, precheck_processed=True):
        """
        Main processing. Writes each record as it is resolved.
        counters: mutable dict to update {total, processed, succeeded, failed, skipped}
        precheck_processed: for LIVE runs, before submitting each row, check the service
            for an existing COMPLETED/PENDING adjustment request on the same
            <agreement, invoice> and skip it (status ALREADY_PROCESSED) instead of
            risking a duplicate refund once the 8-hour idempotency window has lapsed.
            Ignored for dry-run. Defaults to True (safe by default).
        Returns a summary dict.
        """
        counters = counters if counters is not None else {}
        valid_rows = [r for r in rows if r['agreement_id']]
        counters['total'] = len(valid_rows)
        counters.setdefault('processed', 0)
        counters.setdefault('succeeded', 0)
        counters.setdefault('failed', 0)
        counters.setdefault('skipped', 0)

        # Wrap the writer so we also accumulate $ totals (submitted/completed/failed)
        # for the summary, in addition to the counts. Delegates writes unchanged.
        writer = _AmountTally(writer)

        duplicate_invoices = find_duplicate_invoices(valid_rows)
        if duplicate_invoices:
            self._log(f"Found {len(duplicate_invoices)} invoice(s) across multiple agreements (handled in phases).")

        phases = group_rows_by_invoice_occurrence(valid_rows)
        self._log(f"Processing in {len(phases)} phase(s). Dry run: {dry_run}")

        summary = {
            "started_at": datetime.now().isoformat(),
            "dry_run": dry_run,
            "total_rows": len(valid_rows),
            "total_phases": len(phases),
            "duplicate_invoices": duplicate_invoices,
            "submitted": 0,
            "succeeded": 0,
            "failed": 0,
            "already_processed": 0,
        }

        # Cache of existing adjustment requests per agreement, reused across phases so
        # the live pre-check lists each agreement at most once per run.
        precheck_cache = {}

        # Dry-run only: accumulate per-invoice requested totals to flag when the sum
        # of all rows for one invoice exceeds its maxAdjustmentAmount.
        dry_run_invoice_totals = defaultdict(lambda: {"total": 0.0, "max": None, "rows": 0})

        for phase_num, phase_rows in enumerate(phases, 1):
            if self.cancel_check():
                self._log("Job cancelled.")
                summary["cancelled"] = True
                break

            self._log(f"=== Phase {phase_num}/{len(phases)}: {len(phase_rows)} row(s) ===")

            # Validate
            validated = []
            for row in phase_rows:
                if self.cancel_check():
                    break
                is_valid, max_amount, error = self.validate_invoice(
                    row['agreement_id'], row['invoice_id'], row['amount']
                )
                if is_valid:
                    row['max_adjustment_amount'] = max_amount
                    validated.append(row)
                else:
                    counters['processed'] += 1
                    counters['failed'] += 1
                    summary["failed"] += 1
                    self._log(f"  invoice {row['invoice_id']} ({row['agreement_id']}): "
                              f"VALIDATION_FAILED - {error}")
                    writer.write({
                        "phase": phase_num,
                        "agreement_id": row['agreement_id'],
                        "invoice_id": row['invoice_id'],
                        "amount": row['amount'],
                        "status": "VALIDATION_FAILED",
                        "billing_adjustment_request_id": "",
                        "message": error,
                    })
                    self.progress_cb(**counters)
                time.sleep(VALIDATE_DELAY)

            if not validated:
                continue

            # Pre-submission guard — runs for live AND dry-run (when enabled). It skips
            # any <agreement, invoice> that already has a COMPLETED/PENDING adjustment
            # request so a re-run (or a run that spans the 8-hour idempotency window)
            # cannot create a duplicate refund. In dry-run nothing is submitted, but the
            # already-processed rows are surfaced as a warning and excluded from the
            # DRY_RUN_OK preview, so the preview reflects only genuinely new refunds.
            if precheck_processed:
                self._log("Checking for already-processed refunds...")
                validated, already_processed, precheck_errors = self.find_already_processed(
                    validated, cache=precheck_cache
                )
                for pe in precheck_errors:
                    self._log(f"  WARNING: could not verify agreement {pe['agreementId']} "
                              f"({pe['error']}); its rows are treated as not-yet-processed.")
                for r in already_processed:
                    counters['processed'] += 1
                    counters['skipped'] = counters.get('skipped', 0) + 1
                    summary["already_processed"] += 1
                    tail = "; would skip (dry-run)" if dry_run else "; skipping (not resubmitted)"
                    self._log(f"  invoice {r['invoice_id']} ({r['agreement_id']}): "
                              f"ALREADY_PROCESSED - existing {r['existing_status']} request "
                              f"{r['existing_request_id']}{tail}")
                    writer.write({
                        "phase": phase_num,
                        "agreement_id": r['agreement_id'],
                        "invoice_id": r['invoice_id'],
                        "amount": r['amount'],
                        "status": "ALREADY_PROCESSED",
                        "billing_adjustment_request_id": r.get('existing_request_id', ''),
                        "message": (f"Skipped: an existing {r['existing_status']} adjustment "
                                    f"request ({r['existing_request_id']}) already exists for "
                                    f"this <agreement, invoice>."),
                    })
                    self.progress_cb(**counters)

            if dry_run:
                # Record the rows that WOULD be submitted in a live run.
                for row in validated:
                    counters['processed'] += 1
                    counters['succeeded'] += 1
                    summary["succeeded"] += 1
                    agg = dry_run_invoice_totals[row['invoice_id']]
                    try:
                        agg["total"] += float(row['amount'])
                    except (TypeError, ValueError):
                        pass
                    agg["max"] = row.get('max_adjustment_amount')
                    agg["rows"] += 1
                    writer.write({
                        "phase": phase_num,
                        "agreement_id": row['agreement_id'],
                        "invoice_id": row['invoice_id'],
                        "amount": row['amount'],
                        "status": "DRY_RUN_OK",
                        "billing_adjustment_request_id": "",
                        "message": f"Would submit. Max allowed: {row.get('max_adjustment_amount')}",
                    })
                    self.progress_cb(**counters)
                continue  # No submission in dry-run

            if not validated:
                continue


            # Submit batches
            grouped = group_by_agreement(validated)
            batches = create_batches(grouped, BATCH_SIZE)
            self._log(f"Submitting {len(batches)} batch(es)...")

            pending_requests = []
            for batch in batches:
                if self.cancel_check():
                    break
                agreement_id = batch['agreement_id']
                entries = batch['entries']
                entry_by_token = {
                    generate_client_token(e['agreement_id'], e['invoice_id']): e
                    for e in entries
                }
                try:
                    response = self._call(
                        'batch_create_billing_adjustment_request',
                        billingAdjustmentRequestEntries=self._create_batch_entries(entries)
                    )
                    items = response.get('items', [])
                    errors = response.get('errors', [])
                    summary["submitted"] += len(items)

                    for item in items:
                        req_id = item.get('billingAdjustmentRequestId')
                        token = item.get('clientToken')
                        entry = entry_by_token.get(token) or entries[0]
                        pending_requests.append({
                            'request_id': req_id,
                            'agreement_id': agreement_id,
                            'invoice_id': entry['invoice_id'],
                            'amount': entry['amount'],
                            'phase': phase_num,
                        })

                    for err in errors:
                        token = err.get('clientToken')
                        entry = entry_by_token.get(token, {})
                        counters['processed'] += 1
                        counters['failed'] += 1
                        summary["failed"] += 1
                        err_msg = f"{err.get('code', '')} {err.get('message', '')}".strip() \
                            or json.dumps(err, default=str)
                        self._log(f"  invoice {entry.get('invoice_id', '')} ({agreement_id}): "
                                  f"SUBMIT_FAILED - {err_msg}")
                        writer.write({
                            "phase": phase_num,
                            "agreement_id": agreement_id,
                            "invoice_id": entry.get('invoice_id', ''),
                            "amount": entry.get('amount', ''),
                            "status": "SUBMIT_FAILED",
                            "billing_adjustment_request_id": "",
                            "message": json.dumps(err, default=str),
                        })
                        self.progress_cb(**counters)
                except CredentialsCancelled:
                    raise
                except Exception as e:
                    # An authorization/compliance denial (e.g. the seller behind this
                    # agreement is not KYC compliant) is a per-request rejection, not a
                    # broken submit call: retrying won't help. Surface it as
                    # VALIDATION_FAILED with the real API message so the row is
                    # actionable, and reserve SUBMIT_FAILED for genuine call failures.
                    if is_access_denied(e):
                        _, api_msg = extract_api_error(e)
                        status = "VALIDATION_FAILED"
                        reason = api_msg
                    else:
                        status = "SUBMIT_FAILED"
                        reason = str(e)
                    for entry in entries:
                        counters['processed'] += 1
                        counters['failed'] += 1
                        summary["failed"] += 1
                        self._log(f"  invoice {entry['invoice_id']} ({agreement_id}): "
                                  f"{status} - {reason}")
                        writer.write({
                            "phase": phase_num,
                            "agreement_id": agreement_id,
                            "invoice_id": entry['invoice_id'],
                            "amount": entry['amount'],
                            "status": status,
                            "billing_adjustment_request_id": "",
                            "message": reason,
                        })
                        self.progress_cb(**counters)
                time.sleep(SUBMIT_DELAY)

            # Poll for completion of this phase's submitted requests
            self._wait_and_record(pending_requests, writer, counters, summary, phase_num)

        summary["finished_at"] = datetime.now().isoformat()
        summary["succeeded"] = counters['succeeded']
        summary["failed"] = counters['failed']
        summary["amount_totals"] = writer.summary()
        if dry_run:
            warnings = []
            for inv, info in dry_run_invoice_totals.items():
                if info["max"] is not None and info["total"] > float(info["max"]):
                    warnings.append({
                        "invoice_id": inv,
                        "total_requested": round(info["total"], 2),
                        "max_adjustment_amount": info["max"],
                        "row_count": info["rows"],
                    })
            summary["aggregate_warnings"] = warnings
        return summary

    def _wait_and_record(self, pending_requests, writer, counters, summary, phase_num):
        """Poll each submitted request until terminal status, recording incrementally.

        On every poll it logs each request's current status (and the service's
        statusMessage when present) plus the countdown to the next status check, so a
        request that stays in progress for a while doesn't look stuck."""
        if not pending_requests:
            return
        max_poll_time = _compute_poll_budget(len(pending_requests))
        self._log(f"Waiting for {len(pending_requests)} submitted request(s) to complete "
                  f"(checks paced at {GET_CALLS_PER_SECOND}/s, polling every "
                  f"{POLL_INTERVAL}s, up to {max_poll_time}s)...")
        start = time.time()
        poll_round = 0
        while pending_requests and (time.time() - start) < max_poll_time:
            if self.cancel_check():
                break
            poll_round += 1
            elapsed = int(time.time() - start)
            self._log(f"Poll #{poll_round} (elapsed {elapsed}s): checking "
                      f"{len(pending_requests)} pending request(s)...")
            still_pending = []
            for req in pending_requests:
                status, message = self.get_adjustment_status(req['agreement_id'], req['request_id'])
                detail = f" - {message}" if message else ""
                if status in ('COMPLETED', 'VALIDATION_FAILED', 'ERROR'):
                    counters['processed'] += 1
                    if status == 'COMPLETED':
                        counters['succeeded'] += 1
                    else:
                        counters['failed'] += 1
                    self._log(f"  invoice {req['invoice_id']} ({req['request_id']}): "
                              f"{status}{detail}")
                    writer.write({
                        "phase": phase_num,
                        "agreement_id": req['agreement_id'],
                        "invoice_id": req['invoice_id'],
                        "amount": req['amount'],
                        "status": status,
                        "billing_adjustment_request_id": req['request_id'],
                        "message": message or "",
                    })
                    self.progress_cb(**counters)
                else:
                    still_pending.append(req)
                    self._log(f"  invoice {req['invoice_id']} ({req['request_id']}): "
                              f"{status or 'PENDING'}{detail} - still processing; "
                              f"next status check in {GET_DELAY:.1f}s")
                time.sleep(GET_DELAY)
            pending_requests = still_pending
            if pending_requests:
                elapsed = int(time.time() - start)
                remaining = max(0, max_poll_time - elapsed)
                self._log(f"{len(pending_requests)} request(s) still pending after {elapsed}s; "
                          f"next poll in {POLL_INTERVAL}s (about {remaining}s left before timeout).")
                time.sleep(POLL_INTERVAL)

        # Timeouts
        for req in pending_requests:
            counters['processed'] += 1
            counters['failed'] += 1
            writer.write({
                "phase": phase_num,
                "agreement_id": req['agreement_id'],
                "invoice_id": req['invoice_id'],
                "amount": req['amount'],
                "status": "TIMEOUT",
                "billing_adjustment_request_id": req['request_id'],
                "message": f"Timed out after {max_poll_time}s",
            })
            self.progress_cb(**counters)
