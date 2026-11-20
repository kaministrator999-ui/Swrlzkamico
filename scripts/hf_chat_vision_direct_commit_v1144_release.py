#!/usr/bin/env python3
"""§C 1.1.44: one owner-verified Qwen vision answer, streamed once and committed.

Source-pin two existing HF files; preserve Qwen weights, model router, §E,
history, and all other runtime endpoints. Fail on drift; snapshot and rollback.
"""
from __future__ import annotations
import ast, hashlib, io, json, os, re, time, urllib.error, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
START="a676721e889c7b1c3552d7e02e3c510680c31b99"
UI="chat/§wyrlz/index.html"
STATION="station.py"
FILES=(UI,STATION)
EXPECTED={
 UI:"6c9d3651247ae3d9da4b0e1d723825b2f4c73182b4b3d55f79f14506b538ebb9",
 STATION:"1b4f517fb891f4be89d88702d4584706fa0c10e34ae578e639b5e76d2f30c73f"
}
CANDIDATE={
 UI:"842a76fbc525186209ff2cbed300c9b11f73d5733d0cea34c98067b4a21ab67d",
 STATION:"7aebbab687b8df7c5bdd1e4da583d7333df56bff957ef755b8b4dcc39751f4b0"
}
BACKUP=Path("reports/swrlz-vision-direct-commit-1144")
BASE="https://kamiloki-swyrlz.hf.space"

def digest(b):return hashlib.sha256(b).hexdigest()
def emit(event,**fields):
 print("SWRLZ_VISION_DIRECT_1144 "+json.dumps({"event":event,**fields},sort_keys=True),flush=True)
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise RuntimeError("SOURCE_DRIFT_"+label+": found "+str(n))
 return s.replace(old,new,1)
class IDParser(HTMLParser):
 def __init__(self):super().__init__();self.ids=[]
 def handle_starttag(self,tag,attrs):
  key=dict(attrs).get("id")
  if key:self.ids.append(key)
def ids(html):
 p=IDParser();p.feed(html);return p.ids

def patch_station(raw):
 s=raw.decode("utf-8")
 s=one(s,'from model_router import dispatch, ModelUnavailable, routes',
       'from model_router import dispatch, ModelUnavailable, routes, _direct_vision_description',"router")
 s=one(s,
 '''    vision_receipt=(vision_job_resource_receipt(google_owner,body.get("visionJobId"),prompt)
                    if isinstance(body.get("visionJobId"),str) else None)
    profile_id=str(body.get("profileId") or "LALM")''',
 '''    vision_job_id=body.get("visionJobId") if isinstance(body.get("visionJobId"),str) else ""
    vision_receipt=(vision_job_resource_receipt(google_owner,vision_job_id,prompt)
                    if vision_job_id else None)
    # swrlz-vision-direct-commit-v1144: a signed-in, owner-verified Qwen vision
    # job is the ONLY authority for reusing the text it actually generated.
    # A client-forged handoff or another account's image cannot skip inference.
    # Reject stale/mismatched jobs rather than rerun the text chat model on an
    # unverified description that could masquerade as visual observation.
    if vision_job_id and vision_receipt is None:
        raise HTTPException(409,"Image analysis is no longer verifiable. Reattach the original image to retry.")
    direct_vision_answer=None
    if vision_receipt and _direct_vision_description({"prompt":prompt}) is not None:
        handoff=vision_handoff_from_message({"role":"user","text":prompt})
        if handoff:
            direct_vision_answer=handoff["descriptionSentToChatModel"]
    profile_id=str(body.get("profileId") or "LALM")''',"receipt_gate")
 s=one(s,
 '''    if vision_receipt:
        payload["visionResourceUsage"]=copy.deepcopy(vision_receipt)
    local_project_intent=''', 
 '''    if vision_receipt:
        payload["visionResourceUsage"]=copy.deepcopy(vision_receipt)
    if direct_vision_answer:
        # No second LLM decoding or text-on-text reinterpretation. This text
        # exactly matches the completed image job and saved user evidence.
        payload["verifiedVisionAnswer"]=direct_vision_answer
    local_project_intent=''', "payload")
 s=one(s,
 '''        if forge_context is None and model_id=="stock" and _stock_generate is None and not (payload.get("githubDirectTestTxt") or payload.get("githubChatFileAction") or payload.get("verifiedPrivateAnswer") or payload.get("githubStart") or payload.get("githubAction") or payload.get("suppliedGitHubReportExplanation")):raise RuntimeError("Original HF generator is not installed")''',
 '''        if forge_context is None and model_id=="stock" and _stock_generate is None and not (payload.get("verifiedVisionAnswer") or payload.get("githubDirectTestTxt") or payload.get("githubChatFileAction") or payload.get("verifiedPrivateAnswer") or payload.get("githubStart") or payload.get("githubAction") or payload.get("suppliedGitHubReportExplanation")):raise RuntimeError("Original HF generator is not installed")''', "stock")
 s=one(s,
 '''        if forge_context is not None:
            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate,forge_context=forge_context)
        elif isinstance(payload.get("codeContinuation"),dict):''',
 '''        if isinstance(payload.get("verifiedVisionAnswer"),str) and payload["verifiedVisionAnswer"].strip():
            # swrlz-vision-direct-commit-v1144: move the exact first Qwen
            # answer through Station's normal DELTA and durable chat commit.
            # This branch has no model call, no code-validator or paraphraser.
            event_source=iter(({"type":"STATUS","phase":"VISION_ANSWER_REUSED",
                                 "reason":"Saving the original Qwen image response."},
                               {"type":"DELTA","text":payload["verifiedVisionAnswer"]},
                               {"type":"COMPLETE"}))
        elif forge_context is not None:
            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate,forge_context=forge_context)
        elif isinstance(payload.get("codeContinuation"),dict):''',"direct_run")
 s=one(s,
 '''    response=JSONResponse({"ok":True,"contract":CONTRACT,"requestId":rid,"modelId":model_id},status_code=202)''',
 '''    response=JSONResponse({"ok":True,"contract":CONTRACT,"requestId":rid,"modelId":model_id,
                           "visionAnswerReused":bool(direct_vision_answer)},status_code=202)''',"ack")
 ast.parse(s,filename=STATION)
 if s.count("swrlz-vision-direct-commit-v1144")!=2:raise RuntimeError("Station direct-answer markers changed")
 return s.encode("utf-8")

def patch_ui(raw):
 s=raw.decode("utf-8")
 before_ids=ids(s)
 s=one(s,'swrlz-chat-version" content="1.1.43"',
       'swrlz-chat-version" content="1.1.44"',"version")
 s=one(s,
 '''        if(syncedGeneration&&matchingGeneration&&(!alreadySettled||syncedGeneration.terminal)&&(!stationGeneration||syncedGeneration.requestId===stationGeneration.requestId||stationGeneration.terminal))
          stationGeneration=syncedGeneration;''',
 '''        if(syncedGeneration&&matchingGeneration&&(!alreadySettled||syncedGeneration.terminal)&&(!stationGeneration||syncedGeneration.requestId===stationGeneration.requestId||stationGeneration.terminal)){
          // swrlz-vision-direct-commit-v1144: a slower authoritative snapshot
          // must not blank the already-visible original Qwen answer while
          // Station commits that exact answer to the account conversation.
          const held=stationGeneration?.visionResponseReused &&
            stationGeneration.requestId===syncedGeneration.requestId &&
            !syncedGeneration.terminal && !String(syncedGeneration.text||"");
          stationGeneration=held
            ?{...syncedGeneration,text:stationGeneration.text,visionResponseReused:true}
            :syncedGeneration;
        }''',"snapshot")
 s=one(s,
 '''        let sendAcknowledged=false,sendStarted=false,activity=null,visionDraftHeld=false,provisionalThread=null,provisionalMessageId="",imageThreadCreated=false,imageThreadId="";''',
 '''        let sendAcknowledged=false,sendStarted=false,activity=null,visionDraftHeld=false,provisionalThread=null,provisionalMessageId="",imageThreadCreated=false,imageThreadId="";
        let firstQwenVisionAnswer="";''',"state")
 s=one(s,
 '''            const description=await requestVisionDescription(attachment,draftText,activity);
            if(!ownsSubmission())return false;''',
 '''            const description=await requestVisionDescription(attachment,draftText,activity);
            if(!ownsSubmission())return false;
            firstQwenVisionAnswer=description;''',"vision_result")
 s=one(s,
 '''          if(activity){
            activity.update("RESPONDING");
            // Station now owns the real chat response and its own activity UI.
            removeVisionActivity(activity);
          }''',
 '''          if(activity){
            // swrlz-vision-direct-commit-v1144: on a server-verified reuse,
            // transfer the SAME first Qwen words directly to the assistant
            // bubble before removing the original vision streaming card.
            // The normal Station stream later confirms their exact bytes.
            if(accepted.visionAnswerReused===true && firstQwenVisionAnswer &&
               stationGeneration?.requestId===requestId){
              stationGeneration={...stationGeneration,text:firstQwenVisionAnswer,
                                 visionResponseReused:true};
              renderStationGeneration();
            }else activity.update("RESPONDING");
            removeVisionActivity(activity);
          }''',"no_blank_handoff")
 if ids(s)!=before_ids:raise RuntimeError("Chat DOM IDs changed")
 if 'name="swrlz-chat-design-version" content="1.0.60"' not in s:raise RuntimeError("Professional UI baseline missing")
 if s.count("swrlz-vision-direct-commit-v1144")!=2:raise RuntimeError("UI direct-commit markers changed")
 return s.encode("utf-8")

def client():
 token=os.getenv("HF_TOKEN")
 if not token:raise RuntimeError("Hugging Face Space deploy token unavailable")
 return HfApi(token=token)
def read(api,revision):
 return {p:Path(hf_hub_download(SPACE,p,revision=revision,repo_type="space",token=api.token)).read_bytes() for p in FILES}
def patch(original):
 return {UI:patch_ui(original[UI]),STATION:patch_station(original[STATION])}
def inspect(api):
 revision=api.repo_info(SPACE,repo_type="space").sha
 if revision!=START:raise RuntimeError("HF Space head changed: "+revision)
 source=read(api,revision)
 hashes={p:digest(v) for p,v in source.items()}
 if hashes!=EXPECTED:raise RuntimeError("Live source fingerprints drifted: "+str(hashes))
 candidate=patch(source)
 patched_hashes={p:digest(v) for p,v in candidate.items()}
 if patched_hashes!=CANDIDATE:raise RuntimeError("Patch changed from local regression-tested bytes: "+str(patched_hashes))
 BACKUP.mkdir(parents=True,exist_ok=True)
 for path in FILES:
  for directory,raw in (("original",source[path]),("candidate",candidate[path])):
   dest=BACKUP/directory/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 (BACKUP/"manifest.json").write_text(json.dumps({
  "revision":revision,"before":EXPECTED,"after":CANDIDATE,"files":list(FILES)},indent=2)+"\n")
 emit("PREFLIGHT_OK",revision=revision,hashes=patched_hashes)
 return candidate

def commit(api,revision,contents,message):
 result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
  operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(raw)) for p,raw in contents.items()],
  commit_message=message)
 return str(result.oid or api.repo_info(SPACE,repo_type="space").sha)

def ready():
 try:
  req=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz?release=1144",
      headers={"Cache-Control":"no-cache","User-Agent":"Swyrlz-Vision-Direct-Commit-1144"})
  with urllib.request.urlopen(req,timeout=18) as res:
   content=res.read(900000).decode("utf-8","replace")
   if res.status!=200 or 'swrlz-chat-version" content="1.1.44"' not in content or "swrlz-vision-direct-commit-v1144" not in content:return False
  req=urllib.request.Request(BASE+"/api/hf/qwen35-ready",headers={"Cache-Control":"no-cache"})
  with urllib.request.urlopen(req,timeout=18) as res:
   status=json.load(res)
   return res.status==200 and status.get("ready") is True and status.get("model")=="qwen3.5-9b"
 except (urllib.error.URLError,TimeoutError,ValueError,KeyError):return False

def verify(api,revision):
 previous=None;success=0
 for attempt in range(1,71):
  head=api.repo_info(SPACE,repo_type="space").sha
  if head!=revision:raise RuntimeError("Concurrent update superseded release")
  runtime=api.get_space_runtime(SPACE)
  stage=str(runtime.stage).upper().split(".")[-1]
  serving=str((runtime.raw or {}).get("sha") or "")
  ok=ready() if stage=="RUNNING" and serving==revision else False
  observed=(stage,serving,ok)
  if observed!=previous:
   emit("RUNTIME_GATE",attempt=attempt,stage=stage,serving=serving,ready=ok)
   previous=observed
  if stage=="RUNTIME_ERROR":raise RuntimeError("HF Space runtime error")
  success=success+1 if stage=="RUNNING" and serving==revision and ok else 0
  if success>=2:
   emit("LIVE_ACCEPTED",revision=revision,version="1.1.44",qwenReady=True)
   return
  time.sleep(12)
 raise RuntimeError("Verified live Chat and preloaded Qwen revision unavailable")

def publish(api):
 if os.getenv("SWRLZ_VISION_DIRECT_1144_APPROVED")!="yes":
  raise PermissionError("Approved deployment flag missing")
 info=json.loads((BACKUP/"manifest.json").read_text())
 if info!={"revision":START,"before":EXPECTED,"after":CANDIDATE,"files":list(FILES)}:
  raise RuntimeError("Release manifest changed")
 old={p:(BACKUP/"original"/p).read_bytes() for p in FILES}
 new={p:(BACKUP/"candidate"/p).read_bytes() for p in FILES}
 if {p:digest(v) for p,v in old.items()}!=EXPECTED or {p:digest(v) for p,v in new.items()}!=CANDIDATE:
  raise RuntimeError("Release file fingerprints changed")
 if patch(old)!=new:raise RuntimeError("Candidate is not exact pinned patch")
 if api.repo_info(SPACE,repo_type="space").sha!=START or read(api,START)!=old:
  raise RuntimeError("Live source changed; no publish")
 revision=None
 try:
  revision=commit(api,START,new,"§C 1.1.44: commit original Qwen vision text without rerunning Chat")
  emit("PUBLISHED",revision=revision)
  if read(api,revision)!=new:raise RuntimeError("Exact committed source readback failed")
  emit("EXACT_READBACK_PASS",revision=revision)
  verify(api,revision)
 except Exception as error:
  emit("RELEASE_REJECTED",revision=revision,reason=str(error)[:250])
  if revision and api.repo_info(SPACE,repo_type="space").sha==revision:
   rollback=commit(api,revision,old,"Rollback §C 1.1.44 to exact previous sources")
   emit("EXACT_SOURCE_ROLLBACK",revision=rollback)
  else:emit("ROLLBACK_UNSAFE_CONCURRENT_HEAD")
  raise

if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["publish"]):raise SystemExit("Usage: inspect|publish")
 api=client()
 if sys.argv[1]=="inspect":inspect(api)
 else:publish(api)
