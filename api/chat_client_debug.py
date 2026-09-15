from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
from threading import Lock

_RECENT = deque(maxlen=500)
_LOCK = Lock()
_RUNTIME_WEB_TOKEN = Path("/tmp/swrlz-admin/runtime/web-chat-token.txt")


def _clean(value, depth=0):
    if depth > 4:
        return "[depth-limit]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:2000]
    if isinstance(value, list):
        return [_clean(v, depth + 1) for v in value[:40]]
    if isinstance(value, dict):
        return {str(k)[:80]: _clean(v, depth + 1) for k, v in list(value.items())[:40]}
    return str(value)[:2000]


def _valid_token(value: str) -> bool:
    return 16 <= len(value) <= 512 and not any(ord(char) < 32 or ord(char) == 127 for char in value)


def _expected_web_token() -> str:
    try:
        runtime_token = _RUNTIME_WEB_TOKEN.read_text("utf-8").strip()
    except OSError:
        runtime_token = ""
    if _valid_token(runtime_token):
        return runtime_token
    configured = os.environ.get("SWRLZ_WEB_CHAT_TOKEN", "").strip()
    return configured if _valid_token(configured) else ""


def _authorized_chat_ingress(request) -> bool:
    expected = _expected_web_token()
    supplied = request.headers.get("x-swrlz-chat-token", "")
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


def _account_scope(request) -> str:
    try:
        from api.google_account import user_id_from_request
        user_id = user_id_from_request(request)
    except Exception:
        return ""
    return hashlib.sha256(str(user_id).encode("utf-8")).hexdigest()[:24]


def _message_receipt(payload: dict, request) -> dict | None:
    prompt = str(payload.get("prompt") or "").strip()
    if not prompt:
        return None
    request_id = str(payload.get("requestId") or "").strip()[:128]
    thread_id = str(payload.get("threadId") or "").strip()[:128]
    supplied_message_id = str(payload.get("messageId") or "").strip()[:160]
    derived = hashlib.sha256((request_id + "\x00" + thread_id + "\x00" + prompt).encode("utf-8")).hexdigest()[:24]
    return {
        "eventType": "CHAT_MESSAGE_ACCEPTED",
        "receivedAt": datetime.now(timezone.utc).isoformat(),
        "accountScope": _account_scope(request),
        "threadId": thread_id,
        "messageId": supplied_message_id or ("ingress:" + derived),
        "requestId": request_id,
        "role": "user",
        "text": prompt[:16000],
        "textBytes": len(prompt.encode("utf-8")),
        "persistence": "VERCEL_RUNTIME_LOG",
        "generationStarted": False,
    }


def install(server) -> None:
    from fastapi import Request
    from fastapi.responses import JSONResponse

    app = getattr(server, "app", server)

    async def chat_client_debug_post(request: Request):
        try:
            raw = await request.json()
        except Exception:
            raw = {}
        event = _clean(raw if isinstance(raw, dict) else {})
        record = {
            "receivedAt": datetime.now(timezone.utc).isoformat(),
            "event": event,
        }
        with _LOCK:
            _RECENT.append(record)
        print("SWRLZ_CHAT_CLIENT_DEBUG " + json.dumps(record, separators=(",", ":"), ensure_ascii=True), flush=True)
        return JSONResponse({"ok": True}, headers={"Cache-Control": "no-store"})

    async def chat_client_debug_get(request: Request):
        try:
            limit = int(request.query_params.get("limit", "120") or 120)
        except (TypeError, ValueError):
            limit = 120
        safe_limit = max(1, min(limit, 500))
        with _LOCK:
            rows = list(_RECENT)[-safe_limit:]
        return JSONResponse({"ok": True, "count": len(rows), "events": rows}, headers={"Cache-Control": "no-store"})

    # Vercel's function destination path is /api/chat.py. The public diagnostic
    # route is marked by vercel.json with a private query flag, so intercept it
    # before FastAPI route matching. This avoids depending on Vercel's internal
    # ASGI pathname semantics while keeping api/chat.py as the single owner.
    @app.middleware("http")
    async def chat_client_debug_middleware(request: Request, call_next):
        if request.query_params.get("__swrlz_client_debug") == "1":
            if request.method == "POST":
                return await chat_client_debug_post(request)
            if request.method == "GET":
                return await chat_client_debug_get(request)
            return JSONResponse({"ok": False, "detail": "Method Not Allowed"}, status_code=405, headers={"Cache-Control": "no-store"})

        # Capture the authenticated Chat message at the server ingress boundary,
        # before the route starts generation. This is intentionally a private
        # structured runtime-log receipt, not a public diagnostic response.
        if request.method == "POST" and _authorized_chat_ingress(request):
            action = request.query_params.get("action", "stream").strip().lower()
            if action == "stream":
                try:
                    raw = await request.json()
                except Exception:
                    raw = {}
                if isinstance(raw, dict):
                    receipt = _message_receipt(raw, request)
                    if receipt is not None:
                        print("SWRLZ_CHAT_MESSAGE " + json.dumps(receipt, separators=(",", ":"), ensure_ascii=True), flush=True)

        return await call_next(request)

    capabilities = getattr(server, "CAPABILITIES", None)
    if isinstance(capabilities, dict):
        capabilities["chat-client-debug"] = {
            "kind": "diagnostics",
            "ready": True,
            "path": "/api/chat/client-debug",
            "detail": "Bounded browser boot checkpoints are emitted to Vercel runtime logs and retained briefly in-process for direct inspection.",
        }
