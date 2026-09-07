from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Request
from fastapi.responses import JSONResponse

import api.chat as chat
from api.admin_auth_guard import _normalize_secret

SESSION_HEADER = "x-swrlz-chat-session"
SESSION_TTL_SECONDS = 8 * 60 * 60
SESSION_VERSION = 1
_ORIGINAL_REQUIRE = chat._require_web_token


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _signing_key() -> bytes:
    admin = _normalize_secret(os.environ.get("SWRLZ_ADMIN_TOKEN"))
    if not admin:
        return b""
    return hashlib.sha256(("swrlz-chat-admin-session-v1\0" + admin).encode("utf-8")).digest()


def _issue_session() -> tuple[str, int]:
    key = _signing_key()
    if not key:
        raise RuntimeError("ADMIN_SESSION_SIGNING_KEY_UNAVAILABLE")
    now = int(time.time())
    expires_at = now + SESSION_TTL_SECONDS
    payload = {"v": SESSION_VERSION, "iat": now, "exp": expires_at, "nonce": secrets.token_urlsafe(18), "kind": "admin-chat-session"}
    encoded = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = _b64(hmac.new(key, encoded.encode("ascii"), hashlib.sha256).digest())
    return f"{encoded}.{signature}", expires_at


def _session_valid(value: str) -> bool:
    if not value or len(value) > 2048:
        return False
    key = _signing_key()
    if not key:
        return False
    try:
        encoded, supplied_sig = value.split(".", 1)
        expected_sig = _b64(hmac.new(key, encoded.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(supplied_sig, expected_sig):
            return False
        payload = json.loads(_unb64(encoded).decode("utf-8"))
        if not isinstance(payload, dict) or payload.get("v") != SESSION_VERSION or payload.get("kind") != "admin-chat-session":
            return False
        now = int(time.time())
        issued = int(payload.get("iat", 0))
        expires = int(payload.get("exp", 0))
        return issued <= now <= expires and expires - issued <= SESSION_TTL_SECONDS
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        return False


def _require_web_or_admin_session(request: Request) -> None:
    session = request.headers.get(SESSION_HEADER, "").strip()
    if _session_valid(session):
        return
    _ORIGINAL_REQUIRE(request)


def install(server) -> None:
    chat._require_web_token = _require_web_or_admin_session

    @chat.app.post("/admin-session", include_in_schema=False)
    async def admin_chat_session(request: Request):
        if not server.auth(request):
            return JSONResponse({"ok": False, "code": "ADMIN_AUTH_REJECTED", "detail": "A valid Admin credential is required to authorize this Chat browser session."}, status_code=401, headers=chat._no_store_headers())
        try:
            token, expires_at = _issue_session()
        except RuntimeError as exc:
            return JSONResponse({"ok": False, "code": str(exc), "detail": "Admin Chat session signing is unavailable."}, status_code=503, headers=chat._no_store_headers())
        return JSONResponse({"ok": True, "session": token, "expiresAt": expires_at, "ttlSeconds": SESSION_TTL_SECONDS, "credentialKind": "STATELESS_ADMIN_CHAT_SESSION"}, headers=chat._no_store_headers())

    server.CAPABILITIES["admin-chat-session"] = {
        "kind": "stateless-session-auth",
        "ready": True,
        "path": "/api/chat/admin-session",
        "ttlSeconds": SESSION_TTL_SECONDS,
        "instanceIndependent": True,
        "permanentChatSecretExposed": False,
        "fallbackChatTokenSupported": True,
    }
