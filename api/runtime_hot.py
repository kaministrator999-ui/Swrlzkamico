from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

from api.hot_loader import (
    HOT_CHAT,
    HOT_CHAT_HISTORY_POLICY,
    HOT_INFERENCE,
    HOT_ROOT,
    HOT_SERVER_DIR,
    invalidate_chat_history_policy,
    invalidate_engine,
    register_hot_refresher,
)

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
    "chat_history_policy.py": ("runtime_hot/chat_history_policy.py", HOT_CHAT_HISTORY_POLICY, 512_000),
}

AUTO_SYNC_SECONDS = 30.0
AUTO_SYNC_FAILURE_RETRY_SECONDS = 5.0
LAST_SYNC: dict[str, Any] = {"attemptAt": None, "successAt": None, "changed": [], "error": None}
_AUTO_SYNC_LOCK = threading.Lock()
_LAST_AUTO_SYNC_MONOTONIC = 0.0
_LAST_AUTO_RESULT: dict[str, Any] = {"ok": True, "changed": False, "branch": DEFAULT_BRANCH, "files": [], "reason": "not-yet-run"}


def _trace(stage: str, **fields) -> None:
    try:
        from api.chat_client_debug import _lockdown
        _lockdown("hot-runtime-" + stage, request_id=str(fields.pop("requestId", "") or ""), **fields)
    except Exception:
        pass


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _resolve_runtime_head() -> str:
    # Resolve the mutable runtime branch once through GitHub's API. Fetching
    # raw.githubusercontent.com by branch name can return an older CDN view even
    # with query cache-busters; immutable commit-SHA URLs cannot drift.
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/commits/{DEFAULT_BRANCH}?swrlz_runtime={int(time.time() * 1000)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "swrlz-hot-runtime/6",
            "Accept": "application/vnd.github+json",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.loads(response.read(262145).decode("utf-8"))
    sha = str(payload.get("sha") or "").strip().lower()
    if len(sha) != 40 or any(ch not in "0123456789abcdef" for ch in sha):
        _trace("resolve-head-invalid", value=sha)
        raise ValueError("HOT_RUNTIME_HEAD_INVALID")
    _trace("resolve-head-exit", branch=DEFAULT_BRANCH, runtimeHead=sha)
    return sha


def _fetch(path: str, limit: int, *, ref: str) -> bytes:
    url = f"{RAW_BASE}/{ref}/{path}"
    started=time.perf_counter_ns()
    _trace("source-fetch-enter", sourcePath=path, ref=ref, limit=limit)
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-hot-runtime/6"})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"HOT_SOURCE_TOO_LARGE:{path}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"HOT_SOURCE_BINARY_REJECTED:{path}")
    _trace("source-fetch-exit", sourcePath=path, ref=ref, bytes=len(data), sha256=_sha(data), durationNs=time.perf_counter_ns()-started)
    return data

def _atomic_write(path: Path, data: bytes) -> None:
    started=time.perf_counter_ns()
    _trace("atomic-write-enter", targetPath=str(path), bytes=len(data), sha256=_sha(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    _trace("atomic-write-exit", targetPath=str(path), durationNs=time.perf_counter_ns()-started)


def _backup() -> str | None:
    if not HOT_ROOT.exists() or not any(HOT_ROOT.rglob("*")):
        return None
    backup_id = time.strftime("%Y%m%d-%H%M%S")
    target = HOT_BACKUPS / backup_id
    target.mkdir(parents=True, exist_ok=True)
    for child in (HOT_CHAT, HOT_INFERENCE.parent, HOT_SERVER_DIR):
        if child.exists():
            shutil.copytree(child, target / child.name, dirs_exist_ok=True)
    return backup_id


def _runtime_status() -> dict[str, Any]:
    return {name: {"path": str(target), "exists": target.is_file(), "sha256": _sha(target.read_bytes()) if target.is_file() else None} for name, (_source, target, _limit) in SOURCES.items()}


def _fetch_source_item(item: tuple[str, tuple[str, Path, int]], ref: str) -> tuple[str, Path, bytes, str]:
    name, (source, target, limit) = item
    data = _fetch(source, limit, ref=ref)
    return name, target, data, _sha(data)


def _sync_runtime(*, force: bool = False, reason: str = "automatic") -> dict[str, Any]:
    sync_started=time.perf_counter_ns()
    _trace("sync-enter", force=force, reason=reason)
    LAST_SYNC["attemptAt"] = time.time()
    items = list(SOURCES.items())
    runtime_head = _resolve_runtime_head()
    _trace("sync-head-ready", runtimeHead=runtime_head, sourceCount=len(items))
    # Resolve one branch head, then fetch every source from that same immutable
    # snapshot so a sync cannot mix revisions across files.
    with ThreadPoolExecutor(max_workers=max(1, min(6, len(items))), thread_name_prefix="swrlz-hot-fetch") as pool:
        fetched = list(pool.map(lambda item: _fetch_source_item(item, runtime_head), items))
    _trace("sync-fetch-all-complete", runtimeHead=runtime_head, fetched=[{"name":n,"target":str(t),"bytes":len(d),"sha256":s} for n,t,d,s in fetched])

    payloads = []
    for name, target, data, digest in fetched:
        current = _sha(target.read_bytes()) if target.is_file() else None
        if force or digest != current:
            payloads.append((name, target, data, digest))
    if not payloads:
        _trace("sync-no-change", runtimeHead=runtime_head, durationNs=time.perf_counter_ns()-sync_started)
        LAST_SYNC["successAt"] = time.time()
        LAST_SYNC["changed"] = []
        LAST_SYNC["error"] = None
        return {"ok": True, "changed": False, "branch": DEFAULT_BRANCH, "runtimeHead": runtime_head, "files": [], "reason": reason, "parallelFetch": True}
    backup_id = _backup()
    _trace("sync-backup", backupId=backup_id or "", changedCount=len(payloads))
    changed = []
    engine_changed = False
    history_policy_changed = False
    for name, target, data, digest in payloads:
        _trace("sync-file-change-enter", name=name, targetPath=str(target), bytes=len(data), sha256=digest)
        _atomic_write(target, data)
        _trace("sync-file-change-exit", name=name, targetPath=str(target), sha256=digest)
        changed.append({"name": name, "path": str(target), "bytes": len(data), "sha256": digest})
        engine_changed = engine_changed or target == HOT_INFERENCE
        history_policy_changed = history_policy_changed or target == HOT_CHAT_HISTORY_POLICY
    if engine_changed:
        _trace("engine-invalidate-enter")
        invalidate_engine()
        _trace("engine-invalidate-exit")
    if history_policy_changed:
        _trace("history-policy-invalidate-enter")
        invalidate_chat_history_policy()
        _trace("history-policy-invalidate-exit")
    _ensure_portal()
    LAST_SYNC["successAt"] = time.time()
    LAST_SYNC["changed"] = [item["name"] for item in changed]
    LAST_SYNC["error"] = None
    return {"ok": True, "changed": True, "branch": DEFAULT_BRANCH, "runtimeHead": runtime_head, "files": changed, "backupId": backup_id, "reason": reason, "parallelFetch": True}


def _safe_auto_sync(server, *, force: bool = False) -> dict[str, Any]:
    global _LAST_AUTO_SYNC_MONOTONIC, _LAST_AUTO_RESULT
    enabled = os.environ.get("SWRLZ_HOT_AUTO_SYNC", "1").strip().lower() not in {"0", "false", "no", "off"}
    if not enabled:
        return {"ok": True, "enabled": False, "changed": False, "branch": DEFAULT_BRANCH}

    now = time.monotonic()
    if not force and _LAST_AUTO_SYNC_MONOTONIC and now - _LAST_AUTO_SYNC_MONOTONIC < AUTO_SYNC_SECONDS:
        return {**_LAST_AUTO_RESULT, "enabled": True, "throttled": True, "nextRefreshInSeconds": round(max(0.0, AUTO_SYNC_SECONDS - (now - _LAST_AUTO_SYNC_MONOTONIC)), 3)}

    acquired = _AUTO_SYNC_LOCK.acquire(blocking=force)
    if not acquired:
        return {**_LAST_AUTO_RESULT, "enabled": True, "throttled": True, "refreshInProgress": True}
    try:
        now = time.monotonic()
        if not force and _LAST_AUTO_SYNC_MONOTONIC and now - _LAST_AUTO_SYNC_MONOTONIC < AUTO_SYNC_SECONDS:
            return {**_LAST_AUTO_RESULT, "enabled": True, "throttled": True, "nextRefreshInSeconds": round(max(0.0, AUTO_SYNC_SECONDS - (now - _LAST_AUTO_SYNC_MONOTONIC)), 3)}
        _LAST_AUTO_SYNC_MONOTONIC = now
        try:
            result = _sync_runtime(force=force, reason="manual" if force else "automatic")
            _LAST_AUTO_RESULT = result
            if result.get("changed"):
                server.activity("hot-auto-sync", branch=DEFAULT_BRANCH, files=len(result.get("files") or []), changed=[x["name"] for x in result.get("files") or []])
            return {**result, "enabled": True, "throttled": False}
        except Exception as exc:
            LAST_SYNC["error"] = f"{type(exc).__name__}: {exc}"
            # Retry failed refreshes sooner than the normal successful refresh cadence.
            _LAST_AUTO_SYNC_MONOTONIC = time.monotonic() - AUTO_SYNC_SECONDS + AUTO_SYNC_FAILURE_RETRY_SECONDS
            _LAST_AUTO_RESULT = {"ok": False, "changed": False, "branch": DEFAULT_BRANCH, "error": LAST_SYNC["error"]}
            server.activity("hot-auto-sync-failed", branch=DEFAULT_BRANCH, error=LAST_SYNC["error"])
            return {**_LAST_AUTO_RESULT, "enabled": True, "throttled": False, "retryInSeconds": AUTO_SYNC_FAILURE_RETRY_SECONDS}
    finally:
        _AUTO_SYNC_LOCK.release()


def _portal_html() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>§wyrlz Runtime Index</title><style>body{font-family:system-ui;background:#050914;color:#eef7ff;margin:0;padding:20px}a{color:#7ee8ff;text-decoration:none}.card{background:#0b1426;border:1px solid #274362;border-radius:16px;padding:16px;margin:12px 0}.muted{color:#93aac0}button,input{font:inherit}button{background:#13243d;color:#fff;border:1px solid #315478;border-radius:10px;padding:10px 12px;margin:4px}input{width:100%;padding:10px;border-radius:10px;border:1px solid #315478;background:#06101d;color:white}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#040914;border:1px solid #1e3856;border-radius:12px;padding:12px}</style></head><body><h1>§WYRLZ Runtime Index</h1><p class='muted'>Durable application source: <code>runtime</code>. Runtime page, LALM, and allowlisted Server-policy changes are hydrated on request; deployment/restart is not part of the application update path once the stable loader ABI is present.</p><div class='card'><b>Hot Runtime</b><p>Chat UI, R39 runtime, and allowlisted Server history policy follow the runtime branch.</p><input id='adm' type='password' placeholder='SWRLZ_ADMIN_TOKEN'><button onclick='syncHot()'>SYNC NOW</button><button onclick='hotStatus()'>STATUS</button><pre id='hotOut'>Not checked.</pre></div><div class='card'><b>Live pages</b><div id='pages'>Loading…</div></div><script>const adm=document.querySelector('#adm'),out=document.querySelector('#hotOut'),pages=document.querySelector('#pages');adm.value=sessionStorage.getItem('swrlzAdminToken')||'';adm.onchange=()=>sessionStorage.setItem('swrlzAdminToken',adm.value.trim());async function req(path,method='GET'){const r=await fetch(path,{method,headers:{'x-swrlz-admin-token':adm.value.trim()},cache:'no-store'}),t=await r.text();try{out.textContent=JSON.stringify(JSON.parse(t),null,2)}catch{out.textContent=t}}async function syncHot(){await req('/api/hot/sync','POST');location.reload()}async function hotStatus(){await req('/api/hot/status')}fetch('/api/hot/pages',{cache:'no-store'}).then(r=>r.json()).then(j=>pages.innerHTML=(j.pages||[]).map(x=>`<div><a href="${x.url}">${x.relative}</a> <span class='muted'>${x.size} B</span></div>`).join('')||'No additional pages.').catch(e=>pages.textContent='Page discovery failed: '+e);hotStatus();</script></body></html>"""


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
    register_hot_refresher(lambda force=False: _safe_auto_sync(server, force=force))
    server.CAPABILITIES["hot-runtime"] = {"kind": "runtime-mutation", "ready": True, "sourceBranch": DEFAULT_BRANCH, "autoSync": True, "strategy": "30s gated parallel runtime hydration; request-path callers share one refresh authority"}
    server.CAPABILITIES["hot-chat-ui"] = {"kind": "runtime-mutation", "ready": True, "fallback": "bundled", "assets": ["chat.html", "chat_enhancements.css", "chat_enhancements.js", "chat_stream_focus.js"]}
    server.CAPABILITIES["hot-r39-engine"] = {"kind": "runtime-execution", "ready": True, "fallback": "bundled", "reload": "content-hash invalidation", "workerRefreshSeconds": int(AUTO_SYNC_SECONDS)}
    server.CAPABILITIES["hot-server-history-policy"] = {"kind": "runtime-server-policy", "ready": True, "authority": "server-owned-records", "sourceBranch": DEFAULT_BRANCH, "fallback": "bundled-canonical-history", "reload": "content-hash invalidation", "workerRefreshSeconds": int(AUTO_SYNC_SECONDS), "readOnly": True}
    server._write_server_state()

    @server.app.middleware("http")
    async def runtime_hydration(request: Request, call_next):
        # Generation is initiated by POST /api/chat[/]. Hydrating only GET meant
        # a user could submit inference against a stale R39 entrypoint before any
        # page/status GET happened to refresh the worker. Refresh every chat
        # request method through the same throttled single-writer authority.
        if request.url.path == "/api/chat" or request.url.path.startswith("/api/chat/"):
            # A generation POST is an activation boundary: it must observe the
            # current runtime branch before inference. GET/status traffic may use
            # the ordinary worker-local throttle, but POST must not hide a newly
            # committed Brain runtime for up to AUTO_SYNC_SECONDS.
            _trace("middleware-sync-enter", requestId=request_id, force=request.method=="POST")
            sync_result=_safe_auto_sync(server, force=request.method == "POST")
            _trace("middleware-sync-exit", requestId=request_id, result=sync_result)
        _trace("middleware-call-next-enter", requestId=request_id, path=request.url.path)
        response=await call_next(request)
        _trace("middleware-call-next-exit", requestId=request_id, path=request.url.path, status=getattr(response,"status_code",None))
        return response

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
        result = _safe_auto_sync(server, force=True)
        status = 200 if result.get("ok") else 502
        return JSONResponse(status_code=status, content={**result, "chat": "/api/chat", "portal": "/live/"})

    @server.app.post("/api/hot/clear")
    async def hot_clear(request: Request):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        backup_id = _backup()
        if HOT_CHAT.exists():
            shutil.rmtree(HOT_CHAT, ignore_errors=True)
        if HOT_INFERENCE.parent.exists():
            shutil.rmtree(HOT_INFERENCE.parent, ignore_errors=True)
        if HOT_SERVER_DIR.exists():
            shutil.rmtree(HOT_SERVER_DIR, ignore_errors=True)
        invalidate_engine()
        invalidate_chat_history_policy()
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
        if (source / "server").exists():
            shutil.rmtree(HOT_SERVER_DIR, ignore_errors=True)
            shutil.copytree(source / "server", HOT_SERVER_DIR)
        invalidate_engine()
        invalidate_chat_history_policy()
        server.activity("hot-rollback", backupId=backup_id)
        return {"ok": True, "restored": backup_id}