#!/usr/bin/env python3
"""Source-scoped §C repair-not-regenerate coding pipeline release.

Preserves Qwen3.5-9B CPU/KV hardware, profiles, existing chat/artifact storage,
GitHub ownership, §E editor guardrails and verified complete-code delivery.
"""
from __future__ import annotations
import ast,hashlib,http.cookiejar,json,os,re,sys,tempfile,time,urllib.parse,urllib.request,uuid
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
CODE="qwen_coder_engine.py"
HELPER_NAME="project_code_targeted_repair_v1.py"
HELPER_LOCAL=Path(__file__).with_name(HELPER_NAME)
BACKUP=Path("swrlz-targeted-candidate-repair-backup")
MARK="swrlz-targeted-candidate-repair-v1"
HEADER={"User-Agent":"Swyrlz-Code-Repair-Verification","Cache-Control":"no-cache"}
if not HELPER_LOCAL.is_file():raise RuntimeError("Pinned source-preserving repair helper not found")

def emit(name,**fields):
    print("TARGETED_CODE_REPAIR",json.dumps({"stage":name,**fields},sort_keys=True,ensure_ascii=False),flush=True)
def digest(data):return hashlib.sha256(data).hexdigest()
def once(text,old,new,label):
    n=text.count(old)
    if n!=1:raise RuntimeError("EXACT_SOURCE_ANCHOR_DRIFT "+label+" count="+str(n))
    return text.replace(old,new,1)

NEW_HELPER=r'''from project_code_targeted_repair_v1 import (
    patch_context as _swrlz_repair_context,
    apply_patch as _swrlz_apply_patch,
    monotonic_progress as _swrlz_patch_progress,
    TargetedRepairError as _SwrlzPatchError,
    MAX_REPAIRS as _SWRLZ_PATCH_ATTEMPTS,
)


def _swrlz_patch_candidate_once(model,source,check,original):
    """One bounded native JSON patch; do not regenerate the whole artifact."""
    messages=_swrlz_repair_context(source,check.get("reasons"),original)
    allowance=min(2048,CONTEXT_TOKENS-_token_count(model,messages)-CONTEXT_SAFETY_TOKENS)
    if allowance<MIN_OUTPUT_TOKENS:
        raise _SwrlzPatchError("PATCH_CONTEXT","Insufficient context for a safe targeted patch")
    started=time.perf_counter()
    native=model.create_chat_completion(
        messages=messages,max_tokens=allowance,temperature=0.13,stream=False)
    choices=native.get("choices") or []
    if not choices:
        raise _SwrlzPatchError("PATCH_EMPTY","Repair model returned no choice")
    finish=str(choices[0].get("finish_reason") or "")
    if finish!="stop":
        raise _SwrlzPatchError("PATCH_TRUNCATED","Incomplete native repair proposal")
    raw=str((choices[0].get("message") or {}).get("content") or "")
    updated,receipt=_swrlz_apply_patch(source,raw)
    timing={"finishReason":finish,
            "durationMs":round((time.perf_counter()-started)*1000,2),
            "repairPatch":True}
    return updated,receipt,timing


'''
MAIN_REJECT='''            if candidate_check.get("status")=="REJECT":
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":2}'''
MAIN_REPAIR='''            if candidate_check.get("status")=="REJECT" and code_delivery:
                # Never discard a largely complete source and regenerate
                # everything to repair a tiny missing CSS/JS/HTML section.
                if timing.get("finishReason")!="length":
                    for repair_number in range(1,_SWRLZ_PATCH_ATTEMPTS+1):
                        yield {"type":"STATUS","phase":"CODE_REPAIRING",
                            "reason":"Applying targeted validator repair %d/%d"%
                                     (repair_number,_SWRLZ_PATCH_ATTEMPTS)}
                        try:
                            proposed,repair_receipt,repair_timing=_swrlz_patch_candidate_once(
                                model,candidate_text,candidate_check,prompt)
                        except _SwrlzPatchError as exc:
                            yield {"type":"STATUS","phase":"CODE_REPAIR_PROPOSAL_REJECTED",
                                "reason":exc.code}
                            break
                        next_check,next_fp=validate_attempt(
                            proposed,candidate_fp,completion=repair_timing)
                        if not _swrlz_patch_progress(candidate_check,next_check):
                            yield {"type":"STATUS","phase":"CODE_REPAIR_NOT_APPLIED",
                                "reason":"No validator improvement or new regression"}
                            break
                        candidate_text,candidate_check,candidate_fp=proposed,next_check,next_fp
                        regeneration_attempted=True
                        regeneration_reason="source-preserving-targeted-patch"
                        attempt=candidate_attempt_receipt(
                            repair_number+1,"targeted-source-patch",
                            repair_timing,candidate_check,candidate_fp,
                            previous_attempt_fingerprint=repair_receipt["before"],
                            repair_target_fingerprint=repair_target_fp,
                        )
                        candidate_attempts.append(attempt)
                        yield {"type":"CANDIDATE_ATTEMPT","attempt":attempt}
                        yield {"type":"STATUS","phase":"CODE_REPAIR_APPLIED",
                            "reason":"Source-preserving patch; modified %d old bytes and added %d new bytes"%
                                     (repair_receipt["removedBytes"],repair_receipt["addedBytes"])}
                        if candidate_check.get("status")=="PASS":
                            yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":repair_number+1}
                            yield {"type":"CANDIDATE_PREVIEW_DELTA",
                                   "attempt":repair_number+1,"text":candidate_text}
                            break
                if candidate_check.get("status")!="PASS":
                    checkpoint=_swrlz_checkpoint_record(
                        candidate_text,prompt,programming,
                        payload.get("projectImportManifest"),timing.get("continuationSegments"),
                        repair_needed=(timing.get("finishReason")!="length"),
                        reasons=candidate_check.get("reasons"))
                    if checkpoint is not None:
                        yield from _swrlz_pause_code_events(
                            checkpoint,timing.get("continuationSegments") or 1,
                            len(candidate_text.encode("utf-8")))
                        return
                    yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":0}
                    yield {"type":"DELTA","text":(
                        "The existing draft exceeded the safe checkpoint size and has not "
                        "passed code validation. Edit a smaller project file or split the "
                        "request into source-owned files; no earlier code was marked complete."
                    )}
                    yield {"type":"COMPLETED","phase":"CODE_SAFE_LIMIT"}
                    return
            if candidate_check.get("status")=="REJECT" and not code_delivery:
                yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":2}'''
CHECKPOINT_BEFORE='''def _swrlz_checkpoint_record(source,original_prompt,programming,manifest,segments):'''
CHECKPOINT_AFTER='''def _swrlz_checkpoint_record(source,original_prompt,programming,manifest,segments,
                             repair_needed=False,reasons=None):'''
RECORD_BEFORE='''        "state":"UNVERIFIED_INCOMPLETE",
    }'''
RECORD_AFTER='''        "state":"UNVERIFIED_INCOMPLETE",
        "repairNeeded":bool(repair_needed),
        "validationReasons":[str(reason)[:160] for reason in (reasons or [])[:14]],
    }'''
RESUME_GENERATE='''    # Match the normal coding engine's model execution serialization.
    with _lock:
        draft,timing=yield from _swrlz_code_candidate_preview(
            model,[],4096,0.25,1,allow_continue=True,seed_text=source)
    completion=completion_validation(_candidate_structure_check(draft,programming,history),timing)'''
RESUME_REPAIR='''    # Preserve a structural-repair checkpoint without appending unrelated
    # text to the already closed HTML document.
    with _lock:
        if checkpoint.get("repairNeeded"):
            draft=source
            timing={"finishReason":"stop","continuationSegments":0}
        else:
            draft,timing=yield from _swrlz_code_candidate_preview(
                model,[],4096,0.25,1,allow_continue=True,seed_text=source)
        completion=completion_validation(
            _candidate_structure_check(draft,programming,history),timing)
        if timing.get("finishReason")!="length" and completion.get("status")!="PASS":
            for repair_number in range(_SWRLZ_PATCH_ATTEMPTS):
                yield {"type":"STATUS","phase":"CODE_REPAIRING",
                       "reason":"Repairing incomplete saved source; attempt %d"%
                       (repair_number+1)}
                try:
                    proposed,receipt,repair_timing=_swrlz_patch_candidate_once(
                        model,draft,completion,original)
                except _SwrlzPatchError as exc:
                    yield {"type":"STATUS","phase":"CODE_REPAIR_PROPOSAL_REJECTED",
                           "reason":exc.code}
                    break
                next_check=completion_validation(
                    _candidate_structure_check(proposed,programming,history),repair_timing)
                if not _swrlz_patch_progress(completion,next_check):
                    yield {"type":"STATUS","phase":"CODE_REPAIR_NOT_APPLIED",
                           "reason":"No validator improvement or new regression"}
                    break
                draft,completion=proposed,next_check
                yield {"type":"STATUS","phase":"CODE_REPAIR_APPLIED",
                       "reason":"Repaired saved source without replacing unaffected code"}
                if completion.get("status")=="PASS":break'''
RESUME_CHECKPOINT='''        next_checkpoint=_swrlz_checkpoint_record(
            draft,original,programming,checkpoint.get("sourceManifest"),accumulated)'''
RESUME_CHECKPOINT_NEW='''        next_checkpoint=_swrlz_checkpoint_record(
            draft,original,programming,checkpoint.get("sourceManifest"),accumulated,
            repair_needed=(timing.get("finishReason")!="length"),
            reasons=completion.get("reasons"))'''

def patch_engine(raw):
    text=raw.decode("utf-8")
    if MARK in text:raise RuntimeError("Repair pipeline already deployed")
    import_anchor="def _swrlz_resume_code_events(payload):"
    text=once(text,import_anchor,NEW_HELPER+import_anchor,"repair helper import")
    text=once(text,CHECKPOINT_BEFORE,CHECKPOINT_AFTER,"checkpoint repair metadata")
    text=once(text,RECORD_BEFORE,RECORD_AFTER,"checkpoint validation reasons")
    text=once(text,RESUME_GENERATE,RESUME_REPAIR,"resume invalid draft without destructive append")
    text=once(text,RESUME_CHECKPOINT,RESUME_CHECKPOINT_NEW,"resume remaining defects checkpoint")
    text=once(text,MAIN_REJECT,MAIN_REPAIR,"main source-preserving repair before full retry")
    ast.parse(text,filename=CODE)
    return text.encode("utf-8")

def test_helper():
    import importlib.util
    spec=importlib.util.spec_from_file_location("swrlz_targeted_patch",HELPER_LOCAL)
    lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
    source='<html><head></head><body><button id="save">Save</button></body></html>'
    css='<style>button{color:purple}</style>'
    s1,p1=lib.apply_patch(source,json.dumps({
        "sourceSha256":lib.source_sha(source),"op":"insert_before","anchor":"</head>","code":css}))
    assert s1==source.replace("</head>",css+"</head>") and p1["removedBytes"]==0
    js='<script>document.getElementById("save").onclick=()=>{}</script>'
    s2,p2=lib.apply_patch(s1,json.dumps({
        "sourceSha256":lib.source_sha(s1),"op":"insert_before","anchor":"</body>","code":js}))
    assert s2==s1.replace("</body>",js+"</body>")
    assert "<button id=\"save\">" in s2
    assert lib.monotonic_progress({"status":"REJECT","reasons":["missing-css","missing-js"]},
                                  {"status":"REJECT","reasons":["missing-js"]})
    assert not lib.monotonic_progress({"status":"REJECT","reasons":["missing-css","missing-js"]},
                                     {"status":"REJECT","reasons":["missing-css","new-error"]})
    try:lib.apply_patch(s1,{"sourceSha256":lib.source_sha(source),
                            "op":"append","anchor":"","code":"x"})
    except lib.TargetedRepairError:pass
    else:raise RuntimeError("Stale patch unexpectedly accepted")
    emit("EXACT_PATCH_TESTS_PASS",filesPreserved=True,cssAndJsIntegrated=True,
         staleSourceDenied=True,newFailuresDenied=True)

def test_engine(source):
    tree=ast.parse(source,filename=CODE)
    test_helper()
    funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    for name in ("_swrlz_patch_candidate_once","_swrlz_resume_code_events",
                 "_swrlz_checkpoint_record","generate_events"):
        assert name in funcs,name
    assert "if candidate_check.get(\"status\")==\"REJECT\" and code_delivery:" in source
    assert "if candidate_check.get(\"status\")==\"REJECT\" and not code_delivery:" in source
    assert '\"repairNeeded\":bool(repair_needed)' in source
    assert "completion_validation(" in source
    assert "CANDIDATE_PREVIEW_RESET" in source
    assert "CODE_OUTPUT_CHECKPOINT" in source
    assert "CONTEXT_TOKENS=16384" in source
    assert "max_segments=8 if allow_continue else 1" in source
    # Fake model tests prove the repair helper asks for a patch rather than a
    # complete replacement and obeys actual native stop status.
    repair=funcs["_swrlz_patch_candidate_once"]
    libsrc=HELPER_LOCAL.read_text()
    namespace={"time":time,"CONTEXT_TOKENS":16384,
        "CONTEXT_SAFETY_TOKENS":128,"MIN_OUTPUT_TOKENS":384,
        "_token_count":lambda m,x:200,
        "_swrlz_repair_context":None}
    import importlib.util
    spec=importlib.util.spec_from_file_location("swrlz_test_lib",HELPER_LOCAL)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    namespace.update({
        "_swrlz_repair_context":mod.patch_context,
        "_swrlz_apply_patch":mod.apply_patch,
        "_SwrlzPatchError":mod.TargetedRepairError})
    exec(compile(ast.Module(body=[repair],type_ignores=[]),"<targeted-repair-model-test>","exec"),namespace)
    source='<html><head></head><body>Unchanged feature</body></html>'
    class Model:
        def __init__(self,reason="stop"):self.calls=[];self.reason=reason
        def create_chat_completion(self,**kwargs):
            self.calls.append(kwargs)
            p=json.dumps({"sourceSha256":mod.source_sha(source),
                "op":"insert_before","anchor":"</head>","code":"<style>body{color:blue}</style>"})
            return {"choices":[{"finish_reason":self.reason,"message":{"content":p}}]}
    fake=Model()
    repaired,receipt,timing=namespace["_swrlz_patch_candidate_once"](
        fake,source,{"reasons":["missing-required-language:css"]},"Improve page")
    assert "Unchanged feature" in repaired and "<style>" in repaired
    assert receipt["removedBytes"]==0 and timing["finishReason"]=="stop"
    assert fake.calls[0]["max_tokens"]<=2048 and not fake.calls[0]["stream"]
    assert "not rewriting" in fake.calls[0]["messages"][0]["content"]
    try:namespace["_swrlz_patch_candidate_once"](
        Model("length"),source,{"reasons":["missing-css"]},"")
    except mod.TargetedRepairError:pass
    else:raise RuntimeError("Truncated repair patch accepted")
    emit("FAKE_NATIVE_PATCH_TESTS_PASS",patchStopRequired=True,
         originalSourcePreserved=True,patchOutputBounded=True)

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    paths=api.list_repo_files(SPACE,repo_type="space",revision=rev)
    if HELPER_NAME in paths:
        raw=Path(hf_hub_download(SPACE,HELPER_NAME,repo_type="space",
                 revision=rev,token=api.token)).read_bytes()
        if digest(raw)!=digest(HELPER_LOCAL.read_bytes()):
            raise RuntimeError("Conflicting remote helper source; refusing overwrite")
    old=Path(hf_hub_download(SPACE,CODE,repo_type="space",
               revision=rev,token=api.token)).read_bytes()
    candidate=patch_engine(old)
    test_engine(candidate.decode())
    BACKUP.mkdir(exist_ok=True)
    (BACKUP/CODE).write_bytes(old)
    (BACKUP/"revision.txt").write_text(rev)
    (BACKUP/"manifest.json").write_text(json.dumps({
        "revision":rev,"oldSha256":digest(old),"newSha256":digest(candidate),
        "helperSha256":digest(HELPER_LOCAL.read_bytes()),
        "modelChanged":False,"threadCountChanged":False,"contextChanged":False,
        "githubAuthChanged":False,"forgeEditorAuthorityChanged":False},indent=2))
    emit("READ_ONLY_PREFLIGHT_PASS",revision=rev,originalSha=digest(old),
         candidateSha=digest(candidate))
    return rev,old,candidate

def push(api,rev,files,message):
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent HF Space publication; refusing update")
    with tempfile.TemporaryDirectory(prefix="swrlz-targeted-patch-") as folder:
        operations=[]
        for name,blob in files.items():
            path=Path(folder)/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(blob)
            operations.append(CommitOperationAdd(path_in_repo=name,path_or_fileobj=str(path)))
        res=api.create_commit(repo_id=SPACE,repo_type="space",
          parent_commit=rev,operations=operations,commit_message=message)
    new=str(res.oid)
    for name,blob in files.items():
        actual=Path(hf_hub_download(SPACE,name,repo_type="space",
                    revision=new,token=api.token)).read_bytes()
        if digest(blob)!=digest(actual):
            raise RuntimeError("Live source hash mismatch "+name)
    emit("PUBLISHED_SOURCE_HASH_VERIFIED",revision=new,paths=list(files))
    return new

def readiness(api,rev,timeout=960):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if api.repo_info(SPACE,repo_type="space").sha!=rev:
            raise RuntimeError("Concurrent source change during warmup")
        try:
            req=urllib.request.Request(BASE+"/api/hf/qwen35-ready",headers=HEADER)
            with urllib.request.urlopen(req,timeout=25) as response:
                status=json.load(response)
            if (status.get("ready") is True and status.get("model")=="qwen3.5-9b"
                and (status.get("decodeThreads"),status.get("batchThreads"),
                     status.get("cpuCapacity"))==(18,18,16)):
                emit("RESIDENT_MODEL_READY",revision=rev,threads=18,quota=16)
                return
        except Exception:pass
        time.sleep(12)
    raise TimeoutError("Expected 9B runtime did not become ready")

def live_smoke():
    opener=urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4())
    body={"modelId":"700m","requestId":rid,
          "threadId":"swrlz-code-repair-verify-"+uuid.uuid4().hex,
          "prompt":"Create a short complete single HTML page with a clickable button and one CSS style. Return the runnable HTML code.",
          "profileId":"LALM","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",
             method="POST",data=json.dumps(body).encode(),
             headers={**HEADER,"Content-Type":"application/json"})
    with opener.open(req,timeout=40) as response:
        if response.status!=202:raise RuntimeError("Synthetic coding request not accepted")
        response.read()
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    text_parts=[];term=None
    with opener.open(urllib.request.Request(url,headers=HEADER),timeout=490) as response:
        for raw in response:
            try:event=json.loads(raw)
            except (UnicodeError,ValueError):continue
            if event.get("requestId") and event.get("requestId")!=rid:
                raise RuntimeError("Cross-request stream")
            if event.get("type")=="DELTA":text_parts.append(str(event.get("text") or ""))
            if event.get("type") in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                term=event.get("type");break
    final="".join(text_parts)
    state={}
    for _ in range(12):
        with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",
                     headers=HEADER),timeout=30) as response:state=json.load(response)
        active=state.get("activeGeneration") or {}
        if active.get("requestId")==rid and (active.get("candidateValidation") or {}).get("status"):
            break
        time.sleep(2)
    active=state.get("activeGeneration") or {}
    check=active.get("candidateValidation") or {}
    emit("LIVE_HTML_CHECK",terminal=term,finalChars=len(final),
         validator=check.get("status"),matchingRequest=active.get("requestId")==rid,
         hasHtml=("<html" in final.lower() or "<!doctype html" in final.lower()))
    if (term not in ("COMPLETE","COMPLETED")
        or ("<html" not in final.lower() and "<!doctype html" not in final.lower())
        or active.get("requestId")!=rid or check.get("status")!="PASS"):
        raise RuntimeError("Live normal coding regression or missing scoped validation")
    emit("LIVE_NORMAL_CODE_ACCEPTED",sourcePreserved=True)

def main():
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if sys.argv[1:]==["preflight"]:
        snapshot(api);return
    if sys.argv[1:]!=["publish"]:
        raise SystemExit("Usage: preflight|publish")
    if os.environ.get("SWRLZ_TARGETED_REPAIR_APPROVED")!="1" or not api.token:
        raise RuntimeError("Scoped release approval required")
    old_rev=(BACKUP/"revision.txt").read_text().strip()
    old=(BACKUP/CODE).read_bytes()
    new=patch_engine(old)
    test_engine(new.decode())
    if api.repo_info(SPACE,repo_type="space").sha!=old_rev:
        raise RuntimeError("Remote source changed since exact preflight")
    deployed=None
    try:
        deployed=push(api,old_rev,{CODE:new,HELPER_NAME:HELPER_LOCAL.read_bytes()},
            "§C: source-preserving targeted repair of code validation failures")
        readiness(api,deployed)
        live_smoke()
        emit("LIVE_RELEASE_KEPT",revision=deployed,
             patchInsteadOfRegenerate=True)
    except Exception:
        emit("RELEASE_REJECTED",revision=deployed)
        if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
            restored=push(api,deployed,{CODE:old},
                "Rollback §C targeted repair to exact last verified coding engine")
            readiness(api,restored)
            emit("EXACT_ENGINE_ROLLBACK_COMPLETED",revision=restored)
        elif deployed:emit("ROLLBACK_BLOCKED_BY_CONCURRENT_REMOTE_CHANGE")
        raise

if __name__=="__main__":main()
