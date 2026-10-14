"""Synthetic replay of Dragon Chat (51); no private history or credentials stored."""
import hashlib
import sys
import time
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_connection as gh
import github_source_specialist_v241 as specialist
import project_work_registry_v241 as registry

USER="google:owner123"
REPO="example/demo"
MAIN="a"*40
RELEASE="b"*40
BODY="def route(x):\n    return x\n"
BLOB=hashlib.sha1(b"blob "+str(len(BODY.encode())).encode()+b"\0"+BODY.encode()).hexdigest()
REVIEW=("I'm working on improving GitHub inference in hf_space/station.py. "
        "Please review the current architecture. Analysis and planning only. "
        "Do not modify, commit, or deploy anything.")

def test_negated_review():
    route=specialist.parse(REVIEW,{"branch":"main"})
    assert route and route["path"]=="hf_space/station.py",route
    assert specialist.parse("Review and edit hf_space/station.py") is None
    assert specialist.parse("Explain file src/app.py then deploy it") is None
    assert gh._stage_blocks("@GitHub edit file hf_space/model_router.py")
    assert gh._stage_blocks("@GitHub confirm DONT-WRITE")

def _api(_token,path):
    if path=="/repos/"+REPO+"/commits/main":
        return {"sha":MAIN}
    if path=="/repos/"+REPO+"/git/trees/"+MAIN+"?recursive=1":
        return {"truncated":False,"tree":[]}
    if path=="/repos/"+REPO+"/commits/"+RELEASE:
        return {"sha":RELEASE}
    if path=="/repos/"+REPO+"/git/trees/"+RELEASE+"?recursive=1":
        return {"truncated":False,"tree":[{"type":"blob","path":"hf_space/station.py","sha":BLOB,"size":len(BODY)}]}
    raise AssertionError("Unplanned GitHub GET: "+path)

def _read(_token,_repo,path,_ref,_limit):
    if path==".deploy/HF_SPACE_REQUEST.txt":
        return {"sha":"f"*40,"body":"TARGET=kamiloki/Swyrlz\nAPPROVED=1\nSOURCE_REF="+RELEASE+"\nREQUEST_NONCE=previous\n"}
    if path=="hf_space/station.py":
        return {"sha":BLOB,"body":BODY}
    raise AssertionError("Unplanned source read: "+path)

def _events(prompt):
    def coder(payload):
        assert BODY.strip() in payload["prompt"]
        yield {"type":"DELTA","text":"The verified source routes a value, with no evidence of sensor subsystems."}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    context={"repo":REPO,"branch":"main","sourceSha":MAIN,"directory":"","lastFile":""}
    with mock.patch.object(gh,"_config",return_value={}),\
         mock.patch.object(gh,"_load",return_value={"token":"read-only","repo":REPO}),\
         mock.patch.object(gh,"_effective_access",return_value={"allowed":True,"defaultBranch":"main"}),\
         mock.patch.object(gh,"_api",side_effect=_api),\
         mock.patch.object(gh,"_read_optional",side_effect=_read),\
         mock.patch.object(gh,"_post_github",side_effect=AssertionError("NO WRITES")):
        return list(gh.agent_events({"userId":USER,"prompt":prompt,
                    "githubContext":context},coder_generator=coder))

def test_release_source_fallback():
    result=_events(REVIEW)
    answer="".join(x.get("text","") for x in result)
    assert "approved immutable Chat release source" in answer,answer
    assert RELEASE in answer
    assert "verified source routes a value" in answer
    assert any(x.get("type")=="GITHUB_CONTEXT" and
               x["context"]["branch"]==RELEASE for x in result)
    assert not any(x.get("type") in ("GITHUB_WRITE","COMMIT") for x in result)

def test_explicit_main_does_not_switch():
    result=_events("@GitHub explain file hf_space/station.py on branch main")
    answer="".join(x.get("text","") for x in result)
    assert "not found on branch main" in answer,answer
    assert "approved immutable Chat release source" not in answer

def test_overlap_verification():
    query=("Before proceeding check whether another conversation has "
           "declared work involving hf_space/station.py. Do not modify anything.")
    assert registry.is_overlap_question(query)
    assert not registry.is_overlap_question("Please implement hf_space/station.py")
    now=int(time.time())
    entry={"schema":registry.SCHEMA,"repository":REPO,"conversationId":"other",
           "workItemId":"safe","title":"improve GitHub inference",
           "paths":["hf_space/station.py"],"keywords":["github","inference"],
           "lastObservedAt":now,"expiresAt":now+2000}
    different={**entry,"repository":"different/repo"}
    with mock.patch.object(registry.store,"_config",return_value={}),\
         mock.patch.object(registry,"_read",return_value=(1,[entry,different])),\
         mock.patch.object(registry,"_persist",side_effect=AssertionError("No write")):
        result=registry.describe_overlap(USER,"current",REPO,query)
    assert "same-file" in result and "improve GitHub inference" in result
    assert "not proof of active work" in result
    assert "different/repo" not in result
    with mock.patch.object(registry.store,"_config",return_value={}),\
         mock.patch.object(registry,"_read",return_value=(1,[])):
        empty=registry.describe_overlap(USER,"current",REPO,query)
    assert "No matching recent work declaration" in empty
    assert "not proof another conversation is idle" in empty

def test_startup_context_and_stage_lock():
    source=Path(__file__).with_name("station.py").read_text()
    assert 'active_project.get("evidenceType") == "GITHUB_SOURCE_READ_ONLY"' in source
    assert 'payload["verifiedWorkAnswer"]' in source
    assert "project_work_registry.is_overlap_question(prompt)" in source
    assert gh._stage_blocks("@GitHub edit file hf_space/station.py")
    assert gh._stage_blocks("@GitHub confirm 123456789")

if __name__=="__main__":
    for case in (test_negated_review,test_release_source_fallback,
                 test_explicit_main_does_not_switch,test_overlap_verification,
                 test_startup_context_and_stage_lock):
        case()
    print("v242 Dragon Chat 51 source and coordination PASS")
