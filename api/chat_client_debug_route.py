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


@app.post("/")
async def post_debug(request: Request):
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


@app.get("/")
async def get_debug(limit: int = 120):
    safe_limit = max(1, min(int(limit or 120), 500))
    with _LOCK:
        rows = list(_RECENT)[-safe_limit:]
    return JSONResponse({"ok": True, "count": len(rows), "events": rows}, headers={"Cache-Control": "no-store"})
