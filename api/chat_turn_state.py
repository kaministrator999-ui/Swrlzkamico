"""Server-owned durable Chat turn commits and canonical history.

Authenticated turns fail closed until the USER message is durably observable.
Concurrent account-state writers are reconciled by rebasing the requested message
onto the newest canonical snapshot; a successful write is never considered a
commit until an exact read-back proves the message survived.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random
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

TURN_CONTRACT = "swrlz-chat-canonical-turn-v2"
MAX_COMMIT_ATTEMPTS = 7


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


def _state_from_value(value: dict[str, Any] | None) -> tuple[int, dict[str, Any], list[dict[str, Any]]]:
    if not value:
        return 0, {"version": 1, "currentId": "", "threads": []}, []
    revision = int(value.get("revision") or 0)
    raw_state = value.get("state")
    state = _clean_state(raw_state) if isinstance(raw_state, dict) else {"version": 1, "currentId": "", "threads": []}
    tombstones = _clean_tombstones(value.get("tombstones"))
    return revision, _apply_tombstones(state, tombstones), tombstones


def _message(state: dict[str, Any], thread_id: str, message_id: str, role: str) -> dict[str, Any] | None:
    for thread in state.get("threads", []):
        if thread.get("id") != thread_id:
            continue
        return next((m for m in thread.get("messages", []) if m.get("id") == message_id and m.get("role") == role), None)
    return None


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


def _exact_message(message: dict[str, Any] | None, *, text: str, state_name: str, metadata: dict[str, Any]) -> bool:
    if not message or str(message.get("text") or "") != text or str(message.get("state") or "") != state_name:
        return False
    meta = message.get("meta") if isinstance(message.get("meta"), dict) else {}
    return all(meta.get(key) == value for key, value in metadata.items())


def _backoff(attempt: int) -> None:
    # Small bounded jitter prevents multiple serverless writers from repeatedly
    # re-colliding on the same read/write cadence.
    base = min(0.32, 0.025 * (2 ** attempt))
    time.sleep(base + random.random() * min(0.04, base))


def canonical_history(request: Request, *, thread_id: str, request_id: str, limit: int = 32) -> tuple[list[dict[str, str]], int]:
    user_id = user_id_from_request(request)
    current = _read_blob(user_id)
    revision, state, _ = _state_from_value(current)
    thread = next((item for item in state.get("threads", []) if item.get("id") == thread_id), None)
    if not thread:
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
    return history[-max(1, min(int(limit), 32)):], revision


def _commit_message(user_id: str, *, thread_id: str, message_id: str, role: str, text: str, created_at: int, state_name: str, request_id: str, title_hint: str = "", extra_meta: dict[str, Any] | None = None) -> int:
    if role not in {"user", "assistant"}:
        raise ValueError("CHAT_TURN_ROLE_INVALID")
    if not thread_id or not message_id:
        raise ValueError("CHAT_TURN_ID_INVALID")

    metadata = {"requestId": request_id, "authority": "server", "turnContract": TURN_CONTRACT, **(extra_meta or {})}
    expected_text = text[:200000]
    expected_state = state_name[:32]
    observed_revisions: list[int] = []

    for attempt in range(MAX_COMMIT_ATTEMPTS):
        current = _read_blob(user_id)
        current_revision, canonical, tombstones = _state_from_value(current)
        observed_revisions.append(current_revision)
        tombstone_ids = {str(item.get("threadId") or "") for item in tombstones}
        if thread_id in tombstone_ids:
            raise ValueError("CHAT_TURN_THREAD_TOMBSTONED")

        claimed = _request_message(canonical, request_id=request_id, role=role)
        if claimed is not None:
            claimed_thread_id, existing = claimed
            if claimed_thread_id != thread_id or existing.get("id") != message_id:
                raise ValueError("CHAT_TURN_REQUEST_ID_MESSAGE_CONFLICT")
            if not _exact_message(existing, text=expected_text, state_name=expected_state, metadata=metadata):
                raise ValueError("CHAT_TURN_REQUEST_ID_CONTENT_CONFLICT")
            return current_revision

        stamp = _now_ms()
        threads = canonical.setdefault("threads", [])
        thread = next((item for item in threads if item.get("id") == thread_id), None)
        if thread is None:
            thread = {"id": thread_id, "title": title_hint or "New conversation", "createdAt": created_at or stamp, "updatedAt": stamp, "pinned": False, "messages": []}
            threads.insert(0, thread)

        messages = thread.setdefault("messages", [])
        existing = next((item for item in messages if item.get("id") == message_id), None)
        if existing is not None:
            raise ValueError("CHAT_TURN_MESSAGE_ID_CONFLICT")
        messages.append({"id": message_id, "role": role, "text": expected_text, "createdAt": created_at or stamp, "state": expected_state, "pinned": False, "meta": metadata})
        messages.sort(key=lambda item: int(item.get("createdAt") or 0))
        if len(messages) > 1000:
            del messages[:-1000]
        thread["updatedAt"] = stamp
        if title_hint and (not thread.get("title") or thread.get("title") == "New conversation"):
            thread["title"] = title_hint[:120]
        canonical["currentId"] = thread_id
        canonical["threads"] = sorted(threads, key=lambda item: (bool(item.get("pinned")), int(item.get("updatedAt") or 0)), reverse=True)[:80]

        _write_blob(user_id, {"contract": STATE_CONTRACT, "userId": user_id, "revision": current_revision + 1, "updatedAt": stamp, "state": _clean_state(canonical), "tombstones": tombstones})

        # Do not merely test presence. Exact text/state/metadata proves that the
        # canonical object visible after the write is the turn we intended.
        verified = _read_blob(user_id)
        verified_revision, verified_state, verified_tombstones = _state_from_value(verified)
        if thread_id in {str(item.get("threadId") or "") for item in verified_tombstones}:
            raise RuntimeError("CHAT_TURN_COMMIT_TOMBSTONED")
        visible = _message(verified_state, thread_id, message_id, role)
        if _exact_message(visible, text=expected_text, state_name=expected_state, metadata=metadata):
            return verified_revision

        # Another writer won after our PUT. Re-read/rebase on the next attempt
        # rather than regenerating from stale state or bypassing durability.
        _backoff(attempt)

    trail = ",".join(str(value) for value in observed_revisions[-MAX_COMMIT_ATTEMPTS:])
    raise RuntimeError(f"CHAT_TURN_COMMIT_LOST_RACE:revisions={trail}")


def begin_turn(request: Request, payload: dict[str, Any]) -> CanonicalTurn:
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
    revision = _commit_message(user_id, thread_id=thread_id, message_id=user_message_id, role="user", text=prompt, created_at=user_created_at, state_name="complete", request_id=request_id, title_hint=_title_hint(prompt), extra_meta={"commitPhase": "PRE_GENERATION"})
    return CanonicalTurn(user_id=user_id, account_scope=_scope(user_id), thread_id=thread_id, request_id=request_id, user_message_id=user_message_id, assistant_message_id=assistant_message_id, user_created_at=user_created_at, assistant_created_at=assistant_created_at, user_revision=revision)


def finish_turn(turn: CanonicalTurn, *, text: str, terminal_type: str, reason: str = "") -> int:
    terminal = _bounded(terminal_type, 32).upper() or "FAILED"
    state_name = {"COMPLETED": "complete", "CANCELLED": "cancelled", "FAILED": "failed"}.get(terminal, "failed")
    return _commit_message(turn.user_id, thread_id=turn.thread_id, message_id=turn.assistant_message_id, role="assistant", text=str(text or "")[:200000], created_at=turn.assistant_created_at, state_name=state_name, request_id=turn.request_id, extra_meta={"commitPhase": "TERMINAL", "terminalType": terminal, "terminalReason": _bounded(reason, 2000)})
