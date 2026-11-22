#!/usr/bin/env python3
"""CAS-guarded release of scoped §C Chat-auth/§E reference bridge."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.request import urlopen

from hf_chat_engine_bridge_v1_patch import BEFORE, AFTER, apply

SPACE="kamiloki/Swyrlz"
BASE="fa5676e99e7f18adbcc8c0fa4804475400faf067"
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/chat-engine-bridge-v1"
READY="https://kamiloki-swyrlz.hf.space/api/hf/qwen35-ready"

def digest(raw):return hashlib.sha256(raw).hexdigest()

def prepare(download):
 before,after=OUT/"before",OUT/"after"
 for path in (before,after):path.mkdir(parents=True,exist_ok=True)
 for name in BEFORE:
  raw=download(name,BASE)
  if digest(raw)!=BEFORE[name]:raise RuntimeError("Chat live source drift: "+name)
  result=apply(name,raw)
  for directory,data in ((before,raw),(after,result)):
   dest=directory/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 js=after/"chat/§wyrlz/assets/forge-embed-v1.js"
 subprocess.run(["node","--check",str(js)],check=True)
 html=(after/"chat/§wyrlz/index.html").read_text("utf8")
 scripts=[x for x in re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>",html,re.I) if x.strip()]
 if len(scripts)!=1:raise RuntimeError("Chat original inline script ownership changed")
 source=OUT/"chat-inline.js";source.write_text(scripts[0],"utf8")
 subprocess.run(["node","--check",str(source)],check=True)
 subprocess.run([sys.executable,str(ROOT/"tests/test_hf_chat_engine_bridge_v1.py"),str(before),str(after)],check=True)
 print("CHAT_ENGINE_BRIDGE_CANDIDATE",json.dumps({"base":BASE,"files":AFTER}),flush=True)
 return before,after

def run(mode):
 from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
 token=os.getenv("HF_TOKEN") or False
 api=HfApi(token=token)
 def download(name,rev):
  return Path(hf_hub_download(SPACE,name,repo_type="space",revision=rev,token=token)).read_bytes()
 if api.repo_info(SPACE,repo_type="space").sha!=BASE:
  raise RuntimeError("Chat Space changed. Rebase rather than overwrite.")
 before,after=prepare(download)
 if mode=="inspect":return
 if not token or os.getenv("SWRLZ_ENGINE_BRIDGE_APPROVED")!="1":
  raise RuntimeError("Owner authorization and configured HF_TOKEN required.")
 def commit(directory,parent,message):
  return api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=parent,commit_message=message,
    operations=[CommitOperationAdd(path_in_repo=name,path_or_fileobj=str(directory/name)) for name in BEFORE]).oid
 revision=commit(after,BASE,"Improve §E native Google code and §C image reference handoff")
 (OUT/"publication.json").write_text(json.dumps({"base":BASE,"revision":revision,"verified":False}))
 print("CHAT_ENGINE_BRIDGE_PUBLISHED",revision,flush=True)
 try:
  for name in AFTER:
   if digest(download(name,revision))!=AFTER[name]:raise RuntimeError("Published source mismatch: "+name)
  # Do not report live until the existing production Space is running this revision.
  success=0
  for _ in range(50):
   head=api.repo_info(SPACE,repo_type="space").sha
   if head!=revision:raise RuntimeError("Chat Space changed after publication.")
   runtime=api.get_space_runtime(SPACE)
   running=runtime.stage=="RUNNING" and runtime.raw.get("sha")==revision
   try:
    with urlopen(READY,timeout=15) as response:ready=json.load(response)
    running=running and ready.get("ready") is True
   except OSError:running=False
   success=success+1 if running else 0
   if success>=2:break
   time.sleep(12)
  else:raise RuntimeError("Chat Space did not pass running readiness")
 except Exception:
  if api.repo_info(SPACE,repo_type="space").sha==revision:
   old=commit(before,revision,"Rollback scoped §C account and image integration")
   print("CHAT_ENGINE_BRIDGE_ROLLBACK",old,flush=True)
  raise
 (OUT/"publication.json").write_text(json.dumps({"base":BASE,"revision":revision,"verified":True}))
 print("CHAT_ENGINE_BRIDGE_LIVE",revision,flush=True)

if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("mode",choices=["inspect","publish"])
 run(parser.parse_args().mode)
