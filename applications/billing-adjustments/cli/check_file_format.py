#!/usr/bin/env python3
"""
Check that a refund input file has the right format BEFORE running a refund.

This is the CLI equivalent of the web UI's "Check file format" button. It runs the
shared engine's `validate_file_format()` (in `core/engine.py`) and prints a clean
pass/fail report: which required columns were found/missing, which amount column was
detected, the data-row count, and any row-level issues (missing agreement_id /
invoice_id, non-positive amount, or more than 2 decimal places).

It does NOT call AWS and does NOT modify or submit anything. To also split a file
into a cleaned + needs-review pair, use `clean_refund_file.py`.

Exit code is 0 when the file is valid, 1 when it is not (handy for scripting).

Examples:
  python check_file_format.py adjustmentFiles/sample_company.csv
  python check_file_format.py "MongoDb/Harvey Bedrock Refund.csv"
  python check_file_format.py refunds.csv --json
"""

import argparse
import json
import os
import sys

import _cli_common  # noqa: F401  (adds repo root to sys.path for `core`)
from core import validate_file_format


def main():
    ap = argparse.ArgumentParser(
        description="Validate a refund input file's format (no AWS calls, nothing submitted)."
    )
    ap.add_argument("input", help="Refund CSV file (same format as the submit file)")
    ap.add_argument("--json", action="store_true",
                    help="Print the raw details dict as JSON instead of a text report")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: input file not found: {args.input}")
        sys.exit(1)

    is_valid, message, details = validate_file_format(args.input)

    if args.json:
        print(json.dumps({"valid": is_valid, "message": message, "details": details},
                         indent=2, default=str))
        sys.exit(0 if is_valid else 1)

    print(f"File: {args.input}")
    print(f"Result: {'VALID' if is_valid else 'INVALID'} - {message}")
    print()

    found = details.get("found_columns") or []
    print(f"Found columns ({len(found)}): {', '.join(found) if found else '(none)'}")

    missing = details.get("missing_columns") or []
    if missing:
        print(f"Missing required column(s): {', '.join(missing)}")

    amount_col = details.get("amount_column_found")
    if amount_col:
        print(f"Amount column detected: '{amount_col}'")
    else:
        print(f"Amount column detected: (none) - expected one of: "
              f"{', '.join(details.get('amount_column_options') or [])}")

    print(f"Data rows: {details.get('row_count', 0)}")

    row_issues = details.get("row_issues") or []
    if row_issues:
        print(f"\nRow issues ({len(row_issues)}):")
        for issue in row_issues:
            print(f"  line {issue.get('line')}: {'; '.join(issue.get('issues', []))}")

    print()
    if is_valid:
        print("OK - this file is ready to submit (run a --dry-run for live invoice checks).")
    else:
        print("Fix the issues above, or run clean_refund_file.py to split out the bad rows.")

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
