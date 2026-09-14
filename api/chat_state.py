"""Durable account-scoped Chat thread/message state.

This is deliberately separate from generation transcript checkpoints.  The browser is a
cache/presentation surface; the authenticated server account owns the durable state.
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

APP_VERSION = "1.0.0"
CONTRACT = "swrlz-chat-account-state-v1"
BLOB_API = "https://vercel.com/api/blob"
PREFIX = "swrlz/chat/account-state/v1"
MAX_STATE_BYTES = 2 * 1024 * 1024
MAX_THREADS = 80
MAX_MESSAGES_PER_THREAD = 1000

app = FastAPI(title="SWRLZ Chat State", version=APP_VERSION, docs_url=None, redoc_url=None, openapi_url=None)


def _headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store, no-transform",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
    }


def _error(status: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse({"ok": False, "code": code, "detail": detail}, status_code=status, headers=_headers())


def _blob_auth() -> tuple[str, str, str]:
    read_write = os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()
    oidc = os.environ.get("VERCEL_OIDC_TOKEN", "").strip()
    configured_store = os.environ.get("BLOB_STORE_ID", "").strip().removeprefix("store_")
    if read_write:
        pieces = read_write.split("_")
        store_id = (pieces[3] if len(pieces) > 3 else "").removeprefix("store_")
        return read_write, store_id, "read-write"
    if oidc and configured_store:
        return oidc, configured_store, "oidc"
    return "", "", "unconfigured"


def _path(user_id: str) -> str:
    digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
    return f"{PREFIX}/{digest}.json"


def _read_blob(user_id: str) -> dict[str, Any] | None:
    token, store_id, _ = _blob_auth()
    if not token or not store_id:
        raise RuntimeError("CHAT_STATE_BLOB_NOT_CONFIGURED")
    pathname = urllib.parse.quote(_path(user_id), safe="/-._~")
    url = f"https://{store_id}.private.blob.vercel-storage.com/{pathname}?cache=0&t={int(time.time()*1000)}"
    response = requests.get(url, headers={"authorization": f"Bearer {token}"}, timeout=(3, 10))
    if response.status_code == 404:
        return None
    response.raise_for_status()
    if len(response.content) > MAX_STATE_BYTES:
        raise RuntimeError("CHAT_STATE_TOO_LARGE")
    value = response.json()
    if not isinstance(value, dict) or value.get("contract") != CONTRACT or value.get("userId") != user_id:
        raise RuntimeError("CHAT_STATE_INVALID")
    return value


def _write_blob(user_id: str, value: dict[str, Any]) -> None:
    token, store_id, _ = _blob_auth()
    if not token or not store_id:
        raise RuntimeError("CHAT_STATE_BLOB_NOT_CONFIGURED")
    body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(body) > MAX_STATE_BYTES:
        raise RuntimeError("CHAT_STATE_TOO_LARGE")
    headers = {
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
    response = requests.put(BLOB_API + "/", params={"pathname": _path(user_id)}, headers=headers, data=body, timeout=(3, 12))
    if not response.ok:
        raise RuntimeError(f"CHAT_STATE_BLOB_WRITE_HTTP_{response.status_code}")


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
            messages.append({
                "id": message_id,
                "role": role,
                "text": str(msg.get("text") or "")[:200000],
                "createdAt": int(msg.get("createdAt") or 0),
                "state": str(msg.get("state") or "complete")[:32],
                "pinned": bool(msg.get("pinned")),
                "meta": msg.get("meta") if isinstance(msg.get("meta"), dict) else {},
            })
        threads.append({
            "id": thread_id,
            "title": str(item.get("title") or "New conversation").strip()[:120] or "New conversation",
            "createdAt": int(item.get("createdAt") or 0),
            "updatedAt": int(item.get("updatedAt") or 0),
            "pinned": bool(item.get("pinned")),
            "messages": messages,
        })
    current_id = str(raw.get("currentId") or "").strip()[:160]
    if current_id not in seen_threads:
        current_id = threads[0]["id"] if threads else ""
    return {"version": 1, "currentId": current_id, "threads": threads}


def _user(request: Request) -> str:
    return user_id_from_request(request)


@app.get("/", include_in_schema=False)
@app.get("/api/chat_state", include_in_schema=False)
async def get_state(request: Request):
    try:
        user_id = _user(request)
        value = _read_blob(user_id)
        token, store_id, auth_kind = _blob_auth()
        if value is None:
            return JSONResponse({"ok": True, "contract": CONTRACT, "revision": 0, "state": None, "storage": {"configured": bool(token and store_id), "access": "private", "authKind": auth_kind}}, headers=_headers())
        return JSONResponse({"ok": True, "contract": CONTRACT, "revision": int(value.get("revision") or 0), "updatedAt": int(value.get("updatedAt") or 0), "state": value.get("state")}, headers=_headers())
    except AuthenticationError as exc:
        return _error(401, "ACCOUNT_SESSION_INVALID", str(exc))
    except Exception as exc:
        return _error(503, "CHAT_STATE_READ_FAILED", f"{type(exc).__name__}: {exc}")


@app.put("/", include_in_schema=False)
@app.put("/api/chat_state", include_in_schema=False)
async def put_state(request: Request):
    try:
        user_id = _user(request)
        body = await request.body()
        if len(body) > MAX_STATE_BYTES:
            return _error(413, "CHAT_STATE_TOO_LARGE", "Chat state exceeds the 2 MiB safety bound.")
        payload = json.loads(body or b"{}")
        if not isinstance(payload, dict):
            return _error(400, "CHAT_STATE_INVALID", "A JSON object is required.")
        state = _clean_state(payload.get("state"))
        expected = int(payload.get("baseRevision") or 0)
        current = _read_blob(user_id)
        current_revision = int(current.get("revision") or 0) if current else 0
        if expected != current_revision:
            return JSONResponse({"ok": False, "code": "CHAT_STATE_CONFLICT", "revision": current_revision, "state": current.get("state") if current else None}, status_code=409, headers=_headers())
        next_revision = current_revision + 1
        stamp = int(time.time() * 1000)
        _write_blob(user_id, {"contract": CONTRACT, "userId": user_id, "revision": next_revision, "updatedAt": stamp, "state": state})
        return JSONResponse({"ok": True, "contract": CONTRACT, "revision": next_revision, "updatedAt": stamp}, headers=_headers())
    except AuthenticationError as exc:
        return _error(401, "ACCOUNT_SESSION_INVALID", str(exc))
    except (ValueError, json.JSONDecodeError) as exc:
        return _error(400, "CHAT_STATE_INVALID", str(exc))
    except Exception as exc:
        return _error(503, "CHAT_STATE_WRITE_FAILED", f"{type(exc).__name__}: {exc}")
