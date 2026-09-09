from __future__ import annotations

import hmac
import json
import mimetypes
import os
import re
import secrets
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterator

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse

from api.online_evidence import EvidenceError, ONLINE_STREAM_CONTRACT, derive_knowledge_query, evidence_configuration_status


APP_VERSION = "1.1.0"
BRIDGE_CONTRACT = "swrlz_vercel_chat_bridge_v1"
STREAM_CONTRACT_V2 = "swrlz_llm_stream_v2"
STREAM_CONTRACT_V3 = ONLINE_STREAM_CONTRACT
STREAM_CONTRACT = STREAM_CONTRACT_V2
STREAM_PATH = "/ai/swrlz-llm/v2/chat/stream"
MAX_REQUEST_BYTES = 128 * 1024
MAX_EVENT_BYTES = 65_536
REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
EVENT_TYPES = {
    "STARTED",
    "STATUS",
    "ROUTE",
    "DELTA",
    "RESET",
    "COMPLETED",
    "CANCELLED",
    "FAILED",
}
EVENT_TYPES_V3 = EVENT_TYPES | {"SOURCE"}
TERMINAL_TYPES = {"COMPLETED", "CANCELLED", "FAILED"}
ROOT = Path(__file__).resolve().parents[1]
CHAT_PAGE = ROOT / "web" / "chat.html"
RUNTIME_ROOT = Path("/tmp/swrlz-admin/runtime")
RUNTIME_WEB_TOKEN = RUNTIME_ROOT / "web-chat-token.txt"
LIVE_WEB_ROOT = Path("/tmp/swrlz-admin/web")
for directory in (RUNTIME_ROOT, LIVE_WEB_ROOT):
    directory.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="SWRLZ Vercel Chat Bridge",
    version=APP_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


class BridgeError(Exception):
    def __init__(self, status: int, code: str, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.code = code
        self.detail = detail


def _no_store_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store, no-transform",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
    }


def _json_error(status: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(
        {"ok": False, "code": code, "detail": detail},
        status_code=status,
        headers=_no_store_headers(),
    )


def _valid_token(value: str) -> bool:
    return 16 <= len(value) <= 512 and not any(ord(char) < 32 or ord(char) == 127 for char in value)


def _runtime_web_token() -> str:
    try:
        token = RUNTIME_WEB_TOKEN.read_text("utf-8").strip()
    except OSError:
        return ""
    return token if _valid_token(token) else ""


def _web_token_state() -> tuple[str, bool]:
    runtime_token = _runtime_web_token()
    if runtime_token:
        return runtime_token, True
    token = os.environ.get("SWRLZ_WEB_CHAT_TOKEN", "").strip()
    return token, _valid_token(token)


def _require_web_token(request: Request) -> None:
    expected, configured = _web_token_state()
    if not configured:
        raise BridgeError(
            503,
            "WEB_CHAT_TOKEN_NOT_CONFIGURED",
            "Set SWRLZ_WEB_CHAT_TOKEN or /tmp/swrlz-admin/runtime/web-chat-token.txt to a private value of at least 16 characters.",
        )
    supplied = request.headers.get("x-swrlz-chat-token", "")
    if not supplied or not hmac.compare_digest(expected, supplied):
        raise BridgeError(401, "WEB_CHAT_TOKEN_REJECTED", "The chat access token was rejected.")


def _raw_upstream_url() -> str:
    return os.environ.get("SWRLZ_CHAT_UPSTREAM_URL", "").strip()


def _upstream_url() -> str:
    raw = _raw_upstream_url()
    if not raw:
        return ""
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return ""
    clean = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))
    path = parsed.path.rstrip("/")
    if path.endswith(STREAM_PATH):
        return clean
    if path.endswith("/ai/swrlz-llm/v2"):
        return clean + "/chat/stream"
    return clean + STREAM_PATH


def _upstream_credentials() -> tuple[str, str, str]:
    return (
        os.environ.get("SWRLZ_CHAT_UPSTREAM_NODE_ID", "").strip(),
        os.environ.get("SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF", "").strip(),
        os.environ.get("SWRLZ_CHAT_UPSTREAM_BEARER", "").strip(),
    )


def _safe_header_value(value: str, maximum: int) -> bool:
    return bool(value) and len(value) <= maximum and not any(ord(char) < 32 or ord(char) == 127 for char in value)


def _upstream_ready() -> tuple[bool, list[str]]:
    missing: list[str] = []
    if not _upstream_url():
        missing.append("SWRLZ_CHAT_UPSTREAM_URL")
    node_id, proof, bearer = _upstream_credentials()
    if not _safe_header_value(node_id, 256):
        missing.append("SWRLZ_CHAT_UPSTREAM_NODE_ID")
    if len(proof) < 16 or not _safe_header_value(proof, 1024):
        missing.append("SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF")
    if bearer and not _safe_header_value(bearer, 2048):
        missing.append("SWRLZ_CHAT_UPSTREAM_BEARER")
    return not missing, missing


def _status_payload() -> dict[str, Any]:
    token, token_ready = _web_token_state()
    del token
    raw_endpoint = _raw_upstream_url()
    endpoint = _upstream_url()
    upstream_ready, missing = _upstream_ready()
    mode = "UPSTREAM_SERVER" if raw_endpoint else "LOCAL_R39_STATUS_ONLY"
    return {
        "ok": True,
        "bridge": {
            "version": APP_VERSION,
            "contractId": BRIDGE_CONTRACT,
            "streamContractId": STREAM_CONTRACT,
            "streamContracts": {"2": STREAM_CONTRACT_V2, "3": STREAM_CONTRACT_V3},
        },
        "mode": mode,
        "security": {
            "chatTokenConfigured": token_ready,
            "runtimeTokenOverride": RUNTIME_WEB_TOKEN.is_file() and bool(_runtime_web_token()),
        },
        "liveWeb": {
            "enabled": True,
            "basePath": "/live/",
            "storage": "EPHEMERAL_INSTANCE_LOCAL",
        },
        "upstream": {
            "configured": bool(raw_endpoint),
            "urlAccepted": bool(endpoint),
            "configurationReady": upstream_ready,
            "reachability": "UNVERIFIED",
            "missing": missing if raw_endpoint else [],
        },
        "localR39": {
            "containerVerificationAvailable": True,
            "oneTokenReady": False,
            "interactiveReady": False,
            "blockers": ["SECTION_PAYLOAD_LOCATION_AND_INFERENCE_WIRING_PENDING"],
        },
        "knowledge": evidence_configuration_status(),
    }


def _safe_live_path(asset_path: str) -> Path:
    root = LIVE_WEB_ROOT.resolve()
    candidate = (LIVE_WEB_ROOT / asset_path.lstrip("/")).resolve()
    if candidate != root and root not in candidate.parents:
        raise BridgeError(403, "LIVE_PATH_REJECTED", "The requested live path escapes the runtime web root.")
    return candidate


def _live_response(request: Request, asset_path: str):
    try:
        target = _safe_live_path(asset_path)
    except BridgeError as exc:
        return _json_error(exc.status, exc.code, exc.detail)
    if target.is_dir():
        index = target / "index.html"
        if not index.is_file():
            if target == LIVE_WEB_ROOT.resolve():
                return JSONResponse(
                    {
                        "ok": True,
                        "service": "SWRLZ Live Web Workspace",
                        "basePath": "/live/",
                        "detail": "Upload pages and assets under /tmp/swrlz-admin/web. Directories publish index.html.",
                    },
                    headers=_no_store_headers(),
                )
            return _json_error(404, "LIVE_INDEX_MISSING", "This live directory does not contain index.html.")
        if asset_path and not request.url.path.endswith("/"):
            public_path = "/live/" + urllib.parse.quote(asset_path.strip("/"), safe="/-._~") + "/"
            return RedirectResponse(public_path, status_code=307, headers=_no_store_headers())
        target = index
    if not target.is_file():
        return _json_error(404, "LIVE_FILE_NOT_FOUND", "The requested live file does not exist in this runtime instance.")
    media_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    headers = _no_store_headers()
    headers["Cache-Control"] = "no-store, max-age=0"
    headers["Cross-Origin-Resource-Policy"] = "same-origin"
    return FileResponse(target, media_type=media_type, headers=headers)


async def _read_json(request: Request) -> dict[str, Any]:
    body = await request.body()
    if len(body) > MAX_REQUEST_BYTES:
        raise BridgeError(413, "REQUEST_TOO_LARGE", "The request exceeds 128 KiB.")
    try:
        value = json.loads(body or b"{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BridgeError(400, "INVALID_JSON", "A valid UTF-8 JSON object is required.") from exc
    if not isinstance(value, dict):
        raise BridgeError(400, "INVALID_JSON_OBJECT", "The request body must be a JSON object.")
    return value


def _clean_request_id(value: Any) -> str:
    candidate = str(value or "").strip()
    if not candidate:
        candidate = "web:" + secrets.token_urlsafe(18).replace("-", "_")
    if not REQUEST_ID.fullmatch(candidate):
        raise BridgeError(
            400,
            "REQUEST_ID_INVALID",
            "requestId must use 1-128 URL-safe letters, digits, '.', '_', ':', or '-'.",
        )
    return candidate


def _clean_text(value: Any, maximum: int) -> str:
    return str(value or "").strip()[:maximum]


def _normalize_chat_request(payload: dict[str, Any]) -> dict[str, Any]:
    prompt = _clean_text(payload.get("prompt"), 16_001)
    if not prompt or len(prompt) > 16_000:
        raise BridgeError(400, "PROMPT_INVALID", "A nonblank prompt of at most 16000 characters is required.")
    request_id = _clean_request_id(payload.get("requestId"))
    history_value = payload.get("history", [])
    if not isinstance(history_value, list):
        raise BridgeError(400, "HISTORY_INVALID", "history must be a JSON array.")
    history: list[dict[str, str]] = []
    for turn in history_value[-32:]:
        if not isinstance(turn, dict):
            continue
        role = _clean_text(turn.get("role"), 16).lower()
        text = _clean_text(turn.get("text"), 2_000)
        if role in {"user", "assistant"} and text:
            history.append({"role": role.upper(), "text": text})
    protocol_version = payload.get("protocolVersion", 2)
    if isinstance(protocol_version, bool) or not isinstance(protocol_version, int) or protocol_version not in {2, 3}:
        raise BridgeError(400, "PROTOCOL_VERSION_UNSUPPORTED", "protocolVersion must be 2 (offline) or 3 (Online Evidence).")
    knowledge_mode = _clean_text(payload.get("knowledgeMode") or "OFFLINE", 16).upper()
    if knowledge_mode == "AUTO":
        raise BridgeError(400, "KNOWLEDGE_MODE_AUTO_NOT_IMPLEMENTED", "Automatic online routing is not implemented; choose OFFLINE or ONLINE explicitly.")
    if knowledge_mode not in {"OFFLINE", "ONLINE"}:
        raise BridgeError(400, "KNOWLEDGE_MODE_UNSUPPORTED", "knowledgeMode must be OFFLINE or ONLINE.")
    if knowledge_mode == "ONLINE" and protocol_version != 3:
        raise BridgeError(400, "ONLINE_EVIDENCE_REQUIRES_V3", "Online Evidence requires protocolVersion 3.")
    if knowledge_mode == "OFFLINE" and protocol_version != 2:
        raise BridgeError(400, "OFFLINE_CHAT_REQUIRES_V2", "Offline model-only Chat continues to use protocolVersion 2.")
    normalized = {
        "protocolVersion": 2,
        "requestId": request_id,
        "prompt": prompt,
        "history": history,
        "responseDirective": (
            "Answer directly and truthfully. Stream only committed assistant response text as DELTA. "
            "Keep status, routing, and operational detail outside assistant prose."
        ),
        "threadId": _clean_text(payload.get("threadId"), 128),
        "ingress": "VERCEL_CHAT",
        "profileId": _clean_text(payload.get("profileId"), 96),
    }
    if knowledge_mode == "ONLINE":
        try:
            query = derive_knowledge_query(prompt)
        except EvidenceError as exc:
            raise BridgeError(400, exc.code, exc.detail) from exc
        normalized.update(
            {
                "protocolVersion": 3,
                "knowledgeMode": "ONLINE",
                "knowledgeQuery": query.text,
                "knowledgeQuerySha256": query.sha256,
                "knowledgeQueryRedactionCount": query.redaction_count,
            },
        )
    return normalized


def _stream_contract_for_protocol(protocol_version: int) -> str:
    return STREAM_CONTRACT_V3 if protocol_version == 3 else STREAM_CONTRACT_V2


def _bridge_identity(request_id: str, route: str) -> dict[str, str]:
    return {
        "streamId": "vercel:" + request_id,
        "requestId": request_id,
        "route": route,
        "access": "CLIENT",
        "runtimeId": BRIDGE_CONTRACT,
        "engineId": "",
        "modelId": "",
        "modelSha256": "",
    }


def _bridge_event(
    seq: int,
    event_type: str,
    request_id: str,
    *,
    phase: str,
    reason: str = "",
    categories: list[str] | None = None,
    terminal: bool = False,
    protocol_version: int = 2,
    route: str = "LOCAL_R39_STATUS_ONLY",
) -> dict[str, Any]:
    return {
        "protocolVersion": protocol_version,
        "schemaVersion": 3 if protocol_version == 3 else 2,
        "contractId": _stream_contract_for_protocol(protocol_version),
        "seq": seq,
        "type": event_type,
        "identity": _bridge_identity(request_id, route),
        "text": "",
        "reason": reason,
        "categories": categories or [],
        "phase": phase,
        "ingress": "VERCEL_CHAT",
        "answerState": "NOT_STARTED",
        "terminal": terminal,
    }


def _encode_event(event: dict[str, Any]) -> bytes:
    return (json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def _local_not_ready_stream(request_id: str) -> Iterator[bytes]:
    yield _encode_event(
        _bridge_event(1, "STARTED", request_id, phase="ANALYZING_REQUEST", reason="Request admitted by the Vercel chat bridge."),
    )
    yield _encode_event(
        _bridge_event(
            2,
            "STATUS",
            request_id,
            phase="STATE_VALIDATION",
            reason="R39 container verification is available; interactive inference is not wired in the current server revision.",
        ),
    )
    yield _encode_event(
        _bridge_event(
            3,
            "FAILED",
            request_id,
            phase="ERROR",
            reason="Configure a proof-bound SWRLZ SERVER upstream before sending chat requests.",
            categories=["SECTION_PAYLOAD_LOCATION_AND_INFERENCE_WIRING_PENDING"],
            terminal=True,
        ),
    )


def _upstream_headers(request_id: str) -> dict[str, str]:
    node_id, proof, bearer = _upstream_credentials()
    headers = {
        "Accept": "application/x-ndjson",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": f"SWRLZ-Vercel-Chat/{APP_VERSION}",
        "X-SWRLZ-Device-Node-Id": node_id,
        "X-SWRLZ-Device-Proof": proof,
        "X-SWRLZ-Request-Id": request_id,
        "Idempotency-Key": request_id,
    }
    if bearer:
        headers["Authorization"] = "Bearer " + bearer
    return headers


def _timeout_seconds() -> float:
    try:
        value = float(os.environ.get("SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS", "45"))
    except ValueError:
        value = 45.0
    return min(290.0, max(10.0, value))


def _validate_upstream_event(raw: bytes, request_id: str, previous_seq: int) -> tuple[dict[str, Any], int]:
    if len(raw) > MAX_EVENT_BYTES:
        raise ValueError("UPSTREAM_EVENT_TOO_LARGE")
    try:
        event = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("UPSTREAM_EVENT_INVALID_JSON") from exc
    if not isinstance(event, dict):
        raise ValueError("UPSTREAM_EVENT_NOT_OBJECT")
    if event.get("protocolVersion") != 2 or event.get("contractId") != STREAM_CONTRACT:
        raise ValueError("UPSTREAM_EVENT_CONTRACT_MISMATCH")
    if event.get("schemaVersion") not in {1, 2}:
        raise ValueError("UPSTREAM_EVENT_SCHEMA_UNSUPPORTED")
    event_type = event.get("type")
    if event_type not in EVENT_TYPES:
        raise ValueError("UPSTREAM_EVENT_TYPE_UNSUPPORTED")
    seq = event.get("seq")
    if isinstance(seq, bool) or not isinstance(seq, int) or seq <= previous_seq:
        raise ValueError("UPSTREAM_EVENT_SEQUENCE_INVALID")
    identity = event.get("identity")
    if not isinstance(identity, dict) or identity.get("requestId") != request_id:
        raise ValueError("UPSTREAM_EVENT_IDENTITY_MISMATCH")
    if event_type == "DELTA" and not isinstance(event.get("text"), str):
        raise ValueError("UPSTREAM_DELTA_TEXT_INVALID")
    terminal = bool(event.get("terminal"))
    if (event_type in TERMINAL_TYPES) != terminal:
        raise ValueError("UPSTREAM_EVENT_TERMINAL_FLAG_INVALID")
    return event, seq


def _proxy_failed_event(seq: int, request_id: str, code: str, reason: str) -> bytes:
    return _encode_event(
        _bridge_event(
            seq,
            "FAILED",
            request_id,
            phase="ERROR",
            reason=reason,
            categories=[code],
            terminal=True,
        ),
    )


def _proxy_stream(payload: dict[str, Any]) -> Iterator[bytes]:
    request_id = payload["requestId"]
    request = urllib.request.Request(
        _upstream_url(),
        data=json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
        headers=_upstream_headers(request_id),
        method="POST",
    )
    last_seq = 0
    saw_terminal = False
    try:
        with urllib.request.urlopen(request, timeout=_timeout_seconds()) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "application/x-ndjson" not in content_type:
                raise ValueError("UPSTREAM_CONTENT_TYPE_INVALID")
            while True:
                raw = response.readline(MAX_EVENT_BYTES + 2)
                if not raw:
                    break
                if len(raw) > MAX_EVENT_BYTES + 1:
                    raise ValueError("UPSTREAM_EVENT_TOO_LARGE")
                raw = raw.strip()
                if not raw:
                    continue
                event, last_seq = _validate_upstream_event(raw, request_id, last_seq)
                yield _encode_event(event)
                if event["type"] in TERMINAL_TYPES:
                    saw_terminal = True
                    break
        if not saw_terminal:
            yield _proxy_failed_event(
                last_seq + 1,
                request_id,
                "UPSTREAM_STREAM_ENDED_WITHOUT_TERMINAL",
                "The upstream stream closed without a terminal event.",
            )
    except urllib.error.HTTPError as exc:
        yield _proxy_failed_event(
            last_seq + 1,
            request_id,
            f"UPSTREAM_HTTP_{exc.code}",
            f"The proof-bound SWRLZ SERVER rejected the request (HTTP {exc.code}).",
        )
    except urllib.error.URLError:
        yield _proxy_failed_event(
            last_seq + 1,
            request_id,
            "UPSTREAM_UNREACHABLE",
            "The configured SWRLZ SERVER upstream could not be reached.",
        )
    except (OSError, TimeoutError):
        yield _proxy_failed_event(
            last_seq + 1,
            request_id,
            "UPSTREAM_TRANSPORT_FAILED",
            "The upstream stream ended because of a transport failure or idle timeout.",
        )
    except ValueError as exc:
        code = str(exc) if str(exc).startswith("UPSTREAM_") else "UPSTREAM_STREAM_INVALID"
        yield _proxy_failed_event(
            last_seq + 1,
            request_id,
            code,
            "The upstream emitted an event that failed the SWRLZ stream contract.",
        )


def _cancel_url(request_id: str) -> str:
    stream_url = _upstream_url()
    if not stream_url:
        return ""
    parsed = urllib.parse.urlsplit(stream_url)
    path = parsed.path
    if not path.endswith(STREAM_PATH):
        return ""
    path = path[: -len(STREAM_PATH)] + STREAM_PATH + "/" + urllib.parse.quote(request_id, safe="._:-") + "/cancel"
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, ""))


def _forward_cancel(request_id: str) -> tuple[int, dict[str, Any]]:
    upstream_ready, missing = _upstream_ready()
    if not upstream_ready:
        if _raw_upstream_url():
            return 503, {
                "ok": False,
                "code": "UPSTREAM_CONFIGURATION_INCOMPLETE",
                "detail": "The upstream bridge is missing or rejects: " + ", ".join(missing),
            }
        return 200, {
            "protocolVersion": 2,
            "requestId": request_id,
            "accepted": True,
            "quiescent": True,
            "ownerRequestId": request_id,
            "waitedMs": 0,
            "detail": "The local status-only bridge has no active inference owner.",
        }
    request = urllib.request.Request(
        _cancel_url(request_id),
        data=b"{}",
        headers=_upstream_headers(request_id),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=min(30.0, _timeout_seconds())) as response:
            raw = response.read(MAX_REQUEST_BYTES + 1)
            if len(raw) > MAX_REQUEST_BYTES:
                raise ValueError("Cancel response too large")
            value = json.loads(raw or b"{}")
            if not isinstance(value, dict):
                raise ValueError("Cancel response is not an object")
            return int(response.status), value
    except urllib.error.HTTPError as exc:
        return exc.code, {
            "ok": False,
            "code": f"UPSTREAM_CANCEL_HTTP_{exc.code}",
            "detail": "The upstream rejected the cancellation request.",
        }
    except (urllib.error.URLError, OSError, TimeoutError, ValueError, json.JSONDecodeError):
        return 502, {
            "ok": False,
            "code": "UPSTREAM_CANCEL_FAILED",
            "detail": "The bridge could not confirm upstream cancellation.",
        }


def _verify_r39() -> dict[str, Any]:
    try:
        from swyrlz.backend import ensure_r39
        from swyrlz.gate5_live import inspect_r39
    except (ImportError, ModuleNotFoundError) as exc:
        raise BridgeError(
            503,
            "R39_VERIFIER_UNAVAILABLE",
            "The existing swyrlz backend and Gate 5 verifier are not present in this deployment.",
        ) from exc
    try:
        load = ensure_r39()
        gate = inspect_r39() if load.get("modelReady") else None
    except Exception as exc:
        name = type(exc).__name__
        raise BridgeError(503, "R39_VERIFY_FAILED", f"R39 verification failed ({name}).") from exc
    safe_load_keys = {"ok", "modelReady", "source", "code", "detail", "rawSha256", "actual", "expected"}
    safe_gate_keys = {
        "ok",
        "stage",
        "rawSize",
        "rawSha256",
        "containerVerified",
        "canonicalHeaderPresent",
        "requiredSectionsRegistered",
        "oneTokenReady",
        "interactiveReady",
        "blockers",
        "bytesInspectedAfterHash",
        "inspectionMs",
    }
    return {
        "ok": True,
        "load": {key: value for key, value in load.items() if key in safe_load_keys},
        "gate5": ({key: value for key, value in gate.items() if key in safe_gate_keys} if gate else None),
        "note": "Container verification is evidence of integrity, not evidence of one-token or interactive inference.",
    }


def _stream_response(payload: dict[str, Any]) -> StreamingResponse:
    if payload.get("protocolVersion") == 3:
        raise BridgeError(
            503,
            "ONLINE_EVIDENCE_EXECUTOR_UNAVAILABLE",
            "Online Evidence requires the integrated Chat extension executor.",
        )
    upstream_ready, missing = _upstream_ready()
    if _raw_upstream_url() and not upstream_ready:
        raise BridgeError(
            503,
            "UPSTREAM_CONFIGURATION_INCOMPLETE",
            "The upstream bridge is missing: " + ", ".join(missing),
        )
    iterator = _proxy_stream(payload) if upstream_ready else _local_not_ready_stream(payload["requestId"])
    headers = _no_store_headers()
    headers.update(
        {
            "X-SWRLZ-Stream-Contract": STREAM_CONTRACT,
            "X-SWRLZ-Request-Id": payload["requestId"],
            "X-Accel-Buffering": "no",
        },
    )
    return StreamingResponse(iterator, media_type="application/x-ndjson", headers=headers)


@app.get("/live", include_in_schema=False)
@app.get("/live/", include_in_schema=False)
async def live_root(request: Request):
    return _live_response(request, "")


@app.get("/live/{asset_path:path}", include_in_schema=False)
async def live_asset(request: Request, asset_path: str):
    return _live_response(request, asset_path)


@app.get("/", include_in_schema=False)
@app.get("/api/chat", include_in_schema=False)
async def chat_get(request: Request):
    action = request.query_params.get("action", "page").strip().lower()
    if action == "status":
        return JSONResponse(_status_payload(), headers=_no_store_headers())
    if action != "page":
        return _json_error(404, "CHAT_ACTION_NOT_FOUND", "Unknown chat action.")
    try:
        html = CHAT_PAGE.read_text("utf-8")
    except OSError:
        return _json_error(500, "CHAT_PAGE_MISSING", "web/chat.html is missing from the deployment bundle.")
    headers = _no_store_headers()
    headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    )
    return HTMLResponse(html, headers=headers)


@app.get("/status", include_in_schema=False)
@app.get("/api/chat/status", include_in_schema=False)
async def chat_status():
    return JSONResponse(_status_payload(), headers=_no_store_headers())


async def _post_action(request: Request, action: str):
    try:
        _require_web_token(request)
        payload = await _read_json(request)
        if action == "stream":
            return _stream_response(_normalize_chat_request(payload))
        if action == "cancel":
            request_id = _clean_request_id(payload.get("requestId"))
            status, result = _forward_cancel(request_id)
            return JSONResponse(result, status_code=status, headers=_no_store_headers())
        if action == "verify":
            return JSONResponse(_verify_r39(), headers=_no_store_headers())
        return _json_error(404, "CHAT_ACTION_NOT_FOUND", "Unknown chat action.")
    except BridgeError as exc:
        return _json_error(exc.status, exc.code, exc.detail)


@app.post("/", include_in_schema=False)
@app.post("/api/chat", include_in_schema=False)
async def chat_post(request: Request):
    return await _post_action(request, request.query_params.get("action", "stream").strip().lower())


@app.post("/stream", include_in_schema=False)
@app.post("/api/chat/stream", include_in_schema=False)
async def chat_stream(request: Request):
    return await _post_action(request, "stream")


@app.post("/cancel", include_in_schema=False)
@app.post("/api/chat/cancel", include_in_schema=False)
async def chat_cancel(request: Request):
    return await _post_action(request, "cancel")


@app.post("/verify", include_in_schema=False)
@app.post("/api/chat/verify", include_in_schema=False)
async def chat_verify(request: Request):
    return await _post_action(request, "verify")
