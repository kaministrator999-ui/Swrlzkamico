#!/usr/bin/env python3
"""Read-only, source-pinned §C UI/Station/coder audit. No private account data."""
from __future__ import annotations
import hashlib,os,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
SPACE="kamiloki/Swyrlz"
FILES=("chat/§wyrlz/index.html","station.py","qwen_coder_engine.py")
PATTERNS={
 FILES[0]:[r"Continue code",r"continueCode",r"continue-code",r"code.?continu",r"code.?draft",r"stopButton.addEventListener",r"stationCancellation",r"handleStop",r"cancel.*lalm_station",r"codeDraftCheckpoint",r"pendingCodeGeneration",r"stationBusy",r"stationGeneration.terminal",r"status.*CANCELLED"],
 FILES[1]:[r"continue code",r"resume_code",r"pendingCodeGeneration",r"_swrlz_auto_code_chain",r"cancelRequested",r"def cancel",r"codeDraftCheckpoint",r"CODE_OUTPUT_CHECKPOINT",r"auto.*code",r"CODE_REPAIR",r"def _run",r"def .*start"],
 FILES[2]:[r"def _response_mode",r"def .*prompt",r"continuation",r"continue code",r"CODE_OUTPUT_CHECKPOINT",r"def _candidate_structure_check",r"html",r"system_message",r"quality",r"creative",r"interact",r"def _swrlz_code_candidate_preview",r"source.*resume"]
}
def dump(source,patterns):
 lines=source.splitlines()
 hits=[]
 for i,line in enumerate(lines):
  if any(re.search(p,line,re.I) for p in patterns):
   hits.append(i)
 # First-hand source anchors only; never output entire files.
 chosen=set()
 for i in hits[:125]:
  for n in range(max(0,i-2),min(len(lines),i+4)):chosen.add(n)
 output=[]
 last=-2
 for i in sorted(chosen):
  if i>last+1:output.append("...")
  line=lines[i].replace("\t"," ")
  # Never include credential literals or sensitive tokens in logs.
  if re.search(r"(secret|password|api_key|hf_token|bearer|authorization)[^a-z]",line,re.I):
   line="<sensitive source line withheld>"
  output.append(str(i+1)+": "+line[:225])
  last=i
 return output
def main():
 token=os.getenv("HF_TOKEN")
 if not token:raise SystemExit("HF_TOKEN unavailable for read-only audit")
 api=HfApi(token=token);rev=api.repo_info(SPACE,repo_type="space").sha
 print("SOURCE_AUDIT_REVISION",rev,flush=True)
 for path in FILES:
  source=Path(hf_hub_download(SPACE,path,repo_type="space",revision=rev,token=token)).read_text(encoding="utf8")
  print("BEGIN_AUDIT",path,"chars",len(source),"sha256",hashlib.sha256(source.encode()).hexdigest(),flush=True)
  for line in dump(source,PATTERNS[path]):print(line,flush=True)
  ranges={
    FILES[0]:[(3985,4010),(4250,4330),(4680,4740),(4818,4850)],
    FILES[1]:[(1252,1310),(1704,1732),(2015,2090),(2120,2175)],
    FILES[2]:[(320,370),(555,585),(754,851),(1107,1140),(1255,1403)]
  }[path]
  lines=source.splitlines()
  for a,b in ranges:
   print("BEGIN_FOCUSED",path,a,b,flush=True)
   for i in range(a-1,min(len(lines),b)):
    line=lines[i][:290]
    if re.search(r"(secret|password|api_key|hf_token|bearer|authorization)[^a-z]",line,re.I):line="<sensitive source line withheld>"
    print(str(i+1)+": "+line,flush=True)
   print("END_FOCUSED",path,a,b,flush=True)
  print("END_AUDIT",path,flush=True)
if __name__=="__main__":main()
