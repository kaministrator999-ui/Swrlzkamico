from __future__ import annotations

import hmac
import secrets
import time
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

import api.chat as chat

SESSION_HEADER = "x-swrlz-chat-session"
SESSION_TTL_SECONDS = 8 * 60 * 60
_SESSIONS: dict[str, dict[str, Any]] = {}
_ORIGINAL_REQUIRE = chat._require_web_token


def _prune() -> None:
    now = time.time()
    stale = [key for key, value in _SESSIONS.items() if float(value.get("expiresAt", 0)) <= now]
    for key in stale:
        _SESSIONS.pop(key, None)


def _session_valid(value: str) -> bool:
    if not value:
        return False
    _prune()
    now = time.time()
    for token, state in list(_SESSIONS.items()):
        if hmac.compare_digest(token, value):
            return float(state.get("expiresAt", 0)) > now
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
            return JSONResponse(
                {"ok": False, "code": "ADMIN_AUTH_REJECTED", "detail": "A valid Admin credential is required to authorize this Chat browser session."},
                status_code=401,
                headers=chat._no_store_headers(),
            )
        _prune()
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + SESSION_TTL_SECONDS
        _SESSIONS[token] = {"createdAt": time.time(), "expiresAt": expires_at}
        return JSONResponse(
            {"ok": True, "session": token, "expiresAt": expires_at, "ttlSeconds": SESSION_TTL_SECONDS, "credentialKind": "EPHEMERAL_ADMIN_CHAT_SESSION"},
            headers=chat._no_store_headers(),
        )

    server.CAPABILITIES["admin-chat-session"] = {
        "kind": "ephemeral-session-auth",
        "ready": True,
        "path": "/api/chat/admin-session",
        "ttlSeconds": SESSION_TTL_SECONDS,
        "permanentChatSecretExposed": False,
        "fallbackChatTokenSupported": True,
    }
