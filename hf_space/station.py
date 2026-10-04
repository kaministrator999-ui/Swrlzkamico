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
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from model_router import dispatch, ModelUnavailable, routes
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

def _session(request):
    key=request.cookies.get("swrlz_hf_sid")
    if not key or key not in _sessions:
        key=uuid.uuid4().hex
        with _lock:
            _sessions.setdefault(key,{"revision":0,"currentId":"","threads":[],"activeGeneration":None})
    return key,_sessions[key]

def _snapshot(s):
    return {"contract":CONTRACT,"revision":s["revision"],"threads":copy.deepcopy(s["threads"]),
            "currentThread":next((copy.deepcopy(t) for t in s["threads"] if t["id"]==s["currentId"]),None),
            "state":{"currentId":s["currentId"],"threads":copy.deepcopy(s["threads"])},
            "activeGeneration":copy.deepcopy(s["activeGeneration"])}

@app.get("/")
def home():
    return FileResponse(ROOT/"chat/§wyrlz/index.html")

@app.get("/chat/§wyrlz")
def chat():
    return FileResponse(ROOT/"chat/§wyrlz/index.html")

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
                yield json.dumps({"type":"STATUS","phase":str(item.get("phase") or "STATUS"),"reason":str(item.get("reason") or ""), "seq":sent_status,"requestId":rid},ensure_ascii=False)+"\n"
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

def _create_code_artifact(thread,message,request_id,text):
    files=_parse_code_files(text)
    if not files or len(str(text or ""))<120:return None
    existing=_artifact_for_message(thread,message.get("id"))
    if existing:return existing
    artifact_id="artifact-"+uuid.uuid4().hex
    now=int(time.time()*1000)
    revision={"revision":1,"requestId":str(request_id or ""),"createdAt":now,"files":copy.deepcopy(files)}
    artifact={"id":artifact_id,"type":"code","sourceMessageId":str(message.get("id") or ""),"title":files[0]["path"],"currentRevision":1,"files":copy.deepcopy(files),"revisions":[revision],"createdAt":now,"updatedAt":now}
    thread.setdefault("codeArtifacts",[]).append(artifact)
    message.setdefault("meta",{})["codeArtifactId"]=artifact_id
    message["meta"]["artifactRevision"]=1
    return artifact

def _promote_pinned_code_artifact(thread,message):
    if message.get("role")!="assistant" or "```" not in str(message.get("text") or ""):return None
    existing=_artifact_for_message(thread,message.get("id"))
    if existing:return existing
    return _create_code_artifact(thread,message,(message.get("meta") or {}).get("requestId"),message.get("text"))

def _artifact_context_item(thread,message):
    artifact=_artifact_for_message(thread,message.get("id"))
    if artifact is None:
        artifact=_promote_pinned_code_artifact(thread,message)
    if artifact is None:
        return {"messageId":message.get("id"),"role":str(message.get("role") or "").upper(),"text":str(message.get("text") or "")[:12000],"pinned":True}
    files=copy.deepcopy(artifact.get("files") or [])
    return {"messageId":message.get("id"),"role":str(message.get("role") or "").upper(),"text":_artifact_markdown(files)[:12000],"pinned":True,"artifactType":"code","artifactId":artifact.get("id"),"artifactTitle":artifact.get("title"),"artifactRevision":int(artifact.get("currentRevision") or 1),"files":[{"path":f.get("path"),"language":f.get("language")} for f in files]}

def _commit_code_artifact_revision(artifact,text,request_id,base_revision=0):
    files=_parse_code_files(text)
    if not files:return False,"NO_CODE"
    current=int(artifact.get("currentRevision") or 0)
    if int(base_revision or 0) not in (0,current):return False,"REVISION_CONFLICT"
    next_revision=current+1
    now=int(time.time()*1000)
    artifact.setdefault("revisions",[]).append({"revision":next_revision,"requestId":str(request_id or ""),"createdAt":now,"files":copy.deepcopy(files)})
    artifact["currentRevision"]=next_revision
    artifact["files"]=copy.deepcopy(files)
    artifact["updatedAt"]=now
    if files:artifact["title"]=artifact.get("title") or files[0]["path"]
    return True,"COMMITTED"

def _response_prose(text):
    prose=str(text or "")
    for fence in _code_fences(prose):prose=prose.replace(fence,"")
    return prose.strip()


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
                elif kind=="PROGRAMMING_INTENT":
                    intent=event.get("intent")
                    if isinstance(intent,dict):
                        g["programmingIntent"]=copy.deepcopy(intent)
                        contract=intent.get("intentContract")
                        if isinstance(contract,dict):g["intentContract"]=copy.deepcopy(contract)
                        evidence=intent.get("failureEvidence")
                        if isinstance(evidence,dict):g["failureEvidence"]=copy.deepcopy(evidence)
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
                else:g["status"].append({"seq":g["lastSeq"],"phase":str(event.get("phase") or kind),"reason":str(event.get("reason") or "")[:200]})
            if persist_event is not None:
                persist_kind,persist_payload=persist_event
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
            programming_telemetry={
                "schema":"swrlz-station-programming-telemetry-v1",
                "generation":generation_telemetry,
                "station":station_timing,
            } if intent.get("codingTask") else None
            telemetry_meta={"programmingTelemetry":programming_telemetry} if programming_telemetry else {}
            artifact_id=str(intent.get("artifactTargetId") or "")
            artifact=_find_artifact(thread,artifact_id) if artifact_id and intent.get("artifactMutationRequested") and not rejected else None
            if artifact is not None:
                committed,reason=_commit_code_artifact_revision(artifact,text,request_id,int(intent.get("baseRevision") or 0))
                if committed:
                    source=next((m for m in thread.get("messages",[]) if str(m.get("id") or "")==str(artifact.get("sourceMessageId") or "")),None)
                    if source is not None:
                        source.setdefault("meta",{})["codeArtifactId"]=artifact["id"]
                        source["meta"]["artifactRevision"]=artifact["currentRevision"]
                    prose=_response_prose(text) or ("Updated pinned code artifact to revision "+str(artifact["currentRevision"])+".")
                    message={"id":assistant_id,"role":"assistant","text":prose,"createdAt":int(time.time()*1000),"meta":{"requestId":request_id,"modelId":model_id,"state":"COMPLETE","updatedCodeArtifactId":artifact["id"],"artifactRevision":artifact["currentRevision"],**telemetry_meta}}
                    thread["messages"].append(message)
                    g["artifactReceipt"]={"action":"REVISION_COMMITTED","artifactId":artifact["id"],"revision":artifact["currentRevision"],"baseRevision":int(intent.get("baseRevision") or 0)}
                else:
                    message={"id":assistant_id,"role":"assistant","text":_response_prose(text) or text,"createdAt":int(time.time()*1000),"meta":{"requestId":request_id,"modelId":model_id,"state":"COMPLETE","artifactMutationRejected":reason,**telemetry_meta}}
                    thread["messages"].append(message)
                    g["artifactReceipt"]={"action":"REVISION_REJECTED","artifactId":artifact["id"],"reason":reason}
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
                        g["artifactReceipt"]={"action":"ARTIFACT_CREATED","artifactId":artifact["id"],"revision":1}
            if intent.get("codingTask") and generation_telemetry:
                github_telemetry={
                    "schema":"swrlz-station-programming-log-v1",
                    "generationTelemetry":generation_telemetry,
                    "stationTiming":station_timing,
                    "candidateValidation":{
                        "status":validation.get("status"),
                        "reasons":[str(x)[:160] for x in (validation.get("reasons") or [])[:8]],
                        "detectedLanguages":copy.deepcopy(validation.get("detectedLanguages") or []),
                        "executionVerified":validation.get("executionVerified"),
                        "verificationState":validation.get("verificationState"),
                    },
                    "artifactReceipt":{
                        "action":(g.get("artifactReceipt") or {}).get("action"),
                        "revision":(g.get("artifactReceipt") or {}).get("revision"),
                    },
                }
                g["githubTelemetryPersistence"]={"state":"QUEUED","path":"runtime-diagnostics/programming/"+request_id+"/candidate-attempt-telemetry.json","branch":"runtime"}
            s["revision"]+=1
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
        with _lock:
            g=s["activeGeneration"]
            if g and g["requestId"]==request_id:
                g.update(terminal=True,terminalType="FAILED",phase="FAILED")
                g["status"].append({"phase":"FAILED","reason":str(exc)[:240]})
                thread=next((t for t in s["threads"] if t["id"]==payload["threadId"]),None)
                if thread:
                    thread["messages"].append({"id":assistant_id,"role":"assistant","text":"Generation failed: "+str(exc)[:240],"createdAt":int(time.time()*1000),"meta":{"requestId":request_id,"modelId":model_id,"state":"FAILED"}})
                    s["revision"]+=1

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
        history=[{"id":m.get("id"),"role":m["role"],"text":m["text"],"createdAt":m.get("createdAt"),"meta":copy.deepcopy(m.get("meta") or {})} for m in t["messages"] if m["role"] in ("user","assistant")]
        pins=t.get("messagePins") if isinstance(t.get("messagePins"),dict) else {}
        pinned_context=[_artifact_context_item(t,m) for m in t["messages"] if pins.get(str(m.get("id") or "")) and m.get("role") in ("user","assistant")]
        t["messages"].append({"id":str(body.get("messageId") or uuid.uuid4().hex),"role":"user","text":prompt,"createdAt":now_ms,"meta":{"requestId":rid,"modelId":model_id,**({"contentTag":content_tag} if content_tag else {})}})
        s["currentId"]=tid;s["revision"]+=1
        s["activeGeneration"]={"requestId":rid,"threadId":tid,"modelId":model_id,"text":"","phase":"QUEUED","terminal":False,"lastSeq":0,"status":[{"phase":"QUEUED","reason":"Accepted by Workstation"}],"acceptedAtUnixMs":now_ms,"startedAtUnixMs":None,"completedAtUnixMs":None,"queueWaitMs":None,"stationTiming":None,"resourcePlan":None,"diagnosticTrace":None,"memoryCandidates":[],"programmingIntent":None,"intentContract":None,"failureEvidence":None,"candidateValidation":None,"candidateAttempts":[],"generationTelemetry":None,"engineCompletionTelemetry":None,"repairDiagnostics":[],"artifactReceipt":None,"githubTelemetryPersistence":None}
    payload={"requestId":rid,"threadId":tid,"prompt":prompt,"history":history,"pinnedContext":pinned_context,"profileId":"LALM","profile":profile,"userProfile":user_profile,"temporalContext":temporal_context,"priorProgrammingState":copy.deepcopy(t.get("programmingState") or {})}
    _pool.submit(_run,key,rid,model_id,payload,str(body.get("assistantMessageId") or uuid.uuid4().hex))
    response=JSONResponse({"ok":True,"contract":CONTRACT,"requestId":rid,"modelId":model_id},status_code=202)
    response.set_cookie("swrlz_hf_sid",key,httponly=True,samesite="lax",secure=request.url.scheme=="https",max_age=86400,path="/")
    return response
