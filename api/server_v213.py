from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from swyrlz.backend import LIVE, PACKED, RAW, ensure_r39, sha

VERSION = "2.1.3"
ROOT = Path("/tmp/swrlz-admin")
UP = ROOT / "uploads"
WEB = ROOT / "web"
RUNTIME = ROOT / "runtime"
SNAPSHOTS = ROOT / "snapshots"
LOG = ROOT / "full-runtime.log"
ACTIVITY = ROOT / "activity.jsonl"
SERVER_STATE = RUNTIME / "server-state.json"
CHAT_TOKEN_FILE = RUNTIME / "web-chat-token.txt"
ADMIN_PAGE = Path(__file__).resolve().parents[1] / "web" / "admin.html"
for directory in (ROOT, LIVE, UP, WEB, RUNTIME, SNAPSHOTS):
    directory.mkdir(parents=True, exist_ok=True)

INSTANCE = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
STARTED_AT = time.time()
TOKEN = os.environ.get("SWRLZ_ADMIN_TOKEN", "").strip()
MAX_CHUNK = 3 * 1024 * 1024
DOWNLOAD_CHUNK = 3 * 1024 * 1024
DIRECT_DOWNLOAD_MAX = 4 * 1024 * 1024
MAX_TEXT_EDIT = 4 * 1024 * 1024
GATE5 = LIVE / "gate5_live.py"

CAPABILITIES = {
    "admin-files": {"kind": "runtime-mutation", "ready": True},
    "runtime-web": {"kind": "runtime-mutation", "ready": True, "publicBase": "/live/"},
    "runtime-chat-token": {"kind": "secret-runtime-mutation", "ready": True},
    "snapshots": {"kind": "runtime-mutation", "ready": True, "scope": "web-only"},
    "activity-timeline": {"kind": "read-only", "ready": True},
    "release-status": {"kind": "read-only", "ready": True},
    "gate5": {"kind": "runtime-execution", "ready": True},
    "chat-stream": {"kind": "runtime-execution", "ready": True},
    "promote-manifest": {"kind": "read-only", "ready": True, "durableMutation": False},
}

app = FastAPI(title="§wyrlz Unified Server Workbench", version=VERSION)
from api.chat import app as swrlz_chat_app
import api.chat_extensions as _chat_extensions
app.mount("/api/chat", swrlz_chat_app, name="swrlz-chat")


def _write_server_state() -> None:
    payload = {"version": VERSION, "instanceId": INSTANCE, "startedAt": STARTED_AT, "deploymentCommit": os.environ.get("VERCEL_GIT_COMMIT_SHA", ""), "deploymentBranch": os.environ.get("VERCEL_GIT_COMMIT_REF", ""), "capabilities": CAPABILITIES}
    SERVER_STATE.write_text(json.dumps(payload, separators=(",", ":")), "utf-8")

_write_server_state()


def auth(request: Request) -> bool:
    supplied = request.headers.get("x-swrlz-admin-token", "").strip()
    return bool(TOKEN) and hmac.compare_digest(supplied, TOKEN)


def safe_path(value: str | None, default: Path = LIVE) -> Path:
    candidate = Path(value) if value else default
    resolved = candidate.resolve() if candidate.is_absolute() else (ROOT / candidate).resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents: raise PermissionError("path outside /tmp/swrlz-admin")
    return resolved


def mime_for(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def text_candidate(path: Path, mime: str | None = None) -> bool:
    mime = mime or mime_for(path)
    if mime.startswith("text/") or mime in {"application/json", "application/javascript", "application/xml", "application/x-sh", "application/sql"}: return True
    return path.suffix.lower() in {".py", ".kt", ".kts", ".java", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".scss", ".json", ".md", ".txt", ".log", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env", ".sh", ".bat", ".ps1", ".sql", ".csv", ".gradle", ".properties"}


def file_info(path: Path) -> dict:
    stat = path.stat(); mime = "inode/directory" if path.is_dir() else mime_for(path)
    info = {"name": path.name, "path": str(path), "type": "directory" if path.is_dir() else "file", "size": stat.st_size, "modified": int(stat.st_mtime), "mime": mime, "editable": path.is_file() and text_candidate(path, mime) and stat.st_size <= MAX_TEXT_EDIT}
    if path.is_file() and WEB.resolve() in path.resolve().parents:
        rel = path.resolve().relative_to(WEB.resolve()).as_posix(); info["liveUrl"] = "/live/" + rel
    return info


def upload_meta_path(upload_id: str) -> Path: return UP / f"{upload_id}.json"

def append_log(text: str) -> None:
    with LOG.open("a", encoding="utf-8", errors="replace") as out:
        out.write(text); out.write("" if text.endswith("\n") else "\n")


def activity(action: str, **details) -> None:
    safe = {k: v for k, v in details.items() if k.lower() not in {"token", "secret", "content", "body"}}
    with ACTIVITY.open("a", encoding="utf-8") as out: out.write(json.dumps({"ts": time.time(), "action": action, "instanceId": INSTANCE, **safe}, ensure_ascii=False, separators=(",", ":")) + "\n")


def lalm_presence() -> dict:
    return {"packedPresent": PACKED.is_file(), "packedSize": PACKED.stat().st_size if PACKED.is_file() else None, "rawPresent": RAW.is_file(), "rawSize": RAW.stat().st_size if RAW.is_file() else None, "rawPath": str(RAW)}


def preview(path: Path) -> dict:
    if not path.is_file(): raise ValueError("not a file")
    info = file_info(path)
    if text_candidate(path, info["mime"]) and path.stat().st_size <= MAX_TEXT_EDIT:
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
            if "\x00" not in text: return {**info, "previewKind": "text", "content": text}
        except UnicodeDecodeError: pass
    with path.open("rb") as handle: raw = handle.read(4096)
    return {**info, "previewKind": "binary", "hex": raw.hex(" "), "previewBytes": len(raw), "sha256": sha(path) if path.stat().st_size <= 64 * 1024 * 1024 else None}


def run_gate5() -> dict:
    state = ensure_r39()
    if not state.get("ok") or not state.get("modelReady"): return {"ok": False, "code": "R39_NOT_READY", "lalm": state}
    if not GATE5.is_file(): return {"ok": False, "code": "GATE5_NOT_PRESENT", "detail": str(GATE5), "lalm": state}
    env = os.environ.copy(); env.update({"SWRLZ_R39_PATH": str(RAW), "SWRLZ_LALM_PATH": str(RAW), "SWRLZ_R39_GZ_PATH": str(PACKED), "SWRLZ_LIVE_DIR": str(LIVE)})
    started = time.time(); proc = subprocess.run([sys.executable, str(GATE5)], cwd=str(LIVE), env=env, capture_output=True, text=True, errors="replace", timeout=240); elapsed = round(time.time() - started, 3)
    append_log(f"\n=== GATE 5 {time.strftime('%Y-%m-%d %H:%M:%S')} instance={INSTANCE} rc={proc.returncode} elapsed={elapsed}s ===\n{proc.stdout}{proc.stderr}"); activity("gate5-run", returnCode=proc.returncode, elapsedSeconds=elapsed)
    return {"ok": proc.returncode == 0, "returnCode": proc.returncode, "elapsedSeconds": elapsed, "stdout": proc.stdout[-20000:], "stderr": proc.stderr[-20000:], "instanceId": INSTANCE, "modelPath": str(RAW), "lalm": state}


def _web_entries() -> list[dict]:
    entries=[]
    for p in sorted(WEB.rglob("*")):
        if p.is_file():
            rel=p.relative_to(WEB).as_posix(); entries.append({"path":str(p),"relative":rel,"size":p.stat().st_size,"modified":int(p.stat().st_mtime),"mime":mime_for(p),"sha256":sha(p),"liveUrl":"/live/"+rel})
    return entries


def _manifest() -> dict:
    files=[{k:v for k,v in item.items() if k in {"relative","size","sha256","liveUrl"}} for item in _web_entries()]; raw=json.dumps(files,sort_keys=True,separators=(",",":")).encode(); return {"schema":1,"generatedAt":time.time(),"instanceId":INSTANCE,"root":str(WEB),"fileCount":len(files),"files":files,"manifestSha256":hashlib.sha256(raw).hexdigest()}


def _snapshot_create() -> dict:
    sid=time.strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:6]; dst=SNAPSHOTS/sid/"web"
    if WEB.exists(): shutil.copytree(WEB,dst,dirs_exist_ok=True)
    manifest=_manifest(); meta={"snapshotId":sid,"createdAt":time.time(),"instanceId":INSTANCE,"manifest":manifest,"scope":"web-only","secretsExcluded":True}; (SNAPSHOTS/sid/"snapshot.json").write_text(json.dumps(meta,indent=2),"utf-8"); activity("snapshot-create",snapshotId=sid,fileCount=manifest["fileCount"]); return {"ok":True,**meta}


def _snapshot_list() -> list[dict]:
    out=[]
    for d in sorted((p for p in SNAPSHOTS.iterdir() if p.is_dir()),reverse=True):
        try: out.append(json.loads((d/"snapshot.json").read_text("utf-8")))
        except Exception: out.append({"snapshotId":d.name,"corrupt":True})
    return out[:30]


def _snapshot_restore(snapshot_id: str) -> dict:
    if not snapshot_id or not all(c.isalnum() or c in "-_." for c in snapshot_id): raise ValueError("invalid snapshotId")
    src=SNAPSHOTS/snapshot_id/"web"
    if not src.exists(): raise FileNotFoundError(src)
    backup=_snapshot_create(); shutil.rmtree(WEB,ignore_errors=True); shutil.copytree(src,WEB); activity("snapshot-restore",snapshotId=snapshot_id,backupSnapshotId=backup["snapshotId"]); return {"ok":True,"restored":snapshot_id,"backupSnapshotId":backup["snapshotId"],"manifest":_manifest()}


def _config_status() -> dict:
    try: runtime=CHAT_TOKEN_FILE.read_text("utf-8").strip()
    except OSError: runtime=""
    env=os.environ.get("SWRLZ_WEB_CHAT_TOKEN","").strip(); source="runtime" if len(runtime)>=16 else "env" if len(env)>=16 else "missing"
    return {"ok":True,"chatToken":{"configured":source!="missing","source":source,"runtimeOverridePresent":len(runtime)>=16,"environmentFallbackPresent":len(env)>=16,"valueExposed":False}}


def _set_chat_token(value: str) -> dict:
    value=value.strip()
    if not (16<=len(value)<=512) or any(ord(c)<32 or ord(c)==127 for c in value): raise ValueError("chat token must be 16..512 printable characters")
    tmp=CHAT_TOKEN_FILE.with_suffix(".tmp"); tmp.write_text(value,"utf-8"); os.chmod(tmp,0o600); os.replace(tmp,CHAT_TOKEN_FILE); activity("chat-token-set",length=len(value)); return {"ok":True,"saved":True,"source":"runtime","length":len(value),"valueExposed":False}


def _generate_chat_token() -> dict:
    value="swrlz_chat_"+secrets.token_urlsafe(32).replace("-","").replace("_",""); _set_chat_token(value); return {"ok":True,"saved":True,"source":"runtime","token":value,"shownOnce":True}


def _release_status() -> dict:
    return {"ok":True,"runtimeVersion":VERSION,"instanceId":INSTANCE,"uptimeSeconds":round(time.time()-STARTED_AT,1),"deployedCommit":os.environ.get("VERCEL_GIT_COMMIT_SHA",""),"deployedBranch":os.environ.get("VERCEL_GIT_COMMIT_REF",""),"production":os.environ.get("VERCEL_ENV","")=="production","sourceExpectedVersion":VERSION}


def _health_dashboard() -> dict:
    usage=shutil.disk_usage(ROOT)
    try:
        from api.chat_extensions import runtime_chat_state
        chat_state=runtime_chat_state()
    except Exception as exc: chat_state={"available":False,"detail":type(exc).__name__}
    web=_web_entries(); return {"ok":True,"version":VERSION,"instanceId":INSTANCE,"uptimeSeconds":round(time.time()-STARTED_AT,1),"tmp":{"free":usage.free,"used":usage.used,"total":usage.total},"publishedPages":len([x for x in web if x["relative"].endswith(".html")]),"publishedFiles":len(web),"runtimeLogBytes":LOG.stat().st_size if LOG.exists() else 0,"chat":chat_state,**lalm_presence()}


@app.get("/")
@app.get("/api")
def root(): return {"ok":True,"service":"§wyrlz Unified Vercel Server","version":VERSION,"health":"/api/health","admin":"/api/admin","lalm":"/api/lalm","chat":"/api/chat","live":"/live/"}

@app.get("/api/health")
def health(): return {"ok":True,"version":VERSION,"routingReady":True,"runtimeBoundary":"single-api-index","instanceId":INSTANCE,"adminAuthConfigured":bool(TOKEN),**lalm_presence(),"storage":"Vercel /tmp is ephemeral and instance-local; Gate 5 loads/verifies R39 in the same invocation."}

@app.get("/api/lalm")
def lalm():
    try:
        state=ensure_r39(); return JSONResponse(status_code=200 if state.get("ok") else 503,content={**state,"instanceId":INSTANCE})
    except Exception as exc: return JSONResponse(status_code=500,content={"ok":False,"code":"R39_LOAD_FAILED","detail":f"{type(exc).__name__}: {exc}","instanceId":INSTANCE})

@app.get("/api/admin")
def admin_page():
    try: html=ADMIN_PAGE.read_text("utf-8")
    except OSError: return HTMLResponse("Admin page missing",status_code=500)
    return HTMLResponse(html,headers={"Cache-Control":"no-store"})

@app.post("/api/admin")
async def admin_action(request:Request,action:str=Query(...),path:str|None=Query(default=None),name:str|None=Query(default=None),newName:str|None=Query(default=None),size:int|None=Query(default=None),uploadId:str|None=Query(default=None),offset:int=Query(default=0),length:int|None=Query(default=None),instanceId:str|None=Query(default=None),snapshotId:str|None=Query(default=None)):
    if not auth(request):
        supplied=request.headers.get("x-swrlz-admin-token","").strip(); return JSONResponse(status_code=401,content={"ok":False,"error":"invalid or missing SWRLZ_ADMIN_TOKEN","authConfigured":bool(TOKEN),"tokenReceived":bool(supplied),"receivedLength":len(supplied),"instanceId":INSTANCE})
    try:
        if action=="auth-check": return {"ok":True,"authenticated":True,"version":VERSION,"instanceId":INSTANCE,"message":"Admin token accepted."}
        if action=="runtime": return {"ok":True,"version":VERSION,"instanceId":INSTANCE,"root":str(ROOT),"live":str(LIVE),"web":str(WEB),"runtime":str(RUNTIME),"uploadAuthConfigured":bool(TOKEN),"downloadChunkBytes":DOWNLOAD_CHUNK,"capabilities":CAPABILITIES,**lalm_presence()}
        if action=="health-dashboard": return _health_dashboard()
        if action=="capabilities": return {"ok":True,"capabilities":CAPABILITIES}
        if action=="release-status": return _release_status()
        if action=="config-status": return _config_status()
        if action=="chat-token-generate": return _generate_chat_token()
        if action=="chat-token-clear": CHAT_TOKEN_FILE.unlink(missing_ok=True); activity("chat-token-clear"); return {"ok":True,"cleared":True,"fallback":"environment"}
        if action=="chat-token-set": return _set_chat_token((await request.body()).decode("utf-8"))
        if action=="live-web-list": return {"ok":True,"root":str(WEB),"entries":_web_entries(),"instanceId":INSTANCE}
        if action=="promote-manifest": return {"ok":True,"manifest":_manifest(),"durableMutationPerformed":False}
        if action=="snapshot-create": return _snapshot_create()
        if action=="snapshot-list": return {"ok":True,"snapshots":_snapshot_list()}
        if action=="snapshot-restore": return _snapshot_restore(snapshotId or "")
        if action=="activity":
            lines=ACTIVITY.read_text("utf-8",errors="replace").splitlines()[-200:] if ACTIVITY.exists() else []; return {"ok":True,"events":[json.loads(x) for x in lines if x.strip()]}
        if action=="list":
            base=safe_path(path)
            if not base.exists(): raise FileNotFoundError(base)
            if not base.is_dir(): return {"ok":True,**file_info(base),"entries":[]}
            entries=sorted((file_info(p) for p in base.iterdir()),key=lambda x:(x["type"]!="directory",x["name"].lower())); return {"ok":True,"path":str(base),"entries":entries,"instanceId":INSTANCE}
        if action=="preview":
            target=safe_path(path)
            if target.is_dir(): return {"ok":True,**file_info(target),"previewKind":"directory"}
            return {"ok":True,**preview(target),"instanceId":INSTANCE}
        if action=="download":
            target=safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            if target.stat().st_size>DIRECT_DOWNLOAD_MAX: return JSONResponse(status_code=413,content={"ok":False,"error":"file exceeds direct-download limit; use chunked download","size":target.stat().st_size,"chunkBytes":DOWNLOAD_CHUNK})
            return FileResponse(target,media_type=mime_for(target),filename=target.name)
        if action=="download-info":
            target=safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            return {"ok":True,"name":target.name,"path":str(target),"size":target.stat().st_size,"mime":mime_for(target),"chunkBytes":DOWNLOAD_CHUNK,"instanceId":INSTANCE}
        if action=="download-chunk":
            if instanceId!=INSTANCE: return JSONResponse(status_code=409,content={"ok":False,"error":"runtime instance changed; restart download","instanceId":INSTANCE})
            target=safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            total=target.stat().st_size
            if offset<0 or offset>total: raise ValueError("invalid download offset")
            wanted=DOWNLOAD_CHUNK if length is None else length
            if wanted<=0 or wanted>DOWNLOAD_CHUNK: raise ValueError(f"download length must be 1..{DOWNLOAD_CHUNK}")
            wanted=min(wanted,total-offset)
            with target.open("rb") as handle: handle.seek(offset); body=handle.read(wanted)
            end=offset+len(body); return Response(content=body,status_code=206,media_type="application/octet-stream",headers={"x-swrlz-instance-id":INSTANCE,"x-swrlz-offset":str(offset),"x-swrlz-next-offset":str(end),"x-swrlz-total-size":str(total),"content-range":f"bytes {offset}-{max(offset,end-1)}/{total}","accept-ranges":"bytes"})
        if action=="hash":
            target=safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            return {"ok":True,"path":str(target),"size":target.stat().st_size,"sha256":sha(target)}
        if action=="save-text":
            target=safe_path(path); body=await request.body()
            if len(body)>MAX_TEXT_EDIT: return JSONResponse(status_code=413,content={"ok":False,"error":"text file exceeds editor limit"})
            body.decode("utf-8"); target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(body); activity("save-text",path=str(target),size=len(body)); return {"ok":True,**file_info(target),"sha256":sha(target)}
        if action=="mkdir":
            base=safe_path(path)
            if not name or Path(name).name!=name: raise ValueError("simple folder name required")
            target=safe_path(str(base/name)); target.mkdir(parents=False,exist_ok=False); activity("mkdir",path=str(target)); return {"ok":True,**file_info(target)}
        if action=="rename":
            target=safe_path(path)
            if not newName or Path(newName).name!=newName: raise ValueError("simple newName required")
            renamed=safe_path(str(target.parent/newName)); target.rename(renamed); activity("rename",old=str(target),new=str(renamed)); return {"ok":True,**file_info(renamed)}
        if action=="delete":
            target=safe_path(path)
            if target in {ROOT,LIVE,UP,WEB,RUNTIME,SNAPSHOTS}: raise PermissionError("protected runtime directory")
            shutil.rmtree(target) if target.is_dir() else target.unlink(); activity("delete",path=str(target)); return {"ok":True,"deleted":str(target)}
        if action=="upload-init":
            if not name or Path(name).name!=name or size is None or size<0: raise ValueError("simple name and non-negative size required")
            base=safe_path(path); base.mkdir(parents=True,exist_ok=True); target=safe_path(str(base/name)); uid=uuid.uuid4().hex; part=UP/f"{uid}.part"; part.touch(); metadata={"uploadId":uid,"instanceId":INSTANCE,"target":str(target),"part":str(part),"expected":size,"received":0}; upload_meta_path(uid).write_text(json.dumps(metadata),"utf-8"); return {"ok":True,"uploadId":uid,"instanceId":INSTANCE,"chunkBytes":MAX_CHUNK}
        if action=="upload-chunk":
            if instanceId!=INSTANCE: return JSONResponse(status_code=409,content={"ok":False,"error":"runtime instance changed; restart upload","instanceId":INSTANCE})
            if not uploadId: raise ValueError("uploadId required")
            metadata=json.loads(upload_meta_path(uploadId).read_text("utf-8")); body=await request.body()
            if len(body)>MAX_CHUNK: return JSONResponse(status_code=413,content={"ok":False,"error":"chunk too large"})
            if offset!=metadata["received"]: return JSONResponse(status_code=409,content={"ok":False,"error":"offset mismatch","received":metadata["received"]})
            with Path(metadata["part"]).open("ab") as out: out.write(body)
            metadata["received"]+=len(body); upload_meta_path(uploadId).write_text(json.dumps(metadata),"utf-8"); return {"ok":True,"received":metadata["received"],"expected":metadata["expected"],"instanceId":INSTANCE}
        if action=="upload-finish":
            if instanceId!=INSTANCE: return JSONResponse(status_code=409,content={"ok":False,"error":"runtime instance changed; restart upload"})
            if not uploadId: raise ValueError("uploadId required")
            metadata=json.loads(upload_meta_path(uploadId).read_text("utf-8")); part=Path(metadata["part"]); target=safe_path(metadata["target"])
            if metadata["received"]!=metadata["expected"] or part.stat().st_size!=metadata["expected"]: return JSONResponse(status_code=409,content={"ok":False,"error":"upload incomplete"})
            os.replace(part,target); upload_meta_path(uploadId).unlink(missing_ok=True); activity("upload",path=str(target),size=target.stat().st_size); return {"ok":True,**file_info(target),"sha256":sha(target),"instanceId":INSTANCE}
        if action=="lalm-load":
            state=ensure_r39(); activity("lalm-load",ok=bool(state.get("ok"))); return JSONResponse(status_code=200 if state.get("ok") else 503,content={**state,"instanceId":INSTANCE})
        if action=="gate5-run":
            result=run_gate5(); return JSONResponse(status_code=200 if result.get("ok") else 500,content=result)
        if action=="log-read": return {"ok":True,"content":LOG.read_text("utf-8",errors="replace") if LOG.exists() else "","path":str(LOG),"instanceId":INSTANCE}
        return JSONResponse(status_code=400,content={"ok":False,"error":"unknown action"})
    except subprocess.TimeoutExpired as exc:
        append_log(f"\n=== GATE 5 TIMEOUT instance={INSTANCE} ===\n{exc}\n"); return JSONResponse(status_code=504,content={"ok":False,"error":"Gate 5 exceeded 240 seconds","instanceId":INSTANCE})
    except Exception as exc:
        return JSONResponse(status_code=500,content={"ok":False,"error":f"{type(exc).__name__}: {exc}","instanceId":INSTANCE})
