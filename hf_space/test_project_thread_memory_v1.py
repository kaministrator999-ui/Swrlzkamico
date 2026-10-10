"""Offline evidence-continuity assertions: tenant isolation, crypto, routing and provenance."""
import json
import sys
from pathlib import Path
from unittest import mock

from cryptography.fernet import Fernet
sys.path.insert(0,str(Path(__file__).parent))
import github_connection as gh
import project_thread_memory as pm

OWNER="google:alice"
OTHER="google:bob"
THREAD="web-abc_123"
SHA="a"*40
SOURCE={
    "repo":"owner/repo","branch":"main","sourceSha":SHA,"runtimeSha":"b"*40,
    "startupPath":"START.md","docsRead":["START.md","ROADMAP.md"],
    "modules":[["REPOSITORY_WORK","1.0.124","active"],["SERVER_RUNTIME","2.3.338","active"]],
    "latestCompleted":"Bounded project manifest planning",
    "latestCompletedDate":"2026-10-09",
    "possibleUnresolved":"Coder candidate broad CI failed",
}
def _c():
    return {"client":"id","secret":"private","callback":"https://example.com/api/github/callback",
            "fernet":Fernet.generate_key().decode(),"redis":"https://redis.example.com","redis_token":"superprivate"}

def test_durable_encrypted_strict_scope():
    cfg=_c()
    stored={}
    def redis(_,command,key,*args):
        if command=="SET":
            assert args[1]=="EX" and args[2]==pm.RETENTION_SECONDS
            stored[key]=args[0]
            return "OK"
        if command=="GET":return stored.get(key)
        if command=="DEL":return int(stored.pop(key,None) is not None)
        raise AssertionError(command)
    with mock.patch.object(gh,"_settings",return_value=cfg),mock.patch.object(gh,"_redis",side_effect=redis):
        assert pm.save(OWNER,THREAD,SOURCE)
        encoded=json.dumps(stored)
        for forbidden in ("owner/repo","Bounded project","google:alice","superprivate"):
            assert forbidden not in encoded
        assert pm.load(OWNER,THREAD)["repo"]=="owner/repo"
        assert pm.load(OTHER,THREAD) is None
        assert pm.load(OWNER,"another-thread") is None
        assert pm.model_context(pm.load(OWNER,THREAD),"What is the project status?")
        assert not pm.model_context(pm.load(OWNER,THREAD),"Write a poem about dragons")
        # Copying another account's cipher does not convert its owner.
        foreign=pm._key(OTHER,THREAD)
        stored[foreign]=stored[pm._key(OWNER,THREAD)]
        assert pm.load(OTHER,THREAD) is None
        stored[pm._key(OWNER,THREAD)]="bad-token"
        assert pm.load(OWNER,THREAD) is None
        assert pm.delete(OWNER,THREAD)
        assert pm.load(OWNER,THREAD) is None

def test_strict_input_limits_no_made_up_facts():
    assert pm.normalize(SOURCE)["acceptance"]=="SOURCE_EVIDENCE_ONLY"
    assert pm.normalize({**SOURCE,"sourceSha":"untrusted"}) is None
    assert pm.normalize({**SOURCE,"repo":"other/../../../thing"}) is None
    assert pm._config() is None or isinstance(pm._config(),dict)
    assert not pm.relevant("How do I tune my guitar?")
    assert pm.relevant("Continue that GitHub project, what remains?")
    normalized=pm.normalize(SOURCE)
    output=pm.model_context(normalized,"What was our GitHub project plan?")
    assert "1.0.124" in output and "source snapshot" in output
    assert "superprivate" not in output
    assert "not current deployment" in output
    assert len(output)<=1650
    assert "sourceSha" in normalized and "capturedAt" in normalized

def test_startup_receipt_and_route_source_contract():
    # Static exact-owner checks supplement dynamic encrypted Redis assertions.
    ghsrc=Path(__file__).with_name("github_connection.py").read_text()
    station=Path(__file__).with_name("station.py").read_text()
    engines=[
        Path(__file__).with_name("lfm2_700m_engine.py").read_text(),
        Path(__file__).with_name("qwen_coder_engine.py").read_text(),
        Path(__file__).with_name("original_engine.py").read_text(),
    ]
    assert 'yield {"type":"PROJECT_CONTEXT","context":context}' in ghsrc
    assert "project_memory_receipt=(user_id,str(thread" in station
    assert "project_thread_memory.save(*project_memory_receipt)" in station
    assert "project_thread_memory.load(google_owner,tid)" in station
    assert 'payload["projectThreadEvidence"]=memory_evidence' in station
    assert 'project_thread_memory.delete(google_owner,deleted)' in station
    assert "ownerGoogleId" in station
    for src in engines:
        assert 'payload.get("projectThreadEvidence")' in src
    assert "UPSTASH_REDIS_REST_TOKEN" not in station

def test_github_report_emits_same_pinned_source_snapshot():
    def api(_,path):
        if path=="/repos/owner/repo":return {"default_branch":"main"}
        if path in ("/repos/owner/repo/commits/main","/repos/owner/repo/commits/runtime"):return {"sha":SHA}
        raise AssertionError(path)
    def optional(_,repo,path,ref,max_bytes=100000):
        assert ref==SHA
        if path=="§wyrlz_§tart.md":
            return {"body":"# startup\nRead docs","sha":SHA,"path":path}
        if path=="SWRLZ_SERVER_ROADMAP.md":
            return {"body":"## UPDATE FINISHED — 2026-10-09 — project planner verification\n\n**Result: SOURCE VERIFIED / LIVE PENDING.**\n","sha":SHA,"path":path}
        if path=="VERSION.txt":
            return {"body":"REPOSITORY_WORK=versions/repository-work.txt","sha":SHA,"path":path}
        if path=="versions/repository-work.txt":
            return {"body":"VERSION=1.0.124\nSTATUS=active","sha":SHA,"path":path}
        return None
    with mock.patch.object(gh,"_config",return_value={}),mock.patch.object(gh,"_load",return_value={"token":"opaque","repo":"owner/repo"}),mock.patch.object(gh,"_api",side_effect=api),mock.patch.object(gh,"_read_optional",side_effect=optional):
        messages=list(gh.start_events({"userId":OWNER}))
        context=next(e["context"] for e in messages if e.get("type")=="PROJECT_CONTEXT")
        report=next(e["text"] for e in messages if e.get("type")=="DELTA")
        assert context["sourceSha"]==SHA and context["repo"]=="owner/repo"
        assert context["modules"][0][1]=="1.0.124"
        assert "project planner verification" in report
        assert "SOURCE VERIFIED" in report
        assert messages[-1]["type"]=="COMPLETED"
        assert not any(e.get("type")=="PROJECT_CONTEXT" and e.get("context",{}).get("token") for e in messages)

if __name__=="__main__":
    test_durable_encrypted_strict_scope()
    test_strict_input_limits_no_made_up_facts()
    test_startup_receipt_and_route_source_contract()
    test_github_report_emits_same_pinned_source_snapshot()
    print("Project thread source-memory isolation and route tests passed")
