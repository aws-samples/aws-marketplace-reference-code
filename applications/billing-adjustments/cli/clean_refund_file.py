#!/usr/bin/env python3
"""
Pre-flight cleaner for a refund input file.

Splits a refund CSV (same format as the submit file) into:
  - cleaned_<input>_<timestamp>.csv      : rows that are safe to submit (original
                                            columns preserved), de-duplicated so each
                                            <agreement_id, invoice_id> appears once.
  - needs_review_<input>_<timestamp>.csv : rows that should NOT be submitted, in the
                                            original format plus a 'review_reason'
                                            column. Includes invalid rows AND
                                            duplicate <agreement, invoice> combos.

A row is routed to needs-review when:
  - agreement_id is blank or a placeholder (e.g. #N/A, N/A, NULL)
  - invoice_id is blank or a placeholder
  - the amount is missing, non-numeric, or <= 0
  - the <agreement_id, invoice_id> combination already appeared earlier (only the
    first occurrence is kept in the cleaned file)

This does NOT call AWS. The classification logic lives in `core` (classify_input_rows),
shared with the web app and the bulk submit script.

Examples:
  python clean_refund_file.py "MongoDb/AWS Latest MP Refund List 2026-05-01 - AWS.csv"
  python clean_refund_file.py refunds.csv --output-dir ./out
"""

import argparse
import csv
import os
import re
import sys
from collections import Counter
from datetime import datetime

import _cli_common  # noqa: F401  (adds repo root to sys.path for `core`)
from core import classify_input_rows, REVIEW_REASON_COL


def main():
    ap = argparse.ArgumentParser(description="Split a refund file into cleaned + needs-review files.")
    ap.add_argument("input", help="Refund CSV file (same format as the submit file)")
    ap.add_argument("--output-dir", default=".", help="Directory for the output files (default: current dir)")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: input file not found: {args.input}")
        sys.exit(1)

    try:
        valid_records, review_rows, columns, amount_col = classify_input_rows(args.input)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"Amount column: '{amount_col}'")

    base = re.sub(r"[^A-Za-z0-9_-]", "_", os.path.splitext(os.path.basename(args.input))[0])
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(args.output_dir, exist_ok=True)
    cleaned_path = os.path.join(args.output_dir, f"cleaned_{base}_{ts}.csv")
    review_path = os.path.join(args.output_dir, f"needs_review_{base}_{ts}.csv")

    with open(cleaned_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for rec in valid_records:
            w.writerow(rec["original"])

    review_cols = columns + ([REVIEW_REASON_COL] if REVIEW_REASON_COL not in columns else [])
    with open(review_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=review_cols, extrasaction="ignore")
        w.writeheader()
        for row in review_rows:
            w.writerow(row)

    reason_counts = Counter(r[REVIEW_REASON_COL] for r in review_rows)

    print(f"\nValid rows  : {len(valid_records)}  -> {cleaned_path}")
    print(f"Needs review: {len(review_rows)}  -> {review_path}")
    if reason_counts:
        print("\nReview breakdown:")
        for reason, n in reason_counts.most_common():
            print(f"  {n:>5}  {reason}")


if __name__ == "__main__":
    main()
