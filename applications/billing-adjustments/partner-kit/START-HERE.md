# Billing Adjustments — Partner Kit (engineer start here)

This kit lets an external partner run AWS Marketplace **bulk billing adjustments**
through a simple web UI. It is meant to be set up by an **engineer** (the partner's
or a supporting engineer), then handed to non-technical (accounting) users.

## What's in this kit

```
START-HERE.md            <- this file
README.md                <- main reference (input format, statuses, errors, idempotency, quotas)
CROSS-ACCOUNT-WALKTHROUGH.md  <- step-by-step for the "app in one account, agreements in another" setup
sample_input.csv         <- example input file (dummy data) showing the required format
requirements.txt         <- Python dependencies (for the local / CLI options)
webapp/                  <- the web application (source) + its README
cli/                     <- command-line scripts + README (alternative to the web UI)
deploy/                  <- Dockerfile + CloudFormation templates to deploy into AWS
```

> For all common information — the input file format, currencies, run-output statuses,
> idempotency behavior, error codes, and service quotas — see **`README.md`** (the main
> reference, included in this kit).

## Pick how to run it

There are two supported ways. Choose based on the partner's needs.

### Option A — Run locally (fastest to try)

Good for a quick start or a single user on one machine. The user enters their own
AWS credentials in the UI; nothing is installed beyond Python packages.

1. Install Python 3.8+ and dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start it:
   ```bash
   cd webapp
   python app.py
   ```
3. A browser opens at http://127.0.0.1:5050. Upload `sample_input.csv` (or real data),
   enter AWS credentials, keep **Dry run** checked first, then **Start job**.

Non-technical users can instead double-click the launcher in `webapp/`:
- macOS: `Start-BillingAdjustments-Mac.command`
- Windows: `Start-BillingAdjustments-Windows.bat`

See `webapp/README.md` for full details, including the dry-run vs live-run behavior
and how expired credentials are handled.

### Option B — Deploy into the partner's AWS account (recommended for partners)

Runs the app on AWS App Runner inside the partner's account. Users get a URL and a
password — **no AWS credentials are ever entered**, because the app uses an IAM role.
Optionally, it can assume a role in a *different* account that owns the agreements.

Full step-by-step (build image, deploy CloudFormation, cross-account setup, teardown)
is in **`deploy/README.md`**. For the specific "app in one account, agreements in
another account" setup, see **`CROSS-ACCOUNT-WALKTHROUGH.md`** — a complete worked
runbook with copy-paste commands.

Quick outline:
1. Build and push the container image to the partner's ECR (`deploy/publish-image.sh`).
2. Deploy `deploy/cloudformation.yaml` with an access password.
3. (Cross-account only) Deploy `deploy/cross-account-role-target.yaml` in the
   account that owns the agreements, and pass its role ARN + external ID to the app.
4. Share the App Runner URL + password with the users.

### Option C — Run the CLI (for engineers)

Prefer the command line, or want to script/automate? The same workflow is available as
CLI scripts in `cli/` (validate, dry-run, submit, reconcile, look-ups). Engineers can
run these directly with their own AWS credentials:

```bash
pip install -r requirements.txt
cd cli
python billing_adjustment_bulk_sdk_creds.py --dry-run adjustmentFiles/sample_company.csv
```

See `cli/README.md` for full CLI setup, IAM permissions, and all commands.

## Required input file format

The uploaded file must be a `.csv` with the header row shown in `sample_input.csv`.
The **full format spec** — columns, data types, Excel/CSV tips, amount and currency
rules — is in **`README.md` → Input file format** (the main reference in this kit).
The required columns are `seller_id`, `aws_account_id`, `invoice_id`, `product_code`,
`month_id`, `refund_amount`, and `agreement_id`.

The UI has a **Check file format** button that validates the file before running.

## Important notes for the engineer

- **Verify IAM action names.** The deploy templates use the `aws-marketplace:`
  namespace for the four billing-adjustment actions. Confirm them against the AWS
  Service Authorization Reference before production (noted in `deploy/README.md`).
- **Access control.** When deployed (Option B), the app requires an access password
  and uses an IAM role, so it refuses to start without a password set.
- **Dry run is read-only.** It validates invoice existence and amount limits but does
  NOT catch submit-time errors (e.g. compliance/KYC). Always review the live-run CSV.
- **Idempotency.** Submissions use a deterministic client token per
  (agreement_id, invoice_id), so re-running won't create duplicate adjustments. The
  API honors this for an **8-hour window**. Your input file must contain **at most
  one row per `<invoice, agreement>`** — duplicate combinations share a token and
  only the first is processed.
- This kit contains **no credentials and no real account/agreement data.** The
  sample file uses placeholder values only.
