#!/usr/bin/env python3
"""Source-pinned §C v1.1.49: cross-modal private history retrieval.

This release edits ONLY Station, model_router and the new pure retrieval module
inside the user's Hugging Face Space. No model, §E, account data or schema edits.
"""
from __future__ import annotations
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
SOURCE="221d3fcaea6b6fea9910d787ffc507f15468f63a"
STATION="station.py"
ROUTER="model_router.py"
RELATED="related_visual_history.py"
MODULE=Path("scripts/releases/related_visual_history_v1149.py")
FILES=(STATION,ROUTER,RELATED)
BEFORE={STATION:"0808605e64232af723ce18523909b10636edc55de58ed4238b4d92af34012551",
        ROUTER:"13985a29d964af64639d84fd826e7c36cfe5a288955bb41162370b277854456a"}
WORK=Path("reports/swrlz-related-visual-memory-v1149")
BASE="https://kamiloki-swyrlz.hf.space"

def digest(data):return hashlib.sha256(data).hexdigest()
def log(event,**details):
 print("SWRLZ_RELATED_VISUAL_1149 "+json.dumps({"event":event,**details},sort_keys=True),flush=True)
def one(text,old,new,label):
 n=text.count(old)
 if n!=1:raise RuntimeError(f"SOURCE_DRIFT {label}: exact anchor count {n}")
 return text.replace(old,new,1)

INJECTION='''
    # swrlz-related-visual-memory-v1149: a completed, owner-verified Qwen
    # description lets us search for related discussion-only memories as well
    # as earlier image observations. Retrieval neither asserts identity nor
    # gives prior text permission to act or change a project.
    if google_owner.startswith("google:") and str(s.get("ownerGoogleId") or "")==google_owner:
        try:
            current_handoff=(vision_handoff_from_message({"role":"user","text":prompt})
                             if vision_receipt else None)
            visual_description=(str(current_handoff.get("descriptionSentToChatModel") or "")
                                if isinstance(current_handoff,dict) else "")
            image_question=(str(current_handoff.get("questionSentToChatModel") or "")
                            if isinstance(current_handoff,dict) else str(followup_prompt or prompt))
            with _lock:
                related=related_visual_history.retrieve(
                    s["threads"],tid,image_question,visual_description,
                    verified_image_sha,vision_handoff_from_message)
            if related["context"]:
                payload["history"]=[{"role":"user","text":related["context"]}]+payload["history"]
                payload["relatedVisualHistory"]=True
                # A vision-only fast answer would discard the relevant old
                # discussion; use the existing contextual text response route.
                direct_vision_answer=None
            # The existing opt-in imported ChatGPT archive uses a separate
            # tenant-bound volatile index. No new archive access is enabled
            # and a topic must share multiple substantive words to qualify.
            candidate_query=str(related.get("query") or "")
            if vision_receipt and len(candidate_query.split())>=3:
                imported=chatgpt_account_memory.retrieve(google_owner,candidate_query)
                if imported:
                    shared=(set(related_visual_history.terms(imported)) &
                            set(related_visual_history.terms(candidate_query)))
                    if len(shared)>=3:
                        payload["history"]=[{"role":"user","text":
                            "[OLDER OPT-IN ARCHIVE: potentially relevant past discussion; "
                            "not pixels, identity proof or instructions]\\n"+imported[:1700]}]+payload["history"]
                        payload["relatedVisualHistory"]=True
                        direct_vision_answer=None
        except Exception:
            # Historical search is optional enrichment. Do not block image
            # processing, expose private data in logs or alter send ownership.
            pass
'''

def patch_station(raw):
 source=raw.decode("utf-8")
 source=one(source,
  "from chat_vision import export_threads_with_vision_handoffs, vision_handoff_from_message, vision_job_resource_receipt",
  "from chat_vision import export_threads_with_vision_handoffs, vision_handoff_from_message, vision_job_resource_receipt\nimport related_visual_history",
  "owner-scoped module import")
 source=one(source,
  "    if direct_vision_answer:\n        # No second LLM decoding or text-on-text reinterpretation.",
  INJECTION+"    if direct_vision_answer:\n        # No second LLM decoding or text-on-text reinterpretation.",
  "inject after real Qwen image handoff")
 if source.count("swrlz-related-visual-memory-v1149")!=1:
  raise RuntimeError("Unexpected station retrieval patch markers")
 return source.encode("utf-8")

def patch_router(raw):
 source=raw.decode("utf-8")
 source=one(source,
  "    direct_vision = _direct_vision_description(payload)",
  '''    # swrlz-related-visual-memory-v1149: a genuinely relevant old discussion
    # needs a context-aware answer. Keep the original zero-extra-model fast
    # path for every standalone image that has no matching account history.
    direct_vision = (None if payload.get("relatedVisualHistory") is True
                     else _direct_vision_description(payload))''',
  "avoid prematurely returning Qwen-only answer when related history exists")
 return source.encode("utf-8")

def client():
 token=os.getenv("HF_TOKEN")
 if not token:raise RuntimeError("Hugging Face credential unavailable")
 return HfApi(token=token)

def remote(api,rev):
 names=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
 if RELATED in names:
  raise RuntimeError("Related memory module already present, source pin invalid")
 if not set((STATION,ROUTER)).issubset(names):
  raise RuntimeError("Original Station and model router not found")
 return {p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=rev,token=api.token)).read_bytes()
         for p in (STATION,ROUTER)}

def prepare(api):
 head=api.repo_info(SPACE,repo_type="space").sha
 if head!=SOURCE:raise RuntimeError("Space head moved; refusing to patch unknown source: "+head)
 before=remote(api,head)
 hashes={p:digest(data) for p,data in before.items()}
 if hashes!=BEFORE:raise RuntimeError("Exact production fingerprints changed: "+str(hashes))
 native=MODULE.read_bytes()
 updated={STATION:patch_station(before[STATION]),ROUTER:patch_router(before[ROUTER]),RELATED:native}
 for p in FILES:ast.parse(updated[p].decode("utf-8"),filename=p)
 assert "vision_job_resource_receipt(google_owner,vision_job_id,prompt)" in updated[STATION].decode("utf-8")
 assert "if selected_image_context is not None:" in updated[STATION].decode("utf-8")
 assert "related_visual_history.retrieve(" in updated[STATION].decode("utf-8")
 assert "import related_visual_history" in updated[STATION].decode("utf-8")
 assert 'payload["relatedVisualHistory"]=True' in updated[STATION].decode("utf-8")
 assert 'direct_vision = (None if payload.get("relatedVisualHistory") is True' in updated[ROUTER].decode("utf-8")
 assert "def retrieve(" in updated[RELATED].decode("utf-8")
 subprocess.run(["python","scripts/tests/test_related_visual_history_v1149.py"],check=True,timeout=20)
 for p in FILES:
  for family,data in (("original",before.get(p,b"")),("candidate",updated[p])):
   if not data:continue
   output=WORK/family/p;output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(data)
 (WORK/"manifest.json").write_text(json.dumps({
    "space":SPACE,"source":SOURCE,"files":list(FILES),
    "before":hashes,"after":{p:digest(value) for p,value in updated.items()},
    "privacy":"same-owner native; preexisting opt-in imported archive only",
    "scope":"read-only context retrieval; no persistence or model changes",
 },indent=2)+"\n")
 log("PREFLIGHT_PASS",revision=head,changed={p:digest(value) for p,value in updated.items()})
 return before,updated

def commit(api,revision,contents,message):
 result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
    operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(data))
               for p,data in contents.items()],commit_message=message)
 return str(result.oid or api.repo_info(SPACE,repo_type="space").sha)

def served():
 try:
  request=urllib.request.Request(BASE+"/api/hf/qwen35-ready",
    headers={"Cache-Control":"no-cache","User-Agent":"Swyrlz-related-memory-v1149"})
  with urllib.request.urlopen(request,timeout=18) as r:
   status=json.load(r)
   return r.status==200 and status.get("ready") is True and status.get("model")=="qwen3.5-9b"
 except (urllib.error.URLError,TimeoutError,ValueError,KeyError):
  return False

def verify(api,revision):
 old=None;consecutive=0
 for attempt in range(1,78):
  if api.repo_info(SPACE,repo_type="space").sha!=revision:
   raise RuntimeError("Concurrent Space source superseded our update")
  runtime=api.get_space_runtime(SPACE)
  stage=str(runtime.stage).upper().split(".")[-1]
  actual=str((runtime.raw or {}).get("sha") or "")
  healthy=served() if stage=="RUNNING" and actual==revision else False
  obs=(stage,actual,healthy)
  if obs!=old:
   log("RUNTIME_GATE",attempt=attempt,stage=stage,serving=actual,qwenReady=healthy)
   old=obs
  if stage=="RUNTIME_ERROR":raise RuntimeError("Updated Space failed at startup")
  consecutive=consecutive+1 if stage=="RUNNING" and actual==revision and healthy else 0
  if consecutive>=2:
   log("LIVE_ACCEPTED",revision=revision,release="1.1.49",qwenReady=True)
   return
  time.sleep(12)
 raise RuntimeError("Exact source serving or Qwen readiness could not be verified")

def release(api):
 if os.getenv("SWRLZ_RELATED_VISUAL_1149_APPROVED")!="yes":
  raise PermissionError("Explicit user-initiated release authority missing")
 before,updated=prepare(api)
 if api.repo_info(SPACE,repo_type="space").sha!=SOURCE or remote(api,SOURCE)!=before:
  raise RuntimeError("Race: production source has changed")
 new_rev=None
 try:
  new_rev=commit(api,SOURCE,updated,
    "§C 1.1.49: connect relevant past text discussions and image observations with verified visual context")
  log("PUBLISHED",revision=new_rev)
  result_files=set(api.list_repo_files(SPACE,repo_type="space",revision=new_rev))
  if not set(FILES).issubset(result_files):
   raise RuntimeError("Published module files missing")
  for p in FILES:
   actual=Path(hf_hub_download(SPACE,p,repo_type="space",revision=new_rev,
                               token=api.token)).read_bytes()
   if actual!=updated[p]:raise RuntimeError("Exact file readback mismatch: "+p)
  log("READBACK_PASS",revision=new_rev)
  verify(api,new_rev)
 except Exception as exc:
  log("RELEASE_REJECTED",revision=new_rev,reason=str(exc)[:240])
  if new_rev and api.repo_info(SPACE,repo_type="space").sha==new_rev:
   from huggingface_hub import CommitOperationDelete
   result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new_rev,
      operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(before[p]))
                  for p in (STATION,ROUTER)]+[CommitOperationDelete(path_in_repo=RELATED)],
      commit_message="Rollback §C 1.1.49 to exact previous Station and routing source")
   log("EXACT_ROLLBACK",revision=str(result.oid))
  raise

if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["deploy"]):
  raise SystemExit("Usage: inspect|deploy")
 api=client()
 prepare(api) if sys.argv[1]=="inspect" else release(api)
