from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

from api.hot_loader import HOT_CHAT, HOT_INFERENCE, HOT_ROOT, invalidate_engine

OWNER = "kaministrator999-ui"
REPO = "Swrlzkamico"
DEFAULT_BRANCH = "dev"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
HOT_BACKUPS = HOT_ROOT / "backups"
WEB_ROOT = Path("/tmp/swrlz-admin/web")

SOURCES = {
    "chat.html": ("web/chat.html", HOT_CHAT / "chat.html", 2_000_000),
    "chat_enhancements.css": ("web/chat_enhancements.css", HOT_CHAT / "chat_enhancements.css", 512_000),
    "chat_enhancements.js": ("web/chat_enhancements.js", HOT_CHAT / "chat_enhancements.js", 1_000_000),
    "r39_engine.py": ("runtime_hot/r39_engine.py", HOT_INFERENCE, 4_000_000),
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fetch(branch: str, path: str, limit: int) -> bytes:
    url = f"{RAW_BASE}/{branch}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-hot-sync/1"})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"HOT_SOURCE_TOO_LARGE:{path}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"HOT_SOURCE_BINARY_REJECTED:{path}")
    return data


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _backup() -> str | None:
    if not HOT_ROOT.exists() or not any(HOT_ROOT.rglob("*")):
        return None
    backup_id = time.strftime("%Y%m%d-%H%M%S")
    target = HOT_BACKUPS / backup_id
    target.mkdir(parents=True, exist_ok=True)
    for child in (HOT_CHAT, HOT_INFERENCE.parent):
        if child.exists():
            shutil.copytree(child, target / child.name, dirs_exist_ok=True)
    return backup_id


def _portal_html() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>§wyrlz Runtime Index</title><style>body{font-family:system-ui;background:#050914;color:#eef7ff;margin:0;padding:24px}h1{color:#63e8ff}a{color:#7ee8ff;text-decoration:none}.card{background:#0b1426;border:1px solid #274362;border-radius:16px;padding:16px;margin:12px 0}.muted{color:#93aac0}button{background:#13243d;color:#fff;border:1px solid #315478;border-radius:10px;padding:10px 12px}</style></head><body><h1>§WYRLZ Runtime Index</h1><p class='muted'>Temporary live index. It discovers current pages from this runtime instance.</p><div id='core'></div><div id='pages'></div><script>const core=[['Admin','/api/admin'],['Chat','/api/chat'],['Health','/api/health'],['LALM','/api/lalm'],['Hot Runtime Status','/api/hot/status']];document.querySelector('#core').innerHTML='<div class="card"><b>Core</b><br>'+core.map(x=>`<a href="${x[1]}">${x[0]}</a>`).join('<br>')+'</div>';fetch('/api/hot/pages',{cache:'no-store'}).then(r=>r.json()).then(j=>{document.querySelector('#pages').innerHTML='<div class="card"><b>Live pages</b><br>'+((j.pages||[]).map(x=>`<a href="${x.url}">${x.relative}</a>`).join('<br>')||'No additional pages yet.')+'</div>'}).catch(e=>document.querySelector('#pages').textContent='Page discovery failed: '+e);</script></body></html>"""


def _ensure_portal() -> None:
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    _atomic_write(WEB_ROOT / "index.html", _portal_html().encode("utf-8"))


def _pages() -> list[dict[str, Any]]:
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    out = []
    for path in sorted(WEB_ROOT.rglob("*.html")):
        rel = path.relative_to(WEB_ROOT).as_posix()
        if rel == "index.html":
            continue
        out.append({"relative": rel, "url": "/live/" + rel, "size": path.stat().st_size})
    return out


def install(server) -> None:
    HOT_ROOT.mkdir(parents=True, exist_ok=True)
    HOT_BACKUPS.mkdir(parents=True, exist_ok=True)
    _ensure_portal()
    server.CAPABILITIES["hot-runtime"] = {"kind": "runtime-mutation", "ready": True, "sourceBranch": DEFAULT_BRANCH}
    server.CAPABILITIES["hot-chat-ui"] = {"kind": "runtime-mutation", "ready": True, "fallback": "bundled"}
    server.CAPABILITIES["hot-r39-engine"] = {"kind": "runtime-execution", "ready": True, "fallback": "bundled"}
    server._write_server_state()

    def authorized(request: Request) -> bool:
        return server.auth(request)

    @server.app.get("/api/hot/status")
    async def hot_status():
        return {"ok": True, "branch": DEFAULT_BRANCH, "chatOverride": (HOT_CHAT / "chat.html").is_file(), "inferenceOverride": HOT_INFERENCE.is_file(), "portal": "/live/", "pages": len(_pages())}

    @server.app.get("/api/hot/pages")
    async def hot_pages():
        _ensure_portal()
        return {"ok": True, "pages": _pages(), "portal": "/live/"}

    @server.app.post("/api/hot/sync")
    async def hot_sync(request: Request):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        branch = request.query_params.get("branch", DEFAULT_BRANCH).strip() or DEFAULT_BRANCH
        if not all(ch.isalnum() or ch in "-._/" for ch in branch):
            return JSONResponse(status_code=400, content={"ok": False, "error": "invalid branch"})
        backup_id = _backup()
        fetched = []
        try:
            payloads: list[tuple[str, Path, bytes]] = []
            for name, (source, target, limit) in SOURCES.items():
                data = _fetch(branch, source, limit)
                payloads.append((name, target, data))
            for name, target, data in payloads:
                _atomic_write(target, data)
                fetched.append({"name": name, "path": str(target), "bytes": len(data), "sha256": _sha(data)})
            invalidate_engine()
            _ensure_portal()
            server.activity("hot-sync", branch=branch, files=len(fetched), backupId=backup_id)
            return {"ok": True, "branch": branch, "files": fetched, "backupId": backup_id, "chat": "/api/chat", "portal": "/live/"}
        except Exception as exc:
            return JSONResponse(status_code=502, content={"ok": False, "error": f"{type(exc).__name__}: {exc}", "branch": branch, "backupId": backup_id})

    @server.app.post("/api/hot/clear")
    async def hot_clear(request: Request):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        backup_id = _backup()
        if HOT_CHAT.exists():
            shutil.rmtree(HOT_CHAT)
        if HOT_INFERENCE.parent.exists():
            shutil.rmtree(HOT_INFERENCE.parent)
        invalidate_engine()
        server.activity("hot-clear", backupId=backup_id)
        return {"ok": True, "fallback": "bundled", "backupId": backup_id}

    @server.app.post("/api/hot/rollback")
    async def hot_rollback(request: Request):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        backup_id = request.query_params.get("backupId", "").strip()
        if not backup_id or not all(ch.isalnum() or ch in "-._" for ch in backup_id):
            return JSONResponse(status_code=400, content={"ok": False, "error": "backupId required"})
        source = HOT_BACKUPS / backup_id
        if not source.is_dir():
            return JSONResponse(status_code=404, content={"ok": False, "error": "backup not found"})
        current_backup = _backup()
        if (source / "chat").exists():
            shutil.rmtree(HOT_CHAT, ignore_errors=True)
            shutil.copytree(source / "chat", HOT_CHAT)
        if (source / "inference").exists():
            shutil.rmtree(HOT_INFERENCE.parent, ignore_errors=True)
            shutil.copytree(source / "inference", HOT_INFERENCE.parent)
        invalidate_engine()
        server.activity("hot-rollback", backupId=backup_id, currentBackupId=current_backup)
        return {"ok": True, "restored": backup_id, "currentBackupId": current_backup}
