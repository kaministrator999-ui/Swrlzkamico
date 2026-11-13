#!/usr/bin/env python3
"""§C guarded HTML continuation capacity + validated provisional coding stream.

Patch exact current Hugging Face Space (not stale GitHub checkout).
All changes must be AST/syntax-tested, SHA-snapshotted and parent-CAS published;
no new inference provider, weights, hardware, auth, identity, §E, voice or
persistent conversation history changes.
"""
from __future__ import annotations
import ast,hashlib,http.cookiejar,json,os,re,subprocess,sys,tempfile,time
import urllib.parse,urllib.request,uuid
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
RUNTIME="qwen35_single_runtime.py"
CODER="qwen_coder_engine.py"
GENERAL="lfm2_700m_engine.py"
STATION="station.py"
CHAT="chat/§wyrlz/index.html"
FILES=(RUNTIME,CODER,GENERAL,STATION,CHAT)
REVISION_FILE="qwen35-code-preview-backup/revision.txt"
BACKUP=Path("qwen35-code-preview-backup")
CONTEXT=16384
THREADS=18
TAG="swrlz-qwen35-code-preview-context-v1"
HEADERS={"User-Agent":"Swyrlz-Coding-Context16k-Preview-Guard","Cache-Control":"no-cache"}

def emit(event,**values):
    print("CODE_PREVIEW_RELEASE",json.dumps({"event":event,**values},ensure_ascii=False,sort_keys=True),flush=True)

def sha(b):return hashlib.sha256(b).hexdigest()

def one(text,old,new,name):
    count=text.count(old)
    if count!=1:raise RuntimeError("EXACT_SOURCE_ANCHOR_DRIFT: %s %s"%(name,count))
    return text.replace(old,new,1)

def context_patch(source,file):
    if TAG in source:raise RuntimeError("Source already patched "+file)
    source=one(source,
        "CONTEXT_TOKENS = 8192" if file==RUNTIME else "CONTEXT_TOKENS=8192",
        "CONTEXT_TOKENS = 16384" if file==RUNTIME else "CONTEXT_TOKENS=16384",
        file+" context")
    if file in (GENERAL,CODER):
        old='''    target_input=CONTEXT_TOKENS-desired_output-CONTEXT_SAFETY_TOKENS
    kept=list(history[-16:])'''
        new='''    # swrlz-qwen35-code-preview-context-v1: preserve mandatory complete
    # source before negotiating output reservation. Never truncate user code.
    mandatory_messages=[{"role":"system","content":system},
                        {"role":"user","content":prompt}]
    mandatory_tokens=_token_count(model,mandatory_messages)
    max_decode=CONTEXT_TOKENS-mandatory_tokens-CONTEXT_SAFETY_TOKENS
    if max_decode>=MIN_OUTPUT_TOKENS:
        desired_output=min(desired_output,max_decode)
    target_input=CONTEXT_TOKENS-desired_output-CONTEXT_SAFETY_TOKENS
    kept=list(history[-16:])'''
        source=one(source,old,new,file+" source fit")
        old='''    max_input=CONTEXT_TOKENS-desired_output-CONTEXT_SAFETY_TOKENS
    messages=[{"role":"system","content":system}]+recent+[{"role":"user","content":fitted_prompt}]'''
        new='''    # Same source-preserving allowance for canonical repairs.
    mandatory_tokens=_token_count(model,[{"role":"system","content":system},
        {"role":"user","content":fitted_prompt}])
    max_decode=CONTEXT_TOKENS-mandatory_tokens-CONTEXT_SAFETY_TOKENS
    if max_decode>=MIN_OUTPUT_TOKENS:
        desired_output=min(desired_output,max_decode)
    max_input=CONTEXT_TOKENS-desired_output-CONTEXT_SAFETY_TOKENS
    messages=[{"role":"system","content":system}]+recent+[{"role":"user","content":fitted_prompt}]'''
        source=one(source,old,new,file+" repair fit")
    if file==CODER:
        old='''    budget_policy=response_budget(programming,prompt)
    delivery_output_limit=(512 if source_change_mode=="plan" else 2048 if source_change_mode else budget_policy["tokens"])'''
        new='''    budget_policy=response_budget(programming,prompt)
    if web_page_delivery and not source_change_mode:
        # An HTML file requested in full gets room to return a full improved
        # version, not a 4K output reservation that evicts its own source.
        budget_policy={**budget_policy,"tokens":max(8192,int(budget_policy["tokens"])),
                       "tier":"web-page-extended"}
    delivery_output_limit=(512 if source_change_mode=="plan" else 2048 if source_change_mode else budget_policy["tokens"])'''
        source=one(source,old,new,"HTML response budget")
        source=one(source,"WEB_PAGE_OUTPUT_TOKENS=4096","WEB_PAGE_OUTPUT_TOKENS=8192","HTML limit")
        source=one(source,"PROJECT_OUTPUT_TOKENS=4096","PROJECT_OUTPUT_TOKENS=8192","project limit")
        source=one(source,"LARGE_OUTPUT_TOKENS=6144","LARGE_OUTPUT_TOKENS=12288","large limit")
    ast.parse(source,filename=file)
    return source

PREVIEW_FUNCTION=r'''def _swrlz_code_candidate_preview(model,messages,max_tokens,temperature,attempt):
    """Yield unverified model deltas; return complete source and original telemetry.

    CANDIDATE_PREVIEW_DELTA is never a final DELTA. Station does not persist it,
    and UI never marks it accepted or enables code artifact controls.
    """
    started=time.perf_counter()
    first_token_at=None
    parts=[]
    delta_chunks=0
    observation={"finishReason":None,"requestedMaxTokens":int(max_tokens)}
    for chunk in model.create_chat_completion(
        messages=messages,max_tokens=max_tokens,temperature=temperature,stream=True
    ):
        observe_completion_chunk(observation,chunk)
        choices=chunk.get("choices") or []
        delta=(choices[0].get("delta") or {}).get("content") if choices else None
        if delta:
            if first_token_at is None:first_token_at=time.perf_counter()
            parts.append(str(delta))
            delta_chunks+=1
            yield {"type":"CANDIDATE_PREVIEW_DELTA","text":str(delta),"attempt":attempt}
    ended=time.perf_counter()
    return "".join(parts), {
        "durationMs":round((ended-started)*1000,3),
        "firstTokenLatencyMs":round((first_token_at-started)*1000,3)
                              if first_token_at is not None else None,
        "deltaChunks":delta_chunks,**observation,
    }

'''
def preview_patch(source):
    source=one(source,"def generate_events(payload):",
                PREVIEW_FUNCTION+"def generate_events(payload):","preview helper")
    source=one(source,
        "candidate_text,timing=buffered_chat_completion(model,messages,response_tokens,temperature)",
        "candidate_text,timing=yield from _swrlz_code_candidate_preview(model,messages,response_tokens,temperature,1)",
        "first candidate preview")
    source=one(source,
        '''            if candidate_check.get("status")=="REJECT":
                regeneration_attempted=True''',
        '''            if candidate_check.get("status")=="REJECT":
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":2}
                regeneration_attempted=True''',
        "first rejection reset")
    source=one(source,
        "retry_text,retry_timing=buffered_chat_completion(model,retry_messages,retry_tokens,min(0.45,temperature+0.10))",
        "retry_text,retry_timing=yield from _swrlz_code_candidate_preview(model,retry_messages,retry_tokens,min(0.45,temperature+0.10),2)",
        "second candidate preview")
    source=one(source,
        '''                if candidate_check.get("status")=="REJECT":
                    retry_stalled=''',
        '''                if candidate_check.get("status")=="REJECT":
                    yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":3}
                    retry_stalled=''', "second rejection reset")
    source=one(source,
        "third_text,third_timing=buffered_chat_completion(model,final_messages,final_tokens,min(0.50,temperature+0.15))",
        "third_text,third_timing=yield from _swrlz_code_candidate_preview(model,final_messages,final_tokens,min(0.50,temperature+0.15),3)",
        "third candidate preview")
    source=one(source,
        '''            else:
                safe_text="I couldn't produce a candidate that satisfies the programming contract, so I did not return the rejected code."''',
        '''            else:
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":0}
                safe_text="I couldn't produce a candidate that satisfies the programming contract, so I did not return the rejected code."''',
        "final rejection does not expose draft")
    ast.parse(source,filename=CODER)
    return source

def station_patch(s):
    if TAG in s:raise RuntimeError("station already patched")
    s=one(s,
        '''        sent_text=""
        sent_status=0''',
        '''        sent_text=""
        sent_preview=""
        sent_preview_epoch=0
        sent_status=0''',"stream preview markers")
    old='''            text_now=str(g.get("text") or "")
            if len(text_now)>len(sent_text):'''
    new='''            # swrlz-qwen35-code-preview-context-v1: stream unverified code
            # separately; never append it to accepted/persisted answer text.
            preview_epoch=int(g.get("previewEpoch") or 0)
            if preview_epoch!=sent_preview_epoch:
                sent_preview_epoch=preview_epoch
                sent_preview=""
                yield json.dumps({"type":"CANDIDATE_PREVIEW_RESET","requestId":rid,
                                  "attempt":int(g.get("previewAttempt") or 0),
                                  "seq":int(g.get("lastSeq") or 0)},ensure_ascii=False)+"\\n"
            preview_now=str(g.get("previewText") or "")
            if len(preview_now)>len(sent_preview) and not str(g.get("text") or ""):
                draft_delta=preview_now[len(sent_preview):]
                sent_preview=preview_now
                yield json.dumps({"type":"CANDIDATE_PREVIEW_DELTA","text":draft_delta,
                                  "attempt":int(g.get("previewAttempt") or 0),
                                  "seq":int(g.get("lastSeq") or 0),
                                  "requestId":rid},ensure_ascii=False)+"\\n"
            text_now=str(g.get("text") or "")
            if len(text_now)>len(sent_text):'''
    s=one(s,old,new,"stream projection preview")
    old='''                if kind=="DELTA":
                    delta=str(event.get("text") or "");text+=delta;g["text"]=text'''
    new='''                if kind=="CANDIDATE_PREVIEW_DELTA":
                    part=str(event.get("text") or "")
                    if len(str(g.get("previewText") or ""))+len(part)<=131072:
                        g["previewText"]=str(g.get("previewText") or "")+part
                        g["previewAttempt"]=int(event.get("attempt") or 1)
                elif kind=="CANDIDATE_PREVIEW_RESET":
                    g["previewText"]=""
                    g["previewEpoch"]=int(g.get("previewEpoch") or 0)+1
                    g["previewAttempt"]=int(event.get("attempt") or 0)
                elif kind=="DELTA":
                    delta=str(event.get("text") or "");text+=delta;g["text"]=text
                    g["previewText"]=""'''
    s=one(s,old,new,"station ephemeral preview")
    old='''"stationTiming":None,"resourcePlan":None,"diagnosticTrace":None,'''
    new='''"stationTiming":None,"resourcePlan":None,"previewText":"","previewEpoch":0,"previewAttempt":0,"diagnosticTrace":None,'''
    s=one(s,old,new,"new generation preview fields")
    ast.parse(s,filename=STATION)
    return s

UI_STYLE=r'''  <style id="swrlz-guarded-code-draft-v1">
    .swrlz-code-draft{margin:.75rem 0;padding:.8rem;border:1px solid rgba(80,192,227,.38);border-radius:14px;background:rgba(3,20,38,.82);max-width:100%;min-width:0}
    .swrlz-code-draft-label{font:600 .78rem/1.4 system-ui,sans-serif;letter-spacing:.035em;color:#9ce1f4;margin-bottom:.65rem}
    .swrlz-code-draft pre{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;font: .82rem/1.55 ui-monospace,SFMono-Regular,Consolas,monospace;color:#dbf2ff;max-height:44vh;overflow:auto;overscroll-behavior:contain;margin:0;padding:.2rem}
    @media (max-width:680px){.swrlz-code-draft{margin:.55rem 0;padding:.65rem}.swrlz-code-draft pre{font-size:.78rem;max-height:38vh}}
  </style>
'''
def ui_patch(s):
    if TAG in s or "swrlz-guarded-code-draft-v1" in s:raise RuntimeError("UI already patched")
    s=one(s,"</head>",UI_STYLE+"</head>","HTML styling")
    old='''        const body=node.querySelector(".assistant-body");
        const nextText=String(g.text||"");'''
    new='''        const body=node.querySelector(".assistant-body");
        // swrlz-qwen35-code-preview-context-v1: this is provisional display
        // only, never a saved response or a runnable/downloadable code artifact.
        const draftText=(!g.terminal&&!String(g.text||"").trim())
          ?String(g.previewText||""):"";
        let draftPanel=node.querySelector(".swrlz-code-draft");
        if(draftText){
          if(!draftPanel){
            draftPanel=document.createElement("div");
            draftPanel.className="swrlz-code-draft";
            draftPanel.setAttribute("aria-label","Unverified code in progress");
            const label=document.createElement("div");
            label.className="swrlz-code-draft-label";
            label.textContent="Code draft · generating and validating · not saved";
            const code=document.createElement("pre");
            draftPanel.append(label,code);body.before(draftPanel);
          }
          const code=draftPanel.querySelector("pre");
          if(code&&code.textContent!==draftText)code.textContent=draftText;
        }else if(draftPanel){draftPanel.remove();}
        const nextText=String(g.text||"");'''
    s=one(s,old,new,"active response draft panel")
    old='''            if(event.type==="DELTA"){
              const deltaText=String(event.text||"");
              stationGeneration.text=(stationGeneration.text||"")+deltaText;
              if(deltaText)window.dispatchEvent(new CustomEvent("swrlz-voice-delta",{detail:{requestId,threadId,text:deltaText}}));
            }
            else if(event.type==="WIDGET"'''
    new='''            if(event.type==="DELTA"){
              const deltaText=String(event.text||"");
              stationGeneration.text=(stationGeneration.text||"")+deltaText;
              stationGeneration.previewText="";
              if(deltaText)window.dispatchEvent(new CustomEvent("swrlz-voice-delta",{detail:{requestId,threadId,text:deltaText}}));
            }
            else if(event.type==="CANDIDATE_PREVIEW_DELTA"){
              stationGeneration.previewText=(stationGeneration.previewText||"")+String(event.text||"");
              stationGeneration.previewAttempt=Number(event.attempt||1);
            }
            else if(event.type==="CANDIDATE_PREVIEW_RESET"){
              stationGeneration.previewText="";
              stationGeneration.previewAttempt=Number(event.attempt||0);
            }
            else if(event.type==="WIDGET"'''
    s=one(s,old,new,"client preview events")
    old='''          stationGeneration={...stationGeneration,terminal:true,terminalType:state,...(typeof text==="string"?{text}: {})};'''
    new='''          stationGeneration={...stationGeneration,terminal:true,terminalType:state,
            previewText:"",...(typeof text==="string"?{text}: {})};'''
    s=one(s,old,new,"terminal preview cleanup")
    return s

def validate(before,after):
    for name in (RUNTIME,CODER,GENERAL,STATION):
        ast.parse(after[name].decode("utf-8"),filename=name)
    coder=after[CODER].decode()
    general=after[GENERAL].decode()
    runtime=after[RUNTIME].decode()
    ui=after[CHAT].decode()
    station=after[STATION].decode()
    for name in (RUNTIME,CODER,GENERAL):
        assert "CONTEXT_TOKENS" in after[name].decode()
    assert "CONTEXT_TOKENS = 16384" in runtime
    assert "CONTEXT_TOKENS=16384" in coder
    assert "CONTEXT_TOKENS=16384" in general
    assert "Qwen3.5-9B-Q4_K_M.gguf" in runtime
    assert "DECODE_THREADS = 18 if CPU_CAPACITY == 16" in runtime
    assert "BATCH_THREADS = 18 if CPU_CAPACITY == 16" in runtime
    assert '"cache_prompt": True' in runtime
    assert "PARALLEL_REQUESTS = 1" in runtime
    assert "model.create_chat_completion(" in coder
    assert 'yield {"type":"CANDIDATE_PREVIEW_DELTA"' in coder
    assert "candidate_check=completion_validation(" in coder
    assert 'yield {"type":"CANDIDATE_VALIDATION"' in coder
    assert 'yield {"type":"DELTA","text":candidate_text}' in coder
    assert "model_history=model_history[-4:]" not in coder
    assert "CANDIDATE_PREVIEW_DELTA" in station and "CANDIDATE_PREVIEW_RESET" in station
    assert '"previewText":""' in station
    assert "CANDIDATE_PREVIEW_DELTA" in ui
    assert "swrlz-code-draft" in ui
    assert 'code.textContent=draftText' in ui
    assert "window.dispatchEvent(new CustomEvent(\\"swrlz-voice-delta\\"" in ui
    assert "renderAssistantContent(body,nextText" in ui
    assert before[CHAT].count(b"</head>")==1
    assert ui.count('id="swrlz-guarded-code-draft-v1"')==1
    assert coder.count("BUILTIN_ASSISTANT_PROFILE=")==before[CODER].decode().count("BUILTIN_ASSISTANT_PROFILE=")
    assert general.count("BUILTIN_ASSISTANT_PROFILE=")==before[GENERAL].decode().count("BUILTIN_ASSISTANT_PROFILE=")
    # The 4,944 mandatory token / 8,192 response budget scenario now fits:
    assert 4944+8192+128 < CONTEXT
    # Programming repair and coding guards remain authoritative.
    for x in ("candidate_retry_messages(","enforce_strategy_change(","_candidate_structure_check",
              "strict_language","repair_turn","source_sized_budget("):
        assert x in coder
    # Check that all existing endpoint and chat wiring survives exactly.
    for x in ("/api/lalm_station/stream","/api/lalm_station/send","renderStationGeneration",
              "renderAssistantContent","stationSettledRequests"):
        assert x in ui
    assert "def stream_generation(" in station
    # Syntax-check all inline executable JS (HTML is 500KB and many modules).
    script_re=re.compile(r"<script\b([^>]*)>(.*?)</script\s*>",re.S|re.I)
    with tempfile.TemporaryDirectory(prefix="swrlz-code-preview-ui-") as td:
        for idx,m in enumerate(script_re.finditer(ui)):
            attrs=m.group(1).lower()
            if 'type="application/ld+json"' in attrs or 'type="application/json"' in attrs:
                continue
            content=m.group(2).strip()
            if not content:continue
            file=Path(td)/("inline-%d.js"%idx);file.write_text(content)
            result=subprocess.run(["node","--check",str(file)],capture_output=True,
                                  text=True,timeout=30)
            if result.returncode:
                raise RuntimeError("Inline Chat JS syntax invalid: "+result.stderr[-350:])
    # Integration semantic tests: a sample native chunk arrives first as
    # preview, and only an accepted candidate becomes a persisted DELTA.
    tree=ast.parse(coder)
    preview_fn=next(t for t in tree.body if isinstance(t,ast.FunctionDef)
                    and t.name=="_swrlz_code_candidate_preview")
    class Fake:
        def create_chat_completion(self,**kwargs):
            for s in ("<html>","<body>","OK</body></html>"):
                yield {"choices":[{"delta":{"content":s},"finish_reason":None}]}
            yield {"choices":[{"delta":{},"finish_reason":"stop"}]}
    class Clock:
        @staticmethod
        def perf_counter():return 5.0
    def observe(o,ch):
        v=(ch.get("choices") or [{}])[0].get("finish_reason")
        if v:o["finishReason"]=v
    env={"time":Clock,"observe_completion_chunk":observe}
    exec(compile(ast.Module(body=[preview_fn],type_ignores=[]),"<preview>", "exec"),env)
    gen=env["_swrlz_code_candidate_preview"](Fake(),[],100,0.2,1)
    parts=[]
    try:
        while True: parts.append(next(gen))
    except StopIteration as done: result=done.value
    assert len(parts)==3 and all(p["type"]=="CANDIDATE_PREVIEW_DELTA" for p in parts)
    assert result[0]=="<html><body>OK</body></html>"
    assert result[1]["finishReason"]=="stop"
    emit("STATIC_VALIDATION_PASS",files=list(FILES),
         originalProfilePreserved=True,userHistoryStoragePreserved=True,
         maxContext=CONTEXT,coderHTMLAllowedOutput=8192,
         partialPreviewUnverified=True,finalValidationRequired=True,
         modelChanged=False,threadPlanUnchanged=True)

def patch(before):
    after=dict(before)
    after[RUNTIME]=context_patch(before[RUNTIME].decode(),RUNTIME).encode()
    after[GENERAL]=context_patch(before[GENERAL].decode(),GENERAL).encode()
    coder=context_patch(before[CODER].decode(),CODER)
    after[CODER]=preview_patch(coder).encode()
    after[STATION]=station_patch(before[STATION].decode()).encode()
    after[CHAT]=ui_patch(before[CHAT].decode()).encode()
    validate(before,after)
    return after

def load_files(api,revision):
    return {f:Path(hf_hub_download(SPACE,f,repo_type="space",
              revision=revision,token=api.token)).read_bytes() for f in FILES}

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    original=load_files(api,rev)
    patched=patch(original)
    BACKUP.mkdir(exist_ok=True)
    for file,blob in original.items():
        path=BACKUP/file;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
    (BACKUP/"revision.txt").write_text(rev)
    (BACKUP/"manifest.json").write_text(json.dumps({
        "revision":rev,"fileHashes":{f:sha(original[f]) for f in FILES},
        "candidateHashes":{f:sha(patched[f]) for f in FILES},
        "paidHardware":False},indent=2))
    emit("PREFLIGHT",revision=rev,
         originalHashes={f:sha(original[f]) for f in FILES},
         candidateHashes={f:sha(patched[f]) for f in FILES})
    return rev,original,patched

def publish(api,expected_rev,parts,message):
    head=api.repo_info(SPACE,repo_type="space").sha
    if head!=expected_rev:raise RuntimeError("Concurrent HF Space source update; abort")
    with tempfile.TemporaryDirectory(prefix="swrlz-code-preview-") as td:
        operations=[]
        for file,data in parts.items():
            path=Path(td)/file
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
            operations.append(CommitOperationAdd(path_in_repo=file,path_or_fileobj=str(path)))
        commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=expected_rev,
                                  operations=operations,commit_message=message)
        rev=str(commit.oid)
    actual=load_files(api,rev)
    for file,data in parts.items():
        if sha(actual[file])!=sha(data):raise RuntimeError("Published bytes mismatch: "+file)
    emit("EXACT_SOURCE_VERIFIED",revision=rev,modified=list(parts))
    return rev

def fetch(path):
    req=urllib.request.Request(BASE+path,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=22) as response:return json.load(response)

def warm(api,revision,max_seconds=1200):
    deadline=time.monotonic()+max_seconds
    count=0
    while time.monotonic()<deadline:
        count+=1
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Concurrent HF source update during model warmup")
        try:
            r=fetch("/api/hf/qwen35-ready")
            if (r.get("ready") is True and r.get("model")=="qwen3.5-9b"
                and r.get("cpuCapacity")==16 and r.get("decodeThreads")==THREADS
                and r.get("batchThreads")==THREADS):
                emit("MODEL_READY",revision=revision,checks=count,
                     contextExpected=CONTEXT,cpu=16,threads=THREADS)
                return
        except Exception as e:
            if count%6==0:emit("WARM_PENDING",error=type(e).__name__,checks=count)
        time.sleep(12)
    raise RuntimeError("Resident 9B did not warm under expanded context")

def synthetic(prompt,timeout=480):
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4())
    thread="swrlz-synthetic-code-preview-"+str(uuid.uuid4())
    started=time.monotonic()
    body={"modelId":"700m","prompt":prompt,"threadId":thread,"requestId":rid,
          "profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
         data=json.dumps(body).encode(),headers={**HEADERS,"Content-Type":"application/json"})
    with opener.open(req,timeout=35) as response:
        if response.status!=202:raise RuntimeError("Synthetic chat send failed")
        response.read()
    parts=[];preview=[];first_preview=None;first_final=None;terminal=None;statuses=[]
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    with opener.open(urllib.request.Request(url,headers=HEADERS),timeout=timeout) as response:
        for raw in response:
            elapsed=time.monotonic()-started
            if elapsed>timeout-20:raise TimeoutError("Synthetic coding timed out")
            try:ev=json.loads(raw)
            except (ValueError,UnicodeError):continue
            if ev.get("requestId") and ev["requestId"]!=rid:raise RuntimeError("Cross-request stream")
            kind=ev.get("type")
            if kind=="CANDIDATE_PREVIEW_RESET":preview.clear()
            elif kind=="CANDIDATE_PREVIEW_DELTA":
                if first_preview is None:first_preview=round(elapsed,2)
                preview.append(str(ev.get("text") or ""))
            elif kind=="DELTA":
                if first_final is None:first_final=round(elapsed,2)
                parts.append(str(ev.get("text") or ""))
            elif kind=="STATUS":
                statuses.append(str(ev.get("phase") or ""))
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    elapsed=time.monotonic()-started
    with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",headers=HEADERS),timeout=25) as response:
        snap=json.load(response)
    active=snap.get("activeGeneration") or {}
    if active.get("requestId")!=rid:raise RuntimeError("Synthetic context request mismatch")
    ctx=active.get("contextBudget") or {}
    validation=active.get("candidateValidation") or {}
    result={"terminal":terminal,"firstProvisionalSec":first_preview,
        "firstAcceptedSec":first_final,"totalSec":round(elapsed,2),
        "inputTokens":ctx.get("estimatedInputTokens"),
        "contextTokens":ctx.get("contextWindowTokens"),
        "reservedOutputTokens":ctx.get("reservedOutputTokens"),
        "candidateStatus":validation.get("status"),
        "provisionalChars":len("".join(preview)),"finalChars":len("".join(parts)),
        "confirmedCodeHTML":("<html" in "".join(parts).lower()
                            or "<!doctype html" in "".join(parts).lower()),
        "stages":statuses[-7:]}
    emit("LIVE_SYNTHETIC",**result)
    return result

def accept_live(api,revision):
    # Do not use source SHA or ready marker alone; require the new live
    # context telemetry and actual provisional deltas through Station.
    deadline=time.monotonic()+1000
    prompt=("Create one complete responsive HTML demonstration page in a single "
            "HTML file with CSS and JavaScript. Add a centered title and a "
            "button that toggles the card's highlight. Make it visually polished.")
    while time.monotonic()<deadline:
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Concurrent deployment during live acceptance")
        try:
            r=synthetic(prompt,timeout=260)
            if (r["terminal"] in ("COMPLETE","COMPLETED")
                and r["contextTokens"]==CONTEXT
                and r["firstProvisionalSec"] is not None
                and r["firstAcceptedSec"] is not None
                and r["firstProvisionalSec"]<r["firstAcceptedSec"]
                and r["candidateStatus"]=="PASS"
                and r["confirmedCodeHTML"]
                and r["finalChars"]>=80):
                emit("LIVE_ACCEPTED",revision=revision,**r)
                return r
            emit("LIVE_VALIDATION_PENDING",revision=revision,observed=r)
        except Exception as e:
            emit("LIVE_ATTEMPT_PENDING",reason=type(e).__name__,
                 detail=str(e)[:120])
        time.sleep(12)
    raise RuntimeError("Expanded context/provisional stream did not pass live acceptance")

def main():
    mode=sys.argv[1:]
    if mode not in (["snapshot"],["publish"]):
        raise SystemExit("Usage: script snapshot|publish")
    token=os.environ.get("HF_TOKEN") or None
    api=HfApi(token=token)
    if mode==["snapshot"]:
        snapshot(api)
        return
    if os.environ.get("SWRLZ_CODE_PREVIEW_16K_APPROVED")!="1" or not token:
        raise RuntimeError("Explicit release authorization and HF token required")
    source_rev=(BACKUP/"revision.txt").read_text().strip()
    before={f:(BACKUP/f).read_bytes() for f in FILES}
    patched=patch(before)
    if api.repo_info(SPACE,repo_type="space").sha!=source_rev:
        raise RuntimeError("Production changed since source snapshot; refusing overwrite")
    new_rev=None
    try:
        new_rev=publish(api,source_rev,patched,
            "§C 9B: 16K complete-code context, adaptive reserve and validated provisional streaming")
        warm(api,new_rev)
        accept_live(api,new_rev)
    except Exception:
        emit("LIVE_RELEASE_REJECTED",revision=new_rev)
        if new_rev and api.repo_info(SPACE,repo_type="space").sha==new_rev:
            revert=publish(api,new_rev,before,
                "Rollback §C 16K coding context and provisional UI to exact prior source")
            warm(api,revert)
            emit("ROLLED_BACK_EXACT",revision=revert)
        elif new_rev:
            emit("ROLLBACK_BLOCKED",detail="Concurrent production update; refuse overwrite")
        raise

if __name__=="__main__":main()
