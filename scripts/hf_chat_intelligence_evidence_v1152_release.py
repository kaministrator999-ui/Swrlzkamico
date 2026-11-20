#!/usr/bin/env python3
"""§C v1.1.52: use historical statements as typed evidence, not fabricated turns.

Only exact pinned HF source files are modified; no user data is read for the
preflight. Production rollback is attempted upon post-publish failure.
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
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
REVISION="f5ebce144a1f6f7c16d89754e5308e3fc59f8bb2"
STATION="station.py"
BRAIN="lfm2_700m_engine.py"
FALLBACK="original_engine.py"
HELPER="historical_evidence.py"
FILE_SET=(STATION,BRAIN,FALLBACK,HELPER)
ORIGINALS={
 STATION:"2100abaff7fa9c3e59c34af65d0741d1898e6c3870948fa14e81b4f8f7dea13c",
 BRAIN:"702b6d61fd4da62664e7bcfbc6c0d66b1b95dd4c9e4f8470f01314361f8b1724",
 FALLBACK:"7bcd1ae3cfbc12f58ff19bd2efde2fea6523f16efb9ec5bccb5c309c4d75f161",
}
WORK=Path("reports/swrlz-general-intelligence-v1152")
LOCAL_HELPER=Path("scripts/releases/historical_evidence_v1152.py")
URL="https://kamiloki-swyrlz.hf.space/api/hf/qwen35-ready"

def checksum(data):return hashlib.sha256(data).hexdigest()
def report(event,**details):
 print("SWRLZ_GENERAL_INTELLIGENCE_1152 "+
       json.dumps({"event":event,**details},sort_keys=True),flush=True)
def only(s,anchor,label):
 count=s.count(anchor)
 if count!=1:raise RuntimeError(f"Source anchor drift at {label}: {count}")
 return s.index(anchor)
def substitute(s,old,new,label):
 only(s,old,label)
 return s.replace(old,new,1)

def station_patch(data):
 s=data.decode("utf8")
 s=substitute(s,"import related_visual_history",
     "import related_visual_history\nimport historical_evidence",
     "evidence projection import")

 # Same-image historical context has been falsely added to the chat as a
 # new USER utterance. Preserve the actual old role labels and provenance.
 marker=only(s,'"[PRIOR DISCUSSION OF THE SAME EXACT IMAGE IN A DIFFERENT CONVERSATION; "',
             "same-image evidence marker")
 start=s.rfind('            payload["history"]=[{"role":"user","text":\n',0,marker)
 if start<0:raise RuntimeError("Missing same-image injection before marker")
 end=s.find('            payload["imageContextMatchedThreadId"]',start)
 if end<start:raise RuntimeError("Image history source terminator missing")
 old=s[start:end]
 if not ("PRIOR DISCUSSION OF THE SAME EXACT IMAGE" in old and
         '"\\n".join(excerpt)' in old and 'payload["history"]' in old):
  raise RuntimeError("Original image history projection differs")
 new='''            # swrlz-history-provenance-v1152: prior account history
            # is a typed, read-only reference, NOT a new USER message.
            historical_evidence.add(
                payload,"same-exact-image",
                "[Previous same-pixel discussion; historical roles follow]\\\\n"
                +"\\\\n".join(excerpt)[:4200])
'''
 # New is Python code; after triple quote evaluation it must contain \n
 # escape sequences, not embedded literal source newlines in the string.
 s=s[:start]+new+s[end:]

 s=substitute(s,
   '                payload["history"]=[{"role":"user","text":related["context"]}]+payload["history"]',
   '                historical_evidence.add(payload,"related-visual-history",related["context"])',
   "related images as evidence, not user")
 start=only(s,'                        payload["history"]=[{"role":"user","text":\n',
            "imported conversation history injection")
 end=s.find('                        payload["relatedVisualHistory"]=True',start)
 if end<start:raise RuntimeError("Imported history source terminator missing")
 old=s[start:end]
 if "OLDER OPT-IN ARCHIVE" not in old or 'imported[:1700]' not in old:
  raise RuntimeError("Original imported history projection differs")
 s=s[:start]+'''                        # Preserve the opt-in imported archive's role
                        # and age as evidence rather than an added USER turn.
                        historical_evidence.add(
                            payload,"opt-in-imported-history",imported[:1700])
'''+s[end:]
 return s.encode("utf8")

def brain_patch(data):
 s=data.decode("utf8")
 anchor='    # The router has already emitted a source-grounded widget through Station.'
 code='''    # swrlz-history-provenance-v1152: historical image/archival
    # candidates cannot contaminate the user turn or conversation intent.
    from historical_evidence import render as _historical_evidence_render
    source_evidence=_historical_evidence_render(payload,max_chars=3300)
    if source_evidence:
        system+="\\\\n"+source_evidence
'''
 s=substitute(s,anchor,code+anchor,"typed historical data in Qwen engine")
 return s.encode("utf8")

def fallback_patch(data):
 s=data.decode("utf8")
 anchor='    online_context=payload.get("onlineContext") if isinstance(payload.get("onlineContext"),dict) else {}'
 code='''    from historical_evidence import render as _historical_evidence_render
    source_evidence=_historical_evidence_render(payload,max_chars=950)
    if source_evidence:
        messages.append({"role":"system","content":source_evidence})
'''
 s=substitute(s,anchor,code+anchor,"typed historical data in fallback engine")
 return s.encode("utf8")

def test_static(patched):
 # Compilation is the first gate; tests independently exercise pure projection.
 for name,content in patched.items():
  ast.parse(content.decode("utf8"),filename=name)
 subprocess.run(["python","scripts/tests/test_historical_evidence_v1152.py"],
                timeout=20,check=True)
 station=patched[STATION].decode("utf8")
 brain=patched[BRAIN].decode("utf8")
 fallback=patched[FALLBACK].decode("utf8")
 assert station.count("historical_evidence.add(")==3
 assert 'payload["history"]=[{"role":"user","text":related["context"]}' not in station
 assert "PRIOR DISCUSSION OF THE SAME EXACT IMAGE IN A DIFFERENT CONVERSATION" not in station
 assert "OLDER OPT-IN ARCHIVE: potentially relevant past discussion" not in station
 assert 'payload["relatedVisualHistory"]=True' in station
 assert "direct_vision_answer=None" in station
 assert "selected_image_context is not None" in station
 assert "conversation_continuity.retrieve(" in station
 assert "_historical_evidence_render(payload,max_chars=3300)" in brain
 assert "_historical_evidence_render(payload,max_chars=950)" in fallback
 assert "response_cognition_policy(response_cognition)" in brain
 assert "def add(" in patched[HELPER].decode("utf8")
 report("STATIC_TESTS_PASS",
        tests=["no-synthetic-user-turns","typed-history-sources",
               "Qwen-and-fallback-compatibility","original-current-intent",
               "memory-and-vision-regression-anchors"])

def client():
 token=os.getenv("HF_TOKEN")
 if not token:raise RuntimeError("Missing HF_TOKEN; source is read-only")
 return HfApi(token=token)

def source(api,revision):
 existing=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
 if HELPER in existing:raise RuntimeError("Existing helper file; reject unexpected source")
 if not set(ORIGINALS).issubset(existing):raise RuntimeError("Missing source file")
 return {name:Path(hf_hub_download(SPACE,name,repo_type="space",
        revision=revision,token=api.token)).read_bytes()
        for name in ORIGINALS}

def prepare(api):
 current=api.repo_info(SPACE,repo_type="space").sha
 if current!=REVISION:raise RuntimeError("Space head changed; refusing update "+str(current))
 base=source(api,REVISION)
 hashes={name:checksum(raw) for name,raw in base.items()}
 if hashes!=ORIGINALS:
  raise RuntimeError("Verified original source hash changed: "+str(hashes))
 updates={
  STATION:station_patch(base[STATION]),
  BRAIN:brain_patch(base[BRAIN]),
  FALLBACK:fallback_patch(base[FALLBACK]),
  HELPER:LOCAL_HELPER.read_bytes(),
 }
 test_static(updates)
 for name in FILE_SET:
  for flavor,contents in (("original",base.get(name,b"")),("candidate",updates[name])):
   if not contents:continue
   path=WORK/flavor/name
   path.parent.mkdir(parents=True,exist_ok=True)
   path.write_bytes(contents)
 (WORK/"manifest.json").write_text(json.dumps({
   "source":REVISION,"files":FILE_SET,
   "before":hashes,"after":{name:checksum(contents) for name,contents in updates.items()},
   "invariants":"No account schema, image model, message history or tool authorization changes"
 },indent=2)+"\n")
 report("PREFLIGHT_PASS",source=REVISION,
     after={name:checksum(contents) for name,contents in updates.items()})
 return base,updates

def write(api,revision,contents,subject):
 result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
    operations=[CommitOperationAdd(path_in_repo=name,path_or_fileobj=io.BytesIO(raw))
                for name,raw in contents.items()],commit_message=subject)
 return str(result.oid or api.repo_info(SPACE,repo_type="space").sha)

def qwen_ready():
 try:
  request=urllib.request.Request(URL,headers={
     "Cache-Control":"no-cache","User-Agent":"Swyrlz-intelligence-1152"})
  with urllib.request.urlopen(request,timeout=18) as r:
   data=json.load(r)
   return r.status==200 and data.get("ready") is True and data.get("model")=="qwen3.5-9b"
 except (urllib.error.URLError,TimeoutError,ValueError,KeyError):
  return False

def runtime_gate(api,revision):
 previous=None;streak=0
 for attempt in range(1,79):
  if api.repo_info(SPACE,repo_type="space").sha!=revision:
   raise RuntimeError("Concurrent newer Space revision")
  runtime=api.get_space_runtime(SPACE)
  stage=str(runtime.stage).upper().split(".")[-1]
  serving=str((runtime.raw or {}).get("sha") or "")
  healthy=qwen_ready() if stage=="RUNNING" and serving==revision else False
  current=(stage,serving,healthy)
  if current!=previous:
   report("RUNTIME_GATE",attempt=attempt,stage=stage,serving=serving,qwenReady=healthy)
   previous=current
  if stage=="RUNTIME_ERROR":
   raise RuntimeError("HF app failed to start")
  streak=streak+1 if stage=="RUNNING" and serving==revision and healthy else 0
  if streak>=2:
   report("LIVE_ACCEPTED",revision=revision,version="1.1.52",qwenReady=True);return
  time.sleep(12)
 raise RuntimeError("Serving or resident Qwen readiness could not be verified")

def deploy(api):
 if os.getenv("SWRLZ_INTELLIGENCE_1152_APPROVED")!="yes":
  raise PermissionError("Authorized deployment scope not present")
 before,updates=prepare(api)
 if api.repo_info(SPACE,repo_type="space").sha!=REVISION or source(api,REVISION)!=before:
  raise RuntimeError("Space source changed before publication")
 published=None
 try:
  published=write(api,REVISION,updates,
   "§C 1.1.52: keep past discussion evidence out of current-turn history and action routing")
  report("PUBLISHED",revision=published)
  present=set(api.list_repo_files(SPACE,repo_type="space",revision=published))
  if not set(FILE_SET).issubset(present):
   raise RuntimeError("Published Space missing module")
  for name in FILE_SET:
   value=Path(hf_hub_download(SPACE,name,repo_type="space",
              revision=published,token=api.token)).read_bytes()
   if value!=updates[name]:raise RuntimeError("Exact source readback mismatch "+name)
  report("EXACT_READBACK_PASS",revision=published)
  runtime_gate(api,published)
 except Exception as ex:
  report("RELEASE_REJECTED",revision=published,error=str(ex)[:280])
  if published and api.repo_info(SPACE,repo_type="space").sha==published:
   from huggingface_hub import CommitOperationDelete
   result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
     operations=[CommitOperationAdd(path_in_repo=name,path_or_fileobj=io.BytesIO(before[name]))
                 for name in ORIGINALS]+[CommitOperationDelete(path_in_repo=HELPER)],
     commit_message="Rollback §C 1.1.52 to verified original conversation sources")
   report("EXACT_ROLLBACK",revision=str(result.oid))
  raise

if __name__=="__main__":
 import sys
 if sys.argv[1:] not in (["inspect"],["deploy"]):
  raise SystemExit("Usage inspect|deploy")
 hub=client()
 prepare(hub) if sys.argv[1]=="inspect" else deploy(hub)
