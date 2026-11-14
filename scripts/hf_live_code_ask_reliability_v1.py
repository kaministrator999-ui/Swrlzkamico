#!/usr/bin/env python3
"""Guarded live §C coding Ask reliability release.

Extends the CURRENT Hugging Face Station, not a stale GitHub copy.
Read-only progress does not need a durable write, but account identity still
requires verification. No bypass of login security when storage is down.
"""
from __future__ import annotations
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
FILES = ("station.py", "chat/§wyrlz/index.html")
BACKUP = Path("hf-code-ask-reliability-backup")
MARK = "swrlz-code-ask-storage-recovery-v1"

def one(source, old, new, name):
    number = source.count(old)
    if number != 1:
        raise RuntimeError(f"LIVE_SOURCE_DRIFT {name} occurrences={number}")
    return source.replace(old,new,1)

def patch_station(source):
    if MARK in source:
        raise RuntimeError("Ask storage fix already applied")
    old = '''    if kind not in ("ASK","STEER") or not prompt or len(prompt)>2000:
        raise HTTPException(400,"Invalid live coding question or instruction")
    key,s=_session(request)
    with _lock:'''
    new = '''    if kind not in ("ASK","STEER") or not prompt or len(prompt)>2000:
        raise HTTPException(400,"Invalid live coding question or instruction")
    # swrlz-code-ask-storage-recovery-v1: a transient Redis/auth read failure
    # must not silently turn an Ask into a normal coding turn or cancel decoding.
    # Never bypass verified account identity to retrieve private project state.
    for attempt in range(3):
        try:
            key,s=_session(request)
            break
        except HTTPException as exc:
            if exc.status_code != 503:
                raise
            if attempt >= 2:
                return JSONResponse({
                    "ok":False,"code":"ACCOUNT_STORAGE_UNAVAILABLE",
                    "retryable":True,
                    "detail":"Account storage temporarily unavailable. The Ask request was not accepted; check the ongoing code stream independently."
                },status_code=503,headers={"Cache-Control":"private, no-store"})
            await asyncio.sleep(0.2*(attempt+1))
    with _lock:'''
    source=one(source,old,new,"station Ask authenticated session retry")
    ast.parse(source,filename="station.py")
    return source

def patch_chat(source):
    if MARK in source:
        raise RuntimeError("Ask client fix already applied")
    old = '''        const rid=generation.requestId,tid=generation.threadId;
        const action=/\\b(add|change|modify|fix|remove|rewrite|refactor|implement|ensure|include|make sure|update|switch|move)\\b/i.test(text)?"STEER":"ASK";
        swrlzGuideSubmitting=true;swrlzGuideButton.disabled=true;'''
    new = '''        const rid=generation.requestId,tid=generation.threadId;
        // swrlz-code-ask-storage-recovery-v1: "Continue" is not a separate
        // send while a coding task is active; source continuation is automatic.
        if(/^(?:continue(?:\\s+(?:code|coding|generation))?|keep\\s+going|resume(?:\\s+code)?)\\s*[.!]?$/i.test(text)&&!generation.terminal){
          swrlzGuideAnswer.textContent="Coding is already underway. An extra Continue message is not needed while this task is active. Check the streaming code and activity log for fresh progress; no new task was submitted.";
          swrlzGuideReceipt.hidden=false;
          return;
        }
        const action=/\\b(add|change|modify|fix|remove|rewrite|refactor|implement|ensure|include|make sure|update|switch|move)\\b/i.test(text)?"STEER":"ASK";
        swrlzGuideSubmitting=true;swrlzGuideButton.disabled=true;'''
    source=one(source,old,new,"local continue command")
    old2 = '''          const result=await response.json().catch(()=>({}));
          if(!response.ok||!result.ok)throw Error(result.detail||result.code||"Request rejected");
          if(prompt.value.trim()===text){prompt.value="";resizeComposer();}'''
    new2 = '''          const result=await response.json().catch(()=>({}));
          if(response.status===503&&action==="ASK"){
            // The progress display below is local/stale-able observation only.
            // Do not imply an active server job is confirmed by this fallback.
            const g=stationGeneration;
            const recent=(g?.status||[]).slice(-1)[0]||{};
            const phase=String(recent.phase||g?.phase||"unknown").replaceAll("_"," ").toLowerCase();
            const bytes=new TextEncoder().encode(String(g?.previewText||g?.text||"")).length;
            swrlzGuideAnswer.textContent="Account storage is temporarily unavailable. This question was not answered by the server. Local tab observation only: last phase "+phase+", "+bytes+" bytes visible, task "+(g?.terminal?"shown as ended":"not shown as ended")+". The Ask failure does not request Stop. Retry after the connection recovers; the text remains in your composer.";
            swrlzGuideReceipt.hidden=false;
            return;
          }
          if(!response.ok||!result.ok)throw Error(result.detail||result.code||"Request rejected");
          if(prompt.value.trim()===text){prompt.value="";resizeComposer();}'''
    source=one(source,old2,new2,"progress-only fallback and retain composer")
    source=one(source,
        '''          swrlzGuideAnswer.textContent="Couldn't send coding question: "+String(error.message||error);''',
        '''          swrlzGuideAnswer.textContent="Coding request was not confirmed and was not applied: "+String(error.message||error)+". The draft remains in your composer. The ongoing coding job has not been cancelled by this request.";''',
        "explicit unconfirmed guidance")
    return source

def check_js(source):
    matches=re.findall(r"<script\b([^>]*)>(.*?)</script\s*>",source,flags=re.I|re.S)
    count=0
    with tempfile.TemporaryDirectory() as root:
        for number,(attrs,body) in enumerate(matches):
            if not body.strip() or "application/json" in attrs:
                continue
            file=Path(root)/(str(number)+".js")
            file.write_text(body)
            process=subprocess.run(["node","--check",str(file)],capture_output=True,text=True,timeout=20)
            if process.returncode:
                raise RuntimeError("CHAT_JS_INVALID "+process.stderr[-1000:])
            count+=1
    if count==0:
        raise RuntimeError("NO_EMBEDDED_JS_VERIFIED")
    print("ASK_JS_SYNTAX_VERIFIED",count,flush=True)

def test_patch(station,chat):
    assert 'except HTTPException as exc:' in station
    assert 'if exc.status_code != 503:' in station
    assert 'retryable":True' in station
    assert "await asyncio.sleep(0.2*(attempt+1))" in station
    assert "No new task" not in chat  # Control only; no forged server acknowledgment
    assert "Local tab observation only:" in chat
    assert "the text remains in your composer" in chat
    assert "if(response.status===503&&action===\"ASK\")" in chat
    assert 'if(!response.ok||!result.ok)throw Error(' in chat
    check_js(chat)
    print("ASK_FAILURE_INTEGRATION_CONTRACT_VERIFIED",flush=True)

def sha(blob):
    return hashlib.sha256(blob).hexdigest()

def preflight(api):
    revision=api.repo_info(SPACE,repo_type="space").sha
    before={f:Path(hf_hub_download(SPACE,f,repo_type="space",
        revision=revision,token=api.token)).read_bytes() for f in FILES}
    after={
        "station.py":patch_station(before["station.py"].decode()).encode(),
        "chat/§wyrlz/index.html":patch_chat(before["chat/§wyrlz/index.html"].decode()).encode(),
    }
    test_patch(after["station.py"].decode(),after["chat/§wyrlz/index.html"].decode())
    BACKUP.mkdir(parents=True,exist_ok=True)
    for name,blob in before.items():
        p=BACKUP/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
    (BACKUP/"revision.txt").write_text(revision)
    (BACKUP/"manifest.json").write_text(json.dumps({
        "revision":revision,
        "before":{k:sha(v) for k,v in before.items()},
        "after":{k:sha(v) for k,v in after.items()}
    },indent=2))
    print("ASK_RELIABILITY_PREFLIGHT_VERIFIED",revision,flush=True)

def publish(api,parent,source,reason):
    if api.repo_info(SPACE,repo_type="space").sha != parent:
        raise RuntimeError("HF_SOURCE_CHANGED_REPREFLIGHT_REQUIRED")
    with tempfile.TemporaryDirectory() as root:
        ops=[]
        for name,blob in source.items():
            p=Path(root)/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
            ops.append(CommitOperationAdd(path_in_repo=name,path_or_fileobj=str(p)))
        result=api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=parent,
            operations=ops,commit_message=reason)
    return str(result.oid)

def health(api,revision):
    page=urllib.request.urlopen(BASE+"/chat/%C2%A7wyrlz",timeout=30).read(400000).decode("utf-8","replace")
    if MARK not in page:
        raise RuntimeError("LIVE_CHAT_MARKER_MISSING")
    info=json.load(urllib.request.urlopen(BASE+"/api/hf/qwen35-ready",timeout=30))
    if info.get("model")!="qwen3.5-9b":
        raise RuntimeError("LIVE_MODEL_ID_CHANGED")
    current=api.repo_info(SPACE,repo_type="space")
    if current.sha != revision:
        raise RuntimeError("LIVE_SOURCE_SHA_NOT_MATCHED")
    print("LIVE_ASK_RELIABILITY_HEALTH_VERIFIED",revision,flush=True)

def main():
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    mode=sys.argv[1] if len(sys.argv)>1 else "preflight"
    if mode=="preflight":
        preflight(api);return
    if mode!="publish":
        raise ValueError("preflight or publish only")
    if not api.token or os.environ.get("SWRLZ_ASK_RELIABILITY_APPROVED")!="1":
        raise RuntimeError("PUBLISH_APPROVAL_MISSING")
    parent=(BACKUP/"revision.txt").read_text().strip()
    before={f:(BACKUP/f).read_bytes() for f in FILES}
    after={"station.py":patch_station(before["station.py"].decode()).encode(),
           "chat/§wyrlz/index.html":patch_chat(before["chat/§wyrlz/index.html"].decode()).encode()}
    if api.repo_info(SPACE,repo_type="space").sha!=parent:
        raise RuntimeError("HF_SOURCE_CHANGED_REPREFLIGHT_REQUIRED")
    deployed=None
    try:
        deployed=publish(api,parent,after,"§C: recover live coding Ask from transient account storage errors")
        for trial in range(40):
            try:
                health(api,deployed)
                break
            except Exception:
                if trial==39:raise
                time.sleep(8)
        print("ASK_RELIABILITY_DEPLOYED",deployed,flush=True)
    except Exception:
        if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
            reverted=publish(api,deployed,before,"Restore exact §C pre-Ask-reliability sources")
            print("ASK_RELIABILITY_ROLLED_BACK",reverted,flush=True)
        raise

if __name__=="__main__":
    main()
