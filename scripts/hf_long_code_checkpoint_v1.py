#!/usr/bin/env python3
"""Guarded §C long-code resumable draft checkpoint release.

Resident model, 16K KV/context, 18 CPU inference threads, history ownership,
GitHub permissions and §E native editor permissions are unchanged. Only a
verified final candidate can become an accepted source artifact.
"""
from __future__ import annotations
import ast,hashlib,http.cookiejar,json,os,re,sys,tempfile,time,urllib.parse,urllib.request,uuid
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
CODE="qwen_coder_engine.py"
STATION="station.py"
FILES=(CODE,STATION)
BACKUP=Path("swrlz-long-code-checkpoint-backup")
MARK="swrlz-long-code-checkpoint-v1"
MAX_DRAFT_BYTES=240*1024
HEAD={"User-Agent":"Swyrlz-Resumable-Project-Code-Test","Cache-Control":"no-cache"}

def emit(name,**data):
    print("LONG_CODE_CHECKPOINT",json.dumps({"event":name,**data},ensure_ascii=False,sort_keys=True),flush=True)
def sha(data):return hashlib.sha256(data).hexdigest()
def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError("LIVE_SOURCE_DRIFT "+label+" count="+str(n))
    return s.replace(old,new,1)

TAIL_FN=r'''def _swrlz_resume_tail_messages(prefix):
    """Give the model an exact suffix, never ask it to recreate the prefix."""
    suffix=str(prefix)[-4800:]
    return [
        {"role":"system","content":(
            "Continue the existing code artifact immediately after its last byte. "
            "The caller has saved all earlier bytes and will append only the new "
            "suffix. Do NOT repeat the opening language fence, file names, prior "
            "lines, or explanations. Finish incomplete HTML/CSS/JavaScript "
            "structures and end the existing artifact cleanly. Do not invent "
            "execution results or change the task's project identity."
        )},
        {"role":"user","content":(
            "You are continuing a saved, unfinished source candidate. "
            "The exact last suffix is below. Write only the NEXT source bytes, "
            "without repeating the suffix or starting a different file unless "
            "the previous file is completely closed.\n"
            "SOURCE_OUTPUT_TAIL_BEGIN\n"+suffix+
            "\nSOURCE_OUTPUT_TAIL_END\nNEXT_BYTES_ONLY:"
        )}
    ]


def _swrlz_checkpoint_record(source,original_prompt,programming,manifest,segments):
    """Unverified draft only; explicitly not an accepted code artifact."""
    data=source.encode("utf-8")
    if not source or len(data)>240*1024:return None
    return {
        "schema":"swrlz-long-code-checkpoint-v1",
        "source":source,
        "sourceSha256":hashlib.sha256(data).hexdigest(),
        "originalPrompt":str(original_prompt or "")[:12000],
        "programmingIntent":programming if isinstance(programming,dict) else {},
        "sourceManifest":manifest if isinstance(manifest,dict) else {},
        "segmentsCompleted":int(segments or 0),
        "state":"UNVERIFIED_INCOMPLETE",
    }


def _swrlz_pause_code_events(checkpoint,segments,source_size):
    yield {"type":"CODE_OUTPUT_CHECKPOINT","checkpoint":checkpoint}
    yield {"type":"CANDIDATE_VALIDATION","validation":{
        "status":"INCOMPLETE","reasons":["output-segment-budget-paused"],
        "verificationState":"UNVERIFIED_SAVED_DRAFT","executionVerified":False,
    }}
    yield {"type":"STATUS","phase":"CODE_DRAFT_SAVED",
           "reason":"Unverified source saved; next user turn can resume exact code"}
    yield {"type":"DELTA","text":(
        "The code is not finished or accepted yet. I preserved "+
        str(source_size)+" bytes of the unverified draft across "+
        str(segments)+" generation segments in this conversation. "+
        "Send **Continue code** to resume from its ending rather than regenerate it. "+
        "The project will only be marked complete after structural validation."
    )}
    yield {"type":"COMPLETED","phase":"CODE_PAUSED"}


def _swrlz_resume_code_events(payload):
    checkpoint=payload["codeContinuation"]
    source=str(checkpoint.get("source") or "")
    if (checkpoint.get("schema")!="swrlz-long-code-checkpoint-v1"
        or not source or hashlib.sha256(source.encode("utf-8")).hexdigest()!=checkpoint.get("sourceSha256")
        or len(source.encode("utf-8"))>240*1024):
        raise ValueError("Source checkpoint invalid or stale")
    programming=checkpoint.get("programmingIntent") or {}
    original=str(checkpoint.get("originalPrompt") or payload.get("prompt") or "")
    history=[{"role":m.get("role"),"content":m.get("text","")}
             for m in payload.get("history",[]) if isinstance(m,dict)]
    yield {"type":"STATUS","phase":"RESUMING_CODE",
           "reason":"Continuing source checkpoint "+str(checkpoint["sourceSha256"])[:16]}
    if isinstance(programming,dict):
        yield {"type":"PROGRAMMING_INTENT","intent":programming}
    model=load()
    yield {"type":"RESOURCE","cpuCapacity":SHARED_CPU_CAPACITY,
           "decodeThreads":SHARED_DECODE_THREADS,"batchThreads":SHARED_BATCH_THREADS,
           "maxResponseTokens":4096}
    # Match the normal coding engine's model execution serialization.
    with _lock:
        draft,timing=yield from _swrlz_code_candidate_preview(
            model,[],4096,0.25,1,allow_continue=True,seed_text=source)
    completion=completion_validation(_candidate_structure_check(draft,programming,history),timing)
    accumulated=int(checkpoint.get("segmentsCompleted") or 0)+int(timing.get("continuationSegments") or 0)
    if timing.get("finishReason")=="length" or completion.get("status")!="PASS":
        next_checkpoint=_swrlz_checkpoint_record(
            draft,original,programming,checkpoint.get("sourceManifest"),accumulated)
        if next_checkpoint is not None:
            yield from _swrlz_pause_code_events(next_checkpoint,accumulated,
                  len(draft.encode("utf-8")))
            return
        yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":0}
        yield {"type":"CANDIDATE_VALIDATION","validation":completion}
        yield {"type":"DELTA","text":"The unfinished draft exceeded this session's safe checkpoint storage limit. It was not accepted. Split this project into smaller complete files for versioned editing."}
        yield {"type":"COMPLETED","phase":"CODE_SAFE_LIMIT"}
        return
    yield {"type":"CODE_OUTPUT_FINISHED","sourceSha256":checkpoint["sourceSha256"]}
    yield {"type":"CANDIDATE_VALIDATION","validation":completion}
    yield {"type":"DELTA","text":draft}
    yield {"type":"COMPLETED","phase":"COMPLETE","resumedSource":True,
           "totalSegments":accumulated}

'''

def patch_engine(before):
    source=before.decode("utf-8")
    if MARK in source:raise RuntimeError("Already integrated")
    tree=ast.parse(source)
    fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef)
             and n.name=="_swrlz_code_candidate_preview")
    old=ast.get_source_segment(source,fun)
    new=old
    new=once(new,"allow_continue=False):","allow_continue=False,seed_text=''):","generator seed")
    new=once(new,"    parts=[]","    parts=[seed_text] if seed_text else []","seeded prefix")
    new=once(new,"max_segments=4 if allow_continue else 1",
             "max_segments=8 if allow_continue else 1","eight bounded segments")
    new=once(new,"    next_messages=messages",
             "    next_messages=_swrlz_resume_tail_messages(seed_text) if seed_text else messages",
             "source-resume prompt")
    new=once(new,"    token_allowance=int(max_tokens)",
             "    token_allowance=min(4096,int(max_tokens)) if seed_text else int(max_tokens)",
             "segment output budget")
    new=once(new,"    for segment in range(1,max_segments+1):",
             "    for segment in range(1,max_segments+1):\n"
             "        # Check at segment boundaries; never interrupt a native decode mid-token.\n"
             "        if segment>1 and time.perf_counter()-started>540:break",
             "nine-minute turn budget")
    new=once(new,"            if segment>1:","            if segment>1 or seed_text:",
             "continuation prefix overlap")
    source=once(source,old,TAIL_FN+new,"generation continuation helper")
    prompt_head='''    prompt=str(payload.get("prompt") or "").strip()
    if not prompt: raise ValueError("Empty prompt")'''
    prompt_new=prompt_head+'''
    # swrlz-long-code-checkpoint-v1: account-owned, request-scoped resume.
    if isinstance(payload.get("codeContinuation"),dict):
        yield from _swrlz_resume_code_events(payload)
        return'''
    source=once(source,prompt_head,prompt_new,"resume router")
    eligibility='''    auto_resume_existing_source=bool(
        code_delivery and not programming.get("newProject") and (
            preserve_existing_source(programming)
            or bool(programming.get("artifactContinuation"))
            or bool(programming.get("artifactEditSource"))
            or any(
                item.get("role")=="assistant"
                and source_fence_present(str(item.get("content") or item.get("text") or ""))
                for item in list(history or [])[-8:]
            )
        )
    )'''
    more='''    # Any actual code deliverable, new or existing, may exceed one
    # model decode. Review/explanation and ordinary chat retain fast paths.
    auto_resume_existing_source=bool(code_delivery)'''
    source=once(source,eligibility,more,"code-stage eligibility")
    line='''            if candidate_check.get("status")=="REJECT":
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":2}'''
    replacement='''            # On length exhaustion, retain the entire partial candidate.
            # Do not launch two more FULL from-scratch retries that consume
            # minutes only to reach the same cap again.
            if (timing.get("finishReason")=="length" and auto_resume_existing_source):
                checkpoint=_swrlz_checkpoint_record(
                    candidate_text,prompt,programming,
                    payload.get("projectImportManifest"),timing.get("continuationSegments"))
                if checkpoint is not None:
                    yield from _swrlz_pause_code_events(
                        checkpoint,timing.get("continuationSegments"),
                        len(candidate_text.encode("utf-8")))
                    return
            if candidate_check.get("status")=="REJECT":
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":2}'''
    source=once(source,line,replacement,"checkpoint before wasteful retries")
    ast.parse(source,filename=CODE)
    return source.encode("utf-8")

STATION_PERSIST_BEFORE='''                elif kind=="CANDIDATE_PREVIEW_RESET":
                    g["previewText"]=""'''
STATION_PERSIST_AFTER='''                elif kind=="CODE_OUTPUT_CHECKPOINT":
                    checkpoint=event.get("checkpoint") if isinstance(event.get("checkpoint"),dict) else {}
                    draft=str(checkpoint.get("source") or "")
                    if (checkpoint.get("schema")!="swrlz-long-code-checkpoint-v1"
                            or not draft or len(draft.encode("utf-8"))>240*1024
                            or hashlib.sha256(draft.encode("utf-8")).hexdigest()!=checkpoint.get("sourceSha256")):
                        raise RuntimeError("Refusing unverified or oversized source checkpoint")
                    target=next((t for t in s["threads"] if t.get("id")==payload["threadId"]),None)
                    if target is None:raise RuntimeError("Checkpoint source thread missing")
                    # Explicitly no codeArtifact entry: not validated, not exportable.
                    target["pendingCodeGeneration"]=copy.deepcopy(checkpoint)
                    g["codeDraftCheckpoint"]={
                        "sourceSha256":checkpoint["sourceSha256"],
                        "bytes":len(draft.encode("utf-8")),
                        "segments":int(checkpoint.get("segmentsCompleted") or 0),
                        "verificationState":"UNVERIFIED_INCOMPLETE"}
                    _commit_revision(s)
                    g["status"].append({"seq":g["lastSeq"],"phase":"CODE_DRAFT_CHECKPOINTED",
                        "reason":"Unverified source safely saved; continue code to resume"})
                elif kind=="CODE_OUTPUT_FINISHED":
                    target=next((t for t in s["threads"] if t.get("id")==payload["threadId"]),None)
                    pending=(target or {}).get("pendingCodeGeneration") or {}
                    # Only this request's previously bound source can close it.
                    if (payload.get("codeContinuation") and pending.get("sourceSha256")==
                            payload["codeContinuation"].get("sourceSha256")):
                        target.pop("pendingCodeGeneration",None)
                        g["status"].append({"seq":g["lastSeq"],"phase":"CODE_DRAFT_COMPLETED",
                            "reason":"Accepted source to replace verified draft checkpoint"})
                elif kind=="CANDIDATE_PREVIEW_RESET":
                    g["previewText"]=""'''
SEND_HEAD='''        history=_history_projection(t, current_prompt=prompt)'''
SEND_NEW='''        # Only an explicit same-thread continuation command may restore
        # a previous unverified coding draft; no new task is overwritten.
        pending=t.get("pendingCodeGeneration") if isinstance(t.get("pendingCodeGeneration"),dict) else None
        resume_code=None
        if pending and re.fullmatch(
            r"(?is)\\s*(?:(?:please|now)\\s+)?(?:continue(?:\\s+(?:the\\s+)?(?:code|generation|project|file|output))?|resume(?:\\s+(?:the\\s+)?(?:code|generation|project|file|output))?|keep\\s+generating(?:\\s+code)?)\\s*[.!]?\\s*",
            str(prompt or "")):
            source=str(pending.get("source") or "")
            if (pending.get("schema")!="swrlz-long-code-checkpoint-v1"
                or not source or len(source.encode("utf-8"))>240*1024
                or hashlib.sha256(source.encode("utf-8")).hexdigest()!=pending.get("sourceSha256")):
                raise HTTPException(409,"Saved unfinished code checkpoint is invalid; it was not used")
            origin=pending.get("sourceManifest") or {}
            if origin.get("artifactId"):
                actual=_find_artifact(t,str(origin["artifactId"]))
                if (not actual or actual.get("id")!=t.get("activeImportedArtifactId")
                    or int(actual.get("currentRevision") or 0)!=int(origin.get("currentRevision") or -1)):
                    raise HTTPException(409,"Project source changed since unfinished code; inspect the latest revision")
            resume_code=copy.deepcopy(pending)
        history=_history_projection(t, current_prompt=prompt)'''
SEND_PAYLOAD='''    payload={"requestId":rid,"threadId":tid,"prompt":_inference_prompt_after_vision(prompt),"history":history,"pinnedContext":pinned_context,"profileId":profile_id,"profile":profile,"userProfile":user_profile,"temporalContext":temporal_context,"clientLocation":client_location,"priorProgrammingState":copy.deepcopy(t.get("programmingState") or {})}'''
SEND_PAYLOAD_NEW=SEND_PAYLOAD+'''
    if resume_code is not None:
        payload["codeContinuation"]=resume_code'''
ROUTE_BEFORE='''        if forge_context is not None:
            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate,forge_context=forge_context)
        elif payload.get("verifiedWorkAnswer"):'''
ROUTE_AFTER='''        if forge_context is not None:
            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate,forge_context=forge_context)
        elif isinstance(payload.get("codeContinuation"),dict):
            # A persisted source checkpoint stays in the coding model and
            # never grants §E or GitHub write authority.
            event_source=_coder_generate(payload)
        elif payload.get("verifiedWorkAnswer"):'''

def patch_station(before):
    s=before.decode("utf-8")
    if MARK in s:raise RuntimeError("Already integrated")
    for a,b,label in [
        (STATION_PERSIST_BEFORE,STATION_PERSIST_AFTER,"checkpoint state"),
        (SEND_HEAD,SEND_NEW,"same-thread command"),
        (SEND_PAYLOAD,SEND_PAYLOAD_NEW,"verified checkpoint payload"),
        (ROUTE_BEFORE,ROUTE_AFTER,"resume routing"),
    ]:
        s=once(s,a,b,label)
    ast.parse(s,filename=STATION)
    return s.encode("utf-8")

def check_fake_generator(engine_source):
    tree=ast.parse(engine_source)
    funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    names=("_swrlz_trim_code_resume","_swrlz_resume_tail_messages",
           "_swrlz_code_candidate_preview","_swrlz_checkpoint_record",
           "_swrlz_pause_code_events")
    subset=[funcs[x] for x in names]
    class Fake:
        def __init__(self,items):self.items=items;self.calls=[]
        def create_chat_completion(self,**kwargs):
            self.calls.append(kwargs)
            i=len(self.calls)-1
            text,reason=self.items[i]
            yield {"choices":[{"delta":{"content":text},"finish_reason":None}]}
            yield {"choices":[{"delta":{},"finish_reason":reason}],
                   "usage":{"prompt_tokens":12,"completion_tokens":34,"total_tokens":46}}
    def observe(ob,chunk):
        for choice in chunk.get("choices",[]):
            if choice.get("finish_reason") is not None:
                ob["finishReason"]=choice["finish_reason"]
        if chunk.get("usage"):ob["usage"]=chunk["usage"]
    ns={"time":time,"hashlib":hashlib,
        "observe_completion_chunk":observe,
        "_token_count":lambda m,items:100,
        "CONTEXT_TOKENS":16384,"CONTEXT_SAFETY_TOKENS":128,
        "MIN_OUTPUT_TOKENS":384}
    exec(compile(ast.Module(body=subset,type_ignores=[]),"<resumable-code-test>","exec"),ns)
    def drain(g):
        events=[]
        while True:
            try:events.append(next(g))
            except StopIteration as stop:return events,stop.value
    head=""+chr(96)*3+"html\n<!doctype html><html><body><h1>Demo"
    foot="</h1></body></html>\n"+chr(96)*3
    g=ns["_swrlz_code_candidate_preview"](Fake([(head,"length"),(foot,"stop")]),
        [{"role":"user","content":"Create HTML"}],4096,0.3,1,allow_continue=True)
    events,(code,receipt)=drain(g)
    assert code==head+foot
    assert receipt["finishReason"]=="stop" and receipt["continuationSegments"]==2
    assert sum(e["type"]=="CANDIDATE_PREVIEW_DELTA" for e in events)==2
    incomplete=Fake([(head,"length")]*8)
    events,(code,receipt)=drain(ns["_swrlz_code_candidate_preview"](
        incomplete,[],4096,0.3,1,allow_continue=True))
    assert receipt["finishReason"]=="length"
    assert receipt["continuationSegments"]==8
    assert len(incomplete.calls)==8
    record=ns["_swrlz_checkpoint_record"](code,"Improve original",{"codingTask":True},{},8)
    assert record["state"]=="UNVERIFIED_INCOMPLETE"
    seeded=Fake([(foot,"stop")])
    events,(resumed,receipt)=drain(ns["_swrlz_code_candidate_preview"](
        seeded,[],4096,0.3,1,allow_continue=True,seed_text=head))
    assert resumed==head+foot and receipt["finishReason"]=="stop"
    assert len(seeded.calls)==1
    assert "SOURCE_OUTPUT_TAIL_BEGIN" in seeded.calls[0]["messages"][1]["content"]
    checkpoint_events=list(ns["_swrlz_pause_code_events"](record,8,len(code)))
    assert checkpoint_events[0]["type"]=="CODE_OUTPUT_CHECKPOINT"
    assert any(e.get("type")=="CANDIDATE_VALIDATION" and
               e.get("validation",{}).get("status")=="INCOMPLETE" for e in checkpoint_events)
    assert len(ns["_swrlz_resume_tail_messages"](head))==2
    emit("FAKE_STREAM_TESTS_PASS",eightSegments=True,seedResume=True,
         nativeStopRequired=True,partialNeverAccepted=True)

def test_source(old,updated):
    ast.parse(updated[CODE].decode("utf-8"),filename=CODE)
    ast.parse(updated[STATION].decode("utf-8"),filename=STATION)
    src=updated[CODE].decode()
    st=updated[STATION].decode()
    check_fake_generator(src)
    assert 'CODE_OUTPUT_CHECKPOINT' in src and 'codeContinuation' in src
    assert 'CODE_OUTPUT_FINISHED' in src and 'CODE_PAUSED' in src
    assert "SOURCE_OUTPUT_TAIL_BEGIN" in src
    assert "projectFileEvidence" in src
    assert "CONTEXT_TOKENS=16384" in src
    assert "_candidate_structure_check(" in src and "completion_validation(" in src
    assert "SOURCE_HASH_CONFLICT" in st
    assert 'pendingCodeGeneration' in st
    assert "_commit_revision(s)" in st
    assert "codeArtifacts" in st
    assert "projectFiles" in st
    assert "codeContinuation" in st
    assert "forge_context is not None" in st
    for name in FILES:
        assert old[name]!=updated[name]
    emit("AST_AND_INVARIANTS_PASS",files=list(FILES),sameModel=True,
         sameKvWindow=True,githubWriteUnchanged=True,forgeAuthorityUnchanged=True)

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before={name:Path(hf_hub_download(SPACE,name,repo_type="space",
           revision=rev,token=api.token)).read_bytes() for name in FILES}
    after={CODE:patch_engine(before[CODE]),STATION:patch_station(before[STATION])}
    test_source(before,after)
    BACKUP.mkdir(parents=True,exist_ok=True)
    for name,data in before.items():(BACKUP/name).write_bytes(data)
    (BACKUP/"revision.txt").write_text(rev)
    (BACKUP/"manifest.json").write_text(json.dumps({
         "revision":rev,"files":list(FILES),
         "before":{n:sha(d) for n,d in before.items()},
         "after":{n:sha(d) for n,d in after.items()},
         "modelChanged":False,"cpuThreadsChanged":False,
         "contextWindowChanged":False},indent=2))
    emit("SOURCE_SNAPSHOTTED",revision=rev)
    return rev,before,after

def commit(api,rev,updates,reason):
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Space updated concurrently; refusing overwrite")
    with tempfile.TemporaryDirectory(prefix="swrlz-code-checkpoint-") as folder:
        ops=[]
        for name,data in updates.items():
            path=Path(folder)/name;path.write_bytes(data)
            ops.append(CommitOperationAdd(path_in_repo=name,path_or_fileobj=str(path)))
        result=api.create_commit(repo_id=SPACE,repo_type="space",
           parent_commit=rev,operations=ops,commit_message=reason)
    new=str(result.oid)
    for name,data in updates.items():
        actual=Path(hf_hub_download(SPACE,name,repo_type="space",
                       revision=new,token=api.token)).read_bytes()
        if sha(actual)!=sha(data):raise RuntimeError("Live source hash mismatch "+name)
    emit("SOURCE_VERIFIED",revision=new)
    return new

def ready():
    with urllib.request.urlopen(urllib.request.Request(BASE+"/api/hf/qwen35-ready",
        headers=HEAD),timeout=22) as r:return json.load(r)

def warm(api,rev,timeout=930):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if api.repo_info(SPACE,repo_type="space").sha!=rev:
            raise RuntimeError("Concurrent Space change during warmup")
        try:
            x=ready()
            if (x.get("ready") is True and x.get("model")=="qwen3.5-9b"
                and (x.get("decodeThreads"),x.get("batchThreads"),
                     x.get("cpuCapacity"))==(18,18,16)):
                emit("SAME_QWEN_9B_READY",revision=rev)
                return
        except Exception:pass
        time.sleep(12)
    raise TimeoutError("Resident 9B model not ready after source revision")

def live_smoke():
    opener=urllib.request.build_opener(
      urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    request_id=str(uuid.uuid4())
    payload={"modelId":"700m","requestId":request_id,
             "threadId":"swrlz-checkpoint-smoke-"+uuid.uuid4().hex,
             "prompt":"Write a small runnable HTML page with an interactive button. Keep it under 70 lines.",
             "profileId":"LALM","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
          data=json.dumps(payload).encode(),
          headers={**HEAD,"Content-Type":"application/json"})
    with opener.open(req,timeout=35) as r:
        if r.status!=202:raise RuntimeError("Production Station rejected synthetic code")
        r.read()
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":request_id})
    code=[];draft=0;terminal=None;deadline=time.monotonic()+420;validation=None
    with opener.open(urllib.request.Request(url,headers=HEAD),timeout=420) as r:
        for raw in r:
            if time.monotonic()>deadline:raise TimeoutError("Synthetic code exceeded test budget")
            try:ev=json.loads(raw)
            except (ValueError,UnicodeError):continue
            if ev.get("requestId") and ev["requestId"]!=request_id:
                raise RuntimeError("Cross-request streaming event")
            kind=ev.get("type")
            if kind=="DELTA":code.append(str(ev.get("text") or ""))
            elif kind=="CANDIDATE_PREVIEW_DELTA":draft+=len(str(ev.get("text") or ""))
            elif kind=="CANDIDATE_VALIDATION":validation=ev.get("validation")
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    text="".join(code)
    emit("LIVE_CODING_SMOKE",terminal=terminal,sourceChars=len(text),
         previewChars=draft,validationStatus=(validation or {}).get("status"),
         html=("<html" in text.lower() or "<!doctype html" in text.lower()))
    if terminal not in ("COMPLETE","COMPLETED") or "<html" not in text.lower():
        raise RuntimeError("Live ordinary code generation failed after patch")
    if (validation or {}).get("status")!="PASS":
        raise RuntimeError("Code candidate not validated in smoke test")

def main():
    argv=sys.argv[1:]
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if argv==["preflight"]:
        snapshot(api);return
    if argv!=["publish"]:raise SystemExit("Usage: preflight|publish")
    if os.environ.get("SWRLZ_LONG_CODE_APPROVED")!="1" or not api.token:
        raise RuntimeError("Scoped release authorization required")
    rev=(BACKUP/"revision.txt").read_text().strip()
    original={name:(BACKUP/name).read_bytes() for name in FILES}
    newbytes={CODE:patch_engine(original[CODE]),STATION:patch_station(original[STATION])}
    test_source(original,newbytes)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Source changed since snapshot")
    deployed=None
    try:
        deployed=commit(api,rev,newbytes,
              "§C: resumable long-code checkpoints instead of repeated output-limit retries")
        warm(api,deployed)
        live_smoke()
        emit("LIVE_RELEASE_KEPT",revision=deployed,sourcePreserved=True)
    except Exception:
        emit("RELEASE_REJECTED",revision=deployed)
        if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
            restored=commit(api,deployed,original,
                 "Rollback §C resumable long-code draft to exact previous source")
            warm(api,restored)
            emit("EXACT_ROLLBACK_COMPLETE",revision=restored)
        elif deployed:emit("ROLLBACK_BLOCKED_CONCURRENT_REVISION")
        raise

if __name__=="__main__":main()
