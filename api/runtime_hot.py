from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
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
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"
HOT_BACKUPS = HOT_ROOT / "backups"
HOT_REVISION = HOT_ROOT / "runtime-revision.json"
WEB_ROOT = Path("/tmp/swrlz-admin/web")

SOURCES = {
    "chat.html": ("web/chat.html", HOT_CHAT / "chat.html", 2_000_000),
    "chat_account.js": ("web/chat_account.js", HOT_CHAT / "chat_account.js", 1_000_000),
    "chat_enhancements.css": ("web/chat_enhancements.css", HOT_CHAT / "chat_enhancements.css", 512_000),
    "chat_enhancements.js": ("web/chat_enhancements.js", HOT_CHAT / "chat_enhancements.js", 1_000_000),
    "chat_stream_focus.js": ("web/chat_stream_focus.js", HOT_CHAT / "chat_stream_focus.js", 1_000_000),
    "r39_engine.py": ("runtime_hot/r39_engine.py", HOT_INFERENCE, 4_000_000),
}

_sync_lock = threading.RLock()
_revision_lock = threading.RLock()
_last_revision_check_at = 0.0
_last_revision_seen = ""
AUTO_SYNC_SECONDS = 30.0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _auto_sync_enabled() -> bool:
    raw = os.environ.get("SWRLZ_HOT_AUTO_SYNC", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _auto_sync_interval() -> float:
    try:
        value = float(os.environ.get("SWRLZ_HOT_AUTO_SYNC_INTERVAL_SECONDS", str(AUTO_SYNC_SECONDS)))
    except ValueError:
        value = AUTO_SYNC_SECONDS
    return min(300.0, max(5.0, value))


def _fetch(branch: str, path: str, limit: int) -> bytes:
    url = f"{RAW_BASE}/{branch}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-hot-sync/3"})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"HOT_SOURCE_TOO_LARGE:{path}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"HOT_SOURCE_BINARY_REJECTED:{path}")
    return data


def _branch_revision(branch: str = DEFAULT_BRANCH) -> str:
    url = f"{API_BASE}/git/ref/heads/{branch}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "swrlz-hot-revision/1",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    revision = str(((payload.get("object") or {}).get("sha")) or "").strip()
    if not revision:
        raise RuntimeError("HOT_RUNTIME_REVISION_UNAVAILABLE")
    return revision


def _read_active_revision() -> str:
    try:
        payload = json.loads(HOT_REVISION.read_text("utf-8"))
        return str(payload.get("revision") or "").strip()
    except (OSError, ValueError, TypeError):
        return ""


def _write_active_revision(branch: str, revision: str) -> None:
    _atomic_write(
        HOT_REVISION,
        json.dumps(
            {"branch": branch, "revision": revision, "updatedAt": time.time()},
            separators=(",", ":"),
        ).encode("utf-8"),
    )


def _runtime_ready() -> bool:
    return all(target.is_file() for _, (_, target, _) in SOURCES.items())


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


def _sync_branch(branch: str = DEFAULT_BRANCH, *, revision: str | None = None, reason: str = "manual") -> dict[str, Any]:
    if branch != DEFAULT_BRANCH:
        raise ValueError(f"HOT_BRANCH_LOCKED:{DEFAULT_BRANCH}")
    with _sync_lock:
        target_revision = revision or _branch_revision(branch)
        if target_revision == _read_active_revision() and _runtime_ready():
            return {"ok": True, "changed": False, "branch": branch, "revision": target_revision, "reason": reason, "files": []}
        backup_id = _backup()
        payloads: list[tuple[str, Path, bytes]] = []
        for name, (source, target, limit) in SOURCES.items():
            data = _fetch(branch, source, limit)
            payloads.append((name, target, data))
        fetched = []
        for name, target, data in payloads:
            _atomic_write(target, data)
            fetched.append({"name": name, "path": str(target), "bytes": len(data), "sha256": _sha(data)})
        _write_active_revision(branch, target_revision)
        invalidate_engine()
        _ensure_portal()
        return {
            "ok": True,
            "changed": True,
            "branch": branch,
            "revision": target_revision,
            "reason": reason,
            "files": fetched,
            "backupId": backup_id,
        }


def _auto_sync(server) -> dict[str, Any]:
    global _last_revision_check_at, _last_revision_seen
    if not _auto_sync_enabled():
        return {"ok": True, "enabled": False, "changed": False, "branch": DEFAULT_BRANCH}
    now = time.monotonic()
    with _revision_lock:
        if now - _last_revision_check_at < _auto_sync_interval() and _runtime_ready():
            return {"ok": True, "enabled": True, "changed": False, "branch": DEFAULT_BRANCH, "revision": _last_revision_seen or _read_active_revision(), "checked": False}
        _last_revision_check_at = now
        revision = _branch_revision(DEFAULT_BRANCH)
        _last_revision_seen = revision
        active = _read_active_revision()
        needs_sync = revision != active or not _runtime_ready()
    if not needs_sync:
        return {"ok": True, "enabled": True, "changed": False, "branch": DEFAULT_BRANCH, "revision": revision, "checked": True}
    result = _sync_branch(DEFAULT_BRANCH, revision=revision, reason="automatic")
    server.activity("hot-auto-sync", branch=DEFAULT_BRANCH, revision=revision, changed=bool(result.get("changed")), files=len(result.get("files") or []), backupId=result.get("backupId"))
    return {**result, "enabled": True, "checked": True}


def _portal_html() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>§wyrlz Runtime Index</title><style>body{font-family:system-ui;background:#050914;color:#eef7ff;margin:0;padding:20px}h1{color:#63e8ff;margin-bottom:4px}a{color:#7ee8ff;text-decoration:none}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card{background:#0b1426;border:1px solid #274362;border-radius:16px;padding:16px;margin:12px 0}.muted{color:#93aac0}button,input{font:inherit}button{background:#13243d;color:#fff;border:1px solid #315478;border-radius:10px;padding:10px 12px;margin:4px 4px 4px 0}button.hot{background:#4a3215;border-color:#e5a13b}button.danger{background:#4a1d29;border-color:#b94860}input{width:100%;padding:10px;border-radius:10px;border:1px solid #315478;background:#06101d;color:white}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#040914;border:1px solid #1e3856;border-radius:12px;padding:12px}</style></head><body><h1>§WYRLZ Runtime Index</h1><p class='muted'>Temporary launchpad + revision-aware hot-runtime controls. Current pages are discovered from this runtime instance.</p><div class='grid'><div class='card'><b>Core</b><div id='core'></div></div><div class='card'><b>Hot Runtime</b><p class='muted'>Chat UI + R39 runtime automatically follow the durable non-deploying <code>runtime</code> branch.</p><input id='adm' type='password' placeholder='SWRLZ_ADMIN_TOKEN'><div><button class='hot' onclick='syncHot()'>SYNC HOT FROM RUNTIME</button><button onclick='hotStatus()'>STATUS</button><button class='danger' onclick='clearHot()'>CLEAR → BUNDLED FALLBACK</button></div><pre id='hotOut'>Not checked.</pre></div></div><div class='card'><b>Live pages</b><div id='pages'>Loading…</div></div><script>const core=[['Admin','/api/admin'],['Chat','/api/chat'],['Hot Runtime Control','/api/hot'],['Health','/api/health'],['LALM','/api/lalm'],['Hot Runtime Status','/api/hot/status']];coreEl=document.querySelector('#core');coreEl.innerHTML=core.map(x=>`<div><a href="${x[1]}">${x[0]}</a></div>`).join('');adm.value=sessionStorage.getItem('swrlzAdminToken')||'';adm.onchange=()=>sessionStorage.setItem('swrlzAdminToken',adm.value.trim());async function req(path,method='GET'){const r=await fetch(path,{method,headers:{'x-swrlz-admin-token':adm.value.trim()},cache:'no-store'}),t=await r.text();let j;try{j=JSON.parse(t)}catch{j={raw:t}}hotOut.textContent=JSON.stringify(j,null,2);if(!r.ok)throw Error(t);return j}async function syncHot(){sessionStorage.setItem('swrlzAdminToken',adm.value.trim());await req('/api/hot/sync','POST');location.reload()}async function clearHot(){if(confirm('Clear runtime overrides and fall back to bundled Chat/R39?'))await req('/api/hot/clear','POST')}async function hotStatus(){await req('/api/hot/status')}fetch('/api/hot/pages',{cache:'no-store'}).then(r=>r.json()).then(j=>{pages.innerHTML=(j.pages||[]).map(x=>`<div><a href="${x.url}">${x.relative}</a> <span class="muted">${x.size} B</span></div>`).join('')||'No additional pages yet.'}).catch(e=>pages.textContent='Page discovery failed: '+e);hotStatus();</script></body></html>"""


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


def _control_html() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>§wyrlz Hot Runtime</title><style>body{font-family:system-ui;background:#050914;color:#eef7ff;padding:20px;max-width:760px;margin:auto}a{color:#72e6ff}button,input{font:inherit}input{width:100%;padding:11px;background:#06101d;color:#fff;border:1px solid #315478;border-radius:10px}button{padding:10px 12px;margin:8px 6px 0 0;background:#122741;color:#fff;border:1px solid #38638d;border-radius:10px}pre{background:#040914;border:1px solid #203a58;border-radius:12px;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere}</style></head><body><h1>Hot Runtime Control</h1><p><a href='/live/'>← Runtime Index</a> · <a href='/api/admin'>Admin</a> · <a href='/api/chat'>Chat</a></p><p>Chat UI + account controls + R39 runtime automatically follow the non-deploying <b>runtime</b> branch. Manual sync remains available as an explicit recovery/control action.</p><input id='t' type='password' placeholder='SWRLZ_ADMIN_TOKEN'><button onclick='go("sync")'>SYNC HOT FROM RUNTIME</button><button onclick='status()'>STATUS</button><button onclick='go("clear")'>CLEAR OVERRIDES</button><pre id='o'>Ready.</pre><script>t.value=sessionStorage.getItem('swrlzAdminToken')||'';async function call(url,method='GET'){sessionStorage.setItem('swrlzAdminToken',t.value.trim());let r=await fetch(url,{method,headers:{'x-swrlz-admin-token':t.value.trim()},cache:'no-store'}),x=await r.text();try{o.textContent=JSON.stringify(JSON.parse(x),null,2)}catch{o.textContent=x}}function go(a){call('/api/hot/'+a,'POST')}function status(){call('/api/hot/status')}status()</script></body></html>"""


def install(server) -> None:
    HOT_ROOT.mkdir(parents=True, exist_ok=True)
    HOT_BACKUPS.mkdir(parents=True, exist_ok=True)
    _ensure_portal()
    server.CAPABILITIES["hot-runtime"] = {"kind": "runtime-mutation", "ready": True, "sourceBranch": DEFAULT_BRANCH, "autoSync": True, "autoSyncIntervalSeconds": _auto_sync_interval()}
    server.CAPABILITIES["hot-chat-ui"] = {"kind": "runtime-mutation", "ready": True, "fallback": "bundled", "assets": sorted(k for k in SOURCES if k.startswith("chat_")) + ["chat.html"]}
    server.CAPABILITIES["hot-r39-engine"] = {"kind": "runtime-execution", "ready": True, "fallback": "bundled"}
    server._write_server_state()

    @server.app.middleware("http")
    async def revision_aware_hot_runtime(request: Request, call_next):
        path = request.url.path
        if request.method == "GET" and (path == "/api/chat" or path.startswith("/api/chat/")):
            try:
                _auto_sync(server)
            except Exception as exc:
                server.activity("hot-auto-sync-failed", branch=DEFAULT_BRANCH, error=f"{type(exc).__name__}: {exc}")
        return await call_next(request)

    def authorized(request: Request) -> bool:
        return server.auth(request)

    @server.app.get("/api/hot")
    async def hot_control():
        return HTMLResponse(_control_html(), headers={"Cache-Control": "no-store"})

    @server.app.get("/api/hot/status")
    async def hot_status():
        try:
            auto = _auto_sync(server)
        except Exception as exc:
            auto = {"ok": False, "enabled": _auto_sync_enabled(), "error": f"{type(exc).__name__}: {exc}", "branch": DEFAULT_BRANCH}
        return {"ok": True, "branch": DEFAULT_BRANCH, "autoSync": auto, "activeRevision": _read_active_revision(), "chatOverride": (HOT_CHAT / "chat.html").is_file(), "chatAccountOverride": (HOT_CHAT / "chat_account.js").is_file(), "inferenceOverride": HOT_INFERENCE.is_file(), "portal": "/live/", "control": "/api/hot", "pages": len(_pages())}

    @server.app.get("/api/hot/pages")
    async def hot_pages():
        _ensure_portal()
        return {"ok": True, "pages": _pages(), "portal": "/live/"}

    @server.app.post("/api/hot/sync")
    async def hot_sync(request: Request):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        try:
            result = _sync_branch(DEFAULT_BRANCH, reason="manual")
            server.activity("hot-sync", branch=DEFAULT_BRANCH, revision=result.get("revision"), changed=bool(result.get("changed")), files=len(result.get("files") or []), backupId=result.get("backupId"))
            return {**result, "chat": "/api/chat", "portal": "/live/", "control": "/api/hot"}
        except Exception as exc:
            return JSONResponse(status_code=502, content={"ok": False, "error": f"{type(exc).__name__}: {exc}", "branch": DEFAULT_BRANCH})

    @server.app.post("/api/hot/clear")
    async def hot_clear(request: Request):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        backup_id = _backup()
        if HOT_CHAT.exists():
            shutil.rmtree(HOT_CHAT)
        if HOT_INFERENCE.parent.exists():
            shutil.rmtree(HOT_INFERENCE.parent)
        HOT_REVISION.unlink(missing_ok=True)
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
        HOT_REVISION.unlink(missing_ok=True)
        invalidate_engine()
        server.activity("hot-rollback", backupId=backup_id, currentBackupId=current_backup)
        return {"ok": True, "restored": backup_id, "currentBackupId": current_backup}
