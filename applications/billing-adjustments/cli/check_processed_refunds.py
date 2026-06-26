#!/usr/bin/env python3
"""
Reconcile a refund input file against AWS Marketplace billing adjustment requests.

Takes the SAME CSV file you used to submit bulk refunds. For each agreement id it
lists the agreement's adjustment requests, checks whether each input invoice id was
processed, and confirms matches with GetBillingAdjustmentRequest. The reconciliation
logic lives in the shared `core` engine (AdjustmentProcessor.reconcile_refunds).

Produces two output files:
  - processed_<input>_<timestamp>.csv      : confirmed refunds (GetBillingAdjustmentRequest detail)
  - not_processed_<input>_<timestamp>.csv  : rows whose invoice was NOT found, in the
                                              ORIGINAL input file format (columns intact)

Uses the default AWS credential chain.

Examples:
  python check_processed_refunds.py adjustmentFiles/sample_company.csv
  python check_processed_refunds.py refunds.csv --output-dir ./out
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timezone

import _cli_common  # noqa: F401  (adds repo root to sys.path for `core`)
from core import COL_AGREEMENT_ID, COL_INVOICE_ID, build_header_map, get_field

# Fields written to the processed output (GetBillingAdjustmentRequest detail).
PROCESSED_FIELDS = [
    "billingAdjustmentRequestId", "agreementId", "originalInvoiceId",
    "matchedInvoiceId", "adjustmentAmount", "currencyCode", "status",
    "statusMessage", "adjustmentReasonCode", "description", "createdAt", "updatedAt",
]


def fmt_value(v):
    """Render datetimes as UTC strings; leave everything else as-is."""
    if isinstance(v, datetime):
        return v.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if v is None:
        return ""
    return v


def load_input(filepath):
    """Read the input CSV preserving original columns. Returns (records, columns)."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        header_map = build_header_map(columns)
        records = []
        for row in reader:
            if not any((v or "").strip() for v in row.values()):
                continue  # skip blank lines
            records.append({
                "agreement_id": (get_field(row, header_map, COL_AGREEMENT_ID) or "").strip(),
                "invoice_id": (get_field(row, header_map, COL_INVOICE_ID) or "").strip(),
                "original": dict(row),
            })
    return records, columns


def main():
    ap = argparse.ArgumentParser(description="Reconcile a refund file against processed adjustments.")
    ap.add_argument("input", help="Refund CSV file (same format as the submit file)")
    ap.add_argument("--output-dir", default=".", help="Directory for the two output files (default: current dir)")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: input file not found: {args.input}")
        sys.exit(1)

    records, columns = load_input(args.input)
    if not columns:
        print("ERROR: input file is empty or has no header row.")
        sys.exit(1)
    header_map = build_header_map(columns)
    if (COL_AGREEMENT_ID.lower() not in header_map
            or COL_INVOICE_ID.lower() not in header_map):
        print(f"ERROR: input must contain '{COL_AGREEMENT_ID}' and '{COL_INVOICE_ID}' columns. Found: {columns}")
        sys.exit(1)
    if not records:
        print("ERROR: input file has headers but no data rows.")
        sys.exit(1)

    processor = _cli_common.make_processor(log_cb=lambda m: print(f"  {m}"))

    print(f"Reconciling {len(records)} row(s)...")
    processed, not_processed, errors = processor.reconcile_refunds(records)

    # Write outputs
    base = os.path.splitext(os.path.basename(args.input))[0]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(args.output_dir, exist_ok=True)
    processed_path = os.path.join(args.output_dir, f"processed_{base}_{ts}.csv")
    not_processed_path = os.path.join(args.output_dir, f"not_processed_{base}_{ts}.csv")

    with open(processed_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PROCESSED_FIELDS, extrasaction="ignore")
        w.writeheader()
        for d in processed:
            w.writerow({k: fmt_value(d.get(k, "")) for k in PROCESSED_FIELDS})

    with open(not_processed_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        for row in not_processed:
            w.writerow(row)

    print(f"\nInput rows : {len(records)}")
    print(f"Processed  : {len(processed)}  -> {processed_path}")
    print(f"Not proc.  : {len(not_processed)}  -> {not_processed_path}")
    if errors:
        print(f"Errors     : {len(errors)}")
        for e in errors[:10]:
            loc = e.get("agreementId", "")
            if e.get("invoiceId"):
                loc += f" / {e['invoiceId']}"
            print(f"  \u2717 {loc}: {e['error']}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")


if __name__ == "__main__":
    main()
