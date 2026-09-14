from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
import json
from threading import Lock

_RECENT = deque(maxlen=500)
_LOCK = Lock()


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


def install(server) -> None:
    from fastapi import Request
    from fastapi.responses import JSONResponse

    # Stable api/index.py passes the server module; Vercel's file-routed
    # api/chat.py passes its FastAPI app directly. Support both authorities so
    # /api/chat/client-debug is installed on the function that actually owns
    # the /api/chat filesystem route.
    app = getattr(server, "app", server)

    @app.post("/api/chat/client-debug")
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
        # Vercel runtime logs are the durable operator-visible trail for a request.
        print("SWRLZ_CHAT_CLIENT_DEBUG " + json.dumps(record, separators=(",", ":"), ensure_ascii=True), flush=True)
        return JSONResponse({"ok": True}, headers={"Cache-Control": "no-store"})

    @app.get("/api/chat/client-debug")
    async def chat_client_debug_get(limit: int = 120):
        safe_limit = max(1, min(int(limit or 120), 500))
        with _LOCK:
            rows = list(_RECENT)[-safe_limit:]
        return JSONResponse({"ok": True, "count": len(rows), "events": rows}, headers={"Cache-Control": "no-store"})

    capabilities = getattr(server, "CAPABILITIES", None)
    if isinstance(capabilities, dict):
        capabilities["chat-client-debug"] = {
            "kind": "diagnostics",
            "ready": True,
            "path": "/api/chat/client-debug",
            "detail": "Bounded browser boot checkpoints are emitted to Vercel runtime logs and retained briefly in-process for direct inspection.",
        }
