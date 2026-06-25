#!/usr/bin/env python3
"""
Check status of billing adjustment requests from a results log file.
Extracts all billingAdjustmentRequestIds and queries their current status via the
shared `core` engine (AdjustmentProcessor.get_adjustment_detail).

Uses the default AWS credential chain.
"""

import json
import sys
import time

import _cli_common  # noqa: F401  (adds repo root to sys.path for `core`)
from core import DELAY_BETWEEN_BATCHES


def load_results_file(filepath):
    """Load and parse the results JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_requests(results):
    """Extract all billingAdjustmentRequestIds with their agreement IDs.
    Supports both new format (row_results) and legacy format (batches)."""
    requests = []

    # New format: flat row_results array
    if 'row_results' in results:
        for row in results['row_results']:
            request_id = row.get('request_id')
            if request_id:
                requests.append({
                    'request_id': request_id,
                    'agreement_id': row.get('agreement_id')
                })
        return requests

    # Legacy format: nested batches
    for batch in results.get('batches', []):
        agreement_id = batch.get('agreement_id')
        for item in batch.get('items', []):
            request_id = item.get('billingAdjustmentRequestId')
            if request_id:
                requests.append({
                    'request_id': request_id,
                    'agreement_id': agreement_id
                })
    return requests


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_adjustment_status.py <results_file.json>")
        print("Example: python check_adjustment_status.py adjustment_results_20260406_122715.json")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"Loading results from: {filepath}")

    results = load_results_file(filepath)
    requests = extract_requests(results)

    if not requests:
        print("No billing adjustment requests found in the file.")
        sys.exit(0)

    print(f"Found {len(requests)} billing adjustment request(s)")
    print(f"Original timestamp: {results.get('timestamp', 'N/A')}")
    print()

    processor = _cli_common.make_processor()

    statuses = {'COMPLETED': 0, 'PENDING': 0, 'VALIDATION_FAILED': 0, 'ERROR': 0}

    print(f"{'Request ID':<30} {'Invoice':<15} {'Status':<20} {'Amount':<10}")
    print("-" * 80)

    for req in requests:
        try:
            detail = processor.get_adjustment_detail(req['agreement_id'], req['request_id'])
            status = detail.get('status', 'UNKNOWN')
            invoice = detail.get('originalInvoiceId', 'N/A')
            amount = detail.get('adjustmentAmount', 'N/A')
            message = detail.get('statusMessage')
        except Exception as e:
            status, invoice, amount, message = 'ERROR', 'N/A', 'N/A', str(e)

        if status in statuses:
            statuses[status] += 1
        else:
            statuses['ERROR'] += 1

        print(f"{req['request_id']:<30} {str(invoice):<15} {status:<20} {str(amount):<10}")
        if message:
            print(f"  \u2514\u2500 {message}")

        time.sleep(DELAY_BETWEEN_BATCHES)

    print()
    print("=" * 40)
    print("SUMMARY")
    print("=" * 40)
    print(f"Total requests: {len(requests)}")
    print(f"  COMPLETED:         {statuses['COMPLETED']}")
    print(f"  PENDING:           {statuses['PENDING']}")
    print(f"  VALIDATION_FAILED: {statuses['VALIDATION_FAILED']}")
    print(f"  ERROR:             {statuses['ERROR']}")


if __name__ == "__main__":
    main()
