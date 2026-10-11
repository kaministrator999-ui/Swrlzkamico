"""Detached, account-scoped ChatGPT ZIP import jobs with durable progress receipts.

A browser may disconnect without cancelling the server-owned worker. The ZIP is
temporary: an actual server restart can stop the job; already-committed archive
records remain durable and a repeat import safely skips duplicates.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid

from fastapi import HTTPException

import account_chat_store
import chatgpt_archive
import chatgpt_account_memory
import github_connection as gh

STATUS_TTL = 7 * 86400
LOCK_TTL = 3600
STALE_AFTER = 180
_local_lock = threading.RLock()
_active = set()
_UNLOCK = ("if redis.call('GET',KEYS[1])==ARGV[1] then "
           "return redis.call('DEL',KEYS[1]) else return 0 end")


def _keys(owner):
    account_chat_store._chat_key(owner)
    suffix = hashlib.sha256(owner.encode("utf-8")).hexdigest()
    return ("swrlz:google:chatgpt-import-status:v1:" + suffix,
            "swrlz:google:chatgpt-import-lock:v1:" + suffix)


def _save(owner, state):
    status_key, _ = _keys(owner)
    if gh._redis(account_chat_store._config(), "SET", status_key,
                 json.dumps(state, separators=(",", ":")), "EX", STATUS_TTL) != "OK":
        raise HTTPException(503, "Import job progress could not be saved")


def status(owner):
    status_key, _ = _keys(owner)
    raw = gh._redis(account_chat_store._config(), "GET", status_key)
    if not raw:
        return {"state": "idle"}
    try:
        state = json.loads(raw)
        if state.get("schema") != "swrlz-chatgpt-import-job-v1":
            raise ValueError("Unexpected job status schema")
        if state.get("state") == "running" and time.time() - float(state.get("updatedAt", 0)) > STALE_AFTER:
            state = {**state, "state": "interrupted",
                     "message": "The server job stopped. Saved conversations remain; reselect the ZIP to resume safely."}
        return state
    except (ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(503, "Import job status is unavailable") from exc


def assert_not_running(owner):
    state = status(owner)
    if state["state"] == "running":
        raise HTTPException(409, "An import is already running for this Google account")
    with _local_lock:
        if owner in _active:
            raise HTTPException(409, "An import is already running for this Google account")


def start(owner, filename, upload_id):
    """Claim one job per Google owner before spawning; never wait for a client stream."""
    status_key, lock_key = _keys(owner)
    with _local_lock:
        if owner in _active:
            raise HTTPException(409, "This account is already importing an archive")
        existing = status(owner)
        if existing["state"] == "running":
            raise HTTPException(409, "This account is already importing an archive")
        c = account_chat_store._config()
        claimed = gh._redis(c, "SET", lock_key, upload_id, "NX", "EX", LOCK_TTL)
        if claimed != "OK":
            # A stale/dead process can leave a lock, but never steal a live one.
            if existing["state"] != "interrupted":
                raise HTTPException(409, "A previous import is still active")
            prior = gh._redis(c, "GET", lock_key)
            if prior:
                gh._redis(c, "EVAL", _UNLOCK, "1", lock_key, prior)
            if gh._redis(c, "SET", lock_key, upload_id, "NX", "EX", LOCK_TTL) != "OK":
                raise HTTPException(409, "Another import started; retry the status check")
        state = {"schema": "swrlz-chatgpt-import-job-v1", "jobId": upload_id,
                 "state": "running", "updatedAt": time.time(),
                 "conversations": 0, "created": 0, "updated": 0, "skipped": 0,
                 "unsupported": 0, "addedMessages": 0}
        try:
            _save(owner, state)
            _active.add(owner)
            worker = threading.Thread(target=_work, args=(owner, filename, upload_id, state),
                                      name="chatgpt-import-" + upload_id[:8], daemon=True)
            worker.start()
        except Exception:
            _active.discard(owner)
            gh._redis(c, "EVAL", _UNLOCK, "1", lock_key, upload_id)
            raise
    return state


def _work(owner, filename, token, initial):
    final = dict(initial)
    _, lock_key = _keys(owner)
    try:
        for event in chatgpt_archive.import_archive(filename, owner):
            state = "complete" if event["type"] == "COMPLETE" else "running"
            final = {**final, **{k: v for k, v in event.items() if k != "type"},
                     "state": state, "updatedAt": time.time()}
            _save(owner, final)
    except HTTPException as exc:
        final = {**final, "state": "error", "updatedAt": time.time(),
                 "message": str(exc.detail)[:240]}
        try: _save(owner, final)
        except Exception: pass
    except Exception:
        final = {**final, "state": "error", "updatedAt": time.time(),
                 "message": "Server import failed. Previously saved conversations are safe; reselect the ZIP to retry."}
        try: _save(owner, final)
        except Exception: pass
    finally:
        chatgpt_account_memory.invalidate(owner)
        try: os.unlink(filename)
        except FileNotFoundError: pass
        try: gh._redis(account_chat_store._config(), "EVAL", _UNLOCK, "1", lock_key, token)
        except Exception: pass
        with _local_lock:
            _active.discard(owner)
