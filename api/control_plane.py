from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

import api.chat_extensions as chat_extensions
from api.chat_admin_session import _session_valid
from api.hot_loader import HOT_INFERENCE, HOT_ROOT, get_engine, invalidate_engine

ROOT = Path(__file__).resolve().parents[1]
BUNDLED_SERVER_PAGE = ROOT / "web" / "server.html"
BUNDLED_LALM_PAGE = ROOT / "web" / "lalm.html"
CONTROL_HOT = HOT_ROOT / "control"
HOT_SERVER_PAGE = CONTROL_HOT / "server.html"
HOT_LALM_PAGE = CONTROL_HOT / "lalm.html"
OWNER = "kaministrator999-ui"
REPO = "Swrlzkamico"
DEFAULT_BRANCH = "dev"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
SERVER_UI_VERSION = "1.0.0"
LALM_UI_VERSION = "1.0.0"

SCOPES = {
    "server": [("web/server.html", HOT_SERVER_PAGE, 1_000_000)],
    "lalm": [
        ("web/lalm.html", HOT_LALM_PAGE, 1_000_000),
        ("runtime_hot/r39_engine.py", HOT_INFERENCE, 4_000_000),
    ],
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fetch(branch: str, path: str, limit: int) -> bytes:
    req = urllib.request.Request(
        f"{RAW_BASE}/{branch}/{path}",
        headers={"User-Agent": "swrlz-control-plane-sync/1"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"CONTROL_SOURCE_TOO_LARGE:{path}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"CONTROL_SOURCE_BINARY_REJECTED:{path}")
    return data


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _page(hot: Path, bundled: Path) -> Path:
    return hot if hot.is_file() else bundled


def _request_chat_session(request: Request) -> str:
    return request.headers.get("x-swrlz-chat-session", "").strip()


def _authorized(server, request: Request, *, allow_chat_session: bool = False) -> bool:
    if server.auth(request):
        return True
    return allow_chat_session and _session_valid(_request_chat_session(request))


def _engine_receipt() -> dict[str, Any]:
    try:
        engine, source = get_engine()
        return {
            "available": True,
            "source": source,
            "engineId": str(getattr(engine, "ENGINE_ID", "")),
            "modelSha256": str(getattr(engine, "MODEL_SHA256", "")),
            "hotRevision": str(getattr(engine, "HOT_REVISION", "")),
            "hotServerVersion": str(getattr(engine, "HOT_SERVER_VERSION", "")),
        }
    except Exception as exc:
        return {
            "available": False,
            "source": "unavailable",
            "engineId": "",
            "modelSha256": "",
            "hotRevision": "",
            "hotServerVersion": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def _lalm_status(server) -> dict[str, Any]:
    try:
        from swyrlz import r39_native
        native_available = bool(r39_native.available())
    except Exception:
        native_available = False
    readiness = dict(chat_extensions.LOCAL_READINESS)
    return {
        "ok": True,
        "plane": "lalm",
        "uiVersion": LALM_UI_VERSION,
        "serverVersion": server.VERSION,
        "instanceId": server.INSTANCE,
        "engine": _engine_receipt(),
        "nativeBackendAvailable": native_available,
        "readiness": readiness,
        "modelFiles": server.lalm_presence(),
        "activeStreams": len(chat_extensions.ACTIVE),
        "statusProbeNonBlocking": True,
        "chatOwnsModelDiagnostics": False,
    }


def _server_status(server) -> dict[str, Any]:
    return {
        "ok": True,
        "plane": "server",
        "uiVersion": SERVER_UI_VERSION,
        "version": server.VERSION,
        "instanceId": server.INSTANCE,
        "startedAt": server.STARTED_AT,
        "uptimeSeconds": round(time.time() - server.STARTED_AT, 2),
        "deploymentCommit": os.environ.get("VERCEL_GIT_COMMIT_SHA", ""),
        "deploymentBranch": os.environ.get("VERCEL_GIT_COMMIT_REF", ""),
        "deploymentEnvironment": os.environ.get("VERCEL_ENV", ""),
        "capabilities": server.CAPABILITIES,
        "routes": {
            "server": "/server/",
            "lalm": "/lalm/",
            "chat": "/api/chat",
            "admin": "/api/admin",
            "legacyHot": "/api/hot",
            "scopedHot": "/api/control/hot/sync",
        },
        "hot": {
            "serverPageOverride": HOT_SERVER_PAGE.is_file(),
            "lalmPageOverride": HOT_LALM_PAGE.is_file(),
            "r39Override": HOT_INFERENCE.is_file(),
        },
    }


def install(server) -> None:
    CONTROL_HOT.mkdir(parents=True, exist_ok=True)
    server.CAPABILITIES["split-control-planes"] = {
        "kind": "control-plane",
        "ready": True,
        "serverPage": "/server/",
        "lalmPage": "/lalm/",
        "chatPage": "/api/chat",
        "chatFrozenForLalmWork": True,
    }
    server.CAPABILITIES["scoped-hot-sync"] = {
        "kind": "runtime-mutation",
        "ready": True,
        "endpoint": "/api/control/hot/sync",
        "scopes": ["server", "lalm", "all"],
        "lalmScopeTouchesChat": False,
    }

    @server.app.get("/server/", include_in_schema=False)
    @server.app.get("/server", include_in_schema=False)
    async def server_page():
        return FileResponse(
            _page(HOT_SERVER_PAGE, BUNDLED_SERVER_PAGE),
            media_type="text/html",
            headers={"Cache-Control": "no-store"},
        )

    @server.app.get("/lalm/", include_in_schema=False)
    @server.app.get("/lalm", include_in_schema=False)
    async def lalm_page():
        return FileResponse(
            _page(HOT_LALM_PAGE, BUNDLED_LALM_PAGE),
            media_type="text/html",
            headers={"Cache-Control": "no-store"},
        )

    @server.app.get("/api/server/status")
    async def server_status():
        return JSONResponse(_server_status(server), headers={"Cache-Control": "no-store"})

    @server.app.get("/api/lalm/status")
    async def lalm_status():
        return JSONResponse(_lalm_status(server), headers={"Cache-Control": "no-store"})

    @server.app.get("/api/control/route")
    async def route_client(request: Request):
        client = request.query_params.get("client", "chat").strip().lower()
        routes = {
            "chat": "/api/chat",
            "browser-chat": "/api/chat",
            "lalm": "/lalm/",
            "model": "/lalm/",
            "server": "/server/",
            "admin": "/api/admin",
        }
        target = routes.get(client, "/api/chat")
        return {
            "ok": True,
            "client": client,
            "target": target,
            "serverVersion": server.VERSION,
            "instanceId": server.INSTANCE,
            "plane": "chat" if target == "/api/chat" else "lalm" if target == "/lalm/" else "server",
        }

    @server.app.get("/route", include_in_schema=False)
    async def route_redirect(request: Request):
        client = request.query_params.get("client", "chat").strip().lower()
        target = {"lalm": "/lalm/", "server": "/server/", "admin": "/api/admin"}.get(client, "/api/chat")
        return RedirectResponse(target, status_code=307)

    @server.app.post("/api/control/hot/sync")
    async def scoped_hot_sync(request: Request):
        scope = request.query_params.get("scope", "lalm").strip().lower()
        branch = request.query_params.get("branch", DEFAULT_BRANCH).strip() or DEFAULT_BRANCH
        if scope not in {"server", "lalm", "all"}:
            return JSONResponse(status_code=400, content={"ok": False, "error": "scope must be server, lalm, or all"})
        if not all(ch.isalnum() or ch in "-._/" for ch in branch):
            return JSONResponse(status_code=400, content={"ok": False, "error": "invalid branch"})
        allow_chat_session = scope == "lalm"
        if not _authorized(server, request, allow_chat_session=allow_chat_session):
            return JSONResponse(status_code=401, content={"ok": False, "error": "authorization required", "scope": scope})
        selected = ["server", "lalm"] if scope == "all" else [scope]
        files: list[dict[str, Any]] = []
        try:
            payloads: list[tuple[str, Path, bytes]] = []
            for selected_scope in selected:
                for source, target, limit in SCOPES[selected_scope]:
                    data = _fetch(branch, source, limit)
                    payloads.append((source, target, data))
            for source, target, data in payloads:
                _atomic_write(target, data)
                files.append({"source": source, "target": str(target), "bytes": len(data), "sha256": _sha(data)})
            if any(target == HOT_INFERENCE for _, target, _ in payloads):
                invalidate_engine()
            server.activity("scoped-hot-sync", scope=scope, branch=branch, files=len(files))
            return {
                "ok": True,
                "scope": scope,
                "branch": branch,
                "files": files,
                "chatTouched": False,
                "serverPage": "/server/",
                "lalmPage": "/lalm/",
                "chat": "/api/chat",
            }
        except Exception as exc:
            return JSONResponse(status_code=502, content={"ok": False, "scope": scope, "branch": branch, "error": f"{type(exc).__name__}: {exc}"})

    @server.app.post("/api/lalm/verify")
    async def verify_lalm(request: Request):
        if not _authorized(server, request, allow_chat_session=True):
            return JSONResponse(status_code=401, content={"ok": False, "error": "authorization required"})
        try:
            engine, source = get_engine()
            state = engine.inspect_engine()
            chat_extensions.LOCAL_READINESS.clear()
            chat_extensions.LOCAL_READINESS.update({"checked": True, "engineSource": source, **state})
            return {"ok": True, "source": source, "engineId": str(engine.ENGINE_ID), "state": state}
        except Exception as exc:
            return JSONResponse(status_code=500, content={"ok": False, "error": f"{type(exc).__name__}: {exc}"})

    server._write_server_state()
