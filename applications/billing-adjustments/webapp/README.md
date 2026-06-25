# Billing Adjustments Web UI

A simple web interface for non-technical (accounting) users to run AWS Marketplace
billing adjustments without using the command line.

> **Common information** — input file format, currencies, run-output statuses,
> idempotency, error codes, and quotas — is in the **[main README](../README.md)**.
> This guide covers only the web-UI-specific behavior.

## Features

1. **File upload with format guide** — In-page guide shows the required CSV columns,
   plus a **Check file format** button that validates the file before running.
2. **Dry run + downloadable output** — Tick "Dry run" to validate only (no
   adjustments submitted). Results are downloadable as a readable CSV.
3. **Background jobs** — Jobs run in the background and keep running even if you
   close the page. Reopen the page and use "Job history" to track or download results.
4. **Readable CSV logs** — In addition to JSON, every record is written to a
   human-readable CSV (`records.csv`) with status per invoice.
5. **Credentials from the UI** — Enter access key, secret key, and an optional
   session token. Credentials are kept in memory only for the duration of the job
   and are never written to disk.
6. **Incremental recording** — Each invoice's result (success/failure) is written
   to the output files the moment it is resolved, not only at the end. If a job is
   interrupted, completed records are already saved.
7. **Handles expired temporary credentials** — If temporary credentials expire
   while a job is running, the job automatically **pauses** instead of failing. The
   UI shows a prompt to paste fresh credentials, and the job **resumes from where it
   left off**. Already-processed records are not repeated (submissions use
   deterministic client tokens for idempotency).
8. **Check processed refunds (reconciliation)** — A left-nav view that takes the
   **same refund CSV** you submitted and confirms which invoices were actually
   processed. For each agreement it lists adjustment requests
   (`ListBillingAdjustmentRequests`) and confirms matches with
   `GetBillingAdjustmentRequest`. It returns two downloadable CSVs: **processed**
   (full request detail) and **not processed** (original file format).
9. **Check one request** — Look up a single adjustment request by agreement ID and
   billing adjustment request ID (`GetBillingAdjustmentRequest`).
10. **Automatic invalid/duplicate handling** — On submit, rows that can't be
    processed are not allowed to block the run. Rows with a missing/placeholder
    `agreement_id` or `invoice_id` (e.g. `#N/A`), a bad amount, or a duplicate
    `<agreement, invoice>` combination are routed to a **Needs review** file. Only
    the clean, de-duplicated rows are submitted, and the run reports how many rows
    were set aside. Download the **Needs review** file (original columns plus a
    `review_reason`) from the job's download row to fix those entries separately.

## Install

```bash
pip install -r ../requirements.txt
```

## Run

```bash
cd webapp
python app.py
```

Then open http://127.0.0.1:5050 in a browser.

To use a different port:

```bash
PORT=8080 python app.py
```

## Dry run vs live run — what is actually checked

The **Dry run** option performs **read-only validation only**. For each row it calls
`ListAgreementInvoiceLineItems` and confirms:

1. **Invoice exists** under the given agreement ID.
2. **Invoice is adjustable** — it has a `maxAdjustmentAmount` and an eligible
   invoice type.
3. **Amount is within the limit** — the requested amount is ≤ `maxAdjustmentAmount`.
4. **Credentials/access work** — implicitly, since the read API call must succeed.

Dry run does **NOT** submit anything and therefore **cannot** catch errors that only
surface when the adjustment is actually submitted and processed server-side, including:

- **KYC / compliance failures** (e.g. an agreement that is not KYC-compliant) — these
  come back as a `VALIDATION_FAILED` status only **after** a live submission.
- **Conflicts** when the same invoice appears across multiple agreements processed
  close together (`CONFLICT_EXCEPTION`).
- **Agreement state issues** (expired, terminated, etc.).
- Any other server-side eligibility rule enforced at submit time.

> **Important:** A clean dry run means the invoices exist, are adjustable, and the
> amounts are within range. It is a useful pre-flight check, but it is **not** a
> guarantee that the live run will succeed. Compliance/KYC and other submit-time
> checks only appear in the **live run** results, where each record ends as
> `COMPLETED` or `VALIDATION_FAILED`. There is no API mode that simulates these
> submit-time checks without actually submitting.

After a live run, always review the downloadable CSV: the `status` column shows
`COMPLETED` for successful adjustments and `VALIDATION_FAILED` (with a reason in the
`message` column) for ones that were rejected at submit time.

## If your credentials expire mid-run

Temporary credentials (those with a session token) have a limited lifetime. If they
expire while a job is still running, the job does **not** fail — it **pauses** and
the page shows a highlighted prompt asking for fresh credentials. Paste a new access
key, secret key, and session token, click **Resume job**, and processing continues
from exactly where it stopped.

This is safe to do because:

- Records already processed are written to the output files immediately and are not
  redone.
- Submissions use a deterministic client token per invoice
  (`agreement_id` + `invoice_id`), so re-submitting the same invoice is idempotent
  and will not create a duplicate adjustment. This is honored by the API for an
  **8-hour window** — within 8 hours a repeat is recognized and skipped; after that
  the token is forgotten, so don't rely on it to block duplicates across days (the
  per-invoice maximum is the long-term safeguard).

> **Input rule:** your uploaded file must not contain more than one row with the same
> invoice and agreement. Duplicate `<invoice, agreement>` rows share a client token,
> so only the first is processed and the rest are treated as duplicates.

If you don't have fresh credentials handy, you can leave the job paused and come back
to it, or click **Cancel job** to stop it (already-processed records are kept).

## Delivering to non-technical users (no command line)

### Double-click launcher (requires Python installed once)

Give the user the whole `webapp` folder plus `requirements.txt`. They double-click:

- **Mac:** `Start-BillingAdjustments-Mac.command`
- **Windows:** `Start-BillingAdjustments-Windows.bat`

The launcher creates its own private environment, installs dependencies on the
first run, starts the app, and opens the browser automatically. Later runs start
immediately. The only prerequisite is that Python 3.8+ is installed once (the
launcher prints download instructions if it isn't).

> On Mac, the first time they may need to right-click the `.command` file > Open
> to get past the "unidentified developer" warning.

For a fully hosted experience with no local install at all, deploy the app into an
AWS account instead — see `../deploy/README.md`.


## Security notes

- This app does **not** add its own login. Run it on a trusted host (localhost or
  behind an authenticated reverse proxy / VPN).
- Serve over **HTTPS** in any shared environment, since AWS credentials are posted
  from the browser.
- Credentials are held in memory for the job only and are not persisted.
- Run with a **single worker process** (the default `python app.py`) so the
  in-memory job registry stays consistent. Background threads handle concurrency.

## Output files (per job, under `webapp/jobs/<job_id>/`)

| File | Description |
|------|-------------|
| `records.csv` | Human-readable, one row per invoice with status |
| `records.jsonl` | One JSON object per line (machine-readable, streamed) |
| `summary.json` | Final summary (totals, duplicates, timings) |
| `status.json` | Live job status used by the UI |

## Result statuses (the `status` column in `records.csv`)

Each invoice ends with a status such as `COMPLETED`, `DRY_RUN_OK`, `VALIDATION_FAILED`,
`SUBMIT_FAILED`, `ERROR`, or `TIMEOUT`. What each means — and the key difference
between `VALIDATION_FAILED` (rejected on the data; fix the input) and `SUBMIT_FAILED`
(the submit call broke; usually retry-safe) — is documented once in the
[main README → Run output statuses](../README.md#run-output-statuses).
