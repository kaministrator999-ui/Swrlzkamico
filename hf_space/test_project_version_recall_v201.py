"""v201 regressions for short source-grounded project-version follow-ups.

No model pass or live inference quality is claimed by these offline tests.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))

import project_thread_memory as pm
from model_router import dispatch

SHA="a"*40
DATA={
    "repo":"example/project","branch":"main","sourceSha":SHA,"runtimeSha":"b"*40,
    "startupPath":"§wyrlz_§tart.md","docsRead":["§wyrlz_§tart.md"],
    "modules":[
        ["REPOSITORY_WORK","1.0.137","active"],
        ["SERVER_RUNTIME","2.3.351","active"],
        ["WEB_CHAT","1.5.95","active"],
        ["LALM_ENGINE","2.1.179","active"],
        ["CLIENT_APK","UNASSIGNED","reserved"],
        ["SERVER_RUNTIME","999.0.0","fabricated-duplicate"],
        ["BROKEN|FIELD","bad|value","bad"],
    ],
    "latestCompleted":"v200 source validation of a vending-machine rap request",
    "possibleUnresolved":"Unknown"
}

def test_real_short_recall_intent():
    for prompt in (
        "Can you tell me the versions again?",
        "What were the versions again?",
        "What are our versions again",
        "List the module versions again",
        "Repeat the versions",
        "Remind me of the versions again",
    ):
        assert pm.short_version_recall(prompt), prompt
        result=pm.source_version_recap(DATA,prompt)
        assert result.startswith("Here are the versions from our last GitHub source read")
        assert result.count("| Server Runtime |")==1, result
        assert "2.3.351" in result and "1.5.95" in result
        assert "2.1.179" in result and "UNASSIGNED" in result
        assert "999.0.0" not in result and "bad|value" not in result
        assert "initial commit" not in result.lower()
        assert "vending" not in result.lower(), result
        assert "§tart.md" not in result and "%C2%A7" not in result
        assert "not a fresh live deployment check" in result
        assert len(result)<1800, len(result)

def test_complex_requests_stay_generational():
    for prompt in (
        "What changed between the versions?",
        "Which commit first introduced the server version?",
        "Can you compare version 2.3.351 with 2.3.350?",
        "What is semantic versioning?",
        "Write a rap about versions and vending machines",
        "Which versions are compatible with Python 3.11?",
        "Can you tell me the versions again and explain every release?",
        "Version history please",
        "Can you tell me the versions again? Also, write a rap.",
    ):
        assert not pm.short_version_recall(prompt), prompt
        assert pm.source_version_recap(DATA,prompt)=="",prompt
    assert pm.source_version_recap(None,"What were the versions again?")==""
    assert pm.source_version_recap({**DATA,"sourceSha":"unverified"},"What were the versions again?")==""
    assert pm.source_version_recap({**DATA,"modules":[]},"What were the versions again?")==""


def test_source_owned_model_router_event():
    reply=pm.source_version_recap(DATA,"What were the versions again?")
    called=[]
    def model(_):
        called.append("model-called")
        yield {"type":"DELTA","text":"Unverified speculation"}
    events=list(dispatch("700m",{
        "prompt":"What were the versions again?",
        "history":[{"role":"user","text":"Read the GitHub §tart document."}],
        "projectVersionRecall":reply,
    },model,large_generate=model))
    assert not called, "Source recall should not require inference"
    assert [e["type"] for e in events][-3:]==["STATUS","DELTA","COMPLETED"], events
    assert next(e["text"] for e in events if e["type"]=="DELTA")==reply
    assert events[-1].get("fastPath")=="verified-project-version-recall"
    station=Path(__file__).with_name("station.py").read_text()
    assert 'google_owner.startswith("google:")' in station
    assert 'project_thread_memory.source_version_recap(active_project,prompt)' in station
    assert 'payload["projectVersionRecall"]=recap' in station
    assert 'project_thread_memory.load(google_owner,tid)' in station


if __name__=="__main__":
    test_real_short_recall_intent()
    test_complex_requests_stay_generational()
    test_source_owned_model_router_event()
    print("v201 authenticated source-version recall tests passed")
