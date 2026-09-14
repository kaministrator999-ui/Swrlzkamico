from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
import json
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
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


async def _post_debug(request: Request):
    try:
        raw = await request.json()
    except Exception:
        raw = {}
    record = {
        "receivedAt": datetime.now(timezone.utc).isoformat(),
        "event": _clean(raw if isinstance(raw, dict) else {}),
    }
    with _LOCK:
        _RECENT.append(record)
    print("SWRLZ_CHAT_CLIENT_DEBUG " + json.dumps(record, separators=(",", ":"), ensure_ascii=True), flush=True)
    return JSONResponse({"ok": True}, headers={"Cache-Control": "no-store"})


async def _get_debug(limit: int = 120):
    safe_limit = max(1, min(int(limit or 120), 500))
    with _LOCK:
        rows = list(_RECENT)[-safe_limit:]
    return JSONResponse({"ok": True, "count": len(rows), "events": rows}, headers={"Cache-Control": "no-store"})


# Vercel's current backend-framework rewrite behavior preserves the rewritten
# destination pathname when dispatching into the ASGI app. Keep the public,
# internal destination, and function-root forms explicit so diagnostics remain
# reachable without relying on pathname stripping semantics.
for _path in ("/", "/api/chat/client-debug", "/api/chat_client_debug_route"):
    app.add_api_route(_path, _post_debug, methods=["POST"], include_in_schema=False)
    app.add_api_route(_path, _get_debug, methods=["GET"], include_in_schema=False)
