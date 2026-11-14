#!/usr/bin/env python3
"""Exercise §C's actual new targeted-repair control-flow branch offline.

No model download/execution or user-data access. The exact pinned original
engine source is patched in memory using the production release patcher.
"""
from __future__ import annotations
import ast,hashlib,importlib.util,textwrap
from pathlib import Path
from huggingface_hub import hf_hub_download

from hf_chat_targeted_candidate_repair_v1 import patch_engine
from project_code_targeted_repair_v1 import TargetedRepairError,source_sha

SOURCE_REV="266404be909890b2dd421c0a980190dcc61b4662"
orig=Path(hf_hub_download("kamiloki/Swyrlz","qwen_coder_engine.py",
             repo_type="space",revision=SOURCE_REV)).read_bytes()
modified=patch_engine(orig).decode()
tree=ast.parse(modified)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="generate_events")
target=[]
for node in ast.walk(fn):
    if not isinstance(node,ast.If):continue
    if ('candidate_check.get("status")=="REJECT" and code_delivery' in
        ast.get_source_segment(modified,node).splitlines()[0]):
        target.append(node)
assert len(target)==1,len(target)
snippet=textwrap.dedent(ast.get_source_segment(modified,target[0]))
# Let the host event logic run verbatim, with prior candidate state bound
# as local parameters; unrelated external collaborators use deterministic doubles.
code=("def branch(candidate_text,candidate_check,candidate_fp):\n"
      +textwrap.indent(snippet,"    ")+"\n"
      +"    return candidate_text,candidate_check,candidate_fp\n")
old='<html><head></head><body><button id="ok">Keep me</button></body></html>'
new=old.replace("</head>","<style>button{color:cyan}</style></head>")
assert source_sha(new)!=source_sha(old)
attempts=[]
def fake_patch(model,source,check,prompt):
    assert source==old and check["reasons"]==["missing-css"]
    return new,{"before":source_sha(old),"after":source_sha(new),"removedBytes":0,
                "addedBytes":len("<style>button{color:cyan}</style>")},{"finishReason":"stop"}
scope={"code_delivery":True,"_SWRLZ_PATCH_ATTEMPTS":2,
 "timing":{"finishReason":"stop","continuationSegments":1},
 "model":object(),"prompt":"Improve same page",
 "_swrlz_patch_candidate_once":fake_patch,
 "_swrlz_patch_progress":lambda old,new:new["status"]=="PASS",
 "validate_attempt":lambda text,prev,completion:({"status":"PASS","reasons":[]},"new-fp"),
 "candidate_attempt_receipt":lambda *args,**kwargs:{"status":"PASS"},
 "candidate_attempts":attempts,"repair_target_fp":None,
 "regeneration_attempted":False,"regeneration_reason":"",
 "payload":{"projectImportManifest":None},"programming":{"codingTask":True},
 "_SwrlzPatchError":TargetedRepairError}
exec(code,scope)
iterator=scope["branch"](old,{"status":"REJECT","reasons":["missing-css"]},"old-fp")
events=[]
while True:
    try:events.append(next(iterator))
    except StopIteration as ending:
        final=ending.value
        break
assert final==(new,{"status":"PASS","reasons":[]},"new-fp")
assert any(x.get("type")=="CANDIDATE_PREVIEW_DELTA" and x.get("text")==new for x in events)
assert any(x.get("type")=="STATUS" and x.get("phase")=="CODE_REPAIR_APPLIED" for x in events)
assert not any(x.get("type")=="CANDIDATE_PREVIEW_RESET" and x.get("attempt")==0 for x in events)
assert len(attempts)==1
print("REPAIR_CONTROL_FLOW_ONE_PATCH_PRESERVES_SOURCE_PASS",flush=True)

def bad_patch(*args):raise TargetedRepairError("INVALID_JSON","not a patch")
events=[]
scope["_swrlz_patch_candidate_once"]=bad_patch
scope["_swrlz_checkpoint_record"]=lambda *args,**kwargs:{"source":args[0],"state":"UNVERIFIED_INCOMPLETE"}
def pause(checkpoint,*args):
    yield {"type":"CODE_OUTPUT_CHECKPOINT","checkpoint":checkpoint}
    yield {"type":"STATUS","phase":"CODE_DRAFT_SAVED"}
scope["_swrlz_pause_code_events"]=pause
exec(code,scope)
iterator=scope["branch"](old,{"status":"REJECT","reasons":["missing-css"]},"old-fp")
for event in iterator:events.append(event)
assert any(e.get("type")=="CODE_OUTPUT_CHECKPOINT" and e["checkpoint"]["source"]==old for e in events)
assert not any(e.get("type")=="CANDIDATE_PREVIEW_RESET" for e in events)
print("REPAIR_INVALID_PATCH_SAVES_ORIGINAL_UNVERIFIED_DRAFT_PASS",flush=True)
