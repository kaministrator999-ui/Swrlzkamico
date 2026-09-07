from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Request
from fastapi.responses import JSONResponse, Response

import api.chat as chat
from api.admin_auth_guard import _normalize_secret

SESSION_HEADER = "x-swrlz-chat-session"
SESSION_COOKIE = "swrlz_chat_session"
SESSION_TTL_SECONDS = 8 * 60 * 60
SESSION_VERSION = 2
_ORIGINAL_REQUIRE = chat._require_web_token


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _chat_secret() -> str:
    """Resolve the durable Chat secret without exposing it to the browser."""
    env = _normalize_secret(os.environ.get("SWRLZ_WEB_CHAT_TOKEN"))
    if chat._valid_token(env):
        return env
    token, configured = chat._web_token_state()
    return token if configured else ""


def _signing_key() -> bytes:
    secret = _chat_secret()
    if not secret:
        return b""
    return hashlib.sha256(("swrlz-browser-chat-session-v2\0" + secret).encode("utf-8")).digest()


def _issue_session() -> tuple[str, int]:
    key = _signing_key()
    if not key:
        raise RuntimeError("CHAT_SESSION_SIGNING_KEY_UNAVAILABLE")
    now = int(time.time())
    expires_at = now + SESSION_TTL_SECONDS
    payload = {
        "v": SESSION_VERSION,
        "iat": now,
        "exp": expires_at,
        "nonce": secrets.token_urlsafe(18),
        "kind": "browser-chat-session",
    }
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
        if not isinstance(payload, dict) or payload.get("v") != SESSION_VERSION or payload.get("kind") != "browser-chat-session":
            return False
        now = int(time.time())
        issued = int(payload.get("iat", 0))
        expires = int(payload.get("exp", 0))
        return issued <= now <= expires and expires - issued <= SESSION_TTL_SECONDS
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        return False


def _request_session(request: Request) -> str:
    header = request.headers.get(SESSION_HEADER, "").strip()
    if header:
        return header
    return request.cookies.get(SESSION_COOKIE, "").strip()


def _require_web_or_browser_session(request: Request) -> None:
    if _session_valid(_request_session(request)):
        return
    _ORIGINAL_REQUIRE(request)


def attach_browser_session_cookie(response: Response, request: Request) -> Response:
    """Attach/refresh a same-origin HttpOnly Chat session when Chat is configured.

    The permanent SWRLZ_WEB_CHAT_TOKEN remains server-side. The browser receives
    only a bounded signed session cookie scoped to /api/chat.
    """
    existing = request.cookies.get(SESSION_COOKIE, "").strip()
    if _session_valid(existing):
        return response
    try:
        token, _ = _issue_session()
    except RuntimeError:
        return response
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/api/chat",
    )
    response.headers["X-SWRLZ-Chat-Session"] = "server-managed-cookie"
    return response


def install(server) -> None:
    chat._require_web_token = _require_web_or_browser_session

    @chat.app.post("/admin-session", include_in_schema=False)
    async def admin_chat_session(request: Request):
        """Compatibility route: Admin may still request an explicit session token."""
        if not server.auth(request):
            return JSONResponse(
                {"ok": False, "code": "ADMIN_AUTH_REJECTED", "detail": "A valid Admin credential is required to authorize this Chat browser session."},
                status_code=401,
                headers=chat._no_store_headers(),
            )
        try:
            token, expires_at = _issue_session()
        except RuntimeError as exc:
            return JSONResponse(
                {"ok": False, "code": str(exc), "detail": "Chat session signing is unavailable."},
                status_code=503,
                headers=chat._no_store_headers(),
            )
        return JSONResponse(
            {
                "ok": True,
                "session": token,
                "expiresAt": expires_at,
                "ttlSeconds": SESSION_TTL_SECONDS,
                "credentialKind": "STATELESS_BROWSER_CHAT_SESSION",
            },
            headers=chat._no_store_headers(),
        )

    server.CAPABILITIES["browser-chat-session"] = {
        "kind": "same-origin-http-only-session",
        "ready": True,
        "cookie": SESSION_COOKIE,
        "path": "/api/chat",
        "ttlSeconds": SESSION_TTL_SECONDS,
        "instanceIndependentWhenEnvTokenConfigured": True,
        "permanentChatSecretExposed": False,
        "manualChatTokenRequired": False,
        "fallbackChatTokenSupported": True,
    }
