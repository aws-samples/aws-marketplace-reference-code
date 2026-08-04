#!/usr/bin/env python3
"""
Background job manager for billing adjustment processing.

- Each job runs in a daemon thread, so it continues after the user leaves the UI.
- Job status is persisted to disk (jobs/<job_id>/status.json) so the UI can poll
  it and so status survives page reloads.
- Outputs (JSON summary, JSONL records, readable CSV) are written into the job dir.
"""

import os
import json
import time
import uuid
import threading
import traceback
from datetime import datetime

# Make the repo-root `core` package importable when run from inside webapp/.
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    AdjustmentProcessor, RecordWriter, load_csv, CredentialsCancelled,
    REVIEW_REASON_COL, COL_AGREEMENT_ID, COL_INVOICE_ID,
    build_header_map, get_field, resolve_amount_column,
)


JOBS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs")
os.makedirs(JOBS_DIR, exist_ok=True)


def _env_positive_int(name, default):
    """Read a positive integer from the environment, falling back to `default`
    for missing/blank/invalid/non-positive values."""
    try:
        val = int(str(os.environ.get(name, "")).strip())
        return val if val > 0 else default
    except (ValueError, TypeError):
        return default


# Bound how long a paused job waits for fresh credentials before it stops on its
# own, so a run can never hang in "awaiting_credentials" forever (as observed when
# a seller closed the tab mid-run). 30 min leaves ample room for a legitimate
# refresh (the longest successful pause on record was ~19 min) while guaranteeing
# the job eventually finishes and records what it completed. Both values are
# overridable via environment for operators who want a different window.
CREDENTIAL_WAIT_TIMEOUT = _env_positive_int("CREDENTIAL_WAIT_TIMEOUT_SECONDS", 1800)
# How often to log a "still waiting" heartbeat so a long pause doesn't look frozen.
CREDENTIAL_WAIT_NOTICE_INTERVAL = _env_positive_int("CREDENTIAL_WAIT_NOTICE_SECONDS", 120)

# In-memory registry of running jobs (thread + cancel flag). Status lives on disk.
_jobs = {}
_lock = threading.Lock()


def _job_dir(job_id):
    return os.path.join(JOBS_DIR, job_id)


def _status_path(job_id):
    return os.path.join(_job_dir(job_id), "status.json")


def _write_status(job_id, status):
    path = _status_path(job_id)
    tmp = path + ".tmp"
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_status(job_id):
    path = _status_path(job_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def list_jobs():
    """Return all jobs sorted by created_at desc."""
    jobs = []
    if not os.path.isdir(JOBS_DIR):
        return jobs
    for jid in os.listdir(JOBS_DIR):
        st = read_status(jid)
        if st:
            jobs.append(st)
    jobs.sort(key=lambda s: s.get('created_at', ''), reverse=True)
    return jobs


class JobManager:
    def create_job(self, csv_path, original_filename, credentials, dry_run=False,
                   managed_credentials=False, assume_role_arn=None,
                   assume_role_external_id=None, review_rows=None,
                   review_columns=None, precheck_processed=True):
        job_id = uuid.uuid4().hex[:12]
        jdir = _job_dir(job_id)
        os.makedirs(jdir, exist_ok=True)

        outputs = {
            "summary_json": "summary.json",
            "records_jsonl": "records.jsonl",
            "records_csv": "records.csv",
        }

        # Needs-review rows (invalid + duplicate) are merged into the main records
        # file as NEED_REVIEW by _run_job, so a single file shows the complete picture.
        # No separate needs-review file is produced.
        review_rows = review_rows or []

        status = {
            "job_id": job_id,
            "original_filename": original_filename,
            "dry_run": dry_run,
            "managed_credentials": managed_credentials,
            "state": "queued",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "finished_at": None,
            "progress": {"total": len(review_rows), "processed": 0, "succeeded": 0,
                         "failed": 0, "skipped": 0, "need_review": len(review_rows)},
            "review_count": len(review_rows),
            "logs": [],
            "summary": None,
            "error": None,
            "outputs": outputs,
        }
        _write_status(job_id, status)

        cancel_flag = {"cancel": False}
        # Slot used to pass fresh credentials into a paused job (expired creds).
        # `timed_out` is set if the bounded credential wait elapses (see _run_job).
        cred_slot = {"event": threading.Event(), "creds": None, "timed_out": False}
        thread = threading.Thread(
            target=self._run_job,
            args=(job_id, csv_path, credentials, dry_run, cancel_flag, cred_slot,
                  managed_credentials, assume_role_arn, assume_role_external_id,
                  precheck_processed, review_rows, review_columns),
            daemon=True,
        )
        with _lock:
            _jobs[job_id] = {
                "thread": thread,
                "cancel_flag": cancel_flag,
                "cred_slot": cred_slot,
            }
        thread.start()
        return job_id

    def cancel_job(self, job_id):
        with _lock:
            job = _jobs.get(job_id)
        if job:
            job["cancel_flag"]["cancel"] = True
            # Wake a job that is paused waiting for credentials so it can exit.
            job["cred_slot"]["event"].set()
            return True
        return False

    def provide_credentials(self, job_id, credentials):
        """Supply fresh credentials to a job paused on expired credentials."""
        with _lock:
            job = _jobs.get(job_id)
        if not job:
            return False
        job["cred_slot"]["creds"] = credentials
        job["cred_slot"]["event"].set()
        return True

    def _run_job(self, job_id, csv_path, credentials, dry_run, cancel_flag, cred_slot,
                 managed_credentials=False, assume_role_arn=None,
                 assume_role_external_id=None, precheck_processed=True,
                 review_rows=None, review_columns=None):
        jdir = _job_dir(job_id)
        status = read_status(job_id)

        def save():
            _write_status(job_id, status)

        def log_cb(msg):
            ts = datetime.now().strftime("%H:%M:%S")
            status["logs"].append(f"[{ts}] {msg}")
            status["logs"] = status["logs"][-500:]  # cap log size
            save()

        review_count = len(review_rows or [])

        def progress_cb(**counters):
            # Total/processed include the needs-review rows so the grid reconciles:
            # total = input-file rows; succeeded + failed + skipped + need_review = total.
            # need_review = pre-validation bad rows (review_count) + rows the engine
            # held back because it could not verify whether a refund already exists
            # (the fail-closed duplicate guard). Both must never be submitted.
            status["progress"].update({
                "total": counters.get("total", 0) + review_count,
                "processed": counters.get("processed", 0) + review_count,
                "succeeded": counters.get("succeeded", 0),
                "failed": counters.get("failed", 0),
                "skipped": counters.get("skipped", 0),
                "need_review": review_count + counters.get("need_review", 0),
            })
            save()

        def request_credentials():
            """Pause the job and block until the user supplies fresh credentials via
            the UI, the job is cancelled, or the bounded wait elapses.

            Returns the creds dict on success, or None to stop the job (on cancel or
            timeout). The wait is bounded by CREDENTIAL_WAIT_TIMEOUT so a run can never
            hang forever in 'awaiting_credentials' if the seller walks away."""
            timeout_min = CREDENTIAL_WAIT_TIMEOUT // 60
            deadline = time.time() + CREDENTIAL_WAIT_TIMEOUT
            status["state"] = "awaiting_credentials"
            status["credentials_deadline"] = datetime.fromtimestamp(deadline).isoformat()
            log_cb(f"Paused: AWS credentials expired. Enter fresh credentials in the UI "
                   f"to resume from where it left off. Waiting up to {timeout_min} min; "
                   f"the job stops on its own if none are provided.")
            save()
            cred_slot["event"].clear()
            next_notice = time.time() + CREDENTIAL_WAIT_NOTICE_INTERVAL
            while not cred_slot["event"].is_set():
                if cancel_flag["cancel"]:
                    return None
                remaining = deadline - time.time()
                if remaining <= 0:
                    cred_slot["timed_out"] = True
                    status["state"] = "credentials_timeout"
                    log_cb(f"Timed out after {timeout_min} min waiting for fresh "
                           f"credentials. Stopping the job — refunds completed so far "
                           f"are recorded; re-run with fresh credentials to finish the "
                           f"rest (already-processed rows are skipped automatically).")
                    save()
                    return None
                # Heartbeat so a long (but legitimate) pause doesn't look frozen.
                if time.time() >= next_notice:
                    mins, secs = divmod(int(remaining), 60)
                    log_cb(f"Still waiting for fresh credentials... about "
                           f"{mins} min {secs} s left before the job stops on its own.")
                    next_notice = time.time() + CREDENTIAL_WAIT_NOTICE_INTERVAL
                    save()
                cred_slot["event"].wait(timeout=1)
            if cancel_flag["cancel"] and not cred_slot["creds"]:
                return None
            new_creds = cred_slot["creds"]
            cred_slot["creds"] = None
            status.pop("credentials_deadline", None)
            status["state"] = "running"
            save()
            return new_creds

        try:
            status["state"] = "running"
            status["started_at"] = datetime.now().isoformat()
            save()
            log_cb(f"Job started ({'dry run' if dry_run else 'live run'}).")

            rows = load_csv(csv_path)
            log_cb(f"Loaded {len(rows)} row(s) from {status['original_filename']}.")

            writer = RecordWriter(
                jsonl_path=os.path.join(jdir, "records.jsonl"),
                csv_path=os.path.join(jdir, "records.csv"),
            )

            # Include the needs-review rows in the main records file so a single file
            # shows the complete picture (status NEED_REVIEW). They are written up front
            # and are NOT counted in the run's progress/summary — they were separated
            # out before processing. No separate needs-review file is produced.
            if review_rows:
                _hmap = build_header_map(review_columns or [])
                _amount_col = resolve_amount_column(_hmap)
                for rr in review_rows:
                    writer.write({
                        "phase": "",
                        "agreement_id": (get_field(rr, _hmap, COL_AGREEMENT_ID) or "").strip(),
                        "invoice_id": (get_field(rr, _hmap, COL_INVOICE_ID) or "").strip(),
                        "amount": (rr.get(_amount_col, "") if _amount_col else ""),
                        "status": "NEED_REVIEW",
                        "billing_adjustment_request_id": "",
                        "message": rr.get(REVIEW_REASON_COL, ""),
                    })

            processor = AdjustmentProcessor(
                access_key=credentials.get("access_key") if credentials else None,
                secret_key=credentials.get("secret_key") if credentials else None,
                session_token=credentials.get("session_token") if credentials else None,
                progress_cb=progress_cb,
                log_cb=log_cb,
                cancel_check=lambda: cancel_flag["cancel"],
                request_credentials=None if managed_credentials else request_credentials,
                managed_credentials=managed_credentials,
                assume_role_arn=assume_role_arn,
                assume_role_external_id=assume_role_external_id,
            )

            counters = {"total": 0, "processed": 0, "succeeded": 0, "failed": 0,
                        "skipped": 0, "need_review": 0}
            try:
                summary = processor.run(rows, writer, dry_run=dry_run, counters=counters,
                                        precheck_processed=precheck_processed)
            except CredentialsCancelled:
                timed_out = cred_slot.get("timed_out", False)
                summary = {
                    "cancelled": True,
                    "reason": "credentials_timeout" if timed_out else "credentials_not_provided",
                    "submitted": 0,
                    "succeeded": counters["succeeded"],
                    "failed": counters["failed"],
                }
                log_cb("Job stopped: timed out waiting for fresh credentials."
                       if timed_out else
                       "Job stopped: fresh credentials were not provided.")

            with open(os.path.join(jdir, "summary.json"), 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)

            status["summary"] = summary
            if cancel_flag["cancel"]:
                status["state"] = "cancelled"
            elif cred_slot.get("timed_out"):
                status["state"] = "credentials_timeout"
            else:
                status["state"] = "completed"
            status["finished_at"] = datetime.now().isoformat()
            skipped_note = (f", Skipped (already processed): {counters['skipped']}"
                            if counters.get('skipped') else "")
            # Need review = pre-validation bad rows + rows the engine held back because
            # it could not verify whether a refund already exists (fail-closed guard).
            total_review = review_count + counters.get('need_review', 0)
            review_note = f", Need review: {total_review}" if total_review else ""
            log_cb(f"Job {status['state']}. "
                   f"Succeeded: {counters['succeeded']}, Failed: {counters['failed']}"
                   f"{skipped_note}{review_note}.")
            save()

        except Exception as e:
            status["state"] = "failed"
            status["error"] = str(e)
            status["finished_at"] = datetime.now().isoformat()
            status["logs"].append(f"ERROR: {e}")
            status["logs"].append(traceback.format_exc())
            save()
        finally:
            with _lock:
                _jobs.pop(job_id, None)
