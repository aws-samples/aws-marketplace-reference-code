#!/usr/bin/env python3
"""
Get the status/detail of an individual billing adjustment request
(GetBillingAdjustmentRequest), by agreement ID and billing adjustment request ID.

Uses the default AWS credential chain (via the shared `core` engine).

Examples:
  # single request
  python get_adjustment_request.py agmt-aaa ba-1111

  # many requests from a file (one "agreementId,billingAdjustmentRequestId" per line)
  python get_adjustment_request.py --file pairs.csv

Docs: https://docs.aws.amazon.com/marketplace/latest/APIReference/API_marketplace-agreements_GetBillingAdjustmentRequest.html
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone

import _cli_common  # noqa: F401  (adds repo root to sys.path for `core`)
from core import DELAY_BETWEEN_BATCHES


def fmt_epoch(v):
    if v is None or v == "":
        return ""
    if isinstance(v, datetime):
        return v.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        return datetime.fromtimestamp(float(v), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError):
        return str(v)


def load_pairs(args):
    """Return list of (agreement_id, request_id)."""
    pairs = []
    if args.agreement_id and args.request_id:
        pairs.append((args.agreement_id.strip(), args.request_id.strip()))
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                row = [c.strip() for c in row if c.strip()]
                if len(row) >= 2 and not row[0].lower().startswith("agreement"):
                    pairs.append((row[0], row[1]))
    return pairs


def main():
    ap = argparse.ArgumentParser(description="Get billing adjustment request detail.")
    ap.add_argument("agreement_id", nargs="?", help="Agreement ID")
    ap.add_argument("request_id", nargs="?", help="Billing adjustment request ID")
    ap.add_argument("--file", help="CSV/text file of 'agreementId,billingAdjustmentRequestId' rows")
    ap.add_argument("--output", help="Optional JSON output path")
    args = ap.parse_args()

    pairs = load_pairs(args)
    if not pairs:
        print("ERROR: provide agreement_id and request_id, or --file with pairs.")
        sys.exit(1)

    processor = _cli_common.make_processor()

    results = []
    for aid, rid in pairs:
        try:
            detail = processor.get_adjustment_detail(aid, rid)
            detail["_error"] = None
        except Exception as e:
            detail = {"agreementId": aid, "billingAdjustmentRequestId": rid, "_error": str(e)}
        results.append(detail)

        print("=" * 70)
        if detail.get("_error"):
            print(f"{rid} ({aid}) -> ERROR: {detail['_error']}")
        else:
            print(f"Request:  {detail.get('billingAdjustmentRequestId')}")
            print(f"Agreement:{detail.get('agreementId')}")
            print(f"Invoice:  {detail.get('originalInvoiceId')}")
            print(f"Amount:   {detail.get('adjustmentAmount')} {detail.get('currencyCode')}")
            print(f"Reason:   {detail.get('adjustmentReasonCode')}")
            print(f"Status:   {detail.get('status')}  {detail.get('statusMessage') or ''}")
            print(f"Created:  {fmt_epoch(detail.get('createdAt'))}")
            print(f"Updated:  {fmt_epoch(detail.get('updatedAt'))}")
        time.sleep(DELAY_BETWEEN_BATCHES)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nSaved {len(results)} result(s) to {args.output}")

    errs = sum(1 for r in results if r.get("_error"))
    print(f"\nChecked {len(results)} request(s) | errors: {errs}")


if __name__ == "__main__":
    main()
