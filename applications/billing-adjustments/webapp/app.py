#!/usr/bin/env python3
"""
Web UI for AWS Marketplace Billing Adjustments.

Designed for non-technical (accounting) users:
- Upload a CSV in the required format, with an in-page format guide and a
  "Check file format" button.
- Optional dry-run (validation only) with downloadable, human-readable output.
- Jobs run in the background and keep running if the user leaves the page.

Two credential modes:
- Default (local use): the user pastes AWS access key / secret key / session token
  in the UI; used only for that job and never written to disk.
- Managed (MANAGED_CREDENTIALS=true, e.g. when deployed into an AWS account):
  credentials come from the attached IAM role via the default provider chain. The
  UI hides the credential fields and the user never sees or enters keys.

Optional access control:
- If APP_ACCESS_PASSWORD is set, the app requires a shared password to use it. This
  is REQUIRED when deployed with managed credentials, because the app can act on the
  account's behalf using the IAM role.

SECURITY NOTE: In local mode the app accepts AWS credentials over HTTP form posts.
Run it only on a trusted host/network and serve over HTTPS in any shared environment.
"""

import os
import re
import csv
import uuid
import secrets
import functools
from datetime import datetime, timezone

from flask import (
    Flask, request, jsonify, render_template,
    send_from_directory, abort, session, redirect, url_for,
)
from werkzeug.utils import secure_filename

# Make the repo-root `core` package importable when run from inside webapp/
# (locally `cd webapp; python app.py`, or in the container at /app/webapp).
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    validate_file_format, AdjustmentProcessor, CredentialsCancelled,
    COL_AGREEMENT_ID, COL_INVOICE_ID, classify_input_rows, REVIEW_REASON_COL,
)
from job_manager import JobManager, read_status, list_jobs, _job_dir


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

# Credentials come from the attached IAM role (default provider chain) instead of
# the UI form when deployed into an AWS account.
MANAGED_CREDENTIALS = os.environ.get("MANAGED_CREDENTIALS", "false").lower() == "true"
# Optional shared-password gate. Required (enforced below) in managed mode.
APP_ACCESS_PASSWORD = os.environ.get("APP_ACCESS_PASSWORD")
# Optional cross-account role assumption: the app assumes this role (in the account
# that owns the agreements) and uses its temporary credentials. Used together with
# MANAGED_CREDENTIALS when the app is deployed in a different account from the data.
ASSUME_ROLE_ARN = os.environ.get("AWS_ASSUME_ROLE_ARN") or None
ASSUME_ROLE_EXTERNAL_ID = os.environ.get("AWS_ASSUME_ROLE_EXTERNAL_ID") or None

if MANAGED_CREDENTIALS and not APP_ACCESS_PASSWORD:
    raise RuntimeError(
        "MANAGED_CREDENTIALS is enabled but APP_ACCESS_PASSWORD is not set. "
        "Refusing to start: the app would be able to act on the account's IAM role "
        "without any access control. Set APP_ACCESS_PASSWORD."
    )

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

job_manager = JobManager()


def login_required(view):
    """Protect a view when APP_ACCESS_PASSWORD is configured."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if APP_ACCESS_PASSWORD and not session.get("authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if not APP_ACCESS_PASSWORD:
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        supplied = request.form.get("password", "")
        if secrets.compare_digest(supplied, APP_ACCESS_PASSWORD):
            session["authenticated"] = True
            return redirect(url_for("index"))
        error = "Incorrect password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def _save_upload(file_storage):
    """Save uploaded file to disk with a unique name. Returns (path, original_name)."""
    original = secure_filename(file_storage.filename or "upload.csv")
    if not original.lower().endswith(".csv"):
        original += ".csv"
    unique = f"{uuid.uuid4().hex[:8]}_{original}"
    path = os.path.join(UPLOAD_DIR, unique)
    file_storage.save(path)
    return path, original


@app.route("/healthz")
def healthz():
    """Unauthenticated health check for load balancers / App Runner."""
    return jsonify({"status": "ok"})


@app.route("/")
@login_required
def index():
    return render_template("index.html", managed_credentials=MANAGED_CREDENTIALS)


@app.route("/api/config")
@login_required
def api_config():
    return jsonify({"managed_credentials": MANAGED_CREDENTIALS})


@app.route("/api/validate", methods=["POST"])
@login_required
def api_validate():
    """Check an uploaded file's format without submitting anything."""
    if "file" not in request.files:
        return jsonify({"valid": False, "message": "No file uploaded."}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"valid": False, "message": "No file selected."}), 400

    path, original = _save_upload(f)
    try:
        valid, message, details = validate_file_format(path)
        return jsonify({
            "valid": valid,
            "message": message,
            "details": details,
            "original_filename": original,
        })
    finally:
        # Validation uploads are temporary
        try:
            os.remove(path)
        except OSError:
            pass


@app.route("/api/submit", methods=["POST"])
@login_required
def api_submit():
    """Start a background job (dry-run or live)."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "No file selected."}), 400

    dry_run = request.form.get("dry_run", "false").lower() == "true"
    precheck_processed = request.form.get("precheck", "true").lower() == "true"

    credentials = None
    if not MANAGED_CREDENTIALS:
        access_key = (request.form.get("access_key") or "").strip()
        secret_key = (request.form.get("secret_key") or "").strip()
        session_token = (request.form.get("session_token") or "").strip() or None
        if not access_key or not secret_key:
            return jsonify({"error": "Access key and secret key are required."}), 400
        credentials = {
            "access_key": access_key,
            "secret_key": secret_key,
            "session_token": session_token,
        }

    path, original = _save_upload(f)

    # Split the file into rows we can process vs. rows that need review (invalid
    # agreement/invoice/amount, or duplicate <agreement, invoice> combinations).
    # The bad rows are routed to a downloadable "needs review" file instead of
    # blocking the whole upload.
    try:
        valid_records, review_rows, columns, _amount_col = classify_input_rows(path)
    except ValueError as e:
        try:
            os.remove(path)
        except OSError:
            pass
        return jsonify({"error": f"File format invalid: {e}"}), 400

    if not valid_records:
        try:
            os.remove(path)
        except OSError:
            pass
        return jsonify({
            "error": "No valid rows to process. All rows were routed to review.",
            "review_count": len(review_rows),
        }), 400

    # Write a cleaned CSV containing only the valid rows (original columns intact);
    # the job runs against this file.
    clean_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex[:8]}_clean_{original}")
    with open(clean_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for rec in valid_records:
            writer.writerow(rec["original"])

    # Original upload no longer needed (valid rows are in clean_path; review rows
    # are passed to the job manager).
    try:
        os.remove(path)
    except OSError:
        pass

    job_id = job_manager.create_job(
        csv_path=clean_path,
        original_filename=original,
        credentials=credentials,
        dry_run=dry_run,
        managed_credentials=MANAGED_CREDENTIALS,
        assume_role_arn=ASSUME_ROLE_ARN,
        assume_role_external_id=ASSUME_ROLE_EXTERNAL_ID,
        review_rows=review_rows,
        review_columns=columns,
        precheck_processed=precheck_processed,
    )
    return jsonify({
        "job_id": job_id,
        "dry_run": dry_run,
        "valid_count": len(valid_records),
        "review_count": len(review_rows),
    })


# ---------------------------------------------------------------------------
# Read-only query endpoints (List / Get billing adjustment requests)
# ---------------------------------------------------------------------------

def _build_processor():
    """Build an AdjustmentProcessor for a synchronous query from the current request.
    Managed mode uses the IAM role (and optional assume-role); local mode reads the
    AWS credentials from the form. Returns (processor, error_response_or_None)."""
    if MANAGED_CREDENTIALS:
        creds = {}
    else:
        access_key = (request.form.get("access_key") or "").strip()
        secret_key = (request.form.get("secret_key") or "").strip()
        session_token = (request.form.get("session_token") or "").strip() or None
        if not access_key or not secret_key:
            return None, (jsonify({"error": "Access key and secret key are required."}), 400)
        creds = {"access_key": access_key, "secret_key": secret_key, "session_token": session_token}
    try:
        processor = AdjustmentProcessor(
            access_key=creds.get("access_key"),
            secret_key=creds.get("secret_key"),
            session_token=creds.get("session_token"),
            managed_credentials=MANAGED_CREDENTIALS,
            assume_role_arn=ASSUME_ROLE_ARN,
            assume_role_external_id=ASSUME_ROLE_EXTERNAL_ID,
        )
        return processor, None
    except Exception as e:
        return None, (jsonify({"error": f"Could not initialize AWS client: {e}"}), 400)


def _parse_epoch_datetime(value, end_of_day=False):
    """Parse a UI date/datetime string into a timezone-aware UTC datetime.
    Accepts 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM'. Returns None if empty."""
    value = (value or "").strip()
    if not value:
        return None
    try:
        if "T" in value:
            dt = datetime.fromisoformat(value)
        else:
            dt = datetime.fromisoformat(value + ("T23:59:59" if end_of_day else "T00:00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _agreement_ids_from_request():
    """Collect agreement IDs from an uploaded file and/or a pasted text field."""
    ids = []
    f = request.files.get("agreements_file")
    if f and f.filename:
        try:
            content = f.read().decode("utf-8", errors="ignore")
            ids += re.split(r"[\r\n,]+", content)
        except Exception:
            pass
    text = request.form.get("agreement_ids") or ""
    ids += re.split(r"[\r\n,]+", text)
    # normalize: trim, drop blanks, de-dupe preserving order
    seen, out = set(), []
    for x in (i.strip() for i in ids):
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


@app.route("/api/list-adjustments", methods=["POST"])
@login_required
def api_list_adjustments():
    """ListBillingAdjustmentRequests across one or more agreement IDs and statuses."""
    agreement_ids = _agreement_ids_from_request()
    if not agreement_ids:
        return jsonify({"error": "Provide at least one agreement ID (paste or upload a file)."}), 400

    statuses = [s.strip() for s in request.form.getlist("status") if s.strip()] or None
    catalog = (request.form.get("catalog") or "AWSMarketplace").strip()
    created_after = _parse_epoch_datetime(request.form.get("created_after"))
    created_before = _parse_epoch_datetime(request.form.get("created_before"), end_of_day=True)
    max_results = request.form.get("max_results")
    try:
        max_results = int(max_results) if max_results else None
    except ValueError:
        max_results = None

    processor, err = _build_processor()
    if err:
        return err
    try:
        items, errors = processor.list_adjustment_requests(
            agreement_ids=agreement_ids, statuses=statuses, catalog=catalog,
            created_after=created_after, created_before=created_before,
            max_results=max_results,
        )
    except CredentialsCancelled:
        return jsonify({"error": "Credentials unavailable."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"count": len(items), "items": items, "query_errors": errors,
                    "agreement_ids_queried": len(agreement_ids)})


@app.route("/api/get-adjustment", methods=["POST"])
@login_required
def api_get_adjustment():
    """GetBillingAdjustmentRequest for a single agreementId + billingAdjustmentRequestId."""
    agreement_id = (request.form.get("agreement_id") or "").strip()
    request_id = (request.form.get("billing_adjustment_request_id") or "").strip()
    if not agreement_id or not request_id:
        return jsonify({"error": "Both agreement ID and billing adjustment request ID are required."}), 400

    processor, err = _build_processor()
    if err:
        return err
    try:
        detail = processor.get_adjustment_detail(agreement_id, request_id)
    except CredentialsCancelled:
        return jsonify({"error": "Credentials unavailable."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"detail": detail})


@app.route("/api/reconcile", methods=["POST"])
@login_required
def api_reconcile():
    """Reconcile a refund input file against the service.

    Takes the same CSV format as the bulk refund file. For each agreement id we
    list its billing adjustment requests and check whether each input invoice id
    was found; confirmed ones are returned in `processed` (full
    GetBillingAdjustmentRequest detail), the rest in `not_processed` (original
    rows). The client renders these as two downloadable CSV files."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "No file selected."}), 400

    path, original = _save_upload(f)
    try:
        # Read the input file preserving every original column.
        try:
            with open(path, "r", encoding="utf-8-sig") as fh:
                reader = csv.DictReader(fh)
                original_columns = list(reader.fieldnames or [])
                records = []
                for row in reader:
                    # skip fully blank lines
                    if not any((v or "").strip() for v in row.values()):
                        continue
                    records.append({
                        "agreement_id": (row.get(COL_AGREEMENT_ID) or "").strip(),
                        "invoice_id": (row.get(COL_INVOICE_ID) or "").strip(),
                        "original": dict(row),
                    })
        except Exception as e:
            return jsonify({"error": f"Could not read file: {e}"}), 400

        if not original_columns:
            return jsonify({"error": "File is empty or has no header row."}), 400
        if COL_AGREEMENT_ID not in original_columns or COL_INVOICE_ID not in original_columns:
            return jsonify({"error": (
                f"File must contain '{COL_AGREEMENT_ID}' and '{COL_INVOICE_ID}' columns."
            )}), 400
        if not records:
            return jsonify({"error": "File has headers but no data rows."}), 400

        processor, err = _build_processor()
        if err:
            return err
        try:
            processed, not_processed, errors = processor.reconcile_refunds(records)
        except CredentialsCancelled:
            return jsonify({"error": "Credentials unavailable."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

        return jsonify({
            "original_filename": original,
            "original_columns": original_columns,
            "processed": processed,
            "not_processed": not_processed,
            "errors": errors,
            "counts": {
                "input_rows": len(records),
                "processed": len(processed),
                "not_processed": len(not_processed),
                "errors": len(errors),
            },
        })
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


@app.route("/api/jobs")
@login_required
def api_jobs():
    return jsonify({"jobs": list_jobs()})


@app.route("/api/jobs/<job_id>")
@login_required
def api_job_status(job_id):
    status = read_status(job_id)
    if not status:
        return jsonify({"error": "Job not found."}), 404
    return jsonify(status)


@app.route("/api/jobs/<job_id>/cancel", methods=["POST"])
@login_required
def api_job_cancel(job_id):
    ok = job_manager.cancel_job(job_id)
    return jsonify({"cancelled": ok})


@app.route("/api/jobs/<job_id>/credentials", methods=["POST"])
@login_required
def api_job_credentials(job_id):
    """Supply fresh credentials to a job paused because its credentials expired.
    Not applicable in managed mode (the IAM role refreshes automatically)."""
    if MANAGED_CREDENTIALS:
        return jsonify({"error": "Managed credentials mode does not require this."}), 400
    status = read_status(job_id)
    if not status:
        return jsonify({"error": "Job not found."}), 404
    if status.get("state") != "awaiting_credentials":
        return jsonify({"error": "Job is not waiting for credentials."}), 400

    data = request.form if request.form else (request.get_json(silent=True) or {})
    access_key = (data.get("access_key") or "").strip()
    secret_key = (data.get("secret_key") or "").strip()
    session_token = (data.get("session_token") or "").strip() or None
    if not access_key or not secret_key:
        return jsonify({"error": "Access key and secret key are required."}), 400

    ok = job_manager.provide_credentials(job_id, {
        "access_key": access_key,
        "secret_key": secret_key,
        "session_token": session_token,
    })
    if not ok:
        return jsonify({"error": "Job is no longer active."}), 400
    return jsonify({"resumed": True})


@app.route("/api/jobs/<job_id>/download/<kind>")
@login_required
def api_download(job_id, kind):
    """Download outputs: kind in {csv, json, jsonl, review}."""
    status = read_status(job_id)
    if not status:
        abort(404)
    filenames = {
        "csv": "records.csv",
        "json": "summary.json",
        "jsonl": "records.jsonl",
        "review": "needs_review.csv",
    }
    fname = filenames.get(kind)
    if not fname:
        abort(404)
    jdir = _job_dir(job_id)
    if not os.path.exists(os.path.join(jdir, fname)):
        abort(404)
    ext = "csv" if kind in ("csv", "review") else ("json" if kind == "json" else "jsonl")
    suffix = "needs_review" if kind == "review" else kind
    download_name = f"{os.path.splitext(status['original_filename'])[0]}_{suffix}.{ext}"
    return send_from_directory(jdir, fname, as_attachment=True, download_name=download_name)


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large (max 10 MB)."}), 413


if __name__ == "__main__":
    # threaded=True allows background job threads + request handling concurrently.
    # Use a single worker process so in-memory job registry stays consistent.
    import threading
    import webbrowser

    port = int(os.environ.get("PORT", "5050"))
    url = f"http://127.0.0.1:{port}"

    # Auto-open the browser shortly after the server starts (unless disabled).
    if os.environ.get("NO_BROWSER", "false").lower() != "true":
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    print(f"\n  Billing Adjustments UI running at: {url}")
    print("  Leave this window open while you work. Close it to stop the app.\n")

    app.run(host="127.0.0.1", port=port, threaded=True, debug=False)
