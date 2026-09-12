"""Stable authenticated host for the runtime-owned frozen web collector.

The deployment boundary owns authentication and fixed source selection. The
collector implementation and its module version remain on the non-deploying
``runtime`` branch so compatible behavior can evolve without another deploy.
"""
from __future__ import annotations

import hashlib
import importlib.util
import inspect
import os
import sys
import threading
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response

OWNER = "kaministrator999-ui"
REPO = "Swrlzkamico"
BRANCH = "runtime"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
COLLECTOR_SOURCE = "runtime_hot/web_snapshot_collector.py"
VERSION_SOURCE = "versions/frozen-web-collector.txt"
MODULE_ID = "frozen-web-collector"
API_SCHEMA_VERSION = 1
MAX_SOURCE_BYTES = 900_000
MAX_VERSION_BYTES = 16_000
MAX_REQUEST_BYTES = 192_000
REFRESH_SECONDS = 2.0
HOT_DIR = Path("/tmp/swrlz-admin/runtime/hot/collector")
HOT_FILE = HOT_DIR / "web_snapshot_collector.py"

_LOCK = threading.RLock()
_CACHED_MODULE: ModuleType | None = None
_CACHED_CODE_SHA256 = ""
_CACHED_VERSION = "UNAVAILABLE"
_CACHED_VERSION_SHA256 = ""
_LAST_ATTEMPT_MONOTONIC = 0.0
_LAST_SUCCESS_AT: float | None = None
_LAST_ERROR: str | None = None


@dataclass(frozen=True)
class CollectorHostContext:
    """Narrow stable capabilities exposed to the runtime implementation."""

    module_id: str
    module_version: str
    module_sha256: str
    source_branch: str
    source_path: str
    version_source: str
    activity: Callable[..., None]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fetch(source: str, limit: int) -> bytes:
    encoded_branch = urllib.parse.quote(BRANCH, safe="-._/")
    encoded_source = urllib.parse.quote(source, safe="-._/")
    url = f"{RAW_BASE}/{encoded_branch}/{encoded_source}?swrlz_collector={int(time.time() * 1000)}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "swrlz-frozen-web-collector-host/1",
            "Cache-Control": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"COLLECTOR_RUNTIME_SOURCE_TOO_LARGE:{source}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"COLLECTOR_RUNTIME_BINARY_REJECTED:{source}")
    return data


def _parse_version(data: bytes) -> str:
    fields: dict[str, str] = {}
    for raw_line in data.decode("utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        fields[key.strip().upper()] = value.strip()
    if fields.get("ID") != MODULE_ID:
        raise RuntimeError("COLLECTOR_VERSION_AUTHORITY_ID_MISMATCH")
    version = fields.get("VERSION", "")
    if not version or version.upper() in {"UNKNOWN", "UNASSIGNED"}:
        raise RuntimeError("COLLECTOR_VERSION_AUTHORITY_UNASSIGNED")
    return version


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _load_module(code: bytes, digest: str) -> ModuleType:
    _atomic_write(HOT_FILE, code)
    module_name = f"swrlz_hot_frozen_web_collector_{digest[:16]}"
    spec = importlib.util.spec_from_file_location(module_name, HOT_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError("COLLECTOR_RUNTIME_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    if getattr(module, "MODULE_ID", None) != MODULE_ID:
        raise RuntimeError("COLLECTOR_RUNTIME_MODULE_ID_MISMATCH")
    if getattr(module, "API_SCHEMA_VERSION", None) != API_SCHEMA_VERSION:
        raise RuntimeError("COLLECTOR_RUNTIME_API_SCHEMA_MISMATCH")
    if not callable(getattr(module, "handle", None)):
        raise RuntimeError("COLLECTOR_RUNTIME_CONTRACT_MISSING:handle")
    if not callable(getattr(module, "inspect_module", None)):
        raise RuntimeError("COLLECTOR_RUNTIME_CONTRACT_MISSING:inspect_module")
    return module


def _receipt() -> dict[str, Any]:
    return {
        "moduleId": MODULE_ID,
        "moduleVersion": _CACHED_VERSION,
        "apiSchemaVersion": API_SCHEMA_VERSION,
        "source": "github-runtime",
        "sourceBranch": BRANCH,
        "sourcePath": COLLECTOR_SOURCE,
        "sourceSha256": _CACHED_CODE_SHA256 or None,
        "versionSource": VERSION_SOURCE,
        "versionSourceSha256": _CACHED_VERSION_SHA256 or None,
        "lastSuccessAt": _LAST_SUCCESS_AT,
        "lastError": _LAST_ERROR,
        "refreshSeconds": REFRESH_SECONDS,
        "deploymentRequiredForRuntimeChanges": False,
    }


def _refresh(force: bool = False) -> tuple[ModuleType, dict[str, Any]]:
    global _CACHED_MODULE, _CACHED_CODE_SHA256, _CACHED_VERSION
    global _CACHED_VERSION_SHA256, _LAST_ATTEMPT_MONOTONIC
    global _LAST_SUCCESS_AT, _LAST_ERROR

    now = time.monotonic()
    with _LOCK:
        if (
            not force
            and _CACHED_MODULE is not None
            and _LAST_ATTEMPT_MONOTONIC
            and now - _LAST_ATTEMPT_MONOTONIC < REFRESH_SECONDS
        ):
            return _CACHED_MODULE, _receipt()
        _LAST_ATTEMPT_MONOTONIC = now
        try:
            code = _fetch(COLLECTOR_SOURCE, MAX_SOURCE_BYTES)
            version_data = _fetch(VERSION_SOURCE, MAX_VERSION_BYTES)
            code_sha = _sha(code)
            version_sha = _sha(version_data)
            version = _parse_version(version_data)
            if _CACHED_MODULE is None or code_sha != _CACHED_CODE_SHA256:
                _CACHED_MODULE = _load_module(code, code_sha)
                _CACHED_CODE_SHA256 = code_sha
            _CACHED_VERSION = version
            _CACHED_VERSION_SHA256 = version_sha
            _LAST_SUCCESS_AT = time.time()
            _LAST_ERROR = None
        except Exception as exc:
            _LAST_ERROR = f"{type(exc).__name__}: {exc}"[:600]
            if _CACHED_MODULE is None:
                raise
        return _CACHED_MODULE, _receipt()


def _response_headers(receipt: dict[str, Any]) -> dict[str, str]:
    return {
        "Cache-Control": "no-store, max-age=0",
        "X-Content-Type-Options": "nosniff",
        "X-SWRLZ-Collector-Source": "github-runtime",
        "X-SWRLZ-Collector-Branch": BRANCH,
        "X-SWRLZ-Collector-Version": str(receipt.get("moduleVersion") or "unavailable"),
        "X-SWRLZ-Collector-SHA256": str(receipt.get("sourceSha256") or "unavailable"),
    }


def _readiness_payload(module: ModuleType, receipt: dict[str, Any]) -> dict[str, Any]:
    """Return non-sensitive module/storage facts for deployment probes."""

    details = module.inspect_module()
    if not isinstance(details, dict):
        raise RuntimeError("COLLECTOR_RUNTIME_INSPECTION_INVALID")
    raw_storage = details.get("storage")
    storage = raw_storage if isinstance(raw_storage, dict) else {}
    safe_storage = {
        key: storage.get(key)
        for key in (
            "backend",
            "configured",
            "access",
            "authoritativeState",
            "ephemeralTmpUsedAsAuthority",
        )
    }
    ready = bool(safe_storage.get("configured"))
    return {
        "ok": ready,
        "ready": ready,
        "module": {
            "id": details.get("moduleId"),
            "version": receipt.get("moduleVersion"),
            "apiSchemaVersion": details.get("apiSchemaVersion"),
            "stateSchemaVersion": details.get("stateSchemaVersion"),
        },
        "storage": safe_storage,
        "host": receipt,
    }


def install(server: Any) -> None:
    def record(event: str, **fields: Any) -> None:
        safe_fields = {
            key: value
            for key, value in fields.items()
            if key not in {"token", "authorization"}
        }
        server.activity(f"collector-{event}", **safe_fields)

    server.CAPABILITIES["frozen-web-collector-host"] = {
        "kind": "authenticated-runtime-execution-host",
        "ready": True,
        "endpoint": "/api/collector/*",
        "page": "/collector",
        "sourceBranch": BRANCH,
        "sourcePath": COLLECTOR_SOURCE,
        "versionSource": VERSION_SOURCE,
        "authentication": "SWRLZ admin token; checked by stable host on every operational request",
        "runtimeUpdate": "fixed allowlist, hash refresh, last-known-good in-worker fallback",
        "durableStorage": "private Vercel Blob",
        "deploymentRequiredForRuntimeChanges": False,
    }

    async def dispatch(request: Request, subpath: str = "status") -> Response:
        normalized = subpath.strip("/") or "status"
        if request.method == "GET" and normalized == "readiness":
            try:
                module, receipt = _refresh()
                response = JSONResponse(
                    content=_readiness_payload(module, receipt),
                    headers={"Cache-Control": "no-store"},
                )
                for key, value in _response_headers(receipt).items():
                    response.headers[key] = value
                return response
            except Exception as exc:
                record("readiness-failed", error=f"{type(exc).__name__}: {exc}"[:600])
                return JSONResponse(
                    status_code=503,
                    content={"ok": False, "ready": False, "error": "collector runtime unavailable"},
                    headers={"Cache-Control": "no-store"},
                )

        if not server.auth(request):
            return JSONResponse(
                status_code=401,
                content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"},
                headers={"Cache-Control": "no-store"},
            )

        content_length = request.headers.get("content-length", "").strip()
        if content_length:
            try:
                if int(content_length) > MAX_REQUEST_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={"ok": False, "error": "collector request body exceeds stable host limit"},
                    )
            except ValueError:
                return JSONResponse(status_code=400, content={"ok": False, "error": "invalid content-length"})
        if request.method == "POST" and len(await request.body()) > MAX_REQUEST_BYTES:
            return JSONResponse(
                status_code=413,
                content={"ok": False, "error": "collector request body exceeds stable host limit"},
            )

        try:
            module, receipt = _refresh(force=normalized == "host/refresh")
            context = CollectorHostContext(
                module_id=MODULE_ID,
                module_version=str(receipt["moduleVersion"]),
                module_sha256=str(receipt["sourceSha256"]),
                source_branch=BRANCH,
                source_path=COLLECTOR_SOURCE,
                version_source=VERSION_SOURCE,
                activity=record,
            )
            result = module.handle(request=request, path=normalized, context=context)
            if inspect.isawaitable(result):
                result = await result
            response = result if isinstance(result, Response) else JSONResponse(content=result)
            for key, value in _response_headers(receipt).items():
                response.headers[key] = value
            return response
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"[:600]
            record("host-failed", path=normalized[:120], error=error)
            return JSONResponse(
                status_code=503,
                content={
                    "ok": False,
                    "error": "collector runtime unavailable",
                    "detail": error,
                    "host": _receipt(),
                },
                headers={"Cache-Control": "no-store"},
            )

    @server.app.api_route("/api/collector", methods=["GET", "POST"], include_in_schema=False)
    async def collector_root(request: Request):
        return await dispatch(request, "status")

    @server.app.api_route("/api/collector/{subpath:path}", methods=["GET", "POST"], include_in_schema=False)
    async def collector_route(request: Request, subpath: str):
        return await dispatch(request, subpath)

    server._write_server_state()
