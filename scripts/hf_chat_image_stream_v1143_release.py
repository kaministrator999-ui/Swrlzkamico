#!/usr/bin/env python3
"""§C 1.1.43: stream original Qwen image tokens; gate coding on the user question.

Three-file source-pinned, checksum-gated Hugging Face release. No changes to
weights, credentials, chat history, §E, native decoder, or account storage.
"""
from __future__ import annotations

import ast, hashlib, io, json, os, re, time, urllib.error, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
START="561e5fa93039cde26c3563ade1cd238860368893"
UI="chat/§wyrlz/index.html"
VISION="chat_vision.py"
ROUTER="model_router.py"
FILES=(UI,VISION,ROUTER)
BEFORE={
 UI:"7f9087779b486d525cdb96ceb104b625a5397427f50a805bd62e9f9da8c56652",
 VISION:"91d5bb5dcf0ce05254b32df7baa5fde5d15388ee19f401daef86c37e520673d8",
 ROUTER:"b48b09a3336fd9ba4e2347febda4eb6c0d727430fe990cc13149bce8d43088bd",
}
AFTER={
 UI:"6c9d3651247ae3d9da4b0e1d723825b2f4c73182b4b3d55f79f14506b538ebb9",
 VISION:"5c32a8d22dd2a3770573c5ca9ee703bbe8e10c8adffbdea52dfc7a43ba2c0290",
 ROUTER:"13985a29d964af64639d84fd826e7c36cfe5a288955bb41162370b277854456a",
}
BACKUP=Path("reports/swrlz-image-live-stream-1143")
BASE="https://kamiloki-swyrlz.hf.space"
MARK="swrlz-image-live-stream-v1143"

def sha(data):return hashlib.sha256(data).hexdigest()
def emit(event,**kwargs):
 print("SWRLZ_IMAGE_STREAM_1143 "+json.dumps({"event":event,**kwargs},sort_keys=True),flush=True)
def once(text,before,after,tag):
 count=text.count(before)
 if count!=1:raise RuntimeError("SOURCE_DRIFT "+tag+" matches="+str(count))
 return text.replace(before,after,1)
class IDs(HTMLParser):
 def __init__(self):super().__init__();self.found=[]
 def handle_starttag(self,tag,attrs):
  value=dict(attrs).get("id")
  if value:self.found.append(value)
def ids(text):
 parser=IDs();parser.feed(text);return parser.found

def patch_router(raw):
 text=raw.decode("utf-8");old=text
 text=once(text,
  '    question = re.sub(r"\\s+", " ", question.strip().lower().rstrip("?! .")).strip()',
  '    question = re.sub(r"\\s+", " ", question.strip().lower().replace("’", "\'").rstrip("?! .")).strip()',
  "mobile punctuation")
 text=once(text,'        "what do you notice in this image",',
  '''        "what do you notice in this image",
        "what's this image look like to you",
        "what does this image look like to you",
        "what's this picture look like to you",
        "what does this picture look like to you",''',
  "basic original-vision question")
 text=once(text,
  '    intent=programming_intent(str(payload.get("prompt") or ""),history,pins,payload.get("priorProgrammingState") if isinstance(payload.get("priorProgrammingState"),dict) else {})',
  '''    # swrlz-image-live-stream-v1143: the original user question, not the
    # image model's untrusted description, controls coding/research/UI intent.
    # A visual observation may contain words such as "source", "code", or
    # "project"; those are EVIDENCE, never a request to write or repair code.
    raw_prompt=str(payload.get("prompt") or "")
    vision_question=None
    if raw_prompt.endswith(_VISION_END) and _VISION_START in raw_prompt:
        vision_question=raw_prompt[:-len(_VISION_END)].rpartition(_VISION_START)[0].strip()
    intent_prompt=vision_question if vision_question is not None else raw_prompt
    prior_programming=(payload.get("priorProgrammingState")
                       if isinstance(payload.get("priorProgrammingState"),dict) else {})
    if vision_question is not None:
        # Only explicit programming language/actions in the current USER
        # question can activate code validation. Prior coding state or pins
        # cannot turn "What does this image look like?" into a code request.
        isolated=programming_intent(intent_prompt,[],[],{})
        intent=(programming_intent(intent_prompt,history,pins,prior_programming)
                if isolated.get("codingTask") else isolated)
    else:
        intent=programming_intent(intent_prompt,history,pins,prior_programming)''',
  "coding intent isolation")
 text=once(text,'    risk_kind=classify_intent_risk(str(payload.get("prompt") or ""))',
           '    risk_kind=classify_intent_risk(intent_prompt)',"risk input")
 text=once(text,'    identity_answer=direct_app_identity_answer(str(payload.get("prompt") or ""))',
           '    identity_answer=direct_app_identity_answer(intent_prompt)',"identity input")
 text=once(text,'    online_plan=classify_online_request(str(payload.get("prompt") or ""),history,intent,payload.get("clientLocation"))',
           '    online_plan=classify_online_request(intent_prompt,history,intent,payload.get("clientLocation"))',"online input")
 text=once(text,
           '    widget_plan=plan_conversation_widget(\n        str(payload.get("prompt") or ""),history,intent,bool(online_plan.get("requested")))',
           '    widget_plan=plan_conversation_widget(\n        intent_prompt,history,intent,bool(online_plan.get("requested")))',"widget input")
 ast.parse(text,filename=ROUTER)
 if MARK not in text:raise RuntimeError("Router marker missing")
 return text.encode("utf-8")

def patch_vision(raw):
 text=raw.decode("utf-8")
 text=once(text,
  'def _run_vision_job(job_id: str, image: str, question: str, cancel_event: threading.Event, analysis_levels: int = 1) -> None:',
  '''def _set_vision_partial(job_id: str, description: str) -> None:
    """Only the authenticated job owner can read this provisional text.

    Inference is CPU-bound; keep updates bounded and never log/store the
    user's private image content or model text in repository diagnostics.
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is not None and job["phase"] in ACTIVE_PHASES:
            job["partialDescription"] = str(description or "")[:MAX_DESCRIPTION_CHARS]
            job["updatedAt"] = time.monotonic()


def _run_vision_job(job_id: str, image: str, question: str, cancel_event: threading.Event, analysis_levels: int = 1) -> None:''',
 "private streaming RAM")
 text=once(text,
 '''            report_phase=lambda phase, **fields: _set_job_phase(job_id, phase, **fields),
            should_cancel=cancel_event.is_set, analysis_levels=analysis_levels,''',
 '''            report_phase=lambda phase, **fields: _set_job_phase(job_id, phase, **fields),
            should_cancel=cancel_event.is_set, analysis_levels=analysis_levels,
            on_partial=lambda description: _set_vision_partial(job_id, description),''',"partial callback owner")
 text=once(text,
 '''def _ask_vision_local(image_url: str, question: str, report_phase=None, should_cancel=None,
                      analysis_levels: int = 1) -> str:''',
 '''def _ask_vision_local(image_url: str, question: str, report_phase=None, should_cancel=None,
                      analysis_levels: int = 1, on_partial=None) -> str:''',"stream callback signature")
 text=once(text,
 '''    report = report_phase or (lambda _phase, **_fields: None)
    cancelled = should_cancel or (lambda: False)''',
 '''    report = report_phase or (lambda _phase, **_fields: None)
    publish_partial = on_partial or (lambda _text: None)
    cancelled = should_cancel or (lambda: False)''',"stream callback binding")
 text=once(text,
 '''            parts = []
            finish_reason = None''',
 '''            parts = []
            finish_reason = None
            last_partial_at = 0.0''',"stream publish timer")
 text=once(text,
 '''                        parts.append(delta)
            finally:''',
 '''                        parts.append(delta)
                        if region is None and level == 1:
                            now = time.monotonic()
                            if now - last_partial_at >= 0.4:
                                publish_partial("".join(parts)[:MAX_DESCRIPTION_CHARS])
                                last_partial_at = now
            finally:''',"Qwen chunk forwarding")
 text=once(text,
 '''            result = "".join(parts).strip()
            if not result:
                raise ValueError("VISION_RESPONSE_EMPTY")
            return (result[:MAX_DESCRIPTION_CHARS],''',
 '''            result = "".join(parts).strip()
            if not result:
                raise ValueError("VISION_RESPONSE_EMPTY")
            if region is None and level == 1:
                publish_partial(result[:MAX_DESCRIPTION_CHARS])
            return (result[:MAX_DESCRIPTION_CHARS],''',"final partial flush")
 text=once(text,
 '''            if phase in ("ANALYZING", "COMPLETE"):
                # Observed native inference progress only, never fabricated percentages.
                response["inferenceStage"] = job.get("inferenceStage")''',
 '''            if phase in ("ANALYZING", "COMPLETE"):
                # Private, owner-scoped provisional Qwen words while decoding.
                response["partialDescription"] = str(job.get("partialDescription") or "")[:MAX_DESCRIPTION_CHARS]
                # Observed native inference progress only, never fabricated percentages.
                response["inferenceStage"] = job.get("inferenceStage")''',"owner-only streaming status")
 ast.parse(text,filename=VISION)
 if MARK.replace("image-live-stream","image-live-stream") not in text and "def _set_vision_partial" not in text:
  raise RuntimeError("Vision streaming patch absent")
 return text.encode("utf-8")

def patch_ui(raw):
 text=raw.decode("utf-8")
 old_ids=ids(text)
 text=once(text,'swrlz-chat-version" content="1.1.42"',
           'swrlz-chat-version" content="1.1.43"',"version")
 text=once(text,
 '''            originalBytesPreserved:state.originalBytesPreserved
          });''',
 '''            originalBytesPreserved:state.originalBytesPreserved,
            partialDescription:state.partialDescription
          });''',"private status projected to UI")
 text=once(text,
 '''        // Show L1 as the first useful provisional answer and append L2 crop
        // observations inside this SAME live surface. No premature persisted
        // assistant turn; the single final assistant message replaces it.''',
 '''        // swrlz-image-live-stream-v1143: Qwen's FIRST image generation is
        // displayed while decoding. It becomes a saved assistant answer only
        // after the authenticated Station handoff commits the result.''',"streaming preview note")
 text=once(text,
 '''        progressiveNote.textContent="Local model observations · unverified. The final reply will reconcile the views.";''',
 '''        progressiveNote.textContent="Qwen 9B live observation · not yet saved to the conversation.";''',"initial preview note")
 text=once(text,
 '''            if(phase==="ANALYZING"&&Number(timing?.requestedLevels)>=2){''',
 '''            const streamingVision=String(timing?.partialDescription||"").slice(0,6000);
            if(phase==="ANALYZING"&&streamingVision){
              progressive.hidden=false;
              progressiveTitle.textContent="Qwen 9B · Writing the image response";
              if(progressiveBody.textContent!==streamingVision){
                progressiveBody.textContent=streamingVision;
                if(progressive.isConnected&&this.root.isConnected){
                  const nearBottom=messageList.scrollHeight-messageList.scrollTop-messageList.clientHeight<140;
                  if(nearBottom)messageList.scrollTop=messageList.scrollHeight;
                }
              }
              progressiveNote.textContent="Streaming original-image observations · saved after chat acceptance.";
            }
            if(phase==="ANALYZING"&&!streamingVision&&Number(timing?.requestedLevels)>=2){''',"streaming first Qwen observation")
 if ids(text)!=old_ids:raise RuntimeError("Unexpected DOM ID/interaction change")
 if text.count('name="swrlz-chat-design-version" content="1.0.60"')!=1:raise RuntimeError("UI baseline drift")
 if MARK not in text:raise RuntimeError("UI patch marker absent")
 return text.encode("utf-8")

def api():
 token=os.environ.get("HF_TOKEN")
 if not token:raise RuntimeError("Hugging Face deploy authority missing")
 return HfApi(token=token)
def read(client,rev):
 return {p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=rev,token=client.token)).read_bytes() for p in FILES}
def candidate(original):
 return {UI:patch_ui(original[UI]),VISION:patch_vision(original[VISION]),ROUTER:patch_router(original[ROUTER])}

def preflight(client):
 rev=client.repo_info(SPACE,repo_type="space").sha
 if rev!=START:raise RuntimeError("Live HF Space head changed, no mutation: "+rev)
 original=read(client,rev)
 if {p:sha(v) for p,v in original.items()}!=BEFORE:raise RuntimeError("Original source hashes mismatch")
 result=candidate(original)
 hashes={p:sha(v) for p,v in result.items()}
 if hashes!=AFTER:raise RuntimeError("Exact candidate hashes differ from locally tested source: "+str(hashes))
 BACKUP.mkdir(parents=True,exist_ok=True)
 for p in FILES:
  for folder,data in (("original",original[p]),("candidate",result[p])):
   f=BACKUP/folder/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 (BACKUP/"manifest.json").write_text(json.dumps({"revision":rev,"before":BEFORE,"after":AFTER,"files":FILES},indent=2)+"\n")
 emit("PREFLIGHT_OK",revision=rev,hashes=hashes)
 return result

def commit(client,rev,data,label):
 response=client.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
  operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(v)) for p,v in data.items()],
  commit_message=label)
 return str(response.oid or client.repo_info(SPACE,repo_type="space").sha)

def served():
 try:
  req=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz?revision=1.1.43",
    headers={"Cache-Control":"no-cache","User-Agent":"Swrlz-Vision-Streaming-1.1.43"})
  with urllib.request.urlopen(req,timeout=20) as response:
   html=response.read(900000).decode("utf-8","replace")
   if response.status!=200:return False
   if 'swrlz-chat-version" content="1.1.43"' not in html or MARK not in html:return False
  req=urllib.request.Request(BASE+"/api/hf/qwen35-ready",
     headers={"Cache-Control":"no-cache","User-Agent":"Swrlz-Vision-Streaming-1.1.43"})
  with urllib.request.urlopen(req,timeout=20) as response:
   body=json.load(response)
   return response.status==200 and body.get("ready") is True and body.get("model")=="qwen3.5-9b"
 except (urllib.error.URLError,TimeoutError,ValueError,KeyError):return False

def verify(client,rev):
 previous=None;stable=0
 for attempt in range(1,71):
  if client.repo_info(SPACE,repo_type="space").sha!=rev:
   raise RuntimeError("Concurrent HF Space commit; refuse to accept another owner's release")
  runtime=client.get_space_runtime(SPACE)
  stage=str(runtime.stage).upper().split(".")[-1]
  serving=str((runtime.raw or {}).get("sha") or "")
  ready=served() if stage=="RUNNING" and serving==rev else False
  observed=(stage,serving,ready)
  if observed!=previous:
   emit("RUNTIME_GATE",attempt=attempt,stage=stage,serving=serving,ready=ready)
   previous=observed
  if stage=="RUNTIME_ERROR":raise RuntimeError("HF runtime failed during release")
  stable=stable+1 if stage=="RUNNING" and serving==rev and ready else 0
  if stable>=2:
   emit("LIVE_ACCEPTED",revision=rev,chatVersion="1.1.43",qwenReady=True)
   return
  time.sleep(12)
 raise RuntimeError("Exact live Chat revision and Qwen readiness not confirmed")

def publish(client):
 if os.environ.get("SWRLZ_IMAGE_STREAM_1143_APPROVED")!="yes":
  raise PermissionError("This release is not explicitly authorized")
 info=json.loads((BACKUP/"manifest.json").read_text())
 old={p:(BACKUP/"original"/p).read_bytes() for p in FILES}
 new={p:(BACKUP/"candidate"/p).read_bytes() for p in FILES}
 if info!={"revision":START,"before":BEFORE,"after":AFTER,"files":list(FILES)}:
  raise RuntimeError("Release snapshot manifest drift")
 if {p:sha(v) for p,v in old.items()}!=BEFORE or {p:sha(v) for p,v in new.items()}!=AFTER:
  raise RuntimeError("Source snapshot hashes mismatch")
 if candidate(old)!=new:raise RuntimeError("Candidate patch source drift")
 if client.repo_info(SPACE,repo_type="space").sha!=START or read(client,START)!=old:
  raise RuntimeError("Live source changed; no deploy")
 applied=None
 try:
  applied=commit(client,START,new,"§C 1.1.43: stream original Qwen image response and prevent image-to-code misrouting")
  emit("PUBLISHED",revision=applied)
  if read(client,applied)!=new:raise RuntimeError("HF source readback differs")
  emit("EXACT_READBACK_PASS",revision=applied)
  verify(client,applied)
 except Exception as exc:
  emit("RELEASE_REJECTED",revision=applied,reason=str(exc)[:220])
  if applied and client.repo_info(SPACE,repo_type="space").sha==applied:
   rollback=commit(client,applied,old,"Rollback §C 1.1.43 to verified former sources")
   emit("EXACT_ROLLBACK",revision=rollback)
  else:emit("ROLLBACK_NOT_SAFE_CONCURRENT_HEAD")
  raise

if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["publish"]):raise SystemExit("Use inspect|publish")
 client=api()
 if sys.argv[1]=="inspect":preflight(client)
 else:publish(client)
