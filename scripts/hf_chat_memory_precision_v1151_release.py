#!/usr/bin/env python3
"""§C v1.1.51: make image/context reuse precise without losing old same-thread images.

Patch only exact pinned HF Space sources. Same-Google-owner boundaries and
Qwen's original-pixel single-pass image analysis remain unchanged.
"""
from __future__ import annotations
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
SOURCE="ba91d6841a1e1242eed9f63716d8f9c3330aeffc"
STATION="station.py"
RELATED="related_visual_history.py"
VISION="chat_vision.py"
FILES=(STATION,RELATED)
EXPECTED={
 STATION:"2b9c178b1de13ce3be5431e63fabca7ebf76df1205eae33083ff6e209c3fdaf7",
 RELATED:"405082d01ea4c6a7d476589f64d04c1f55df43afa67a32b0af1a800101bef071",
 VISION:"1f808c54f95e134b07c2a0804920afa81c07f20b2d660353c3aa2ec519ed8b88"
}
WORK=Path("reports/swrlz-memory-precision-1151")
BASE="https://kamiloki-swyrlz.hf.space"

def sha(value):return hashlib.sha256(value).hexdigest()
def log(event,**kwargs):print("SWRLZ_MEMORY_PRECISION_1151 "+json.dumps({"event":event,**kwargs},sort_keys=True),flush=True)
def replace_one(content,old,new,label):
 count=content.count(old)
 if count!=1:raise RuntimeError(f"SOURCE_DRIFT_{label} exact anchor count={count}")
 return content.replace(old,new,1)

def station_patch(before):
 source=before.decode("utf-8")
 source=replace_one(source,
  '''            matches.sort(key=lambda item:(item[0],item[1]),reverse=True)
            return [row[2] for row in matches[:4]]''',
  '''            # swrlz-vision-exact-context-v1151: before seeing the pixels,
            # unrelated older screenshots are NOT relevant evidence. Different
            # images may still find related discussions after Qwen's analysis
            # through the separate similarity-scored same-owner history route.
            matches=[item for item in matches if item[0]==1]
            matches.sort(key=lambda item:item[1],reverse=True)
            return [row[2] for row in matches[:4]]''',
  "first pass image grounding")
 return source.encode("utf-8")

def related_patch(before):
 source=before.decode("utf-8")
 source=replace_one(source,
  '''    known_threads=sorted(
        (t for t in threads if isinstance(t,dict) and str(t.get("id") or "")!=str(active_thread_id)),
        key=_thread_stamp,reverse=True
    )[:MAX_THREADS]
    docs=[]
    for thread in known_threads:
        messages=[m for m in (thread.get("messages") or [])[-MAX_MESSAGES:] if isinstance(m,dict)]''',
  '''    # swrlz-old-image-thread-recall-v1151: the most recent same-thread
    # messages already reach the model through the normal conversation
    # projection; only older image turns need automatic retrieval here.
    # This also prevents the just-sent image from matching itself.
    known_threads=sorted(
        (t for t in threads if isinstance(t,dict)),
        key=_thread_stamp,reverse=True
    )[:MAX_THREADS]
    docs=[]
    for thread in known_threads:
        messages=thread.get("messages") or []
        if not isinstance(messages,list):continue
        if str(thread.get("id") or "")==str(active_thread_id):
            messages=messages[:-18] if len(messages)>18 else []
        messages=[m for m in messages[-MAX_MESSAGES:] if isinstance(m,dict)]''',
  "include old images from current thread safely")
 return source.encode("utf-8")

def synthetic_tests(station,related):
 # Execute only the bounded helper definition (no app startup / account data).
 program=ast.parse(station.decode("utf-8"),filename="station.py")
 fn=next(node for node in program.body if isinstance(node,ast.FunctionDef)
         and node.name=="_vision_reference_hints")
 old_sha="a"*64
 new_sha="b"*64
 old_msg={"role":"user","createdAt":1730000000000,
          "meta":{"imageSha256":old_sha},
          "handoff":{"descriptionSentToChatModel":"A brown pointed hat with wide folded brim"}}
 more_msg={"role":"user","createdAt":1730010000000,
           "meta":{"imageSha256":"c"*64},
           "handoff":{"descriptionSentToChatModel":"A shiny blue spaceship hovering above an orange planet"}}
 def handoff(msg):return msg.get("handoff")
 owner="google:sample"
 session={"ownerGoogleId":owner,"threads":[{"id":"old","messages":[
    old_msg,{"role":"user","text":"It is the Sorting Hat; that fold is its mouth.",
            "createdAt":1730000001000},more_msg]}]}
 scope={
  "re":re,"_lock":threading.RLock(),
  "_session":lambda _request:("key",session),
  "_refresh_account_chat":lambda *_args,**_kwargs:None,
  "vision_handoff_from_message":handoff
 }
 exec(compile(ast.Module(body=[fn],type_ignores=[]),"<scoped_vision_reference>","exec"),scope)
 hints=scope["_vision_reference_hints"]
 assert hints(None,owner,new_sha,"What do you see?")==[], "unrelated picture must never prime Qwen"
 assert hints(None,"google:other",old_sha,"What do you see?")==[], "account isolation"
 matches=hints(None,owner,old_sha,"What do you see?")
 assert len(matches)==1 and matches[0]["exactSourceImage"] is True, "exact SHA only"
 assert "Sorting Hat" in str(matches[0]["laterUserClarifications"])
 assert "spaceship" not in str(matches)
 # An old image and its user corrections can be recalled on a much later
 # text turn within the same thread; recent turns cannot be double-injected.
 context={}
 exec(compile(related.decode("utf-8"),"<related_visual_history>","exec"),context)
 retrieve=context["retrieve"]
 image={"role":"user","text":"What do you see?",
        "meta":{"imageSha256":old_sha},"createdAt":1730000000000,
        "handoff":{"descriptionSentToChatModel":"A brown pointed hat with a wide folded brim and face"}}
 older=[image,{"role":"user","text":"It is the Sorting Hat; its folds form a mouth.",
              "createdAt":1730000001000}]
 filler=[{"role":"assistant","text":"Some later normal conversation.","createdAt":1730000002000+i}
         for i in range(22)]
 past={"id":"current","title":"Long running sculpt","createdAt":1730000000000,
       "messages":older+filler}
 found=retrieve([past],"current","What about our brown Sorting Hat with wide brim?",
                "",old_sha,handoff)
 assert found["count"]>=1, "older same-thread image not found"
 assert "Sorting Hat" in found["context"] and "later USER clarification" in found["context"]
 assert retrieve([{"id":"current","messages":older}],"current",
                 "What about our Sorting Hat folds and mouth?","",old_sha,handoff)["count"]==0, "recent history should not be re-injected"
 assert retrieve([past],"current","What about this blue spaceship?", "",new_sha,handoff)["count"]==0, "unrelated old image false positive"
 assert retrieve([],"current","What about our Sorting Hat folds?", "",old_sha,handoff)["count"]==0, "no history"
 cross={"id":"other","title":"Other conversation","messages":older}
 assert retrieve([cross],"current","What about our Sorting Hat folds and mouth?",
                 "",old_sha,handoff)["count"]>=1, "cross-thread regression"
 log("SYNTHETIC_TESTS_PASS",scenarios=[
  "no-unrelated-first-vision-hints","only-matching-sha",
  "account-isolation","image-bound-user-corrections",
  "old-same-thread-image","recent-history-exclusion",
  "no-cross-image-contamination","empty-history","cross-thread-preservation"])

def api_client():
 token=os.environ.get("HF_TOKEN")
 if not token:raise RuntimeError("HF_TOKEN unavailable")
 return HfApi(token=token)

def download_source(api,revision):
 return {name:Path(hf_hub_download(SPACE,name,repo_type="space",
                  revision=revision,token=api.token)).read_bytes()
         for name in EXPECTED}

def preflight(api):
 head=api.repo_info(SPACE,repo_type="space").sha
 if head!=SOURCE:raise RuntimeError("Space source moved; no mutation: "+str(head))
 original=download_source(api,SOURCE)
 actual={name:sha(raw) for name,raw in original.items()}
 if actual!=EXPECTED:raise RuntimeError("Pinned production file digest differs: "+str(actual))
 updated={STATION:station_patch(original[STATION]),
          RELATED:related_patch(original[RELATED])}
 for name,raw in updated.items():ast.parse(raw.decode("utf-8"),filename=name)
 synthetic_tests(updated[STATION],updated[RELATED])
 # Existing vision weights, preprocessing, job routing and cross-modal
 # search stay source-identical; this release changes only two Python files.
 assert "analysis_levels = 1" in original[VISION].decode()
 assert "image = image_url" in original[VISION].decode()
 assert "related_visual_history.retrieve(" in updated[STATION].decode()
 assert "conversation_continuity.retrieve(" in updated[STATION].decode()
 assert "matches=[item for item in matches if item[0]==1]" in updated[STATION].decode()
 for name in FILES:
  for version,data in (("before",original[name]),("after",updated[name])):
   dst=WORK/version/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
 (WORK/"manifest.json").write_text(json.dumps({
  "source":SOURCE,"files":list(FILES),"before":actual,
  "after":{p:sha(x) for p,x in updated.items()},
  "inference":"one Qwen image pass",
  "provenance":"same-account, exact SHA before vision; semantic cues after",
  "safety":"no schema change, mutation authority, model weights, or user data"
 },indent=2)+"\n")
 log("PREFLIGHT_PASS",source=SOURCE,files=list(FILES),
     hashes={name:sha(raw) for name,raw in updated.items()})
 return original,updated

def commit(api,parent,files,message):
 res=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=parent,
     operations=[CommitOperationAdd(path_in_repo=name,
                 path_or_fileobj=io.BytesIO(raw)) for name,raw in files.items()],
     commit_message=message)
 return str(res.oid or api.repo_info(SPACE,repo_type="space").sha)

def ready():
 try:
  req=urllib.request.Request(BASE+"/api/hf/qwen35-ready",
      headers={"Cache-Control":"no-cache","User-Agent":"Swyrlz-memory-precision-1151"})
  with urllib.request.urlopen(req,timeout=18) as response:
   payload=json.load(response)
   return response.status==200 and payload.get("ready") is True and payload.get("model")=="qwen3.5-9b"
 except (urllib.error.URLError,TimeoutError,ValueError,KeyError):
  return False

def live_gate(api,revision):
 previous=None;stable=0
 for attempt in range(1,79):
  if api.repo_info(SPACE,repo_type="space").sha!=revision:
   raise RuntimeError("Concurrent Space mutation")
  status=api.get_space_runtime(SPACE)
  stage=str(status.stage).upper().split(".")[-1]
  serving=str((status.raw or {}).get("sha") or "")
  healthy=ready() if stage=="RUNNING" and serving==revision else False
  current=(stage,serving,healthy)
  if current!=previous:
   log("RUNTIME_GATE",attempt=attempt,stage=stage,serving=serving,qwenReady=healthy)
   previous=current
  if stage=="RUNTIME_ERROR":raise RuntimeError("Space crashed after release")
  stable=stable+1 if stage=="RUNNING" and serving==revision and healthy else 0
  if stable>=2:
   log("LIVE_ACCEPTED",revision=revision,version="1.1.51",qwenReady=True);return
  time.sleep(12)
 raise RuntimeError("No confirmed healthy exact-revision Space runtime")

def deploy(api):
 if os.environ.get("SWRLZ_MEMORY_PRECISION_1151_APPROVED")!="yes":
  raise PermissionError("User-authorized release flag missing")
 originals,updated=preflight(api)
 if api.repo_info(SPACE,repo_type="space").sha!=SOURCE or download_source(api,SOURCE)!=originals:
  raise RuntimeError("Production changed between preflight and publish")
 release=None
 try:
  release=commit(api,SOURCE,updated,
    "§C 1.1.51: prevent unrelated vision hint contamination; recall older same-thread images")
  log("PUBLISHED",revision=release)
  for name,expected in updated.items():
   actual=Path(hf_hub_download(SPACE,name,repo_type="space",revision=release,
                        token=api.token)).read_bytes()
   if actual!=expected:raise RuntimeError("Source readback mismatch: "+name)
  log("EXACT_READBACK_PASS",revision=release)
  live_gate(api,release)
 except Exception as exc:
  log("RELEASE_REJECTED",release=release,errorType=type(exc).__name__,detail=str(exc)[:240])
  if release and api.repo_info(SPACE,repo_type="space").sha==release:
   rev=commit(api,release,{p:originals[p] for p in FILES},
              "Rollback §C 1.1.51 to pinned pre-change vision and history sources")
   log("EXACT_ROLLBACK",revision=rev)
  raise

if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["deploy"]):raise SystemExit("Usage: inspect|deploy")
 client=api_client()
 preflight(client) if sys.argv[1]=="inspect" else deploy(client)
