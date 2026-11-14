"""Durable, account-owned live coding progress and noninterrupting control inbox.

This is a control plane, not a second inference model. Never report a steering
instruction as applied until an execution owner explicitly acknowledges it.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from typing import Any

from api.durable_redis_store import RedisRestChatStore

REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
MAX_INSTRUCTION = 4000
MAX_CONTROLS = 40
TERMINAL = {"COMPLETE", "COMPLETED", "FAILED", "CANCELLED"}

def _owned(store: RedisRestChatStore, user_id: str, request_id: str, thread_id: str = ""):
    if not REQUEST_ID.fullmatch(request_id):
        raise ValueError("INVALID_REQUEST_ID")
    job = store.get_generation(user_id=user_id, request_id=request_id)
    if job is None or job.user_id != user_id or (thread_id and job.thread_id != thread_id):
        raise LookupError("GENERATION_NOT_FOUND")
    return job

def _key(store: RedisRestChatStore, user_id: str, request_id: str) -> str:
    return store._key("coding-controls-v1", user_id, request_id)

def _read_controls(store: RedisRestChatStore, user_id: str, request_id: str) -> list[dict[str, Any]]:
    raw = store._command("LRANGE", _key(store, user_id, request_id), 0, -1, sensitive=True)
    controls: list[dict[str, Any]] = []
    for item in raw or []:
        try:
            entry = json.loads(item)
        except (ValueError, TypeError):
            continue
        if isinstance(entry, dict) and entry.get("kind") in {"STEER", "CHECKPOINT"}:
            controls.append(entry)
    return controls

def snapshot(*, user_id: str, request_id: str, thread_id: str = "", store=None) -> dict[str, Any]:
    store = store or RedisRestChatStore.from_env()
    job = _owned(store, user_id, request_id, thread_id)
    events = store.list_events(user_id, request_id, after_seq=-1)
    last = events[-1] if events else None
    phases = []
    for event in events[-60:]:
        payload = event.payload if isinstance(event.payload, dict) else {}
        phase = str(payload.get("phase") or event.event_type or "")
        if phase and (not phases or phases[-1] != phase):
            phases.append(phase)
    controls = _read_controls(store, user_id, request_id)
    terminal = str(job.state).upper() in TERMINAL
    return {
        "requestId": request_id,
        "threadId": job.thread_id,
        "state": job.state,
        "lastSeq": int(job.last_seq),
        "phase": phases[-1] if phases else str(job.state),
        "recentPhases": phases[-12:],
        "startedAt": float(job.created_at),
        "updatedAt": float(job.updated_at),
        "terminal": terminal,
        "verifiedProgress": None,
        "remainingWork": None,
        "estimate": None,
        "note": "Completion percentage and remaining work are unavailable until the coding executor publishes verified task milestones.",
        "controlInbox": controls[-MAX_CONTROLS:],
    }

def record_control(*, user_id: str, request_id: str, thread_id: str,
                   kind: str, text: str = "", store=None) -> dict[str, Any]:
    store = store or RedisRestChatStore.from_env()
    job = _owned(store, user_id, request_id, thread_id)
    kind = str(kind or "").upper()
    if kind not in {"STEER", "CHECKPOINT"}:
        raise ValueError("INVALID_CONTROL_KIND")
    text = str(text or "").strip()
    if kind == "STEER" and (not text or len(text) > MAX_INSTRUCTION):
        raise ValueError("INVALID_INSTRUCTION")
    if kind == "CHECKPOINT":
        text = ""
    if str(job.state).upper() in TERMINAL:
        raise ValueError("GENERATION_ALREADY_TERMINAL")
    item = {
        "controlId": "control_" + uuid.uuid4().hex,
        "kind": kind,
        "text": text,
        "state": "RECORDED_PENDING_EXECUTOR",
        "recordedAt": time.time(),
        "requestId": request_id,
    }
    key = _key(store, user_id, request_id)
    # Each Redis operation is atomic. An inbox append never cancels or restarts
    # a running generation, and no client-supplied model/worker identity is trusted.
    store._command("RPUSH", key, json.dumps(item, ensure_ascii=False), sensitive=True)
    store._command("LTRIM", key, -MAX_CONTROLS, -1, sensitive=True)
    store._command("EXPIRE", key, 86400, sensitive=True)
    return {"accepted": True, "control": item, "applied": False,
            "note": "Recorded without interrupting generation; the executor must acknowledge and apply this at a safe checkpoint."}

def mark_applied(*, user_id: str, request_id: str, control_id: str,
                 executor_receipt: str, store=None) -> bool:
    """Executor-only acknowledgement; must never be exposed as a browser action."""
    store = store or RedisRestChatStore.from_env()
    _owned(store, user_id, request_id)
    if not executor_receipt.strip():
        raise ValueError("EXECUTOR_RECEIPT_REQUIRED")
    key = _key(store, user_id, request_id)
    # Optimistic compare/retry keeps concurrent writes from silently replacing
    # a new steering instruction; no browser API accepts executor receipts.
    for _attempt in range(4):
        raw = store._command("LRANGE", key, 0, -1, sensitive=True) or []
        for index, item in enumerate(raw):
            entry = json.loads(item)
            if entry.get("controlId") != control_id:
                continue
            if entry.get("state") == "APPLIED":
                return True
            updated = {**entry, "state": "APPLIED",
                       "appliedAt": time.time(),
                       "executorReceipt": str(executor_receipt)[:160]}
            script = ("if redis.call('LINDEX',KEYS[1],ARGV[1])==ARGV[2] then "
                      "redis.call('LSET',KEYS[1],ARGV[1],ARGV[3]);return 1 end;return 0")
            changed = store._command(
                "EVAL", script, 1, key, index, item,
                json.dumps(updated, ensure_ascii=False), sensitive=True)
            if int(changed or 0) == 1:
                return True
            break
        else:
            return False
    return False

def status_answer(view: dict[str, Any], question: str = "") -> str:
    phase = str(view.get("phase") or "unknown").replace("_", " ").lower()
    state = str(view.get("state") or "unknown").lower()
    pending = sum(c.get("state") == "RECORDED_PENDING_EXECUTOR"
                  for c in view.get("controlInbox") or [])
    sentence = f"Generation is {state}; latest reported phase: {phase}."
    if pending:
        sentence += f" {pending} control request(s) recorded, not yet confirmed applied."
    sentence += " No verified percent-complete or finish-time estimate is available."
    return sentence
