#!/usr/bin/env python3
"""Guarded existing-Space source patch: §C lyric remixes, parody and remaster QA.

Change two current live Python sources and add one pure helper module.
No whole-Space upload, model/config/voice changes, or destructive resets.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import io
import json
import os
import re
from pathlib import Path

SPACE="kamiloki/Swyrlz"
ENGINE="lfm2_700m_engine.py"
STRUCTURE="music_structure.py"
HELPER="music_transform_quality.py"
ONLINE="online_tools.py"
STATION="station.py"
NATIVE="qwen35_single_runtime.py"
UI="chat/§wyrlz/index.html"
STOP="stop_transport.py"
BACKUP=Path("reports/swrlz-music-transform-v1")

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def once(source: str, old: str, new: str, label: str) -> str:
    count=source.count(old)
    if count != 1:
        raise ValueError(f"LIVE_SOURCE_DRIFT {label} expected 1 found {count}")
    return source.replace(old,new,1)

def patch_structure(source: str) -> str:
    if "swrlz-song-transformation-quality-v1" in source:
        raise ValueError("Already installed")
    source=once(source,
        "from typing import Any",
        "from typing import Any\nfrom music_transform_quality import transformation_contract, quality_review",
        "music quality import")
    # The original parser recognized 'those', but missed 'remix it' and
    # 'create a parody from it'. Resolve these ONLY when the user requests
    # a creative transformation and a prior verified song is in the thread.
    source=once(source,
        'r"(?i)\\b(?:those|these|earlier|previous|provided|above|reference|study|from\\s+that)\\b"',
        'r"(?i)\\b(?:those|these|earlier|previous|provided|above|reference|study|from\\s+that|from\\s+it|this|that|it)\\b"',
        "reference pointer")
    wrapper='''# swrlz-song-transformation-quality-v1: extend existing router, do not
# divert ordinary song lookups or music-analysis questions into generation.
_swrlz_prior_creative_transform_request=creative_music_transform_request
def creative_music_transform_request(prompt: str) -> bool:
    return (_swrlz_prior_creative_transform_request(prompt)
            or transformation_contract(prompt) is not None)


'''
    source=once(source,
        "def creative_music_request(prompt: str) -> dict[str,Any]:",
        wrapper+"def creative_music_request(prompt: str) -> dict[str,Any]:",
        "creative intent extension")
    func=next((node for node in ast.parse(source).body
               if isinstance(node,ast.FunctionDef) and node.name=="original_rap_violations"),None)
    if func is None:
        raise ValueError("Missing existing source borrowing guard")
    old=ast.get_source_segment(source,func)
    if not old:
        raise ValueError("Missing lyric guard source")
    review='''    # swrlz-song-transformation-quality-v1: source-safe structural checks.
    review=quality_review(delivered,allow_aab=False)
    faults.extend(x for x in review["reasons"] if x not in faults)
    return faults'''
    patched=once(old,"    return faults",review,"lyric quality gate")
    source=once(source,old,patched,"source borrowing gate extension")
    ast.parse(source,filename=STRUCTURE)
    return source

def patch_engine(source: str) -> str:
    if "swrlz-song-transformation-quality-v1" in source:
        raise ValueError("Already installed")
    imports=[line for line in source.splitlines()
             if line.startswith("from music_structure import ")]
    if len(imports)!=1:
        raise ValueError("Cannot find canonical music structure import")
    source=once(source,imports[0],imports[0]+
        "\nfrom music_transform_quality import transformation_contract, transformation_directive, quality_review, repair_directive",
        "music transform imports")
    old='''    music_policy="" if source_change_mode else music_model_policy(prompt)'''
    new='''    # swrlz-song-transformation-quality-v1: classify a genuine creative
    # operation separately from source lookup, analysis or coding.
    music_transform_contract=(transformation_contract(
        prompt,reference_available=bool(reference_structure))
        if not source_change_mode and not programming.get("codingTask") else None)
    music_policy="" if source_change_mode else music_model_policy(prompt)'''
    source=once(source,old,new,"music operation contract")
    source=once(source,
        "    native_evidence=payload.get(\"nativeEditorEvidence\")",
        "    if music_transform_contract:\n        system+=transformation_directive(music_transform_contract)\n    native_evidence=payload.get(\"nativeEditorEvidence\")",
        "operation guidance")
    old='''        elif reference_structure and not programming.get("codingTask"):
            # Complete-song work used the generic 768 token cap'''
    new='''        elif music_transform_contract:
            response_tokens=min(2048,available_output_tokens);temperature=0.42
        elif reference_structure and not programming.get("codingTask"):
            # Complete-song work used the generic 768 token cap'''
    source=once(source,old,new,"creative output budget")
    branch='''        elif longform_target:
            longform_result=complete_longform('''
    replacement='''        elif music_transform_contract and not programming.get("codingTask"):
            # swrlz-song-transformation-quality-v1: buffer all non-source music
            # transformations before emitting text. A rejected duplicate verse
            # must never be published then retracted from an SSE stream.
            lyric_mode=music_transform_contract["mode"]
            draft,timing=buffered_chat_completion(model,messages,response_tokens,temperature)
            candidate_text=original_rap_delivery(draft)
            def review_song_transform(rendered,raw):
                check=quality_review(
                    rendered,
                    allow_aab=bool(re.search(r"(?i)\b(?:aab|12[- ]bar blues)\b",prompt)))
                if reference_structure:
                    borrowed=original_rap_violations(raw,rendered,history,reference_structure)
                    if borrowed:
                        check["status"]="REJECT"
                        check["reasons"]=list(dict.fromkeys(
                            list(check.get("reasons") or [])+borrowed))
                return check
            candidate_check=review_song_transform(candidate_text,draft)
            first_fp=_candidate_fingerprint(candidate_text)
            candidate_attempts.append(candidate_attempt_receipt(
                1,"music-transform-"+lyric_mode,timing,candidate_check,first_fp))
            yield {"type":"CANDIDATE_ATTEMPT","attempt":candidate_attempts[-1]}
            if candidate_check["status"]!="PASS":
                regeneration_attempted=True
                regeneration_reason="music-structural-quality"
                retry_messages=list(messages)+[{"role":"system","content":
                    repair_directive(candidate_check["reasons"],lyric_mode)}]
                repaired,retry_timing=buffered_chat_completion(
                    model,retry_messages,response_tokens,min(0.52,temperature+0.07))
                candidate_text=original_rap_delivery(repaired)
                candidate_check=review_song_transform(candidate_text,repaired)
                candidate_attempts.append(candidate_attempt_receipt(
                    2,"music-transform-repair",retry_timing,candidate_check,
                    _candidate_fingerprint(candidate_text),
                    previous_attempt_fingerprint=first_fp))
                yield {"type":"CANDIDATE_ATTEMPT","attempt":candidate_attempts[-1]}
            if candidate_check["status"]=="PASS":
                first_delta=round((time.perf_counter()-started)*1000,3)
                yield {"type":"DELTA","text":candidate_text}
            else:
                first_delta=round((time.perf_counter()-started)*1000,3)
                yield {"type":"DELTA","text":"I couldn't verify a distinct, complete lyrical transformation. I won't present duplicated verses as a finished song."}
        elif longform_target:
            longform_result=complete_longform('''
    source=once(source,branch,replacement,"transform quality generation branch")
    ast.parse(source,filename=ENGINE)
    return source

def patch_online(source: str) -> str:
    if "swrlz-music-followup-feedback-v1" in source:
        raise ValueError("Already installed")
    line=next((x for x in source.splitlines()
               if x.startswith("from music_structure import ")),None)
    if line is None:raise ValueError("Missing verified music routing import")
    source=once(source,line,line+"\nfrom music_transform_quality import music_feedback_followup",
                "feedback import")
    marker='    lyrics_creative=creative_music_transform_request(text)'
    injected='''    lyrics_creative=creative_music_transform_request(text)
    # swrlz-music-followup-feedback-v1: current-turn critique beats prior
    # lyric lookup. Explicit affirmative new research is still routed normally.
    if not programming.get("codingTask") and music_feedback_followup(text,history):
        return {"contract":ONLINE_CONTRACT,"requested":False,
                "kind":"none","reason":"music-quality-feedback",
                "query":"","locationText":"","clientLocation":None,
                "locationRequired":False,"programming":False}'''
    source=once(source,marker,injected,"feedback lookup guard")
    ast.parse(source,filename=ONLINE)
    return source

def patch_native(source: str) -> str:
    source=once(source,'from huggingface_hub import hf_hub_download',
         'from huggingface_hub import hf_hub_download\nfrom stop_transport import completion_response, generation_cancelled',
         "native stop import")
    source=once(source,
         'with _post("/v1/chat/completions", payload, timeout=900) as response:',
         'with completion_response(payload,SERVER_PORT,_post,timeout=900) as response:',
         "native interruptible loopback socket")
    source=once(source,
         '                    for raw in response:\n                        if not raw.startswith(b"data:"):',
         '                    for raw in response:\n                        if generation_cancelled():\n                            return\n                        if not raw.startswith(b"data:"):',
         "native stream stop gate")
    source=once(source,
         '            finally:\n                self.reset_token_cache()',
         '''            except Exception:
                if not generation_cancelled():
                    raise
                # A verified user Stop interrupted the local socket; no
                # unrelated backend error is swallowed.
                return
            finally:
                self.reset_token_cache()''',
         "native cancel exception handling")
    ast.parse(source,filename=NATIVE)
    return source

def patch_station(source: str) -> str:
    source=once(source,
         '    payload["_cancelCheck"]=_cancel_from_worker\n    try:',
         '    payload["_cancelCheck"]=_cancel_from_worker\n    from stop_transport import bind_generation_cancel, release_generation_cancel\n    bind_generation_cancel(request_id,_cancel_from_worker)\n    try:',
         "station generation bind")
    source=once(source,
         '    finally:\n        # Early cancellation, response replacement, and CAS failures also',
         '    finally:\n        release_generation_cancel(request_id)\n        # Early cancellation, response replacement, and CAS failures also',
         "station generation release")
    source=once(source,
         '    _invalidate_forge(_forge_contexts.get(key))\n    return {"ok":True,"requestId":rid,"state":"CANCEL_REQUESTED"}',
         '''    _invalidate_forge(_forge_contexts.get(key))
    # The account/session request ID above was authenticated. Interrupt only
    # that request's registered loopback Qwen stream (including prefill).
    from stop_transport import cancel_active_request
    native_interrupt=cancel_active_request(rid)
    return {"ok":True,"requestId":rid,"state":"CANCEL_REQUESTED",
            "nativeInterruptRequested":bool(native_interrupt)}''',
         "Station native Stop endpoint")
    ast.parse(source,filename=STATION)
    return source

def patch_ui(source: str) -> str:
    source=once(source,
         'stopButton.addEventListener("pointerdown",()=>{swrlzStopPointerArmed=true;},{passive:true});',
         '''stopButton.addEventListener("pointerdown",event=>{
        // swrlz-mobile-stop-gesture-v1: send Stop on actual finger-down,
        // not after a potentially cancelled/re-targeted synthetic tap click.
        swrlzStopPointerArmed=true;
        if(event.isPrimary&&event.button===0)stopButton.click();
      },{passive:true});''',
         "mobile stop pointerdown")
    source=once(source,
         '        stationCancellation=cancellation;\n        if(stationSubmission?.requestId===rid)stationSubmission.cancelRequested=true;',
         '''        stationCancellation=cancellation;
        if(stationGeneration?.requestId===rid){
          stationGeneration.status=[...(stationGeneration.status||[]),
            {phase:"STOPPING",reason:"Stop requested; interrupting the current model response"}];
          renderStationGeneration();
        }
        if(stationSubmission?.requestId===rid)stationSubmission.cancelRequested=true;''',
         "immediate Stop visual receipt")
    if 'swrlz-mobile-stop-gesture-v1' not in source:
        raise ValueError("Mobile pointer fix missing")
    return source

def candidate(live: dict[str,bytes]) -> dict[str,bytes]:
    helper=Path(__file__).with_name("music_transform_quality_v1.py").read_bytes()
    stopper=Path(__file__).with_name("stop_transport_v1.py").read_bytes()
    ast.parse(helper,filename=HELPER)
    ast.parse(stopper,filename=STOP)
    edits={
        ENGINE:patch_engine(live[ENGINE].decode("utf-8")).encode("utf-8"),
        STRUCTURE:patch_structure(live[STRUCTURE].decode("utf-8")).encode("utf-8"),
        ONLINE:patch_online(live[ONLINE].decode("utf-8")).encode("utf-8"),
        STATION:patch_station(live[STATION].decode("utf-8")).encode("utf-8"),
        NATIVE:patch_native(live[NATIVE].decode("utf-8")).encode("utf-8"),
        UI:patch_ui(live[UI].decode("utf-8")).encode("utf-8"),
        HELPER:helper,
        STOP:stopper,
    }
    return edits

def snapshot():
    from huggingface_hub import HfApi,hf_hub_download
    api=HfApi()
    rev=api.repo_info(SPACE,repo_type="space").sha
    if not re.fullmatch(r"[0-9a-f]{40}",str(rev or "")):
        raise ValueError("Live Space sha unavailable")
    before={}
    for f in (ENGINE,STRUCTURE,ONLINE,STATION,NATIVE,UI):
        before[f]=Path(hf_hub_download(SPACE,f,repo_type="space",revision=rev)).read_bytes()
    # Avoid silently replacing a helper from another release line.
    info=api.list_repo_files(SPACE,repo_type="space",revision=rev)
    if HELPER in info or STOP in info:
        raise ValueError("Existing helper already deployed; reconcile instead of overwriting")
    modified=candidate(before)
    BACKUP.mkdir(parents=True,exist_ok=True)
    for name,data in before.items():
        target=BACKUP / name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    record={"schema":"swrlz-music-transformation-release-v1",
            "space":SPACE,"revision":rev,
            "before":{f:sha(v) for f,v in before.items()},
            "after":{f:sha(v) for f,v in modified.items()}}
    (BACKUP/"manifest.json").write_text(json.dumps(record,indent=2)+"\n")
    print("MUSIC_TRANSFORM_PREFLIGHT",json.dumps(record,sort_keys=True),flush=True)

def publish():
    from huggingface_hub import HfApi,CommitOperationAdd,hf_hub_download
    if os.getenv("SWRLZ_MUSIC_TRANSFORM_APPROVED")!="1":
        raise PermissionError("Missing governed user-approved release mode")
    token=os.getenv("HF_TOKEN")
    if not token:raise PermissionError("Missing guarded Hugging Face credential")
    record=json.loads((BACKUP/"manifest.json").read_text())
    api=HfApi(token=token)
    rev=record["revision"]
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("SPACE_REVISION_MOVED: no deployment from stale snapshot")
    originals={}
    for name in (ENGINE,STRUCTURE,ONLINE,STATION,NATIVE,UI):
        data=(BACKUP/name).read_bytes()
        if sha(data)!=record["before"][name]:
            raise RuntimeError("Snapshot hash mismatch "+name)
        actual=Path(hf_hub_download(SPACE,name,repo_type="space",revision=rev,token=token)).read_bytes()
        if data!=actual:raise RuntimeError("Live source and snapshot disagree "+name)
        originals[name]=data
    edits=candidate(originals)
    for f,data in edits.items():
        if sha(data)!=record["after"][f]:
            raise RuntimeError("Candidate has drifted "+f)
    operations=[CommitOperationAdd(path_in_repo=f,path_or_fileobj=io.BytesIO(data))
                for f,data in edits.items()]
    commit=api.create_commit(repo_id=SPACE,repo_type="space",
             operations=operations,parent_commit=rev,
             commit_message="feat(§C): original remixes, parodies and lyric remaster QA")
    newrev=getattr(commit,"oid",None) or api.repo_info(SPACE,repo_type="space").sha
    try:
        for f,data in edits.items():
            actual=Path(hf_hub_download(SPACE,f,repo_type="space",revision=newrev,token=token)).read_bytes()
            if actual!=data:raise RuntimeError("Published file content differs "+f)
    except Exception:
        if api.repo_info(SPACE,repo_type="space").sha==newrev:
            from huggingface_hub import CommitOperationDelete
            operations=[CommitOperationAdd(path_in_repo=f,path_or_fileobj=io.BytesIO(data))
                        for f,data in originals.items()]
            operations.append(CommitOperationDelete(path_in_repo=HELPER))
            operations.append(CommitOperationDelete(path_in_repo=STOP))
            api.create_commit(repo_id=SPACE,repo_type="space",operations=operations,
                              parent_commit=newrev,
                              commit_message="rollback(§C): restore exact music files after verification failure")
        raise
    print("MUSIC_TRANSFORM_PUBLISHED",json.dumps(
         {"before":rev,"after":newrev,"paths":list(edits),"verified":True}),flush=True)

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("mode",choices=("snapshot","publish"))
    args=cli.parse_args()
    if args.mode=="snapshot":snapshot()
    else:publish()
