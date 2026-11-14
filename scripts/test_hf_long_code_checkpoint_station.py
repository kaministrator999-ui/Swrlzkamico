#!/usr/bin/env python3
"""Read-only production-source regression for account-owned code checkpoints.

Exact AST branch tests: save, invalid source denial, cross-thread isolation,
resume command binding, and commit receipt before final artifact delivery.
No model download, account read, or repository mutation.
"""
from __future__ import annotations
import ast,copy,hashlib,re
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download

SPACE="kamiloki/Swyrlz"
api=HfApi()
rev=api.repo_info(SPACE,repo_type="space").sha
station=Path(hf_hub_download(SPACE,"station.py",repo_type="space",revision=rev)).read_text()
engine=Path(hf_hub_download(SPACE,"qwen_coder_engine.py",repo_type="space",revision=rev)).read_text()
tree=ast.parse(station)
def compare_branch(key):
    hits=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.If) and isinstance(node.test,ast.Compare):
            test=node.test
            if (isinstance(test.left,ast.Name) and test.left.id=="kind"
               and len(test.comparators)==1 and isinstance(test.comparators[0],ast.Constant)
               and test.comparators[0].value==key):
                hits.append(node)
    assert len(hits)==1,(key,len(hits))
    return compile(ast.Module(body=hits[0].body,type_ignores=[]),"<"+key+">","exec")

save=compare_branch("CODE_OUTPUT_CHECKPOINT")
finish=compare_branch("CODE_OUTPUT_FINISHED")
source=""+chr(96)*3+"html\n<!doctype html><html><body><h1>Hi"
checksum=hashlib.sha256(source.encode()).hexdigest()
checkpoint={
 "schema":"swrlz-long-code-checkpoint-v1","source":source,
 "sourceSha256":checksum,"originalPrompt":"Build complete HTML",
 "programmingIntent":{"codingTask":True,"changeClass":"feature"},
 "sourceManifest":{},"segmentsCompleted":8,"state":"UNVERIFIED_INCOMPLETE"
}
s={"threads":[{"id":"current","codeArtifacts":[{"id":"verified","currentRevision":6}]},
              {"id":"foreign","codeArtifacts":[{"id":"unrelated"}]}]}
g={"lastSeq":12,"status":[]}
payload={"threadId":"current"}
saved=[]
scope={"s":s,"g":g,"payload":payload,
       "copy":copy,"hashlib":hashlib,
       "event":{"checkpoint":checkpoint},
       "_commit_revision":lambda s_: saved.append(copy.deepcopy(s_["threads"][0].get("pendingCodeGeneration")))}
exec(save,scope)
assert len(saved)==1 and saved[0]["sourceSha256"]==checksum
assert s["threads"][0]["pendingCodeGeneration"]["source"]==source
assert len(s["threads"][0]["codeArtifacts"])==1
assert "pendingCodeGeneration" not in s["threads"][1]
assert any(x.get("phase")=="CODE_DRAFT_CHECKPOINTED" for x in g["status"])
print("LONG_CODE_ACCOUNT_CHECKPOINT_VERIFIED",rev,flush=True)
for malformed in [
   dict(checkpoint,sourceSha256="0"*64),
   dict(checkpoint,source="x"*(240*1024+1)),
   dict(checkpoint,schema="wrong"),
]:
    scope["event"]={"checkpoint":malformed}
    try:exec(save,scope)
    except RuntimeError:pass
    else:raise AssertionError("Invalid/oversize checkpoint admitted")
assert len(saved)==1
print("LONG_CODE_TAMPER_AND_SIZE_REJECTED",flush=True)
scope["event"]={}
scope["payload"]={"threadId":"current","codeContinuation":{"sourceSha256":"0"*64}}
exec(finish,scope)
assert s["threads"][0]["pendingCodeGeneration"]["sourceSha256"]==checksum
scope["payload"]["codeContinuation"]["sourceSha256"]=checksum
exec(finish,scope)
assert "pendingCodeGeneration" not in s["threads"][0]
assert len(s["threads"][0]["codeArtifacts"])==1
print("LONG_CODE_EXACT_SOURCE_FINISH_VERIFIED",flush=True)

start=station.index('        pending=t.get("pendingCodeGeneration")')
end=station.index("        history=_history_projection(t, current_prompt=prompt)",start)
import textwrap
command_code=textwrap.dedent(station[start:end])
def test_command(prompt,state):
    t={"pendingCodeGeneration":state}
    scope={"t":t,"prompt":prompt,"hashlib":hashlib,"copy":copy,"re":re,
           "_find_artifact":lambda *a:None,
           "HTTPException":type("HTTPException",(Exception,),{"__init__":lambda self,a,b:Exception.__init__(self,b)})}
    exec(command_code,scope)
    return scope["resume_code"]
assert test_command("Continue code",checkpoint)["sourceSha256"]==checksum
assert test_command("Please resume the code",checkpoint)["sourceSha256"]==checksum
assert test_command("Continue discussing CSS",checkpoint) is None
assert test_command("Improve the page",checkpoint) is None
try:test_command("Continue code",dict(checkpoint,source="untrusted"))
except Exception:pass
else:raise AssertionError("Invalid source hash accepted by resume command")
assert "payload[\"codeContinuation\"]=resume_code" in station
assert 'event_source=_coder_generate(payload)' in station
assert "yield from _swrlz_pause_code_events" in engine
assert "CANDIDATE_VALIDATION" in engine and "completion_validation(" in engine
assert "max_segments=8 if allow_continue else 1" in engine
print("LONG_CODE_RESUME_COMMAND_BOUND_TO_SAVED_THREAD",flush=True)
print("LONG_CODE_FULL_STATION_CHECKPOINT_SOURCE_TEST_PASS",flush=True)
