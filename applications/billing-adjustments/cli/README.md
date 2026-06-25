# AWS Marketplace Bulk Billing Adjustment Workflow

## Overview

Process bulk billing adjustments (refunds) for AWS Marketplace sellers using the Marketplace Billing Adjustments API. This toolset provides:

- **`billing_adjustment_bulk_sdk_creds.py`** — Validates and submits billing adjustments in bulk from a CSV file
- **`check_adjustment_status.py`** — Checks the status of previously submitted adjustment requests
- **`check_processed_refunds.py`** — Reconciles a refund input file against the service: lists each agreement's requests, confirms which input invoices were processed, and writes a processed file and a not-processed file
- **`clean_refund_file.py`** — Pre-flight cleaner: splits an input file into a cleaned file (safe to submit, de-duplicated) and a `needs_review` file (invalid or duplicate rows, with a reason). Does not call AWS
- **`list_adjustment_requests.py`** — Queries `ListBillingAdjustmentRequests` across one or more agreements with optional status/date filters (CSV output)
- **`get_adjustment_request.py`** — Looks up a single request (or a file of pairs) via `GetBillingAdjustmentRequest`

> To explore the underlying APIs interactively (request by request), see the published
> [Postman collection](https://www.postman.com/aws-partners/aws-marketplace/collection/38157848-955c413d-92d7-4ef3-b8dc-021f5321d941)
> in the AWS Partners workspace.

> **Common information** — the input file format, amount/currency rules, run-output
> statuses, idempotency behavior, error codes, and service quotas are documented once
> in the **[main README](../README.md)**. This guide covers only CLI-specific setup
> and usage.
>
> These scripts are **thin wrappers over the shared `core/` engine** (the same engine
> the web app uses), so their validation, batching, idempotency, and statuses match
> the web app exactly.

## Prerequisites

- Python 3.8+
- boto3 / botocore 1.42.80+ (the release that added the billing-adjustment APIs;
  installed via `pip install -r ../requirements.txt`)
- AWS CLI v2.34.21+ (only needed for the manual/Postman workflow)
- IAM user/role with appropriate permissions (see IAM Setup below)
- CSV file with adjustment data (see Input Format below)
- `pip install -r ../requirements.txt`

> Run the commands in this guide from inside the `cli/` directory. The scripts
> default to reading inputs from `adjustmentFiles/` and writing results to the
> current directory, both relative to where you run them.

---

## IAM Setup

The IAM identity needs permissions to call the Marketplace Agreement billing adjustment APIs.

### Option 1: Full Access (Recommended for simplicity)

Attach the managed policy `AWSMarketplaceSellerFullAccess`:

```bash
aws iam attach-user-policy \
  --user-name <your-iam-user> \
  --policy-arn arn:aws:iam::aws:policy/AWSMarketplaceSellerFullAccess
```

> **Security caution.** `AWSMarketplaceSellerFullAccess` is convenient but **broad** —
> it grants access to *all* mutating seller actions (not just billing adjustments).
> The least-privilege custom policy in Option 2 is the recommended choice for
> production; only use full access in low-risk/test accounts, and exercise caution
> about who holds the credentials.

### Option 2: Minimal Permissions (Custom Policy)

Create a custom policy with only the required API permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:BatchCreateBillingAdjustmentRequest",
        "aws-marketplace:GetBillingAdjustmentRequest",
        "aws-marketplace:ListBillingAdjustmentRequests",
        "aws-marketplace:ListAgreementInvoiceLineItems",
        "aws-marketplace:SearchAgreements",
        "aws-marketplace:DescribeAgreement",
        "aws-marketplace:GetAgreementTerms"
      ],
      "Resource": "*"
    }
  ]
}
```

To create and attach the custom policy:

```bash
# Create the policy
aws iam create-policy \
  --policy-name BillingAdjustmentAccess \
  --policy-document file://billing-adjustment-policy.json

# Attach to user
aws iam attach-user-policy \
  --user-name <your-iam-user> \
  --policy-arn arn:aws:iam::<account-id>:policy/BillingAdjustmentAccess
```

---

## AWS Credential Options

The scripts use the **AWS default credential chain**. Credentials are resolved in this order:

1. **Environment variables** — `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`
2. **Shared credentials file** — `~/.aws/credentials` under `[default]` profile
3. **AWS config file** — `~/.aws/config` (SSO, assume-role configs)
4. **AWS SSO** — if configured in the config file
5. **Container credentials** — ECS task role (if running in a container)
6. **Instance metadata** — EC2 instance profile (if running on EC2)

### Common Setup Methods

```bash
# Method 1: Configure default profile with access keys
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Method 2: SSO login
aws sso login --profile <your-profile>
export AWS_PROFILE=<your-profile>

# Method 3: Environment variables (e.g., from assume-role)
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
```

If credentials expire mid-run, the script will pause and prompt you to refresh before continuing.

---

## Input CSV Format

Place CSV files in the `adjustmentFiles/` directory. Required columns:

| Column | Required | Description |
|--------|----------|-------------|
| `agreement_id` | Yes | AWS Marketplace agreement ID (e.g., `agmt-abc123...`) |
| `invoice_id` | Yes | Invoice ID to adjust |
| `refund_amount` | Yes* | Amount to refund (supports `$1,234.56` format) |

Optional columns (preserved for reference but not used in API calls):
- `seller_id`
- `aws_account_id`
- `product_code`
- `month_id`

> **Currency (USD only) and the fixed `OTHER` reason code** are documented in the
> [main README → Currency](../README.md#currency) and
> [Adjustment reason code](../README.md#adjustment-reason-code). There is no currency
> or reason-code column.

> **Each `<invoice_id, agreement_id>` combination must appear at most once in the
> file.** Duplicate combinations generate the same client token, so only the first is
> processed and the rest are treated as duplicates (no additional refund). De-duplicate
> your file before running.

### Sample CSV (`adjustmentFiles/sample_company.csv`)

```csv
seller_id,aws_account_id,invoice_id,product_code,month_id,refund_amount,agreement_id
123456789012,111222333444,2500000001,prod-abc123def456g,25-Jun,$150.00 ,agmt-exampleagreement1abcdefg
123456789012,111222333444,2500000001,prod-xyz789ghi012j,25-Jun,$75.50 ,agmt-exampleagreement2hijklmn
123456789012,111222333444,2500000002,prod-abc123def456g,25-Jul,"$1,200.00 ",agmt-exampleagreement1abcdefg
123456789012,555666777888,2500000003,prod-abc123def456g,25-Jul,$320.25 ,agmt-exampleagreement3opqrstu
123456789012,555666777888,2500000003,prod-xyz789ghi012j,25-Jul,$45.00 ,agmt-exampleagreement4vwxyz01
123456789012,555666777888,2500000004,prod-abc123def456g,25-Aug,$890.00 ,agmt-exampleagreement3opqrstu
```

### Amount formatting

Amounts may include `$`, commas, and surrounding spaces (e.g. `"$1,341.70 "` →
`1341.70`). The full amount and currency rules are in the
[main README → Input file format](../README.md#input-file-format).

---

## Usage

### Dry Run (Recommended First Step)

Validates all rows against the API without submitting any adjustments. Also checks whether the aggregate refund per invoice exceeds the allowed maximum.

```bash
python billing_adjustment_bulk_sdk_creds.py --dry-run adjustmentFiles/sample_company.csv
```

Dry-run will:
- Verify each invoice exists for the given agreement
- Check that each row's amount does not exceed `maxAdjustmentAmount`
- Check that the **total** requested across all rows for the same invoice does not exceed `maxAdjustmentAmount`
- Report any validation failures with specific error messages

### Live Submission

```bash
python billing_adjustment_bulk_sdk_creds.py adjustmentFiles/sample_company.csv
```

If no CSV file is specified, defaults to `adjustmentFiles/sample_company.csv`.

> **Invalid and duplicate rows are handled automatically.** Before processing, the
> script splits the input into rows that are safe to submit and rows that need
> review. Rows with a missing or placeholder `agreement_id`/`invoice_id` (e.g.
> `#N/A`), a non-positive/invalid amount, or a duplicate `<agreement, invoice>`
> combination are written to `needs_review_<input>_<timestamp>.csv` (original columns
> plus a `review_reason`) and are **not** submitted. Only the first occurrence of
> each `<agreement, invoice>` is processed. The path is also recorded in the results
> JSON under `needs_review_file`.

### Clean a File Without Submitting (Pre-flight)

To split a file into a cleaned file and a needs-review file **without** calling AWS:

```bash
python clean_refund_file.py adjustmentFiles/sample_company.csv
# optional output directory
python clean_refund_file.py "MongoDb/AWS Latest MP Refund List 2026-05-01 - AWS.csv" --output-dir ./out
```

Outputs:
- `cleaned_<input>_<timestamp>.csv` — safe-to-submit rows, de-duplicated, original columns.
- `needs_review_<input>_<timestamp>.csv` — invalid + duplicate rows, original columns plus `review_reason`.

The script prints a breakdown of how many rows were flagged and why.

### Check Status of Previous Run

```bash
python check_adjustment_status.py adjustment_results_20260408_125207.json
```

### Reconcile a Refund File (Check Which Refunds Were Processed)

Use the **same CSV file** you submitted for refunds. For each agreement id the script
calls `ListBillingAdjustmentRequests` (all statuses), checks whether each input
`invoice_id` appears in the returned list, and confirms each match with
`GetBillingAdjustmentRequest`.

```bash
python check_processed_refunds.py adjustmentFiles/sample_company.csv
# optional: choose where the two output files are written
python check_processed_refunds.py refunds.csv --output-dir ./out
```

It writes two files (timestamped, with the input file name embedded):

- `processed_<input>_<timestamp>.csv` — confirmed refunds, with all the fields returned
  by `GetBillingAdjustmentRequest` (`billingAdjustmentRequestId`, `agreementId`,
  `originalInvoiceId`, `matchedInvoiceId`, `adjustmentAmount`, `currencyCode`, `status`,
  `statusMessage`, `adjustmentReasonCode`, `description`, `createdAt`, `updatedAt`).
- `not_processed_<input>_<timestamp>.csv` — rows whose invoice was **not** found, in the
  **original input file format** (all original columns preserved). If listing fails for
  an agreement, its rows are placed here and the error is reported.

The same reconciliation is available in the web UI under **Check processed refunds**.

### Query Adjustment Requests (Filtered List)

```bash
# one or more agreement IDs
python list_adjustment_requests.py agmt-aaa agmt-bbb

# from a newline/comma-delimited file, only COMPLETED, in a date range
python list_adjustment_requests.py --agreements-file ids.txt \
    --status COMPLETED --created-after 2026-06-01 --created-before 2026-06-30
```

### Look Up One Request

```bash
python get_adjustment_request.py agmt-aaa ba-xxxx
# or a file of "agreement_id,request_id" pairs
python get_adjustment_request.py --file pairs.csv
```

---

## How It Works

### Processing Pipeline

1. **Load CSV** — Parse rows, identify amount column, skip rows without `agreement_id`
2. **Detect duplicates** — Find invoice IDs appearing in multiple agreements (these cause conflicts if submitted concurrently)
3. **Phase grouping** — Group rows by invoice occurrence order. If invoice X appears in 3 agreements, it runs in 3 separate phases
4. **Validate** — For each row, call `ListAgreementInvoiceLineItems` to verify the invoice exists and amount is within limits
5. **Submit** — Batch up to 5 entries per agreement per API call via `BatchCreateBillingAdjustmentRequest`
6. **Poll** — Wait for each phase to complete before starting the next (60s poll interval)

### Rate Limiting

- API calls: 2 TPS
- Batch size: max 5 invoices per API call (all must share the same agreement)
- Phase transitions: 60s polling interval between status checks

### Idempotency

The CLI uses **deterministic client tokens** (`agreement_id:invoice_id`), so re-running
the same file won't create duplicate refunds. There's an **8-hour idempotency window**,
and your input must contain **at most one row per `<invoice, agreement>`**. Full details
— including the window semantics and the per-invoice `maxAdjustmentAmount` backstop —
are in the [main README → Idempotency guardrail](../README.md#idempotency-guardrail-no-duplicate-refunds).

---

## Output Format

Results are saved to `adjustment_results_<input_file>_<mode>_YYYYMMDD_HHMMSS.json` in
the current directory, where `<mode>` is `dryrun` for a dry run or `prod` for a live
run. The input file name and mode are included so you can tell which output belongs
to which input and whether it was a validation-only run. Examples:

- `test_refunds.csv` dry run → `adjustment_results_test_refunds_dryrun_20260617_102705.json`
- `test_refunds.csv` live run → `adjustment_results_test_refunds_prod_20260617_102705.json`

### Structure

```json
{
  "timestamp": "2026-04-08T12:52:07.396622",
  "mode": "live",
  "csv_file": "adjustmentFiles/sample_company.csv",
  "total_rows": 6,
  "total_phases": 2,
  "duplicate_invoices": {
    "2500000001": ["agmt-example1...", "agmt-example2..."]
  },
  "summary": {
    "validation_failed": 1,
    "submit_failed": 0,
    "submitted": 5,
    "completed": 5,
    "completion_failed": 0,
    "pending": 0,
    "amount_totals": {
      "currency": "USD",
      "submitted": 2685.75,
      "completed": 2685.75,
      "failed": 45.00
    }
  },
  "row_results": [
    {
      "invoice_id": "2500000001",
      "agreement_id": "agmt-example1...",
      "amount": "150.00",
      "request_id": "ba-abc123...",
      "client_token": "424022e4-...",
      "status": "COMPLETED",
      "error": null
    }
  ]
}
```

### Dry-Run Output

In dry-run mode, the output includes:
- `"mode": "dry_run"`
- Rows that pass validation have status `DRY_RUN_OK`
- An `aggregate_warnings` array if any invoice's total requested amount exceeds its maximum

```json
{
  "summary": {
    "validation_failed": 1,
    "dry_run_ok": 5
  },
  "aggregate_warnings": [
    {
      "invoice_id": "2500000001",
      "total_requested": 225.50,
      "max_adjustment_amount": "200.00",
      "row_count": 2
    }
  ]
}
```

### Status Values

The CLI now shares the engine in `core/`, so it emits the **same** status values as the
web app:

| Status | Meaning |
|--------|---------|
| `DRY_RUN_OK` | Passed validation in dry-run (not submitted) |
| `VALIDATION_FAILED` | Invoice not found, non-adjustable type, or amount exceeds max (pre-submit) |
| `SUBMIT_FAILED` | The create call (`BatchCreateBillingAdjustmentRequest`) was rejected |
| `COMPLETED` | Adjustment processed successfully |
| `ERROR` | Service returned an error status while polling |
| `TIMEOUT` | Did not complete within the polling window (10 min) |

> The conceptual difference between `VALIDATION_FAILED` (rejected pre-submit) and
> `SUBMIT_FAILED` (the create call failed), and the full status list, are in the
> [main README → Run output statuses](../README.md#run-output-statuses).

### Summary Counters

| Counter | Description |
|---------|-------------|
| `validation_failed` | Rows that failed pre-submission validation |
| `submit_failed` | Rows that the API rejected at submission time |
| `submitted` | Rows successfully sent to the API |
| `completed` | Rows confirmed as fully processed |
| `completion_failed` | Rows that were submitted but failed during processing |
| `pending` | Rows submitted but not yet confirmed (polling timed out) |

In addition to these counts, the summary includes an **`amount_totals`** object with the
dollar value (in `CURRENCY_CODE`, i.e. USD) of `submitted`, `completed`, and `failed`
requests, so you can see the financial total alongside the row counts.

---

## Handling Duplicate Invoices

The same invoice ID can appear across multiple agreements because one invoice may contain charges from multiple products/agreements. If the same invoice ID is submitted concurrently across different agreements, a `CONFLICT_EXCEPTION` will occur.

The script handles this by:
1. Grouping rows by invoice occurrence order into phases
2. Processing Phase 1 (first occurrence of each invoice) immediately
3. Polling `GetBillingAdjustmentRequest` until Phase N-1 completes (60s poll interval)
4. Then processing Phase N

---

## Common Errors

See the [main README → Common errors and error codes](../README.md#common-errors-and-error-codes)
for the shared list (`ResourceNotFoundException`, `REFUND_AMOUNT_EXCEEDS_MAXIMUM`,
`CONFLICT_EXCEPTION`, KYC, `ExpiredTokenException`, etc.).

---

## Execution Checklist

- [ ] Set up AWS credentials (see Credential Options above)
- [ ] Place CSV file in `adjustmentFiles/` with required columns
- [ ] Run dry-run: `python billing_adjustment_bulk_sdk_creds.py --dry-run <file.csv>`
- [ ] Review dry-run output — check for validation failures and aggregate warnings
- [ ] Run live: `python billing_adjustment_bulk_sdk_creds.py <file.csv>`
- [ ] Monitor output — script shows real-time progress
- [ ] Check results JSON for any `SUBMIT_FAILED` or `TIMEOUT` entries
- [ ] For timed-out entries, use: `python check_adjustment_status.py <results_file.json>`

---

## Processing Time Estimates

| Metric | Formula |
|--------|---------|
| Validation API calls | 1 per row |
| Batch submission calls | ceil(rows_per_agreement / 5) per agreement |
| API time | total_calls / 2 TPS |
| Phase wait time | (num_phases - 1) × 60s |
| **Total time** | API time + phase wait time |

For large files (1000+ rows with many phases), expect 1-2 hours. Start with smaller files for testing.

### Recommendations

1. **Start small** — Test with `sample_company.csv` or a small subset of your data
2. **Run dry-run first** — Always validate before submitting
3. **Run overnight for large files** — Files with many phases have long polling waits
4. **Resume after interruption** — Check the output JSON for completed adjustments, create a new CSV with remaining rows
