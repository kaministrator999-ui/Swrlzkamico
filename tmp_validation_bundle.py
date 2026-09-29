# FILE: api/chat_state.py
"""Durable account-scoped Chat thread/message state.

Authenticated server state is canonical. Browser state is presentation/cache only.
Whole-snapshot writes are retired for signed-in state; browser metadata changes are
applied through bounded server-owned mutations.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.parse
import uuid
from typing import Any

import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.google_account import AuthenticationError, user_id_from_request
from api.canonical_redis_state import store as canonical_redis_store

APP_VERSION = "1.1.5"
CONTRACT = "swrlz-chat-account-state-v1"
MUTATION_CONTRACT = "swrlz-chat-account-mutation-v1"
BLOB_API = "https://vercel.com/api/blob"
PREFIX = "swrlz/chat/account-state/v1"
MAX_STATE_BYTES = 2 * 1024 * 1024
MAX_THREADS = 80
MAX_MESSAGES_PER_THREAD = 1000
MAX_MUTATIONS = 32
MAX_TOMBSTONES = 320
MAX_MESSAGE_PINS_PER_THREAD = 24
REDIS_PREFIX = "swrlz:v1:chat-state:"

app = FastAPI(title="SWRLZ Chat State", version=APP_VERSION, docs_url=None, redoc_url=None, openapi_url=None)


def _headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store, no-transform",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
    }


def _error(status: int, code: str, detail: str, **extra: Any) -> JSONResponse:
    return JSONResponse({"ok": False, "code": code, "detail": detail, **extra}, status_code=status, headers=_headers())


def _store_id_from_read_write_token(token: str) -> str:
    pieces = token.split("_")
    if len(pieces) <= 3:
        return ""
    return pieces[3].strip().removeprefix("store_")


def _blob_auth_candidates() -> list[tuple[str, str, str]]:
    read_write = os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()
    oidc = os.environ.get("VERCEL_OIDC_TOKEN", "").strip()
    configured_store = os.environ.get("BLOB_STORE_ID", "").strip().removeprefix("store_")
    candidates: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(token: str, store_id: str, auth_kind: str) -> None:
        key = (token, store_id)
        if token and store_id and key not in seen:
            seen.add(key)
            candidates.append((token, store_id, auth_kind))

    add(oidc, configured_store, "oidc")
    add(read_write, configured_store, "read-write-configured-store")
    if read_write:
        add(read_write, _store_id_from_read_write_token(read_write), "read-write-token-store")
    return candidates


def _blob_auth() -> tuple[str, str, str]:
    candidates = _blob_auth_candidates()
    return candidates[0] if candidates else ("", "", "unconfigured")


def _blob_trace(operation: str, auth_kind: str, attempt: int, candidate_count: int, status: int, duration_ms: int) -> None:
    # Structured flight-recorder event. Never include credentials, user IDs,
    # authorization headers, object paths, or private Blob URLs here.
    store_source = "configured-store" if auth_kind in {"oidc", "read-write-configured-store"} else "token-derived-store"
    print(json.dumps({
        "camera": "chat-state-blob",
        "event": "BLOB_ATTEMPT_COMPLETE",
        "at": int(time.time() * 1000),
        "operation": operation,
        "attempt": attempt,
        "candidateCount": candidate_count,
        "authKind": auth_kind,
        "storeSource": store_source,
        "httpStatus": status,
        "durationMs": duration_ms,
        "credentialMaterialLogged": False,
    }, separators=(",", ":")), flush=True)


def _path(user_id: str) -> str:
    return f"{PREFIX}/{hashlib.sha256(user_id.encode('utf-8')).hexdigest()}.json"


def _private_blob_url(store_id: str, user_id: str) -> str:
    pathname = urllib.parse.quote(_path(user_id), safe="/-._~")
    return f"https://{store_id}.private.blob.vercel-storage.com/{pathname}?cache=0&t={int(time.time()*1000)}"


def _redis_key(user_id: str) -> str:
    return REDIS_PREFIX + hashlib.sha256(user_id.encode("utf-8")).hexdigest()


def _read_state(user_id: str) -> dict[str, Any] | None:
    """Prefer canonical Redis; migrate readable legacy Blob state when available."""
    try:
        raw = canonical_redis_store()._command("GET", _redis_key(user_id))
        if raw:
            value = json.loads(raw)
            if isinstance(value, dict) and value.get("contract") == CONTRACT and value.get("userId") == user_id:
                return value
    except Exception:
        pass
    try:
        legacy = _read_blob(user_id)
    except Exception:
        legacy = None
    if legacy:
        try:
            canonical_redis_store()._command("SET", _redis_key(user_id), json.dumps(legacy, ensure_ascii=False, separators=(",", ":")))
        except Exception:
            pass
    return legacy


def _write_state(user_id: str, value: dict[str, Any]) -> None:
    body = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if len(body.encode("utf-8")) > MAX_STATE_BYTES:
        raise RuntimeError("CHAT_STATE_TOO_LARGE")
    canonical_redis_store()._command("SET", _redis_key(user_id), body)


def _read_blob(user_id: str) -> dict[str, Any] | None:
    candidates = _blob_auth_candidates()
    if not candidates:
        raise RuntimeError("CHAT_STATE_BLOB_NOT_CONFIGURED")
    last_status = 0
    for index, (token, store_id, auth_kind) in enumerate(candidates):
        started = time.monotonic()
        response = requests.get(_private_blob_url(store_id, user_id), headers={"authorization": f"Bearer {token}"}, timeout=(3, 10))
        _blob_trace("READ", auth_kind, index + 1, len(candidates), response.status_code, int((time.monotonic() - started) * 1000))
        if response.status_code == 404:
            return None
        if response.status_code in {401, 403} and index + 1 < len(candidates):
            last_status = response.status_code
            continue
        if not response.ok:
            raise RuntimeError(f"CHAT_STATE_BLOB_READ_HTTP_{response.status_code}")
        if len(response.content) > MAX_STATE_BYTES:
            raise RuntimeError("CHAT_STATE_TOO_LARGE")
        value = response.json()
        if not isinstance(value, dict) or value.get("contract") != CONTRACT or value.get("userId") != user_id:
            raise RuntimeError("CHAT_STATE_INVALID")
        return value
    raise RuntimeError(f"CHAT_STATE_BLOB_READ_HTTP_{last_status or 403}")


def _blob_write_headers(token: str, store_id: str) -> dict[str, str]:
    return {
        "authorization": f"Bearer {token}",
        "x-vercel-blob-store-id": store_id,
        "x-api-version": "12",
        "x-api-blob-request-attempt": "0",
        "x-api-blob-request-id": f"{store_id}:{int(time.time()*1000)}:{uuid.uuid4().hex[:12]}",
        "content-type": "application/json; charset=utf-8",
        "x-content-type": "application/json; charset=utf-8",
        "x-vercel-blob-access": "private",
        "x-add-random-suffix": "0",
        "x-allow-overwrite": "1",
        "x-cache-control-max-age": "0",
    }


def _write_blob(user_id: str, value: dict[str, Any]) -> None:
    candidates = _blob_auth_candidates()
    if not candidates:
        raise RuntimeError("CHAT_STATE_BLOB_NOT_CONFIGURED")
    body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(body) > MAX_STATE_BYTES:
        raise RuntimeError("CHAT_STATE_TOO_LARGE")
    last_status = 0
    for index, (token, store_id, auth_kind) in enumerate(candidates):
        started = time.monotonic()
        response = requests.put(BLOB_API + "/", params={"pathname": _path(user_id)}, headers=_blob_write_headers(token, store_id), data=body, timeout=(3, 12))
        _blob_trace("WRITE", auth_kind, index + 1, len(candidates), response.status_code, int((time.monotonic() - started) * 1000))
        if response.status_code in {401, 403} and index + 1 < len(candidates):
            last_status = response.status_code
            continue
        if response.ok:
            return
        raise RuntimeError(f"CHAT_STATE_BLOB_WRITE_HTTP_{response.status_code}")
    raise RuntimeError(f"CHAT_STATE_BLOB_WRITE_HTTP_{last_status or 403}")


def _clean_state(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("state must be an object")
    threads_in = raw.get("threads")
    if not isinstance(threads_in, list):
        raise ValueError("state.threads must be an array")
    threads: list[dict[str, Any]] = []
    seen_threads: set[str] = set()
    for item in threads_in[:MAX_THREADS]:
        if not isinstance(item, dict):
            continue
        thread_id = str(item.get("id") or "").strip()[:160]
        if not thread_id or thread_id in seen_threads:
            continue
        seen_threads.add(thread_id)
        messages: list[dict[str, Any]] = []
        seen_messages: set[str] = set()
        source_messages = item.get("messages") if isinstance(item.get("messages"), list) else []
        for msg in source_messages[-MAX_MESSAGES_PER_THREAD:]:
            if not isinstance(msg, dict):
                continue
            message_id = str(msg.get("id") or "").strip()[:160]
            role = str(msg.get("role") or "").lower()
            if not message_id or message_id in seen_messages or role not in {"user", "assistant"}:
                continue
            seen_messages.add(message_id)
            messages.append({"id": message_id, "role": role, "text": str(msg.get("text") or "")[:200000], "createdAt": int(msg.get("createdAt") or 0), "state": str(msg.get("state") or "complete")[:32], "pinned": bool(msg.get("pinned")), "meta": msg.get("meta") if isinstance(msg.get("meta"), dict) else {}})
        raw_pins = item.get("messagePins") if isinstance(item.get("messagePins"), dict) else {}
        message_pins: dict[str, bool] = {}
        for raw_id, raw_value in list(raw_pins.items())[-MAX_MESSAGE_PINS_PER_THREAD:]:
            pin_id = str(raw_id or "").strip()[:160]
            if pin_id and bool(raw_value):
                message_pins[pin_id] = True
        threads.append({"id": thread_id, "title": str(item.get("title") or "New conversation").strip()[:120] or "New conversation", "createdAt": int(item.get("createdAt") or 0), "updatedAt": int(item.get("updatedAt") or 0), "pinned": bool(item.get("pinned")), "messagePins": message_pins, "messages": messages})
    current_id = str(raw.get("currentId") or "").strip()[:160]
    if current_id not in seen_threads:
        current_id = threads[0]["id"] if threads else ""
    return {"version": 1, "currentId": current_id, "threads": threads}


def _clean_tombstones(raw: Any) -> list[dict[str, Any]]:
    values = raw if isinstance(raw, list) else []
    latest: dict[str, int] = {}
    for item in values[-MAX_TOMBSTONES * 2 :]:
        if not isinstance(item, dict):
            continue
        thread_id = str(item.get("threadId") or "").strip()[:160]
        if not thread_id:
            continue
        deleted_at = int(item.get("deletedAt") or 0)
        latest[thread_id] = max(deleted_at, latest.get(thread_id, 0))
    ordered = sorted(latest.items(), key=lambda pair: pair[1], reverse=True)[:MAX_TOMBSTONES]
    return [{"threadId": thread_id, "deletedAt": deleted_at} for thread_id, deleted_at in ordered]


def _apply_tombstones(state: dict[str, Any], tombstones: list[dict[str, Any]]) -> dict[str, Any]:
    deleted = {str(item.get("threadId") or "") for item in tombstones}
    if not deleted:
        return state
    threads = [thread for thread in state.get("threads", []) if thread.get("id") not in deleted]
    ids = {thread.get("id") for thread in threads}
    current_id = state.get("currentId") if state.get("currentId") in ids else (threads[0]["id"] if threads else "")
    return {"version": 1, "currentId": current_id, "threads": threads}


def _blank_state() -> dict[str, Any]:
    return {"version": 1, "currentId": "", "threads": []}


def _state_value(current: dict[str, Any] | None) -> tuple[int, dict[str, Any], list[dict[str, Any]]]:
    if not current:
        return 0, _blank_state(), []
    revision = int(current.get("revision") or 0)
    state = _clean_state(current.get("state") if isinstance(current.get("state"), dict) else _blank_state())
    tombstones = _clean_tombstones(current.get("tombstones"))
    return revision, _apply_tombstones(state, tombstones), tombstones


def _user(request: Request) -> str:
    return user_id_from_request(request)


def _mutation_response(*, revision: int, state: dict[str, Any] | None, updated_at: int = 0, conflict: bool = False) -> JSONResponse:
    payload: dict[str, Any] = {"ok": not conflict, "contract": CONTRACT, "mutationContract": MUTATION_CONTRACT, "revision": revision, "snapshotWriteAuthority": "retired", "stateAuthority": "server"}
    if updated_at:
        payload["updatedAt"] = updated_at
    if state is not None:
        payload["state"] = state
    if conflict:
        payload["code"] = "CHAT_STATE_CONFLICT"
    return JSONResponse(payload, status_code=409 if conflict else 200, headers=_headers())


def _thread_by_id(state: dict[str, Any], thread_id: str) -> dict[str, Any] | None:
    return next((thread for thread in state.get("threads", []) if thread.get("id") == thread_id), None)


def _mutation_id(value: Any) -> str:
    return str(value or "").strip()[:160]


def _apply_mutation(state: dict[str, Any], tombstones: list[dict[str, Any]], operation: dict[str, Any], stamp: int) -> tuple[bool, dict[str, Any], list[dict[str, Any]]]:
    op = str(operation.get("type") or "").strip().upper()
    thread_id = _mutation_id(operation.get("threadId"))
    if not op:
        raise ValueError("mutation.type is required")
    tombstone_ids = {str(item.get("threadId") or "") for item in tombstones}
    changed = False
    if op == "UPSERT_THREAD":
        if not thread_id:
            raise ValueError("threadId is required")
        if thread_id in tombstone_ids:
            raise ValueError("CHAT_STATE_THREAD_TOMBSTONED")
        thread = _thread_by_id(state, thread_id)
        title = str(operation.get("title") or "New conversation").strip()[:120] or "New conversation"
        pinned = bool(operation.get("pinned"))
        created_at = int(operation.get("createdAt") or stamp)
        if thread is None:
            thread = {"id": thread_id, "title": title, "createdAt": created_at, "updatedAt": stamp, "pinned": pinned, "messagePins": {}, "messages": []}
            state.setdefault("threads", []).insert(0, thread)
            changed = True
        else:
            if thread.get("title") != title:
                thread["title"] = title; changed = True
            if bool(thread.get("pinned")) != pinned:
                thread["pinned"] = pinned; changed = True
            if changed:
                thread["updatedAt"] = stamp
    elif op == "DELETE_THREAD":
        if not thread_id:
            raise ValueError("threadId is required")
        before = len(state.get("threads", []))
        state["threads"] = [thread for thread in state.get("threads", []) if thread.get("id") != thread_id]
        if len(state["threads"]) != before or thread_id not in tombstone_ids:
            tombstones = _clean_tombstones([*tombstones, {"threadId": thread_id, "deletedAt": stamp}]); changed = True
        if state.get("currentId") == thread_id:
            state["currentId"] = state["threads"][0]["id"] if state["threads"] else ""
    elif op == "SET_CURRENT_THREAD":
        if not thread_id:
            new_value = ""
        else:
            if _thread_by_id(state, thread_id) is None:
                raise ValueError("CHAT_STATE_THREAD_NOT_FOUND")
            new_value = thread_id
        if state.get("currentId") != new_value:
            state["currentId"] = new_value; changed = True
    elif op == "SET_MESSAGE_PINNED":
        if not thread_id:
            raise ValueError("threadId is required")
        message_id = _mutation_id(operation.get("messageId"))
        if not message_id:
            raise ValueError("messageId is required")
        thread = _thread_by_id(state, thread_id)
        if thread is None:
            raise ValueError("CHAT_STATE_THREAD_NOT_FOUND")
        pins = thread.get("messagePins") if isinstance(thread.get("messagePins"), dict) else {}
        pins = dict(pins)
        pinned = bool(operation.get("pinned"))
        was_pinned = bool(pins.get(message_id))
        if pinned and not was_pinned:
            if len(pins) >= MAX_MESSAGE_PINS_PER_THREAD:
                raise ValueError("CHAT_STATE_MESSAGE_PIN_LIMIT")
            pins[message_id] = True; thread["messagePins"] = pins; thread["updatedAt"] = stamp; changed = True
        elif not pinned and was_pinned:
            pins.pop(message_id, None); thread["messagePins"] = pins; thread["updatedAt"] = stamp; changed = True
    else:
        raise ValueError("CHAT_STATE_MUTATION_UNSUPPORTED")
    state = _apply_tombstones(_clean_state(state), tombstones)
    return changed, state, tombstones


def set_message_pinned_for_user(*, user_id: str, thread_id: str, message_id: str, pinned: bool) -> bool:
    """Server-owned pin mutation used by trusted turn lifecycle code."""
    current = _read_state(user_id)
    revision, state, tombstones = _state_value(current)
    stamp = int(time.time() * 1000)
    if _thread_by_id(state, thread_id) is None:
        state.setdefault("threads", []).insert(0, {
            "id": thread_id,
            "title": "New conversation",
            "createdAt": stamp,
            "updatedAt": stamp,
            "pinned": False,
            "messagePins": {},
            "messages": [],
        })
    changed, state, tombstones = _apply_mutation(state, tombstones, {
        "type": "SET_MESSAGE_PINNED",
        "threadId": thread_id,
        "messageId": message_id,
        "pinned": bool(pinned),
    }, stamp)
    if not changed:
        return False
    _write_state(user_id, {
        "contract": CONTRACT,
        "mutationContract": MUTATION_CONTRACT,
        "userId": user_id,
        "revision": revision + 1,
        "updatedAt": stamp,
        "state": state,
        "tombstones": tombstones,
    })
    return True


@app.get("/api/chat_state", include_in_schema=False)
async def get_state(request: Request):
    try:
        user_id = _user(request)
        value = _read_state(user_id)
        token, store_id, auth_kind = _blob_auth()
        revision, state, _ = _state_value(value)
        return JSONResponse({"ok": True, "contract": CONTRACT, "mutationContract": MUTATION_CONTRACT, "revision": revision, "updatedAt": int(value.get("updatedAt") or 0) if value else 0, "state": state if value else None, "stateAuthority": "server", "snapshotWriteAuthority": "retired", "storage": {"configured": bool(token and store_id), "access": "private", "authKind": auth_kind}}, headers=_headers())
    except AuthenticationError as exc:
        return _error(401, "ACCOUNT_SESSION_INVALID", str(exc))
    except Exception as exc:
        return _error(503, "CHAT_STATE_READ_FAILED", f"{type(exc).__name__}: {exc}")


@app.post("/api/chat_state", include_in_schema=False)
async def mutate_state(request: Request):
    try:
        user_id = _user(request)
        body = await request.body()
        if len(body) > 128 * 1024:
            return _error(413, "CHAT_STATE_MUTATION_TOO_LARGE", "Chat state mutation exceeds the safety bound.")
        payload = json.loads(body or b"{}")
        if not isinstance(payload, dict) or payload.get("contract") != MUTATION_CONTRACT:
            return _error(400, "CHAT_STATE_MUTATION_INVALID", f"contract must be {MUTATION_CONTRACT}")
        raw_operations = payload.get("operations")
        if not isinstance(raw_operations, list) or not raw_operations or len(raw_operations) > MAX_MUTATIONS:
            return _error(400, "CHAT_STATE_MUTATION_INVALID", f"operations must contain 1..{MAX_MUTATIONS} items")
        if not all(isinstance(item, dict) for item in raw_operations):
            return _error(400, "CHAT_STATE_MUTATION_INVALID", "Every operation must be an object.")
        expected_revision = int(payload.get("expectedRevision") or 0)
        current = _read_state(user_id)
        revision, state, tombstones = _state_value(current)
        if expected_revision != revision:
            return _mutation_response(revision=revision, state=state, updated_at=int(current.get("updatedAt") or 0) if current else 0, conflict=True)
        stamp = int(time.time() * 1000)
        changed = False
        for operation in raw_operations:
            item_changed, state, tombstones = _apply_mutation(state, tombstones, operation, stamp)
            changed = changed or item_changed
        if not changed:
            return _mutation_response(revision=revision, state=state, updated_at=int(current.get("updatedAt") or 0) if current else stamp)
        next_revision = revision + 1
        record = {"contract": CONTRACT, "mutationContract": MUTATION_CONTRACT, "userId": user_id, "revision": next_revision, "updatedAt": stamp, "state": state, "tombstones": tombstones}
        _write_state(user_id, record)
        return _mutation_response(revision=next_revision, state=state, updated_at=stamp)
    except AuthenticationError as exc:
        return _error(401, "ACCOUNT_SESSION_INVALID", str(exc))
    except (ValueError, json.JSONDecodeError) as exc:
        return _error(400, "CHAT_STATE_MUTATION_INVALID", str(exc))
    except Exception as exc:
        return _error(503, "CHAT_STATE_MUTATION_FAILED", f"{type(exc).__name__}: {exc}")


# FILE: api/lalm_station.py
"""Unified server-owned Chat/LALM station synchronization boundary.

The station gives a Chat client one coherent account snapshot: thread list, current
thread, current messages, and active generation state/status.  The browser is a
renderer/subscriber; it is never conversation or generation authority.
"""
from __future__ import annotations

import time
import hashlib
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse
from vercel.queue import send as queue_send

from api.google_account import AuthenticationError, user_id_from_request
from api.chat_state import _read_state, _state_value, _headers
from api.chat_transcript_store import STORE
from api.canonical_redis_state import store as canonical_redis_store, _canonical_messages_compatible
import api.chat as chat
from api import chat_turn_state

CONTRACT = "swrlz-lalm-station-sync-v1"
MAX_ACTIVE = 8


def _status_list(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    raw = snapshot.get("status")
    if isinstance(raw, list):
        return [dict(item) for item in raw[-256:] if isinstance(item, dict)]
    phase = str(snapshot.get("phase") or "").strip()
    if not phase:
        return []
    return [{
        "seq": int(snapshot.get("lastSeq") or 0),
        "phase": phase,
        "at": float(snapshot.get("updatedAt") or 0),
    }]


def _generation_view(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "requestId": str(snapshot.get("requestId") or ""),
        "ownerId": str(snapshot.get("ownerId") or ""),
        "phase": str(snapshot.get("phase") or ""),
        "terminal": bool(snapshot.get("terminal")),
        "terminalType": str(snapshot.get("terminalType") or ""),
        "text": str(snapshot.get("text") or snapshot.get("transcript") or ""),
        "textRevision": int(snapshot.get("textRevision") or 0),
        "lastSeq": int(snapshot.get("lastSeq") or 0),
        "lastDeltaSeq": int(snapshot.get("lastDeltaSeq") or 0),
        "status": _status_list(snapshot),
        "createdAt": float(snapshot.get("createdAt") or 0),
        "updatedAt": float(snapshot.get("updatedAt") or 0),
        "storage": dict(snapshot.get("storage") or {}),
    }



def _pinned_context(*, user_id: str, thread_id: str, limit: int = 24) -> list[dict[str, Any]]:
    """Project authoritative pinned messages for Brain context without trusting browser text."""
    value = _read_state(user_id)
    _revision, state, _tombstones = _state_value(value)
    meta = next((item for item in state.get("threads", []) if str(item.get("id") or "") == thread_id), None)
    pins = meta.get("messagePins") if isinstance(meta, dict) and isinstance(meta.get("messagePins"), dict) else {}
    wanted = {str(message_id) for message_id, enabled in pins.items() if enabled}
    if not wanted:
        return []
    redis = canonical_redis_store()
    durable, _legacy_count = _canonical_messages_compatible(redis, user_id=user_id, thread_id=thread_id, limit=1000)
    result: list[dict[str, Any]] = []
    for message in durable:
        message_id = str(message.message_id or "")
        role = str(message.role or "").upper()
        text = str(message.committed_text or "")
        if message_id in wanted and role in {"USER", "ASSISTANT"} and text:
            result.append({"messageId": message_id, "role": role, "text": text[:12000], "pinned": True})
    return result[-max(1, min(int(limit), 24)):]


def install(server, chat_extensions) -> None:
    app = server.app

    @app.post("/api/lalm_station/generate", include_in_schema=False)
    async def station_generate(request: Request):
        """Admit one authenticated Chat turn and delegate generation to the installed R39 owner."""
        try:
            user_id = user_id_from_request(request)
            payload = await chat._read_json(request)
            # Account authentication is the Station boundary; canonical turn/state
            # wrappers installed on chat._normalize_chat_request remain authoritative.
            payload["ingress"] = "SWRLZ_LALM_STATION"
            normalized = chat._normalize_chat_request(payload)
            response = chat._stream_response(normalized)
            response.headers["X-SWRLZ-LALM-Station"] = CONTRACT
            response.headers["X-SWRLZ-LALM-Station-Account"] = hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:24]
            return response
        except AuthenticationError as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except chat.BridgeError as exc:
            return chat._json_error(exc.status, exc.code, exc.detail)
        except Exception as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_GENERATE_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())

    @app.post("/api/lalm_station/send", include_in_schema=False)
    async def station_send(request: Request):
        """Persist one authenticated turn, enqueue generation, and return immediately.

        The browser is only an ingress/subscriber. Once the canonical turn is
        accepted, the Workstation queue owns generation lifetime.
        """
        request_id = str(request.headers.get("X-SWRLZ-Request-Id") or "").strip()
        print("SWRLZ_STATION_TRANSPORT "+__import__("json").dumps({
            "stage":"send-enter","requestId":request_id,"path":str(request.url.path),
            "method":request.method,"atUnixMs":int(time.time()*1000)
        },separators=(",",":")),flush=True)
        try:
            user_id = user_id_from_request(request)
            print("SWRLZ_STATION_TRANSPORT "+__import__("json").dumps({
                "stage":"auth-ok","requestId":request_id,"atUnixMs":int(time.time()*1000)
            },separators=(",",":")),flush=True)
            payload = await request.json()
            if not isinstance(payload, dict):
                return JSONResponse({"ok": False, "contract": CONTRACT, "code": "INVALID_REQUEST"}, status_code=400, headers=_headers())
            payload["ingress"] = "SWRLZ_LALM_STATION"
            turn = chat_turn_state.begin_turn(request, payload)
            history, _history_revision = chat_turn_state.canonical_history(
                request, thread_id=turn.thread_id, request_id=turn.request_id, limit=32
            )
            work = {
                "contract": "swrlz-lalm-workstation-job-v1",
                "requestId": turn.request_id,
                "userId": turn.user_id,
                "accountScope": turn.account_scope,
                "threadId": turn.thread_id,
                "userMessageId": turn.user_message_id,
                "assistantMessageId": turn.assistant_message_id,
                "prompt": str(payload.get("prompt") or ""),
                "history": history,
                "pinnedContext": _pinned_context(user_id=user_id, thread_id=turn.thread_id),
                "payload": {
                    **{
                        key: value for key, value in payload.items()
                        if key not in {"history", "pinnedContext", "session", "cookie", "authorization"}
                    },
                    "pinnedContext": _pinned_context(user_id=user_id, thread_id=turn.thread_id),
                },
                "acceptedAt": time.time(),
            }
            message_id = await queue_send(
                "swrlz-generation",
                work,
                idempotency_key=turn.request_id,
            )
            print("SWRLZ_WORKSTATION_QUEUE "+__import__("json").dumps({
                "contract":"swrlz-lalm-workstation-job-v1","stage":"enqueued",
                "requestId":turn.request_id,"threadId":turn.thread_id,
                "queueMessageId":str(message_id),"atUnixMs":int(time.time()*1000)
            },separators=(",",":")),flush=True)
            return JSONResponse({
                "ok": True,
                "contract": CONTRACT,
                "accepted": True,
                "requestId": turn.request_id,
                "threadId": turn.thread_id,
                "userMessageId": turn.user_message_id,
                "assistantMessageId": turn.assistant_message_id,
                "generationOwner": "workstation-queue",
                "synchronize": {
                    "endpoint": "/api/lalm_station/sync",
                    "strategy": "snapshot-follow",
                },
            }, status_code=202, headers=_headers())
        except AuthenticationError as exc:
            print("SWRLZ_STATION_TRANSPORT "+__import__("json").dumps({"stage":"auth-failed","requestId":request_id,"error":str(exc),"atUnixMs":int(time.time()*1000)},separators=(",",":")),flush=True)
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except Exception as exc:
            print("SWRLZ_STATION_TRANSPORT "+__import__("json").dumps({"stage":"send-failed","requestId":request_id,"errorType":type(exc).__name__,"error":str(exc),"atUnixMs":int(time.time()*1000)},separators=(",",":")),flush=True)
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_SEND_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())

    @app.get("/api/lalm_station/sync", include_in_schema=False)
    async def station_sync(request: Request):
        try:
            user_id = user_id_from_request(request)
            account_scope = hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:24]
            value = _read_state(user_id)
            revision, state, _ = _state_value(value)
            state = state or {"version": 1, "currentId": "", "threads": []}
            # Canonical Redis is the conversation authority. chat_state is metadata
            # only (current selection, title/pin overrides, tombstones). The Station
            # projects durable threads/messages into one account snapshot for the Mask.
            metadata_threads = {str(t.get("id") or ""): t for t in state.get("threads", []) if isinstance(t, dict)}
            tombstones = {str(t.get("threadId") or "") for t in (value or {}).get("tombstones", []) if isinstance(t, dict)}
            redis = canonical_redis_store()
            # A serverless worker can disappear while full R39 inference is in flight.
            # Reap durable jobs that outlive the bounded active-generation window so
            # no assistant placeholder can remain STREAMING forever.
            try:
                from api import canonical_redis_state
                canonical_redis_state.expire_stale_active_turns(user_id=user_id, max_age_seconds=120.0)
            except Exception as exc:
                print(f"SWRLZ_STATION_STALE_REAPER_FAILED {type(exc).__name__}: {exc}", flush=True)
            threads: list[dict[str, Any]] = []
            for record in redis.list_threads(user_id, limit=80):
                thread_id = str(record.thread_id)
                if not thread_id or thread_id in tombstones:
                    continue
                meta = metadata_threads.get(thread_id, {})
                durable_messages, _legacy_count = _canonical_messages_compatible(redis, user_id=user_id, thread_id=thread_id, limit=1000)
                rendered_messages: list[dict[str, Any]] = []
                for message in durable_messages:
                    role = str(message.role or "").upper()
                    if role not in {"USER", "ASSISTANT"}:
                        continue
                    text = str(message.committed_text or "")
                    # Streaming assistant placeholders are generation state, not
                    # committed conversation messages.
                    if role == "ASSISTANT" and (not text or str(message.state or "").upper() == "STREAMING"):
                        continue
                    provenance = message.provenance if isinstance(message.provenance, dict) else {}
                    safe_provenance = {
                        "sourceAuthority": str(provenance.get("authority") or "")[:64],
                        "turnContract": str(provenance.get("turnContract") or "")[:96],
                        "commitPhase": str(provenance.get("commitPhase") or "")[:64],
                        "terminalType": str(provenance.get("terminalType") or "")[:32],
                    }
                    safe_provenance = {key: value for key, value in safe_provenance.items() if value}
                    rendered_messages.append({
                        "id": str(message.message_id),
                        "role": role.lower(),
                        "text": text,
                        "createdAt": int(float(message.created_at or 0) * 1000),
                        "state": str(message.state or "").lower(),
                        "pinned": bool((meta.get("messagePins") if isinstance(meta.get("messagePins"), dict) else {}).get(str(message.message_id), False)),
                        "meta": {
                            "requestId": str(message.request_id or ""),
                            "authority": "workstation",
                            "provenance": safe_provenance,
                        },
                    })
                threads.append({
                    "id": thread_id,
                    "title": str((record.title if str(meta.get("title") or "").strip() in {"", "New conversation"} else meta.get("title")) or "New conversation"),
                    "createdAt": int(float(record.created_at or 0) * 1000),
                    "updatedAt": int(float(record.updated_at or 0) * 1000),
                    "pinned": bool(meta.get("pinned", False)),
                    "messagePins": dict(meta.get("messagePins") or {}) if isinstance(meta.get("messagePins"), dict) else {},
                    "messages": rendered_messages,
                })

            # If the first canonical turn created a durable thread before metadata
            # knew about it, promote that thread into account metadata here. This keeps
            # the Workstation authoritative while making the new thread immediately
            # eligible for drawer population and later metadata actions.
            durable_ids = {str(t.get("id") or "") for t in threads}
            metadata_ids = set(metadata_threads)
            missing_metadata = durable_ids - metadata_ids
            if missing_metadata:
                from api.chat_state import _write_state
                stamp = int(time.time() * 1000)
                state_threads = list(state.get("threads") or [])
                by_id = {str(t.get("id") or ""): t for t in threads}
                for thread_id in missing_metadata:
                    projected = by_id[thread_id]
                    state_threads.insert(0, {
                        "id": thread_id,
                        "title": str(projected.get("title") or "New conversation"),
                        "createdAt": int(projected.get("createdAt") or stamp),
                        "updatedAt": stamp,
                        "pinned": False,
                        "messagePins": {},
                        "messages": [],
                    })
                revision += 1
                state = {"version": 1, "currentId": next(iter(missing_metadata)), "threads": state_threads}
                _write_state(user_id, {
                    "contract": "swrlz-chat-account-state-v1",
                    "mutationContract": "swrlz-chat-account-mutation-v1",
                    "userId": user_id,
                    "revision": revision,
                    "updatedAt": stamp,
                    "state": state,
                    "tombstones": list((value or {}).get("tombstones") or []),
                })

            current_id = str(state.get("currentId") or "")
            if current_id not in {str(t.get("id") or "") for t in threads}:
                current_id = str(threads[0].get("id") or "") if threads else ""
            current = next((t for t in threads if str(t.get("id") or "") == current_id), None)
            messages = list(current.get("messages") or []) if isinstance(current, dict) else []

            active: list[dict[str, Any]] = []
            sessions = getattr(chat_extensions, "RESUMABLE_GENERATIONS", {})
            lock = getattr(chat_extensions, "RESUMABLE_GENERATION_LOCK", None)
            if lock is not None:
                with lock:
                    local = list(sessions.values())
            else:
                local = list(sessions.values())
            for session in sorted(local, key=lambda s: float(s.get("updatedAt") or 0), reverse=True):
                if bool(session.get("terminal")):
                    continue
                identity = session.get("identity") if isinstance(session.get("identity"), dict) else {}
                # Only expose a session when its durable turn identity belongs to this
                # account/thread.  Legacy sessions lacking identity stay hidden rather
                # than crossing account boundaries.
                session_thread = str(identity.get("threadId") or session.get("threadId") or "")
                session_scope = str(identity.get("accountScope") or session.get("accountScope") or "")
                if not session_scope or session_scope != account_scope:
                    continue
                view = _generation_view(session)
                view["threadId"] = session_thread
                active.append(view)
                if len(active) >= MAX_ACTIVE:
                    break

            primary = active[0] if active else None
            return JSONResponse({
                "ok": True,
                "contract": CONTRACT,
                "serverTime": time.time(),
                "revision": revision,
                "updatedAt": int(value.get("updatedAt") or 0) if value else 0,
                "stateAuthority": "server",
                "threads": threads,
                "currentThread": current,
                "messages": messages,
                "activeGeneration": primary,
                "activeGenerations": active,
                "synchronize": {
                    "required": bool(primary),
                    "requestId": str(primary.get("requestId") or "") if primary else "",
                    "afterSeq": int(primary.get("lastSeq") or 0) if primary else 0,
                    "transcriptEndpoint": "/api/chat/transcript",
                    "streamEndpoint": "/api/chat",
                    "strategy": "resume-existing-never-restart",
                },
            }, headers=_headers())
        except AuthenticationError as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)}, status_code=401, headers=_headers())
        except Exception as exc:
            return JSONResponse({"ok": False, "contract": CONTRACT, "code": "LALM_STATION_SYNC_FAILED", "detail": f"{type(exc).__name__}: {exc}"}, status_code=503, headers=_headers())


# FILE: api/chat_turn_state.py
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
    set_message_pinned_for_user,
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


def _should_auto_pin_code(text: str, terminal: str) -> bool:
    if terminal != "COMPLETED":
        return False
    source = str(text or "")
    start = source.find("```")
    if start < 0:
        return False
    end = source.find("```", start + 3)
    return end >= 0 and len(source[start + 3:end].strip()) >= 24


def _auto_pin_completed_code(turn: CanonicalTurn, text: str, terminal: str) -> None:
    if not _should_auto_pin_code(text, terminal):
        return
    try:
        set_message_pinned_for_user(
            user_id=turn.user_id,
            thread_id=turn.thread_id,
            message_id=turn.assistant_message_id,
            pinned=True,
        )
        _chat_lockdown("turn-code-auto-pin", request_id=turn.request_id, threadId=turn.thread_id, assistantMessageId=turn.assistant_message_id, pinned=True)
    except Exception as exc:
        _chat_lockdown("turn-code-auto-pin-failed", request_id=turn.request_id, threadId=turn.thread_id, assistantMessageId=turn.assistant_message_id, errorType=type(exc).__name__)


def finish_turn(turn: CanonicalTurn, *, text: str, terminal_type: str, reason: str = "") -> int:
    terminal = _bounded(terminal_type, 32).upper() or "FAILED"
    _chat_lockdown("turn-finish-enter", request_id=turn.request_id, threadId=turn.thread_id, assistantMessageId=turn.assistant_message_id, backend=turn.storage_backend, terminalType=terminal, reason=reason, textChars=len(str(text or "")), text=str(text or "")[:16000])
    if turn.storage_backend == "redis":
        canonical_redis_state.finish_canonical_turn(
            user_id=turn.user_id, request_id=turn.request_id, assistant_message_id=turn.assistant_message_id,
            text=str(text or "")[:200000], terminal_type=terminal, reason=_bounded(reason, 2000), turn_contract=TURN_CONTRACT,
        )
        _auto_pin_completed_code(turn, str(text or ""), terminal)
        _chat_lockdown("turn-finish-exit", request_id=turn.request_id, threadId=turn.thread_id, backend="redis", revision=0, terminalType=terminal)
        return 0
    state_name = {"COMPLETED": "complete", "CANCELLED": "cancelled", "FAILED": "failed"}.get(terminal, "failed")
    revision = _commit_blob_message(turn.user_id, thread_id=turn.thread_id, message_id=turn.assistant_message_id, role="assistant", text=str(text or "")[:200000], created_at=turn.assistant_created_at, state_name=state_name, request_id=turn.request_id, extra_meta={"commitPhase": "TERMINAL", "terminalType": terminal, "terminalReason": _bounded(reason, 2000)})
    _auto_pin_completed_code(turn, str(text or ""), terminal)
    _chat_lockdown("turn-finish-exit", request_id=turn.request_id, threadId=turn.thread_id, backend="blob", revision=revision, terminalType=terminal)
    return revision