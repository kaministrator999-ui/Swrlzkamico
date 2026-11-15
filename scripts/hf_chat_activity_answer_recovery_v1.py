#!/usr/bin/env python3
"""Guarded §C existing-HF-Space source patch: event-backed narration + sourced answer continuation.

The exact live Hugging Face revision is source of truth. No repo-local HTML
snapshot is silently published. Deploy only with an explicit gated CI request.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from huggingface_hub import CommitOperationAdd, CommitOperationDelete, HfApi, hf_hub_download

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
ENGINE = "lfm2_700m_engine.py"
UI = "chat/§wyrlz/index.html"
HELPER = "api/response_limit_recovery.py"
FILES = (ENGINE, UI, HELPER)
ENGINE_MARKER = "swrlz-research-answer-limit-recovery-v1"
UI_MARKER = "swrlz-event-backed-work-narration-v1"
OUT = Path("swrlz-activity-answer-recovery-snapshot")
HEADERS = {"User-Agent": "SWRLZ-Event-Backed-Release/1",
           "Cache-Control": "no-cache"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"SOURCE_DRIFT_{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


BRIEF_OLD = '''    if source_change_mode:
        # Keep source/plan tokens available and bypass ordinary response-shape'''
BRIEF_NEW = '''    # swrlz-research-answer-limit-recovery-v1: let the model finish a
    # factual comparison before the reserved output window is exhausted.
    if (isinstance(payload.get("onlineContext"), dict)
            and int(payload["onlineContext"].get("resultCount") or 0) > 0
            and not programming.get("codingTask") and not source_change_mode):
        system+=(
            "\\nSOURCED FACTUAL RESPONSE LENGTH: Answer the current question directly "
            "using the supplied evidence. Prefer a compact, accurate comparison "
            "with release dates and the main differences. Usually finish in "
            "200-300 words. Do not pad with generic explanations. End the answer "
            "normally before the response token budget is exhausted."
        )
    if source_change_mode:
        # Keep source/plan tokens available and bypass ordinary response-shape'''

STREAM_OLD = '''            attempt_ended=time.perf_counter()
            candidate_text="".join(generated_parts)'''
STREAM_NEW = '''            # swrlz-research-answer-limit-recovery-v1:
            # Only an observed length finish on a sourced ordinary answer
            # qualifies. Preserve already streamed deltas and all evidence.
            # Code/edits and longform retain their existing separate contracts.
            from api.response_limit_recovery import (
                should_continue_research as _should_continue_research_v1,
                continuation_prompt as _continuation_prompt_v1,
                trim_overlap as _trim_answer_overlap_v1,
            )
            continuation_segments=0
            while (continuation_segments<2 and generated_parts
                   and _should_continue_research_v1(
                       str(stream_observation.get("finishReason") or ""),
                       payload, programming, source_change_mode,
                       bool(longform_target))):
                prior_text="".join(generated_parts)
                follow_messages=list(messages)+[
                    {"role":"assistant","content":prior_text[-1800:]},
                    {"role":"user","content":_continuation_prompt_v1()},
                ]
                room=CONTEXT_TOKENS-_token_count(model,follow_messages)-CONTEXT_SAFETY_TOKENS
                more_tokens=min(640,room)
                if more_tokens<256:
                    yield {"type":"STATUS","phase":"RESPONSE_CONTINUATION_UNAVAILABLE",
                           "reason":"Insufficient reserved context for safe continuation"}
                    break
                continuation_segments+=1
                yield {"type":"STATUS","phase":"RESPONSE_CONTINUING",
                       "reason":"The sourced answer reached its first output segment; finishing the answer without restarting"}
                follow_observation={"finishReason":None,"requestedMaxTokens":more_tokens}
                follow_parts=[]
                for follow_chunk in model.create_chat_completion(
                        messages=follow_messages,max_tokens=more_tokens,
                        temperature=min(0.30,temperature),stream=True):
                    observe_completion_chunk(follow_observation,follow_chunk)
                    choices=follow_chunk.get("choices") or []
                    follow_delta=(choices[0].get("delta") or {}).get("content") if choices else None
                    if follow_delta:follow_parts.append(str(follow_delta))
                appended=_trim_answer_overlap_v1(prior_text,"".join(follow_parts))
                if appended:
                    generated_parts.append(appended)
                    yield {"type":"DELTA","text":appended}
                follow_finish=str(follow_observation.get("finishReason") or "")
                if follow_finish=="stop" and appended.strip():
                    stream_observation["finishReason"]="stop"
                    yield {"type":"STATUS","phase":"RESPONSE_CONTINUATION_COMPLETED",
                           "reason":"The model completed the remaining sourced answer"}
                    break
                # Preserve observed length; do not report unverified completion.
                stream_observation["finishReason"]="length"
            stream_observation["continuationSegments"]=continuation_segments
            attempt_ended=time.perf_counter()
            candidate_text="".join(generated_parts)'''


def patch_engine(original: bytes) -> bytes:
    source = original.decode("utf-8")
    if ENGINE_MARKER in source:
        raise RuntimeError("Engine already contains the scoped repair")
    source = once(source, BRIEF_OLD, BRIEF_NEW, "answer_length_policy")
    source = once(source, STREAM_OLD, STREAM_NEW, "stream_continuation")
    ast.parse(source, filename=ENGINE)
    if source.count(ENGINE_MARKER) != 2:
        raise RuntimeError("Engine feature marker count drift")
    return source.encode("utf-8")


NARRATION_OLD = '''      const renderActivityTimelineV238=(messageNode,trace,options={})=>{'''
NARRATION_NEW = '''      // swrlz-event-backed-work-narration-v1
      // Deterministic presentation only. Never ask the model to invent tool
      // execution or research progress; only describe real Station receipts.
      const activityNarrationV1=(events,{active=false,streaming=false,failed=false}={})=>{
        if(!active){
          return {title:failed?"Response needs attention":"Activity recorded",
                  detail:"Recorded work steps can be inspected in the activity log."};
        }
        const phases=new Set(events.map(item=>String(item?.phase||"").toUpperCase()));
        const has=phase=>phases.has(phase);
        if(has("RESPONSE_CONTINUING"))
          return {title:"Finishing the answer",detail:"I reached a response segment limit, so I'm continuing from the existing answer rather than starting over."};
        if(has("RESPONSE_CONTINUATION_UNAVAILABLE"))
          return {title:"Checking response limits",detail:"The current context has too little space to continue safely; I'll report the result rather than invent completion."};
        if(has("RESEARCH_READY"))
          return {title:streaming?"Writing with sources":"Research complete",
                  detail:streaming?"I found relevant public sources and I'm using them to answer.":"I found relevant sources. I'm preparing the comparison."};
        if(has("RESEARCH_UNAVAILABLE"))
          return {title:"Research unavailable",detail:"I couldn't retrieve relevant public sources for this request."};
        if(has("SOURCE_FETCH_COMPLETE")||has("ONLINE_RESEARCH"))
          return {title:streaming?"Writing from research":"Checking research",
                  detail:"I've recorded the source-retrieval result and I'm preparing the answer."};
        if(has("SOURCE_FETCH_STARTED")||has("SEARCH_STARTED")||has("RESEARCH_STARTED"))
          return {title:"Checking sources",detail:"I'm looking through public sources for the information you requested."};
        if(has("CODE_DRAFT_CHECKPOINTED")||has("RESUMING_SAVED_CODE"))
          return {title:"Continuing saved code",detail:"I'm continuing from the retained code checkpoint, not generating a replacement file."};
        if(has("CODE_DRAFT_STREAMING"))
          return {title:"Writing code",detail:"I'm producing an unverified draft. It still needs validation before it can be called complete."};
        if(has("GITHUB_CONTEXT_READY")||has("PROJECT_CONTEXT_READY"))
          return {title:"Using project context",detail:"I have recorded project or repository context for this response."};
        if([...phases].some(phase=>phase.startsWith("GITHUB_TOOL_")||phase==="GITHUB_READ_EVIDENCE"))
          return {title:"Checking GitHub",detail:"I'm reading the repository information exposed by the connected tool."};
        if(has("CROSS_CONVERSATION_REVIEW"))
          return {title:"Checking conversation context",detail:"I'm checking the conversation context the server made available."};
        return {title:streaming?"Writing the response":"Preparing the response",
                detail:streaming?"I'm putting the answer together.":"I'm preparing the response."};
      };
      const renderActivityTimelineV238=(messageNode,trace,options={})=>{'''

TITLE_OLD = '''        const heading=isFailure?"Response needs attention":
          active&&options.streaming?"Writing the response":
          active?activityNameV238(latest?.phase||"CONNECTING"):"Activity recorded";
        const title=wrapper.querySelector(".station-activity-title");'''
TITLE_NEW = '''        const narration=activityNarrationV1(events,{
          active,streaming:!!options.streaming,failed:isFailure});
        const heading=narration.title;
        const title=wrapper.querySelector(".station-activity-title");'''

SUB_OLD = '''        wrapper.querySelector(".station-activity-sub").textContent=(active?"Live Station activity":"Saved response activity")+" · "+events.length+" step"+(events.length===1?"":"s")+(omitted?" · "+omitted+" earlier omitted":"");'''
SUB_NEW = '''        wrapper.querySelector(".station-activity-sub").textContent=
          (active?narration.detail+" · ":"Saved response activity · ")+events.length+" observed step"+(events.length===1?"":"s")+(omitted?" · "+omitted+" earlier omitted":"");'''


def patch_ui(original: bytes) -> bytes:
    source = original.decode("utf-8")
    if UI_MARKER in source:
        raise RuntimeError("UI already contains scoped narration")
    source = once(source, NARRATION_OLD, NARRATION_NEW, "activity_function")
    source = once(source, TITLE_OLD, TITLE_NEW, "activity_heading")
    source = once(source, SUB_OLD, SUB_NEW, "activity_detail")
    if source.count(UI_MARKER) != 1:
        raise RuntimeError("UI feature marker drift")
    return source.encode("utf-8")


def source_revision(api: HfApi) -> str:
    return api.repo_info(SPACE, repo_type="space").sha


def source_bytes(api: HfApi, path: str, revision: str) -> bytes:
    return Path(hf_hub_download(SPACE,path,revision=revision,repo_type="space",
                                token=api.token)).read_bytes()


def build_candidate(api: HfApi, folder: Path):
    folder.mkdir(parents=True,exist_ok=True)
    before=source_revision(api)
    live_files=set(api.list_repo_files(SPACE,repo_type="space",revision=before))
    if HELPER in live_files:
        raise RuntimeError("Unexpected existing helper path, refusing overwrite")
    original_engine=source_bytes(api,ENGINE,before)
    original_ui=source_bytes(api,UI,before)
    changed={ENGINE:patch_engine(original_engine),UI:patch_ui(original_ui),
             HELPER:(Path(__file__).resolve().parents[1]/HELPER).read_bytes()}
    ast.parse(changed[HELPER].decode("utf-8"),filename=HELPER)
    orig={ENGINE:original_engine,UI:original_ui}
    for path,blob in orig.items():
        target=folder/"before"/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(blob)
    for path,blob in changed.items():
        target=folder/"candidate"/path
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(blob)
    receipt={"space":SPACE,"sourceRevision":before,"candidate":{p:digest(d) for p,d in changed.items()},
             "original":{p:digest(d) for p,d in orig.items()},
             "files":list(FILES),"status":"PREPARED_NOT_DEPLOYED"}
    (folder/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")
    print("SWRLZ_ACTIVITY_RECOVERY_CANDIDATE "+json.dumps(receipt),flush=True)
    return receipt


def verify_runtime(api: HfApi, revision: str, deadline_seconds: int = 960):
    started=time.monotonic()
    attempts=0
    while time.monotonic()-started<deadline_seconds:
        if source_revision(api)!=revision:raise RuntimeError("Concurrent Space source update detected")
        attempts+=1
        stage=None
        actual=None
        try:
            req=urllib.request.Request("https://huggingface.co/api/spaces/"+SPACE,headers=HEADERS)
            with urllib.request.urlopen(req,timeout=15) as response:
                public=json.load(response)
            runtime=public.get("runtime") or {}
            stage=runtime.get("stage");actual=runtime.get("sha")
            if stage=="RUNNING" and actual==revision:
                with urllib.request.urlopen(
                    urllib.request.Request(BASE+"/api/hf/qwen35-ready",headers=HEADERS),
                    timeout=20) as response:
                    ready=json.load(response)
                if ready.get("ready") is True and ready.get("model")=="qwen3.5-9b":
                    print("SWRLZ_ACTIVITY_RUNTIME_READY "+json.dumps(
                        {"revision":revision,"stage":stage,"attempts":attempts}),flush=True)
                    return
        except (ValueError,OSError,urllib.error.URLError):
            pass
        if attempts%6==0:
            print("SWRLZ_ACTIVITY_RUNTIME_WARMING "+json.dumps({
                "attempts":attempts,"target":revision,"running":actual,"stage":stage}),flush=True)
        time.sleep(12)
    raise RuntimeError("Exact running 9B revision did not become ready")


def accepted_live_turn(prompt: str):
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    rid=str(uuid.uuid4())
    thread="swrlz-activity-recovery-test-"+str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,"threadId":thread,"requestId":rid,
          "profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",
        data=json.dumps(body).encode(),method="POST",
        headers={**HEADERS,"Content-Type":"application/json"})
    with opener.open(req,timeout=50) as response:
        if response.status!=202:raise RuntimeError("Synthetic send not accepted")
    url=BASE+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid})
    phases=[];chunks=[];terminal=None;start=time.monotonic()
    with opener.open(urllib.request.Request(url,headers=HEADERS),timeout=360) as response:
        for raw in response:
            if time.monotonic()-start>360:raise RuntimeError("Live response stream time budget exceeded")
            try:event=json.loads(raw)
            except (UnicodeError,ValueError):continue
            kind=event.get("type")
            if kind=="STATUS":phases.append(event.get("phase"))
            if kind=="DELTA":chunks.append(str(event.get("text") or ""))
            if kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    text="".join(chunks)
    outcome={"terminal":terminal,"characters":len(text),"duration":round(time.monotonic()-start,2),
             "researchReady":"RESEARCH_READY" in phases,
             "autoContinued":"RESPONSE_CONTINUING" in phases}
    print("SWRLZ_ACTIVITY_RECOVERY_LIVE_TURN "+json.dumps(outcome),flush=True)
    if terminal not in ("COMPLETE","COMPLETED") or len(text)<50 or "diablo" not in text.lower():
        raise RuntimeError("Live factual response failed to complete and address the topic")
    if not outcome["researchReady"]:
        raise RuntimeError("The live factual test did not use selective research")


def validate_live_ui():
    req=urllib.request.Request(BASE+"/",headers=HEADERS)
    with urllib.request.urlopen(req,timeout=30) as response:
        html=response.read(2_000_000).decode("utf-8","replace")
    if UI_MARKER not in html:
        raise RuntimeError("New activity narration UI marker not served")
    print("SWRLZ_ACTIVITY_UI_LIVE "+json.dumps({"marker":UI_MARKER,"present":True}),flush=True)


def publish(api: HfApi, receipt: dict, folder: Path):
    if os.environ.get("SWRLZ_ACTIVITY_ANSWER_RECOVERY_DEPLOY_APPROVED")!="1":
        raise RuntimeError("Deployment requires explicit owner release approval")
    before=receipt["sourceRevision"]
    if source_revision(api)!=before:raise RuntimeError("Source moved after staging")
    operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=str(folder/"candidate"/p))
                for p in FILES]
    result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=before,
                             operations=operations,
                             commit_message="§C: event-backed conversational activity and bounded research answer recovery")
    published=str(result.oid)
    receipt.update({"publishedRevision":published,"status":"PUBLISHED_ACCEPTANCE_PENDING"})
    (folder/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")
    try:
        if source_revision(api)!=published:raise RuntimeError("Concurrent Space write")
        for path,expected in receipt["candidate"].items():
            if digest(source_bytes(api,path,published))!=expected:
                raise RuntimeError("Published byte verification failed: "+path)
        verify_runtime(api,published)
        validate_live_ui()
        accepted_live_turn("Was Diablo II Classic released before Lord of Destruction? Research both versions and explain the differences.")
        receipt["status"]="LIVE_VERIFIED"
        print("SWRLZ_ACTIVITY_RECOVERY_LIVE_ACCEPTED "+json.dumps(
            {"space":SPACE,"published":published,"fileCount":len(FILES)}),flush=True)
    except BaseException:
        print("SWRLZ_ACTIVITY_RECOVERY_REJECTED_ATTEMPT_ROLLBACK",flush=True)
        if source_revision(api)!=published:
            raise RuntimeError("Concurrent Space source change: rollback unsafe") from None
        rollback_operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=str(folder/"before"/p))
                             for p in (ENGINE,UI)]
        rollback_operations.append(CommitOperationDelete(path_in_repo=HELPER))
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
                operations=rollback_operations,
                commit_message="Rollback §C activity and sourced answer recovery to exact originals")
        restored=str(result.oid)
        if source_revision(api)!=restored:raise RuntimeError("Rollback revision mismatch")
        for path,expected in receipt["original"].items():
            if digest(source_bytes(api,path,restored))!=expected:
                raise RuntimeError("Original source rollback integrity check failed: "+path)
        receipt.update({"status":"ROLLED_BACK","restoredRevision":restored})
        print("SWRLZ_ACTIVITY_RECOVERY_ROLLED_BACK "+json.dumps(
            {"published":published,"restored":restored}),flush=True)
        raise
    finally:
        (folder/"receipt.json").write_text(json.dumps(receipt,indent=2),"utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default=str(OUT))
    parser.add_argument("--deploy",action="store_true")
    args=parser.parse_args()
    token=os.environ.get("HF_TOKEN") or None
    api=HfApi(token=token)
    receipt=build_candidate(api,Path(args.out))
    if args.deploy:
        if not token:raise RuntimeError("Existing owner Hugging Face credential required")
        publish(api,receipt,Path(args.out))


if __name__=="__main__":
    main()
