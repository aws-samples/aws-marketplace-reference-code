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
import csv
import uuid
import threading
import traceback
from datetime import datetime

# Make the repo-root `core` package importable when run from inside webapp/.
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    AdjustmentProcessor, RecordWriter, load_csv, CredentialsCancelled,
    REVIEW_REASON_COL,
)


JOBS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jobs")
os.makedirs(JOBS_DIR, exist_ok=True)

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
                   review_columns=None):
        job_id = uuid.uuid4().hex[:12]
        jdir = _job_dir(job_id)
        os.makedirs(jdir, exist_ok=True)

        outputs = {
            "summary_json": "summary.json",
            "records_jsonl": "records.jsonl",
            "records_csv": "records.csv",
        }

        # Write the needs-review file (invalid + duplicate rows) so the user can
        # download it and fix those entries separately.
        review_rows = review_rows or []
        if review_rows:
            review_cols = list(review_columns or [])
            if REVIEW_REASON_COL not in review_cols:
                review_cols = review_cols + [REVIEW_REASON_COL]
            with open(os.path.join(jdir, "needs_review.csv"), 'w', newline='',
                      encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=review_cols, extrasaction='ignore')
                w.writeheader()
                for r in review_rows:
                    w.writerow(r)
            outputs["needs_review_csv"] = "needs_review.csv"

        status = {
            "job_id": job_id,
            "original_filename": original_filename,
            "dry_run": dry_run,
            "managed_credentials": managed_credentials,
            "state": "queued",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "finished_at": None,
            "progress": {"total": 0, "processed": 0, "succeeded": 0, "failed": 0},
            "review_count": len(review_rows),
            "logs": [],
            "summary": None,
            "error": None,
            "outputs": outputs,
        }
        _write_status(job_id, status)

        cancel_flag = {"cancel": False}
        # Slot used to pass fresh credentials into a paused job (expired creds).
        cred_slot = {"event": threading.Event(), "creds": None}
        thread = threading.Thread(
            target=self._run_job,
            args=(job_id, csv_path, credentials, dry_run, cancel_flag, cred_slot,
                  managed_credentials, assume_role_arn, assume_role_external_id),
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
                 assume_role_external_id=None):
        jdir = _job_dir(job_id)
        status = read_status(job_id)

        def save():
            _write_status(job_id, status)

        def log_cb(msg):
            ts = datetime.now().strftime("%H:%M:%S")
            status["logs"].append(f"[{ts}] {msg}")
            status["logs"] = status["logs"][-500:]  # cap log size
            save()

        def progress_cb(**counters):
            status["progress"].update({
                "total": counters.get("total", status["progress"]["total"]),
                "processed": counters.get("processed", 0),
                "succeeded": counters.get("succeeded", 0),
                "failed": counters.get("failed", 0),
            })
            save()

        def request_credentials():
            """Pause the job and block until the user supplies fresh credentials
            via the UI, or the job is cancelled. Returns creds dict or None."""
            status["state"] = "awaiting_credentials"
            log_cb("Paused: AWS credentials expired. Enter fresh credentials in the "
                   "UI to resume from where it left off.")
            save()
            cred_slot["event"].clear()
            while not cred_slot["event"].is_set():
                if cancel_flag["cancel"]:
                    return None
                cred_slot["event"].wait(timeout=1)
            if cancel_flag["cancel"] and not cred_slot["creds"]:
                return None
            new_creds = cred_slot["creds"]
            cred_slot["creds"] = None
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

            counters = {"total": 0, "processed": 0, "succeeded": 0, "failed": 0}
            try:
                summary = processor.run(rows, writer, dry_run=dry_run, counters=counters)
            except CredentialsCancelled:
                summary = {
                    "cancelled": True,
                    "reason": "credentials_not_provided",
                    "submitted": 0,
                    "succeeded": counters["succeeded"],
                    "failed": counters["failed"],
                }
                log_cb("Job stopped: fresh credentials were not provided.")

            with open(os.path.join(jdir, "summary.json"), 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)

            status["summary"] = summary
            status["state"] = "cancelled" if cancel_flag["cancel"] else "completed"
            status["finished_at"] = datetime.now().isoformat()
            log_cb(f"Job {status['state']}. "
                   f"Succeeded: {counters['succeeded']}, Failed: {counters['failed']}.")
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
