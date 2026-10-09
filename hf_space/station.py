"""HF-only in-process Station adapter for the canonical Chat projection.

The Station/Workstation owns operational response orchestration: admission,
queue/lifecycle state, worker/engine delegation, resource telemetry, cancellation,
state projection, synchronization, and delivery readiness. It does not grade the
semantic correctness of response content. Ready/terminal means operationally
complete for the next routed stage, not independently proven correct.

Candidate limitations: process-local state, anonymous session, no durable account
storage or external durable queue. Do not claim production parity.
"""
from __future__ import annotations
import asyncio, base64, copy, hashlib, json, os, threading, time, uuid, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from model_router import dispatch, ModelUnavailable, routes
from code_packages import PackageError, build_package, wants_archive
from staged_projects import (WorkspaceError as AutoWorkspaceError, parse_manifest,
                             create_workspace as create_auto_workspace,
                             stage_files, project_view, package_project)
from staged_workspaces import (WorkspaceError, WorkspaceConflict, create_workspace,
                               attach_revision, progress as workspace_progress,
                               finalize as finalize_workspace, cancel as cancel_workspace,
                               downloadable_files, MAX_WORKSPACES_PER_THREAD)
try:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token as google_id_token
except Exception:
    google_requests=None
    google_id_token=None

ROOT=Path(__file__).resolve().parent
CONTRACT="swrlz-lalm-station-sync-v1"
app=FastAPI(title="§wyrlz HF Station candidate")
app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")
_lock=threading.RLock()
_github_diagnostic_lock=threading.Lock()
_sessions={}
_pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix="hf-r39")
_generate=None
_stock_generate=None
_large_generate=None
_coder_generate=None

def set_generator(fn,stock_fn=None,large_fn=None,coder_fn=None):
    global _generate,_stock_generate,_large_generate,_coder_generate
    _generate=fn
    _stock_generate=stock_fn
    _large_generate=large_fn
    _coder_generate=coder_fn


def persist_runtime_diagnostic(request_id,model_id,event_type,diagnostic):
    """Persist one bounded diagnostic document with serialized 409 recovery."""
    token=str(os.environ.get("SWRLZ_DIAGNOSTIC_GITHUB_TOKEN") or "").strip()
    if not token:
        result={"ok":False,"reason":"diagnostic-token-not-configured","attempts":0,"conflictCount":0}
        print(json.dumps({"event":"RUNTIME_DIAGNOSTIC_PERSIST_SKIPPED","requestId":request_id,**result}),flush=True)
        return result
    allowed={
        "REPAIR_DIAGNOSTIC":("repair","repair-diagnostic.json","swrlz-github-repair-log-v1"),
        "REPAIR_OUTCOME_DIAGNOSTIC":("repair","repair-outcome-diagnostic.json","swrlz-github-repair-log-v1"),
        "PROGRAMMING_GENERATION_TELEMETRY":("programming","candidate-attempt-telemetry.json","swrlz-github-programming-attempt-log-v1"),
        "ONLINE_RESEARCH_TRACE":("online-research","online-research-trace.json","swrlz-github-online-research-trace-v1"),
        "ONLINE_RESEARCH_OUTCOME":("online-research","online-research-outcome.json","swrlz-github-online-research-outcome-v2"),
        "KNOWLEDGE_ACQUISITION_SNAPSHOT":("knowledge-snapshots","knowledge-snapshot.json","swrlz-knowledge-acquisition-snapshot-v1"),
        "KNOWLEDGE_ACQUISITION_FOLLOWUP_1":("knowledge-snapshots","followup-1.json","swrlz-knowledge-followup-v1"),
        "KNOWLEDGE_ACQUISITION_FOLLOWUP_2":("knowledge-snapshots","followup-2.json","swrlz-knowledge-followup-v1"),
        "KNOWLEDGE_ACQUISITION_FOLLOWUP_3":("knowledge-snapshots","followup-3.json","swrlz-knowledge-followup-v1"),
    }
    spec=allowed.get(str(event_type or ""))
    if spec is None or not isinstance(diagnostic,dict):
        return {"ok":False,"reason":"unsupported-diagnostic","attempts":0,"conflictCount":0}
    category,filename,schema=spec
    owner=str(os.environ.get("SWRLZ_GITHUB_OWNER") or "kaministrator999-ui").strip()
    repo=str(os.environ.get("SWRLZ_GITHUB_REPO") or "Swrlzkamico").strip()
    safe_request="".join(ch for ch in str(request_id or "") if ch.isalnum() or ch in "-_")[:80]
    if not safe_request:
        return {"ok":False,"reason":"invalid-request-id","attempts":0,"conflictCount":0}
    path=f"runtime-diagnostics/{category}/{safe_request}/{filename}"
    document={
        "schema":schema,
        "requestId":str(request_id or "")[:160],
        "modelId":str(model_id or "")[:80],
        "eventType":str(event_type or "")[:80],
        "sourceRef":str(os.environ.get("SWRLZ_GITHUB_REF") or "")[:80] or None,
        "persistedAtUnixMs":int(time.time()*1000),
        "diagnostic":diagnostic,
    }
    body=json.dumps(document,ensure_ascii=False,indent=2)+"\n"
    encoded_path=urllib.parse.quote(path,safe="/")
    url=f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}"
    headers={
        "Authorization":"Bearer "+token,
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"swrlz-runtime-diagnostics/1",
    }
    max_attempts=4
    conflicts=0
    last_error_preview=None
    with _github_diagnostic_lock:
        for attempt in range(1,max_attempts+1):
            existing_sha=None
            try:
                read_request=urllib.request.Request(url+"?ref=runtime",headers=headers,method="GET")
                with urllib.request.urlopen(read_request,timeout=12) as response:
                    current=json.loads(response.read().decode("utf-8"))
                    existing_sha=str(current.get("sha") or "") or None
            except urllib.error.HTTPError as exc:
                preview=""
                try:
                    preview=exc.read().decode("utf-8","replace")[:600]
                except Exception:
                    preview=""
                if exc.code!=404:
                    result={
                        "ok":False,"reason":"github-read-failed","status":int(exc.code),
                        "path":path,"branch":"runtime","attempts":attempt,
                        "conflictCount":conflicts,"errorPreview":preview or None,
                    }
                    print(json.dumps({"event":"RUNTIME_DIAGNOSTIC_PERSIST_FAILED","requestId":request_id,**result}),flush=True)
                    return result
            except Exception as exc:
                result={
                    "ok":False,"reason":"github-read-failed","errorType":type(exc).__name__,
                    "path":path,"branch":"runtime","attempts":attempt,"conflictCount":conflicts,
                }
                print(json.dumps({"event":"RUNTIME_DIAGNOSTIC_PERSIST_FAILED","requestId":request_id,**result}),flush=True)
                return result

            payload={
                "message":f"Record {category} diagnostic {safe_request[:12]}",
                "content":base64.b64encode(body.encode("utf-8")).decode("ascii"),
                "branch":"runtime",
            }
            if existing_sha:
                payload["sha"]=existing_sha
            try:
                write_request=urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={**headers,"Content-Type":"application/json"},
                    method="PUT",
                )
                with urllib.request.urlopen(write_request,timeout=12) as response:
                    status=int(response.status)
                result={
                    "ok":status in (200,201),"path":path,"branch":"runtime","status":status,
                    "attempts":attempt,"conflictCount":conflicts,
                    "conflictRecovered":bool(conflicts),
                    "errorPreview":last_error_preview,
                }
                print(json.dumps({"event":"RUNTIME_DIAGNOSTIC_PERSISTED" if result["ok"] else "RUNTIME_DIAGNOSTIC_PERSIST_FAILED","requestId":request_id,**result}),flush=True)
                return result
            except urllib.error.HTTPError as exc:
                preview=""
                try:
                    preview=exc.read().decode("utf-8","replace")[:600]
                except Exception:
                    preview=""
                last_error_preview=preview or None
                if exc.code==409 and attempt<max_attempts:
                    conflicts+=1
                    print(json.dumps({
                        "event":"RUNTIME_DIAGNOSTIC_PERSIST_RETRY",
                        "requestId":request_id,"path":path,"branch":"runtime",
                        "status":409,"attempt":attempt,"nextAttempt":attempt+1,
                        "errorPreview":last_error_preview,
                    }),flush=True)
                    time.sleep(0.15*attempt)
                    continue
                result={
                    "ok":False,"reason":"github-write-failed","status":int(exc.code),
                    "path":path,"branch":"runtime","attempts":attempt,
                    "conflictCount":conflicts+(1 if exc.code==409 else 0),
                    "errorPreview":last_error_preview,
                }
                print(json.dumps({"event":"RUNTIME_DIAGNOSTIC_PERSIST_FAILED","requestId":request_id,**result}),flush=True)
                return result
            except Exception as exc:
                result={
                    "ok":False,"reason":"github-write-failed","errorType":type(exc).__name__,
                    "path":path,"branch":"runtime","attempts":attempt,"conflictCount":conflicts,
                    "errorPreview":last_error_preview,
                }
                print(json.dumps({"event":"RUNTIME_DIAGNOSTIC_PERSIST_FAILED","requestId":request_id,**result}),flush=True)
                return result
    return {
        "ok":False,"reason":"github-write-retry-exhausted","path":path,"branch":"runtime",
        "attempts":max_attempts,"conflictCount":conflicts,"errorPreview":last_error_preview,
    }

def _bounded_knowledge_snapshot(request_id,prompt,online_research,trace,sources,widgets,final_response,status_trail):
    """Separate learning snapshot: compact, reviewable, and intentionally not a debug dump."""
    clean_prompt=str(prompt or "").strip()[:4000]
    useful_sources=[]
    for item in (sources or [])[:12]:
        if not isinstance(item,dict):continue
        useful_sources.append({
            "title":str(item.get("title") or item.get("name") or "")[:240],
            "source":str(item.get("source") or item.get("provider") or "")[:120],
            "url":str(item.get("url") or "")[:900],
            "snippet":str(item.get("snippet") or "")[:900],
            "rank":item.get("rank") if isinstance(item.get("rank"),(int,float)) else None,
        })
    research=online_research if isinstance(online_research,dict) else {}
    return {
        "schema":"swrlz-knowledge-acquisition-snapshot-v1",
        "requestId":str(request_id or "")[:160],
        "trigger":{"userText":clean_prompt,"sha256":hashlib.sha256(clean_prompt.encode("utf-8")).hexdigest()},
        "research":{
            "kind":str(research.get("kind") or "")[:80],
            "status":str(research.get("status") or "")[:80],
            "provider":str(research.get("provider") or "")[:120],
            "reason":str(research.get("reason") or "")[:160],
            "query":str(research.get("query") or "")[:800],
            "resultCount":research.get("resultCount") if isinstance(research.get("resultCount"),(int,float)) else None,
            "sources":useful_sources,
            "sourceSites":sorted({str(urllib.parse.urlsplit(str(x.get("url") or "")).hostname or "").lower() for x in useful_sources if x.get("url")})[:12],
            "widgetKinds":[str(x.get("kind") or "")[:80] for x in (widgets or []) if isinstance(x,dict)][:8],
            "trace":[{
                "phase":str(x.get("phase") or "")[:100],
                "provider":str(x.get("provider") or "")[:100],
                "activity":str(x.get("activity") or "")[:240],
                "status":x.get("status") if isinstance(x.get("status"),(int,float,str)) else None,
                "elapsedMs":x.get("elapsedMs") if isinstance(x.get("elapsedMs"),(int,float)) else None,
            } for x in (trace or [])[-32:] if isinstance(x,dict)],
        },
        "answer":{"text":str(final_response or "")[:16000],"sha256":hashlib.sha256(str(final_response or "").encode("utf-8")).hexdigest()},
        "followUpWindow":{"maxUserTurns":3,"captured":[],"state":"OPEN"},
        "review":{"state":"PENDING","promoteToLocalKnowledge":False,"notes":[]},
        "privacy":{"preciseLocationStored":False,"privateReasoningStored":False,"fullHistoryStored":False},
        "statusTrail":[{"phase":str(x.get("phase") or "")[:100],"reason":str(x.get("reason") or "")[:240]} for x in (status_trail or [])[-32:] if isinstance(x,dict)],
    }

def _session(request):
    key=request.cookies.get("swrlz_hf_sid")
    if not key or key not in _sessions:
        key=uuid.uuid4().hex
        with _lock:
            _sessions.setdefault(key,{"revision":0,"currentId":"","threads":[],"activeGeneration":None})
    return key,_sessions[key]

def _snapshot(s):
    # The canonical Station holds source bodies; the Mask only receives progress
    # metadata. This prevents duplicating staged source code in sync responses.
    threads=copy.deepcopy(s["threads"])
    for thread in threads:
        if isinstance(thread.get("autoProjectWorkspaces"),list):
            thread["autoProjectWorkspaces"]=[project_view(w) for w in thread["autoProjectWorkspaces"]]
        if isinstance(thread.get("projectWorkspaces"),list):
            thread["projectWorkspaces"]=[workspace_progress(w) for w in thread["projectWorkspaces"]]
    return {"contract":CONTRACT,"revision":s["revision"],"threads":threads,
            "currentThread":next((copy.deepcopy(t) for t in threads if t["id"]==s["currentId"]),None),
            "state":{"currentId":s["currentId"],"threads":copy.deepcopy(threads)},
            "activeGeneration":copy.deepcopy(s["activeGeneration"])}

def _chat_document():
    """Serve the canonical Chat document plus the bounded HF presentation adapter."""
    source=(ROOT/"chat/§wyrlz/index.html").read_text(encoding="utf-8")
    marker='</body>'
    adapter='<script src="/chat/§wyrlz/assets/widget-analysis-v128.js" defer></script>'
    return source.replace(marker,adapter+marker,1) if marker in source else source+adapter

@app.get("/")
def home():
    return HTMLResponse(_chat_document(),headers={"Cache-Control":"no-store"})

@app.get("/chat/§wyrlz")
def chat():
    return HTMLResponse(_chat_document(),headers={"Cache-Control":"no-store"})

@app.get("/api/hf/models")
def models():
    return {"models":[vars(r) for r in routes()]}

GOOGLE_CLIENT_ID=os.environ.get("SWRLZ_GOOGLE_CLIENT_ID","").strip() or "1083208613166-bj7isingvbv5dcns9ldtru8cjfj993mc.apps.googleusercontent.com"
_hf_accounts={}

def _account_session(request:Request):
    sid=request.cookies.get("swrlz_hf_account")
    return sid,_hf_accounts.get(sid) if sid else None

@app.get("/api/account/status")
def account_status():
    return {"googleClientId":GOOGLE_CLIENT_ID if google_id_token is not None else "","durable":False,"authority":"hf-process-local-google"}

@app.get("/api/account/me")
def account_me(request:Request):
    _,user=_account_session(request)
    if not user:return JSONResponse({"ok":False,"code":"ACCOUNT_SESSION_INVALID"},status_code=401)
    return {"user":user,"profile":{"version":0},"durable":False}

@app.post("/api/account/google")
async def account_google(request:Request):
    if google_id_token is None or google_requests is None:
        return JSONResponse({"ok":False,"code":"GOOGLE_AUTH_UNAVAILABLE"},status_code=503)
    body=await request.json();credential=str(body.get("credential") or "").strip()
    if not credential:return JSONResponse({"ok":False,"code":"GOOGLE_CREDENTIAL_REQUIRED"},status_code=400)
    try:
        claims=google_id_token.verify_oauth2_token(credential,google_requests.Request(),GOOGLE_CLIENT_ID)
        subject=str(claims.get("sub") or "").strip()
        if not subject:raise ValueError("Google token has no subject")
        user={"id":"google:"+subject,"email":claims.get("email"),"displayName":claims.get("name") or claims.get("email") or "Google user","picture":claims.get("picture")}
    except Exception:
        return JSONResponse({"ok":False,"code":"GOOGLE_CREDENTIAL_INVALID"},status_code=401)
    sid=uuid.uuid4().hex
    with _lock:_hf_accounts[sid]=user
    response=JSONResponse({"user":user,"profile":{"version":0},"durable":False})
    response.set_cookie("swrlz_hf_account",sid,httponly=True,samesite="lax",secure=True,max_age=7*86400)
    return response

@app.post("/api/account/logout")
def account_logout(request:Request):
    sid,_=_account_session(request)
    if sid:
        with _lock:_hf_accounts.pop(sid,None)
    response=JSONResponse({"ok":True})
    response.delete_cookie("swrlz_hf_account")
    return response

@app.get("/api/lalm_station/sync")
def sync(request:Request):
    key,s=_session(request)
    with _lock: response=JSONResponse(_snapshot(s))
    response.set_cookie("swrlz_hf_sid",key,httponly=True,samesite="lax",secure=request.url.scheme=="https",max_age=86400,path="/")
    return response

@app.get("/api/lalm_station/stream")
async def stream_generation(request:Request, requestId:str):
    """NDJSON projection of one accepted Station generation.

    The model generator remains authoritative for token deltas. This endpoint
    forwards newly observed text/status state promptly so Chat does not need to
    discover incremental output through whole-session snapshot polling.
    """
    key,s=_session(request)
    rid=str(requestId or "").strip()
    if not rid or len(rid)>160:raise HTTPException(400,"Invalid requestId")
    async def events():
        sent_text=""
        sent_status=0
        sent_widgets=0
        terminal_sent=False
        while True:
            if await request.is_disconnected():return
            with _lock:
                g=copy.deepcopy(s.get("activeGeneration"))
            if not g or str(g.get("requestId") or "")!=rid:
                yield json.dumps({"type":"FAILED","phase":"STREAM_UNAVAILABLE","reason":"Generation is no longer active","terminal":True,"requestId":rid},ensure_ascii=False)+"\n"
                return
            statuses=g.get("status") if isinstance(g.get("status"),list) else []
            while sent_status<len(statuses):
                item=statuses[sent_status] if isinstance(statuses[sent_status],dict) else {}
                sent_status+=1
                yield json.dumps({"type":"STATUS","phase":str(item.get("phase") or "STATUS"),"reason":str(item.get("reason") or ""),"categories":copy.deepcopy(item.get("categories") or []),"site":str(item.get("site") or "")[:180],"url":str(item.get("url") or "")[:1000],"provider":str(item.get("provider") or "")[:120],"httpStatus":item.get("httpStatus"),"resultCount":item.get("resultCount"),"seq":sent_status,"requestId":rid},ensure_ascii=False)+"\n"
            widgets=g.get("widgets") if isinstance(g.get("widgets"),list) else []
            while sent_widgets<len(widgets):
                widget=widgets[sent_widgets] if isinstance(widgets[sent_widgets],dict) else {}
                sent_widgets+=1
                if widget:
                    yield json.dumps({"type":"WIDGET","widget":widget,"seq":int(g.get("lastSeq") or 0),"requestId":rid},ensure_ascii=False)+"\n"
            text_now=str(g.get("text") or "")
            if len(text_now)>len(sent_text):
                delta=text_now[len(sent_text):]
                sent_text=text_now
                yield json.dumps({"type":"DELTA","text":delta,"seq":int(g.get("lastSeq") or 0),"requestId":rid},ensure_ascii=False)+"\n"
            if g.get("terminal") and not terminal_sent:
                terminal_sent=True
                yield json.dumps({"type":str(g.get("terminalType") or "COMPLETE"),"phase":str(g.get("phase") or "COMPLETE"),"terminal":True,"seq":int(g.get("lastSeq") or 0),"requestId":rid},ensure_ascii=False)+"\n"
                return
            await asyncio.sleep(0.025)
    return StreamingResponse(events(),media_type="application/x-ndjson",headers={"Cache-Control":"no-store, no-transform","X-Accel-Buffering":"no"})

@app.get("/api/lalm_station/export")
def export_session(request:Request):
    """Download only the caller's process-local conversation and generation diagnostics."""
    key=request.cookies.get("swrlz_hf_sid")
    with _lock:
        if not key or key not in _sessions:raise HTTPException(404,"No active HF session")
        snapshot=_snapshot(_sessions[key])
    document={"format":"swrlz-hf-session-export-v1","exportedAtUnixMs":int(time.time()*1000),"storage":"process-local; not durable account history","threads":snapshot["threads"],"activeGeneration":snapshot["activeGeneration"]}
    return Response(content=json.dumps(document,ensure_ascii=False,indent=2),media_type="application/json",headers={"Content-Disposition":"attachment; filename=swrlz-dragon-chat.json","Cache-Control":"no-store","X-Content-Type-Options":"nosniff"})

@app.get("/api/lalm_station/artifacts/download")
def download_code_artifact(
    request: Request, threadId: str, artifactId: str,
    revision: int = 0, sourceHash: str = "", asArchive: bool = False,
):
    """Download one completed, cookie-scoped code artifact revision.

    Never accept arbitrary caller-provided paths or raw file content. Reuse only
    canonical in-session artifact snapshots; revision/hash prevent wrong downloads
    after concurrent edits, and archives are built in memory, never on disk.
    """
    if not (1 <= len(threadId) <= 160 and 1 <= len(artifactId) <= 160):
        raise HTTPException(400, "Invalid code artifact locator")
    if not (1 <= revision <= 10000 and len(sourceHash) == 64):
        raise HTTPException(400, "A valid artifact revision and hash are required")
    key = request.cookies.get("swrlz_hf_sid")
    with _lock:
        session = _sessions.get(key) if key else None
        if session is None:
            raise HTTPException(404, "Code artifact unavailable")
        thread = next((item for item in session.get("threads", [])
                       if item.get("id") == threadId), None)
        artifact = _find_artifact(thread, artifactId) if thread else None
        record = _artifact_revision_record(artifact, revision) if artifact else None
        if record is None or str(record.get("sourceHash") or "") != sourceHash:
            raise HTTPException(404, "Requested artifact revision unavailable")
        files = copy.deepcopy(record.get("files") or [])
        archive_requested = bool(record.get("archiveRequested"))
    if _artifact_source_hash(files) != sourceHash:
        raise HTTPException(409, "Artifact source integrity mismatch")
    try:
        package = build_package(files, force_archive=bool(asArchive) or archive_requested)
    except PackageError as exc:
        raise HTTPException(422, str(exc)) from exc
    # ASCII filename is guaranteed by the packaging path validator.
    filename = package["filename"].replace('"', "")
    return Response(
        content=package["body"], media_type=package["mediaType"],
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
            "Cross-Origin-Resource-Policy": "same-origin",
            "X-Code-Package-Sha256": package["sha256"],
            "X-Code-Package-Files": str(package["fileCount"]),
        },
    )


def _workspace_session_thread(request: Request, thread_id: str):
    """Must be called holding _lock; do not mint a new session for downloads."""
    if not isinstance(thread_id, str) or not 1 <= len(thread_id) <= 160:
        raise HTTPException(400, "Invalid thread locator")
    sid=request.cookies.get("swrlz_hf_sid")
    session=_sessions.get(sid) if sid else None
    if session is None:
        raise HTTPException(404, "Workspace session unavailable")
    thread=next((x for x in session.get("threads", []) if x.get("id")==thread_id), None)
    if thread is None:
        raise HTTPException(404, "Workspace thread unavailable")
    return session, thread


def _workspace_record(thread, workspace_id):
    return next((w for w in thread.get("projectWorkspaces", [])
                 if w.get("id")==workspace_id), None)


@app.get("/api/lalm_station/workspaces")
def list_project_workspaces(request: Request, threadId: str):
    with _lock:
        _,thread=_workspace_session_thread(request,threadId)
        return {"schema":"swrlz-staged-workspace-list-v1",
                "workspaces":[workspace_progress(w) for w in thread.get("projectWorkspaces",[])]}


@app.post("/api/lalm_station/workspaces")
async def create_project_workspace(request: Request):
    body=await request.json()
    if not isinstance(body,dict):
        raise HTTPException(400,"Invalid workspace request")
    with _lock:
        session,thread=_workspace_session_thread(request,body.get("threadId"))
        current=thread.setdefault("projectWorkspaces",[])
        if len(current)>=MAX_WORKSPACES_PER_THREAD:
            raise HTTPException(422,"Workspace capacity reached for this thread")
        try:
            project=create_workspace("workspace-"+uuid.uuid4().hex,
                                     body.get("title","Project files"),body.get("requiredPaths"))
        except WorkspaceError as exc:
            raise HTTPException(422,str(exc)) from exc
        current.append(project)
        session["revision"]+=1
        return {"ok":True,"workspace":workspace_progress(project)}


@app.post("/api/lalm_station/workspaces/attach")
async def attach_project_source(request: Request):
    body=await request.json()
    if not isinstance(body,dict):raise HTTPException(400,"Invalid attach request")
    with _lock:
        session,thread=_workspace_session_thread(request,body.get("threadId"))
        project=_workspace_record(thread,body.get("workspaceId"))
        if project is None:raise HTTPException(404,"Workspace not found")
        artifact=_find_artifact(thread,body.get("artifactId"))
        if artifact is None:raise HTTPException(404,"Code artifact not found")
        try:
            source_revision=int(body.get("artifactRevision") or 0)
            expected=int(body.get("expectedWorkspaceRevision") or 0)
        except (ValueError,TypeError):
            raise HTTPException(400,"Invalid revision")
        source_sha=body.get("artifactSourceHash")
        revision_record=_artifact_revision_record(artifact,source_revision)
        if revision_record is None or str(revision_record.get("sourceHash") or "")!=source_sha:
            raise HTTPException(409,"Artifact revision/source hash changed")
        source_files=copy.deepcopy(revision_record.get("files") or [])
        if _artifact_source_hash(source_files)!=source_sha:
            raise HTTPException(409,"Artifact body fails integrity check")
        try:
            updated=attach_revision(
                project,source_files,artifact_id=artifact["id"],
                artifact_revision=source_revision,artifact_sha=source_sha,
                expected_revision=expected,
            )
        except WorkspaceConflict as exc:
            raise HTTPException(409,str(exc)) from exc
        except WorkspaceError as exc:
            raise HTTPException(422,str(exc)) from exc
        project.clear();project.update(updated)
        session["revision"]+=1
        return {"ok":True,"workspace":workspace_progress(project)}


@app.post("/api/lalm_station/workspaces/finalize")
async def finalize_project_workspace(request: Request):
    body=await request.json()
    if not isinstance(body,dict):raise HTTPException(400,"Invalid finalize request")
    with _lock:
        session,thread=_workspace_session_thread(request,body.get("threadId"))
        project=_workspace_record(thread,body.get("workspaceId"))
        if project is None:raise HTTPException(404,"Workspace not found")
        try:
            result=finalize_workspace(project,int(body.get("expectedWorkspaceRevision") or 0))
        except WorkspaceConflict as exc:
            raise HTTPException(409,str(exc)) from exc
        except (WorkspaceError,TypeError,ValueError) as exc:
            raise HTTPException(422,str(exc)) from exc
        project.clear();project.update(result)
        session["revision"]+=1
        return {"ok":True,"workspace":workspace_progress(project)}


@app.post("/api/lalm_station/workspaces/cancel")
async def cancel_project_workspace(request: Request):
    body=await request.json()
    if not isinstance(body,dict):raise HTTPException(400,"Invalid cancel request")
    with _lock:
        session,thread=_workspace_session_thread(request,body.get("threadId"))
        project=_workspace_record(thread,body.get("workspaceId"))
        if project is None:raise HTTPException(404,"Workspace not found")
        try:
            result=cancel_workspace(project,int(body.get("expectedWorkspaceRevision") or 0))
        except WorkspaceConflict as exc:
            raise HTTPException(409,str(exc)) from exc
        except (WorkspaceError,ValueError,TypeError) as exc:
            raise HTTPException(422,str(exc)) from exc
        project.clear();project.update(result)
        session["revision"]+=1
        return {"ok":True,"workspace":workspace_progress(project)}


@app.get("/api/lalm_station/workspaces/download")
def download_project_workspace(request: Request, threadId: str,
                               workspaceId: str, revision: int = 0,
                               sourceHash: str = ""):
    with _lock:
        _,thread=_workspace_session_thread(request,threadId)
        project=_workspace_record(thread,workspaceId)
        if project is None:raise HTTPException(404,"Workspace not found")
        try:
            files=downloadable_files(project,revision,sourceHash)
        except WorkspaceConflict as exc:
            raise HTTPException(409,str(exc)) from exc
        except WorkspaceError as exc:
            raise HTTPException(422,str(exc)) from exc
    try:
        package=build_package(files,force_archive=True)
    except PackageError as exc:
        raise HTTPException(422,str(exc)) from exc
    filename=package["filename"].replace('"',"")
    return Response(content=package["body"],media_type="application/zip",headers={
        "Content-Disposition":f'attachment; filename="{filename}"',
        "Cache-Control":"private, no-store","X-Content-Type-Options":"nosniff",
        "Cross-Origin-Resource-Policy":"same-origin",
        "X-Code-Package-Sha256":package["sha256"],
        "X-Code-Package-Files":str(package["fileCount"]),
        "X-Workspace-Validation":"not-run",
    })


@app.get("/api/lalm_station/projects/download")
def download_staged_project(request: Request, threadId: str, workspaceId: str,
                            revision: int, manifestSha256: str):
    """Only completed manifest-backed projects from the caller's session."""
    if not all(isinstance(x,str) and 1<=len(x)<=160 for x in (threadId,workspaceId)):
        raise HTTPException(400,"Invalid workspace locator")
    if not 1<=revision<=10000 or len(manifestSha256)!=64:
        raise HTTPException(400,"Invalid workspace revision")
    key=request.cookies.get("swrlz_hf_sid")
    with _lock:
        session=_sessions.get(key) if key else None
        if not session:raise HTTPException(404,"Project unavailable")
        thread=next((t for t in session.get("threads",[]) if t.get("id")==threadId),None)
        workspace=next((w for w in (thread or {}).get("autoProjectWorkspaces",[])
                        if w.get("id")==workspaceId),None)
        if not workspace or workspace.get("revision")!=revision or workspace.get("manifestSha256")!=manifestSha256:
            raise HTTPException(404,"Project revision unavailable")
        saved=copy.deepcopy(workspace)
    try:package=package_project(saved)
    except AutoWorkspaceError as exc:raise HTTPException(409,str(exc)) from exc
    filename=package["filename"].replace('"',"")
    return Response(content=package["body"],media_type="application/zip",
        headers={"Content-Disposition":f'attachment; filename="{filename}"',
                 "Cache-Control":"private, no-store","X-Content-Type-Options":"nosniff",
                 "Cross-Origin-Resource-Policy":"same-origin",
                 "X-Code-Package-Sha256":package["sha256"],
                 "X-Code-Package-Files":str(package["fileCount"])})


@app.post("/api/chat_state")
async def mutate(request:Request):
    key,s=_session(request)
    body=await request.json()
    if body.get("contract")!="swrlz-chat-account-mutation-v1":raise HTTPException(400,"Invalid state contract")
    with _lock:
        if int(body.get("expectedRevision",-1))!=s["revision"]:
            return JSONResponse(_snapshot(s),status_code=409)
        for op in body.get("operations",[]):
            kind=op.get("type"); tid=op.get("threadId")
            if kind=="SET_CURRENT_THREAD" and any(t["id"]==tid for t in s["threads"]):s["currentId"]=tid
            elif kind=="DELETE_THREAD":
                s["threads"]=[t for t in s["threads"] if t["id"]!=tid]
                if s["currentId"]==tid:s["currentId"]=s["threads"][0]["id"] if s["threads"] else ""
            elif kind=="UPSERT_THREAD" and tid:
                t=next((t for t in s["threads"] if t["id"]==tid),None)
                if t is None:
                    t={"id":tid,"title":str(op.get("title") or "New conversation")[:120],"pinned":False,"messagePins":{},"codeArtifacts":[],"createdAt":time.time()*1000,"messages":[]}
                    s["threads"].append(t)
                for k in ("title","pinned"):
                    if k in op:t[k]=op[k]
            elif kind=="SET_MESSAGE_PINNED" and tid:
                t=next((t for t in s["threads"] if t["id"]==tid),None)
                if t is None:raise HTTPException(404,"Thread not found")
                mid=str(op.get("messageId") or "").strip()
                if not mid:raise HTTPException(400,"Message id required")
                pins=t.setdefault("messagePins",{})
                if bool(op.get("pinned")):
                    pins[mid]=True
                    message=next((m for m in t.get("messages",[]) if str(m.get("id") or "")==mid),None)
                    if message is not None:_promote_pinned_code_artifact(t,message)
                else:pins.pop(mid,None)
            else:raise HTTPException(400,"Unsupported state operation")
        s["revision"]+=1
        return {"ok":True,"revision":s["revision"]}

def _code_fences(text):
    import re
    return re.findall(r"```[^\n]*\n[\s\S]*?```",str(text or ""))

def _parse_code_files(text):
    import re
    files=[]
    pattern=re.compile(r"```([^\n]*)\n([\s\S]*?)```")
    for index,match in enumerate(pattern.finditer(str(text or "")),start=1):
        header=str(match.group(1) or "").strip()
        parts=header.split()
        language=parts[0] if parts and "=" not in parts[0] else "text"
        if language.lower()=="project-manifest":continue  # Manifest is metadata, never downloadable source.
        attrs={}
        for part in parts[1:] if parts and "=" not in parts[0] else parts:
            if "=" in part:
                key,value=part.split("=",1);attrs[key.strip().lower()]=value.strip().strip('"').strip("'")
        path=attrs.get("file") or attrs.get("path") or ("code."+({"python":"py","javascript":"js","typescript":"ts","html":"html","css":"css","java":"java","kotlin":"kt","cpp":"cpp","c":"c","json":"json"}.get(language.lower(),"txt")) if index==1 else f"file-{index}.txt")
        files.append({"path":path[:240],"language":language[:40],"content":match.group(2)})
    return files

def _artifact_markdown(files):
    chunks=[]
    for item in files or []:
        language=str(item.get("language") or "text")
        path=str(item.get("path") or "code.txt")
        chunks.append(f"```{language} file={path}\n{str(item.get('content') or '')}```")
    return "\n\n".join(chunks)

def _find_artifact(thread,artifact_id):
    return next((a for a in thread.get("codeArtifacts",[]) if str(a.get("id") or "")==str(artifact_id or "")),None)

def _artifact_for_message(thread,message_id):
    return next((a for a in thread.get("codeArtifacts",[]) if str(a.get("sourceMessageId") or "")==str(message_id or "")),None)

def _artifact_source_hash(files):
    normalized=[
        {
            "path":str(item.get("path") or ""),
            "language":str(item.get("language") or ""),
            "content":str(item.get("content") or ""),
        }
        for item in (files or [])
        if isinstance(item,dict)
    ]
    payload=json.dumps(normalized,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _artifact_revision_record(artifact,revision):
    target=int(revision or 0)
    for item in artifact.get("revisions") or []:
        if isinstance(item,dict) and int(item.get("revision") or 0)==target:
            return item
    return None


def _artifact_revision_markdown(artifact,revision):
    record=_artifact_revision_record(artifact,revision)
    files=copy.deepcopy((record or {}).get("files") or [])
    return _artifact_markdown(files)[:12000] if files else ""


def _create_code_artifact(thread,message,request_id,text):
    files=[item for item in _parse_code_files(text)
           if str(item.get("language") or "").lower() not in {"lyrics","lyric","song","music","verse","chorus"}]
    if not files:return None
    existing=_artifact_for_message(thread,message.get("id"))
    if existing:return existing
    artifact_id="artifact-"+uuid.uuid4().hex
    now=int(time.time()*1000)
    source_hash=_artifact_source_hash(files)
    requested_text=next((
        str(item.get("text") or "") for item in reversed(thread.get("messages") or [])
        if item.get("role")=="user" and str((item.get("meta") or {}).get("requestId") or "")==str(request_id or "")
    ), "")
    archive_requested=wants_archive(requested_text)
    revision={
        "revision":1,
        "requestId":str(request_id or ""),
        "createdAt":now,
        "sourceHash":source_hash,
        "archiveRequested":archive_requested,
        "files":copy.deepcopy(files),
    }
    artifact={
        "id":artifact_id,
        "type":"code",
        "sourceMessageId":str(message.get("id") or ""),
        "title":files[0]["path"],
        "currentRevision":1,
        "currentSourceHash":source_hash,
        "files":copy.deepcopy(files),
        "revisions":[revision],
        "createdAt":now,
        "updatedAt":now,
    }
    thread.setdefault("codeArtifacts",[]).append(artifact)
    message.setdefault("meta",{})["codeArtifactId"]=artifact_id
    message["meta"]["artifactRevision"]=1
    message["meta"]["artifactSourceHash"]=source_hash
    return artifact

def _promote_pinned_code_artifact(thread,message):
    if message.get("role")!="assistant" or "```" not in str(message.get("text") or ""):return None
    existing=_artifact_for_message(thread,message.get("id"))
    if existing:return existing
    return _create_code_artifact(thread,message,(message.get("meta") or {}).get("requestId"),message.get("text"))

def _artifact_context_item(thread,message):
    artifact=_artifact_for_message(thread,message.get("id"))
    if artifact is None:
        meta=message.get("meta") if isinstance(message.get("meta"),dict) else {}
        artifact_id=str(meta.get("codeArtifactId") or meta.get("updatedCodeArtifactId") or "")
        if artifact_id:
            artifact=_find_artifact(thread,artifact_id)
    if artifact is None:
        artifact=_promote_pinned_code_artifact(thread,message)
    if artifact is None:
        return {"messageId":message.get("id"),"role":str(message.get("role") or "").upper(),"text":str(message.get("text") or "")[:12000],"pinned":True}
    files=copy.deepcopy(artifact.get("files") or [])
    source_hash=str(artifact.get("currentSourceHash") or "") or _artifact_source_hash(files)
    return {
        "messageId":message.get("id"),
        "role":str(message.get("role") or "").upper(),
        "text":_artifact_markdown(files)[:12000],
        "pinned":True,
        "artifactType":"code",
        "artifactId":artifact.get("id"),
        "artifactTitle":artifact.get("title"),
        "artifactRevision":int(artifact.get("currentRevision") or 1),
        "artifactSourceHash":source_hash,
        "files":[{"path":f.get("path"),"language":f.get("language")} for f in files],
    }

def _commit_code_artifact_revision(artifact,text,request_id,base_revision=0,base_source_hash="",archive_requested=False):
    files=_parse_code_files(text)
    if not files:return False,"NO_CODE"
    current=int(artifact.get("currentRevision") or 0)
    current_files=copy.deepcopy(artifact.get("files") or [])
    current_hash=str(artifact.get("currentSourceHash") or "") or _artifact_source_hash(current_files)
    requested_revision=int(base_revision or 0)
    requested_hash=str(base_source_hash or "")
    if requested_revision<=0:
        return False,"BASE_REVISION_REQUIRED"
    if requested_revision!=current:
        return False,"REVISION_CONFLICT"
    if not requested_hash:
        return False,"SOURCE_HASH_REQUIRED"
    if requested_hash!=current_hash:
        return False,"SOURCE_HASH_CONFLICT"
    next_revision=current+1
    now=int(time.time()*1000)
    next_hash=_artifact_source_hash(files)
    artifact.setdefault("revisions",[]).append({
        "revision":next_revision,
        "requestId":str(request_id or ""),
        "createdAt":now,
        "sourceHash":next_hash,
        "archiveRequested":bool(archive_requested),
        "parentRevision":current,
        "parentSourceHash":current_hash,
        "files":copy.deepcopy(files),
    })
    artifact["currentRevision"]=next_revision
    artifact["currentSourceHash"]=next_hash
    artifact["files"]=copy.deepcopy(files)
    artifact["updatedAt"]=now
    if files:artifact["title"]=artifact.get("title") or files[0]["path"]
    return True,"COMMITTED"

def _select_staged_workspace(thread,prompt):
    """Explicit user follow-up only; unrelated chat cannot alter a project."""
    import re
    workspaces=thread.get("autoProjectWorkspaces") or []
    if not workspaces:return None
    latest=workspaces[-1]
    p=str(prompt or "").strip().lower()
    is_continuation=bool(re.search(
        r"\b(?:continue(?: this| the)? project|keep going|next (?:file|files|part|step)|finish (?:the )?project|resume (?:the )?project|continue)\b",p))
    refers_to_file=any(str(path).lower() in p for path in latest.get("requiredFiles",[]))
    return latest if is_continuation or refers_to_file else None


def _stage_completed_generation(thread, payload, text, request_id, artifact):
    """Commit only finalized typed files; source owner remains codeArtifacts."""
    try:
        manifest=parse_manifest(text)
        selected=payload.get("stagedProject") if isinstance(payload.get("stagedProject"),dict) else {}
        workspaces=thread.setdefault("autoProjectWorkspaces",[])
        if manifest is not None:
            if len(workspaces)>=4:raise AutoWorkspaceError("Project workspace limit reached")
            workspace=create_auto_workspace(manifest,"workspace-"+uuid.uuid4().hex,request_id)
            workspaces.append(workspace)
        elif selected.get("id"):
            workspace=next((w for w in workspaces if w.get("id")==selected.get("id")),None)
            if workspace is None or workspace.get("revision")!=selected.get("revision"):
                raise AutoWorkspaceError("PROJECT_REVISION_CONFLICT")
        else:return None
        files=[item for item in _parse_code_files(text)
               if str(item.get("language") or "").lower() not in {"lyrics","lyric","song","music","verse","chorus"}]
        result="MANIFEST_ACCEPTED"
        if files:
            if artifact is None:raise AutoWorkspaceError("NO_SOURCE_ARTIFACT")
            previous=workspace
            workspace,result=stage_files(workspace,files,expected_revision=workspace["revision"],
                request_id=request_id,artifact_id=str(artifact.get("id") or ""),
                artifact_revision=int(artifact.get("currentRevision") or 0),
                artifact_source_hash=str(artifact.get("currentSourceHash") or ""),
                allow_replace=bool(selected.get("allowReplace")))
            workspaces[workspaces.index(previous)]=workspace
        return {"status":result,"project":project_view(workspace)}
    except AutoWorkspaceError as exc:
        return {"status":"REJECTED","error":str(exc)[:160]}


def _response_prose(text):
    prose=str(text or "")
    for fence in _code_fences(prose):prose=prose.replace(fence,"")
    return prose.strip()


def _history_projection(thread):
    projected=[]
    for message in thread.get("messages") or []:
        if message.get("role") not in ("user","assistant"):
            continue
        meta=copy.deepcopy(message.get("meta") or {})
        artifact_id=str(meta.get("codeArtifactId") or meta.get("updatedCodeArtifactId") or "")
        if artifact_id:
            artifact=_find_artifact(thread,artifact_id)
            revision=int(meta.get("artifactRevision") or 0)
            if artifact is not None and revision>0:
                record=_artifact_revision_record(artifact,revision)
                if record is not None:
                    source_hash=str(record.get("sourceHash") or "") or _artifact_source_hash(record.get("files") or [])
                    meta["codeArtifactId"]=artifact_id
                    meta["artifactRevision"]=revision
                    meta["artifactSourceHash"]=source_hash
                    meta["artifactSourceSnapshot"]=_artifact_markdown(record.get("files") or [])[:12000]
        projected.append({
            "id":message.get("id"),
            "role":message["role"],
            "text":message["text"],
            "createdAt":message.get("createdAt"),
            "meta":meta,
        })
    return projected


def _run(key,request_id,model_id,payload,assistant_id):
    with _lock:
        s=_sessions[key];g=s["activeGeneration"];g["phase"]="GENERATING"
        g["startedAtUnixMs"]=int(time.time()*1000)
        g["queueWaitMs"]=max(0,g["startedAtUnixMs"]-int(g.get("acceptedAtUnixMs") or g["startedAtUnixMs"]))
        g["status"].append({"phase":"GENERATING","reason":"Workstation admitted generation"})
    try:
        if model_id=="r39" and _generate is None:raise RuntimeError("R39 generator is not installed")
        if model_id=="stock" and _stock_generate is None:raise RuntimeError("Original HF generator is not installed")
        text=""; completed=False
        cancelled=False
        for event in dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate):
            with _lock:
                active=s.get("activeGeneration")
                if not active or active.get("requestId")!=request_id:return
                if active.get("cancelRequested"):
                    cancelled=True
                    break
            if not isinstance(event,dict):continue
            kind=str(event.get("type") or "")
            persist_event=None
            with _lock:
                g=s["activeGeneration"]
                if not g or g["requestId"]!=request_id:return
                g["lastSeq"]+=1
                if kind=="DELTA":
                    delta=str(event.get("text") or "");text+=delta;g["text"]=text
                elif kind=="DIAGNOSTIC":
                    trace=event.get("trace")
                    if isinstance(trace,dict):g["diagnosticTrace"]=copy.deepcopy(trace)
                    g["status"].append({"seq":g["lastSeq"],"phase":"DIAGNOSTIC_READY","reason":""})
                elif kind=="MEMORY_CANDIDATE":
                    candidate=event.get("candidate")
                    if isinstance(candidate,dict):g.setdefault("memoryCandidates",[]).append(copy.deepcopy(candidate))
                    g["status"].append({"seq":g["lastSeq"],"phase":"MEMORY_CANDIDATE","reason":""})
                elif kind=="RESPONSE_COGNITION":
                    state=event.get("state")
                    if isinstance(state,dict):g["responseCognition"]=copy.deepcopy(state)
                    g["status"].append({"seq":g["lastSeq"],"phase":"RESPONSE_COGNITION","reason":""})
                elif kind=="ROUTE":
                    selected=str(event.get("selectedModelId") or g.get("selectedModelId") or model_id)[:80]
                    requested=str(event.get("requestedModelId") or g.get("requestedModelId") or model_id)[:80]
                    g["requestedModelId"]=requested
                    g["selectedModelId"]=selected
                    g["status"].append({"seq":g["lastSeq"],"phase":str(event.get("phase") or "MODEL_ROUTE"),"reason":str(event.get("reason") or "")[:200],"categories":["MODEL_ROUTE"],"provider":selected})
                elif kind=="ONLINE_TRACE":
                    trace=event.get("trace") if isinstance(event.get("trace"),dict) else {}
                    if trace:
                        trace={str(k)[:64]:copy.deepcopy(v) for k,v in trace.items() if k in {"contract","phase","provider","site","url","activity","atUnixMs","httpStatus","resultCount","responseBytes","errorType"}}
                        g.setdefault("onlineTrace",[]).append(trace)
                        g["onlineTrace"]=g["onlineTrace"][-64:]
                        g["status"].append({
                            "seq":g["lastSeq"],
                            "phase":str(trace.get("phase") or "ONLINE_VISIT"),
                            "reason":str(trace.get("activity") or "")[:200],
                            "categories":["ONLINE_RESEARCH","SEARCH","FETCH"],
                            "site":str(trace.get("site") or "")[:180],
                            "url":str(trace.get("url") or "")[:1000],
                            "provider":str(trace.get("provider") or "")[:120],
                            "httpStatus":trace.get("httpStatus"),
                            "resultCount":trace.get("resultCount"),
                        })
                elif kind=="ONLINE_RESEARCH":
                    result=event.get("result") if isinstance(event.get("result"),dict) else {}
                    sources=event.get("sources") if isinstance(event.get("sources"),list) else []
                    if event.get("requestedModelId"):g["requestedModelId"]=str(event.get("requestedModelId"))[:80]
                    if event.get("selectedModelId"):g["selectedModelId"]=str(event.get("selectedModelId"))[:80]
                    g["onlineResearch"]=copy.deepcopy(result)
                    g["sources"]=[copy.deepcopy(item) for item in sources if isinstance(item,dict)][:24]
                    g["status"].append({"seq":g["lastSeq"],"phase":"ONLINE_RESEARCH","reason":str(result.get("status") or ""),"categories":["ONLINE_RESEARCH",str(result.get("kind") or "").upper()]})
                    source_sites=[]
                    for item in g["sources"]:
                        try:
                            host=str(urllib.parse.urlsplit(str(item.get("url") or "")).hostname or "").lower()
                        except Exception:
                            host=""
                        if host and host not in source_sites:source_sites.append(host)
                    trace=copy.deepcopy((g.get("onlineTrace") or [])[-64:])
                    online_log={
                        "schema":"swrlz-online-research-log-v1",
                        "research":copy.deepcopy(result),
                        "trace":trace,
                        "sourceSites":source_sites[:24],
                        "widgetKinds":copy.deepcopy(result.get("widgetKinds") or []),
                        "requestedModelId":str(g.get("requestedModelId") or model_id)[:80],
                        "selectedModelId":str(g.get("selectedModelId") or model_id)[:80],
                        "rawPromptStored":False,
                        "historyStored":False,
                        "preciseLocationStored":False,
                    }
                    g["onlineLogPersistence"]={"state":"QUEUED","tracePath":"runtime-diagnostics/online-research/"+request_id+"/online-research-trace.json","outcomePath":"runtime-diagnostics/online-research/"+request_id+"/online-research-outcome.json","branch":"runtime"}
                    persist_event=("ONLINE_RESEARCH_TRACE",online_log)
                elif kind=="WIDGET":
                    widget=event.get("widget") if isinstance(event.get("widget"),dict) else {}
                    if widget:g.setdefault("widgets",[]).append(copy.deepcopy(widget))
                    g["status"].append({"seq":g["lastSeq"],"phase":"WIDGET_READY","reason":str(widget.get("kind") or ""),"categories":["WIDGET"]})
                elif kind=="PROGRAMMING_INTENT":
                    intent=event.get("intent")
                    if isinstance(intent,dict):
                        g["programmingIntent"]=copy.deepcopy(intent)
                        contract=intent.get("intentContract")
                        if isinstance(contract,dict):g["intentContract"]=copy.deepcopy(contract)
                        evidence=intent.get("failureEvidence")
                        if isinstance(evidence,dict):g["failureEvidence"]=copy.deepcopy(evidence)
                        constraints=intent.get("repairConstraints")
                        if isinstance(constraints,dict):g["repairConstraints"]=copy.deepcopy(constraints)
                        behavior=intent.get("behaviorLedger")
                        if isinstance(behavior,dict):g["behaviorLedger"]=copy.deepcopy(behavior)
                        repair_base=intent.get("behaviorRepairBase")
                        if isinstance(repair_base,dict):g["behaviorRepairBase"]=copy.deepcopy(repair_base)
                    g["status"].append({"seq":g["lastSeq"],"phase":"PROGRAMMING_INTENT","reason":""})
                elif kind in ("REPAIR_DIAGNOSTIC","REPAIR_OUTCOME_DIAGNOSTIC"):
                    diagnostic=event.get("diagnostic") if isinstance(event.get("diagnostic"),dict) else {}
                    g.setdefault("repairDiagnostics",[]).append({"type":kind,"diagnostic":copy.deepcopy(diagnostic)})
                    g["status"].append({"seq":g["lastSeq"],"phase":kind,"reason":""})
                    if diagnostic:
                        persist_event=(kind,copy.deepcopy(diagnostic))
                elif kind=="CANDIDATE_ATTEMPT":
                    attempt=event.get("attempt") if isinstance(event.get("attempt"),dict) else {}
                    if attempt:
                        g.setdefault("candidateAttempts",[]).append(copy.deepcopy(attempt))
                    g["status"].append({"seq":g["lastSeq"],"phase":"CANDIDATE_ATTEMPT","reason":"attempt="+str(attempt.get("attempt") or "")})
                elif kind=="GENERATION_TELEMETRY":
                    telemetry=event.get("telemetry") if isinstance(event.get("telemetry"),dict) else {}
                    if telemetry:
                        g["generationTelemetry"]=copy.deepcopy(telemetry)
                    g["status"].append({"seq":g["lastSeq"],"phase":"GENERATION_TELEMETRY","reason":""})
                elif kind=="CANDIDATE_VALIDATION":
                    validation=event.get("validation") if isinstance(event.get("validation"),dict) else {}
                    g["candidateValidation"]=copy.deepcopy(validation)
                    g["status"].append({"seq":g["lastSeq"],"phase":"CANDIDATE_"+str(validation.get("status") or "UNKNOWN"),"reason":",".join(str(x) for x in (validation.get("reasons") or []))[:200]})
                elif kind=="CONTEXT":
                    g["contextBudget"]={
                        "contextWindowTokens":int(event.get("contextWindowTokens") or 0),
                        "inputBudgetTokens":int(event.get("inputBudgetTokens") or 0),
                        "estimatedInputTokens":int(event.get("estimatedInputTokens") or 0),
                        "reservedOutputTokens":int(event.get("reservedOutputTokens") or 0),
                        "historyMessagesDropped":int(event.get("historyMessagesDropped") or 0),
                        "historyMessagesKept":int(event.get("historyMessagesKept") or 0),
                        "repairTurn":bool(event.get("repairTurn")),
                        "repairContext":copy.deepcopy(event.get("repairContext") or {}),
                        "tokenBreakdown":copy.deepcopy(event.get("tokenBreakdown") or {}),
                    }
                    g["status"].append({"seq":g["lastSeq"],"phase":"CONTEXT_BUDGETED","reason":""})
                elif kind=="RESOURCE":
                    g["resourcePlan"]={
                        "cpuCapacity":int(event.get("cpuCapacity") or 1),
                        "decodeThreads":int(event.get("decodeThreads") or 1),
                        "batchThreads":int(event.get("batchThreads") or 1),
                        "maxResponseTokens":int(event.get("maxResponseTokens") or 0),
                    }
                    g["status"].append({"seq":g["lastSeq"],"phase":"RESOURCE_ALLOCATED","reason":"Workstation inference budget active"})
                elif kind in ("COMPLETE","COMPLETED"):
                    g["engineCompletionTelemetry"]={
                        "totalLatencyMs":event.get("totalLatencyMs"),
                        "loadLatencyMs":event.get("loadLatencyMs"),
                        "firstDeltaLatencyMs":event.get("firstDeltaLatencyMs"),
                    }
                    g["status"].append({"seq":g["lastSeq"],"phase":"COMPLETE","reason":""})
                else:g["status"].append({"seq":g["lastSeq"],"phase":str(event.get("phase") or kind),"reason":str(event.get("reason") or "")[:200],"categories":[str(x)[:80] for x in (event.get("categories") or [])[:16]] if isinstance(event.get("categories"),list) else []})
            if persist_event is not None:
                persist_kind,persist_payload=persist_event
                if persist_kind=="ONLINE_RESEARCH_TRACE":
                    def persist_online_log(kind=persist_kind,document=persist_payload):
                        result=persist_runtime_diagnostic(request_id,str(document.get("selectedModelId") or model_id),kind,document)
                        with _lock:
                            current=s.get("activeGeneration")
                            if current and current.get("requestId")==request_id:
                                persistence=copy.deepcopy(current.get("onlineLogPersistence") or {})
                                persistence["trace"]=copy.deepcopy(result)
                                current["onlineLogPersistence"]=persistence
                            target_thread=next((t for t in s.get("threads",[]) if t.get("id")==payload.get("threadId")),None)
                            if target_thread:
                                target_message=next((m for m in reversed(target_thread.get("messages",[])) if str(m.get("id") or "")==str(assistant_id)),None)
                                if target_message is not None:
                                    target_message.setdefault("meta",{})["onlineLogPersistence"]=copy.deepcopy(result)
                            s["revision"]+=1
                    threading.Thread(target=persist_online_log,daemon=True,name="online-log-"+request_id[:8]).start()
                else:
                    threading.Thread(
                        target=persist_runtime_diagnostic,
                        args=(request_id,model_id,persist_kind,persist_payload),
                        daemon=True,
                        name="runtime-diagnostic-"+request_id[:8],
                    ).start()
            if kind=="FAILED":raise RuntimeError(str(event.get("reason") or "Generation failed"))
            if kind in ("COMPLETE","COMPLETED"):completed=True
        if cancelled:
            with _lock:
                g=s.get("activeGeneration")
                if g and g.get("requestId")==request_id:
                    g.update(terminal=True,terminalType="CANCELLED",phase="CANCELLED")
                    g["status"].append({"phase":"CANCELLED","reason":"Stopped by user"});s["revision"]+=1
            return
        if not text:raise RuntimeError("R39 emitted no DELTA")
        github_telemetry=None
        online_outcome=None
        knowledge_snapshot=None
        with _lock:
            g=s["activeGeneration"]
            completed_ms=int(time.time()*1000)
            g.update(terminal=True,terminalType="COMPLETE",phase="COMPLETE",completedAtUnixMs=completed_ms)
            started_ms=int(g.get("startedAtUnixMs") or completed_ms)
            accepted_ms=int(g.get("acceptedAtUnixMs") or started_ms)
            g["stationTiming"]={
                "acceptedAtUnixMs":accepted_ms,
                "startedAtUnixMs":started_ms,
                "completedAtUnixMs":completed_ms,
                "queueWaitMs":int(g.get("queueWaitMs") or 0),
                "stationRunMs":max(0,completed_ms-started_ms),
                "endToEndMs":max(0,completed_ms-accepted_ms),
            }
            thread=next(t for t in s["threads"] if t["id"]==payload["threadId"])
            intent=g.get("programmingIntent") if isinstance(g.get("programmingIntent"),dict) else {}
            if intent.get("codingTask"):
                thread["programmingState"]=copy.deepcopy(intent)
            validation=g.get("candidateValidation") if isinstance(g.get("candidateValidation"),dict) else {}
            rejected=validation.get("status")=="REJECT"
            if rejected:
                g.update(terminalType="CANDIDATE_REJECTED",phase="CANDIDATE_REJECTED")
            generation_telemetry=copy.deepcopy(g.get("generationTelemetry") or {})
            station_timing=copy.deepcopy(g.get("stationTiming") or {})
            behavior=intent.get("behaviorLedger") if isinstance(intent.get("behaviorLedger"),dict) else {}
            behavior_base=intent.get("behaviorRepairBase") if isinstance(intent.get("behaviorRepairBase"),dict) else {}
            behavior_camera={
                "currentScore":copy.deepcopy(behavior.get("currentScore")),
                "bestKnownScore":copy.deepcopy(behavior.get("bestKnownScore")),
                "regressedCases":copy.deepcopy((behavior.get("regressedCases") or [])[:20]),
                "resolvedCases":copy.deepcopy((behavior.get("resolvedCases") or [])[:20]),
                "preservePassingCases":copy.deepcopy((behavior.get("preservePassingCases") or [])[:30]),
                "rebaseRecommended":bool(behavior.get("rebaseRecommended")),
                "bestKnownArtifact":copy.deepcopy(behavior.get("bestKnownArtifact")),
                "repairBaseMode":behavior_base.get("mode"),
            }
            response_cognition=copy.deepcopy(g.get("responseCognition") or {})
            programming_telemetry={
                "schema":"swrlz-station-programming-telemetry-v3",
                "generation":generation_telemetry,
                "station":station_timing,
                "repairConstraints":copy.deepcopy(intent.get("repairConstraints") or {}),
                "behaviorLedger":behavior_camera,
                "structuredReceipt":copy.deepcopy(((intent.get("failureEvidence") or {}).get("receiptSemantics") or {}).get("structuredReceipt") or {}),
            } if intent.get("codingTask") else None
            telemetry_meta={}
            if response_cognition: telemetry_meta["responseCognition"]=response_cognition
            online_research=copy.deepcopy(g.get("onlineResearch") or {})
            online_sources=copy.deepcopy((g.get("sources") or [])[:24])
            online_widgets=copy.deepcopy((g.get("widgets") or [])[:8])
            online_trace=copy.deepcopy((g.get("onlineTrace") or [])[-64:])
            online_log_persistence=copy.deepcopy(g.get("onlineLogPersistence") or {})
            if online_research: telemetry_meta["onlineResearch"]=online_research
            if online_sources: telemetry_meta["sources"]=online_sources
            if online_widgets: telemetry_meta["widgets"]=online_widgets
            if online_research:
                telemetry_meta["onlineModelRoute"]={
                    "requestedModelId":str(g.get("requestedModelId") or model_id)[:80],
                    "selectedModelId":str(g.get("selectedModelId") or model_id)[:80],
                }
            if online_trace: telemetry_meta["onlineTrace"]=online_trace
            if online_log_persistence: telemetry_meta["onlineLogPersistence"]=online_log_persistence
            if programming_telemetry: telemetry_meta["programmingTelemetry"]=programming_telemetry
            artifact_id=str(intent.get("artifactTargetId") or "")
            artifact=_find_artifact(thread,artifact_id) if artifact_id and intent.get("artifactMutationRequested") and not rejected else None
            if artifact is not None:
                committed,reason=_commit_code_artifact_revision(
                    artifact,
                    text,
                    request_id,
                    int(intent.get("baseRevision") or 0),
                    str(intent.get("baseSourceHash") or ""),
                    archive_requested=wants_archive(next((
                        str(entry.get("text") or "") for entry in reversed(thread.get("messages") or [])
                        if entry.get("role")=="user" and str((entry.get("meta") or {}).get("requestId") or "")==request_id
                    ), "")),
                )
                if committed:
                    current_hash=str(artifact.get("currentSourceHash") or "")
                    prose=_response_prose(text) or ("Updated pinned code artifact to revision "+str(artifact["currentRevision"])+".")
                    message={
                        "id":assistant_id,
                        "role":"assistant",
                        "text":prose,
                        "createdAt":int(time.time()*1000),
                        "meta":{
                            "requestId":request_id,
                            "modelId":model_id,
                            "state":"COMPLETE",
                            "updatedCodeArtifactId":artifact["id"],
                            "codeArtifactId":artifact["id"],
                            "artifactRevision":artifact["currentRevision"],
                            "artifactSourceHash":current_hash,
                            **telemetry_meta,
                        },
                    }
                    thread["messages"].append(message)
                    g["artifactReceipt"]={
                        "action":"REVISION_COMMITTED",
                        "artifactId":artifact["id"],
                        "revision":artifact["currentRevision"],
                        "sourceHash":current_hash,
                        "baseRevision":int(intent.get("baseRevision") or 0),
                        "baseSourceHash":str(intent.get("baseSourceHash") or ""),
                    }
                else:
                    message={"id":assistant_id,"role":"assistant","text":_response_prose(text) or text,"createdAt":int(time.time()*1000),"meta":{"requestId":request_id,"modelId":model_id,"state":"COMPLETE","artifactMutationRejected":reason,**telemetry_meta}}
                    thread["messages"].append(message)
                    g["artifactReceipt"]={
                        "action":"REVISION_REJECTED",
                        "artifactId":artifact["id"],
                        "reason":reason,
                        "requestedBaseRevision":int(intent.get("baseRevision") or 0),
                        "requestedBaseSourceHash":str(intent.get("baseSourceHash") or ""),
                        "currentRevision":int(artifact.get("currentRevision") or 0),
                        "currentSourceHash":str(artifact.get("currentSourceHash") or ""),
                    }
            else:
                assistant_tag=_container_content_tag(text)
                state="CANDIDATE_REJECTED" if rejected else "COMPLETE"
                message={"id":assistant_id,"role":"assistant","text":text,"createdAt":int(time.time()*1000),"meta":{"requestId":request_id,"modelId":model_id,"state":state,**({"contentTag":assistant_tag} if assistant_tag else {}),**telemetry_meta}}
                thread["messages"].append(message)
                if rejected:
                    g["artifactReceipt"]={"action":"CANDIDATE_REJECTED","reasons":copy.deepcopy(validation.get("reasons") or [])}
                else:
                    artifact=_create_code_artifact(thread,message,request_id,text)
                    if artifact is not None:
                        g["artifactReceipt"]={"action":"ARTIFACT_CREATED","artifactId":artifact["id"],"revision":1,"sourceHash":artifact.get("currentSourceHash")}
            # Only completed, accepted generations may advance a staged project.
            if not rejected and message.get("meta",{}).get("state")=="COMPLETE":
                receipt=_stage_completed_generation(thread,payload,text,request_id,artifact)
                if receipt:
                    message.setdefault("meta",{})["projectWorkspaceReceipt"]=copy.deepcopy(receipt)
                    g["projectWorkspaceReceipt"]=copy.deepcopy(receipt)
                    g["status"].append({"phase":"PROJECT_FILES_STAGED",
                        "reason":str(receipt.get("status") or "")[:80]})
            if online_research:
                # Durable Online Research diagnostics consume the same bounded server
                # telemetry projected to Chat.  The browser must never be the richest
                # authority for a server-owned generation.  Keep prompt/history/private
                # reasoning and precise coordinates out of the repository camera.
                bounded_sources=[]
                for item in online_sources[:24]:
                    if not isinstance(item,dict):continue
                    bounded_sources.append({
                        "title":str(item.get("title") or item.get("name") or "")[:300],
                        "source":str(item.get("source") or item.get("provider") or "")[:180],
                        "url":str(item.get("url") or "")[:1200],
                        "snippet":str(item.get("snippet") or "")[:1200],
                        "rank":item.get("rank") if isinstance(item.get("rank"),(int,float)) else None,
                    })
                online_outcome={
                    "schema":"swrlz-online-research-outcome-v2",
                    "terminalState":str(g.get("terminalType") or "COMPLETE")[:80],
                    "research":online_research,
                    "trace":copy.deepcopy((g.get("onlineTrace") or [])[-64:]),
                    "sources":bounded_sources,
                    "sourceSites":sorted({str(urllib.parse.urlsplit(str(item.get("url") or "")).hostname or "").lower() for item in online_sources if item.get("url")})[:24],
                    "widgets":copy.deepcopy(online_widgets[:8]),
                    "widgetKinds":[str(item.get("kind") or "")[:80] for item in online_widgets if isinstance(item,dict)][:8],
                    "statusTrail":copy.deepcopy((g.get("status") or [])[-128:]),
                    "responseCognition":copy.deepcopy(g.get("responseCognition") or {}),
                    "programmingIntent":copy.deepcopy(g.get("programmingIntent") or {}),
                    "candidateValidation":copy.deepcopy(g.get("candidateValidation") or {}),
                    "candidateAttempts":copy.deepcopy((g.get("candidateAttempts") or [])[-16:]),
                    "generationTelemetry":copy.deepcopy(g.get("generationTelemetry") or {}),
                    "engineCompletionTelemetry":copy.deepcopy(g.get("engineCompletionTelemetry") or {}),
                    "contextBudget":copy.deepcopy(g.get("contextBudget") or {}),
                    "resourcePlan":copy.deepcopy(g.get("resourcePlan") or {}),
                    "finalResponse":str(text or "")[:24000],
                    "finalResponseSha256":hashlib.sha256(str(text or "").encode("utf-8")).hexdigest(),
                    "requestedModelId":str(g.get("requestedModelId") or model_id)[:80],
                    "selectedModelId":str(g.get("selectedModelId") or model_id)[:80],
                    "stationTiming":station_timing,
                    "rawPromptStored":False,
                    "historyStored":False,
                    "preciseLocationStored":False,
                    "privateReasoningStored":False,
                }
            if online_research:
                knowledge_snapshot=_bounded_knowledge_snapshot(
                    request_id,payload.get("prompt"),online_research,online_trace,
                    online_sources,online_widgets,text,g.get("status") or []
                )
            if intent.get("codingTask") and generation_telemetry:
                github_telemetry={
                    "schema":"swrlz-station-programming-log-v1",
                    "generationTelemetry":generation_telemetry,
                    "stationTiming":station_timing,
                    "candidateValidation":{
                        "status":validation.get("status"),
                        "reasons":[str(x)[:160] for x in (validation.get("reasons") or [])[:8]],
                        "detectedLanguages":copy.deepcopy(validation.get("detectedLanguages") or []),
                        "activeRepairConstraints":copy.deepcopy(validation.get("activeRepairConstraints") or {}),
                        "behaviorLedger":copy.deepcopy(validation.get("behaviorLedger") or {}),
                        "structuredReceipt":copy.deepcopy(validation.get("structuredReceipt") or {}),
                        "executionVerified":validation.get("executionVerified"),
                        "verificationState":validation.get("verificationState"),
                    },
                    "repairConstraints":copy.deepcopy(intent.get("repairConstraints") or {}),
                    "behaviorLedger":behavior_camera,
                    "behaviorRepairBase":copy.deepcopy(intent.get("behaviorRepairBase") or {}),
                    "structuredReceipt":copy.deepcopy(((intent.get("failureEvidence") or {}).get("receiptSemantics") or {}).get("structuredReceipt") or {}),
                    "artifactReceipt":{
                        "action":(g.get("artifactReceipt") or {}).get("action"),
                        "revision":(g.get("artifactReceipt") or {}).get("revision"),
                        "sourceHash":(g.get("artifactReceipt") or {}).get("sourceHash"),
                        "reason":(g.get("artifactReceipt") or {}).get("reason"),
                    },
                }
                g["githubTelemetryPersistence"]={"state":"QUEUED","path":"runtime-diagnostics/programming/"+request_id+"/candidate-attempt-telemetry.json","branch":"runtime"}
            s["revision"]+=1
        if online_outcome is not None:
            def persist_online_outcome():
                result=persist_runtime_diagnostic(request_id,str(online_outcome.get("selectedModelId") or model_id),"ONLINE_RESEARCH_OUTCOME",online_outcome)
                with _lock:
                    current=s.get("activeGeneration")
                    if current and current.get("requestId")==request_id:
                        persistence=copy.deepcopy(current.get("onlineLogPersistence") or {})
                        persistence["outcome"]=copy.deepcopy(result)
                        current["onlineLogPersistence"]=persistence
                    target_thread=next((t for t in s.get("threads",[]) if t.get("id")==payload.get("threadId")),None)
                    if target_thread:
                        target_message=next((m for m in reversed(target_thread.get("messages",[])) if str(m.get("id") or "")==str(assistant_id)),None)
                        if target_message is not None:
                            target_message.setdefault("meta",{})["onlineLogPersistence"]=copy.deepcopy((s.get("activeGeneration") or {}).get("onlineLogPersistence") or {})
                    s["revision"]+=1
            threading.Thread(target=persist_online_outcome,daemon=True,name="online-outcome-"+request_id[:8]).start()
        if knowledge_snapshot is not None:
            def persist_knowledge_snapshot():
                persist_runtime_diagnostic(request_id,str(online_outcome.get("selectedModelId") if isinstance(online_outcome,dict) else model_id),"KNOWLEDGE_ACQUISITION_SNAPSHOT",knowledge_snapshot)
            threading.Thread(target=persist_knowledge_snapshot,daemon=True,name="knowledge-snapshot-"+request_id[:8]).start()
        if github_telemetry is not None:
            def persist_programming_log():
                result=persist_runtime_diagnostic(request_id,model_id,"PROGRAMMING_GENERATION_TELEMETRY",github_telemetry)
                with _lock:
                    current=s.get("activeGeneration")
                    if current and current.get("requestId")==request_id:
                        current["githubTelemetryPersistence"]=copy.deepcopy(result)
                    target_thread=next((t for t in s.get("threads",[]) if t.get("id")==payload.get("threadId")),None)
                    if target_thread:
                        target_message=next((m for m in reversed(target_thread.get("messages",[])) if str(m.get("id") or "")==str(assistant_id)),None)
                        if target_message is not None:
                            target_message.setdefault("meta",{})["githubTelemetryPersistence"]=copy.deepcopy(result)
                    s["revision"]+=1
            threading.Thread(target=persist_programming_log,daemon=True,name="programming-log-"+request_id[:8]).start()
    except Exception as exc:
        failed_online_outcome=None
        with _lock:
            g=s["activeGeneration"]
            if g and g["requestId"]==request_id:
                g.update(terminal=True,terminalType="FAILED",phase="FAILED")
                g["status"].append({"phase":"FAILED","reason":str(exc)[:240]})
                if isinstance(g.get("onlineResearch"),dict) and g.get("onlineResearch"):
                    failed_online_outcome={
                        "schema":"swrlz-online-research-outcome-v1",
                        "terminalState":"FAILED",
                        "errorType":type(exc).__name__,
                        "research":copy.deepcopy(g.get("onlineResearch") or {}),
                        "trace":copy.deepcopy((g.get("onlineTrace") or [])[-64:]),
                        "requestedModelId":str(g.get("requestedModelId") or model_id)[:80],
                        "selectedModelId":str(g.get("selectedModelId") or model_id)[:80],
                        "rawPromptStored":False,
                        "historyStored":False,
                        "preciseLocationStored":False,
                    }
                thread=next((t for t in s["threads"] if t["id"]==payload["threadId"]),None)
                if thread:
                    thread["messages"].append({"id":assistant_id,"role":"assistant","text":"Generation failed: "+str(exc)[:240],"createdAt":int(time.time()*1000),"meta":{"requestId":request_id,"modelId":model_id,"state":"FAILED","onlineResearch":copy.deepcopy(g.get("onlineResearch") or {}),"onlineTrace":copy.deepcopy((g.get("onlineTrace") or [])[-64:])}})
                    s["revision"]+=1
        if failed_online_outcome is not None:
            threading.Thread(target=persist_runtime_diagnostic,args=(request_id,str(failed_online_outcome.get("selectedModelId") or model_id),"ONLINE_RESEARCH_OUTCOME",failed_online_outcome),daemon=True,name="online-failed-"+request_id[:8]).start()

def _container_content_tag(text):
    source=str(text or "")
    import re
    fences=re.findall(r"```([^\n`]*)\n?[\s\S]*?```",source)
    if not fences:return ""
    lyric={"lyrics","lyric","song","music","verse","chorus"}
    langs=[str(header or "").strip().lower().split()[0] if str(header or "").strip() else "code" for header in fences]
    return "container:lyrics" if langs and all(lang in lyric for lang in langs) else "container:code"

def _gap_label(ms):
    if ms is None:return None
    seconds=max(0,int(ms)//1000)
    if seconds<45:return "moments"
    minutes=seconds//60
    if minutes<60:return str(minutes)+" minute"+("" if minutes==1 else "s")
    hours=minutes//60
    if hours<24:return str(hours)+" hour"+("" if hours==1 else "s")
    days=hours//24
    return str(days)+" day"+("" if days==1 else "s")

def _temporal_context(messages,client_timezone,now_ms):
    zone_name=str(client_timezone or "").strip()[:80]
    try: zone=ZoneInfo(zone_name) if zone_name else timezone.utc
    except Exception:
        zone_name="UTC";zone=timezone.utc
    def stamp(ms):
        if not isinstance(ms,(int,float)) or ms<=0:return None
        dt=datetime.fromtimestamp(ms/1000,tz=timezone.utc).astimezone(zone)
        return {"unixMs":int(ms),"local":dt.isoformat(timespec="minutes"),"localDate":dt.date().isoformat()}
    prior=[m for m in messages if isinstance(m,dict) and isinstance(m.get("createdAt"),(int,float))]
    last_user=next((m for m in reversed(prior) if m.get("role")=="user"),None)
    last_assistant=next((m for m in reversed(prior) if m.get("role")=="assistant"),None)
    previous=prior[-1] if prior else None
    def gap(m):
        if not m:return None
        ms=max(0,int(now_ms-int(m["createdAt"])))
        return {"milliseconds":ms,"semantic":_gap_label(ms)}
    now=datetime.fromtimestamp(now_ms/1000,tz=timezone.utc).astimezone(zone)
    return {
        "schema":"swrlz-temporal-context-v1","timeZone":zone_name or "UTC",
        "nowUtc":datetime.fromtimestamp(now_ms/1000,tz=timezone.utc).isoformat(timespec="seconds"),
        "localNow":now.isoformat(timespec="minutes"),"localDate":now.date().isoformat(),
        "previousMessage":stamp(previous.get("createdAt")) if previous else None,
        "previousMessageRole":previous.get("role") if previous else None,
        "previousUserMessage":stamp(last_user.get("createdAt")) if last_user else None,
        "previousAssistantMessage":stamp(last_assistant.get("createdAt")) if last_assistant else None,
        "gapSincePreviousMessage":gap(previous),"gapSinceLastUserTurn":gap(last_user),"gapSinceLastAssistantTurn":gap(last_assistant)
    }

@app.post("/api/lalm_station/cancel")
async def cancel_generation(request:Request):
    body=await request.json();rid=str(body.get("requestId") or "").strip()
    if not rid:raise HTTPException(400,"requestId required")
    key,s=_session(request)
    with _lock:
        g=s.get("activeGeneration")
        if not g or g.get("requestId")!=rid:return JSONResponse({"ok":False,"requestId":rid,"state":"NOT_ACTIVE"},status_code=409)
        if g.get("terminal"):return {"ok":True,"requestId":rid,"state":str(g.get("terminalType") or "TERMINAL")}
        g["cancelRequested"]=True;g["status"].append({"phase":"CANCEL_REQUESTED","reason":"User requested stop"})
    return {"ok":True,"requestId":rid,"state":"CANCEL_REQUESTED"}


@app.post("/api/lalm_station/send",status_code=202)
async def send(request:Request):
    key,s=_session(request)
    body=await request.json()
    model_id=body.get("modelId","auto")
    route=next((r for r in routes() if r.model_id==model_id),None)
    if route is None or not route.available:raise HTTPException(422,"Selected model is not configured")
    prompt=body.get("prompt");tid=body.get("threadId");rid=body.get("requestId")
    profile=body.get("profile","")
    user_profile=body.get("userProfile","")
    client_timezone=body.get("timeZone","UTC")
    client_location=body.get("clientLocation")
    if client_location is not None:
        if not isinstance(client_location,dict) or client_location.get("authorized") is not True:raise HTTPException(400,"Invalid client location")
        try:
            latitude=float(client_location.get("latitude"));longitude=float(client_location.get("longitude"))
        except (TypeError,ValueError):raise HTTPException(400,"Invalid client location")
        if not (-90.0<=latitude<=90.0 and -180.0<=longitude<=180.0):raise HTTPException(400,"Invalid client location")
        client_location={"authorized":True,"latitude":latitude,"longitude":longitude,"label":str(client_location.get("label") or "Your shared location")[:120]}
    content_tag=body.get("contentTag","")
    if content_tag not in ("","container:code","container:lyrics"):raise HTTPException(400,"Invalid content tag")
    if not isinstance(client_timezone,str) or len(client_timezone)>80:raise HTTPException(400,"Invalid timezone")
    if not isinstance(profile,str) or len(profile)>2000:raise HTTPException(400,"Invalid test profile")
    if not isinstance(user_profile,str) or len(user_profile)>2000:raise HTTPException(400,"Invalid user profile")
    if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>32768:raise HTTPException(400,"Invalid prompt")
    if not all(isinstance(v,str) and 0<len(v)<=160 for v in (tid,rid)):raise HTTPException(400,"Invalid IDs")
    with _lock:
        if s["activeGeneration"] and not s["activeGeneration"]["terminal"]:raise HTTPException(409,"Generation already active")
        t=next((t for t in s["threads"] if t["id"]==tid),None)
        if t is None:
            t={"id":tid,"title":prompt[:48],"pinned":False,"messagePins":{},"codeArtifacts":[],"programmingState":None,"createdAt":time.time()*1000,"messages":[]}
            s["threads"].append(t)
        now_ms=int(time.time()*1000)
        temporal_context=_temporal_context(t["messages"],client_timezone,now_ms)
        # Attach up to three subsequent user turns to the most recent online
        # knowledge snapshot. This is feedback/context for later review, not an
        # automatic promotion signal and not part of runtime diagnostic logs.
        prior_online=None;followup_index=0
        for index in range(len(t["messages"])-1,-1,-1):
            candidate=t["messages"][index]
            if candidate.get("role")=="assistant" and isinstance((candidate.get("meta") or {}).get("onlineResearch"),dict):
                later_users=[m for m in t["messages"][index+1:] if m.get("role")=="user"]
                if len(later_users)<3:
                    prior_online=candidate;followup_index=len(later_users)+1
                break
        if prior_online and followup_index in (1,2,3):
            prior_request=str((prior_online.get("meta") or {}).get("requestId") or "")
            if prior_request and prior_request!=str(rid):
                feedback={"schema":"swrlz-knowledge-followup-v1","parentRequestId":prior_request,"turnIndex":followup_index,"userText":str(prompt)[:4000],"capturedAtUnixMs":now_ms}
                event_type="KNOWLEDGE_ACQUISITION_FOLLOWUP_"+str(followup_index)
                threading.Thread(target=persist_runtime_diagnostic,args=(prior_request,model_id,event_type,feedback),daemon=True,name="knowledge-followup-"+prior_request[:8]).start()
        history=_history_projection(t)
        pins=t.get("messagePins") if isinstance(t.get("messagePins"),dict) else {}
        pinned_context=[_artifact_context_item(t,m) for m in t["messages"] if pins.get(str(m.get("id") or "")) and m.get("role") in ("user","assistant")]
        selected_project=_select_staged_workspace(t,prompt)
        staged_context=None
        if selected_project is not None:
            staged_context=project_view(selected_project)
            staged_context["allowReplace"]=bool(__import__("re").search(
                r"\b(?:fix|repair|update|modify|change|replace|refactor)\b",prompt,__import__("re").I))
        t["messages"].append({"id":str(body.get("messageId") or uuid.uuid4().hex),"role":"user","text":prompt,"createdAt":now_ms,"meta":{"requestId":rid,"modelId":model_id,**({"contentTag":content_tag} if content_tag else {})}})
        s["currentId"]=tid;s["revision"]+=1
        s["activeGeneration"]={"requestId":rid,"threadId":tid,"modelId":model_id,"requestedModelId":model_id,"selectedModelId":model_id,"text":"","phase":"QUEUED","terminal":False,"lastSeq":0,"status":[{"phase":"QUEUED","reason":"Accepted by Workstation"}],"acceptedAtUnixMs":now_ms,"startedAtUnixMs":None,"completedAtUnixMs":None,"queueWaitMs":None,"stationTiming":None,"resourcePlan":None,"diagnosticTrace":None,"memoryCandidates":[],"responseCognition":None,"onlineResearch":None,"onlineTrace":[],"onlineLogPersistence":None,"sources":[],"widgets":[],"programmingIntent":None,"intentContract":None,"failureEvidence":None,"repairConstraints":None,"behaviorLedger":None,"behaviorRepairBase":None,"candidateValidation":None,"candidateAttempts":[],"generationTelemetry":None,"engineCompletionTelemetry":None,"repairDiagnostics":[],"artifactReceipt":None,"githubTelemetryPersistence":None}
    payload={"requestId":rid,"threadId":tid,"prompt":prompt,"history":history,"pinnedContext":pinned_context,"profileId":"LALM","profile":profile,"userProfile":user_profile,"temporalContext":temporal_context,"clientLocation":client_location,"priorProgrammingState":copy.deepcopy(t.get("programmingState") or {}),"stagedProject":staged_context}
    _pool.submit(_run,key,rid,model_id,payload,str(body.get("assistantMessageId") or uuid.uuid4().hex))
    response=JSONResponse({"ok":True,"contract":CONTRACT,"requestId":rid,"modelId":model_id},status_code=202)
    response.set_cookie("swrlz_hf_sid",key,httponly=True,samesite="lax",secure=request.url.scheme=="https",max_age=86400,path="/")
    return response
