#!/usr/bin/env python3
"""Guarded release: auto-resume exact saved code, plus live progress/steering.

The live Hugging Face Space is source-of-truth. Snapshot current revision,
patch exact anchors, AST/JS check, run deterministic fake continuation tests,
publish with parent-revision CAS, and restore exact prior files if health fails.
Never modify model weights, threads, user projects, or §E.
"""
from __future__ import annotations
import ast, hashlib, json, os, re, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
FILES=("station.py","qwen_coder_engine.py","chat/§wyrlz/index.html")
BACKUP=Path("hf-guided-continuation-backup")
MARK="swrlz-live-guided-code-v1"

def one(src,old,new,label):
    n=src.count(old)
    if n!=1: raise RuntimeError("LIVE_ANCHOR_DRIFT "+label+" occurrences="+str(n))
    return src.replace(old,new,1)

def patch_coder(src):
    if MARK in src: raise RuntimeError("Already integrated coder")
    src=one(src,
        "allow_continue=False,seed_text='',cancel_check=None):",
        "allow_continue=False,seed_text='',cancel_check=None,live_guidance=None):",
        "coder guidance parameter")
    src=one(src,
        "    next_messages=_swrlz_resume_tail_messages(seed_text) if seed_text else messages",
        """    next_messages=_swrlz_resume_tail_messages(seed_text) if seed_text else messages
    # swrlz-live-guided-code-v1: guidance affects future output only; earlier
    # committed source bytes are never overwritten by append-only continuation.
    if seed_text and live_guidance:
        guidance=str(live_guidance)[:3600]
        next_messages[0]["content"]+=(
            " The user added requirements while you were coding. Incorporate "
            "them in remaining sections when possible; do not discard or "
            "repeat prior source, and do not claim earlier code was revised. "
            "USER_GUIDANCE: "+guidance)""",
        "coder guidance injection")
    src=one(src,
        'seed_text=source,cancel_check=payload.get("_cancelCheck"))',
        'seed_text=source,cancel_check=payload.get("_cancelCheck"),live_guidance=payload.get("liveCodeSteering"))',
        "resume call forwards bounded steering")
    ast.parse(src,filename="qwen_coder_engine.py")
    return src

AUTO_CHAIN='''# swrlz-live-guided-code-v1: one continuous generation across native
# 240-second checkpoints. Stop, checkpoint integrity and validator remain authoritative.
def _swrlz_auto_code_chain(events,payload,key,request_id):
    started=time.monotonic()
    last_size=0
    checkpoints=0
    while True:
        saved=None
        for event in events:
            if isinstance(event,dict) and event.get("type")=="CODE_OUTPUT_CHECKPOINT":
                cp=event.get("checkpoint") if isinstance(event.get("checkpoint"),dict) else {}
                source=str(cp.get("source") or "")
                valid=(cp.get("schema")=="swrlz-long-code-checkpoint-v1"
                       and bool(source) and not cp.get("repairNeeded")
                       and len(source.encode("utf-8"))<=240*1024
                       and hashlib.sha256(source.encode("utf-8")).hexdigest()==cp.get("sourceSha256"))
                # Finite work budget, no-progress guard, and exact saved bytes.
                can_resume=(valid and _coder_generate is not None
                    and len(source)>last_size+16 and checkpoints<32
                    and time.monotonic()-started<10800)
                if can_resume:
                    yield event
                    saved=cp
                    break
            yield event
        if saved is None:
            return
        try:
            events.close()
        except (AttributeError,ValueError):
            pass
        checkpoints+=1
        last_size=len(str(saved["source"]))
        with _lock:
            session=_sessions.get(key) or {}
            generation=session.get("activeGeneration") or {}
            if (generation.get("requestId")!=request_id or generation.get("cancelRequested")):
                return
            notes=generation.get("liveCodeInstructions") or []
            carry=[]
            for note in notes:
                if note.get("state")=="QUEUED":
                    note["state"]="FORWARDED_UNVERIFIED"
                    carry.append(str(note.get("text") or "")[:1000])
            guidance="; ".join(carry)[:3600]
            if guidance:
                generation["status"].append({"phase":"CODE_GUIDANCE_FORWARDED",
                    "reason":"New requirements forwarded to continuation. Prior sections may require a later revision."})
        payload["codeContinuation"]=saved
        payload["liveCodeSteering"]=guidance
        yield {"type":"STATUS","phase":"CODE_CONTINUING_AUTOMATICALLY",
               "reason":"Continuing saved source in the same task after checkpoint "+
                   str(checkpoints)+"; source remains unverified until validation."}
        events=_coder_generate(payload)


'''

LIVE_CONTROL='''# swrlz-live-guided-code-v1: independent live control lane. This is
# account/session-scoped state, not a parallel second model decode.
@app.post("/api/lalm_station/live-code-control")
async def live_code_control(request:Request):
    body=await request.json()
    if not isinstance(body,dict):raise HTTPException(400,"Invalid control payload")
    kind=str(body.get("kind") or "ASK").upper()
    prompt=str(body.get("text") or "").strip()
    rid=str(body.get("requestId") or "")
    tid=str(body.get("threadId") or "")
    if kind not in ("ASK","STEER") or not prompt or len(prompt)>2000:
        raise HTTPException(400,"Invalid live coding question or instruction")
    key,s=_session(request)
    with _lock:
        g=s.get("activeGeneration") or {}
        if not rid or rid!=g.get("requestId") or tid!=g.get("threadId"):
            raise HTTPException(409,"Coding task no longer active in that conversation")
        if kind=="STEER" and g.get("terminal"):
            raise HTTPException(409,"Coding task completed; use a normal revision message")
        if kind=="STEER":
            instructions=g.setdefault("liveCodeInstructions",[])
            if len(instructions)>=24:
                raise HTTPException(409,"Too many pending coding instructions")
            item={"id":uuid.uuid4().hex,"text":prompt,"state":"QUEUED",
                  "createdAtUnixMs":int(time.time()*1000)}
            instructions.append(item)
            try:_commit_revision(s)
            except Exception:
                instructions.pop()
                raise
            return JSONResponse({"ok":True,"kind":"STEER","state":"QUEUED",
                "answer":"Instruction saved while generation continues. It will be forwarded at the next safe continuation checkpoint. Changes to earlier code are not yet applied or verified."},
                headers={"Cache-Control":"private, no-store"})
        thread=next((t for t in s.get("threads",[]) if t.get("id")==tid),None)
        pending=(thread or {}).get("pendingCodeGeneration") or {}
        preview=str(g.get("previewText") or "")
        source=str(pending.get("source") or "")
        bytes_saved=len(source.encode("utf-8"))
        bytes_live=len(preview.encode("utf-8"))
        segments=int((g.get("codeDraftCheckpoint") or {}).get("segments") or
                     pending.get("segmentsCompleted") or 0)
        latest=(g.get("status") or [{}])[-1]
        phase=str(latest.get("phase") or g.get("phase") or "GENERATING").replace("_"," ").lower()
        notes=g.get("liveCodeInstructions") or []
        reply=("Coding status: "+("finished" if g.get("terminal") else "still running")+
          ". Latest phase: "+phase+". "+
          str(max(bytes_saved,bytes_live))+" bytes of draft output observed; "+
          str(segments)+" checkpoint segment(s) recorded. "+
          str(sum(n.get("state")=="QUEUED" for n in notes))+
          " guidance note(s) waiting. "+
          "This draft is unverified until structural validation passes. "
          "The remaining code length and exact completion time are unknown.")
        if re.search(r"(?i)what (?:have|has) (?:you|it) (?:done|written)|show (?:me )?(?:current|latest) code|what.*so far",prompt):
            excerpt=preview[-600:] or source[-600:]
            if excerpt:reply+="\\nLatest draft tail (not a validated program):\\n"+excerpt
        return JSONResponse({"ok":True,"kind":"ASK","answer":reply,
            "progress":{"sourceBytes":max(bytes_saved,bytes_live),
            "checkpointSegments":segments,"phase":phase,"terminal":bool(g.get("terminal")),
            "verification":"UNVERIFIED" if not g.get("terminal") else
            str((g.get("candidateValidation") or {}).get("status") or "UNKNOWN")}},
            headers={"Cache-Control":"private, no-store"})


'''

def patch_station(src):
    if MARK in src:raise RuntimeError("Already integrated station")
    src=one(src,"def _run(key,request_id,model_id,payload,assistant_id,forge_context=None):",
                AUTO_CHAIN+"def _run(key,request_id,model_id,payload,assistant_id,forge_context=None):",
                "station helper insertion")
    src=one(src,"        for event in event_source:",
                "        for event in _swrlz_auto_code_chain(event_source,payload,key,request_id):",
                "station event owner handoff")
    src=one(src,'@app.post("/api/lalm_station/cancel")',
                LIVE_CONTROL+'@app.post("/api/lalm_station/cancel")',
                "station live control route")
    ast.parse(src,filename="station.py")
    return src

JS_GUIDE=r'''      // swrlz-live-guided-code-v1: an independent composer action, never Stop.
      const swrlzGuideButton=document.createElement("button");
      swrlzGuideButton.type="button";swrlzGuideButton.hidden=true;
      swrlzGuideButton.textContent="Ask";
      swrlzGuideButton.title="Ask progress or guide coding without stopping it";
      swrlzGuideButton.setAttribute("aria-label","Ask or steer the running coding task");
      swrlzGuideButton.style.cssText="flex:0 0 auto;min-width:46px;height:42px;padding:0 8px;border-radius:24px;border:1px solid #38e8ff;background:#0b3046;color:#eef8ff;font-size:13px;cursor:pointer";
      stopButton.parentElement?.insertBefore(swrlzGuideButton,stopButton);
      const swrlzGuideReceipt=document.createElement("div");
      swrlzGuideReceipt.hidden=true;
      swrlzGuideReceipt.setAttribute("role","status");
      swrlzGuideReceipt.style.cssText="position:fixed;left:12px;right:12px;bottom:calc(var(--composer-visible-height, 170px) + 10px);max-height:28vh;overflow:auto;z-index:30;border-radius:12px;border:1px solid rgba(143,234,255,.45);background:#061b2d;color:#e8f8ff;box-shadow:0 8px 28px #000b;padding:13px;font-size:13px;white-space:pre-wrap";
      document.body.appendChild(swrlzGuideReceipt);
      const swrlzGuideClose=document.createElement("button");
      swrlzGuideClose.type="button";swrlzGuideClose.textContent="×";
      swrlzGuideClose.setAttribute("aria-label","Dismiss coding answer");
      swrlzGuideClose.style.cssText="float:right;border:0;background:transparent;color:inherit;font-size:21px;cursor:pointer";
      swrlzGuideReceipt.appendChild(swrlzGuideClose);
      const swrlzGuideAnswer=document.createElement("div");
      swrlzGuideReceipt.appendChild(swrlzGuideAnswer);
      swrlzGuideClose.addEventListener("click",()=>{swrlzGuideReceipt.hidden=true;});
      let swrlzGuideSubmitting=false;
      const sendLiveCodeGuide=async()=>{
        if(swrlzGuideSubmitting)return;
        const text=prompt.value.trim();
        const generation=stationGeneration;
        if(!text||!generation?.requestId||generation.threadId!==activeThreadId)return;
        const rid=generation.requestId,tid=generation.threadId;
        const action=/\\b(add|change|modify|fix|remove|rewrite|refactor|implement|ensure|include|make sure|update|switch|move)\\b/i.test(text)?"STEER":"ASK";
        swrlzGuideSubmitting=true;swrlzGuideButton.disabled=true;
        try{
          const response=await fetch("/api/lalm_station/live-code-control",{
            method:"POST",credentials:"same-origin",cache:"no-store",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({kind:action,text,requestId:rid,threadId:tid})
          });
          const result=await response.json().catch(()=>({}));
          if(!response.ok||!result.ok)throw Error(result.detail||result.code||"Request rejected");
          if(prompt.value.trim()===text){prompt.value="";resizeComposer();}
          swrlzGuideAnswer.textContent=(action==="STEER"?"Guidance recorded\\n":"Progress answer\\n")+String(result.answer||"");
          swrlzGuideReceipt.hidden=false;
          void syncStation();
        }catch(error){
          swrlzGuideAnswer.textContent="Couldn't send coding question: "+String(error.message||error);
          swrlzGuideReceipt.hidden=false;
        }finally{swrlzGuideSubmitting=false;swrlzGuideButton.disabled=false;}
      };
      swrlzGuideButton.addEventListener("click",event=>{
        event.preventDefault();event.stopPropagation();void sendLiveCodeGuide();
      });
'''
def patch_chat(src):
    if MARK in src:raise RuntimeError("Already integrated chat")
    anchor='      let stationAcknowledgedRequest=null,stationSubmission=null,stationCancellation=null;'
    src=one(src,anchor,anchor+"\n"+JS_GUIDE,"chat independent send control")
    src=one(src,
        '        stopButton.disabled=!!stationCancellation&&stationCancellation.requestId===requestId;',
        '''        stopButton.disabled=!!stationCancellation&&stationCancellation.requestId===requestId;
        swrlzGuideButton.hidden=!(active&&stationGeneration?.requestId&&
          stationGeneration.threadId===activeThreadId);
        if(!active)swrlzGuideReceipt.hidden=true;''',
        "chat guide visibility")
    src=one(src,
        '        if(settingsState.general.enterToSend||shortcut){e.preventDefault();commitDraftFromPrompt();}',
        '''        if(settingsState.general.enterToSend||shortcut){
          e.preventDefault();
          if(stationBusy()){void sendLiveCodeGuide();return;}
          commitDraftFromPrompt();
        }''',
        "chat keyboard guide routing")
    return src

def sha(data):return hashlib.sha256(data).hexdigest()

def test_auto_chain(src):
    tree=ast.parse(src)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)
            and n.name=="_swrlz_auto_code_chain")
    module=ast.Module(body=[fn],type_ignores=[])
    class DummyLock:
        def __enter__(self):return self
        def __exit__(self,*args):return False
    def checkpoint(source):
        return {"schema":"swrlz-long-code-checkpoint-v1","source":source,
                "sourceSha256":sha(source.encode()),"segmentsCompleted":1}
    sessions={"k":{"activeGeneration":{"requestId":"r","liveCodeInstructions":[
        {"id":"i","text":"Use controller support","state":"QUEUED"}]}}}
    def original():
        yield {"type":"CANDIDATE_PREVIEW_DELTA","text":"abc"}
        yield {"type":"CODE_OUTPUT_CHECKPOINT","checkpoint":checkpoint("a"*80)}
        yield {"type":"DELTA","text":"Send Continue code"}
        yield {"type":"COMPLETED"}
    def resume(payload):
        assert payload["codeContinuation"]["source"]=="a"*80
        assert "controller support" in payload["liveCodeSteering"]
        yield {"type":"CANDIDATE_PREVIEW_DELTA","text":"b"*20}
        yield {"type":"DELTA","text":"accepted full code"}
        yield {"type":"COMPLETED"}
    ns={"time":time,"hashlib":hashlib,"_lock":DummyLock(),
        "_sessions":sessions,"_coder_generate":resume}
    exec(compile(module,"<auto-test>","exec"),ns)
    events=list(ns["_swrlz_auto_code_chain"](original(),{},"k","r"))
    assert any(x.get("phase")=="CODE_CONTINUING_AUTOMATICALLY" for x in events)
    assert any(x.get("text")=="accepted full code" for x in events)
    assert not any("Send Continue" in x.get("text","") for x in events)
    assert sessions["k"]["activeGeneration"]["liveCodeInstructions"][0]["state"]=="FORWARDED_UNVERIFIED"
    # If the checkpoint is a repair request, do not silently append to closed code.
    cp=checkpoint("a"*80);cp["repairNeeded"]=True
    untouched=list(ns["_swrlz_auto_code_chain"](
        iter([{"type":"CODE_OUTPUT_CHECKPOINT","checkpoint":cp},
              {"type":"DELTA","text":"pause for repair"}]),{},"k","r"))
    assert untouched[-1]["text"]=="pause for repair"
    print("AUTO_CHAIN_SOURCE_INTEGRITY_FAKE_TEST_PASS",flush=True)

def test_ui(src):
    scripts=re.findall(r"<script\\b([^>]*)>(.*?)</script\\s*>",src,flags=re.I|re.S)
    count=0
    with tempfile.TemporaryDirectory() as folder:
        for i,(attrs,body) in enumerate(scripts):
            if not body.strip() or "application/json" in attrs:continue
            file=Path(folder)/(str(i)+".js");file.write_text(body)
            result=subprocess.run(["node","--check",str(file)],
                                  capture_output=True,text=True,timeout=25)
            if result.returncode:raise RuntimeError("JS_SYNTAX "+result.stderr[-1200:])
            count+=1
    assert count>0 and "/api/lalm_station/live-code-control" in src
    print("CHAT_JS_SYNTAX_PASS",count,flush=True)

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before={file:Path(hf_hub_download(SPACE,file,repo_type="space",
                  revision=rev,token=api.token)).read_bytes() for file in FILES}
    after={
        "station.py":patch_station(before["station.py"].decode()).encode(),
        "qwen_coder_engine.py":patch_coder(before["qwen_coder_engine.py"].decode()).encode(),
        "chat/§wyrlz/index.html":patch_chat(before["chat/§wyrlz/index.html"].decode()).encode(),
    }
    test_auto_chain(after["station.py"].decode())
    test_ui(after["chat/§wyrlz/index.html"].decode())
    BACKUP.mkdir(parents=True,exist_ok=True)
    for file,data in before.items():
        dest=BACKUP/file;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    (BACKUP/"revision.txt").write_text(rev)
    (BACKUP/"manifest.json").write_text(json.dumps(
        {"revision":rev,"before":{p:sha(x) for p,x in before.items()},
         "after":{p:sha(x) for p,x in after.items()}},indent=2))
    print("LIVE_GUIDANCE_PREFLIGHT_PASS",rev,flush=True)
    return rev,before,after

def publish(api,rev,files,reason):
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("CONCURRENT_SPACE_CHANGE")
    with tempfile.TemporaryDirectory() as folder:
        operations=[]
        for name,data in files.items():
            p=Path(folder)/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            operations.append(CommitOperationAdd(path_in_repo=name,path_or_fileobj=str(p)))
        commit=api.create_commit(repo_id=SPACE,repo_type="space",
             parent_commit=rev,operations=operations,commit_message=reason)
    return str(commit.oid)

def live_check(expected):
    response=urllib.request.urlopen(urllib.request.Request(
        BASE+"/chat/%C2%A7wyrlz",
        headers={"User-Agent":"swrlz-guided-code-release"}),timeout=30)
    page=response.read(400000).decode("utf-8","replace")
    if MARK not in page:raise RuntimeError("LIVE_CHAT_MARKER_NOT_VISIBLE")
    resp=urllib.request.urlopen(BASE+"/api/hf/qwen35-ready",timeout=30)
    info=json.load(resp)
    if info.get("model")!="qwen3.5-9b":raise RuntimeError("MODEL_ID_DRIFT")
    print("LIVE_GUIDANCE_DEPLOYED_UI_AND_MODEL_ID",expected,flush=True)

def main():
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    mode=sys.argv[1] if len(sys.argv)>1 else "preflight"
    if mode=="preflight":
        snapshot(api);return
    if mode!="publish":raise SystemExit("preflight|publish")
    if os.environ.get("SWRLZ_GUIDED_CODE_APPROVED")!="1" or not api.token:
        raise RuntimeError("PUBLISH_AUTHORIZATION_REQUIRED")
    rev=(BACKUP/"revision.txt").read_text().strip()
    before={p:(BACKUP/p).read_bytes() for p in FILES}
    after={
        "station.py":patch_station(before["station.py"].decode()).encode(),
        "qwen_coder_engine.py":patch_coder(before["qwen_coder_engine.py"].decode()).encode(),
        "chat/§wyrlz/index.html":patch_chat(before["chat/§wyrlz/index.html"].decode()).encode(),
    }
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("SPACE_CHANGED_SINCE_PREFLIGHT")
    deployed=None
    try:
        deployed=publish(api,rev,after,"§C: auto-resume unfinished code and answer progress while generating")
        for attempt in range(45):
            try:
                live_check(deployed);break
            except Exception as exc:
                if attempt==44:raise
                time.sleep(8)
        print("LIVE_GUIDED_CODING_VERIFIED",deployed,flush=True)
    except Exception:
        if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
            restored=publish(api,deployed,before,"Rollback §C guided coding to exact previous source")
            print("LIVE_GUIDANCE_EXACT_ROLLBACK",restored,flush=True)
        raise
if __name__=="__main__":main()
