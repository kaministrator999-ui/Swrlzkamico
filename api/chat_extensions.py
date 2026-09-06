from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

import api.chat as chat

ROOT = Path(__file__).resolve().parents[1]
CHAT_PAGE = ROOT / "web" / "chat.html"
ENH_JS = ROOT / "web" / "chat_enhancements.js"
ENH_CSS = ROOT / "web" / "chat_enhancements.css"
SERVER_STATE = Path("/tmp/swrlz-admin/runtime/server-state.json")
ACTIVE: dict[str, dict[str, Any]] = {}

_original_normalize = chat._normalize_chat_request

def _normalize_with_generation(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _original_normalize(payload)
    raw = payload.get("generation")
    if isinstance(raw, dict):
        generation: dict[str, Any] = {}
        try:
            if "temperature" in raw: generation["temperature"] = min(2.0, max(0.0, float(raw["temperature"])))
            if "topP" in raw: generation["topP"] = min(1.0, max(0.0, float(raw["topP"])))
            if "maxTokens" in raw: generation["maxTokens"] = min(8192, max(1, int(raw["maxTokens"])))
        except (TypeError, ValueError):
            generation = {}
        if generation:
            normalized["generation"] = generation
    return normalized

chat._normalize_chat_request = _normalize_with_generation
chat.APP_VERSION = "1.2.0"
chat.app.version = "1.2.0"


def _server_state() -> dict[str, Any]:
    try:
        return json.loads(SERVER_STATE.read_text("utf-8"))
    except Exception:
        return {}


def runtime_chat_state() -> dict[str, Any]:
    now = time.time()
    return {
        "available": True,
        "activeStreams": len(ACTIVE),
        "requests": [{**v, "ageSeconds": round(now-v["startedAt"], 2)} for v in ACTIVE.values()],
        "server": _server_state(),
        "bridgeVersion": chat.APP_VERSION,
    }


@chat.app.middleware("http")
async def swrlz_chat_extensions(request: Request, call_next):
    path = request.url.path.rstrip("/")
    if request.method == "GET" and path.endswith("/api/chat") and not request.query_params:
        html = CHAT_PAGE.read_text("utf-8")
        html = html.replace("</head>", '<link rel="stylesheet" href="/api/chat/assets/enhancements.css"></head>')
        html = html.replace("</body>", '<script src="/api/chat/assets/enhancements.js"></script></body>')
        return HTMLResponse(html, headers={"Cache-Control":"no-store","Content-Security-Policy":"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"})
    is_stream = request.method == "POST" and (request.query_params.get("action", "").lower() == "stream" or path.endswith("/stream"))
    response = await call_next(request)
    if is_stream:
        rid = response.headers.get("x-swrlz-request-id", "")
        if rid:
            ACTIVE[rid] = {"requestId": rid, "startedAt": time.time(), "path": request.url.path}
            iterator = getattr(response, "body_iterator", None)
            if iterator is not None:
                original = iterator
                async def wrapped():
                    try:
                        async for chunk in original:
                            yield chunk
                    finally:
                        ACTIVE.pop(rid, None)
                response.body_iterator = wrapped()
    return response


@chat.app.get("/assets/enhancements.js", include_in_schema=False)
async def enhancements_js():
    return FileResponse(ENH_JS, media_type="application/javascript", headers={"Cache-Control":"no-store"})


@chat.app.get("/assets/enhancements.css", include_in_schema=False)
async def enhancements_css():
    return FileResponse(ENH_CSS, media_type="text/css", headers={"Cache-Control":"no-store"})


@chat.app.get("/ops", include_in_schema=False)
async def ops_status():
    base = chat._status_payload()
    base["operations"] = runtime_chat_state()
    return JSONResponse(base, headers=chat._no_store_headers())
