#!/usr/bin/env python3
"""
Bulk Billing Adjustment Script (CLI) — a thin adapter over the shared `core` engine.

All billing-adjustment logic (input parsing/validation, client/credentials, batching,
the deterministic client token, submission, polling, and the per-invoice aggregate
check) lives in `core/`. This script only:
  - parses CLI args,
  - splits the input into submit-able vs needs-review rows (core.classify_input_rows),
  - runs the engine (core.AdjustmentProcessor.run) against the default credential chain,
  - writes the results JSON and prints a summary.

Uses the default AWS credential chain (~/.aws/credentials default profile or env vars),
with an interactive "press ENTER to retry" prompt if credentials expire mid-run.

Usage:
  python billing_adjustment_bulk_sdk_creds.py [--dry-run] [csv_file]
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

import _cli_common  # noqa: F401  (adds repo root to sys.path for `core`)
from core import (
    classify_input_rows, generate_client_token, CredentialsCancelled,
    CURRENCY_CODE, REVIEW_REASON_COL,
)

CSV_FILE = "adjustmentFiles/sample_company.csv"


class _Collector:
    """Duck-typed RecordWriter: keeps each resolved record in memory."""

    def __init__(self):
        self.records = []

    def write(self, record):
        self.records.append(dict(record))


def write_needs_review_file(review_rows, columns, csv_file):
    """Write flagged rows to needs_review_<input>_<timestamp>.csv. Returns the path."""
    review_cols = list(columns)
    if REVIEW_REASON_COL not in review_cols:
        review_cols.append(REVIEW_REASON_COL)
    base = re.sub(r'[^A-Za-z0-9_-]', '_', os.path.splitext(os.path.basename(csv_file))[0])
    path = f"needs_review_{base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    import csv as _csv
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = _csv.DictWriter(f, fieldnames=review_cols, extrasaction='ignore')
        w.writeheader()
        for r in review_rows:
            w.writerow(r)
    return path


def parse_args():
    dry_run = False
    csv_file = CSV_FILE
    for arg in sys.argv[1:]:
        if arg == '--dry-run':
            dry_run = True
        elif arg.startswith('-'):
            print(f"Unknown option: {arg}")
            print("Usage: python billing_adjustment_bulk_sdk_creds.py [--dry-run] [csv_file]")
            sys.exit(1)
        else:
            csv_file = arg
    return dry_run, csv_file


def _amount(record):
    try:
        return float(record.get('amount') or 0)
    except (TypeError, ValueError):
        return 0.0


def build_row_results(records):
    """Map engine records (phase/agreement_id/invoice_id/amount/status/...) to the
    CLI results shape (kept stable for check_adjustment_status.py)."""
    out = []
    for r in records:
        out.append({
            'invoice_id': r.get('invoice_id'),
            'agreement_id': r.get('agreement_id'),
            'amount': r.get('amount'),
            'request_id': r.get('billing_adjustment_request_id') or None,
            'client_token': generate_client_token(r.get('agreement_id', ''), r.get('invoice_id', '')),
            'status': r.get('status'),
            'error': r.get('message') or None,
        })
    return out


def build_summary(records, dry_run):
    def count(*statuses):
        return sum(1 for r in records if r.get('status') in statuses)

    summary = {
        "validation_failed": count('VALIDATION_FAILED'),
        "submit_failed": count('SUBMIT_FAILED'),
        "submitted": count('COMPLETED', 'ERROR', 'TIMEOUT'),
        "completed": count('COMPLETED'),
        "completion_failed": count('ERROR', 'TIMEOUT'),
        "pending": 0,  # CLI waits for terminal states, so nothing stays pending
    }
    if dry_run:
        summary["dry_run_ok"] = count('DRY_RUN_OK')

    summary["amount_totals"] = {
        "currency": CURRENCY_CODE,
        "submitted": round(sum(_amount(r) for r in records if r.get('status') in ('COMPLETED', 'ERROR', 'TIMEOUT')), 2),
        "completed": round(sum(_amount(r) for r in records if r.get('status') == 'COMPLETED'), 2),
        "failed": round(sum(_amount(r) for r in records if r.get('status') in ('VALIDATION_FAILED', 'SUBMIT_FAILED')), 2),
    }
    return summary


def main():
    dry_run, csv_file = parse_args()

    print(f"Mode: {'DRY-RUN (validation only)' if dry_run else 'LIVE'}")
    print("Using default AWS credential chain")
    print(f"\nLoading CSV: {csv_file}")

    try:
        valid_records, review_rows, columns, amount_col = classify_input_rows(csv_file)
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"Using amount column: '{amount_col}'")
    print(f"Loaded {len(valid_records) + len(review_rows)} data row(s)")

    review_file = None
    if review_rows:
        review_file = write_needs_review_file(review_rows, columns, csv_file)
        print(f"\n\u26a0 {len(review_rows)} row(s) routed to needs-review (invalid or duplicate).")
        print(f"  Saved to: {review_file}")
        print("  These rows will NOT be submitted. Review and fix them separately.")

    if not valid_records:
        print("\nNo valid rows to process after cleaning. Exiting.")
        return

    processor = _cli_common.make_processor(log_cb=print)
    collector = _Collector()
    counters = {}

    try:
        engine_summary = processor.run(valid_records, collector, dry_run=dry_run, counters=counters)
    except CredentialsCancelled:
        print("\nStopped: fresh credentials were not provided.")
        engine_summary = {"cancelled": True}

    row_results = build_row_results(collector.records)
    summary = build_summary(collector.records, dry_run)

    output = {
        "timestamp": datetime.now().isoformat(),
        "mode": "dry_run" if dry_run else "live",
        "csv_file": csv_file,
        "total_rows": len(valid_records),
        "needs_review_rows": len(review_rows),
        "needs_review_file": review_file,
        "total_phases": engine_summary.get("total_phases"),
        "duplicate_invoices": engine_summary.get("duplicate_invoices", {}),
        "summary": summary,
        "row_results": row_results,
    }
    if dry_run:
        output["aggregate_warnings"] = engine_summary.get("aggregate_warnings", [])

    base = re.sub(r'[^A-Za-z0-9_-]', '_', os.path.splitext(os.path.basename(csv_file))[0])
    mode_tag = "dryrun" if dry_run else "prod"
    out_path = f"adjustment_results_{base}_{mode_tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for k, v in summary.items():
        if k == "amount_totals":
            continue
        print(f"  {k:<18}: {v}")
    at = summary["amount_totals"]
    print(f"  amount_totals     : submitted={at['submitted']} completed={at['completed']} "
          f"failed={at['failed']} {at['currency']}")
    if dry_run and output.get("aggregate_warnings"):
        print(f"\n  \u26a0 {len(output['aggregate_warnings'])} invoice(s) exceed aggregate max:")
        for w in output["aggregate_warnings"]:
            print(f"    - {w['invoice_id']}: requested {w['total_requested']} > max "
                  f"{w['max_adjustment_amount']} (across {w['row_count']} rows)")
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
