# Example output file (CLI)

`adjustment_results_example.json` is an **example** of what the CLI writes after a run,
so you know what to expect. It uses dummy data.

Each real run writes a timestamped file to the current directory, e.g.
`adjustment_results_sample_company_prod_20260612_101542.json` — the input file name
and the run mode (`prod` for a live run, `dryrun` for a dry run) are included so you
can match each output to its input and tell which were validation-only. The structure:

- `mode` — `live` or `dry_run`
- `summary` — counters (`completed`, `validation_failed`, `submit_failed`, `pending`, etc.)
- `row_results` — one entry per invoice with its `status`, `request_id`, and any `error`
- `duplicate_invoices` — invoices that appear under more than one agreement
- `aggregate_warnings` — (dry-run only) invoices whose total requested amount exceeds the max

Check the status of submitted requests later with:

```bash
python check_adjustment_status.py adjustment_results_example.json
```
