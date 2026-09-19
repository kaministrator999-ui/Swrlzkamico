"""Server-owned durable Chat turn commits and canonical history.

Canonical storage is selected explicitly. Redis preserves exact browser/server IDs
and commits the pre-generation tuple atomically; Blob remains the legacy backend.
Generation remains fail-closed when the selected durable backend cannot commit.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
import time
from typing import Any

from fastapi import Request

from api.chat_state import (
    CONTRACT as STATE_CONTRACT,
    _apply_tombstones,
    _clean_state,
    _clean_tombstones,
    _read_blob,
    _write_blob,
)
from api.google_account import user_id_from_request
from api.hot_loader import get_chat_history_policy
from api import canonical_redis_state
from api.chat_client_debug import _lockdown as _chat_lockdown

TURN_CONTRACT = "swrlz-chat-canonical-turn-v1"
MAX_COMMIT_ATTEMPTS = 3
_HISTORY_CAMERA_CONTRACT = "swrlz-chat-history-policy-loader-v1"


@dataclass(frozen=True)
class CanonicalTurn:
    user_id: str
    account_scope: str
    thread_id: str
    request_id: str
    user_message_id: str
    assistant_message_id: str
    user_created_at: int
    assistant_created_at: int
    user_revision: int
    storage_backend: str = "blob"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _stamp(value: Any, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return parsed if parsed > 0 else fallback


def _bounded(value: Any, maximum: int) -> str:
    return str(value or "").strip()[:maximum]


def _scope(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:24]


def _derived_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()[:28]
    return f"{prefix}:{digest}"


def _title_hint(prompt: str) -> str:
    compact = " ".join(prompt.split())
    return compact[:72] or "New conversation"


def _history_camera(stage: str, **fields: Any) -> None:
    record = {"contract": _HISTORY_CAMERA_CONTRACT, "stage": stage, "atUnixMs": _now_ms()}
    for key, value in fields.items():
        if value is None or isinstance(value, (str, int, float, bool)):
            record[str(key)[:64]] = value
    print("SWRLZ_CHAT_HISTORY_POLICY " + json.dumps(record, ensure_ascii=False, separators=(",", ":")), flush=True)


def canonical_backend() -> str:
    """Return the selected durable backend without silently crossing authorities.

    `auto` is the compatibility default: configured Redis is authoritative when
    available, otherwise legacy Blob remains the fallback. Explicit `redis` stays
    fail-closed when Redis is not configured; explicit `blob` remains available
    for rollback/migration diagnostics.
    """
    requested = os.environ.get("SWRLZ_CHAT_CANONICAL_BACKEND", "auto").strip().lower() or "auto"
    redis_ready=canonical_redis_state.configured()
    _chat_lockdown("turn-backend-select-enter", requested=requested, redisConfigured=redis_ready)
    if requested == "auto":
        selected="redis" if redis_ready else "blob"
        _chat_lockdown("turn-backend-select-exit", selected=selected)
        return selected
    if requested == "redis":
        if not canonical_redis_state.configured():
            raise RuntimeError("CHAT_CANONICAL_REDIS_NOT_CONFIGURED")
        return "redis"
    if requested == "blob":
        _chat_lockdown("turn-backend-select-exit", selected="blob")
        return "blob"
    raise RuntimeError("CHAT_CANONICAL_BACKEND_INVALID")


def canonical_backend_status() -> dict[str, Any]:
    requested = os.environ.get("SWRLZ_CHAT_CANONICAL_BACKEND", "auto").strip().lower() or "auto"
    redis_ready = canonical_redis_state.configured()
    try:
        selected = canonical_backend()
        error = ""
    except RuntimeError as exc:
        selected = "unavailable"
        error = str(exc)
    return {"requested": requested, "selected": selected, "redisConfigured": redis_ready, "error": error}


def _state_from_value(value: dict[str, Any] | None) -> tuple[int, dict[str, Any], list[dict[str, Any]]]:
    if not value:
        return 0, {"version": 1, "currentId": "", "threads": []}, []
    revision = int(value.get("revision") or 0)
    raw_state = value.get("state")
    state = _clean_state(raw_state) if isinstance(raw_state, dict) else {"version": 1, "currentId": "", "threads": []}
    tombstones = _clean_tombstones(value.get("tombstones"))
    return revision, _apply_tombstones(state, tombstones), tombstones


def _contains_message(state: dict[str, Any], thread_id: str, message_id: str, role: str) -> bool:
    for thread in state.get("threads", []):
        if thread.get("id") == thread_id:
            return any(message.get("id") == message_id and message.get("role") == role for message in thread.get("messages", []))
    return False


def _request_message(state: dict[str, Any], *, request_id: str, role: str) -> tuple[str, dict[str, Any]] | None:
    for thread in state.get("threads", []):
        thread_id = str(thread.get("id") or "")
        for message in thread.get("messages", []):
            if not isinstance(message, dict) or message.get("role") != role:
                continue
            meta = message.get("meta") if isinstance(message.get("meta"), dict) else {}
            if str(meta.get("requestId") or "") == request_id:
                return thread_id, message
    return None


def _bundled_redis_history(*, user_id: str, thread_id: str, request_id: str, limit: int) -> list[dict[str, str]]:
    return canonical_redis_state.canonical_history(
        user_id=user_id, thread_id=thread_id, request_id=request_id, limit=limit
    )


def _hot_redis_history(*, user_id: str, thread_id: str, request_id: str, limit: int) -> list[dict[str, str]]:
    """Use the runtime-hot read policy when valid, with bundled Server fallback.

    This boundary never accepts browser history as authority. Both the hot path and
    the fallback read durable server-owned message records only.
    """
    try:
        policy, source = get_chat_history_policy()
    except Exception as exc:
        _history_camera(
            "policy-load-failed",
            requestId=request_id,
            threadId=thread_id,
            errorType=type(exc).__name__,
            fallback="bundled",
        )
        return _bundled_redis_history(user_id=user_id, thread_id=thread_id, request_id=request_id, limit=limit)
    if policy is None:
        _history_camera("policy-bundled", requestId=request_id, threadId=thread_id, source=source)
        return _bundled_redis_history(user_id=user_id, thread_id=thread_id, request_id=request_id, limit=limit)
    try:
        result = policy.resolve_history(
            redis=canonical_redis_state.store(),
            user_id=user_id,
            thread_id=thread_id,
            request_id=request_id,
            limit=limit,
        )
        if not isinstance(result, dict) or not isinstance(result.get("history"), list):
            raise RuntimeError("HOT_CHAT_HISTORY_POLICY_RESULT_INVALID")
        history: list[dict[str, str]] = []
        for item in result.get("history") or []:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role") or "").strip().upper()
            text = str(item.get("text") or "").strip()
            if role in {"USER", "ASSISTANT"} and text:
                history.append({"role": role, "text": text[:2000]})
        meta = result.get("meta") if isinstance(result.get("meta"), dict) else {}
        bounded = history[-max(1, min(int(limit), 32)):]
        _history_camera(
            "policy-applied",
            requestId=request_id,
            threadId=thread_id,
            source=source,
            revision=str(meta.get("revision") or getattr(policy, "HOT_REVISION", ""))[:96],
            currentIndexedMessages=int(meta.get("currentIndexedMessages") or 0),
            legacyIndexedMessages=int(meta.get("legacyIndexedMessages") or 0),
            mergedMessages=int(meta.get("mergedMessages") or 0),
            selectedMessages=len(bounded),
        )
        return bounded
    except Exception as exc:
        _history_camera(
            "policy-execution-failed",
            requestId=request_id,
            threadId=thread_id,
            errorType=type(exc).__name__,
            fallback="bundled",
        )
        return _bundled_redis_history(user_id=user_id, thread_id=thread_id, request_id=request_id, limit=limit)


def canonical_history(request: Request, *, thread_id: str, request_id: str, limit: int = 32) -> tuple[list[dict[str, str]], int]:
    _chat_lockdown("turn-history-enter", request_id=request_id, threadId=thread_id, limit=limit)
    user_id = user_id_from_request(request)
    if canonical_backend() == "redis":
        history=_hot_redis_history(user_id=user_id, thread_id=thread_id, request_id=request_id, limit=limit)
        _chat_lockdown("turn-history-exit", request_id=request_id, threadId=thread_id, backend="redis", revision=0, history=history, historyMessages=len(history))
        return history, 0

    current = _read_blob(user_id)
    revision, state, _ = _state_from_value(current)
    thread = next((item for item in state.get("threads", []) if item.get("id") == thread_id), None)
    if not thread:
        _chat_lockdown("turn-history-exit", request_id=request_id, threadId=thread_id, backend="blob", revision=revision, history=[], historyMessages=0)
        return [], revision
    history: list[dict[str, str]] = []
    for message in thread.get("messages", []):
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or "").lower()
        text = str(message.get("text") or "").strip()
        meta = message.get("meta") if isinstance(message.get("meta"), dict) else {}
        if str(meta.get("requestId") or "") == request_id:
            continue
        if role in {"user", "assistant"} and text:
            history.append({"role": role.upper(), "text": text[:2000]})
    bounded=history[-max(1, min(int(limit), 32)):]
    _chat_lockdown("turn-history-exit", request_id=request_id, threadId=thread_id, backend="blob", revision=revision, history=bounded, historyMessages=len(bounded))
    return bounded, revision


def _commit_blob_message(user_id: str, *, thread_id: str, message_id: str, role: str, text: str, created_at: int, state_name: str, request_id: str, title_hint: str = "", extra_meta: dict[str, Any] | None = None) -> int:
    _chat_lockdown("turn-blob-commit-enter", request_id=request_id, threadId=thread_id, messageId=message_id, role=role, state=state_name, textChars=len(text))
    if role not in {"user", "assistant"}:
        raise ValueError("CHAT_TURN_ROLE_INVALID")
    if not thread_id or not message_id:
        raise ValueError("CHAT_TURN_ID_INVALID")
    metadata = {"requestId": request_id, "authority": "server", "turnContract": TURN_CONTRACT, **(extra_meta or {})}
    expected_text = text[:200000]
    expected_state = state_name[:32]

    for attempt in range(MAX_COMMIT_ATTEMPTS):
        _chat_lockdown("turn-blob-commit-attempt", request_id=request_id, threadId=thread_id, messageId=message_id, attempt=attempt)
        current = _read_blob(user_id)
        current_revision, canonical, tombstones = _state_from_value(current)
        _chat_lockdown("turn-blob-state-read", request_id=request_id, threadId=thread_id, attempt=attempt, currentRevision=current_revision, threadCount=len(canonical.get("threads",[])), tombstones=len(tombstones))
        if thread_id in {str(item.get("threadId") or "") for item in tombstones}:
            raise ValueError("CHAT_TURN_THREAD_TOMBSTONED")
        stamp = _now_ms()
        threads = canonical.setdefault("threads", [])
        claimed = _request_message(canonical, request_id=request_id, role=role)
        if claimed is not None:
            claimed_thread_id, existing = claimed
            if claimed_thread_id != thread_id or existing.get("id") != message_id:
                raise ValueError("CHAT_TURN_REQUEST_ID_MESSAGE_CONFLICT")
            existing_meta = existing.get("meta") if isinstance(existing.get("meta"), dict) else {}
            if str(existing.get("text") or "") != expected_text:
                raise ValueError("CHAT_TURN_MESSAGE_ID_CONTENT_CONFLICT")
            if str(existing.get("state") or "") != expected_state:
                raise ValueError("CHAT_TURN_MESSAGE_ID_STATE_CONFLICT")
            for key, value in metadata.items():
                if existing_meta.get(key) != value:
                    raise ValueError("CHAT_TURN_MESSAGE_ID_META_CONFLICT")
            return current_revision

        thread = next((item for item in threads if item.get("id") == thread_id), None)
        if thread is None:
            thread = {"id": thread_id, "title": title_hint or "New conversation", "createdAt": created_at or stamp, "updatedAt": stamp, "pinned": False, "messages": []}
            threads.insert(0, thread)
        messages = thread.setdefault("messages", [])
        existing = next((item for item in messages if item.get("id") == message_id), None)
        if existing is not None:
            if existing.get("role") != role:
                raise ValueError("CHAT_TURN_MESSAGE_ID_ROLE_CONFLICT")
            raise ValueError("CHAT_TURN_MESSAGE_ID_REQUEST_CONFLICT")
        messages.append({"id": message_id, "role": role, "text": expected_text, "createdAt": created_at or stamp, "state": expected_state, "pinned": False, "meta": metadata})
        messages.sort(key=lambda item: int(item.get("createdAt") or 0))
        if len(messages) > 1000:
            del messages[:-1000]
        thread["updatedAt"] = stamp
        if title_hint and (not thread.get("title") or thread.get("title") == "New conversation"):
            thread["title"] = title_hint[:120]
        canonical["currentId"] = thread_id
        canonical["threads"] = sorted(threads, key=lambda item: (bool(item.get("pinned")), int(item.get("updatedAt") or 0)), reverse=True)[:80]
        next_revision = current_revision + 1
        _chat_lockdown("turn-blob-write-enter", request_id=request_id, threadId=thread_id, messageId=message_id, nextRevision=next_revision)
        _write_blob(user_id, {"contract": STATE_CONTRACT, "userId": user_id, "revision": next_revision, "updatedAt": stamp, "state": _clean_state(canonical), "tombstones": tombstones})
        _chat_lockdown("turn-blob-write-exit", request_id=request_id, threadId=thread_id, messageId=message_id, nextRevision=next_revision)
        verified = _read_blob(user_id)
        verified_revision, verified_state, verified_tombstones = _state_from_value(verified)
        if thread_id in {str(item.get("threadId") or "") for item in verified_tombstones}:
            raise RuntimeError("CHAT_TURN_COMMIT_TOMBSTONED")
        if _contains_message(verified_state, thread_id, message_id, role):
            _chat_lockdown("turn-blob-commit-verified", request_id=request_id, threadId=thread_id, messageId=message_id, verifiedRevision=verified_revision, attempt=attempt)
            return verified_revision
        _chat_lockdown("turn-blob-commit-retry", request_id=request_id, threadId=thread_id, messageId=message_id, attempt=attempt)
        time.sleep(0.04 * (attempt + 1))
    raise RuntimeError("CHAT_TURN_COMMIT_LOST_RACE")


def begin_turn(request: Request, payload: dict[str, Any]) -> CanonicalTurn:
    request_hint=str(payload.get("requestId") or "")[:128]
    _chat_lockdown("turn-begin-enter", request_id=request_hint, payload=payload)
    user_id = user_id_from_request(request)
    now = _now_ms()
    request_id = _bounded(payload.get("requestId"), 128)
    prompt = _bounded(payload.get("prompt"), 16000)
    if not request_id or not prompt:
        raise ValueError("CHAT_TURN_REQUEST_INVALID")
    thread_id = _bounded(payload.get("threadId"), 160) or _derived_id("thread", user_id, request_id)
    user_message_id = _bounded(payload.get("messageId"), 160) or _derived_id("message", request_id, thread_id, prompt)
    assistant_message_id = _bounded(payload.get("assistantMessageId"), 160) or _derived_id("assistant", request_id, thread_id)
    user_created_at = _stamp(payload.get("userCreatedAt"), now)
    assistant_created_at = _stamp(payload.get("assistantCreatedAt"), max(now, user_created_at + 1))
    backend = canonical_backend()
    _chat_lockdown("turn-begin-identities", request_id=request_id, threadId=thread_id, userMessageId=user_message_id, assistantMessageId=assistant_message_id, backend=backend)
    if backend == "redis":
        canonical_redis_state.begin_canonical_turn(
            user_id=user_id, thread_id=thread_id, request_id=request_id,
            user_message_id=user_message_id, assistant_message_id=assistant_message_id,
            prompt=prompt, title=_title_hint(prompt), user_created_at_ms=user_created_at,
            assistant_created_at_ms=assistant_created_at, turn_contract=TURN_CONTRACT,
        )
        revision = 0
    else:
        revision = _commit_blob_message(user_id, thread_id=thread_id, message_id=user_message_id, role="user", text=prompt, created_at=user_created_at, state_name="complete", request_id=request_id, title_hint=_title_hint(prompt), extra_meta={"commitPhase": "PRE_GENERATION"})
    turn=CanonicalTurn(user_id=user_id, account_scope=_scope(user_id), thread_id=thread_id, request_id=request_id, user_message_id=user_message_id, assistant_message_id=assistant_message_id, user_created_at=user_created_at, assistant_created_at=assistant_created_at, user_revision=revision, storage_backend=backend)
    _chat_lockdown("turn-begin-exit", request_id=request_id, threadId=thread_id, userMessageId=user_message_id, assistantMessageId=assistant_message_id, backend=backend, revision=revision)
    return turn


def finish_turn(turn: CanonicalTurn, *, text: str, terminal_type: str, reason: str = "") -> int:
    terminal = _bounded(terminal_type, 32).upper() or "FAILED"
    _chat_lockdown("turn-finish-enter", request_id=turn.request_id, threadId=turn.thread_id, assistantMessageId=turn.assistant_message_id, backend=turn.storage_backend, terminalType=terminal, reason=reason, textChars=len(str(text or "")), text=str(text or "")[:16000])
    if turn.storage_backend == "redis":
        canonical_redis_state.finish_canonical_turn(
            user_id=turn.user_id, request_id=turn.request_id, assistant_message_id=turn.assistant_message_id,
            text=str(text or "")[:200000], terminal_type=terminal, reason=_bounded(reason, 2000), turn_contract=TURN_CONTRACT,
        )
        _chat_lockdown("turn-finish-exit", request_id=turn.request_id, threadId=turn.thread_id, backend="redis", revision=0, terminalType=terminal)
        return 0
    state_name = {"COMPLETED": "complete", "CANCELLED": "cancelled", "FAILED": "failed"}.get(terminal, "failed")
    return _commit_blob_message(turn.user_id, thread_id=turn.thread_id, message_id=turn.assistant_message_id, role="assistant", text=str(text or "")[:200000], created_at=turn.assistant_created_at, state_name=state_name, request_id=turn.request_id, extra_meta={"commitPhase": "TERMINAL", "terminalType": terminal, "terminalReason": _bounded(reason, 2000)})