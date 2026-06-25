#!/usr/bin/env python3
"""
Shared glue for the CLI scripts over the common `core` engine.

- Adds the repo root to sys.path so `from core import ...` works when a script is
  run from inside `cli/`.
- Provides a single factory for an AdjustmentProcessor wired to the default AWS
  credential chain, with an interactive "press ENTER to retry" refresh on expiry.

All billing-adjustment logic lives in `core/`; these scripts only handle argument
parsing and output formatting.
"""

import os
import sys

# Make the top-level `core` package importable from within cli/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import AdjustmentProcessor  # noqa: E402


def prompt_credential_refresh():
    """Interactive refresh hook: pause, let the user refresh creds out-of-band, retry.

    Returns a truthy sentinel so the engine rebuilds its client from the default
    credential chain (which will pick up the freshly refreshed credentials). Returns
    None if input is unavailable, which the engine treats as a cancellation.
    """
    print("\n" + "=" * 60)
    print("AWS CREDENTIALS EXPIRED OR INVALID")
    print("=" * 60)
    print("Refresh your AWS credentials using your preferred method, e.g.:")
    print("  aws sso login --profile <profile>")
    print("  ada credentials update --profile <profile> ...")
    print("  (or export fresh AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN)")
    print("\nPress ENTER once refreshed to retry...")
    try:
        input()
    except EOFError:
        return None
    return {"refresh": True}


def make_processor(interactive=True, log_cb=None):
    """Build an AdjustmentProcessor that uses the default AWS credential chain.

    interactive=True wires the ENTER-to-retry refresh; pass False for non-interactive
    runs (the engine will then surface credential errors directly).
    """
    return AdjustmentProcessor(
        managed_credentials=False,
        request_credentials=prompt_credential_refresh if interactive else None,
        log_cb=log_cb,
    )
