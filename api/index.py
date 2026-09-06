from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from swyrlz.backend import LIVE, PACKED, RAW, ensure_r39, sha

VERSION = "2.0.7"
ROOT = Path("/tmp/swrlz-admin")
UP = ROOT / "uploads"
LOG = ROOT / "full-runtime.log"
for directory in (ROOT, LIVE, UP):
    directory.mkdir(parents=True, exist_ok=True)

INSTANCE = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
TOKEN = os.environ.get("SWRLZ_ADMIN_TOKEN", "").strip()
MAX_CHUNK = 3 * 1024 * 1024
DOWNLOAD_CHUNK = 3 * 1024 * 1024
DIRECT_DOWNLOAD_MAX = 4 * 1024 * 1024
MAX_TEXT_EDIT = 4 * 1024 * 1024
GATE5 = LIVE / "gate5_live.py"

app = FastAPI(title="§wyrlz Unified Server Workbench", version=VERSION)


def auth(request: Request) -> bool:
    supplied = request.headers.get("x-swrlz-admin-token", "").strip()
    return bool(TOKEN) and hmac.compare_digest(supplied, TOKEN)


def safe_path(value: str | None, default: Path = LIVE) -> Path:
    candidate = Path(value) if value else default
    resolved = candidate.resolve() if candidate.is_absolute() else (ROOT / candidate).resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise PermissionError("path outside /tmp/swrlz-admin")
    return resolved


def mime_for(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def text_candidate(path: Path, mime: str | None = None) -> bool:
    mime = mime or mime_for(path)
    if mime.startswith("text/") or mime in {"application/json", "application/javascript", "application/xml", "application/x-sh", "application/sql"}:
        return True
    return path.suffix.lower() in {".py", ".kt", ".kts", ".java", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".scss", ".json", ".md", ".txt", ".log", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env", ".sh", ".bat", ".ps1", ".sql", ".csv", ".gradle", ".properties"}


def file_info(path: Path) -> dict:
    stat = path.stat()
    mime = "inode/directory" if path.is_dir() else mime_for(path)
    return {
        "name": path.name,
        "path": str(path),
        "type": "directory" if path.is_dir() else "file",
        "size": stat.st_size,
        "modified": int(stat.st_mtime),
        "mime": mime,
        "editable": path.is_file() and text_candidate(path, mime) and stat.st_size <= MAX_TEXT_EDIT,
    }


def upload_meta_path(upload_id: str) -> Path:
    return UP / f"{upload_id}.json"


def append_log(text: str) -> None:
    with LOG.open("a", encoding="utf-8", errors="replace") as out:
        out.write(text)
        if not text.endswith("\n"):
            out.write("\n")


def lalm_presence() -> dict:
    return {
        "packedPresent": PACKED.is_file(),
        "packedSize": PACKED.stat().st_size if PACKED.is_file() else None,
        "rawPresent": RAW.is_file(),
        "rawSize": RAW.stat().st_size if RAW.is_file() else None,
        "rawPath": str(RAW),
    }


def preview(path: Path) -> dict:
    if not path.is_file():
        raise ValueError("not a file")
    info = file_info(path)
    if text_candidate(path, info["mime"]) and path.stat().st_size <= MAX_TEXT_EDIT:
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
            if "\x00" not in text:
                return {**info, "previewKind": "text", "content": text}
        except UnicodeDecodeError:
            pass
    with path.open("rb") as handle:
        raw = handle.read(4096)
    return {
        **info,
        "previewKind": "binary",
        "hex": raw.hex(" "),
        "previewBytes": len(raw),
        "sha256": sha(path) if path.stat().st_size <= 64 * 1024 * 1024 else None,
    }


def run_gate5() -> dict:
    state = ensure_r39()
    if not state.get("ok") or not state.get("modelReady"):
        return {"ok": False, "code": "R39_NOT_READY", "lalm": state}
    if not GATE5.is_file():
        return {"ok": False, "code": "GATE5_NOT_PRESENT", "detail": str(GATE5), "lalm": state}
    env = os.environ.copy()
    env.update({
        "SWRLZ_R39_PATH": str(RAW),
        "SWRLZ_LALM_PATH": str(RAW),
        "SWRLZ_R39_GZ_PATH": str(PACKED),
        "SWRLZ_LIVE_DIR": str(LIVE),
    })
    started = time.time()
    proc = subprocess.run(
        [sys.executable, str(GATE5)],
        cwd=str(LIVE),
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=240,
    )
    elapsed = round(time.time() - started, 3)
    append_log(f"\n=== GATE 5 {time.strftime('%Y-%m-%d %H:%M:%S')} instance={INSTANCE} rc={proc.returncode} elapsed={elapsed}s ===\n{proc.stdout}{proc.stderr}")
    return {
        "ok": proc.returncode == 0,
        "returnCode": proc.returncode,
        "elapsedSeconds": elapsed,
        "stdout": proc.stdout[-20000:],
        "stderr": proc.stderr[-20000:],
        "instanceId": INSTANCE,
        "modelPath": str(RAW),
        "lalm": state,
    }


PAGE = r'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>§wyrlz SERVER Workbench</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{font-family:system-ui,sans-serif;background:#080d15;color:#edf4ff;max-width:1050px;margin:auto;padding:18px}h1,h2{margin:.25em 0}.muted{color:#9fb0c8}.card{background:#101827;border:1px solid #2c3d58;border-radius:22px;padding:18px;margin:16px 0}.row{display:flex;flex-wrap:wrap;gap:9px;align-items:center}input,button,textarea{font:inherit}input{background:#0b1321;color:#fff;border:1px solid #405371;border-radius:12px;padding:11px}button{background:#1a2b42;color:#eaf5ff;border:1px solid #40577a;border-radius:12px;padding:11px 15px;font-weight:750;cursor:pointer}button.hot{background:#675d52}button.danger{background:#5c2630}button.good{background:#245a3f}#path{flex:1;min-width:240px}.bar{height:12px;background:#222c3a;border-radius:9px;overflow:hidden;margin:9px 0}.fill{height:100%;width:0;background:#71df9d}#files{margin-top:12px;border-top:1px solid #26364c}.entry{display:grid;grid-template-columns:1fr auto;gap:10px;padding:11px 6px;border-bottom:1px solid #243247;align-items:center}.entry button{padding:7px 10px}.name{overflow-wrap:anywhere}.meta{font-size:.82rem;color:#9fb0c8}textarea{width:100%;min-height:430px;background:#080f1c;color:#eef6ff;border:1px solid #405371;border-radius:14px;padding:14px;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre;overflow:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#080f1c;padding:13px;border-radius:14px;max-height:420px;overflow:auto}iframe,img,video,audio{max-width:100%;border-radius:12px}iframe{width:100%;height:520px;background:white}.badge{display:inline-block;background:#1c2a40;padding:4px 8px;border-radius:999px;margin:2px;font-size:.8rem}
</style></head><body><h1>§wyrlz SERVER Workbench <span class="badge">v2.0.7</span></h1><p class="muted">Unified Admin + R39 + Gate 5 runtime. Large downloads use response-safe chunks. Vercel /tmp remains ephemeral.</p>
<div class="card"><div class="row"><input id="tok" type="password" placeholder="SWRLZ_ADMIN_TOKEN" style="flex:1;min-width:240px"><button onclick="saveTok()">SET TOKEN</button><button onclick="runtime()">RUNTIME</button><button class="good" onclick="loadLalm()">LOAD / VERIFY LALM</button><button class="hot" onclick="runGate5()">🔥 RUN HOT GATE 5</button></div><pre id="status">Ready.</pre></div>
<div class="card"><h2>Files</h2><div class="row"><button onclick="up()">↑ UP ONE DIR</button><input id="path" value="/tmp/swrlz-admin/live"><button onclick="refresh()">GO / REFRESH</button><button onclick="newFolder()">NEW FOLDER</button></div><div class="row" style="margin-top:10px"><input id="fi" type="file" multiple style="flex:1"><button onclick="uploadAll()">UPLOAD ANY FILES</button></div><div class="bar"><div id="progress" class="fill"></div></div><div id="summary" class="muted"></div><div id="files"></div></div>
<div class="card"><h2>Viewer / Editor</h2><div id="selected" class="muted">No file selected.</div><div class="row" style="margin:10px 0"><button id="saveBtn" onclick="saveText()" disabled>SAVE TEXT</button><button id="downloadBtn" onclick="downloadSelected()" disabled>DOWNLOAD</button><button id="hashBtn" onclick="hashSelected()" disabled>SHA-256</button><button id="renameBtn" onclick="renameSelected()" disabled>RENAME</button><button id="deleteBtn" class="danger" onclick="deleteSelected()" disabled>DELETE</button></div><div class="bar"><div id="downloadProgress" class="fill"></div></div><div id="viewer"><pre>Select a file to preview it.</pre></div></div>
<div class="card"><h2>Runtime Log</h2><div class="row"><button onclick="loadLog()">OPEN FULL LOG</button><button onclick="downloadLog()">DOWNLOAD LOG</button></div><pre id="log">Log not loaded.</pre></div>
<script>
let token=sessionStorage.getItem('swrlzAdminToken')||'',selected=null,selectedMeta=null;const CHUNK=2*1024*1024;document.getElementById('tok').value=token;
async function saveTok(){token=document.getElementById('tok').value.trim();sessionStorage.setItem('swrlzAdminToken',token);try{let j=await api('auth-check');status(j);await refresh()}catch(e){status('FAILED: '+e.message)}}function status(x){document.getElementById('status').textContent=typeof x==='string'?x:JSON.stringify(x,null,2)}function esc(s){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}function fmt(n){if(n==null)return '—';let u=['B','KB','MB','GB'],i=0,v=n;while(v>=1024&&i<u.length-1){v/=1024;i++}return v.toFixed(i?2:0)+' '+u[i]}
async function api(action,q={},body=null,response='json'){const u='/api/admin?'+new URLSearchParams({action,...q});const r=await fetch(u,{method:'POST',headers:{'x-swrlz-admin-token':token},body});if(response==='blob'){if(!r.ok)throw Error(await r.text());return r.blob()}const j=await r.json();if(!r.ok)throw Error(j.error||j.detail||JSON.stringify(j));return j}
async function chunkRequest(path,instanceId,offset,length){const u='/api/admin?'+new URLSearchParams({action:'download-chunk',path,instanceId,offset,length});const r=await fetch(u,{method:'POST',headers:{'x-swrlz-admin-token':token}});if(!r.ok)throw Error(await r.text());return new Uint8Array(await r.arrayBuffer())}
async function downloadInfo(path){return api('download-info',{path})}
async function downloadBlobChunked(path){const info=await downloadInfo(path),parts=[];let off=0;while(off<info.size){const n=Math.min(info.chunkBytes,info.size-off),part=await chunkRequest(path,info.instanceId,off,n);parts.push(part);off+=part.byteLength;document.getElementById('downloadProgress').style.width=(off/info.size*100)+'%';status('Downloading '+info.name+' '+Math.floor(off/info.size*100)+'%')}document.getElementById('downloadProgress').style.width='0';return {blob:new Blob(parts,{type:info.mime}),info}}
async function saveChunked(path){const name=path.split('/').pop();let handle=null;if('showSaveFilePicker' in window){try{handle=await window.showSaveFilePicker({suggestedName:name})}catch(e){if(e.name==='AbortError')return}}const info=await downloadInfo(path);let off=0,parts=[],writable=handle?await handle.createWritable():null;try{while(off<info.size){const n=Math.min(info.chunkBytes,info.size-off),part=await chunkRequest(path,info.instanceId,off,n);if(writable)await writable.write(part);else parts.push(part);off+=part.byteLength;document.getElementById('downloadProgress').style.width=(off/info.size*100)+'%';status('Downloading '+info.name+' '+fmt(off)+' / '+fmt(info.size)+' ('+Math.floor(off/info.size*100)+'%)')}if(writable)await writable.close();else{const blob=new Blob(parts,{type:info.mime}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=info.name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),4000)}status('Download complete: '+info.name+' · '+fmt(info.size))}catch(e){if(writable)try{await writable.abort()}catch(_){ }throw e}finally{document.getElementById('downloadProgress').style.width='0'}}
async function runtime(){try{status(await api('runtime'))}catch(e){status('FAILED: '+e.message)}}function currentPath(){return document.getElementById('path').value.trim()}function up(){let p=currentPath().replace(/\/+$/,''),i=p.lastIndexOf('/');document.getElementById('path').value=i>0?p.slice(0,i):'/tmp/swrlz-admin';refresh()}
async function refresh(){try{let j=await api('list',{path:currentPath()});document.getElementById('path').value=j.path;document.getElementById('summary').textContent=j.entries.length+' entries · '+j.path;document.getElementById('files').innerHTML=j.entries.map(e=>`<div class="entry"><div class="name">${e.type==='directory'?'📁':'📄'} <b>${esc(e.name)}</b><div class="meta">${esc(e.type)} · ${fmt(e.size)} · ${esc(e.mime)}</div></div><button onclick='openEntry(${JSON.stringify(e.path)})'>OPEN</button></div>`).join('');return j}catch(e){status('FAILED: '+e.message);throw e}}
async function openEntry(path){try{let j=await api('preview',{path});if(j.type==='directory'){document.getElementById('path').value=j.path;return refresh()}selected=j.path;selectedMeta=j;document.getElementById('selected').textContent=j.path+' · '+fmt(j.size)+' · '+j.mime;for(const id of ['downloadBtn','hashBtn','renameBtn','deleteBtn'])document.getElementById(id).disabled=false;document.getElementById('saveBtn').disabled=j.previewKind!=='text';let v=document.getElementById('viewer');if(j.previewKind==='text'){v.innerHTML='<textarea id="editor"></textarea>';document.getElementById('editor').value=j.content}else if(j.mime.startsWith('image/'))await mediaPreview('img',j);else if(j.mime.startsWith('video/'))await mediaPreview('video',j);else if(j.mime.startsWith('audio/'))await mediaPreview('audio',j);else if(j.mime==='application/pdf')await mediaPreview('iframe',j);else v.innerHTML='<pre>'+esc('Binary file\n'+(j.sha256?'SHA-256: '+j.sha256+'\n':'')+'First '+j.previewBytes+' bytes:\n'+j.hex)+'</pre>'}catch(e){status('FAILED: '+e.message)}}
async function mediaPreview(tag,j){let d=await downloadBlobChunked(j.path),url=URL.createObjectURL(d.blob),v=document.getElementById('viewer');if(tag==='img')v.innerHTML=`<img src="${url}">`;else if(tag==='video')v.innerHTML=`<video controls src="${url}"></video>`;else if(tag==='audio')v.innerHTML=`<audio controls src="${url}"></audio>`;else v.innerHTML=`<iframe src="${url}"></iframe>`}
async function saveText(){try{let text=document.getElementById('editor').value;status(await api('save-text',{path:selected},new Blob([text],{type:'text/plain;charset=utf-8'})));refresh()}catch(e){status('FAILED: '+e.message)}}async function downloadSelected(){if(!selected)return;try{await saveChunked(selected)}catch(e){status('FAILED: '+e.message)}}async function hashSelected(){try{status(await api('hash',{path:selected}))}catch(e){status('FAILED: '+e.message)}}
async function renameSelected(){let n=prompt('New file name',selectedMeta?.name||'');if(!n)return;try{let j=await api('rename',{path:selected,newName:n});selected=j.path;status(j);refresh();openEntry(j.path)}catch(e){status('FAILED: '+e.message)}}async function deleteSelected(){if(!selected||!confirm('Delete '+selected+' ?'))return;try{status(await api('delete',{path:selected}));selected=null;selectedMeta=null;document.getElementById('viewer').innerHTML='<pre>Select a file to preview it.</pre>';refresh()}catch(e){status('FAILED: '+e.message)}}async function newFolder(){let n=prompt('Folder name');if(!n)return;try{status(await api('mkdir',{path:currentPath(),name:n}));refresh()}catch(e){status('FAILED: '+e.message)}}
async function one(file){let init=await api('upload-init',{path:currentPath(),name:file.name,size:file.size}),off=0;while(off<file.size){let end=Math.min(off+CHUNK,file.size),j=await api('upload-chunk',{uploadId:init.uploadId,offset:off,instanceId:init.instanceId},file.slice(off,end));off=j.received;document.getElementById('progress').style.width=(off/file.size*100)+'%';status(file.name+' '+Math.floor(off/file.size*100)+'%')}return api('upload-finish',{uploadId:init.uploadId,instanceId:init.instanceId})}async function uploadAll(){try{for(const f of document.getElementById('fi').files)status(await one(f));document.getElementById('progress').style.width='0';refresh()}catch(e){status('FAILED: '+e.message)}}
async function loadLalm(){try{status('Loading and verifying R39 in this runtime…');status(await api('lalm-load'));refresh()}catch(e){status('FAILED: '+e.message)}}async function runGate5(){try{status('Preparing R39 and running Gate 5 in the same invocation…');status(await api('gate5-run'));loadLog();refresh()}catch(e){status('FAILED: '+e.message)}}async function loadLog(){try{let j=await api('log-read');document.getElementById('log').textContent=j.content}catch(e){status('FAILED: '+e.message)}}async function downloadLog(){try{await saveChunked('/tmp/swrlz-admin/full-runtime.log')}catch(e){status('FAILED: '+e.message)}}refresh();
</script></body></html>'''


@app.get("/")
@app.get("/api")
def root():
    return {"ok": True, "service": "§wyrlz Unified Vercel Server", "version": VERSION, "health": "/api/health", "admin": "/api/admin", "lalm": "/api/lalm"}


@app.get("/api/health")
def health():
    return {"ok": True, "version": VERSION, "routingReady": True, "runtimeBoundary": "single-api-index", "instanceId": INSTANCE, "adminAuthConfigured": bool(TOKEN), **lalm_presence(), "storage": "Vercel /tmp is ephemeral and instance-local; Gate 5 loads/verifies R39 in the same invocation."}


@app.get("/api/lalm")
def lalm():
    try:
        state = ensure_r39()
        return JSONResponse(status_code=200 if state.get("ok") else 503, content={**state, "instanceId": INSTANCE})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"ok": False, "code": "R39_LOAD_FAILED", "detail": f"{type(exc).__name__}: {exc}", "instanceId": INSTANCE})


@app.get("/api/admin")
def admin_page():
    return HTMLResponse(PAGE)


@app.post("/api/admin")
async def admin_action(
    request: Request,
    action: str = Query(...),
    path: str | None = Query(default=None),
    name: str | None = Query(default=None),
    newName: str | None = Query(default=None),
    size: int | None = Query(default=None),
    uploadId: str | None = Query(default=None),
    offset: int = Query(default=0),
    length: int | None = Query(default=None),
    instanceId: str | None = Query(default=None),
):
    if not auth(request):
        supplied = request.headers.get("x-swrlz-admin-token", "").strip()
        return JSONResponse(status_code=401, content={
            "ok": False,
            "error": "invalid or missing SWRLZ_ADMIN_TOKEN",
            "authConfigured": bool(TOKEN),
            "tokenReceived": bool(supplied),
            "receivedLength": len(supplied),
            "instanceId": INSTANCE,
        })
    try:
        if action == "auth-check":
            return {"ok": True, "authenticated": True, "version": VERSION, "instanceId": INSTANCE, "message": "Admin token accepted."}
        if action == "runtime":
            return {"ok": True, "version": VERSION, "instanceId": INSTANCE, "root": str(ROOT), "live": str(LIVE), "uploadAuthConfigured": bool(TOKEN), "downloadChunkBytes": DOWNLOAD_CHUNK, **lalm_presence()}
        if action == "list":
            base = safe_path(path)
            if not base.exists(): raise FileNotFoundError(base)
            if not base.is_dir(): return {"ok": True, **file_info(base), "entries": []}
            entries = sorted((file_info(p) for p in base.iterdir()), key=lambda x: (x["type"] != "directory", x["name"].lower()))
            return {"ok": True, "path": str(base), "entries": entries, "instanceId": INSTANCE}
        if action == "preview":
            target = safe_path(path)
            if target.is_dir(): return {"ok": True, **file_info(target), "previewKind": "directory"}
            return {"ok": True, **preview(target), "instanceId": INSTANCE}
        if action == "download":
            target = safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            if target.stat().st_size > DIRECT_DOWNLOAD_MAX:
                return JSONResponse(status_code=413, content={"ok": False, "error": "file exceeds direct-download limit; use chunked download", "size": target.stat().st_size, "chunkBytes": DOWNLOAD_CHUNK})
            return FileResponse(target, media_type=mime_for(target), filename=target.name)
        if action == "download-info":
            target = safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            return {"ok": True, "name": target.name, "path": str(target), "size": target.stat().st_size, "mime": mime_for(target), "chunkBytes": DOWNLOAD_CHUNK, "instanceId": INSTANCE}
        if action == "download-chunk":
            if instanceId != INSTANCE:
                return JSONResponse(status_code=409, content={"ok": False, "error": "runtime instance changed; restart download", "instanceId": INSTANCE})
            target = safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            total = target.stat().st_size
            if offset < 0 or offset > total: raise ValueError("invalid download offset")
            wanted = DOWNLOAD_CHUNK if length is None else length
            if wanted <= 0 or wanted > DOWNLOAD_CHUNK: raise ValueError(f"download length must be 1..{DOWNLOAD_CHUNK}")
            wanted = min(wanted, total - offset)
            with target.open("rb") as handle:
                handle.seek(offset)
                body = handle.read(wanted)
            end = offset + len(body)
            headers = {
                "x-swrlz-instance-id": INSTANCE,
                "x-swrlz-offset": str(offset),
                "x-swrlz-next-offset": str(end),
                "x-swrlz-total-size": str(total),
                "content-range": f"bytes {offset}-{max(offset, end - 1)}/{total}",
                "accept-ranges": "bytes",
            }
            return Response(content=body, status_code=206, media_type="application/octet-stream", headers=headers)
        if action == "hash":
            target = safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            return {"ok": True, "path": str(target), "size": target.stat().st_size, "sha256": sha(target)}
        if action == "save-text":
            target = safe_path(path); body = await request.body()
            if len(body) > MAX_TEXT_EDIT: return JSONResponse(status_code=413, content={"ok": False, "error": "text file exceeds editor limit"})
            body.decode("utf-8"); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(body)
            return {"ok": True, **file_info(target), "sha256": sha(target)}
        if action == "mkdir":
            base = safe_path(path)
            if not name or Path(name).name != name: raise ValueError("simple folder name required")
            target = safe_path(str(base / name)); target.mkdir(parents=False, exist_ok=False)
            return {"ok": True, **file_info(target)}
        if action == "rename":
            target = safe_path(path)
            if not newName or Path(newName).name != newName: raise ValueError("simple newName required")
            renamed = safe_path(str(target.parent / newName)); target.rename(renamed)
            return {"ok": True, **file_info(renamed)}
        if action == "delete":
            target = safe_path(path)
            if target in {ROOT, LIVE, UP}: raise PermissionError("protected runtime directory")
            shutil.rmtree(target) if target.is_dir() else target.unlink()
            return {"ok": True, "deleted": str(target)}
        if action == "upload-init":
            if not name or Path(name).name != name or size is None or size < 0: raise ValueError("simple name and non-negative size required")
            base = safe_path(path); base.mkdir(parents=True, exist_ok=True); target = safe_path(str(base / name)); uid = uuid.uuid4().hex; part = UP / f"{uid}.part"; part.touch()
            metadata = {"uploadId": uid, "instanceId": INSTANCE, "target": str(target), "part": str(part), "expected": size, "received": 0}; upload_meta_path(uid).write_text(json.dumps(metadata), "utf-8")
            return {"ok": True, "uploadId": uid, "instanceId": INSTANCE, "chunkBytes": MAX_CHUNK}
        if action == "upload-chunk":
            if instanceId != INSTANCE: return JSONResponse(status_code=409, content={"ok": False, "error": "runtime instance changed; restart upload"})
            if not uploadId: raise ValueError("uploadId required")
            metadata = json.loads(upload_meta_path(uploadId).read_text("utf-8")); body = await request.body()
            if len(body) > MAX_CHUNK: return JSONResponse(status_code=413, content={"ok": False, "error": "chunk too large"})
            if offset != metadata["received"]: return JSONResponse(status_code=409, content={"ok": False, "error": "offset mismatch", "received": metadata["received"]})
            with Path(metadata["part"]).open("ab") as out: out.write(body)
            metadata["received"] += len(body); upload_meta_path(uploadId).write_text(json.dumps(metadata), "utf-8")
            return {"ok": True, "received": metadata["received"], "expected": metadata["expected"], "instanceId": INSTANCE}
        if action == "upload-finish":
            if instanceId != INSTANCE: return JSONResponse(status_code=409, content={"ok": False, "error": "runtime instance changed; restart upload"})
            if not uploadId: raise ValueError("uploadId required")
            metadata = json.loads(upload_meta_path(uploadId).read_text("utf-8")); part = Path(metadata["part"]); target = safe_path(metadata["target"])
            if metadata["received"] != metadata["expected"] or part.stat().st_size != metadata["expected"]: return JSONResponse(status_code=409, content={"ok": False, "error": "upload incomplete"})
            os.replace(part, target); upload_meta_path(uploadId).unlink(missing_ok=True)
            return {"ok": True, **file_info(target), "sha256": sha(target), "instanceId": INSTANCE}
        if action == "lalm-load":
            state = ensure_r39(); return JSONResponse(status_code=200 if state.get("ok") else 503, content={**state, "instanceId": INSTANCE})
        if action == "gate5-run":
            result = run_gate5(); return JSONResponse(status_code=200 if result.get("ok") else 500, content=result)
        if action == "log-read":
            return {"ok": True, "content": LOG.read_text("utf-8", errors="replace") if LOG.exists() else "", "path": str(LOG), "instanceId": INSTANCE}
        return JSONResponse(status_code=400, content={"ok": False, "error": "unknown action"})
    except subprocess.TimeoutExpired as exc:
        append_log(f"\n=== GATE 5 TIMEOUT instance={INSTANCE} ===\n{exc}\n")
        return JSONResponse(status_code=504, content={"ok": False, "error": "Gate 5 exceeded 240 seconds", "instanceId": INSTANCE})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"ok": False, "error": f"{type(exc).__name__}: {exc}", "instanceId": INSTANCE})
