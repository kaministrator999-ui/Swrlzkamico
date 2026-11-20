#!/usr/bin/env python3
"""Source-pinned §C 1.1.45 single assistant bubble and exact-image history.

The candidate is a reproducible binary-verified patch against the REAL Space
revision. Only three approved Space files are committed; all others, including
§E, weights and account storage, remain untouched.
"""
from __future__ import annotations
import ast, base64, hashlib, io, json, lzma, os, pathlib, re
import shutil, subprocess, time, urllib.error, urllib.request
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
SOURCE="70905ffeebd77d21fc99982f6f8f9a5a19a22018"
FILE_NAMES=("station.py","chat_vision.py","chat/§wyrlz/index.html")
BEFORE={
 "station.py":"7aebbab687b8df7c5bdd1e4da583d7333df56bff957ef755b8b4dcc39751f4b0",
 "chat_vision.py":"5c32a8d22dd2a3770573c5ca9ee703bbe8e10c8adffbdea52dfc7a43ba2c0290",
 "chat/§wyrlz/index.html":"842a76fbc525186209ff2cbed300c9b11f73d5733d0cea34c98067b4a21ab67d"}
AFTER={
 "station.py":"494ba42f36728a21b774b904f1a5a83ec8b95e3ce4f111353c85fb1084bd3868",
 "chat_vision.py":"03eadbf814dc1a68dbb7a32c70a94ce95374d026b7b3ccfeefe76912f83665d6",
 "chat/§wyrlz/index.html":"e12f2d3a2e16f759474e75870075b8de89bdc8e67aa5a01cf084ca313849666b"}
PATCH_HASH="5875e2589aac3663e61d82f1028cfe4fd3e8ac1293489f4c69aee5f661d394b4"
PARTS=("scripts/releases/swrlz_image1145_patch_part1.b64",
       "scripts/releases/swrlz_image1145_patch_part2a.b64",
       "scripts/releases/swrlz_image1145_patch_part2b.b64")
WORK=pathlib.Path("reports/swrlz-image-1145")
BASE="https://kamiloki-swyrlz.hf.space"

def h(data): return hashlib.sha256(data).hexdigest()
def record(event,**fields):
 print("SWRLZ_IMAGE_1145 "+json.dumps({"event":event,**fields},sort_keys=True),flush=True)

def get_client():
 token=os.environ.get("HF_TOKEN")
 if not token:raise RuntimeError("HF_TOKEN missing from release authority")
 return HfApi(token=token)

def originals(api,revision):
 return {p:pathlib.Path(hf_hub_download(SPACE,p,repo_type="space",
             revision=revision,token=api.token)).read_bytes() for p in FILE_NAMES}

def check_hashes(data,expected,label):
 actual={p:h(data[p]) for p in FILE_NAMES}
 if actual!=expected:raise RuntimeError(label+" unexpected file fingerprints: "+str(actual))

def make_patch():
 encoded="".join(pathlib.Path(part).read_text().strip() for part in PARTS)
 if len(encoded)!=11512:raise RuntimeError("Patch was not copied completely")
 patch=lzma.decompress(base64.b64decode(encoded,validate=True))
 if h(patch)!=PATCH_HASH:raise RuntimeError("Authenticated source patch SHA mismatch")
 paths=set(re.findall(r"^\+\+\+ b/([^\r\n]+)",patch.decode(),re.M))
 if paths!=set(FILE_NAMES):raise RuntimeError("Patch changed unexpected Space files: "+str(paths))
 return patch

def stage(api):
 head=api.repo_info(SPACE,repo_type="space").sha
 if head!=SOURCE:raise RuntimeError("Space HEAD changed, no mutation: "+head)
 source=originals(api,head)
 check_hashes(source,BEFORE,"SOURCE_DRIFT")
 patch=make_patch()
 for name in FILE_NAMES:
  path=WORK/"original"/name
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(source[name])
  copy=WORK/"candidate"/name
  copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(source[name])
 process=subprocess.run(["patch","--batch","--fuzz=0","-p1"],
                       cwd=WORK/"candidate",input=patch,stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,timeout=40)
 if process.returncode:
  raise RuntimeError("Source patch failed clean application: "+process.stdout.decode(errors="replace")[:500])
 candidate={p:(WORK/"candidate"/p).read_bytes() for p in FILE_NAMES}
 check_hashes(candidate,AFTER,"CANDIDATE_DRIFT")
 for name in ("station.py","chat_vision.py"):ast.parse(candidate[name],filename=name)
 html=candidate["chat/§wyrlz/index.html"].decode()
 if ('swrlz-chat-version" content="1.1.45"' not in html or
     'swrlz-chat-design-version" content="1.0.60"' not in html):
  raise RuntimeError("Production Chat version/layout did not survive")
 scripts=[x for x in re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>",html,re.I) if x.strip()]
 if len(scripts)!=1:raise RuntimeError("Chat has changed JavaScript entrypoints")
 js=WORK/"chat.js";js.write_text(scripts[0])
 subprocess.run(["node","--check",str(js.resolve())],check=True,timeout=30)
 assert "imageSha256" in candidate["station.py"].decode()
 assert "reuseImageContextThreadId" in candidate["station.py"].decode()
 assert 'const imageMemoryMatches=' in html
 assert 'classList.add("rendered-message","station-live-message")' in html
 (WORK/"manifest.json").write_text(json.dumps({"space":SPACE,"revision":head,
    "files":list(FILE_NAMES),"before":BEFORE,"after":AFTER,"patchSha256":PATCH_HASH},indent=2)+"\n")
 record("PREFLIGHT_PASS",revision=head,after=AFTER)
 return source,candidate

def commit(api,head,contents,message):
 result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=head,
  operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(contents[p]))
              for p in FILE_NAMES],commit_message=message)
 return str(result.oid or api.repo_info(SPACE,repo_type="space").sha)

def page_and_qwen_ready():
 try:
  request=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz?release=1145",
      headers={"Cache-Control":"no-cache","User-Agent":"Swrlz-image-memory-1145"})
  with urllib.request.urlopen(request,timeout=20) as result:
   html=result.read(950000).decode("utf-8","replace")
   if (result.status!=200 or 'swrlz-chat-version" content="1.1.45"' not in html
       or "imageReuseSelect" not in html):return False
  request=urllib.request.Request(BASE+"/api/hf/qwen35-ready",
                                 headers={"Cache-Control":"no-cache"})
  with urllib.request.urlopen(request,timeout=20) as result:
   data=json.load(result)
   return (result.status==200 and data.get("ready") is True
           and data.get("model")=="qwen3.5-9b")
 except (urllib.error.URLError,TimeoutError,ValueError,KeyError):return False

def verify(api,revision):
 previous=None;stable=0
 for attempt in range(1,76):
  current=api.repo_info(SPACE,repo_type="space").sha
  if current!=revision:raise RuntimeError("Another Space commit superseded this deployment")
  info=api.get_space_runtime(SPACE)
  phase=str(info.stage).upper().split(".")[-1]
  serving=str((info.raw or {}).get("sha") or "")
  ready=page_and_qwen_ready() if phase=="RUNNING" and serving==revision else False
  observation=(phase,serving,ready)
  if observation!=previous:
   record("LIVE_GATE",attempt=attempt,phase=phase,serving=serving,qwenReady=ready)
   previous=observation
  if phase=="RUNTIME_ERROR":raise RuntimeError("Space runtime error after code release")
  stable=stable+1 if phase=="RUNNING" and serving==revision and ready else 0
  if stable>=2:
   record("LIVE_ACCEPTED",revision=revision,chatVersion="1.1.45",qwenReady=True)
   return
  time.sleep(12)
 raise RuntimeError("Exact live code revision and resident Qwen readiness not confirmed")

def publish(api):
 if os.environ.get("SWRLZ_IMAGE_1145_APPROVED")!="yes":
  raise PermissionError("Approved user-initiated release flag absent")
 original,new=stage(api)
 manifest=json.loads((WORK/"manifest.json").read_text())
 if manifest["revision"]!=SOURCE or manifest["patchSha256"]!=PATCH_HASH:
  raise RuntimeError("Release manifest changed")
 if api.repo_info(SPACE,repo_type="space").sha!=SOURCE or originals(api,SOURCE)!=original:
  raise RuntimeError("Race: Space source changed after candidate built")
 rev=None
 try:
  rev=commit(api,SOURCE,new,
     "§C 1.1.45: one streamed assistant bubble and exact-image account conversation matches")
  record("PUBLISHED",revision=rev)
  check_hashes(originals(api,rev),AFTER,"EXACT_READBACK")
  record("EXACT_READBACK_PASS",revision=rev)
  verify(api,rev)
 except Exception as exc:
  record("RELEASE_REJECTED",revision=rev,reason=str(exc)[:220])
  if rev and api.repo_info(SPACE,repo_type="space").sha==rev:
   rollback=commit(api,rev,original,"Rollback §C 1.1.45 to pre-release exact source")
   record("EXACT_ROLLBACK",revision=rollback)
  else:record("ROLLBACK_NOT_SAFE_CONCURRENT_HEAD")
  raise

if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["publish"]):raise SystemExit("Usage inspect|publish")
 api=get_client()
 stage(api) if sys.argv[1]=="inspect" else publish(api)
