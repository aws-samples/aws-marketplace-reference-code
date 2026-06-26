"""
Shared backend for AWS Marketplace billing adjustments.

This package is the single source of truth for the billing-adjustment logic used by
BOTH the web app (`webapp/`) and the command-line scripts (`cli/`). Anything that
talks to the Marketplace Agreement API — input parsing/validation, client/credential
handling, batching, the deterministic client token, submission, polling, and the
list/get/reconcile queries — lives here so a change is made in exactly one place.

Entry points add the repo root to sys.path and then `from core import ...`.
"""

from core.engine import (
    # Constants
    BATCH_SIZE,
    CALLS_PER_SECOND,
    DELAY_BETWEEN_BATCHES,
    POLL_INTERVAL,
    MAX_POLL_TIME,
    CURRENCY_CODE,
    ADJUSTMENT_REASON,
    ENDPOINT_URL,
    REGION,
    REQUIRED_COLUMNS,
    AMOUNT_COLUMN_OPTIONS,
    COL_AGREEMENT_ID,
    COL_INVOICE_ID,
    REVIEW_REASON_COL,
    NA_PLACEHOLDERS,
    # Exceptions
    CredentialsCancelled,
    # Helpers
    is_credential_error,
    generate_client_token,
    format_amount,
    build_header_map,
    resolve_amount_column,
    get_field,
    validate_file_format,
    load_csv,
    classify_input_rows,
    find_duplicate_invoices,
    group_rows_by_invoice_occurrence,
    group_by_agreement,
    create_batches,
    # Classes
    RecordWriter,
    AdjustmentProcessor,
)

__all__ = [
    "BATCH_SIZE",
    "CALLS_PER_SECOND",
    "DELAY_BETWEEN_BATCHES",
    "POLL_INTERVAL",
    "MAX_POLL_TIME",
    "CURRENCY_CODE",
    "ADJUSTMENT_REASON",
    "ENDPOINT_URL",
    "REGION",
    "REQUIRED_COLUMNS",
    "AMOUNT_COLUMN_OPTIONS",
    "COL_AGREEMENT_ID",
    "COL_INVOICE_ID",
    "REVIEW_REASON_COL",
    "NA_PLACEHOLDERS",
    "CredentialsCancelled",
    "is_credential_error",
    "generate_client_token",
    "format_amount",
    "build_header_map",
    "resolve_amount_column",
    "get_field",
    "validate_file_format",
    "load_csv",
    "classify_input_rows",
    "find_duplicate_invoices",
    "group_rows_by_invoice_occurrence",
    "group_by_agreement",
    "create_batches",
    "RecordWriter",
    "AdjustmentProcessor",
]
