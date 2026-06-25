#!/usr/bin/env python3
"""
Query AWS Marketplace billing adjustment requests (ListBillingAdjustmentRequests).

Lists adjustment requests across one or more agreements, with optional status,
date-range, and result-count filters. The looping/aggregation logic lives in the
shared `core` engine (AdjustmentProcessor.list_adjustment_requests).

Uses the default AWS credential chain.

Examples:
  # one or more agreement IDs as arguments
  python list_adjustment_requests.py agmt-aaa agmt-bbb

  # agreement IDs from a newline-delimited file, only COMPLETED, created in a range
  python list_adjustment_requests.py --agreements-file ids.txt \\
      --status COMPLETED --created-after 2026-06-01 --created-before 2026-06-30

  # multiple statuses
  python list_adjustment_requests.py agmt-aaa --status COMPLETED --status PENDING

Docs: https://docs.aws.amazon.com/marketplace/latest/APIReference/API_marketplace-agreements_ListBillingAdjustmentRequests.html
"""

import argparse
import csv
import re
import sys
from datetime import datetime, timezone

import _cli_common  # noqa: F401  (adds repo root to sys.path for `core`)

ITEM_FIELDS = [
    "billingAdjustmentRequestId", "agreementId", "originalInvoiceId",
    "adjustmentAmount", "currencyCode", "status", "createdAt", "updatedAt",
    "agreementType", "catalog",
]


def parse_date(value, end_of_day=False):
    """Parse 'YYYY-MM-DD' or full ISO into a timezone-aware UTC datetime."""
    if not value:
        return None
    v = value.strip()
    if "T" not in v:
        v += "T23:59:59" if end_of_day else "T00:00:00"
    dt = datetime.fromisoformat(v)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_agreement_ids(args):
    ids = list(args.agreements or [])
    if args.agreements_file:
        with open(args.agreements_file, "r", encoding="utf-8") as f:
            ids += re.split(r"[\r\n,]+", f.read())
    seen, out = set(), []
    for x in (i.strip() for i in ids):
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def fmt_epoch(v):
    if v is None or v == "":
        return ""
    if isinstance(v, datetime):
        return v.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        return datetime.fromtimestamp(float(v), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError):
        return str(v)


def main():
    ap = argparse.ArgumentParser(description="Query billing adjustment requests.")
    ap.add_argument("agreements", nargs="*", help="Agreement IDs")
    ap.add_argument("--agreements-file", help="File of newline/comma-delimited agreement IDs")
    ap.add_argument("--status", action="append", help="Status filter (repeatable). e.g. COMPLETED PENDING VALIDATION_FAILED")
    ap.add_argument("--catalog", default="AWSMarketplace")
    ap.add_argument("--created-after", help="YYYY-MM-DD or ISO (UTC)")
    ap.add_argument("--created-before", help="YYYY-MM-DD or ISO (UTC)")
    ap.add_argument("--max-results", type=int, help="Max results per agreement/status")
    ap.add_argument("--output", help="CSV output path (default: list_adjustment_requests_<timestamp>.csv)")
    args = ap.parse_args()

    agreement_ids = load_agreement_ids(args)
    if not agreement_ids:
        print("ERROR: provide at least one agreement ID (arguments or --agreements-file).")
        sys.exit(1)
    statuses = args.status or None
    created_after = parse_date(args.created_after)
    created_before = parse_date(args.created_before, end_of_day=True)

    processor = _cli_common.make_processor()

    print(f"Querying {len(agreement_ids)} agreement(s), statuses={statuses or 'ALL'} ...")
    items, errors = processor.list_adjustment_requests(
        agreement_ids=agreement_ids, statuses=statuses, catalog=args.catalog,
        created_after=created_after, created_before=created_before,
        max_results=args.max_results,
    )
    for e in errors:
        print(f"  \u2717 {e.get('agreementId')} [{e.get('status') or 'ALL'}]: {e.get('error')}")

    out_path = args.output or f"list_adjustment_requests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ITEM_FIELDS)
        w.writeheader()
        for it in items:
            w.writerow({k: it.get(k, "") for k in ITEM_FIELDS})

    print(f"\n{'BillingAdjustmentRequestId':<28} {'Invoice':<14} {'Amount':<8} {'Status':<18} {'Created':<22}")
    print("-" * 92)
    for it in items[:50]:
        print(f"{it.get('billingAdjustmentRequestId',''):<28} {str(it.get('originalInvoiceId','')):<14} "
              f"{str(it.get('adjustmentAmount','')):<8} {str(it.get('status','')):<18} {fmt_epoch(it.get('createdAt')):<22}")
    if len(items) > 50:
        print(f"... and {len(items) - 50} more (see {out_path})")

    print(f"\nTotal requests: {len(items)} | Query errors: {len(errors)}")
    print(f"Results saved to: {out_path}")


if __name__ == "__main__":
    main()
