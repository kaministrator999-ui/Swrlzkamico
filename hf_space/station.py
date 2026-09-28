"""HF-only in-process Station adapter for the canonical Chat projection.

Candidate limitations: process-local state, anonymous session, no durable account
storage or Vercel queue. Do not claim production parity.
"""
from __future__ import annotations
import copy, json, threading, time, uuid
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from model_router import dispatch, ModelUnavailable, routes

ROOT=Path(__file__).resolve().parent
CONTRACT="swrlz-lalm-station-sync-v1"
app=FastAPI(title="§wyrlz HF Station candidate")
app.mount("/chat/§wyrlz/assets",StaticFiles(directory=ROOT/"chat/§wyrlz/assets"),name="chat-assets")
_lock=threading.RLock()
_sessions={}
_pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix="hf-r39")
_generate=None
_stock_generate=None
_large_generate=None

def set_generator(fn,stock_fn=None,large_fn=None):
    global _generate,_stock_generate,_large_generate
    _generate=fn
    _stock_generate=stock_fn
    _large_generate=large_fn

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

@app.get("/api/lalm_station/sync")
def sync(request:Request):
    key,s=_session(request)
    with _lock: response=JSONResponse(_snapshot(s))
    response.set_cookie("swrlz_hf_sid",key,httponly=True,samesite="lax",secure=request.url.scheme=="https",max_age=86400)
    return response

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
                    t={"id":tid,"title":str(op.get("title") or "New conversation")[:120],"pinned":False,"createdAt":time.time()*1000,"messages":[]}
                    s["threads"].append(t)
                for k in ("title","pinned"):
                    if k in op:t[k]=op[k]
            else:raise HTTPException(400,"Unsupported state operation")
        s["revision"]+=1
        return {"ok":True,"revision":s["revision"]}

def _run(key,request_id,model_id,payload,assistant_id):
    with _lock:
        s=_sessions[key];g=s["activeGeneration"];g["phase"]="GENERATING";g["status"].append({"phase":"GENERATING"})
    try:
        if model_id=="r39" and _generate is None:raise RuntimeError("R39 generator is not installed")
        if model_id=="stock" and _stock_generate is None:raise RuntimeError("Original HF generator is not installed")
        text=""; completed=False
        for event in dispatch(model_id,payload,_generate,_stock_generate,_large_generate):
            if not isinstance(event,dict):continue
            kind=str(event.get("type") or "")
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
                else:g["status"].append({"seq":g["lastSeq"],"phase":str(event.get("phase") or kind),"reason":str(event.get("reason") or "")[:200]})
            if kind=="FAILED":raise RuntimeError(str(event.get("reason") or "Generation failed"))
            if kind in ("COMPLETE","COMPLETED"):completed=True
        if not text:raise RuntimeError("R39 emitted no DELTA")
        with _lock:
            g=s["activeGeneration"];g.update(terminal=True,terminalType="COMPLETE",phase="COMPLETE")
            thread=next(t for t in s["threads"] if t["id"]==payload["threadId"])
            thread["messages"].append({"id":assistant_id,"role":"assistant","text":text,"meta":{"requestId":request_id,"modelId":model_id,"state":"COMPLETE"}})
            s["revision"]+=1
    except Exception as exc:
        with _lock:
            g=s["activeGeneration"]
            if g and g["requestId"]==request_id:
                g.update(terminal=True,terminalType="FAILED",phase="FAILED")
                g["status"].append({"phase":"FAILED","reason":str(exc)[:240]})
                thread=next((t for t in s["threads"] if t["id"]==payload["threadId"]),None)
                if thread:
                    thread["messages"].append({"id":assistant_id,"role":"assistant","text":"Generation failed: "+str(exc)[:240],"meta":{"requestId":request_id,"modelId":model_id,"state":"FAILED"}})
                    s["revision"]+=1

@app.post("/api/lalm_station/send",status_code=202)
async def send(request:Request):
    key,s=_session(request)
    body=await request.json()
    model_id=body.get("modelId","stock")
    route=next((r for r in routes() if r.model_id==model_id),None)
    if route is None or not route.available:raise HTTPException(422,"Selected model is not configured")
    prompt=body.get("prompt");tid=body.get("threadId");rid=body.get("requestId")
    profile=body.get("profile","")
    user_profile=body.get("userProfile","")
    if not isinstance(profile,str) or len(profile)>6000:raise HTTPException(400,"Invalid test profile")
    if not isinstance(user_profile,str) or len(user_profile)>6000:raise HTTPException(400,"Invalid user profile")
    if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>16000:raise HTTPException(400,"Invalid prompt")
    if not all(isinstance(v,str) and 0<len(v)<=160 for v in (tid,rid)):raise HTTPException(400,"Invalid IDs")
    with _lock:
        if s["activeGeneration"] and not s["activeGeneration"]["terminal"]:raise HTTPException(409,"Generation already active")
        t=next((t for t in s["threads"] if t["id"]==tid),None)
        if t is None:
            t={"id":tid,"title":prompt[:48],"pinned":False,"createdAt":time.time()*1000,"messages":[]}
            s["threads"].append(t)
        history=[{"role":m["role"],"text":m["text"]} for m in t["messages"] if m["role"] in ("user","assistant")]
        t["messages"].append({"id":str(body.get("messageId") or uuid.uuid4().hex),"role":"user","text":prompt,"meta":{"requestId":rid,"modelId":model_id}})
        s["currentId"]=tid;s["revision"]+=1
        s["activeGeneration"]={"requestId":rid,"threadId":tid,"modelId":model_id,"text":"","phase":"QUEUED","terminal":False,"lastSeq":0,"status":[{"phase":"QUEUED"}],"diagnosticTrace":None,"memoryCandidates":[]}
    payload={"requestId":rid,"threadId":tid,"prompt":prompt,"history":history,"profileId":"LALM","profile":profile,"userProfile":user_profile}
    _pool.submit(_run,key,rid,model_id,payload,str(body.get("assistantMessageId") or uuid.uuid4().hex))
    response=JSONResponse({"ok":True,"contract":CONTRACT,"requestId":rid,"modelId":model_id},status_code=202)
    response.set_cookie("swrlz_hf_sid",key,httponly=True,samesite="lax",secure=request.url.scheme=="https",max_age=86400)
    return response
