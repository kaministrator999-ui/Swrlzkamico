#!/usr/bin/env python3
"""Source-pinned §C media controls and single-Qwen image-analysis fast path.

Preserve the live Qwen3.5-9B GGUF+mmproj owner, Station endpoints, account state,
and long-running generation semantics. Attachments can be prepared while an
acknowledged model response is streaming; Send remains guarded.
"""
from __future__ import annotations
import ast, hashlib, io, json, os, re, subprocess, tempfile, time, urllib.error, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
SOURCE_REVISION="401d3025870a6338f8f4a53c73b18dadd7cc627a"
UI="chat/§wyrlz/index.html"
ROUTER="model_router.py"
FILES=(UI,ROUTER)
BASE="https://kamiloki-swyrlz.hf.space"
BACKUP=Path("reports/swrlz-media-qwen-unified-v1141")
MARK="swrlz-media-qwen-unified-v1141"
EXPECTED={
 UI:"5cf96b05dfd0d78b97de6917edff4313f097769e52d4cc3d007fff1157cdd0cb",
 ROUTER:"6b29ffa91081b9c82beaeb80c96148182bd28572430d3fe31633b921146441cd"
}

def digest(b):return hashlib.sha256(b).hexdigest()
def emit(stage,**details):
 print("SWRLZ_MEDIA_QWEN_1141",json.dumps({"event":stage,**details},sort_keys=True),flush=True)
def one(s,before,after,label):
 n=s.count(before)
 if n!=1:raise RuntimeError(f"SOURCE_DRIFT {label}: expected one, got {n}")
 return s.replace(before,after,1)
class DomIds(HTMLParser):
 def __init__(self):super().__init__();self.ids=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if d.get("id"):self.ids.append(d["id"])
def dom_ids(source):
 parser=DomIds();parser.feed(source);return parser.ids

def patch_ui(raw):
 old=raw.decode("utf-8")
 if old.count('name="swrlz-chat-version" content="1.1.40"')!=1:
  raise RuntimeError("Live Chat is no longer at the verified 1.1.40 source")
 if "§C 1.0.60 — Unified professional interface" not in old:
  raise RuntimeError("Professional UI design marker missing")
 if MARK in old:raise RuntimeError("Media staging update already applied")
 new=one(old,
   '    .composer-media-button:disabled{opacity:.42;cursor:default}',
   '''    .composer-media-button:disabled{opacity:.42;cursor:default}
     /* swrlz-media-qwen-unified-v1141: visually distinguish enabled tools. */
     .composer-media-button:not(:disabled){opacity:1;color:#effbff;
       background:linear-gradient(180deg,rgba(27,91,124,.97),rgba(15,60,89,.97));
       border-color:rgba(128,223,251,.73);
       box-shadow:inset 0 1px 0 rgba(208,247,255,.12),0 2px 8px rgba(0,5,15,.15)}
     .composer-media-button:hover:not(:disabled){border-color:#9cecff;background:#184e6e}
     .composer-media-button:focus-visible{outline:2px solid #92e7ff;outline-offset:2px}
     .composer-media-button:active:not(:disabled){transform:scale(.97)}
     @media(prefers-reduced-motion:reduce){.composer-media-button{transition:none!important}}''',
   "visible enabled controls")
 new=one(new,
  '      const stationBusy=()=>sending||stationGenerationActive();',
  '''      // swrlz-media-qwen-unified-v1141: independent composer staging is safe
      // once the original submission has been accepted or its image upload has
      // detached from the draft. Send remains locked until terminal.
      let mediaStagingAvailableDuringSend=false;
      const stationBusy=()=>sending||stationGenerationActive();''',
  "media staging ownership")
 new=one(new,
  '        sendButton.disabled=stationBusy();imagePickButton.disabled=stationBusy();micButton.disabled=stationBusy();',
  '''        sendButton.disabled=stationBusy();
        const stageAllowed=!sending||!!stationAcknowledgedRequest||mediaStagingAvailableDuringSend;
        imagePickButton.disabled=!stageAllowed;
        projectFilePickButton.disabled=!stageAllowed;
        micButton.disabled=!stageAllowed;''',
  "independent media from generation busy")
 new=one(new,
  '        const restorePendingVisionDraft=()=>{',
  '''        mediaStagingAvailableDuringSend=false;
        const restorePendingVisionDraft=()=>{''',
  "new turn staging initialization")
 new=one(new,
  '''            if(selectedImage===attachment)selectedImage=null;
            updateImagePreview();resizeComposer();composerNotice("");
            const description=await requestVisionDescription(attachment,draftText,activity);''',
  '''            if(selectedImage===attachment)selectedImage=null;
            updateImagePreview();resizeComposer();composerNotice("");
            // The image job owns its immutable uploaded bytes. New attachments
            // belong to the NEXT draft and cannot change that in-flight job.
            mediaStagingAvailableDuringSend=true;syncStationControls();
            const description=await requestVisionDescription(attachment,draftText,activity);''',
  "enable next turn staging after vision detach")
 new=one(new,
  '''          prompt.value=""; resizeComposer(); followLatest=false; responseStartAnchorRequestId=""; renderConversation(localThread); renderThreads(); renderStationGeneration();''',
  '''          if(prompt.value.trim()===draftText)prompt.value="";
          resizeComposer(); followLatest=false; responseStartAnchorRequestId=""; renderConversation(localThread); renderThreads(); renderStationGeneration();''',
  "retain user's next draft")
 new=one(new,
  '''          sendAcknowledged=true;
          clearSelectedProjectFiles();
          stationAcknowledgedRequest={requestId,threadId:submission.threadId};''',
  '''          sendAcknowledged=true;
          // Clear only the source bundle actually submitted; keep anything
          // the user selected meanwhile for their next conversation turn.
          if(selectedProjectFiles.length===projectFiles.length&&
             selectedProjectFiles.every((file,index)=>file===projectFiles[index]))
            clearSelectedProjectFiles();
          stationAcknowledgedRequest={requestId,threadId:submission.threadId};''',
  "do not discard newer file attachment")
 new=one(new,
  '''          setCompanionState("accepted","send-ack");
          renderStationGeneration();
          try{''',
  '''          setCompanionState("accepted","send-ack");
          renderStationGeneration();syncStationControls();
          try{''',
  "unlock attachment staging at confirmed send")
 new=one(new,
  '''            syncStationControls();projectFilePickButton.disabled=false;if(sendProjectionEpoch===accountProjectionEpoch)scheduleStationSync();''',
  '''            mediaStagingAvailableDuringSend=false;
            syncStationControls();if(sendProjectionEpoch===accountProjectionEpoch)scheduleStationSync();''',
  "centralize media control sync on terminal")
 new=one(new,
  '<meta name="swrlz-chat-version" content="1.1.40">',
  '<meta name="swrlz-chat-version" content="1.1.41">',
  "release version")
 if dom_ids(old)!=dom_ids(new):raise RuntimeError("Component IDs changed in UI-only revision")
 if "projectFilePickButton.disabled=!stageAllowed" not in new:
  raise RuntimeError("File control still lacks canonical state synchronization")
 if new.count(MARK)!=2:raise RuntimeError("Unexpected patch marker count")
 if new.count("const stationBusy=")!=1 or new.count("const syncStationControls=")!=1:
  raise RuntimeError("Duplicate send ownership detected")
 return new.encode("utf-8")

def patch_router(raw):
 old=raw.decode("utf-8")
 if MARK in old:raise RuntimeError("Vision fast-path already installed")
 new=one(old,
  '''        "tell me what is in this picture",
    }
    if question not in direct_questions:''',
  '''        "tell me what is in this picture",
        # swrlz-media-qwen-unified-v1141: same resident Qwen already inspected
        # pixels with mmproj; do not run an unnecessary second Qwen pass for
        # ordinary, self-contained visual inspection. Comparison, coding and
        # history-dependent requests still take the full contextual route.
        "analyze this image",
        "analyze the image",
        "analyze this picture",
        "analyze the picture",
        "analyze this photo",
        "analyze this screenshot",
        "inspect this image",
        "inspect this picture",
        "describe what you see in this image",
        "what do you notice in this image",
        "what can you tell me about this image",
        "take a look at this image",
    }
    if question not in direct_questions:''',
  "self-contained Qwen vision fast-path")
 ast.parse(new,filename=ROUTER)
 for phrase in ("projectFileEvidence","_ground_vision_handoff","_direct_vision_description","ModelRoute("):
  if old.count(phrase)!=new.count(phrase):
   raise RuntimeError("Model source evidence/routing contract drift: "+phrase)
 return new.encode("utf-8")

def api():
 token=os.getenv("HF_TOKEN")
 if not token:raise RuntimeError("Authorized Hugging Face credential required")
 return HfApi(token=token)

def get_files(client,rev):
 files=set(client.list_repo_files(SPACE,repo_type="space",revision=rev))
 if not set(FILES).issubset(files):raise RuntimeError("Live Chat media source absent")
 return {p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=rev,
                     token=client.token)).read_bytes() for p in FILES}

def prepare(client):
 live=client.repo_info(SPACE,repo_type="space").sha
 if live!=SOURCE_REVISION:raise RuntimeError("Space head changed; inspect newer source: "+live)
 original=get_files(client,live)
 hashes={p:digest(content) for p,content in original.items()}
 if hashes!=EXPECTED:raise RuntimeError("Exact live file fingerprints changed: "+str(hashes))
 edited={UI:patch_ui(original[UI]),ROUTER:patch_router(original[ROUTER])}
 if not all(edited[p]!=original[p] for p in FILES):raise RuntimeError("Patch is empty")
 BACKUP.mkdir(parents=True,exist_ok=True)
 for p in FILES:
  for group,data in (("original",original[p]),("candidate",edited[p])):
   f=BACKUP/group/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 (BACKUP/"manifest.json").write_text(json.dumps({
  "space":SPACE,"sourceRevision":live,"files":list(FILES),"before":hashes,
  "after":{p:digest(edited[p]) for p in FILES},
  "modelUnchanged":"twoody/Qwen3.5-9B-GGUF with mmproj-F16.gguf",
  "release":"Chat 1.1.41 / image fast path / enabled next-turn media staging"
 },indent=2)+"\n")
 emit("PREFLIGHT_OK",revision=live,hashes={p:digest(edited[p]) for p in FILES})
 return edited

def commit(client,rev,data,label):
 response=client.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
  operations=[CommitOperationAdd(path_in_repo=k,path_or_fileobj=io.BytesIO(v)) for k,v in data.items()],
  commit_message=label)
 return str(response.oid or client.repo_info(SPACE,repo_type="space").sha)

def served():
 for path in ("/chat/%C2%A7wyrlz","/"):
  try:
   req=urllib.request.Request(BASE+path+"?v1141="+str(time.monotonic_ns()),
    headers={"Cache-Control":"no-cache","User-Agent":"Swrlz-Media-Qwen-1141"})
   with urllib.request.urlopen(req,timeout=17) as reply:
    html=reply.read(750000).decode("utf-8",errors="replace")
    if (reply.status==200 and MARK in html and
        'swrlz-chat-version" content="1.1.41"' in html):
     return True,path
  except (urllib.error.URLError,TimeoutError):pass
 return False,"page did not serve candidate version"

def verify(client,rev):
 previous=None;stable=0
 for i in range(1,61):
  if client.repo_info(SPACE,repo_type="space").sha!=rev:
   raise RuntimeError("Another Space commit superseded the release")
  state=client.get_space_runtime(SPACE)
  stage=str(state.stage).upper().split(".")[-1]
  serving=str((state.raw or {}).get("sha") or "")
  ok,path=served() if stage=="RUNNING" and serving==rev else (False,"pending")
  obs=(stage,serving,ok)
  if obs!=previous:
   emit("REVISION_GATE",attempt=i,stage=stage,serving=serving,expected=rev,served=ok)
   previous=obs
  if stage=="RUNTIME_ERROR":raise RuntimeError("Chat runtime failed after release")
  if stage=="RUNNING" and serving==rev and ok:
   stable+=1
   if stable>=2:
    emit("LIVE_ACCEPTED",revision=rev,path=path,chatVersion="1.1.41")
    return
  else:stable=0
  time.sleep(12)
 raise RuntimeError("Exact live Chat 1.1.41 was not verified as RUNNING")

def publish(client):
 if os.getenv("SWRLZ_MEDIA_QWEN_1141_APPROVED")!="yes":
  raise PermissionError("Explicit approved exact-source release is required")
 manifest=json.loads((BACKUP/"manifest.json").read_text())
 if manifest["sourceRevision"]!=SOURCE_REVISION or manifest["space"]!=SPACE:
  raise RuntimeError("Source manifest mismatch")
 old={p:(BACKUP/"original"/p).read_bytes() for p in FILES}
 updated={p:(BACKUP/"candidate"/p).read_bytes() for p in FILES}
 if ({p:digest(old[p]) for p in FILES}!=manifest["before"] or
     {p:digest(updated[p]) for p in FILES}!=manifest["after"]):
  raise RuntimeError("Snapshot checksum differs")
 if updated!={UI:patch_ui(old[UI]),ROUTER:patch_router(old[ROUTER])}:
  raise RuntimeError("Release patch differed from verified source")
 if client.repo_info(SPACE,repo_type="space").sha!=SOURCE_REVISION or get_files(client,SOURCE_REVISION)!=old:
  raise RuntimeError("Live source drift; no publish")
 released=None
 try:
  released=commit(client,SOURCE_REVISION,updated,
   "§C 1.1.41: usable media controls and single-Qwen image fast path")
  emit("PUBLISHED",revision=released)
  if get_files(client,released)!=updated:raise RuntimeError("Exact readback failed")
  emit("READBACK_OK",revision=released)
  verify(client,released)
 except Exception as error:
  emit("RELEASE_REJECTED",revision=released,reason=str(error)[:180])
  if released and client.repo_info(SPACE,repo_type="space").sha==released:
   restored=commit(client,released,old,"Rollback §C 1.1.41 media/Qwen to exact previous source")
   emit("EXACT_SOURCE_ROLLBACK",revision=restored)
  elif released:
   emit("ROLLBACK_BLOCKED_CONCURRENT_CHANGE")
  raise

if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["publish"]):
  raise SystemExit("Usage: inspect|publish")
 client=api()
 if sys.argv[1]=="inspect":prepare(client)
 else:publish(client)
