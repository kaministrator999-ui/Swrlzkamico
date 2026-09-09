from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse

import api.chat as chat
import swyrlz.r39_matvec_patch
import swyrlz.r39_tokenizer_patch
from api.hot_loader import get_engine, hot_chat_path
from api.online_evidence import (
    ONLINE_ROUTE,
    DerivedQuery,
    EvidenceBundle,
    EvidenceError,
    build_grounded_payload,
    configured_evidence_service,
)

ROOT = Path(__file__).resolve().parents[1]
BUNDLED_CHAT_PAGE = ROOT / "web" / "chat.html"
BUNDLED_ENH_JS = ROOT / "web" / "chat_enhancements.js"
BUNDLED_ENH_CSS = ROOT / "web" / "chat_enhancements.css"
SERVER_STATE = Path("/tmp/swrlz-admin/runtime/server-state.json")
ACTIVE: dict[str, dict[str, Any]] = {}
LOCAL_CANCELLED: set[str] = set()
LOCAL_READINESS: dict[str, Any] = {"checked": False, "oneTokenReady": False, "interactiveReady": False, "code": "R39_ENGINE_NOT_PROBED"}
_original_normalize = chat._normalize_chat_request
_original_status_payload = chat._status_payload
_original_verify_r39 = chat._verify_r39
_original_forward_cancel = chat._forward_cancel
_evidence_service_factory = configured_evidence_service


def _engine():
    module, source = get_engine()
    return module, source


def _normalize_with_generation(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _original_normalize(payload)
    raw = payload.get("generation")
    if isinstance(raw, dict):
        generation = {}
        try:
            if "temperature" in raw:
                generation["temperature"] = min(2.0, max(0.0, float(raw["temperature"])))
            if "topP" in raw:
                generation["topP"] = min(1.0, max(0.0, float(raw["topP"])))
            if "maxTokens" in raw:
                generation["maxTokens"] = min(512, max(1, int(raw["maxTokens"])))
        except (TypeError, ValueError):
            generation = {}
        if generation:
            normalized["generation"] = generation
    return normalized


chat._normalize_chat_request = _normalize_with_generation
chat.APP_VERSION = "1.4.0-rc.1"
chat.app.version = "1.4.0-rc.1"


def _server_state():
    try:
        return json.loads(SERVER_STATE.read_text("utf-8"))
    except Exception:
        return {}


def _probe_local_once(force: bool = False):
    if LOCAL_READINESS.get("checked") and not force:
        return
    try:
        engine, source = _engine()
        state = engine.inspect_engine()
        LOCAL_READINESS.clear()
        LOCAL_READINESS.update({"checked": True, "engineSource": source, **state})
    except Exception as exc:
        LOCAL_READINESS.clear()
        LOCAL_READINESS.update({"checked": True, "ok": False, "oneTokenReady": False, "interactiveReady": False, "code": "R39_ENGINE_PROBE_FAILED", "detail": f"{type(exc).__name__}: {exc}"})


def runtime_chat_state():
    now = time.time()
    engine, source = _engine()
    return {
        "available": True,
        "activeStreams": len(ACTIVE),
        "requests": [{**v, "ageSeconds": round(now - v["startedAt"], 2)} for v in ACTIVE.values()],
        "server": _server_state(),
        "bridgeVersion": chat.APP_VERSION,
        "localEngine": {
            "engineId": str(engine.ENGINE_ID),
            "modelSha256": str(engine.MODEL_SHA256),
            "source": source,
            "hotRevision": str(getattr(engine, "HOT_REVISION", "")),
            **LOCAL_READINESS,
        },
    }


def _status_payload():
    base = _original_status_payload()
    if not chat._raw_upstream_url():
        _probe_local_once()
        engine, source = _engine()
        base["mode"] = "LOCAL_R39"
        base["localR39"] = {
            "containerVerificationAvailable": True,
            "engineWired": True,
            "engineId": str(engine.ENGINE_ID),
            "modelSha256": str(engine.MODEL_SHA256),
            "engineSource": source,
            "hotRevision": str(getattr(engine, "HOT_REVISION", "")),
            "autoInitialize": True,
            "manualGate5Required": False,
            "oneTokenReady": bool(LOCAL_READINESS.get("oneTokenReady")),
            "interactiveReady": bool(LOCAL_READINESS.get("interactiveReady")),
            "readinessChecked": bool(LOCAL_READINESS.get("checked")),
            "blockers": [] if LOCAL_READINESS.get("interactiveReady") else [str(LOCAL_READINESS.get("code") or "R39_ENGINE_NOT_PROBED")],
        }
    return base


chat._status_payload = _status_payload


def _verify_r39():
    base = _original_verify_r39()
    engine, source = _engine()
    state = engine.inspect_engine()
    LOCAL_READINESS.clear()
    LOCAL_READINESS.update({"checked": True, "engineSource": source, **state})
    base["engine"] = {"source": source, **state}
    return base


chat._verify_r39 = _verify_r39


def _event_payload(seq, request_id, raw, *, protocol_version=2, evidence_bundle=None):
    event_type = str(raw.get("type", "STATUS"))
    terminal = event_type in chat.TERMINAL_TYPES
    online = protocol_version == 3
    event = chat._bridge_event(
        seq,
        event_type,
        request_id,
        phase=str(raw.get("phase") or "STATE_VALIDATION"),
        reason=str(raw.get("reason") or ""),
        categories=[str(x) for x in raw.get("categories", [])][:12],
        terminal=terminal,
        protocol_version=protocol_version,
        route=ONLINE_ROUTE if online else "LOCAL_R39_STATUS_ONLY",
    )
    identity = raw.get("identity")
    if isinstance(identity, dict):
        event["identity"].update({k: str(v) for k, v in identity.items() if k in {"route", "engineId", "modelId", "modelSha256"} and v is not None})
    if online:
        event["identity"]["route"] = ONLINE_ROUTE
    if event_type == "DELTA":
        event["text"] = str(raw.get("text") or "")
    if raw.get("firstDeltaLatencyMs") is not None:
        event["firstDeltaLatencyMs"] = int(raw["firstDeltaLatencyMs"])
    if raw.get("totalLatencyMs") is not None:
        event["totalLatencyMs"] = int(raw["totalLatencyMs"])
    if event_type == "COMPLETED":
        event["answerState"] = "COMMITTED"
    elif event_type in {"CANCELLED", "FAILED"}:
        event["answerState"] = "PARTIAL_OR_EMPTY"
    elif event_type == "DELTA":
        event["answerState"] = "STREAMING"
    if evidence_bundle is not None and event_type in {"COMPLETED", "CANCELLED", "FAILED"}:
        event["knowledgeReceipt"] = evidence_bundle.receipt()
    return event


def _heartbeat_events(source):
    """Reset the idle heartbeat timer after every actual engine event/progress event."""
    iterator = iter(source)
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="swrlz-r39") as pool:
        while True:
            future = pool.submit(next, iterator)
            while True:
                try:
                    raw = future.result(timeout=8.0)
                    break
                except FutureTimeout:
                    yield {"type": "STATUS", "phase": "COMPUTE_HEARTBEAT", "reason": "Local R39 compute is still active; keeping the response stream alive."}
            yield raw


def _local_stream(payload):
    request_id = payload["requestId"]
    protocol_version = int(payload.get("protocolVersion", 2))
    online = protocol_version == 3 and payload.get("knowledgeMode") == "ONLINE"
    route = ONLINE_ROUTE if online else "LOCAL_R39_STATUS_ONLY"
    LOCAL_CANCELLED.discard(request_id)
    seq = 1
    started_reason = "Request admitted by the local R39 Vercel inference bridge."
    if online:
        started_reason = "Request admitted by local R39 with explicitly requested remote web evidence."
    yield chat._encode_event(chat._bridge_event(seq, "STARTED", request_id, phase="ANALYZING_REQUEST", reason=started_reason, protocol_version=protocol_version, route=route))
    seq += 1
    evidence_bundle: EvidenceBundle | None = None
    engine_payload = payload
    try:
        if online:
            query = DerivedQuery(
                text=str(payload["knowledgeQuery"]),
                sha256=str(payload["knowledgeQuerySha256"]),
                redaction_count=int(payload.get("knowledgeQueryRedactionCount", 0)),
            )
            yield chat._encode_event(
                chat._bridge_event(
                    seq,
                    "STATUS",
                    request_id,
                    phase="KNOWLEDGE_QUERY_PREPARED",
                    reason="Prepared a bounded current-prompt-only query; conversation history was not sent to search.",
                    protocol_version=3,
                    route=route,
                ),
            )
            seq += 1
            try:
                service = _evidence_service_factory()
                with ThreadPoolExecutor(max_workers=1, thread_name_prefix="swrlz-evidence") as pool:
                    future = pool.submit(service.collect, query)
                    while True:
                        try:
                            evidence_bundle = future.result(timeout=4.0)
                            break
                        except FutureTimeout:
                            yield chat._encode_event(
                                chat._bridge_event(
                                    seq,
                                    "STATUS",
                                    request_id,
                                    phase="KNOWLEDGE_FETCH",
                                    reason="Online Evidence retrieval is still active within its bounded safe-fetch policy.",
                                    protocol_version=3,
                                    route=route,
                                ),
                            )
                            seq += 1
            except EvidenceError as exc:
                yield chat._encode_event(
                    chat._bridge_event(
                        seq,
                        "FAILED",
                        request_id,
                        phase="ERROR",
                        reason=exc.detail,
                        categories=[exc.code],
                        terminal=True,
                        protocol_version=3,
                        route=route,
                    ),
                )
                return
            except Exception:
                yield chat._encode_event(
                    chat._bridge_event(
                        seq,
                        "FAILED",
                        request_id,
                        phase="ERROR",
                        reason="Online Evidence failed before local generation began.",
                        categories=["ONLINE_EVIDENCE_RUNTIME_FAILED"],
                        terminal=True,
                        protocol_version=3,
                        route=route,
                    ),
                )
                return
            for source in evidence_bundle.sources:
                source_event = chat._bridge_event(
                    seq,
                    "SOURCE",
                    request_id,
                    phase="KNOWLEDGE_EVIDENCE_READY",
                    reason="A server-validated source is available as untrusted request-scoped evidence.",
                    protocol_version=3,
                    route=route,
                )
                source_event["source"] = source.public_record()
                yield chat._encode_event(source_event)
                seq += 1
            yield chat._encode_event(
                chat._bridge_event(
                    seq,
                    "STATUS",
                    request_id,
                    phase="KNOWLEDGE_EVIDENCE_READY",
                    reason=f"{len(evidence_bundle.sources)} source(s) passed safe fetch; grounding local R39 without changing model weights.",
                    protocol_version=3,
                    route=route,
                ),
            )
            seq += 1
            engine_payload = build_grounded_payload(payload, evidence_bundle)
            if request_id in LOCAL_CANCELLED:
                cancelled = chat._bridge_event(
                    seq,
                    "CANCELLED",
                    request_id,
                    phase="CANCELLED",
                    reason="Generation was cancelled after evidence retrieval.",
                    categories=["REQUEST_CANCELLED"],
                    terminal=True,
                    protocol_version=3,
                    route=route,
                )
                cancelled["knowledgeReceipt"] = evidence_bundle.receipt()
                yield chat._encode_event(cancelled)
                return
        engine, source = _engine()
        source_events = engine.generate_events(engine_payload, lambda: request_id in LOCAL_CANCELLED)
        try:
            for raw in _heartbeat_events(source_events):
                if raw.get("type") == "ROUTE":
                    LOCAL_READINESS.update({"checked": True, "oneTokenReady": True, "interactiveReady": True, "ok": True, "engineId": str(engine.ENGINE_ID), "engineSource": source})
                event = _event_payload(seq, request_id, raw, protocol_version=protocol_version, evidence_bundle=evidence_bundle)
                yield chat._encode_event(event)
                seq += 1
        except RuntimeError as exc:
            if "StopIteration" not in str(exc):
                raise
    finally:
        LOCAL_CANCELLED.discard(request_id)


def _stream_response(payload):
    upstream_ready, missing = chat._upstream_ready()
    if chat._raw_upstream_url() and not upstream_ready:
        raise chat.BridgeError(503, "UPSTREAM_CONFIGURATION_INCOMPLETE", "The upstream bridge is missing: " + ", ".join(missing))
    if payload.get("protocolVersion") == 3 and chat._raw_upstream_url():
        raise chat.BridgeError(
            409,
            "ONLINE_EVIDENCE_UPSTREAM_UNSUPPORTED",
            "Online Evidence currently composes only with local R39; the configured proof-bound upstream was not used and no fallback occurred.",
        )
    iterator = chat._proxy_stream(payload) if upstream_ready else _local_stream(payload)
    headers = chat._no_store_headers()
    headers.update({"X-SWRLZ-Stream-Contract": chat._stream_contract_for_protocol(int(payload.get("protocolVersion", 2))), "X-SWRLZ-Request-Id": payload["requestId"], "X-Accel-Buffering": "no"})
    return StreamingResponse(iterator, media_type="application/x-ndjson", headers=headers)


chat._stream_response = _stream_response


def _forward_cancel(request_id):
    if chat._raw_upstream_url():
        return _original_forward_cancel(request_id)
    LOCAL_CANCELLED.add(request_id)
    return 200, {"protocolVersion": 2, "requestId": request_id, "accepted": True, "quiescent": False, "ownerRequestId": request_id, "waitedMs": 0, "detail": "Best-effort local cancellation was armed for this runtime instance."}


chat._forward_cancel = _forward_cancel


@chat.app.middleware("http")
async def swrlz_chat_extensions(request: Request, call_next):
    path = request.url.path.rstrip("/")
    if request.method == "GET" and path.endswith("/api/chat") and not request.query_params:
        page = hot_chat_path("chat.html", BUNDLED_CHAT_PAGE)
        html = page.read_text("utf-8")
        html = html.replace("</head>", '<link rel="stylesheet" href="/api/chat/assets/enhancements.css"></head>')
        html = html.replace("</body>", '<script src="/api/chat/assets/enhancements.js"></script></body>')
        return HTMLResponse(html, headers={"Cache-Control": "no-store", "X-SWRLZ-Chat-UI-Source": "runtime-override" if page != BUNDLED_CHAT_PAGE else "bundled", "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"})
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
    target = hot_chat_path("chat_enhancements.js", BUNDLED_ENH_JS)
    return FileResponse(target, media_type="application/javascript", headers={"Cache-Control": "no-store", "X-SWRLZ-Chat-UI-Source": "runtime-override" if target != BUNDLED_ENH_JS else "bundled"})


@chat.app.get("/assets/enhancements.css", include_in_schema=False)
async def enhancements_css():
    target = hot_chat_path("chat_enhancements.css", BUNDLED_ENH_CSS)
    return FileResponse(target, media_type="text/css", headers={"Cache-Control": "no-store", "X-SWRLZ-Chat-UI-Source": "runtime-override" if target != BUNDLED_ENH_CSS else "bundled"})


@chat.app.get("/ops", include_in_schema=False)
async def ops_status():
    base = chat._status_payload()
    base["operations"] = runtime_chat_state()
    return JSONResponse(base, headers=chat._no_store_headers())
