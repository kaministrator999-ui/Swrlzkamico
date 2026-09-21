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

APP_VERSION = "1.1.4"
CONTRACT = "swrlz-chat-account-state-v1"
MUTATION_CONTRACT = "swrlz-chat-account-mutation-v1"
BLOB_API = "https://vercel.com/api/blob"
PREFIX = "swrlz/chat/account-state/v1"
MAX_STATE_BYTES = 2 * 1024 * 1024
MAX_THREADS = 80
MAX_MESSAGES_PER_THREAD = 1000
MAX_MUTATIONS = 32
MAX_TOMBSTONES = 320
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
        threads.append({"id": thread_id, "title": str(item.get("title") or "New conversation").strip()[:120] or "New conversation", "createdAt": int(item.get("createdAt") or 0), "updatedAt": int(item.get("updatedAt") or 0), "pinned": bool(item.get("pinned")), "messages": messages})
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
            thread = {"id": thread_id, "title": title, "createdAt": created_at, "updatedAt": stamp, "pinned": pinned, "messages": []}
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
        message = next((item for item in thread.get("messages", []) if item.get("id") == message_id), None)
        if message is None:
            raise ValueError("CHAT_STATE_MESSAGE_NOT_FOUND")
        pinned = bool(operation.get("pinned"))
        if bool(message.get("pinned")) != pinned:
            message["pinned"] = pinned; thread["updatedAt"] = stamp; changed = True
    else:
        raise ValueError("CHAT_STATE_MUTATION_UNSUPPORTED")
    state = _apply_tombstones(_clean_state(state), tombstones)
    return changed, state, tombstones


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
