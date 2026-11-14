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
    # One bounded Redis MGET: do not perform thousands of HTTP reads just
    # because a large code response streamed thousands of tokens.
    end = int(job.last_seq)
    first = max(1, end - 15)
    keys = [store._key("event", user_id, request_id, str(seq))
            for seq in range(first, end + 1)]
    raw_events = store._command("MGET", *keys, sensitive=True) if keys else []
    events = []
    for raw in raw_events or []:
        try:
            event = json.loads(raw) if raw else None
        except (TypeError, ValueError):
            continue
        if isinstance(event, dict) and str(event.get("user_id") or "") == user_id:
            events.append(event)
    phases = []
    excerpt = ""
    for event in events:
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        phase = str(payload.get("phase") or event.get("event_type") or "")
        if phase and (not phases or phases[-1] != phase):
            phases.append(phase)
        if payload.get("type") == "DELTA" and payload.get("text"):
            excerpt = (excerpt + str(payload["text"]))[-1800:]
    controls = _read_controls(store, user_id, request_id)
    terminal = str(job.state).upper() in TERMINAL
    return {
        "requestId": request_id,
        "threadId": job.thread_id,
        "state": job.state,
        "lastSeq": int(job.last_seq),
        "phase": phases[-1] if phases else str(job.state),
        "recentPhases": phases[-12:],
        "recentOutputExcerpt": excerpt,
        "recentOutputIsComplete": False,
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

def transition_control(*, user_id: str, request_id: str, control_id: str,
                       state: str, revision_request_id: str = "", store=None) -> bool:
    """Optimistically record an executor transition, never a browser assertion."""
    allowed = {
        "REVISION_QUEUED", "REVISION_PRODUCED_UNVERIFIED", "REVISION_FAILED",
        "DEFERRED_SOURCE_TOO_LARGE", "DEFERRED_NO_SOURCE",
        "SOURCE_AVAILABLE_UNVERIFIED",
    }
    if state not in allowed:
        raise ValueError("INVALID_EXECUTOR_TRANSITION")
    store = store or RedisRestChatStore.from_env()
    _owned(store, user_id, request_id)
    key = _key(store, user_id, request_id)
    script = ("if redis.call('LINDEX',KEYS[1],ARGV[1])==ARGV[2] then "
              "redis.call('LSET',KEYS[1],ARGV[1],ARGV[3]);return 1 end;return 0")
    for _ in range(4):
        raw = store._command("LRANGE", key, 0, -1, sensitive=True) or []
        for index, item in enumerate(raw):
            try:
                entry = json.loads(item)
            except (ValueError, TypeError):
                continue
            if entry.get("controlId") != control_id:
                continue
            if entry.get("state") == state and entry.get("revisionRequestId", "") == revision_request_id:
                return True
            next_entry = {**entry, "state": state, "updatedAt": time.time()}
            if revision_request_id:
                next_entry["revisionRequestId"] = revision_request_id
            updated = json.dumps(next_entry, ensure_ascii=False)
            applied = store._command(
                "EVAL", script, 1, key, index, item, updated, sensitive=True)
            if int(applied or 0) == 1:
                return True
            break
        else:
            return False
    return False

async def queue_post_generation_revision(*, user_id: str, request_id: str,
                                         thread_id: str, source: str,
                                         completed: bool, store=None) -> dict[str, Any]:
    """At the *end* of generation, schedule user-requested edits as a new turn.

    This preserves the original complete response and never alters in-flight
    decode buffers. Large sources are deferred rather than silently truncated.
    """
    from hashlib import sha256
    from api.canonical_redis_state import begin_canonical_turn
    from api.hf_generation_dispatch import send as queue_send

    store = store or RedisRestChatStore.from_env()
    _owned(store, user_id, request_id, thread_id)
    controls = _read_controls(store, user_id, request_id)
    pending = [c for c in controls if c.get("state") == "RECORDED_PENDING_EXECUTOR"]
    for control in pending:
        if control.get("kind") != "CHECKPOINT":
            continue
        transition_control(
            user_id=user_id, request_id=request_id,
            control_id=control["controlId"],
            state="SOURCE_AVAILABLE_UNVERIFIED" if completed and source
            else "DEFERRED_NO_SOURCE", store=store)
    steering = [c for c in pending if c.get("kind") == "STEER"]
    if not steering:
        return {"queued": False, "reason": "NO_STEERING"}
    if not completed or not source:
        for c in steering:
            transition_control(user_id=user_id, request_id=request_id,
                               control_id=c["controlId"], state="DEFERRED_NO_SOURCE", store=store)
        return {"queued": False, "reason": "SOURCE_NOT_COMPLETED"}
    if len(source) > 12000:
        for c in steering:
            transition_control(user_id=user_id, request_id=request_id,
                               control_id=c["controlId"], state="DEFERRED_SOURCE_TOO_LARGE", store=store)
        return {"queued": False, "reason": "SOURCE_EXCEEDS_SAFE_REVISION_CONTEXT"}
    if sum(len(str(c.get("text") or "")) for c in steering) > 6000:
        for c in steering:
            transition_control(user_id=user_id, request_id=request_id,
                               control_id=c["controlId"], state="DEFERRED_SOURCE_TOO_LARGE", store=store)
        return {"queued": False, "reason": "STEERING_EXCEEDS_SAFE_REVISION_CONTEXT"}
    requests = "\n".join(f"{i+1}. {str(c.get('text') or '')}" for i,c in enumerate(steering))
    prompt = (
        "Continue the existing project, do not start over from an unrelated design. "
        "Revise the prior complete source to incorporate the following user-provided "
        "steering changes. Preserve working features and interfaces. Return the full "
        "updated code and identify any unverified behavior; do not invent test results."
        "\nUSER_REQUESTED_REVISIONS:\n" + requests +
        "\nEXISTING_SOURCE_BEGIN\n" + source + "\nEXISTING_SOURCE_END"
    )
    # The canonical turn is durable before any worker is submitted.
    seed = (request_id + ":" + steering[0]["controlId"]).encode()
    revision_id = "rev-" + sha256(seed).hexdigest()[:32]
    user_message_id = "message-" + revision_id
    assistant_message_id = "assistant-" + revision_id
    now_ms = int(time.time() * 1000)
    begin_canonical_turn(
        user_id=user_id, thread_id=thread_id, request_id=revision_id,
        user_message_id=user_message_id, assistant_message_id=assistant_message_id,
        prompt=prompt, title="Code revision", user_created_at_ms=now_ms,
        assistant_created_at_ms=now_ms + 1,
        turn_contract="swrlz-live-code-steering-v1")
    work = {
        "contract": "swrlz-lalm-workstation-job-v1",
        "requestId": revision_id, "userId": user_id,
        "threadId": thread_id,
        "userMessageId": user_message_id, "assistantMessageId": assistant_message_id,
        "prompt": prompt, "history": [], "pinnedContext": [],
        "payload": {"requestId": revision_id, "prompt": prompt,
                    "profileId": "AUTO", "presentationIntent": "CODE",
                    "liveSteeringParent": request_id},
        "acceptedAt": time.time(),
    }
    await queue_send("swrlz-generation", work, idempotency_key=revision_id)
    for c in steering:
        transition_control(user_id=user_id, request_id=request_id,
                           control_id=c["controlId"], state="REVISION_QUEUED",
                           revision_request_id=revision_id, store=store)
    return {"queued": True, "revisionRequestId": revision_id,
            "changes": len(steering)}

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
