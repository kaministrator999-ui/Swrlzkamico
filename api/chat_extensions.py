from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterator

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse

import api.chat as chat
import swyrlz.r39_matvec_patch  # apply bounded-memory matvec before local generation
from swyrlz.r39_inference import ENGINE_ID as LOCAL_ENGINE_ID, MODEL_SHA256 as LOCAL_MODEL_SHA256, generate_events, inspect_engine

ROOT = Path(__file__).resolve().parents[1]
CHAT_PAGE = ROOT / "web" / "chat.html"
ENH_JS = ROOT / "web" / "chat_enhancements.js"
ENH_CSS = ROOT / "web" / "chat_enhancements.css"
SERVER_STATE = Path("/tmp/swrlz-admin/runtime/server-state.json")
ACTIVE: dict[str, dict[str, Any]] = {}
LOCAL_CANCELLED: set[str] = set()
LOCAL_READINESS: dict[str, Any] = {"checked": False, "oneTokenReady": False, "interactiveReady": False, "code": "R39_ENGINE_NOT_PROBED"}

_original_normalize = chat._normalize_chat_request
_original_status_payload = chat._status_payload
_original_verify_r39 = chat._verify_r39
_original_forward_cancel = chat._forward_cancel


def _normalize_with_generation(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _original_normalize(payload)
    raw = payload.get("generation")
    if isinstance(raw, dict):
        generation: dict[str, Any] = {}
        try:
            if "temperature" in raw: generation["temperature"] = min(2.0, max(0.0, float(raw["temperature"])))
            if "topP" in raw: generation["topP"] = min(1.0, max(0.0, float(raw["topP"])))
            if "maxTokens" in raw: generation["maxTokens"] = min(512, max(1, int(raw["maxTokens"])))
        except (TypeError, ValueError):
            generation = {}
        if generation:
            normalized["generation"] = generation
    return normalized


chat._normalize_chat_request = _normalize_with_generation
chat.APP_VERSION = "1.3.0"
chat.app.version = "1.3.0"


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
        "localEngine": {"engineId": LOCAL_ENGINE_ID, "modelSha256": LOCAL_MODEL_SHA256, **LOCAL_READINESS},
    }


def _status_payload() -> dict[str, Any]:
    base = _original_status_payload()
    if not chat._raw_upstream_url():
        base["mode"] = "LOCAL_R39"
        base["localR39"] = {
            "containerVerificationAvailable": True,
            "engineWired": True,
            "engineId": LOCAL_ENGINE_ID,
            "modelSha256": LOCAL_MODEL_SHA256,
            "oneTokenReady": bool(LOCAL_READINESS.get("oneTokenReady")),
            "interactiveReady": bool(LOCAL_READINESS.get("interactiveReady")),
            "readinessChecked": bool(LOCAL_READINESS.get("checked")),
            "blockers": [] if LOCAL_READINESS.get("interactiveReady") else [str(LOCAL_READINESS.get("code") or "R39_ENGINE_NOT_PROBED")],
        }
    return base


chat._status_payload = _status_payload


def _verify_r39() -> dict[str, Any]:
    base = _original_verify_r39()
    engine = inspect_engine()
    LOCAL_READINESS.clear()
    LOCAL_READINESS.update({"checked": True, **engine})
    base["engine"] = engine
    return base


chat._verify_r39 = _verify_r39


def _event_payload(seq: int, request_id: str, raw: dict[str, Any]) -> dict[str, Any]:
    event_type = str(raw.get("type", "STATUS"))
    terminal = event_type in chat.TERMINAL_TYPES
    event = chat._bridge_event(
        seq,
        event_type,
        request_id,
        phase=str(raw.get("phase") or "STATE_VALIDATION"),
        reason=str(raw.get("reason") or ""),
        categories=[str(x) for x in raw.get("categories", [])][:12],
        terminal=terminal,
    )
    identity = raw.get("identity")
    if isinstance(identity, dict):
        event["identity"].update({k: str(v) for k, v in identity.items() if k in {"route", "engineId", "modelId", "modelSha256"} and v is not None})
    if event_type == "DELTA": event["text"] = str(raw.get("text") or "")
    if raw.get("firstDeltaLatencyMs") is not None: event["firstDeltaLatencyMs"] = int(raw["firstDeltaLatencyMs"])
    if raw.get("totalLatencyMs") is not None: event["totalLatencyMs"] = int(raw["totalLatencyMs"])
    if event_type == "COMPLETED": event["answerState"] = "COMMITTED"
    elif event_type == "CANCELLED": event["answerState"] = "PARTIAL_OR_EMPTY"
    elif event_type == "FAILED": event["answerState"] = "PARTIAL_OR_EMPTY"
    elif event_type == "DELTA": event["answerState"] = "STREAMING"
    return event


def _local_stream(payload: dict[str, Any]) -> Iterator[bytes]:
    request_id = payload["requestId"]
    LOCAL_CANCELLED.discard(request_id)
    seq = 1
    yield chat._encode_event(chat._bridge_event(seq, "STARTED", request_id, phase="ANALYZING_REQUEST", reason="Request admitted by the local R39 Vercel inference bridge."))
    seq += 1
    try:
        for raw in generate_events(payload, lambda: request_id in LOCAL_CANCELLED):
            event = _event_payload(seq, request_id, raw)
            yield chat._encode_event(event)
            if raw.get("type") == "ROUTE":
                LOCAL_READINESS.update({"checked": True, "oneTokenReady": True, "interactiveReady": True, "ok": True, "engineId": LOCAL_ENGINE_ID})
            seq += 1
    finally:
        LOCAL_CANCELLED.discard(request_id)


def _stream_response(payload: dict[str, Any]) -> StreamingResponse:
    upstream_ready, missing = chat._upstream_ready()
    if chat._raw_upstream_url() and not upstream_ready:
        raise chat.BridgeError(503, "UPSTREAM_CONFIGURATION_INCOMPLETE", "The upstream bridge is missing: " + ", ".join(missing))
    iterator = chat._proxy_stream(payload) if upstream_ready else _local_stream(payload)
    headers = chat._no_store_headers()
    headers.update({"X-SWRLZ-Stream-Contract": chat.STREAM_CONTRACT, "X-SWRLZ-Request-Id": payload["requestId"], "X-Accel-Buffering": "no"})
    return StreamingResponse(iterator, media_type="application/x-ndjson", headers=headers)


chat._stream_response = _stream_response


def _forward_cancel(request_id: str) -> tuple[int, dict[str, Any]]:
    if chat._raw_upstream_url():
        return _original_forward_cancel(request_id)
    LOCAL_CANCELLED.add(request_id)
    return 200, {"protocolVersion": 2, "requestId": request_id, "accepted": True, "quiescent": False, "ownerRequestId": request_id, "waitedMs": 0, "detail": "Best-effort local cancellation was armed for this runtime instance."}


chat._forward_cancel = _forward_cancel


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
                        async for chunk in original: yield chunk
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
    base = chat._status_payload(); base["operations"] = runtime_chat_state()
    return JSONResponse(base, headers=chat._no_store_headers())
