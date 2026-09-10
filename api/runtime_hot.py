from __future__ import annotations

import hashlib
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
DEFAULT_BRANCH = "runtime"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
HOT_BACKUPS = HOT_ROOT / "backups"
WEB_ROOT = Path("/tmp/swrlz-admin/web")

SOURCES = {
    "chat.html": ("web/chat.html", HOT_CHAT / "chat.html", 2_000_000),
    "chat_enhancements.css": ("web/chat_enhancements.css", HOT_CHAT / "chat_enhancements.css", 512_000),
    "chat_enhancements.js": ("web/chat_enhancements.js", HOT_CHAT / "chat_enhancements.js", 1_000_000),
    "chat_stream_focus.js": ("web/chat_stream_focus.js", HOT_CHAT / "chat_stream_focus.js", 1_000_000),
    "r39_engine.py": ("runtime_hot/r39_engine.py", HOT_INFERENCE, 4_000_000),
}

AUTO_SYNC_SECONDS = 30.0
LAST_SYNC: dict[str, Any] = {"attemptAt": None, "successAt": None, "changed": [], "error": None}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fetch(path: str, limit: int) -> bytes:
    url = f"{RAW_BASE}/{DEFAULT_BRANCH}/{path}?swrlz_runtime={int(time.time() * 1000)}"
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-hot-runtime/4", "Cache-Control": "no-cache"})
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


def _runtime_status() -> dict[str, Any]:
    return {name: {"path": str(target), "exists": target.is_file(), "sha256": _sha(target.read_bytes()) if target.is_file() else None} for name, (_source, target, _limit) in SOURCES.items()}


def _sync_runtime(*, force: bool = False, reason: str = "automatic") -> dict[str, Any]:
    LAST_SYNC["attemptAt"] = time.time()
    payloads = []
    for name, (source, target, limit) in SOURCES.items():
        data = _fetch(source, limit)
        digest = _sha(data)
        current = _sha(target.read_bytes()) if target.is_file() else None
        if force or digest != current:
            payloads.append((name, target, data, digest))
    if not payloads:
        LAST_SYNC["successAt"] = time.time()
        LAST_SYNC["changed"] = []
        LAST_SYNC["error"] = None
        return {"ok": True, "changed": False, "branch": DEFAULT_BRANCH, "files": [], "reason": reason}
    backup_id = _backup()
    changed = []
    engine_changed = False
    for name, target, data, digest in payloads:
        _atomic_write(target, data)
        changed.append({"name": name, "path": str(target), "bytes": len(data), "sha256": digest})
        engine_changed = engine_changed or target == HOT_INFERENCE
    if engine_changed:
        invalidate_engine()
    _ensure_portal()
    LAST_SYNC["successAt"] = time.time()
    LAST_SYNC["changed"] = [item["name"] for item in changed]
    LAST_SYNC["error"] = None
    return {"ok": True, "changed": True, "branch": DEFAULT_BRANCH, "files": changed, "backupId": backup_id, "reason": reason}


def _safe_auto_sync(server) -> dict[str, Any]:
    enabled = os.environ.get("SWRLZ_HOT_AUTO_SYNC", "1").strip().lower() not in {"0", "false", "no", "off"}
    if not enabled:
        return {"ok": True, "enabled": False, "changed": False, "branch": DEFAULT_BRANCH}
    try:
        result = _sync_runtime(reason="automatic")
        if result.get("changed"):
            server.activity("hot-auto-sync", branch=DEFAULT_BRANCH, files=len(result.get("files") or []), changed=[x["name"] for x in result.get("files") or []])
        return {**result, "enabled": True}
    except Exception as exc:
        LAST_SYNC["error"] = f"{type(exc).__name__}: {exc}"
        server.activity("hot-auto-sync-failed", branch=DEFAULT_BRANCH, error=LAST_SYNC["error"])
        return {"ok": False, "enabled": True, "changed": False, "branch": DEFAULT_BRANCH, "error": LAST_SYNC["error"]}


def _portal_html() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>§wyrlz Runtime Index</title><style>body{font-family:system-ui;background:#050914;color:#eef7ff;margin:0;padding:20px}a{color:#7ee8ff;text-decoration:none}.card{background:#0b1426;border:1px solid #274362;border-radius:16px;padding:16px;margin:12px 0}.muted{color:#93aac0}button,input{font:inherit}button{background:#13243d;color:#fff;border:1px solid #315478;border-radius:10px;padding:10px 12px;margin:4px}input{width:100%;padding:10px;border-radius:10px;border:1px solid #315478;background:#06101d;color:white}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#040914;border:1px solid #1e3856;border-radius:12px;padding:12px}</style></head><body><h1>§WYRLZ Runtime Index</h1><p class='muted'>Durable application source: <code>runtime</code>. Runtime page and LALM changes are hydrated on request; deployment/restart is not part of the application update path.</p><div class='card'><b>Hot Runtime</b><p>Chat UI, page assets, and R39 runtime follow the runtime branch.</p><input id='adm' type='password' placeholder='SWRLZ_ADMIN_TOKEN'><button onclick='syncHot()'>SYNC NOW</button><button onclick='hotStatus()'>STATUS</button><pre id='hotOut'>Not checked.</pre></div><div class='card'><b>Live pages</b><div id='pages'>Loading…</div></div><script>const adm=document.querySelector('#adm'),out=document.querySelector('#hotOut'),pages=document.querySelector('#pages');adm.value=sessionStorage.getItem('swrlzAdminToken')||'';adm.onchange=()=>sessionStorage.setItem('swrlzAdminToken',adm.value.trim());async function req(path,method='GET'){const r=await fetch(path,{method,headers:{'x-swrlz-admin-token':adm.value.trim()},cache:'no-store'}),t=await r.text();try{out.textContent=JSON.stringify(JSON.parse(t),null,2)}catch{out.textContent=t}}async function syncHot(){await req('/api/hot/sync','POST');location.reload()}async function hotStatus(){await req('/api/hot/status')}fetch('/api/hot/pages',{cache:'no-store'}).then(r=>r.json()).then(j=>pages.innerHTML=(j.pages||[]).map(x=>`<div><a href="${x.url}">${x.relative}</a> <span class='muted'>${x.size} B</span></div>`).join('')||'No additional pages.').catch(e=>pages.textContent='Page discovery failed: '+e);hotStatus();</script></body></html>"""


def _ensure_portal() -> None:
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    _atomic_write(WEB_ROOT / "index.html", _portal_html().encode("utf-8"))


def _pages() -> list[dict[str, Any]]:
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    out = []
    for path in sorted(WEB_ROOT.rglob("*.html")):
        rel = path.relative_to(WEB_ROOT).as_posix()
        if rel != "index.html":
            out.append({"relative": rel, "url": "/live/" + rel, "size": path.stat().st_size})
    return out


def _control_html() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>§wyrlz Hot Runtime</title></head><body style='font-family:system-ui;background:#050914;color:#eef7ff;padding:20px;max-width:760px;margin:auto'><h1>Hot Runtime Control</h1><p>Source: <b>runtime</b>. Changes are fetched directly from the durable runtime branch.</p><input id='t' type='password' placeholder='SWRLZ_ADMIN_TOKEN' style='width:100%;padding:10px;background:#06101d;color:#fff'><button onclick='call("/api/hot/sync","POST")'>SYNC RUNTIME</button><button onclick='call("/api/hot/status")'>STATUS</button><pre id='o'>Ready.</pre><script>const t=document.querySelector('#t'),o=document.querySelector('#o');t.value=sessionStorage.getItem('swrlzAdminToken')||'';async function call(u,m='GET'){sessionStorage.setItem('swrlzAdminToken',t.value.trim());const r=await fetch(u,{method:m,headers:{'x-swrlz-admin-token':t.value.trim()},cache:'no-store'});const x=await r.text();try{o.textContent=JSON.stringify(JSON.parse(x),null,2)}catch{o.textContent=x}}</script></body></html>"""


def install(server) -> None:
    HOT_ROOT.mkdir(parents=True, exist_ok=True)
    HOT_BACKUPS.mkdir(parents=True, exist_ok=True)
    _ensure_portal()
    server.CAPABILITIES["hot-runtime"] = {"kind": "runtime-mutation", "ready": True, "sourceBranch": DEFAULT_BRANCH, "autoSync": True, "strategy": "hash-driven raw-source hydration with disposable instance cache"}
    server.CAPABILITIES["hot-chat-ui"] = {"kind": "runtime-mutation", "ready": True, "fallback": "bundled", "assets": sorted(SOURCES)}
    server.CAPABILITIES["hot-r39-engine"] = {"kind": "runtime-execution", "ready": True, "fallback": "bundled", "reload": "content-hash invalidation"}
    server._write_server_state()

    @server.app.middleware("http")
    async def runtime_hydration(request: Request, call_next):
        if request.method == "GET" and (request.url.path == "/api/chat" or request.url.path.startswith("/api/chat/")):
            _safe_auto_sync(server)
        return await call_next(request)

    def authorized(request: Request) -> bool:
        return server.auth(request)

    @server.app.get("/api/hot")
    async def hot_control():
        return HTMLResponse(_control_html(), headers={"Cache-Control": "no-store"})

    @server.app.get("/api/hot/status")
    async def hot_status():
        auto = _safe_auto_sync(server)
        return {"ok": True, "branch": DEFAULT_BRANCH, "autoSync": auto, "lastSync": dict(LAST_SYNC), "runtime": _runtime_status(), "pages": len(_pages()), "portal": "/live/", "control": "/api/hot"}

    @server.app.get("/api/hot/pages")
    async def hot_pages():
        _ensure_portal()
        return {"ok": True, "pages": _pages(), "portal": "/live/"}

    @server.app.post("/api/hot/sync")
    async def hot_sync(request: Request):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        try:
            result = _sync_runtime(force=True, reason="manual")
            return {**result, "chat": "/api/chat", "portal": "/live/"}
        except Exception as exc:
            LAST_SYNC["error"] = f"{type(exc).__name__}: {exc}"
            return JSONResponse(status_code=502, content={"ok": False, "error": LAST_SYNC["error"], "branch": DEFAULT_BRANCH})

    @server.app.post("/api/hot/clear")
    async def hot_clear(request: Request):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        backup_id = _backup()
        if HOT_CHAT.exists():
            shutil.rmtree(HOT_CHAT, ignore_errors=True)
        if HOT_INFERENCE.parent.exists():
            shutil.rmtree(HOT_INFERENCE.parent, ignore_errors=True)
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
        if (source / "chat").exists():
            shutil.rmtree(HOT_CHAT, ignore_errors=True)
            shutil.copytree(source / "chat", HOT_CHAT)
        if (source / "inference").exists():
            shutil.rmtree(HOT_INFERENCE.parent, ignore_errors=True)
            shutil.copytree(source / "inference", HOT_INFERENCE.parent)
        invalidate_engine()
        server.activity("hot-rollback", backupId=backup_id)
        return {"ok": True, "restored": backup_id}
