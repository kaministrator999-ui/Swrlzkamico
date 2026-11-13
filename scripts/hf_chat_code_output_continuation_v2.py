#!/usr/bin/env python3
"""§C guarded existing-project code continuation on output-token limit.

Patch exact, current source of kamiloki/Swyrlz with immutable revision and
byte-for-byte rollback. The base model, 16K KV window, 18 threads, profiles,
source attribution, user projects and §E are unchanged.
"""
from __future__ import annotations
import ast,hashlib,http.cookiejar,json,os,re,sys,tempfile,time,urllib.parse,urllib.request,uuid
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
FILE="qwen_coder_engine.py"
BASE="https://kamiloki-swyrlz.hf.space"
TAG="swrlz-code-output-continuation-v2"
BACKUP=Path("swrlz-code-continuation-backup")
HEADERS={"User-Agent":"Swyrlz-SourceSafe-Continuation-Test","Cache-Control":"no-cache"}

def emit(kind,**details):
    print("CODE_CONTINUATION",json.dumps({"event":kind,**details},ensure_ascii=False,sort_keys=True),flush=True)

def sha(data):return hashlib.sha256(data).hexdigest()

def replace_once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError("LIVE_ANCHOR_DRIFT %s occurrences=%d"%(label,n))
    return s.replace(old,new,1)

HELPER=r'''def _swrlz_trim_code_resume(prior,following):
    """Remove only exact prefix overlap; do not alter earlier candidate bytes."""
    if not following:return ""
    fence=chr(96)*3
    if prior.count(fence)%2 and following.startswith(fence):
        line=following.split("\n",1)[0].strip().lower()
        if line in (fence+"html",fence+"css",fence+"js",
                    fence+"javascript",fence+"python",fence+"typescript"):
            if "\n" in following:following=following.split("\n",1)[1]
    common=min(len(prior),len(following),2048)
    for count in range(common,7,-1):
        if prior.endswith(following[:count]):return following[count:]
    return following


def _swrlz_code_candidate_preview(model,messages,max_tokens,temperature,attempt,
                                  allow_continue=False):
    """Stream only unverified candidate bytes, with bounded length recovery.

    For existing-project code only, a length-terminated segment can resume
    from its retained tail. The retained candidate is never a saved answer:
    existing deterministic validation still owns final acceptance.
    """
    started=time.perf_counter()
    first_token_at=None
    parts=[]
    delta_chunks=0
    max_segments=4 if allow_continue else 1
    segment_count=0
    observed=[]
    next_messages=messages
    token_allowance=int(max_tokens)
    for segment in range(1,max_segments+1):
        segment_count=segment
        part_observation={"finishReason":None,"requestedMaxTokens":int(token_allowance)}
        pending=""
        for chunk in model.create_chat_completion(
            messages=next_messages,max_tokens=token_allowance,
            temperature=temperature,stream=True
        ):
            observe_completion_chunk(part_observation,chunk)
            choices=chunk.get("choices") or []
            delta=(choices[0].get("delta") or {}).get("content") if choices else None
            if not delta:continue
            now=time.perf_counter()
            if first_token_at is None:first_token_at=now
            delta_chunks+=1
            if segment>1:
                # Briefly buffer the next segment's prefix to recognize
                # a repeated tail or an accidental second opening fence.
                pending+=str(delta)
                if len(pending)<256:continue
                addition=_swrlz_trim_code_resume("".join(parts),pending)
                pending=""
            else:
                addition=str(delta)
            if addition:
                parts.append(addition)
                yield {"type":"CANDIDATE_PREVIEW_DELTA","text":addition,"attempt":attempt}
        if pending:
            addition=_swrlz_trim_code_resume("".join(parts),pending)
            if addition:
                parts.append(addition)
                yield {"type":"CANDIDATE_PREVIEW_DELTA","text":addition,"attempt":attempt}
        observed.append(part_observation)
        if part_observation.get("finishReason")!="length":break
        if segment>=max_segments or not parts:break
        # Existing source and candidate prefix are already held in memory.
        # The next LLM request needs only its bounded suffix, NOT a huge
        # recreation of the original user/project prompt.
        retained="".join(parts)
        suffix=retained[-4800:]
        continuation_system=(
            "You are finishing an existing code artifact, not creating a new one. "
            "All earlier code bytes are retained by the caller. "
            "Write ONLY the missing bytes immediately following the very last "
            "character shown in the prior output. Do NOT repeat earlier lines, "
            "headers, opening fences, file names, or explanations. "
            "Preserve the existing file syntax and complete unclosed structures. "
            "Do not make new claims about execution or successful tests."
        )
        continuation_user=(
            "Continue the exact existing source candidate from its final "
            "character. The text below is its final suffix, not a new task. "
            "Only output the NEXT source bytes, with no prefix or commentary.\n"
            "SOURCE_OUTPUT_TAIL_BEGIN\n"+suffix+
            "\nSOURCE_OUTPUT_TAIL_END\nNEXT_BYTES_ONLY:"
        )
        next_messages=[
            {"role":"system","content":continuation_system},
            {"role":"user","content":continuation_user},
        ]
        # Bound each continuation independently inside the same resident 16K
        # context. This permits long total files without increasing KV RAM.
        extension_room=CONTEXT_TOKENS-_token_count(model,next_messages)-CONTEXT_SAFETY_TOKENS
        token_allowance=min(4096,int(max_tokens),extension_room)
        if token_allowance<MIN_OUTPUT_TOKENS:break
        yield {"type":"STATUS","phase":"CODE_CONTINUING",
               "reason":"Extending unfinished code candidate (segment %d/%d)"%
                        (segment+1,max_segments)}
    ended=time.perf_counter()
    termination=dict(observed[-1]) if observed else {"finishReason":None}
    # Do not fake "stop": the existing completion_validation rejects any
    # candidate whose final provider reason is still "length".
    usage_sum={}
    for observation in observed:
        for key,value in (observation.get("usage") or {}).items():
            if (key in ("prompt_tokens","completion_tokens","total_tokens")
                and isinstance(value,int) and value>=0):
                usage_sum[key]=usage_sum.get(key,0)+value
    if usage_sum:termination["usage"]=usage_sum
    return "".join(parts), {
        "durationMs":round((ended-started)*1000,3),
        "firstTokenLatencyMs":round((first_token_at-started)*1000,3)
                              if first_token_at is not None else None,
        "deltaChunks":delta_chunks,
        "continuationSegments":segment_count,
        "automaticContinuation":segment_count>1,
        **termination,
    }

'''

FLAG_ANCHOR='''    guarded_turn=not source_change_mode and bool(repair_turn or strict_language or code_delivery)'''
FLAG_NEW='''    guarded_turn=not source_change_mode and bool(repair_turn or strict_language or code_delivery)
    # swrlz-code-output-continuation-v2: only grounded existing-project
    # generation may resume after hitting the output limit. New isolated
    # artifacts keep the established regenerate-and-validate behavior.
    auto_resume_existing_source=bool(
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

def patch(source):
    if TAG in source:
        raise RuntimeError("Already running this continuation variant")
    tree=ast.parse(source)
    funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef)
           and n.name=="_swrlz_code_candidate_preview"]
    if len(funcs)!=1:raise RuntimeError("No unique existing preview helper")
    old=ast.get_source_segment(source,funcs[0])
    if "CANDIDATE_PREVIEW_DELTA" not in old:
        raise RuntimeError("Wrong model generation engine")
    source=replace_once(source,old,HELPER.strip()+"\n\n","live model preview function")
    source=replace_once(source,FLAG_ANCHOR,FLAG_NEW,"existing project gating")
    callsites=[
        ("model,messages,response_tokens,temperature,1)",
         "model,messages,response_tokens,temperature,1,allow_continue=auto_resume_existing_source)"),
        ("model,retry_messages,retry_tokens,min(0.45,temperature+0.10),2)",
         "model,retry_messages,retry_tokens,min(0.45,temperature+0.10),2,allow_continue=auto_resume_existing_source)"),
        ("model,final_messages,final_tokens,min(0.50,temperature+0.15),3)",
         "model,final_messages,final_tokens,min(0.50,temperature+0.15),3,allow_continue=auto_resume_existing_source)")
    ]
    for a,b in callsites:source=replace_once(source,a,b,"length continuation invocation")
    ast.parse(source,filename=FILE)
    return source

def tests(original,candidate):
    a=ast.parse(candidate)
    names=[n.name for n in a.body if isinstance(n,ast.FunctionDef)]
    assert names.count("_swrlz_code_candidate_preview")==1
    assert names.count("_swrlz_trim_code_resume")==1
    assert "CONTEXT_TOKENS=16384" in candidate
    assert "WEB_PAGE_OUTPUT_TOKENS=8192" in candidate
    assert "PROJECT_OUTPUT_TOKENS=8192" in candidate
    for mandatory in ("enforce_strategy_change(","_candidate_structure_check(",
                      "candidate_retry_messages(","completion_validation(",
                      'yield {"type":"CANDIDATE_VALIDATION"',
                      'yield {"type":"DELTA","text":candidate_text}',
                      'yield {"type":"CANDIDATE_PREVIEW_RESET"'):
        assert mandatory in candidate,mandatory
    assert candidate.count("BUILTIN_ASSISTANT_PROFILE=")==original.count("BUILTIN_ASSISTANT_PROFILE=")
    assert candidate.count("def generate_events(payload):")==1
    # Test the precise helper in isolation with deterministic provider
    # termination reasons, native deltas, and no model download.
    body=[n for n in a.body if isinstance(n,ast.FunctionDef)
          and n.name in ("_swrlz_trim_code_resume","_swrlz_code_candidate_preview")]
    class Fake:
        def __init__(self,outputs):self.outputs=list(outputs);self.calls=[]
        def create_chat_completion(self,**kw):
            self.calls.append(kw)
            value,reason=self.outputs[len(self.calls)-1]
            yield {"choices":[{"delta":{"content":value},"finish_reason":None}]}
            yield {"choices":[{"delta":{},"finish_reason":reason}],
                   "usage":{"prompt_tokens":12,"completion_tokens":34,"total_tokens":46}}
    def observed(info,chunk):
        for c in chunk.get("choices") or []:
            if c.get("finish_reason") is not None:
                info["finishReason"]=c["finish_reason"]
        usage=chunk.get("usage")
        if usage:info["usage"]={k:v for k,v in usage.items() if isinstance(v,int)}
    scope={
        "time":time,"observe_completion_chunk":observed,"CONTEXT_TOKENS":16384,
        "CONTEXT_SAFETY_TOKENS":128,"MIN_OUTPUT_TOKENS":384,
        "_token_count":lambda model,msgs:sum(len(m["content"])//4+6 for m in msgs),
    }
    exec(compile(ast.Module(body=body,type_ignores=[]),"<source-continuation>","exec"),scope)
    fn=scope["_swrlz_code_candidate_preview"]
    fence=chr(96)*3
    incomplete=fence+"html\n<!DOCTYPE html><html><body><main><h1>Hello</h1>"
    ending="</main></body></html>\n"+fence
    no_resume=Fake([(incomplete,"length")])
    g=fn(no_resume,[{"role":"user","content":"Create a page"}],4096,.3,1,
         allow_continue=False)
    events,return_value=drain(g)
    assert return_value[1]["finishReason"]=="length"
    assert len(no_resume.calls)==1
    assert not any(e.get("type")=="STATUS" for e in events)
    resume=Fake([(incomplete,"length"),(ending,"stop")])
    g=fn(resume,[{"role":"user","content":"Improve this HTML"}],4096,.3,1,
         allow_continue=True)
    events,return_value=drain(g)
    source,receipt=return_value
    assert source==incomplete+ending,(source[:100],source[-100:])
    assert receipt["finishReason"]=="stop"
    assert receipt["continuationSegments"]==2
    assert receipt["automaticContinuation"]
    assert receipt["usage"]["completion_tokens"]==68
    assert len(resume.calls)==2
    assert len([e for e in events if e.get("type")=="STATUS"])==1
    assert "".join(e.get("text","") for e in events if e["type"]=="CANDIDATE_PREVIEW_DELTA")==source
    assert source.endswith("</html>\n"+fence)
    assert len(resume.calls[1]["messages"])==2
    assert resume.calls[1]["max_tokens"]<=4096
    repeated=scope["_swrlz_trim_code_resume"]("abcde123456789","123456789 more")
    assert repeated==" more"
    capped=Fake([(incomplete,"length")]*4)
    events,return_value=drain(fn(capped,[],4096,.3,1,allow_continue=True))
    assert return_value[1]["finishReason"]=="length"
    assert return_value[1]["continuationSegments"]==4
    assert len(capped.calls)==4
    assert len(return_value[0])<=len(incomplete)*4
    # Structural contract: continuation is allowed only when the original
    # output is ongoing project work, NOT all other chat and coding requests.
    assert "not programming.get("+'"newProject"'+")" in candidate
    assert "preserve_existing_source(programming)" in candidate
    assert "source_fence_present(" in candidate
    emit("FAKE_STREAM_REGRESSION_PASS",cases=4,
         partialOnlyStillRejected=True,finalStopRequired=True,
         sourceProfileUnchanged=True,continuationSegmentsMax=4,
         maxAdditionalPerSegment=4096)

def drain(g):
    result=[]
    while True:
        try:result.append(next(g))
        except StopIteration as ex:return result,ex.value

def snapshot(api):
    revision=api.repo_info(SPACE,repo_type="space").sha
    path=hf_hub_download(SPACE,FILE,repo_type="space",revision=revision,token=api.token)
    before=Path(path).read_bytes()
    after=patch(before.decode()).encode()
    tests(before.decode(),after.decode())
    BACKUP.mkdir(parents=True,exist_ok=True)
    (BACKUP/FILE).write_bytes(before)
    (BACKUP/"revision.txt").write_text(revision)
    (BACKUP/"manifest.json").write_text(json.dumps({
        "source":revision,"originalSha256":sha(before),"candidateSha256":sha(after),
        "files":[FILE],"modelChanged":False,"threadingChanged":False,
        "contextChanged":False,"savedChatHistoryChanged":False},indent=2))
    emit("SOURCE_VALIDATED",revision=revision,originalSha=sha(before),
         candidateSha=sha(after),changedFiles=[FILE])
    return revision,before,after

def commit(api,revision,data,message):
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Concurrent source update, refusing overwrite")
    with tempfile.NamedTemporaryFile(suffix=".py") as f:
        f.write(data);f.flush()
        result=api.create_commit(repo_id=SPACE,repo_type="space",
             parent_commit=revision,
             operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=f.name)],
             commit_message=message)
    new_rev=str(result.oid)
    got=Path(hf_hub_download(SPACE,FILE,repo_type="space",
                   revision=new_rev,token=api.token)).read_bytes()
    if sha(got)!=sha(data):
        raise RuntimeError("Published source failed hash verification")
    emit("SOURCE_SHA_VERIFIED",revision=new_rev)
    return new_rev

def status():
    req=urllib.request.Request(BASE+"/api/hf/qwen35-ready",headers=HEADERS)
    with urllib.request.urlopen(req,timeout=22) as response:
        return json.load(response)

def warm(api,revision,max_secs=1100):
    until=time.monotonic()+max_secs
    while time.monotonic()<until:
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Concurrent Space version during warmup")
        try:
            r=status()
            if r.get("ready")==True and r.get("model")=="qwen3.5-9b" and (
               r.get("decodeThreads"),r.get("batchThreads"),r.get("cpuCapacity"))==(18,18,16):
                emit("RESIDENT_9B_READY",revision=revision,threads=18,quota=16)
                return
        except Exception:pass
        time.sleep(10)
    raise TimeoutError("Guarded coding engine did not become ready")

def synthetic(prompt,max_secs=400):
    opener=urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4());tid="swrlz-length-continuation-"+str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,"threadId":tid,"requestId":rid,
          "profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
        headers={**HEADERS,"Content-Type":"application/json"},
        data=json.dumps(body).encode())
    start=time.monotonic()
    with opener.open(req,timeout=35) as res:
        if res.status!=202:raise RuntimeError("Synthetic code request not accepted")
        res.read()
    events=[];text_parts=[];draft_parts=[];first_draft=None;first_text=None;terminal=None
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    with opener.open(urllib.request.Request(url,headers=HEADERS),timeout=max_secs) as res:
        for raw in res:
            elapsed=time.monotonic()-start
            if elapsed>max_secs-20:raise TimeoutError("Synthetic code request exceeded max")
            try:event=json.loads(raw)
            except (ValueError,UnicodeError):continue
            kind=event.get("type")
            if kind=="STATUS":events.append(str(event.get("phase") or ""))
            elif kind=="CANDIDATE_PREVIEW_RESET":draft_parts.clear()
            elif kind=="CANDIDATE_PREVIEW_DELTA":
                if first_draft is None:first_draft=round(elapsed,2)
                draft_parts.append(str(event.get("text") or ""))
            elif kind=="DELTA":
                if first_text is None:first_text=round(elapsed,2)
                text_parts.append(str(event.get("text") or ""))
            elif kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    final="".join(text_parts)
    emit("LIVE_SYNTHETIC",terminal=terminal,firstDraftSec=first_draft,
         firstAcceptedSec=first_text,totalSec=round(time.monotonic()-start,2),
         finalChars=len(final),draftChars=len("".join(draft_parts)),
         isHtml=("<html" in final.lower() or "<!doctype html" in final.lower()),
         statuses=events[-8:])
    return terminal,final

def live_accept(api,rev):
    # End-to-end route is exercised without accessing personal project data.
    # Forced length/resumption branch is covered separately by deterministic
    # provider doubles before this action is permitted to publish.
    deadline=time.monotonic()+1000
    for attempt in range(1,5):
        if api.repo_info(SPACE,repo_type="space").sha!=rev:
            raise RuntimeError("Concurrent Hugging Face publication")
        try:
            terminal,final=synthetic("Write a complete self-contained HTML page with a heading, an interactive button and polished styles. Return runnable HTML.",max_secs=260)
            if terminal in ("COMPLETE","COMPLETED") and ("<html" in final.lower() or "<!doctype html" in final.lower()) and len(final)>100:
                emit("LIVE_ACCEPTED",revision=rev,attempt=attempt)
                return
        except Exception as exc:
            emit("LIVE_CHECK_NOT_READY",kind=type(exc).__name__,attempt=attempt,
                 detail=str(exc)[:130])
        time.sleep(10)
    raise RuntimeError("No complete validated HTML from new live model")

def main():
    args=sys.argv[1:]
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    if args==["preflight"]:
        snapshot(api);return
    if args!=["publish"]:raise SystemExit("Usage: script preflight | publish")
    if not os.getenv("HF_TOKEN") or os.getenv("SWRLZ_CODE_CONTINUATION_APPROVED")!="1":
        raise RuntimeError("HF_TOKEN and source-scoped release approval required")
    old_rev=(BACKUP/"revision.txt").read_text().strip()
    old_data=(BACKUP/FILE).read_bytes()
    candidate=patch(old_data.decode()).encode()
    tests(old_data.decode(),candidate.decode())
    if api.repo_info(SPACE,repo_type="space").sha!=old_rev:
        raise RuntimeError("Space changed since snapshot; abort")
    new_rev=None
    try:
        new_rev=commit(api,old_rev,candidate,
            "§C: resume length-capped source edits before acceptance, preserve code validation")
        warm(api,new_rev)
        live_accept(api,new_rev)
        emit("RELEASE_KEPT",revision=new_rev,tokenWindow=16384,threads=18)
    except Exception:
        emit("RELEASE_REJECTED",newRevision=new_rev)
        if new_rev and api.repo_info(SPACE,repo_type="space").sha==new_rev:
            revert=commit(api,new_rev,old_data,
                "Rollback §C source-edit continuation to exact last working code")
            warm(api,revert)
            emit("EXACT_ROLLBACK_COMPLETE",revision=revert)
        elif new_rev:emit("ROLLBACK_BLOCKED_CONCURRENT_UPDATE")
        raise

if __name__=="__main__":main()
