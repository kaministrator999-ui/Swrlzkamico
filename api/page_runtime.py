from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from api.hot_loader import HOT_CHAT

OWNER = "kaministrator999-ui"
REPO = "Swrlzkamico"
DEFAULT_BRANCH = "dev"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}"
ROOT = Path("/tmp/swrlz-admin")
WEB_ROOT = ROOT / "web"
SYSTEM_ROOT = WEB_ROOT / "system"
ADMIN_RUNTIME = SYSTEM_ROOT / "admin.html"
INDEX_RUNTIME = WEB_ROOT / "index.html"
GITHUB_TOKEN_FILE = ROOT / "runtime" / "github-content-token.txt"
BUNDLED_ROOT = Path(__file__).resolve().parents[1]
BUNDLED_ADMIN = BUNDLED_ROOT / "web" / "admin.html"
PAGE_BACKUPS = ROOT / "runtime" / "page-backups"

CORE: dict[str, dict[str, str]] = {
    "admin": {"source": "web/admin.html", "runtime": str(ADMIN_RUNTIME), "url": "/api/admin", "kind": "html"},
    "chat": {"source": "web/chat.html", "runtime": str(HOT_CHAT / "chat.html"), "url": "/api/chat", "kind": "html"},
    "chat-css": {"source": "web/chat_enhancements.css", "runtime": str(HOT_CHAT / "chat_enhancements.css"), "url": "/api/chat/assets/enhancements.css", "kind": "css"},
    "chat-js": {"source": "web/chat_enhancements.js", "runtime": str(HOT_CHAT / "chat_enhancements.js"), "url": "/api/chat/assets/enhancements.js", "kind": "js"},
    "index": {"source": "runtime_pages/index.html", "runtime": str(INDEX_RUNTIME), "url": "/live/", "kind": "html"},
}

ALLOWED_EXTRA_SUFFIXES = {".html", ".css", ".js", ".json", ".txt", ".md", ".svg"}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _fetch_raw(branch: str, source: str, limit: int = 4_000_000) -> bytes:
    url = f"{RAW_BASE}/{urllib.parse.quote(branch, safe='-._/')}/{urllib.parse.quote(source, safe='-._/')}"
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-page-runtime/1"})
    with urllib.request.urlopen(req, timeout=25) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"PAGE_SOURCE_TOO_LARGE:{source}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"PAGE_SOURCE_BINARY_REJECTED:{source}")
    return data


def _tree(branch: str) -> list[dict[str, Any]]:
    url = f"{API_BASE}/git/trees/{urllib.parse.quote(branch, safe='-._/')}?recursive=1"
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-page-runtime/1", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=25) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return list(payload.get("tree") or [])


def _extra_registry(branch: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    prefix = "runtime_pages/pages/"
    for item in _tree(branch):
        source = str(item.get("path") or "")
        if item.get("type") != "blob" or not source.startswith(prefix):
            continue
        rel = source[len(prefix):]
        if not rel or ".." in Path(rel).parts or Path(rel).suffix.lower() not in ALLOWED_EXTRA_SUFFIXES:
            continue
        key = "page:" + rel
        target = WEB_ROOT / "pages" / rel
        out[key] = {"source": source, "runtime": str(target), "url": "/live/pages/" + rel, "kind": Path(rel).suffix.lower().lstrip(".") or "file"}
    return out


def _registry(branch: str = DEFAULT_BRANCH, discover: bool = True) -> dict[str, dict[str, str]]:
    out = dict(CORE)
    if discover:
        try:
            out.update(_extra_registry(branch))
        except Exception:
            pass
    return out


def _runtime_info(key: str, item: dict[str, str]) -> dict[str, Any]:
    path = Path(item["runtime"])
    exists = path.is_file()
    data = path.read_bytes() if exists and path.stat().st_size <= 4_000_000 else b""
    return {"key": key, **item, "exists": exists, "size": path.stat().st_size if exists else None, "sha256": _sha(data) if data else None}


def _backup(registry: dict[str, dict[str, str]]) -> str | None:
    existing = [(key, Path(item["runtime"])) for key, item in registry.items() if Path(item["runtime"]).is_file()]
    if not existing:
        return None
    backup_id = time.strftime("%Y%m%d-%H%M%S")
    target = PAGE_BACKUPS / backup_id
    for key, source in existing:
        safe = key.replace(":", "__").replace("/", "_")
        dst = target / safe
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dst)
    return backup_id


def _github_token() -> str:
    try:
        runtime = GITHUB_TOKEN_FILE.read_text("utf-8").strip()
    except OSError:
        runtime = ""
    if runtime:
        return runtime
    return os.environ.get("SWRLZ_GITHUB_CONTENT_TOKEN", "").strip() or os.environ.get("SWRLZ_GITHUB_TOKEN", "").strip()


def _github_write(source: str, branch: str, data: bytes, message: str) -> dict[str, Any]:
    token = _github_token()
    if not token:
        raise RuntimeError("GITHUB_WRITE_TOKEN_NOT_CONFIGURED")
    content_url = f"{API_BASE}/contents/{urllib.parse.quote(source, safe='-._/')}?ref={urllib.parse.quote(branch, safe='-._/')}"
    headers = {"User-Agent": "swrlz-page-runtime/1", "Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}", "X-GitHub-Api-Version": "2022-11-28"}
    sha = None
    try:
        req = urllib.request.Request(content_url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            existing = json.loads(response.read().decode("utf-8"))
            sha = existing.get("sha")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
    body: dict[str, Any] = {"message": message, "content": base64.b64encode(data).decode("ascii"), "branch": branch}
    if sha:
        body["sha"] = sha
    put_url = f"{API_BASE}/contents/{urllib.parse.quote(source, safe='-._/')}"
    req = urllib.request.Request(put_url, data=json.dumps(body).encode("utf-8"), method="PUT", headers={**headers, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    return {"source": source, "branch": branch, "commit": (result.get("commit") or {}).get("sha"), "contentSha": (result.get("content") or {}).get("sha")}


def _manager_html() -> str:
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>§wyrlz Live Pages</title><style>body{margin:0;background:#050914;color:#eef7ff;font-family:system-ui}.wrap{max-width:1100px;margin:auto;padding:16px}.card{background:#0a1425;border:1px solid #284768;border-radius:16px;padding:14px;margin:10px 0}input,textarea,button,select{font:inherit}input,select,textarea{width:100%;background:#050c17;color:#fff;border:1px solid #315475;border-radius:10px;padding:9px}textarea{min-height:50vh;font-family:ui-monospace,monospace}button{background:#142943;color:#fff;border:1px solid #37618a;border-radius:10px;padding:9px 12px;font-weight:700}.row{display:flex;gap:8px;flex-wrap:wrap}.row>*{flex:1}.muted{color:#91aac4}.ok{color:#59f1a7}.entry{padding:9px;border-top:1px solid #203650}.entry a{color:#70eaff}.danger{border-color:#b94a5a;background:#481c28}</style></head><body><div class='wrap'><h1>§WYRLZ LIVE PAGE MANAGER</h1><p class='muted'>GitHub dev is durable source. Runtime copies are editable immediately. Updating dev does not deploy Vercel.</p><div class='card'><div class='row'><input id='admin' type='password' placeholder='Admin token'><button onclick='saveAdmin()'>SET ADMIN</button><button onclick='sync()'>SYNC DEV → RUNTIME</button></div><div class='row' style='margin-top:8px'><input id='gh' type='password' placeholder='Optional GitHub fine-grained content token'><button onclick='setGh()'>SET GITHUB WRITE TOKEN</button><button class='danger' onclick='clearGh()'>CLEAR TOKEN</button></div><pre id='out'>Ready.</pre></div><div class='card'><select id='pick' onchange='load()'></select><div class='row' style='margin:8px 0'><button onclick='load()'>LOAD RUNTIME</button><button onclick='saveRuntime()'>SAVE RUNTIME</button><button onclick='push()'>PUSH RUNTIME → DEV</button><button onclick='openPage()'>OPEN PAGE</button></div><textarea id='editor' spellcheck='false'></textarea></div><div class='card'><b>Pages</b><div id='pages'></div></div></div><script>let token=sessionStorage.getItem('swrlzAdminToken')||'';admin.value=token;let items=[];const headers=()=>({'x-swrlz-admin-token':token});async function call(action,key='',body=null){let r=await fetch('/api/pages?'+new URLSearchParams({action,key}),{method:'POST',headers:headers(),body});let j=await r.json();if(!r.ok)throw Error(JSON.stringify(j));return j}function show(x){out.textContent=typeof x==='string'?x:JSON.stringify(x,null,2)}function saveAdmin(){token=admin.value.trim();sessionStorage.setItem('swrlzAdminToken',token);refresh()}async function refresh(){try{let j=await call('list');items=j.pages||[];pick.innerHTML=items.map(x=>`<option value="${x.key}">${x.key} · ${x.source}</option>`).join('');pages.innerHTML=items.map(x=>`<div class="entry"><b>${x.key}</b> · <a href="${x.url}">${x.url}</a><br><span class="muted">${x.source} → ${x.runtime}</span></div>`).join('');show(j);if(items.length)load()}catch(e){show('FAILED '+e.message)}}async function sync(){try{show(await call('sync'));await refresh()}catch(e){show('FAILED '+e.message)}}async function load(){try{let j=await call('read',pick.value);editor.value=j.content||'';show(j.meta)}catch(e){show('FAILED '+e.message)}}async function saveRuntime(){try{show(await call('save-runtime',pick.value,new Blob([editor.value])));await refresh()}catch(e){show('FAILED '+e.message)}}async function push(){if(!confirm('Push this runtime file to dev source-of-truth?'))return;try{show(await call('push-dev',pick.value));await refresh()}catch(e){show('FAILED '+e.message)}}function openPage(){let x=items.find(x=>x.key===pick.value);if(x)window.open(x.url,'_blank')}async function setGh(){try{show(await call('github-token-set','',new Blob([gh.value.trim()])));gh.value=''}catch(e){show('FAILED '+e.message)}}async function clearGh(){try{show(await call('github-token-clear'))}catch(e){show('FAILED '+e.message)}}refresh();</script></body></html>"""


def install(server) -> None:
    SYSTEM_ROOT.mkdir(parents=True, exist_ok=True)
    HOT_CHAT.mkdir(parents=True, exist_ok=True)
    PAGE_BACKUPS.mkdir(parents=True, exist_ok=True)
    if not ADMIN_RUNTIME.is_file() and BUNDLED_ADMIN.is_file():
        shutil.copy2(BUNDLED_ADMIN, ADMIN_RUNTIME)
    server.ADMIN_PAGE = ADMIN_RUNTIME
    server.CAPABILITIES["live-page-runtime"] = {"kind": "runtime-mutation", "ready": True, "sourceBranch": DEFAULT_BRANCH, "manager": "/api/pages", "deployOnDev": False}
    server._write_server_state()

    def authorized(request: Request) -> bool:
        return server.auth(request)

    @server.app.get("/api/pages")
    async def page_manager():
        return HTMLResponse(_manager_html(), headers={"Cache-Control": "no-store"})

    @server.app.get("/api/pages/public")
    async def public_pages():
        pages = [_runtime_info(k, v) for k, v in _registry(DEFAULT_BRANCH).items()]
        return {"ok": True, "branch": DEFAULT_BRANCH, "pages": [{"key": x["key"], "url": x["url"], "kind": x["kind"], "exists": x["exists"]} for x in pages]}

    @server.app.post("/api/pages")
    async def page_action(request: Request, action: str = Query(...), key: str = Query(default="")):
        if not authorized(request):
            return JSONResponse(status_code=401, content={"ok": False, "error": "invalid or missing SWRLZ_ADMIN_TOKEN"})
        branch = DEFAULT_BRANCH
        registry = _registry(branch)
        try:
            if action == "list":
                return {"ok": True, "branch": branch, "githubWriteConfigured": bool(_github_token()), "pages": [_runtime_info(k, v) for k, v in registry.items()]}
            if action == "sync":
                backup_id = _backup(registry)
                fetched = []
                for name, item in registry.items():
                    data = _fetch_raw(branch, item["source"])
                    _atomic(Path(item["runtime"]), data)
                    fetched.append({"key": name, "source": item["source"], "runtime": item["runtime"], "bytes": len(data), "sha256": _sha(data)})
                server.ADMIN_PAGE = ADMIN_RUNTIME
                server.activity("page-runtime-sync", branch=branch, files=len(fetched), backupId=backup_id)
                return {"ok": True, "branch": branch, "files": fetched, "backupId": backup_id, "note": "dev branch sync does not trigger Vercel deployment"}
            if action in {"read", "save-runtime", "push-dev"}:
                if key not in registry:
                    return JSONResponse(status_code=404, content={"ok": False, "error": "unknown page key"})
                item = registry[key]
                path = Path(item["runtime"])
                if action == "read":
                    if not path.is_file():
                        return JSONResponse(status_code=404, content={"ok": False, "error": "runtime file missing; sync first"})
                    return {"ok": True, "meta": _runtime_info(key, item), "content": path.read_text("utf-8")}
                if action == "save-runtime":
                    body = await request.body()
                    if len(body) > 4_000_000:
                        return JSONResponse(status_code=413, content={"ok": False, "error": "page exceeds 4 MB runtime editor limit"})
                    body.decode("utf-8")
                    _atomic(path, body)
                    server.activity("page-runtime-save", key=key, path=str(path), size=len(body))
                    return {"ok": True, "page": _runtime_info(key, item), "durable": False}
                if not path.is_file():
                    return JSONResponse(status_code=404, content={"ok": False, "error": "runtime file missing"})
                data = path.read_bytes()
                result = _github_write(item["source"], branch, data, f"Hot page: update {key}")
                server.activity("page-runtime-push", key=key, branch=branch, source=item["source"])
                return {"ok": True, **result, "deployTriggered": False, "runtimeSha256": _sha(data)}
            if action == "github-token-set":
                value = (await request.body()).decode("utf-8").strip()
                if not (20 <= len(value) <= 512) or any(ord(c) < 32 or ord(c) == 127 for c in value):
                    raise ValueError("GitHub token must be 20..512 printable characters")
                GITHUB_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
                _atomic(GITHUB_TOKEN_FILE, value.encode("utf-8"))
                os.chmod(GITHUB_TOKEN_FILE, 0o600)
                server.activity("github-content-token-set", length=len(value))
                return {"ok": True, "configured": True, "source": "runtime", "valueExposed": False}
            if action == "github-token-clear":
                GITHUB_TOKEN_FILE.unlink(missing_ok=True)
                server.activity("github-content-token-clear")
                return {"ok": True, "configured": bool(_github_token()), "fallback": "environment"}
            return JSONResponse(status_code=400, content={"ok": False, "error": "unknown action"})
        except Exception as exc:
            return JSONResponse(status_code=500, content={"ok": False, "error": f"{type(exc).__name__}: {exc}"})
