#!/usr/bin/env python3
"""§C code-generation lifecycle fix: foreground/background sync, real Stop, bounded decode.

Uses exact production source as authority. No model, weights, thread, GitHub,
§E editor, or stored project-format change. Preflight restores prior bytes
under rollback guard if any post-deployment acceptance step fails.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,subprocess,sys,tempfile,time,urllib.parse,urllib.request,http.cookiejar,uuid
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
ENGINE="qwen_coder_engine.py"
STATION="station.py"
UI="chat/§wyrlz/index.html"
FILES=(ENGINE,STATION,UI)
BACKUP=Path("swrlz-coding-lifecycle-original")
TAG="swrlz-coding-lifecycle-v1"
HEAD={"User-Agent":"Swyrlz-Coding-Lifecycle-Acceptance","Cache-Control":"no-cache"}

def record(phase,**data):
    print("CODING_LIFECYCLE",json.dumps({"phase":phase,**data},sort_keys=True,ensure_ascii=False),flush=True)
def hash_bytes(blob):return hashlib.sha256(blob).hexdigest()
def exactly(source,old,new,label):
    n=source.count(old)
    if n!=1:raise RuntimeError("SOURCE_DRIFT "+label+" count="+str(n))
    return source.replace(old,new,1)

def patch_engine(raw):
    source=raw.decode("utf-8")
    if TAG in source:raise RuntimeError("Already integrated")
    tree=ast.parse(source)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_swrlz_code_candidate_preview")
    old=ast.get_source_segment(source,fn)
    new=old
    new=exactly(new,"allow_continue=False,seed_text=''):",
        "allow_continue=False,seed_text='',cancel_check=None):","decode cancel arg")
    new=exactly(new,"    started=time.perf_counter()\n    first_token_at=None",
        "    # swrlz-coding-lifecycle-v1: soft per-turn CPU budget, checked at\n"
        "    # every yielded native decode chunk rather than between 4096-token segments.\n"
        "    started=time.perf_counter()\n"
        "    cancel_fn=cancel_check if callable(cancel_check) else (lambda:False)\n"
        "    native_budget_seconds=240\n"
        "    first_token_at=None","decode budget/cancel")
    new=exactly(new,"    for segment in range(1,max_segments+1):",
        "    for segment in range(1,max_segments+1):\n"
        "        if cancel_fn():\n"
        "            return ''.join(parts),{'finishReason':'cancelled',\n"
        "                'continuationSegments':segment_count,'durationMs':round((time.perf_counter()-started)*1000,3)}",
        "cancel segment boundary")
    new=exactly(new,"if segment>1 and time.perf_counter()-started>540:break",
        "if segment>1 and time.perf_counter()-started>=native_budget_seconds:break",
        "short per-turn segment gate")
    new=exactly(new,'        pending=""\n        for chunk in model.create_chat_completion(',
        '        pending=""\n        pause_at_budget=False\n        for chunk in model.create_chat_completion(',
        "native budget pending")
    new=exactly(new,"        ):\n            observe_completion_chunk(part_observation,chunk)",
        "        ):\n"
        "            if cancel_fn():\n"
        "                return ''.join(parts),{'finishReason':'cancelled',\n"
        "                    'continuationSegments':segment_count,'durationMs':round((time.perf_counter()-started)*1000,3)}\n"
        "            if time.perf_counter()-started>=native_budget_seconds:\n"
        "                part_observation['finishReason']='length'\n"
        "                pause_at_budget=True\n"
        "                break\n"
        "            observe_completion_chunk(part_observation,chunk)",
        "native token cancellation and timeout")
    new=exactly(new,
        "        observed.append(part_observation)\n        if part_observation.get(\"finishReason\")!=\"length\":break",
        "        observed.append(part_observation)\n"
        "        if pause_at_budget:break\n"
        "        if part_observation.get(\"finishReason\")!=\"length\":break",
        "stop after partial segment")
    # Streaming small code tokens individually makes Station update the
    # same long snapshot thousands of times. Coalesce frequent chunks while
    # preserving the exact byte-for-byte generated candidate.
    new=exactly(new,'    first_token_at=None\n    parts=[seed_text] if seed_text else []',
        '    first_token_at=None\n    preview_buffer=""\n    preview_last_flush=started\n    parts=[seed_text] if seed_text else []',
        "preview event coalescing")
    new=exactly(new,
        '            if addition:\n                parts.append(addition)\n                yield {"type":"CANDIDATE_PREVIEW_DELTA","text":addition,"attempt":attempt}\n        if pending:',
        '            if addition:\n                parts.append(addition)\n                preview_buffer+=addition\n                if len(preview_buffer)>=128 or time.perf_counter()-preview_last_flush>=0.35:\n                    yield {"type":"CANDIDATE_PREVIEW_DELTA","text":preview_buffer,"attempt":attempt}\n                    preview_buffer=""\n                    preview_last_flush=time.perf_counter()\n        if pending:',
        "coalesce native token previews")
    new=exactly(new,
        '        if pending:\n            addition=_swrlz_trim_code_resume("".join(parts),pending)\n            if addition:\n                parts.append(addition)\n                yield {"type":"CANDIDATE_PREVIEW_DELTA","text":addition,"attempt":attempt}',
        '        if pending:\n            addition=_swrlz_trim_code_resume("".join(parts),pending)\n            if addition:\n                parts.append(addition)\n                preview_buffer+=addition',
        "buffer continuation tail")
    new=exactly(new,
        '        observed.append(part_observation)\n        if part_observation.get("finishReason")!="length":break',
        '        if preview_buffer:\n            yield {"type":"CANDIDATE_PREVIEW_DELTA","text":preview_buffer,"attempt":attempt}\n            preview_buffer=""\n            preview_last_flush=time.perf_counter()\n        observed.append(part_observation)\n        if part_observation.get("finishReason")!="length":break',
        "flush preview at segment boundary")
    # Shorten repeated CPU prefill on resumed work; the full saved source
    # remains held by the server for final delivery and SHA validation.
    new=exactly(new,
        '    next_messages=_swrlz_resume_tail_messages(seed_text) if seed_text else messages',
        '    next_messages=_swrlz_resume_tail_messages(seed_text) if seed_text else messages',
        "noop bounded resume sanity")
    source=exactly(source,old,new,"exact code preview helper")
    # This callback is an in-memory capability supplied solely by Station.
    key='''    with _lock:
        mode="RESPONSE MODE: GITHUB-SOURCE-JSON" if source_change_mode else _response_mode(prompt,programming)'''
    val='''    cancel_check=payload.get("_cancelCheck") if callable(payload.get("_cancelCheck")) else (lambda:False)
    with _lock:
        mode="RESPONSE MODE: GITHUB-SOURCE-JSON" if source_change_mode else _response_mode(prompt,programming)'''
    source=exactly(source,key,val,"main coding signal binding")
    # Bound all three full-candidate stages and persist the current candidate
    # instead of allowing the next stage to regenerate after cancellation.
    old_args="allow_continue=auto_resume_existing_source)"
    count=source.count(old_args)
    if count!=3:raise RuntimeError("Expected three guarded code stages, got "+str(count))
    source=source.replace(old_args,"allow_continue=auto_resume_existing_source,cancel_check=cancel_check)")
    for original,new_line,label in [
        ('candidate_text,timing=yield from _swrlz_code_candidate_preview(model,messages,response_tokens,temperature,1,allow_continue=auto_resume_existing_source,cancel_check=cancel_check)\n            candidate_check',
         'candidate_text,timing=yield from _swrlz_code_candidate_preview(model,messages,response_tokens,temperature,1,allow_continue=auto_resume_existing_source,cancel_check=cancel_check)\n            if timing.get("finishReason")=="cancelled":return\n            candidate_check',"initial code cancel"),
        ('retry_text,retry_timing=yield from _swrlz_code_candidate_preview(model,retry_messages,retry_tokens,min(0.45,temperature+0.10),2,allow_continue=auto_resume_existing_source,cancel_check=cancel_check)\n                if retry_text.strip():',
         'retry_text,retry_timing=yield from _swrlz_code_candidate_preview(model,retry_messages,retry_tokens,min(0.45,temperature+0.10),2,allow_continue=auto_resume_existing_source,cancel_check=cancel_check)\n                if retry_timing.get("finishReason")=="cancelled":return\n                if retry_text.strip():',"retry code cancel"),
        ('third_text,third_timing=yield from _swrlz_code_candidate_preview(model,final_messages,final_tokens,min(0.50,temperature+0.15),3,allow_continue=auto_resume_existing_source,cancel_check=cancel_check)\n                    if third_text.strip():',
         'third_text,third_timing=yield from _swrlz_code_candidate_preview(model,final_messages,final_tokens,min(0.50,temperature+0.15),3,allow_continue=auto_resume_existing_source,cancel_check=cancel_check)\n                    if third_timing.get("finishReason")=="cancelled":return\n                    if third_text.strip():',"final code cancel"),
    ]:
        source=exactly(source,original,new_line,label)
    source=exactly(source,"allow_continue=True,seed_text=source)",
              'allow_continue=True,seed_text=source,cancel_check=payload.get("_cancelCheck"))',
              "resumed code native stop")
    # Correctly release the model when a saved-source continuation is cancelled.
    source=exactly(source,
              '        completion=completion_validation(\n            _candidate_structure_check(draft,programming,history),timing)',
              '        if timing.get("finishReason")=="cancelled":return\n'
              '        completion=completion_validation(\n'
              '            _candidate_structure_check(draft,programming,history),timing)',
              "saved code cancel")
    # The short JSON patch path was blocking for up to 2048 output tokens.
    # Streaming lets Stop interrupt at native token boundaries.
    tree=ast.parse(source)
    target=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_swrlz_patch_candidate_once")
    old_patch=ast.get_source_segment(source,target)
    new_patch=old_patch
    new_patch=exactly(new_patch,"def _swrlz_patch_candidate_once(model,source,check,original):",
              "def _swrlz_patch_candidate_once(model,source,check,original,cancel_check=None):",
              "small patch cancel arg")
    new_patch=exactly(new_patch,"allowance=min(2048,CONTEXT_TOKENS",
              "allowance=min(1024,CONTEXT_TOKENS","focused repair token budget")
    beginning=new_patch.index("    native=model.create_chat_completion(")
    ending=new_patch.index("    updated,receipt=_swrlz_apply_patch(source,raw)",beginning)
    block='''    observation={"finishReason":None}
    parts=[]
    for chunk in model.create_chat_completion(
        messages=messages,max_tokens=allowance,temperature=0.13,stream=True
    ):
        if callable(cancel_check) and cancel_check():
            raise _SwrlzPatchError("CANCEL_REQUESTED","User stopped coding")
        if time.perf_counter()-started>=115:
            raise _SwrlzPatchError("REPAIR_BUDGET","Focused repair exceeded its time budget")
        observe_completion_chunk(observation,chunk)
        choices=chunk.get("choices") or []
        delta=(choices[0].get("delta") or {}).get("content") if choices else None
        if delta:parts.append(str(delta))
    finish=str(observation.get("finishReason") or "")
    if finish!="stop":
        raise _SwrlzPatchError("PATCH_TRUNCATED","Incomplete native repair proposal")
    raw="".join(parts)
'''
    new_patch=new_patch[:beginning]+block+new_patch[ending:]
    source=exactly(source,old_patch,new_patch,"short streaming targeted repair")
    # Both normal and saved-code repairs use the process-only signal.
    args="model,candidate_text,candidate_check,prompt)"
    source=exactly(source,args,"model,candidate_text,candidate_check,prompt,cancel_check=cancel_check)",
                   "live repair cancellation")
    args="model,draft,completion,original)"
    source=exactly(source,args,'model,draft,completion,original,cancel_check=payload.get("_cancelCheck"))',
                   "checkpoint repair cancellation")
    # Repair rejection after cancel ends the generator; Station finalizes the
    # request as CANCELLED instead of checkpointing it as a new code task.
    anchor='''                        except _SwrlzPatchError as exc:
                            yield {"type":"STATUS","phase":"CODE_REPAIR_PROPOSAL_REJECTED",'''
    updated='''                        except _SwrlzPatchError as exc:
                            if exc.code=="CANCEL_REQUESTED":return
                            yield {"type":"STATUS","phase":"CODE_REPAIR_PROPOSAL_REJECTED",'''
    source=exactly(source,anchor,updated,"main repair cancellation")
    anchor='''                except _SwrlzPatchError as exc:
                    yield {"type":"STATUS","phase":"CODE_REPAIR_PROPOSAL_REJECTED",'''
    updated='''                except _SwrlzPatchError as exc:
                    if exc.code=="CANCEL_REQUESTED":return
                    yield {"type":"STATUS","phase":"CODE_REPAIR_PROPOSAL_REJECTED",'''
    source=exactly(source,anchor,updated,"saved repair cancellation")
    ast.parse(source,filename=ENGINE)
    return source.encode("utf-8")

def patch_station(raw):
    text=raw.decode("utf-8")
    if TAG in text:raise RuntimeError("Already integrated Station")
    # No client or model can set this; it is created from exact same-user request
    # inside the authoritative Station worker.
    anchor='''    try:
        if forge_context is None and model_id=="stock"'''
    replacement='''    # swrlz-coding-lifecycle-v1: process-private cancellation capability.
    def _cancel_from_worker():
        with _lock:
            current=s.get("activeGeneration")
            return (not current or current.get("requestId")!=request_id
                    or bool(current.get("cancelRequested")))
    payload["_cancelCheck"]=_cancel_from_worker
    try:
        if forge_context is None and model_id=="stock"'''
    text=exactly(text,anchor,replacement,"server native cancel capability")
    anchor='''        if cancelled:
            cancelled_usage=finish_resource_usage("CANCELLED")'''
    replacement='''        # A native model generator may stop without yielding another event.
        # Still honor a request that was explicitly cancelled by this session.
        with _lock:
            final_active=s.get("activeGeneration")
            if final_active and final_active.get("requestId")==request_id and final_active.get("cancelRequested"):
                cancelled=True
        if cancelled:
            cancelled_usage=finish_resource_usage("CANCELLED")'''
    text=exactly(text,anchor,replacement,"cancel when native stream exits")
    anchor='''                if kind=="CANDIDATE_PREVIEW_DELTA":
                    part=str(event.get("text") or "")
                    if len(str(g.get("previewText") or ""))+len(part)<=131072:
                        g["previewText"]=str(g.get("previewText") or "")+part
                        g["previewAttempt"]=int(event.get("attempt") or 1)'''
    replacement='''                if kind=="CANDIDATE_PREVIEW_DELTA":
                    part=str(event.get("text") or "")
                    if len(str(g.get("previewText") or ""))+len(part)<=131072:
                        g["previewText"]=str(g.get("previewText") or "")+part
                        g["previewAttempt"]=int(event.get("attempt") or 1)
                        now_ms=int(time.time()*1000)
                        g["lastCodeProgressAtUnixMs"]=now_ms
                        # Update a visible milestone occasionally, not once per token.
                        if now_ms-int(g.get("lastCodeProgressStatusAtUnixMs") or 0)>=6000:
                            g["lastCodeProgressStatusAtUnixMs"]=now_ms
                            g["status"].append({"phase":"CODE_DRAFT_STREAMING",
                                "reason":"Code output progressing ("+str(len(g["previewText"]))+" chars)",
                                "atUnixMs":now_ms})'''
    text=exactly(text,anchor,replacement,"server code progress and freshness")
    # The stream can replay its own initial content on reconnect while the
    # browser has already imported a newer sync snapshot. Expose UTF-16 code
    # unit offsets, matching JS string indexing, to deduplicate.
    anchor='''            if len(preview_now)>len(sent_preview) and not str(g.get("text") or ""):
                draft_delta=preview_now[len(sent_preview):]
                sent_preview=preview_now
                yield json.dumps({"type":"CANDIDATE_PREVIEW_DELTA","text":draft_delta,'''
    replacement='''            if len(preview_now)>len(sent_preview) and not str(g.get("text") or ""):
                offset_utf16=len(sent_preview.encode("utf-16-le"))//2
                draft_delta=preview_now[len(sent_preview):]
                sent_preview=preview_now
                yield json.dumps({"type":"CANDIDATE_PREVIEW_DELTA","text":draft_delta,
                                  "offsetUtf16":offset_utf16,'''
    text=exactly(text,anchor,replacement,"preview offset on reconnect")
    anchor='''            if len(text_now)>len(sent_text):
                delta=text_now[len(sent_text):]
                sent_text=text_now
                yield json.dumps({"type":"DELTA","text":delta,"seq":int(g.get("lastSeq") or 0),"requestId":rid},ensure_ascii=False)+"\\n"'''
    replacement='''            if len(text_now)>len(sent_text):
                offset_utf16=len(sent_text.encode("utf-16-le"))//2
                delta=text_now[len(sent_text):]
                sent_text=text_now
                yield json.dumps({"type":"DELTA","text":delta,"offsetUtf16":offset_utf16,
                                  "seq":int(g.get("lastSeq") or 0),"requestId":rid},ensure_ascii=False)+"\\n"'''
    text=exactly(text,anchor,replacement,"accepted response offset on reconnect")
    # A verified Continue code command starts with the exact previous source
    # visible in the new generation, not an empty provisional code box.
    # This remains unverified and account/thread scoped.
    seed_anchor='''    payload={"requestId":rid,"threadId":tid,"prompt":_inference_prompt_after_vision(prompt),'''
    seed_replacement='''        if resume_code is not None:
            saved_source=str(resume_code.get("source") or "")
            if saved_source and len(saved_source.encode("utf-8"))<=240*1024:
                active=s["activeGeneration"]
                active["previewText"]=saved_source
                active["codeDraftCheckpoint"]={
                    "sourceSha256":resume_code["sourceSha256"],
                    "bytes":len(saved_source.encode("utf-8")),
                    "segments":int(resume_code.get("segmentsCompleted") or 0),
                    "resuming":True,
                    "verificationState":"UNVERIFIED_INCOMPLETE"}
                active["lastCodeProgressAtUnixMs"]=now_ms
                active["status"].append({"phase":"RESUMING_SAVED_CODE",
                    "reason":"Restored full saved draft; model is extending its source",
                    "atUnixMs":now_ms})
    payload={"requestId":rid,"threadId":tid,"prompt":_inference_prompt_after_vision(prompt),'''
    text=exactly(text,seed_anchor,seed_replacement,"seed saved draft in active Station snapshot")
    text=exactly(text,
        'if len(str(g.get("previewText") or ""))+len(part)<=131072:',
        'if len(str(g.get("previewText") or ""))+len(part)<=262144:',
        "allow full 240KiB saved source in provisional preview")
    text=exactly(text,
        '                        target.pop("pendingCodeGeneration",None)\n                        g["status"].append',
        '                        target.pop("pendingCodeGeneration",None)\n                        g.pop("codeDraftCheckpoint",None)\n                        g["status"].append',
        "clear checkpoint preview metadata only when verified output completes")
    text=exactly(text,
        '                    delta=str(event.get("text") or "");text+=delta;g["text"]=text\n                    g["previewText"]=""',
        '                    delta=str(event.get("text") or "");text+=delta;g["text"]=text\n                    if not (g.get("codeDraftCheckpoint") and g["codeDraftCheckpoint"].get("verificationState")=="UNVERIFIED_INCOMPLETE"):\n                        g["previewText"]=""',
        "keep saved draft visible during paused explanatory response")
    ast.parse(text,filename=STATION)
    return text.encode("utf-8")

def patch_ui(raw):
    source=raw.decode("utf-8")
    if TAG in source:raise RuntimeError("Already integrated UI")
    anchor='''      const consumeGeneration = async (response,requestId,threadId,projectionEpoch) => {'''
    updated='''      // swrlz-coding-lifecycle-v1: an NDJSON stream may replay its
      // beginning after the authoritative server snapshot has advanced.
      // UTF-16 offsets allow overlap-safe merges even with emoji in code.
      const appendStationSourceDelta=(current,delta,offset)=>{
        const before=String(current||""),part=String(delta||"");
        if(!Number.isSafeInteger(offset)||offset<0)return before+part;
        if(before.length<offset)return null;
        const overlap=Math.min(before.length-offset,part.length);
        if(before.slice(offset,offset+overlap)!==part.slice(0,overlap))return null;
        return before+part.slice(overlap);
      };
      const consumeGeneration = async (response,requestId,threadId,projectionEpoch) => {'''
    source=exactly(source,anchor,updated,"UTF-16 sync merge function")
    anchor='''            stationGeneration.lastSeq=Number(event.seq||stationGeneration.lastSeq||0);'''
    replacement='''            stationGeneration.lastSeq=Math.max(Number(event.seq||0),Number(stationGeneration.lastSeq||0));'''
    source=exactly(source,anchor,replacement,"do not reverse stream seq on sync")
    anchor='''              stationGeneration.text=(stationGeneration.text||"")+deltaText;
              stationGeneration.previewText="";'''
    replacement='''              const merged=appendStationSourceDelta(stationGeneration.text,deltaText,event.offsetUtf16);
              if(merged===null){void syncStation(true);continue;}
              stationGeneration.text=merged;
              stationGeneration.previewText="";'''
    source=exactly(source,anchor,replacement,"accepted text replay-safe merge")
    anchor='''              stationGeneration.previewText=(stationGeneration.previewText||"")+String(event.text||"");
              stationGeneration.previewAttempt=Number(event.attempt||1);'''
    replacement='''              const merged=appendStationSourceDelta(stationGeneration.previewText,String(event.text||""),event.offsetUtf16);
              if(merged===null){void syncStation(true);continue;}
              stationGeneration.previewText=merged;
              stationGeneration.previewAttempt=Number(event.attempt||1);'''
    source=exactly(source,anchor,replacement,"draft replay-safe merge")
    # Keep the stream connected until the server acknowledges Stop. Closing
    # the browser stream first previously hid ongoing progress/terminal state.
    source=exactly(source,"if(performance.now()-lastTouchSend<1000)return;",
                         "if(performance.now()-lastTouchSend<350)return;",
                         "stop tap guard reduced")
    anchor='''          streamAbortController?.abort();
          await fetch("/api/lalm_station/cancel",{method:"POST",credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json"},body:JSON.stringify({requestId:rid})});
          if(projectionEpoch===accountProjectionEpoch)await syncStation();'''
    replacement='''          const result=await fetch("/api/lalm_station/cancel",{method:"POST",credentials:"same-origin",cache:"no-store",headers:{"Content-Type":"application/json"},body:JSON.stringify({requestId:rid})});
          const outcome=await result.json().catch(()=>({}));
          if(!result.ok||!outcome.ok)throw new Error("Stop was not acknowledged by Station");
          // Do not abort the response stream: retain the server's CANCELLED
          // receipt and do not mistake temporary browser suspension for a Stop.
          if(projectionEpoch===accountProjectionEpoch)await syncStation(true);'''
    source=exactly(source,anchor,replacement,"Stop authoritative receipt before leaving stream")
    source=exactly(source,
        '        const draftText=(!g.terminal&&!String(g.text||"").trim())\n          ?String(g.previewText||""):"";',
        '        const savedDraft=!!(g.codeDraftCheckpoint?.verificationState==="UNVERIFIED_INCOMPLETE");\n        const draftText=(savedDraft||(!g.terminal&&!String(g.text||"").trim()))\n          ?String(g.previewText||""):"";',
        "show saved code during continuation and after pause")
    source=exactly(source,
        '          const code=draftPanel.querySelector("pre");\n          if(code&&code.textContent!==draftText){\n            const follow=codeViewNearBottom(code);\n            code.textContent=draftText;\n            if(follow)code.scrollTop=code.scrollHeight;\n          }',
        '          const draftLabel=draftPanel.querySelector(".swrlz-code-draft-label");\n          if(draftLabel)draftLabel.textContent=savedDraft\n            ?(g.terminal?"Saved unverified code · Continue code to resume":"Saved draft · continuing · not yet verified")\n            :"Code draft · generating and validating · not saved";\n          const code=draftPanel.querySelector("pre");\n          if(code){\n            const shown=draftPanel._swrlzShownSource||"";\n            if(shown!==draftText){\n              const follow=codeViewNearBottom(code);\n              if(shown&&draftText.startsWith(shown)&&code.firstChild?.nodeType===Node.TEXT_NODE)\n                code.firstChild.appendData(draftText.slice(shown.length));\n              else code.textContent=draftText;\n              draftPanel._swrlzShownSource=draftText;\n              if(follow)code.scrollTop=code.scrollHeight;\n            }\n          }',
        "append only newly decoded code in draft box")
    return source.encode("utf-8")

def check_js(html):
    scripts=re.findall(r"<script\b([^>]*)>(.*?)</script\s*>",html,flags=re.I|re.S)
    checked=0
    with tempfile.TemporaryDirectory(prefix="swrlz-life-js-") as d:
        for i,(attrs,body) in enumerate(scripts):
            if not body.strip() or "application/json" in attrs or "application/ld+json" in attrs:continue
            path=Path(d)/("script"+str(i)+".js");path.write_text(body)
            proc=subprocess.run(["node","--check",str(path)],
                    stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
            if proc.returncode:raise RuntimeError("Chat UI JS syntax "+proc.stderr[-800:])
            checked+=1
    test='''const assert=require("assert");
      const appendStationSourceDelta=(current,delta,offset)=>{
        const before=String(current||""),part=String(delta||"");
        if(!Number.isSafeInteger(offset)||offset<0)return before+part;
        if(before.length<offset)return null;
        const overlap=Math.min(before.length-offset,part.length);
        if(before.slice(offset,offset+overlap)!==part.slice(0,overlap))return null;
        return before+part.slice(overlap);
      };
      assert.equal(appendStationSourceDelta("abc","abcde",0),"abcde");
      assert.equal(appendStationSourceDelta("abcde","cdef",2),"abcdef");
      assert.equal(appendStationSourceDelta("abc","x",3),"abcx");
      assert.equal(appendStationSourceDelta("abc","nope",0),null);
      assert.equal(appendStationSourceDelta("abc","x",99),null);
      assert.equal(appendStationSourceDelta("a🌀","🌀b",1),"a🌀b");
      assert.equal(appendStationSourceDelta("a🌀","!",3),"a🌀!");
      console.log("SWRLZ_LIFE_RECONNECT_MERGE_PASS");'''
    with tempfile.TemporaryDirectory(prefix="swrlz-life-js-test-") as d:
        p=Path(d)/"test.js";p.write_text(test)
        result=subprocess.run(["node",str(p)],capture_output=True,text=True,timeout=20)
        if result.returncode:raise RuntimeError("JS merge test "+result.stderr[-700:])
    record("JS_SOURCE_AND_REPLAY_TEST_PASS",scripts=checked,utf16=True)

def check_candidate(before,after):
    for name in (ENGINE,STATION):ast.parse(after[name].decode(),filename=name)
    check_js(after[UI].decode())
    code=after[ENGINE].decode()
    st=after[STATION].decode()
    html=after[UI].decode()
    for key in ("native_budget_seconds=240","cancel_check=cancel_check",
         'max_segments=8 if allow_continue else 1',
         'if timing.get("finishReason")=="cancelled":return',
         '"CODE_OUTPUT_CHECKPOINT"',"_swrlz_code_candidate_preview",
         "_swrlz_patch_candidate_once","completion_validation("):
        assert key in code,key
    for key in ('payload["_cancelCheck"]','lastCodeProgressAtUnixMs',
                '"offsetUtf16"','"cancelRequested"','"CANCELLED"','_commit_revision(s)'):
        assert key in st,key
    for key in ("appendStationSourceDelta","/api/lalm_station/cancel",
                "visibilitychange","pageshow","keepStationHydrated",
                'id="projectFilePicker"','id="micButton"','CANDIDATE_PREVIEW_DELTA'):
        assert key in html,key
    assert "streamAbortController?.abort();" not in html[html.index('stopButton.addEventListener("click"'):html.index("// §E Analyze is a user-clicked",html.index('stopButton.addEventListener("click"'))]
    assert "preview_buffer" in code and "len(preview_buffer)>=128" in code
    assert '"resuming":True' in st and '262144' in st
    assert "g.pop(\"codeDraftCheckpoint\",None)" in st
    assert "savedDraft" in html and "appendData(draftText.slice(shown.length))" in html
    assert all(before[name]!=after[name] for name in FILES)
    record("SOURCE_CONTRACTS_PASS",files=list(FILES),existingModel=True,
           unchangedThreadBudget=True,sourceRevisionPreserved=True)

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    originals={n:Path(hf_hub_download(SPACE,n,repo_type="space",revision=rev,token=api.token)).read_bytes() for n in FILES}
    candidates={ENGINE:patch_engine(originals[ENGINE]),STATION:patch_station(originals[STATION]),UI:patch_ui(originals[UI])}
    check_candidate(originals,candidates)
    BACKUP.mkdir(parents=True,exist_ok=True)
    for n,blob in originals.items():
        out=BACKUP/n;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(blob)
    (BACKUP/"original-revision.txt").write_text(rev)
    (BACKUP/"sha.json").write_text(json.dumps({"revision":rev,
          "old":{n:hash_bytes(b) for n,b in originals.items()},
          "new":{n:hash_bytes(b) for n,b in candidates.items()},
          "modelChanged":False,"threadsChanged":False,"authChanged":False},indent=2))
    record("SNAPSHOT_PASS",revision=rev)
    return rev,originals,candidates

def publish(api,revision,files,reason):
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Concurrent source change; refusing overwrite")
    with tempfile.TemporaryDirectory(prefix="swrlz-life-deploy-") as d:
        ops=[]
        for path,blob in files.items():
            p=Path(d)/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
            ops.append(CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(p)))
        commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
                         operations=ops,commit_message=reason)
    new=str(commit.oid)
    for path,blob in files.items():
        published=Path(hf_hub_download(SPACE,path,repo_type="space",revision=new,token=api.token)).read_bytes()
        if hash_bytes(published)!=hash_bytes(blob):raise RuntimeError("Published source hash mismatch "+path)
    record("PUBLISHED_SOURCE_HASH_PASS",revision=new)
    return new

def live_ui(revision,timeout=700):
    deadline=time.monotonic()+timeout
    last=None
    while time.monotonic()<deadline:
        try:
            url=BASE+"/chat/%C2%A7wyrlz?swrlz_lifecycle_probe="+uuid.uuid4().hex
            with urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=25) as r:
                source=r.read(950000).decode("utf-8",errors="replace")
            if "appendStationSourceDelta" in source and "SWRLZ_LALM_STATION" in source:
                record("LIVE_UI_ACTIVE",revision=revision,sourceChars=len(source));return
            last="prior UI still serving"
        except Exception as exc:last=type(exc).__name__+":"+str(exc)[:150]
        time.sleep(10)
    raise RuntimeError("New Chat UI not served: "+str(last))

def live_model():
    with urllib.request.urlopen(urllib.request.Request(BASE+"/api/hf/qwen35-ready",headers=HEAD),timeout=25) as r:
        state=json.load(r)
    if state.get("ready") is not True or state.get("model")!="qwen3.5-9b" or (state.get("decodeThreads"),state.get("batchThreads"),state.get("cpuCapacity"))!=(18,18,16):
        raise RuntimeError("Resident model/thread/quota changed: "+str({x:state.get(x) for x in ("ready","model","decodeThreads","batchThreads","cpuCapacity")}))
    record("UNCHANGED_MODEL_READY",model="qwen3.5-9b",threads=18,quota=16)

def smoke():
    # Never look up real user sessions. This is an isolated synthetic chat.
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4())
    thread="swrlz-lifecycle-verify-"+uuid.uuid4().hex
    payload={"modelId":"700m","requestId":rid,"threadId":thread,
             "prompt":"Write a short complete runnable HTML with one simple interactive button and CSS. Return one HTML code artifact.",
             "profileId":"LALM","timeZone":"UTC"}
    request=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
             data=json.dumps(payload).encode(),headers={**HEAD,"Content-Type":"application/json"})
    with opener.open(request,timeout=40) as r:
        if r.status!=202:raise RuntimeError("Synthetic Station admission failed")
        r.read()
    time.sleep(2)
    # The source of truth for in-flight work is the same session's snapshot.
    with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",headers=HEAD),timeout=30) as r:
        snapshot=json.load(r)
    active=snapshot.get("activeGeneration") or {}
    if active.get("requestId")!=rid:
        raise RuntimeError("Synthetic request missing after reconnect")
    # Stop via authenticated real endpoint; acknowledge but do not invent
    # terminal status before the worker has actually observed cancellation.
    stop=urllib.request.Request(BASE+"/api/lalm_station/cancel",method="POST",
             data=json.dumps({"requestId":rid}).encode(),
             headers={**HEAD,"Content-Type":"application/json"})
    with opener.open(stop,timeout=30) as r:
        receipt=json.load(r)
    if receipt.get("state") not in ("CANCEL_REQUESTED","CANCELLED"):
        raise RuntimeError("Stop endpoint failed to acknowledge request: "+str(receipt))
    deadline=time.monotonic()+240
    last={}
    while time.monotonic()<deadline:
        with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",headers=HEAD),timeout=30) as r:
            state=json.load(r)
        active=state.get("activeGeneration") or {}
        if active.get("requestId")==rid:
            last=active
            if active.get("terminal") and active.get("terminalType")=="CANCELLED":
                record("LIVE_CANCEL_AND_SYNC_PASS",requestMatches=True,terminal="CANCELLED",
                       latencyMaxSeconds=240)
                return
        time.sleep(4)
    raise RuntimeError("Stop not confirmed terminal CANCELLED within live bound, last phase="+str(last.get("phase")))

def main():
    args=sys.argv[1:]
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if args==["preflight"]:
        snapshot(api);return
    if args!=["publish"]:raise SystemExit("Usage: script preflight|publish")
    if not api.token or os.environ.get("SWRLZ_CODING_LIFECYCLE_APPROVED")!="1":
        raise RuntimeError("Explicit source-scoped deployment approval required")
    rev=(BACKUP/"original-revision.txt").read_text().strip()
    original={n:(BACKUP/n).read_bytes() for n in FILES}
    candidate={ENGINE:patch_engine(original[ENGINE]),STATION:patch_station(original[STATION]),UI:patch_ui(original[UI])}
    check_candidate(original,candidate)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Exact Hugging Face source SHA changed since preflight")
    deployed=None
    try:
        deployed=publish(api,rev,candidate,
                    "§C: interrupt long coding on Stop, bound CPU work, resync streamed code")
        live_ui(deployed)
        live_model()
        smoke()
        record("LIVE_RELEASE_ACCEPTED",revision=deployed,
               sameModel=True,sourcePreserved=True)
    except Exception:
        record("LIVE_RELEASE_REJECTED",revision=deployed)
        if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
            previous=publish(api,deployed,original,
                         "Rollback §C coding lifecycle to exact previous engine/Station/UI")
            live_ui(previous)
            record("EXACT_OLD_SOURCES_RESTORED",revision=previous)
        elif deployed:record("ROLLBACK_BLOCKED_BY_CONCURRENT_CHANGE")
        raise

if __name__=="__main__":main()
