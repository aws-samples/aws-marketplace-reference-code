"""Utility functions for AWS Marketplace Agreement Service API samples."""

import json
import time
import uuid

def format_output(result):
    """Pretty-print an API response as JSON."""
    print(json.dumps(result, indent=2, default=str))


def generate_client_token():
    """Generate a unique client token for idempotent requests."""
    return str(uuid.uuid4())


def poll_until_entitlements_available(client, agreement_id):
    """Poll GetAgreementEntitlements until none are PENDING (up to 15 min)."""
    timeout = 15 * 60
    backoff = 2
    max_backoff = 60
    deadline = time.monotonic() + timeout

    while True:
        response = client.get_agreement_entitlements(agreementId=agreement_id)
        all_active = all(
            e.get("status") != "PENDING"
            for e in response.get("agreementEntitlements", [])
        )
        if all_active:
            return response
        if time.monotonic() + backoff > deadline:
            raise RuntimeError(
                f"Entitlements still pending after 15 minutes for agreementId: {agreement_id}"
            )
        print(f"Entitlements not yet active. Retrying in {backoff} seconds...")
        time.sleep(backoff)
        backoff = min(backoff * 2, max_backoff)
