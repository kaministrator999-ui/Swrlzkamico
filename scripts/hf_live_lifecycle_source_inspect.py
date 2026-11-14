"""Inspect live §C source boundaries without any Redis reads or secret values."""
import ast,base64,json,os,re
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
SPACE="kamiloki/Swyrlz"
FILES=("qwen_coder_engine.py","station.py","account_chat_store.py","chat/§wyrlz/index.html","programming_telemetry.py","programming_repair_context.py","brain_programming.py")
TERMS={
 "programming_telemetry.py":r"completion_validation|finishReason|length|stop|PASS",
 "programming_repair_context.py":r"source_fence_present|fence|completion|html",
 "brain_programming.py":r"candidate_contract_gate|fence|html",
 "qwen_coder_engine.py":r"fence|candidate_structure|_swrlz_code_candidate_preview|code_checkpoint|repair|complete|finished|parse|manifest|validator|source_fence|continue_code|pause_code|preview",
 "station.py":r"CODE_OUTPUT|CANDIDATE_PREVIEW|CODE_|COMPLETED|PREVIEW|_refresh_account_chat|_commit_revision|_snapshot|GENERATION|ACTIVITY",
 "account_chat_store.py":r"_CAS_LUA|_decode_native_chat|_chat_key|load_chat|save_chat|_config|revision|EVAL",
 "chat/§wyrlz/index.html":r"CODE_|codeDraft|codePreview|continu|repair|Saved draft|Preparing response|activity log|stream|COMPLETED|pending|reconnect|code-fence|fence",
}
WANTED={
 "programming_telemetry.py":("completion_validation",),
 "programming_repair_context.py":("source_fence_present",),
 "brain_programming.py":("candidate_contract_gate",),
 "qwen_coder_engine.py":("_candidate_structure_check","source_fence_present","_swrlz_code_candidate_preview","_swrlz_pause_code_events","_swrlz_resume_code_events","_swrlz_checkpoint_record","_swrlz_patch_candidate_once","generate_events","_swrlz_trim_code_resume"),
 "station.py":("_refresh_account_chat","_snapshot","_commit_revision","sync","_stream_response"),
 "account_chat_store.py":("_config","_chat_key","load_chat","save_chat"),
}
def main():
 api=HfApi(token=os.environ["HF_TOKEN"]); info=api.repo_info(SPACE,repo_type="space")
 paths=set(api.list_repo_files(SPACE,repo_type="space",revision=info.sha))
 print("SWRLZ_INSPECT_REV "+str(info.sha),flush=True)
 for file in FILES:
  if file not in paths:
   print("SWRLZ_INSPECT_MISSING "+file,flush=True);continue
  source=Path(hf_hub_download(SPACE,file,repo_type="space",revision=info.sha,token=api.token)).read_text("utf-8")
  lines=source.splitlines()
  if file.endswith(".py"):
   tree=ast.parse(source)
   funcs=[]
   for n in ast.walk(tree):
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in WANTED.get(file,()):
     funcs.append((n.name,n.lineno,n.end_lineno))
   print("SWRLZ_INSPECT_DEFS "+json.dumps({"file":file,"defs":funcs}),flush=True)
  hits=[i for i,line in enumerate(lines) if re.search(TERMS[file],line,re.I)]
  # Inspect code around focus keywords in live source, preserving indentation.
  chosen=set()
  for i in hits:
   if file=="chat/§wyrlz/index.html":
    if any(x in lines[i] for x in ('setInterval(', 'CANDIDATE_PREVIEW', 'CODE_OUTPUT', 'COMPLETED', 'codeDraft', 'Saved draft', 'Code repairing','Preparing response','complete', 'status.phase','streamStatus', 'renderCode')):
     for j in range(max(0,i-3), min(len(lines),i+6)):chosen.add(j)
   elif file=="station.py":
    if any(x in lines[i] for x in ('CODE_OUTPUT','CANDIDATE_PREVIEW','kind=="COMPLETED"','kind=="STATUS"','_refresh_account_chat','def sync(')):
     for j in range(max(0,i-2),min(len(lines),i+6)):chosen.add(j)
   elif file=="qwen_coder_engine.py":
    if any(x in lines[i] for x in ('source_fence_present','_candidate_structure_check','CODE_REPAIRING','CODE_OUTPUT_FINISHED','_swrlz_pause_code_events','_swrlz_checkpoint_record','_swrlz_resume_code_events','COMPLETED','finishReason','candidate_check','def _swrlz_trim_code_resume','def _swrlz_code_candidate_preview')):
     for j in range(max(0,i-3),min(len(lines),i+7)):chosen.add(j)
   else:
    for j in range(max(0,i-2),min(len(lines),i+4)):chosen.add(j)
  if file in ("programming_telemetry.py","programming_repair_context.py","brain_programming.py"):
   for n in ast.walk(tree):
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in WANTED.get(file,()):
     for j in range(max(0,n.lineno-1),min(len(lines),n.end_lineno)):chosen.add(j)
  # Include entire related functions/regions for source-accurate guarded edits.
  extra={
   "qwen_coder_engine.py":[(285,435),(585,666),(703,952),(955,1220),(1210,1410)],
   "brain_programming.py":[(1,240),(240,500)],
   "programming_repair_context.py":[(1,230),(230,420)],
   "station.py":[(307,365),(680,710),(1450,1560),(1810,1890),(2040,2170)],
   "account_chat_store.py":[(20,55),(105,222)],
   "chat/§wyrlz/index.html":[(4255,4325),(4350,4410),(1650,1750)],
  }
  for start,end in extra.get(file,[]):
   for j in range(max(0,start-1),min(len(lines),end)):chosen.add(j)
  # Print separate short blocks as base64-encoded static source text to avoid
  # GitHub masking a quoted literal and corrupting JSON. No user data read.
  grouped=[]; st=prev=None
  for i in sorted(chosen):
   if st is None:st=prev=i
   elif i<=prev+1:prev=i
   else:grouped.append((st,prev));st=prev=i
  if st is not None:grouped.append((st,prev))
  print("SWRLZ_INSPECT_META "+json.dumps({"file":file,"lines":len(lines),"matches":len(hits),"blocks":len(grouped)}),flush=True)
  for st,en in grouped[:75]:
   frag="\n".join(f"{k+1}: {lines[k]}" for k in range(st,en+1))
   for part in range(0,len(frag),8000):
    data=base64.b64encode(frag[part:part+8000].encode("utf-8")).decode("ascii")
    print("SWRLZ_INSPECT_CODE "+json.dumps({"file":file,"range":[st+1,en+1],"part":part//8000,"sourceB64":data}),flush=True)
if __name__=="__main__":main()
