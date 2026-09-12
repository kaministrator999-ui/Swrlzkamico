from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse

from api import account_routes as _base
from api.durable_redis_store import RedisRestChatStore
from api.google_account import (
    AuthenticationError,
    SESSION_COOKIE,
    issue_session,
    verify_google_credential,
    verify_session,
)


async def _enqueue_generation(payload: dict[str, Any], *, request_id: str) -> None:
    """Publish durable generation using the public Vercel Python Queues API.

    request_id is already persisted as the idempotent job key in Redis before this call.
    Vercel Queues provides at-least-once delivery; the worker therefore re-checks terminal
    state before doing model work.
    """
    from vercel.queue import send

    await send(_base.QUEUE_TOPIC, payload)


def _stateless_profile(identity: dict[str, Any]) -> dict[str, Any]:
    return {
        "user_id": str(identity.get("userId") or ""),
        "display_name": identity.get("name"),
        "preferences": {},
        "model_preferences": {},
        "ui_preferences": {},
        "version": 0,
        "updated_at": 0,
        "durable": False,
    }


def install(server) -> None:
    _base._enqueue_generation = _enqueue_generation

    @server.app.middleware("http")
    async def google_session_fallback(request, call_next):
        """Keep Google identity server-verified even before durable Redis is configured.

        Durable account/chat state still requires the Redis REST boundary. This fallback only
        supplies a signed, HttpOnly Google identity session so every browser can authenticate
        against the server instead of trusting a locally decoded Google credential.
        """
        path = request.url.path
        if RedisRestChatStore.configured():
            return await call_next(request)

        if path == "/api/account/google" and request.method.upper() == "POST":
            try:
                body = await request.json()
                verified = verify_google_credential(body.get("credential") if isinstance(body, dict) else "")
                user_id = f"google:{verified.subject}"
                identity = {
                    "userId": user_id,
                    "provider": "google",
                    "providerSubject": verified.subject,
                    "email": verified.email,
                    "emailVerified": verified.email_verified,
                    "name": verified.name,
                    "picture": verified.picture,
                    "durable": False,
                }
                response = JSONResponse(
                    content={
                        "ok": True,
                        "durable": False,
                        "user": {
                            "id": user_id,
                            "displayName": verified.name,
                            "email": verified.email,
                            "picture": verified.picture,
                        },
                        "profile": _stateless_profile(identity),
                    }
                )
                response.set_cookie(
                    SESSION_COOKIE,
                    issue_session(user_id, claims=identity),
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=7 * 24 * 60 * 60,
                    path="/",
                )
                return response
            except AuthenticationError as exc:
                return JSONResponse(status_code=401, content={"ok": False, "code": "GOOGLE_ID_TOKEN_INVALID", "detail": str(exc)})
            except Exception as exc:
                return JSONResponse(status_code=503, content={"ok": False, "code": "ACCOUNT_LOGIN_FAILED", "detail": f"{type(exc).__name__}: {exc}"})

        if path == "/api/account/me" and request.method.upper() == "GET":
            try:
                session = verify_session(request.cookies.get(SESSION_COOKIE))
                identity = session.get("identity") if isinstance(session.get("identity"), dict) else {}
                user_id = str(session.get("sub") or "")
                identity = {**identity, "userId": user_id, "durable": False}
                return JSONResponse(
                    content={
                        "ok": True,
                        "durable": False,
                        "user": {
                            "id": user_id,
                            "displayName": identity.get("name"),
                            "email": identity.get("email"),
                            "picture": identity.get("picture"),
                        },
                        "profile": _stateless_profile(identity),
                    }
                )
            except AuthenticationError as exc:
                return JSONResponse(status_code=401, content={"ok": False, "code": "ACCOUNT_SESSION_INVALID", "detail": str(exc)})
            except Exception as exc:
                return JSONResponse(status_code=503, content={"ok": False, "code": "ACCOUNT_READ_FAILED", "detail": f"{type(exc).__name__}: {exc}"})

        return await call_next(request)

    _base.install(server)
