#!/usr/bin/env python3
"""Guarded §C 1.1.46 cross-thread image opt-in patch and Hugging Face release.

Only two files change. Source hashes, patch SHA and new hashes are immutable.
No Qwen model, source image, account database or §E modifications.
"""
from __future__ import annotations
import ast,base64,hashlib,io,json,lzma,os,pathlib,re,subprocess,time,urllib.error,urllib.request
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
SOURCE="5cd7fae054108e123eeb7b36ed866276f18cc9ec"
UI="chat/§wyrlz/index.html"
STATION="station.py"
FILES=(UI,STATION)
BEFORE={
 UI:"e12f2d3a2e16f759474e75870075b8de89bdc8e67aa5a01cf084ca313849666b",
 STATION:"494ba42f36728a21b774b904f1a5a83ec8b95e3ce4f111353c85fb1084bd3868"}
AFTER={
 UI:"81e5d8b4e0c88529bf644411a2179d79e41fb90c8707acfa5e42826a916b7cfb",
 STATION:"da86ee6c232cbbd3496cdce781a82450431b0d23345ee72054194435918888b8"}
PATCH_SHA="54aeb83a3afa8b7602288a7a528c68f249ba018fe68fe506b79071f2995268c6"
PATCH_FILE=pathlib.Path("scripts/releases/swrlz_image_consent_1146.diff.xz.b64")
BACKUP=pathlib.Path("reports/swrlz-image-consent-1146")
URL="https://kamiloki-swyrlz.hf.space"

def sha(data):return hashlib.sha256(data).hexdigest()
def event(kind,**details):print("SWRLZ_IMAGE_CONSENT_1146 "+json.dumps({"event":kind,**details},sort_keys=True),flush=True)
def client():
 token=os.environ.get("HF_TOKEN")
 if not token:raise RuntimeError("Hugging Face credential not available")
 return HfApi(token=token)
def source_files(api,rev):
 return {path:pathlib.Path(hf_hub_download(SPACE,path,repo_type="space",revision=rev,token=api.token)).read_bytes()
         for path in FILES}
def check(contents,expected,label):
 values={p:sha(contents[p]) for p in FILES}
 if values!=expected:raise RuntimeError(label+" source changed "+str(values))
def stage(api):
 live=api.repo_info(SPACE,repo_type="space").sha
 if live!=SOURCE:raise RuntimeError("HF Space changed; no mutation: "+live)
 existing=source_files(api,live);check(existing,BEFORE,"Original")
 patch=lzma.decompress(base64.b64decode(PATCH_FILE.read_text().strip(),validate=True))
 if sha(patch)!=PATCH_SHA:raise RuntimeError("Patch hash mismatch")
 paths=set(re.findall(r"^\+\+\+ b/([^\r\n]+)",patch.decode("utf-8"),re.M))
 if paths!=set(FILES):raise RuntimeError("Patch modifies files outside exact Chat scope")
 for path in FILES:
  original=BACKUP/"original"/path;original.parent.mkdir(parents=True,exist_ok=True);original.write_bytes(existing[path])
  candidate=BACKUP/"candidate"/path;candidate.parent.mkdir(parents=True,exist_ok=True);candidate.write_bytes(existing[path])
 applied=subprocess.run(["patch","--batch","--fuzz=0","-p1"],
    cwd=BACKUP/"candidate",input=patch,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
 if applied.returncode!=0:raise RuntimeError("Patch rejected: "+applied.stdout.decode(errors="replace")[:700])
 updated={path:(BACKUP/"candidate"/path).read_bytes() for path in FILES}
 check(updated,AFTER,"Candidate")
 python=updated[STATION].decode("utf-8");html=updated[UI].decode("utf-8")
 ast.parse(python)
 if 'swrlz-chat-version" content="1.1.46"' not in html or 'swrlz-chat-design-version" content="1.0.60"' not in html:
  raise RuntimeError("Chat version or approved UI baseline lost")
 scripts=[s for s in re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',html,re.I) if s.strip()]
 if len(scripts)!=1:raise RuntimeError("Unexpected Chat JavaScript structure")
 path=BACKUP/"chat.js";path.write_text(scripts[0])
 subprocess.run(["node","--check",str(path.resolve())],check=True,timeout=25)
 checks={
  "freshByDefault":'imageReuseCheckbox.checked=false' in html and 'reuseConfirmedForThreadId:""' in html,
  "freshLabel":'Fresh Qwen analysis selected; no other thread' in html,
  "consciousOptIn":'attachment.reuseConfirmedForThreadId===originalThreadId' in html,
  "capturedBeforeComposerClears":html.index("const explicitImageReuseThreadId=")<html.index('if(selectedImage===attachment)selectedImage=null;'),
  "serverConsentFlag":'reuseImageContextApproved:true' in html,
  "serverRequiresConsent":'if reuse_thread_id and not reuse_approved:' in python,
  "serverRequiresVerifiedImage":'if reuse_thread_id and not verified_image_sha:' in python,
  "serverAccountOwner":'vision_job_resource_receipt(google_owner,vision_job_id,prompt)' in python,
  "serverAccountMatch":'if prior.get("id")==reuse_thread_id and reuse_thread_id!=tid' in python,
  "serverSourceProvenance":'\"imageAnalysisContextMode\":\"cross-thread-explicit\" if selected_image_context else \"fresh\"' in python,
  "clientVerifiesServerMode":'IMAGE_CONTEXT_UNEXPECTED_CROSS_THREAD_REUSE' in html,
  "unchangedModel":'\"visionAnswerReused\":bool(direct_vision_answer)' in python
 }
 event("ACCEPTANCE_CHECKS",checks=checks)
 if not all(checks.values()):raise RuntimeError("Failed contract checks")
 (BACKUP/"manifest.json").write_text(json.dumps({"revision":live,"before":BEFORE,"after":AFTER,"patchSha":PATCH_SHA},indent=2)+"\n")
 event("PREFLIGHT_PASS",revision=live,files=list(FILES))
 return existing,updated
def commit(api,rev,contents,message):
 response=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
     operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(contents[p])) for p in FILES],
     commit_message=message)
 return str(response.oid or api.repo_info(SPACE,repo_type="space").sha)
def ready():
 try:
  with urllib.request.urlopen(urllib.request.Request(URL+"/chat/%C2%A7wyrlz?release=1146",
   headers={"Cache-Control":"no-cache","User-Agent":"Swrlz-image-consent-release"}),timeout=20) as response:
   page=response.read(900000).decode("utf-8","replace")
   if response.status!=200 or 'swrlz-chat-version" content="1.1.46"' not in page or "reuseImageContextApproved:true" not in page:return False
  with urllib.request.urlopen(urllib.request.Request(URL+"/api/hf/qwen35-ready",headers={"Cache-Control":"no-cache"}),timeout=20) as response:
   state=json.load(response)
   return response.status==200 and state.get("ready") is True and state.get("model")=="qwen3.5-9b"
 except (urllib.error.URLError,TimeoutError,ValueError,KeyError):return False
def verify(api,rev):
 previous=None;stable=0
 for attempt in range(1,74):
  if api.repo_info(SPACE,repo_type="space").sha!=rev:raise RuntimeError("Concurrent HF Space head, stop")
  runtime=api.get_space_runtime(SPACE)
  stage=str(runtime.stage).upper().split(".")[-1]
  serving=str((runtime.raw or {}).get("sha") or "")
  okay=ready() if stage=="RUNNING" and serving==rev else False
  status=(stage,serving,okay)
  if status!=previous:event("RUNTIME_GATE",attempt=attempt,stage=stage,serving=serving,qwenReady=okay);previous=status
  if stage=="RUNTIME_ERROR":raise RuntimeError("Space boot failed")
  stable=stable+1 if stage=="RUNNING" and serving==rev and okay else 0
  if stable>=2:event("LIVE_ACCEPTED",revision=rev,version="1.1.46",qwenReady=True);return
  time.sleep(12)
 raise RuntimeError("Exact revised Space and resident Qwen could not be verified")
def deploy(api):
 if os.environ.get("SWRLZ_IMAGE_CONSENT_1146_APPROVED")!="yes":raise PermissionError("Approval not present")
 original,updated=stage(api)
 if api.repo_info(SPACE,repo_type="space").sha!=SOURCE or source_files(api,SOURCE)!=original:
  raise RuntimeError("Race detected: live source diverged")
 current=None
 try:
  current=commit(api,SOURCE,updated,"§C 1.1.46: explicit current-request consent required for cross-thread image history")
  event("PUBLISHED",revision=current)
  check(source_files(api,current),AFTER,"Readback")
  event("EXACT_READBACK_PASS",revision=current)
  verify(api,current)
 except Exception as error:
  event("RELEASE_REJECTED",revision=current,reason=str(error)[:200])
  if current and api.repo_info(SPACE,repo_type="space").sha==current:
   restored=commit(api,current,original,"Rollback §C 1.1.46 to exact previous Chat and Station source")
   event("EXACT_ROLLBACK",revision=restored)
  raise
if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["deploy"]):raise SystemExit("Usage inspect|deploy")
 api=client()
 stage(api) if sys.argv[1]=="inspect" else deploy(api)
