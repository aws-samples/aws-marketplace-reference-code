# AWS Marketplace Bulk Billing Adjustments

Tools for AWS Marketplace sellers to process **bulk billing adjustments (refunds)**
against the Marketplace Agreement billing APIs — validate invoices, submit
adjustments in batches, handle duplicate invoices across agreements, and track
status.

Beyond submitting refunds, the toolset can **reconcile** a refund file against the
service (check which invoices were actually processed) and look up individual or
filtered adjustment requests. It also **auto-separates invalid and duplicate rows**
into a "needs review" file so a bad row never blocks the rest of the batch. These are
available both in the web UI (**Check processed refunds**, **Check one request**, and
the needs-review download on submit) and as CLI scripts (`check_processed_refunds.py`,
`clean_refund_file.py`, `list_adjustment_requests.py`, `get_adjustment_request.py`).

## Ways to use it

| Option | Best for | Where |
|--------|----------|-------|
| **Web UI** | Non-technical users (accounting). Upload a CSV, dry-run, submit, download results. | [`webapp/`](webapp/README.md) |
| **Command line** | Engineers / automation. Same workflow from a terminal. | [`cli/`](cli/README.md) |
| **Deploy to AWS** | Hosting the Web UI in an AWS account (App Runner), including cross-account access. | [`deploy/`](deploy/README.md) |
| **Postman collection** | Exploring the raw APIs interactively, request by request. | [Published collection](https://www.postman.com/aws-partners/aws-marketplace/collection/38157848-955c413d-92d7-4ef3-b8dc-021f5321d941) |

The published Postman collection (in the AWS Partners workspace) documents the
complete API workflow — fork it, set your credentials at the collection level, and
run the requests.

## Repository layout

```
core/           Shared engine package — the single source of truth for the
                billing-adjustment logic, used by BOTH the web app and the CLI
cli/            Command-line scripts + their README and example output
  adjustmentFiles/   Sample input CSV (real data is gitignored)
  examples/          Example CLI output (adjustment_results_*.json)
webapp/         Web UI (Flask app) + README, launchers, example outputs
deploy/         Dockerfile + CloudFormation templates (App Runner, IAM, cross-account)
partner-kit/    Authored files for the external-partner deliverable
build-partner-kit.sh   Builds the deliverable zip from tracked sources
requirements.txt       Shared Python dependencies
```

### Architecture: one shared engine

All billing-adjustment logic lives in the **`core/`** package (input parsing and
validation, AWS client and credential handling, batching, the deterministic client
token, submission, polling, and the list/get/reconcile queries). Both entry points are
thin layers over it:

- **`webapp/`** (Flask UI + background jobs) imports `core` and adds the web/job glue.
- **`cli/`** scripts import `core` and add argument parsing + output formatting.
- **`deploy/`** containerizes the web app (the image bundles `core/` + `webapp/`).

A change to the API behavior is made once, in `core/`, and both surfaces pick it up —
so they can no longer drift apart.

## Input file format

The input is a **CSV file with a header row**, UTF-8 encoded. Each data row is one
refund (one invoice on one agreement). The same format is used by the Web UI upload,
the CLI, and the reconcile/clean tools. A committed dummy example lives at
[`cli/adjustmentFiles/sample_company.csv`](cli/adjustmentFiles/sample_company.csv).

### Columns

All of the columns below must be **present in the header row** (the file fails
validation if any are missing). Only `agreement_id`, `invoice_id`, and the amount
column drive the actual adjustment; the others are informational — they are used for
human review/audit and are preserved verbatim in the "needs review" output.

> **Header names are case-insensitive.** Column headers are matched ignoring case and
> surrounding spaces, so `refund_amount`, `Refund_amount`, and `REFUND_AMOUNT` are all
> accepted (the same applies to every column, e.g. `invoice_id` / `Invoice_ID`). The
> values in each row are read regardless of header casing; the original header text is
> preserved unchanged in any output file.

| Column | Required value? | Type | Description | Example |
|--------|-----------------|------|-------------|---------|
| `agreement_id` | **Yes** | Text | Marketplace agreement ID the invoice belongs to. Alphanumeric. | `agmt-byw2g19zkbjhuwxc8ki4w3b4x` |
| `invoice_id` | **Yes** | Text | The original invoice ID to adjust. May be all digits **or** alphanumeric. Must be treated as text (see below). | `2519920101` or `EUMPINGB26-12125` |
| `refund_amount` | **Yes** | Number (as text) | The amount to refund. See **Amount format** and **Currency** below. A second name, `SUM of Calculated Refund (T-Y)`, is also accepted for this column. | `0.01`, `150.00`, `$1,200.00` |
| `seller_id` | Header only | Text | Seller (proposer) account ID. Reference only. | `348230509592` |
| `aws_account_id` | Header only | Text | Buyer (acceptor) account ID. Reference only. **Keep as text** — 12-digit IDs can have leading zeros. | `013579169436` |
| `product_code` | Header only | Text | Product code. Reference only. | `2brlrrc75ciw9evgh9mbpygbn` |
| `month_id` | Header only | Text | Billing month label. Reference only. | `Jan 2026` |

"Header only" means the column must exist, but the value may be blank without failing
validation.

> **One row per `<invoice_id, agreement_id>`.** Because the idempotency client token is
> derived from `agreement_id` + `invoice_id` (see *Idempotency guardrail*), a repeated
> combination is treated as a duplicate — only the first occurrence is processed and the
> rest are routed to the needs-review output. De-duplicate before submitting.

### Data types — important for Excel/CSV

Several columns hold identifiers that **look** numeric but must be kept as **text**, or
Excel will silently corrupt them:

- **`aws_account_id` / `seller_id`** — 12-digit account IDs. If Excel treats them as
  numbers it drops leading zeros (`013579169436` becomes `13579169436`).
- **`invoice_id`** — long all-digit IDs get mangled into scientific notation
  (`2519920101` shown as `2.51992E+09`), and the real value is lost on save. Some
  invoice IDs are alphanumeric (`EUMPINGB26-12125`), so the column cannot be a number
  column at all.
- **`agreement_id`** — always alphanumeric (`agmt-…`).

In Excel: select these columns and set the cell format to **Text** *before* typing or
pasting values, and save as **"CSV UTF-8 (Comma delimited) (.csv)"**. After saving,
reopen the `.csv` in a plain text editor to confirm the IDs are intact (no `E+`,
no dropped leading zeros).

### Amount format

The amount column accepts a positive number, optionally written with common
formatting that is stripped automatically:

- A leading dollar sign — `$150.00`
- Thousands separators as commas — `1,200.00` or `$1,200.00`
- Surrounding spaces — `  150.00 `

Rules:

- The value must parse to a number **greater than 0** (a `0`, blank, or non-numeric
  value is rejected / routed to needs-review).
- **At most 2 digits after the decimal point.** USD carries two minor-unit digits, and
  the billing-adjustment backend rejects amounts with more precision, so a value like
  `150.005` or `13911.6313` is rejected up front (routed to needs-review). Round to 2
  decimals before submitting (e.g. `13911.6313` → `13911.63`).
- The **decimal separator must be a period (`.`)**. The European convention
  (`1.234,56` meaning one-thousand-two-hundred-thirty-four point five six) is **not**
  supported — the comma is always treated as a thousands separator and removed.
- Do not include a currency symbol other than `$`. Symbols like `€`, `£`, `¥` are
  **not** stripped and will cause the row to be rejected as a non-numeric amount.
- The amount must not exceed the invoice's `maxAdjustmentAmount` (checked live against
  `ListAgreementInvoiceLineItems`); rows over the max are rejected.

### Currency

**The tool currently submits every adjustment in `USD`.** The currency is fixed in
code (`CURRENCY_CODE = "USD"` in `core/engine.py`, the shared engine); there is no
currency column and no per-row override.

What this means for the amount you enter:

- **USD (and other 2-decimal currencies):** up to **2 decimal places** is valid
  (`150.00`, `0.01`).
- **Zero-decimal currencies — e.g. JPY (Japanese Yen), KRW (Korean Won):** these have
  **no minor unit**, so amounts must be **whole numbers with no decimal point** (`1000`,
  not `1000.00`). The current template/flow assumes USD-style decimals, so it does
  **not** correctly support zero-decimal currencies — submitting a JPY amount with a
  decimal would be rejected by the API.
- **Three-decimal currencies — e.g. BHD, KWD, OMR:** likewise not handled by the
  USD assumption.

If adjustments in non-USD currencies are needed, that requires a code change: add a
`currency_code` column (or job setting), pass it through to
`adjustmentEntry.currencyCode`, and validate the decimal precision per currency
(0 decimals for JPY/KRW, 2 for USD/EUR, 3 for BHD/KWD). Until then, only use this
template for **USD** invoices.

### Adjustment reason code

Every adjustment is submitted with a fixed `adjustmentReasonCode` of **`OTHER`**
(`ADJUSTMENT_REASON = "OTHER"`). It is **not** a CSV column and cannot currently be
set per row. Changing it requires a code change in `core/engine.py` (the shared engine).

### What validation checks

When you upload (Web UI) or run the CLI, the file goes through:

1. **Format check** — required header columns present; every row has an
   `agreement_id`, an `invoice_id`, and an amount that parses to a number > 0.
2. **Duplicate check** — repeated `<agreement_id, invoice_id>` rows are flagged; the
   first is kept, the rest go to needs-review.
3. **Live invoice validation** (dry-run and submit) — for each row, the invoice must
   exist on the agreement, be an adjustable `INVOICE` (not a `CREDIT_MEMO` etc.), and
   the requested amount must be ≤ its `maxAdjustmentAmount`.

Rows that fail steps 1–2 are separated into a **needs-review** file so they never
block the rest of the batch; rows that fail step 3 are reported per-row in the run
output.

## Run output statuses

When you run a job (Web UI), each invoice ends up with a `status` in the results
(the `status` column of `records.csv` and the `status` field in `records.jsonl`).
Here is what each value means and what to do about it.

| Status | Stage | Meaning | What to do |
|--------|-------|---------|------------|
| `COMPLETED` | after submit (service) | The adjustment was accepted and fully processed by AWS. | Done — the refund is applied. |
| `DRY_RUN_OK` | dry-run only | The invoice passed pre-flight validation and **would** be submitted in a live run. Nothing was submitted. | Re-run without dry-run to actually submit. |
| `ALREADY_PROCESSED` | live pre-check (before submit) | The live run found an existing `COMPLETED` or `PENDING` adjustment request for this `<agreement, invoice>`, so the row was **skipped** (not resubmitted) to avoid a duplicate refund. The existing request id is recorded. | None needed — the refund already exists / is in flight. Use **Check one request** / `get_adjustment_request.py` with the recorded request id to review it. |
| `VALIDATION_FAILED` | pre-submit check, **or** service terminal status | Two cases: (a) the row failed the pre-flight check — invoice not found, not an adjustable invoice type (e.g. `CREDIT_MEMO`), or amount > `maxAdjustmentAmount` — so **nothing was submitted**; or (b) a submitted request was rejected by the service during processing (e.g. KYC/compliance, agreement state). | Fix the input/data; the `message` column has the reason. Re-running unchanged won't help. |
| `SUBMIT_FAILED` | submit (create call) | The row passed validation, the tool called `BatchCreateBillingAdjustmentRequest`, and that call rejected the entry or errored (throttling, permissions, conflict, API error). **No request was created.** | Usually retry-safe — the deterministic client token prevents duplicates. Check the `message`. |
| `ERROR` | service terminal status | While polling, `GetBillingAdjustmentRequest` returned an error status for the request. | Investigate the `message`; may require AWS Marketplace support. |
| `TIMEOUT` | polling | The tool stopped waiting after the poll limit (`MAX_POLL_TIME`, 10 min). The request **may still finish** server-side. | Re-check later with **Check one request** (UI) or `check_adjustment_status.py`. Not necessarily a failure. |
| `PENDING` | in-flight (transient) | Submitted but not yet in a terminal state. Not written as a final row by the Web UI, but shown by the CLI status checker. | Wait and re-check. |

**`VALIDATION_FAILED` vs `SUBMIT_FAILED` in one line:** `VALIDATION_FAILED` means the
refund was rejected **on its merits** (the data/eligibility didn't pass) — fix the
input; `SUBMIT_FAILED` means the data looked fine but the **create call itself broke**
— generally safe to retry.

> The CLI and the web app share the same engine (`core/`), so they emit the **same**
> status values — the CLI's JSON results file uses these identical labels (see
> [`cli/README.md`](cli/README.md) → *Status Values*).

## Common errors and error codes

These are the errors you'll most often see from the Marketplace Agreement API, with
what they mean and how to resolve them. They apply to both the CLI and the web app.

| Error | Cause | Resolution |
|-------|-------|------------|
| `ResourceNotFoundException` | Agreement or invoice does not exist (for the calling account) | Verify the `agreement_id` / `invoice_id` in the input, and that the account owns the agreement |
| `REFUND_AMOUNT_EXCEEDS_MAXIMUM` | Amount exceeds the invoice's `maxAdjustmentAmount` | Run a dry-run to check limits; lower the amount |
| `CONFLICT_EXCEPTION` | Concurrent adjustment on the same invoice (same invoice across agreements processed together) | Wait and retry — the phase logic handles this automatically |
| `AccessDeniedException: Current Identity is not KYC Compliant` | Seller account KYC issue | Contact AWS Marketplace support |
| `ExpiredTokenException` | AWS credentials expired | Refresh credentials (the tools pause and prompt) |
| `AccessDeniedException` (action not authorized) | Missing IAM permission for a billing-adjustment action | Grant the four `aws-marketplace:` actions (see the deploy/CLI permission setup) |

## Troubleshooting

### macOS: "Start-BillingAdjustments-Mac.command cannot be opened because Apple cannot check it for malicious software"

When you first launch `Start-BillingAdjustments-Mac.command`, macOS Gatekeeper may block it
with a message like *"cannot be opened because Apple cannot check it for malicious software"*
(or *"... from an unidentified developer"*). This happens because the file was downloaded
from the internet and carries a `com.apple.quarantine` flag. Clear the flag and make the
script executable:

1. Open Terminal and `cd` to the folder where you downloaded/unzipped the kit (adjust the
   path to wherever the `partner-kit` folder actually is):

   ```bash
   cd ~/Downloads
   ```

2. Remove the quarantine flag from the whole kit (recursively):

   ```bash
   xattr -dr com.apple.quarantine partner-kit
   ```

3. Confirm the flag is gone:

   ```bash
   xattr partner-kit/webapp/Start-BillingAdjustments-Mac.command
   ```

   If `com.apple.quarantine` is **no longer listed** in the output, it worked. (No output at
   all also means there are no extended attributes left, which is fine.)

4. Make the launcher executable:

   ```bash
   chmod +x partner-kit/webapp/Start-BillingAdjustments-Mac.command
   ```

5. Run it — either double-click `Start-BillingAdjustments-Mac.command` in Finder, or run it
   from Terminal:

   ```bash
   ~/Downloads/partner-kit/webapp/Start-BillingAdjustments-Mac.command
   ```

> Tip: if you only want to clear the flag on the one launcher (not the whole kit), point the
> `xattr -dr com.apple.quarantine` command at the `.command` file directly instead of the
> `partner-kit` folder.

## Configuration and operational rules

### Settings (in `core/engine.py`)

These constants near the top of the shared engine control its behavior:

| Setting | Default | Meaning |
|---------|---------|---------|
| `CSV_FILE` | `adjustmentFiles/sample_company.csv` | Default input file when none is passed on the command line |
| `BATCH_SIZE` | `5` | Max invoices per `BatchCreateBillingAdjustmentRequest` call |
| `CALLS_PER_SECOND` | `2` | Client-side API rate limit (TPS) |
| `DELAY_BETWEEN_BATCHES` | `1.0 / CALLS_PER_SECOND` (0.5s) | Pause between API calls to honor the rate limit |
| `POLL_INTERVAL` | `60` | Seconds between status polls while waiting for a phase to complete |
| `MAX_POLL_TIME` | `600` | Max seconds to wait for a phase before marking remaining requests `TIMEOUT` |
| `CURRENCY_CODE` | `USD` | Currency sent with each adjustment. The tool currently supports **USD only** — see [Input file format → Currency](#currency). |
| `ADJUSTMENT_REASON` | `OTHER` | `adjustmentReasonCode` sent with each adjustment |
| `ENDPOINT_URL` | `https://agreement-marketplace.us-east-1.amazonaws.com` | Marketplace Agreement API endpoint |
| `COL_AMOUNT_OPTIONS` | `refund_amount`, `SUM of Calculated Refund (T-Y)` | Accepted names for the amount column in the input CSV |

(Both the web app and the CLI use the shared engine in `core/engine.py`; these
constants live there. `CSV_FILE` is a CLI-only default in
`cli/billing_adjustment_bulk_sdk_creds.py`.)

### Retries on credential failure

If AWS credentials are expired or invalid, the tool retries up to **3 times**
(`max_retries = 3` in `execute_with_retry`). The CLI prompts you to refresh
credentials between attempts; the web app pauses the job and asks for fresh
credentials in the UI. Separately, the boto3 client is configured with
`retries={'max_attempts': 3, 'mode': 'adaptive'}` to absorb transient errors and
throttling.

### Idempotency guardrail (no duplicate refunds)

Every adjustment uses a **deterministic client token**, generated as a UUID5 from
`agreement_id:invoice_id` with a fixed namespace. The same invoice on the same
agreement always produces the same token, so re-running the same file — or retrying
after an interruption — will not create a duplicate refund. The Marketplace API
treats a repeated client token as the same request and returns the existing result
instead of creating a new adjustment.

This means the tool issues **at most one refund per invoice + agreement**. That is a
deliberate safety choice: a refund that has already been submitted (including by an
earlier run, or by a partner already using this scheme) cannot be accidentally
submitted again.

**Input rule — one record per `<invoice, agreement>`.** Because the client token is
derived from `agreement_id` + `invoice_id`, your input file must **not** contain more
than one row with the same invoice and agreement combination. Two such rows produce
the **same** client token, so only the first is processed and the second is treated
as a duplicate (it will not create a second refund). Before submitting, de-duplicate
your file so each `<invoice, agreement>` appears at most once.

**Recommended: aggregate dimension-split rows.** If your data has several rows for
the same `<agreement, invoice>` that differ only by dimension (or line item), combine
them into a **single row with the aggregated refund amount** instead of submitting
them separately. Keeping each `<agreement, invoice>` unique in the refund file avoids
rows being set aside as duplicates for review and shortens the time needed to process
the request. This is the **recommended approach** — prefer it over customizing the
client token to add more fields (see [Customizing the client token](#customizing-the-client-token)):
aggregating keeps the input clean and the idempotency guarantee simple, with no code
changes. To confirm an `<agreement, invoice>` hasn't already been refunded, run
**Check processed refunds** (web UI) or `check_processed_refunds.py` (CLI) before
submitting.

**Idempotency window: 8 hours.** The client token is honored by the Marketplace API
for **8 hours** from the first request. What this means in practice:

- **Within 8 hours:** re-submitting the same `<invoice, agreement>` (same token)
  returns the original result and does **not** create a new refund. This protects
  you from accidental re-runs, retries, and double-submits during a working session.
- **After 8 hours:** the token is no longer remembered, so the *same* token could be
  accepted as a *new* request — which could create a second refund for that invoice.
  Do not rely on the token to prevent duplicates across days. The durable backstop is
  the per-invoice `maxAdjustmentAmount`: once an invoice has been refunded up to its
  maximum, further refunds are rejected regardless of the token.

> **Recommended pre-flight: reconcile the input file before you submit.** Because the
> 8-hour window can lapse between runs, the reliable way to avoid an accidental second
> refund is to reconcile the *exact file you are about to submit* against the service
> first — run **Check processed refunds** (web UI) or
> `python check_processed_refunds.py <your-file.csv>` (CLI). Any `<agreement, invoice>`
> that comes back in the **processed** output has already been refunded; treat that as a
> warning to remove those rows (or confirm you truly intend to refund them again) before
> running the live submit. This check does **not** depend on the idempotency window — it
> works no matter how long ago the prior run happened, so it is the safest guard once
> more than 8 hours may have passed.

**Built-in live pre-check (automatic).** You don't have to remember to reconcile first —
every **live run checks each `<agreement, invoice>` against the service immediately
before submitting it.** If an existing `COMPLETED` or `PENDING` adjustment request is
found, that row is **skipped** (status `ALREADY_PROCESSED`, the existing request id is
recorded) instead of being resubmitted. Rows whose only prior request is
`VALIDATION_FAILED` (no refund happened) are still submitted, so genuine retries are not
blocked. This is what protects you once the 8-hour idempotency window has lapsed, and it
is **on by default**. It also runs during a **dry run** (when enabled) as a preview, so
the dry-run report labels already-refunded rows `ALREADY_PROCESSED` and the `DRY_RUN_OK`
count reflects only genuinely new refunds — a warning before you commit to the live run.
The CLI exposes `--no-precheck` to skip it (faster, for a verified
fresh batch); the web app runs it automatically. Skipped rows appear in the run output —
`already_processed_<input>_<timestamp>.csv` (CLI) or the job's `records` with status
`ALREADY_PROCESSED` (web) — so you can review them with **Check one request** /
`get_adjustment_request.py`.

**Trade-off:** because the amount is intentionally *not* part of the token, you
cannot issue two different refunds against the same invoice and agreement through the
tool — the second would be treated as a duplicate of the first (within the 8-hour
window). If you genuinely need multiple distinct refunds per invoice, change the
token input in `generate_client_token` (in `core/engine.py`) to include an additional
value such as the amount or a per-row reference id. Do this only if no refunds have
been submitted under the current scheme, otherwise previously-submitted refunds could
be duplicated.

### Customizing the client token

> **Most users don't need this.** If you only need to handle multiple line items for
> the same `<agreement, invoice>`, the **recommended approach is to aggregate them
> into one row** with the total amount (see *Input rule* above) — not to customize the
> token. Customize the token only if you genuinely need a different idempotency scope.

The client token is the single knob that controls idempotency. It is built in
`generate_client_token()` in `core/engine.py` from `agreement_id` + `invoice_id`:

```python
def generate_client_token(agreement_id, invoice_id):
    key = f"{agreement_id}:{invoice_id}"
    return str(uuid.uuid5(CLIENT_TOKEN_NAMESPACE, key))
```

You may want to fold **more fields from your input file** into that key — for example
the **refund amount**, the **AWS account id**, or a per-line **dimension / reference
id** — to change what counts as "the same request":

- **Add `refund_amount`** → lets you submit *different* amounts for the same
  `<agreement, invoice>` (each distinct amount becomes a distinct token). This removes
  the built-in "at most one refund per invoice + agreement" guard.
- **Add `aws_account_id` / a dimension id / a reference id** → scopes idempotency to
  your own line-item granularity rather than the whole invoice.

> **⚠️ Change this before you submit anything in production.** Idempotency only works
> while the token formula is stable. If you change the formula *after* refunds have
> been submitted under the old one, the new tokens won't match the old ones, so
> invoices already refunded could be **submitted again** (bounded only by each
> invoice's `maxAdjustmentAmount`). Only customize on a fresh setup, or when you fully
> accept the re-submission implications.

You don't have to hand-edit the code — you can have an AI coding tool (Kiro, Claude
Code, Cursor, etc.) make the change. Open this repo in the tool and paste a prompt
like the following, editing the field list to match your file:

> In `core/engine.py`, the function `generate_client_token(agreement_id, invoice_id)`
> builds a deterministic UUID5 idempotency token from `agreement_id` and `invoice_id`.
> I want the token to also incorporate the **refund amount** and the **AWS account
> id** (and an optional reference/dimension id when present) so that distinct
> amounts/accounts are treated as distinct requests. Update `generate_client_token`
> to accept these extra fields and include them in the hashed key in a stable,
> documented order, keeping the existing `CLIENT_TOKEN_NAMESPACE`. Then update every
> caller so they pass the new fields from each input row — `_create_batch_entries` in
> `core/engine.py` and any callers in `cli/billing_adjustment_bulk_sdk_creds.py` (the
> row dicts already carry `amount` and `aws_account_id`). Don't change unrelated
> behavior, add a short docstring note explaining the new key format and that changing
> it after production submissions can cause re-submission of already-refunded
> invoices, and show me the diff before applying.

After the change, run a **dry run** first and confirm the results look right before
any live submission.

### Batching rule

Adjustments are submitted with `BatchCreateBillingAdjustmentRequest`, which accepts
**up to 5 invoices per call, and every entry in a batch must share the same
`agreementId`**. The tool enforces this by grouping rows by agreement and then
chunking each agreement's rows into batches of at most 5. Invoices for different
agreements are never mixed in one call.

### Service quotas

The client-side rate limit (`CALLS_PER_SECOND = 2`) is aligned with the AWS
Marketplace Agreement Service quotas. Key per-second limits:

| Operation | Quota |
|-----------|-------|
| `BatchCreateBillingAdjustmentRequest` | 2 / second (the binding limit) |
| `GetBillingAdjustmentRequest` | 5 / second |
| `ListAgreementInvoiceLineItems` | 10 / second |

Full, authoritative list: [Service quotas for AWS Marketplace Agreement API](https://docs.aws.amazon.com/marketplace/latest/APIReference/agreement-service-quotas.html).
These are default quotas and may change; check the doc for current values.

### Requirements

- **Python** 3.8 or later.
- **boto3 / botocore 1.42.80 or later** — this is the release that added the
  Marketplace Agreement billing-adjustment APIs (`BatchCreateBillingAdjustmentRequest`,
  `GetBillingAdjustmentRequest`, `ListBillingAdjustmentRequests`,
  `ListAgreementInvoiceLineItems`). Earlier versions do **not** include these
  operations and the tool will not run.
- For the AWS CLI (used by the Postman/manual workflow), v2.34.21 or later.

## Delivering to external partners

Build a self-contained kit (web app + deploy templates + instructions + sample) for
a partner's engineer:

```bash
./build-partner-kit.sh   # produces resource/BillingAdjustments-Partner-Kit.zip
```

Deliver the zip via a secure channel (e.g. an S3 pre-signed link). See
[`partner-kit/README.md`](partner-kit/README.md).

## Data handling

This repository contains **no real customer data and no credentials** — only dummy
sample inputs (`cli/adjustmentFiles/sample_company.csv`) and example outputs. Real
input files and run results are gitignored.

## License

This application is part of the AWS Marketplace API Reference Code Library and is
licensed under the same terms as the rest of the repository — see the root
[LICENSE](../../LICENSE) (MIT-0).
