# Example output files (web app)

These are **example** results so you know what the app produces. They use dummy data.

When a job finishes, the UI offers three downloads (named after your uploaded file —
here the upload was `test_sample.csv`):

| Download | Example file | What it is |
|----------|--------------|------------|
| **CSV (readable)** | `test_sample_csv.csv` | One row per invoice with its final status — the human-friendly result. |
| **Summary (JSON)** | `test_sample_json.json` | Totals, phases, duplicate invoices, and start/finish times. |
| **Records (JSON lines)** | `test_sample_jsonl.jsonl` | One JSON object per invoice (machine-readable, one line each). |

Each invoice's `status` is one of: `COMPLETED`, `VALIDATION_FAILED`, `SUBMIT_FAILED`,
`TIMEOUT`, or `DRY_RUN_OK` (dry-run mode). Failed rows include a reason in `message`.
