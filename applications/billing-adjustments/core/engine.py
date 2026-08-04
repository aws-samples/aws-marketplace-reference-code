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
from collections import defaultdict, deque

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

# Bounded application-level retry for the safety-critical duplicate pre-check list
# call. boto3 already retries transient errors internally (max_attempts=3); these
# extra attempts guard the pre-check specifically, because when it cannot verify an
# agreement the affected rows are held for review (NEED_REVIEW) and NEVER submitted
# unverified — retrying first avoids sending a brief throttle/5xx straight to review.
PRECHECK_LIST_RETRIES = 3        # attempts (in addition to boto3's own retries)
PRECHECK_LIST_RETRY_DELAY = 2.0  # base seconds between attempts (grows linearly)

# Status polling. The total budget SCALES with the number of pending requests so a
# large batch is not falsely timed out: one status sweep of N requests already costs
# ~ N / GET_CALLS_PER_SECOND seconds in pacing alone. We allow up to MAX_POLL_SWEEPS
# full sweeps (each followed by a POLL_INTERVAL idle wait), bounded by a floor (so
# small batches behave as before) and an absolute ceiling. See _compute_poll_budget().
POLL_INTERVAL = 60           # ceiling for the idle wait between status sweeps
POLL_INTERVAL_START = 5      # first idle wait; backs off toward POLL_INTERVAL
POLL_BACKOFF_FACTOR = 2      # multiply the idle wait after each no-progress sweep
MIN_POLL_TIME = 600          # floor in seconds (small batches)
MAX_POLL_SWEEPS = 5          # number of full status sweeps to allow
MAX_POLL_TIME_CAP = 7200     # absolute ceiling in seconds (2 hours)
# Back-compat alias; the effective budget is computed per-run in _wait_and_record.
MAX_POLL_TIME = MIN_POLL_TIME
CURRENCY_CODE = "USD"
ADJUSTMENT_REASON = "OTHER"
ENDPOINT_URL = "https://agreement-marketplace.us-east-1.amazonaws.com"
REGION = "us-east-1"

# Required CSV columns (header must contain these). These plus an amount column
# (see AMOUNT_COLUMN_OPTIONS) are the only columns the tool actually needs: they
# identify the invoice to adjust and by how much.
REQUIRED_COLUMNS = [
    "invoice_id",
    "agreement_id",
]
# Optional "reference" columns. If present they are carried through to the output
# for the operator's convenience, but the tool never reads them to drive a refund,
# so they may be omitted entirely from the file.
REFERENCE_COLUMNS = [
    "seller_id",
    "aws_account_id",
    "product_code",
    "month_id",
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
        "reference_columns": REFERENCE_COLUMNS,
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
        # Cheap local guard first: the billing-adjustment backend rejects an
        # adjustmentAmount with more than MAX_AMOUNT_DECIMALS decimal places (USD has
        # 2 minor-unit digits). Catch it here — the universal pre-submit gate, hit by
        # every entry point — so it fails as a clear VALIDATION_FAILED instead of a
        # cryptic server-side VALIDATION_EXCEPTION at submit time (e.g. "16.9176").
        clean_amount = format_amount(requested_amount)
        if count_decimal_places(clean_amount) > MAX_AMOUNT_DECIMALS:
            return False, None, (
                f"amount must have at most {MAX_AMOUNT_DECIMALS} decimal places "
                f"(got '{requested_amount}')")
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

    def list_invoices_for_agreement(self, agreement_id):
        """List all invoices for an agreement via ListAgreementInvoiceLineItems.

        Returns a list of dicts with invoice_id, invoice_type, amount,
        max_refundable, and currency_code for each invoice group.
        """
        summaries = []
        next_token = None
        while True:
            params = {
                'agreementId': agreement_id,
                'groupBy': 'INVOICE_ID',
            }
            if next_token:
                params['nextToken'] = next_token
            response = self._call('list_agreement_invoice_line_items', **params)
            summaries.extend(response.get('agreementInvoiceLineItemGroupSummaries', []))
            next_token = response.get('nextToken')
            if not next_token:
                break

        results = []
        for s in summaries:
            pricing = s.get('pricingCurrencyAmount', {})
            results.append({
                'invoice_id': s.get('invoiceId'),
                'invoice_type': s.get('invoiceType', 'UNKNOWN'),
                'amount': pricing.get('amount'),
                'max_refundable': pricing.get('maxAdjustmentAmount'),
                'currency_code': pricing.get('currencyCode', 'USD'),
            })
        return results

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

    def _recover_existing_request(self, agreement_id, invoice_id):
        """When a submit fails with 'client token is invalid', look up whether a
        request already exists for this agreement+invoice. Returns the matching
        request dict (with billingAdjustmentRequestId and status) or None."""
        try:
            items, _ = self.list_adjustment_requests(
                [agreement_id], statuses=None, max_results=50)
            inv_str = str(invoice_id).strip()
            for it in items:
                if str(it.get('originalInvoiceId', '')).strip() == inv_str:
                    return it
        except Exception:
            pass
        return None

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

    def _list_adjustment_requests_verified(self, aid):
        """List an agreement's adjustment requests for the duplicate pre-check, with a
        bounded application-level retry.

        Returns (items, list_failed). list_failed is True only if EVERY attempt failed
        (partial pagination failures count as a failure too, since a missed page could
        hide an existing request). boto3 already retries internally; these extra
        attempts exist because a pre-check failure holds rows for review rather than
        submitting them, so it is worth trying harder before giving up. Credential
        errors are not retried here — they propagate (as CredentialsCancelled) so the
        job pauses for fresh credentials instead of being treated as unverifiable."""
        last_errors = None
        for attempt in range(PRECHECK_LIST_RETRIES):
            items, list_errors = self.list_adjustment_requests([aid], statuses=None)
            if not list_errors:
                return items, False
            last_errors = list_errors
            if attempt < PRECHECK_LIST_RETRIES - 1:
                self._log(f"  could not list existing requests for agreement {aid} "
                          f"(attempt {attempt + 1}/{PRECHECK_LIST_RETRIES}); retrying...")
                time.sleep(PRECHECK_LIST_RETRY_DELAY * (attempt + 1))
        return [], (last_errors or [{'error': 'unknown listing error'}])

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
        this live check is the ONLY thing that prevents a second refund.

        FAIL CLOSED: if an agreement cannot be verified (its list call fails even after
        the bounded retry), its rows are returned in `unverifiable` — NOT `to_submit` —
        so the run can never submit an unverified refund without the user's involvement.
        Previously such rows fell through to submission "relying on the client token",
        which silently allowed a duplicate refund once the 8-hour token window lapsed.

        Returns (to_submit, already, unverifiable, errors):
          - to_submit:    rows safe to submit (verified: no blocking request found)
          - already:      rows that already have a blocking request; each is the original
                          row dict plus 'existing_request_id' and 'existing_status'
          - unverifiable: rows whose agreement could not be verified; each is the original
                          row dict plus 'verify_error'. The caller MUST hold these for
                          review and must NOT submit them.
          - errors:       list of {'agreementId', 'error'} for agreements that could not
                          be verified (for surfacing a warning to the operator).
        """
        cache = cache if cache is not None else {}
        to_submit, already, unverifiable, errors = [], [], [], []
        by_agreement = defaultdict(list)
        for r in rows:
            by_agreement[r['agreement_id']].append(r)
        for aid, agrows in by_agreement.items():
            if aid in cache:
                invoice_map, list_failed = cache[aid]
            else:
                items, list_failed = self._list_adjustment_requests_verified(aid)
                invoice_map = defaultdict(list)
                if not list_failed:
                    for it in items:
                        inv = str(it.get('originalInvoiceId') or '').strip()
                        if inv:
                            invoice_map[inv].append(it)
                cache[aid] = (invoice_map, list_failed)
                if list_failed:
                    for le in list_failed if isinstance(list_failed, list) else []:
                        errors.append({'agreementId': aid, 'error': le.get('error')})
                # Pace successive ListBillingAdjustmentRequests calls (one per agreement)
                # to the operation's quota; list_adjustment_requests only paces between
                # pages, not between agreements.
                time.sleep(LIST_BILLING_ADJUSTMENTS_DELAY)
            if list_failed:
                # Could not verify this agreement -> FAIL CLOSED. Hold the rows for
                # review; do NOT submit unverified (the token cannot be relied on past
                # the 8-hour idempotency window). `list_failed` carries the underlying
                # error list (see _list_adjustment_requests_verified); derive the reason
                # from it so a cache hit reports the same detail as the first check.
                verify_msg = "; ".join(
                    str(e.get('error')) for e in list_failed
                    if isinstance(e, dict)
                ) if isinstance(list_failed, list) else ""
                verify_msg = verify_msg or "listing existing requests failed"
                for r in agrows:
                    r2 = dict(r)
                    r2['verify_error'] = verify_msg
                    unverifiable.append(r2)
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
        return to_submit, already, unverifiable, errors

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
        counters.setdefault('need_review', 0)

        # Wrap the writer so we also accumulate $ totals (submitted/completed/failed)
        # for the summary, in addition to the counts. Delegates writes unchanged.
        writer = _AmountTally(writer)

        duplicate_invoices = find_duplicate_invoices(valid_rows)
        if duplicate_invoices:
            self._log(f"Found {len(duplicate_invoices)} invoice(s) that appear on multiple "
                      f"agreements; each such invoice's refunds are processed one at a time "
                      f"(never concurrently), while different invoices run concurrently.")

        # Build one ordered chain per invoice_id. Refunds for the SAME invoice must be
        # processed strictly one-at-a-time — an invoice may have at most one in-flight
        # billing-adjustment request at any moment — but DIFFERENT invoices are
        # independent and their requests are in flight concurrently. Each row is tagged
        # with its 1-based occurrence within its invoice chain; that number is recorded
        # as the record's "phase" (identical meaning to the previous phase-based model).
        remaining = {}
        for _r in valid_rows:
            remaining.setdefault(_r['invoice_id'], deque()).append(_r)
        for _inv, _dq in remaining.items():
            for _i, _row in enumerate(_dq, 1):
                _row['occurrence'] = _i
        max_depth = max((len(_dq) for _dq in remaining.values()), default=0)
        self._log(f"Processing {len(valid_rows)} row(s) across {len(remaining)} invoice "
                  f"chain(s) (max chain depth {max_depth}). Dry run: {dry_run}")

        summary = {
            "started_at": datetime.now().isoformat(),
            "dry_run": dry_run,
            "total_rows": len(valid_rows),
            "total_phases": max_depth,
            "duplicate_invoices": duplicate_invoices,
            "submitted": 0,
            "succeeded": 0,
            "failed": 0,
            "already_processed": 0,
            "need_review": 0,
        }

        # Cache of existing adjustment requests per agreement, reused across phases so
        # the live pre-check lists each agreement at most once per run.
        precheck_cache = {}

        # Dry-run only: accumulate per-invoice requested totals to flag when the sum
        # of all rows for one invoice exceeds its maxAdjustmentAmount.
        dry_run_invoice_totals = defaultdict(lambda: {"total": 0.0, "max": None, "rows": 0})

        # ---- pipelined per-invoice scheduler --------------------------------
        # `busy` holds invoice_ids that currently have an in-flight request, so a later
        # occurrence of the same invoice is never submitted until the earlier one
        # reaches a terminal status (this is what keeps the same invoice on different
        # agreements from ever being in flight at the same time). `in_flight` holds the
        # submitted requests we are polling; requests for DIFFERENT invoices are in
        # flight together, so their server-side processing overlaps instead of being
        # serialized behind a global phase barrier.
        busy = set()
        in_flight = []
        # Per-request wait budget (same scaling/cap as the previous phase model, but
        # applied per request so one slow request cannot hang the whole run).
        poll_budget = _compute_poll_budget(len(valid_rows))
        # Idle wait between status sweeps starts short and backs off toward
        # POLL_INTERVAL, so fast-completing refunds are detected quickly while a long
        # tail of slow requests isn't polled needlessly often. Resets on any progress.
        poll_wait = POLL_INTERVAL_START
        cancelled = False

        def _emit(occurrence, agreement_id, invoice_id, amount, status, req_id, message):
            writer.write({
                "phase": occurrence,
                "agreement_id": agreement_id,
                "invoice_id": invoice_id,
                "amount": amount,
                "status": status,
                "billing_adjustment_request_id": req_id,
                "message": message,
            })
            self.progress_cb(**counters)

        while True:
            if self.cancel_check():
                cancelled = True
                break

            # Pull the head of every invoice chain that is not currently in flight.
            # Within a wave every invoice_id is distinct, so these can be validated and
            # submitted together (still batched per agreement). An invoice already in
            # flight contributes nothing this wave — its next occurrence waits.
            ready = []
            for _inv in list(remaining.keys()):
                if _inv in busy:
                    continue
                _dq = remaining[_inv]
                ready.append(_dq.popleft())
                if not _dq:
                    del remaining[_inv]

            if not ready and not in_flight:
                break

            made_progress = bool(ready)

            # ---------- validate ----------
            validated = []
            for row in ready:
                if self.cancel_check():
                    cancelled = True
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
                    _emit(row['occurrence'], row['agreement_id'], row['invoice_id'],
                          row['amount'], "VALIDATION_FAILED", "", error)
                time.sleep(VALIDATE_DELAY)
            if cancelled:
                break

            # ---------- pre-submission dedup guard (live AND dry-run) ----------
            # Skips any <agreement, invoice> that already has a COMPLETED/PENDING
            # request so a re-run (or a run spanning the 8-hour idempotency window)
            # cannot create a duplicate refund.
            if precheck_processed and validated:
                self._log("Checking for already-processed refunds...")
                validated, already_processed, unverifiable, precheck_errors = \
                    self.find_already_processed(validated, cache=precheck_cache)
                # FAIL CLOSED: rows whose agreement could not be verified are held for
                # review and never submitted, so a duplicate refund can never be created
                # without the user's involvement (the client token cannot be relied on
                # past the 8-hour idempotency window). Re-run once the listing recovers.
                for r in unverifiable:
                    counters['processed'] += 1
                    counters['need_review'] = counters.get('need_review', 0) + 1
                    summary["need_review"] = summary.get("need_review", 0) + 1
                    self._log(f"  invoice {r['invoice_id']} ({r['agreement_id']}): "
                              f"NEED_REVIEW - could not verify whether a refund already "
                              f"exists ({r.get('verify_error')}); NOT submitted.")
                    _emit(r['occurrence'], r['agreement_id'], r['invoice_id'], r['amount'],
                          "NEED_REVIEW", "",
                          f"Held for review: could not verify existing refunds for this "
                          f"<agreement, invoice> ({r.get('verify_error')}). Not submitted "
                          f"to avoid a possible duplicate refund. Re-run once listing "
                          f"succeeds; already-processed rows are skipped automatically.")
                for pe in precheck_errors:
                    self._log(f"  WARNING: could not verify agreement {pe['agreementId']} "
                              f"({pe['error']}); its rows are held for review (NEED_REVIEW), "
                              f"not submitted.")
                for r in already_processed:
                    counters['processed'] += 1
                    counters['skipped'] = counters.get('skipped', 0) + 1
                    summary["already_processed"] += 1
                    tail = "; would skip (dry-run)" if dry_run else "; skipping (not resubmitted)"
                    self._log(f"  invoice {r['invoice_id']} ({r['agreement_id']}): "
                              f"ALREADY_PROCESSED - existing {r['existing_status']} request "
                              f"{r['existing_request_id']}{tail}")
                    _emit(r['occurrence'], r['agreement_id'], r['invoice_id'], r['amount'],
                          "ALREADY_PROCESSED", r.get('existing_request_id', ''),
                          (f"Skipped: an existing {r['existing_status']} adjustment request "
                           f"({r['existing_request_id']}) already exists for this "
                           f"<agreement, invoice>."))

            # ---------- dry-run: record what WOULD be submitted (no submission) ----------
            if dry_run:
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
                    _emit(row['occurrence'], row['agreement_id'], row['invoice_id'],
                          row['amount'], "DRY_RUN_OK", "",
                          f"Would submit. Max allowed: {row.get('max_adjustment_amount')}")
                validated = []   # nothing is submitted in a dry run

            # ---------- live: submit this wave (batched per agreement) ----------
            if validated:
                grouped = group_by_agreement(validated)
                batches = create_batches(grouped, BATCH_SIZE)
                self._log(f"Submitting {len(batches)} batch(es)...")
                for batch in batches:
                    if self.cancel_check():
                        cancelled = True
                        break
                    agreement_id = batch['agreement_id']
                    entries = batch['entries']
                    entry_by_token = {
                        generate_client_token(e['agreement_id'], e['invoice_id']): e
                        for e in entries
                    }
                    handled = set()   # invoice_ids given a terminal record in this batch
                    try:
                        response = self._call(
                            'batch_create_billing_adjustment_request',
                            billingAdjustmentRequestEntries=self._create_batch_entries(entries)
                        )
                        items = response.get('items', [])
                        errors = response.get('errors', [])
                        summary["submitted"] += len(items)

                        for item in items:
                            token = item.get('clientToken')
                            entry = entry_by_token.get(token) or entries[0]
                            in_flight.append({
                                'request_id': item.get('billingAdjustmentRequestId'),
                                'agreement_id': agreement_id,
                                'invoice_id': entry['invoice_id'],
                                'amount': entry['amount'],
                                'phase': entry.get('occurrence', ''),
                                'deadline': time.time() + poll_budget,
                            })
                            busy.add(entry['invoice_id'])

                        for err in errors:
                            token = err.get('clientToken')
                            entry = entry_by_token.get(token, {})
                            err_code = err.get('code', '')
                            err_message = err.get('message', '')

                            # "client token is invalid" => the token was already used by
                            # an earlier submit (e.g. a run that timed out locally but
                            # succeeded server-side). Recover the existing request and
                            # poll it instead of failing permanently.
                            if (err_code == 'VALIDATION_EXCEPTION'
                                    and 'client token' in err_message.lower()
                                    and entry.get('invoice_id')):
                                existing = self._recover_existing_request(
                                    agreement_id, entry['invoice_id'])
                                if existing:
                                    req_id = existing.get('billingAdjustmentRequestId')
                                    ex_status = existing.get('status', '')
                                    if ex_status == 'COMPLETED':
                                        counters['processed'] += 1
                                        counters['skipped'] = counters.get('skipped', 0) + 1
                                        summary["already_processed"] += 1
                                        self._log(
                                            f"  invoice {entry['invoice_id']} ({agreement_id}): "
                                            f"ALREADY_COMPLETED - recovered existing {req_id}")
                                        _emit(entry.get('occurrence', ''), agreement_id,
                                              entry['invoice_id'], entry.get('amount', ''),
                                              "ALREADY_PROCESSED", req_id,
                                              f"Client token reused; existing request "
                                              f"{req_id} is already {ex_status}.")
                                        handled.add(entry['invoice_id'])
                                    else:
                                        # Still in progress — recover it and poll.
                                        self._log(
                                            f"  invoice {entry['invoice_id']} ({agreement_id}): "
                                            f"recovered existing {ex_status} request {req_id}; polling")
                                        in_flight.append({
                                            'request_id': req_id,
                                            'agreement_id': agreement_id,
                                            'invoice_id': entry['invoice_id'],
                                            'amount': entry.get('amount', ''),
                                            'phase': entry.get('occurrence', ''),
                                            'deadline': time.time() + poll_budget,
                                        })
                                        busy.add(entry['invoice_id'])
                                        summary["submitted"] += 1
                                    continue

                            # genuine submit failure for this entry
                            counters['processed'] += 1
                            counters['failed'] += 1
                            summary["failed"] += 1
                            err_msg = f"{err_code} {err_message}".strip() \
                                or json.dumps(err, default=str)
                            self._log(f"  invoice {entry.get('invoice_id', '')} ({agreement_id}): "
                                      f"SUBMIT_FAILED - {err_msg}")
                            _emit(entry.get('occurrence', ''), agreement_id,
                                  entry.get('invoice_id', ''), entry.get('amount', ''),
                                  "SUBMIT_FAILED", "", json.dumps(err, default=str))
                            if entry.get('invoice_id'):
                                handled.add(entry['invoice_id'])

                        # Fail-safe: any entry the service neither accepted (now in
                        # flight) nor returned an error for must still be closed out, so
                        # a chain can never stall or be resubmitted in a loop.
                        for entry in entries:
                            inv = entry['invoice_id']
                            if inv in busy or inv in handled:
                                continue
                            counters['processed'] += 1
                            counters['failed'] += 1
                            summary["failed"] += 1
                            self._log(f"  invoice {inv} ({agreement_id}): SUBMIT_FAILED - "
                                      f"no result returned for this entry")
                            _emit(entry.get('occurrence', ''), agreement_id, inv,
                                  entry.get('amount', ''), "SUBMIT_FAILED", "",
                                  "No result returned by BatchCreateBillingAdjustmentRequest.")
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
                            _emit(entry.get('occurrence', ''), agreement_id,
                                  entry['invoice_id'], entry['amount'], status, "", reason)
                    time.sleep(SUBMIT_DELAY)
            if cancelled:
                break

            # ---------- poll one sweep over the in-flight requests ----------
            # As each request reaches a terminal status its invoice is freed, so that
            # invoice's next occurrence becomes eligible on the next wave — without
            # waiting for unrelated invoices to finish.
            if in_flight:
                still = []
                for idx, req in enumerate(in_flight):
                    if self.cancel_check():
                        cancelled = True
                        still.extend(in_flight[idx:])
                        break
                    status, message = self.get_adjustment_status(
                        req['agreement_id'], req['request_id'])
                    detail = f" - {message}" if message else ""
                    if status in ('COMPLETED', 'VALIDATION_FAILED', 'ERROR'):
                        counters['processed'] += 1
                        if status == 'COMPLETED':
                            counters['succeeded'] += 1
                        else:
                            counters['failed'] += 1
                        busy.discard(req['invoice_id'])
                        self._log(f"  invoice {req['invoice_id']} ({req['request_id']}): "
                                  f"{status}{detail}")
                        _emit(req['phase'], req['agreement_id'], req['invoice_id'],
                              req['amount'], status, req['request_id'], message or "")
                        made_progress = True
                    elif time.time() >= req['deadline']:
                        counters['processed'] += 1
                        counters['failed'] += 1
                        busy.discard(req['invoice_id'])
                        self._log(f"  invoice {req['invoice_id']} ({req['request_id']}): "
                                  f"TIMEOUT after {poll_budget}s")
                        _emit(req['phase'], req['agreement_id'], req['invoice_id'],
                              req['amount'], "TIMEOUT", req['request_id'],
                              f"Timed out after {poll_budget}s")
                        made_progress = True
                    else:
                        still.append(req)
                        self._log(f"  invoice {req['invoice_id']} ({req['request_id']}): "
                                  f"{status or 'PENDING'}{detail} - still processing")
                    time.sleep(GET_DELAY)
                in_flight = still
            if cancelled:
                break

            # Idle only when we are purely waiting on server-side completion (no ready
            # work was done and nothing completed this pass). The wait backs off from
            # POLL_INTERVAL_START toward POLL_INTERVAL, and resets on any progress.
            if made_progress:
                poll_wait = POLL_INTERVAL_START
            elif in_flight:
                self._log(f"{len(in_flight)} request(s) still processing; next status "
                          f"check in {poll_wait}s.")
                time.sleep(poll_wait)
                poll_wait = min(POLL_INTERVAL, poll_wait * POLL_BACKOFF_FACTOR)

        # If cancelled, close out anything still in flight so the counts reconcile.
        if cancelled:
            self._log("Job cancelled.")
            summary["cancelled"] = True
            for req in in_flight:
                counters['processed'] += 1
                counters['failed'] += 1
                _emit(req['phase'], req['agreement_id'], req['invoice_id'], req['amount'],
                      "TIMEOUT", req['request_id'],
                      "Job cancelled while the request was in progress.")

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
