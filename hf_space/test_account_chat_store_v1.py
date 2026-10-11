"""Offline regression of Google account and full chat snapshot retention/recovery."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from cryptography.fernet import Fernet

sys.path.insert(0,str(Path(__file__).resolve().parent))
import account_chat_store as store
import github_connection as gh
# CI checks repository files without constructing the Hugging Face Space stage.
# The production deploy packages its Chat assets separately.
(Path(__file__).parent/'chat/§wyrlz/assets').mkdir(parents=True,exist_ok=True)
import station

OWNER="google:alice123456789"
OTHER="google:bob987654321"
USER={"id":OWNER,"email":"test@example.com","displayName":"Tester","picture":""}
def config():
    return {"fernet":Fernet.generate_key().decode(),"redis":"https://redis.test","redis_token":"hidden-token",
            "client":"test-id","secret":"unused","callback":"https://host.test/api/github/callback"}
def fake_store():
    kv={}
    def redis(_,verb,*args):
        if verb=="GET":return kv.get(args[0])
        if verb=="SET":
            kv[args[0]]=args[1]
            return "OK"
        if verb=="DEL":return int(kv.pop(args[0],None) is not None)
        if verb=="EVAL":
            _,one,key,prior,blob=args
            assert one=="1"
            current=kv.get(key)
            if current is None:
                if int(prior)!=0:return 0
            elif json.loads(current)["revision"]!=int(prior):
                return 0
            kv[key]=blob
            return 1
        raise AssertionError(verb)
    return kv,redis
def make_thread(label):
    return {"id":"threadA","title":label,"pinned":False,"messagePins":{},
            "codeArtifacts":[],"createdAt":123,"messages":[
            {"id":"m1","role":"user","text":"Please review my GitHub project","createdAt":123},
            {"id":"m2","role":"assistant","text":"Reviewed source at a fixed SHA","createdAt":124}]}

def test_google_cookie_redis_rehydrates_and_revokes():
    kv,redis=fake_store()
    with mock.patch.object(gh,"_settings",return_value=config()),mock.patch.object(gh,"_redis",side_effect=redis):
        assert store.configured()
        store.save_login("a"*32,USER)
        stored=str(kv)
        for private in ("google:alice","test@example.com","hidden-token"):
            assert private not in stored
        assert store.load_login("a"*32)["id"]==OWNER
        assert store.load_login("b"*32) is None
        store.revoke_login("a"*32)
        assert store.load_login("a"*32) is None

def test_account_owner_chat_after_restart_and_conflicts():
    kv,redis=fake_store()
    with mock.patch.object(gh,"_settings",return_value=config()),mock.patch.object(gh,"_redis",side_effect=redis),mock.patch.object(station,"_account_session",return_value=("cookie",USER)):
        station._sessions.clear()
        request=SimpleNamespace(cookies={})
        key,s=station._session(request)
        assert s["revision"]==0 and s["threads"]==[]
        s["threads"]=[make_thread("Project notes")]
        s["currentId"]="threadA"
        station._commit_revision(s)
        assert s["revision"]==1
        assert "Please review my GitHub project" not in str(kv)
        assert store.load_chat(OWNER)["threads"][0]["messages"][1]["text"]=="Reviewed source at a fixed SHA"
        assert store.load_chat(OTHER) is None
        stale=dict(s)
        station._sessions.clear()  # Space restarted.
        reloaded_key,restored=station._session(request)
        assert reloaded_key==key
        assert restored["currentId"]=="threadA"
        assert restored["threads"][0]["messages"][0]["text"]=="Please review my GitHub project"
        assert restored["activeGeneration"] is None
        # Browser in a different process has stale rev1 and cannot replace rev2.
        restored["threads"][0]["title"]="new title"
        station._commit_revision(restored)
        assert not store.save_chat(OWNER,{"revision":2,"ownerGoogleId":OWNER,"currentId":"threadA","threads":[make_thread("stale write")]},1)
        assert store.load_chat(OWNER)["threads"][0]["title"]=="new title"

def test_two_browser_cached_worker_refresh_and_non_destructive_conflicts():
    # Two browser requests can land on separate HF workers. A process-local
    # _sessions cache must not hide another worker's committed Google history.
    kv,redis=fake_store()
    c=config()
    with mock.patch.object(gh,"_settings",return_value=c),mock.patch.object(gh,"_redis",side_effect=redis),mock.patch.object(station,"_account_session",return_value=("browser-A",USER)):
        station._sessions.clear()
        request=SimpleNamespace(cookies={})
        key,worker_a=station._session(request)
        worker_a["threads"]=[make_thread("Original account chat")]
        worker_a["currentId"]="threadA"
        station._commit_revision(worker_a)
        assert worker_a["revision"]==1

        # This is a second worker's independent read, with the same verified owner.
        worker_b=store.load_chat(OWNER)
        assert worker_b["revision"]==1
        another=make_thread("New thread saved from Browser B")
        another["id"]="threadB"
        worker_b["threads"].append(another)
        worker_b["currentId"]="threadB"
        worker_b["revision"]=2
        assert store.save_chat(OWNER,worker_b,1)

        # Before reconciliation, A is stale. B's data must not be overwritten.
        assert worker_a["revision"]==1 and len(worker_a["threads"])==1
        assert station._refresh_account_chat(worker_a) is True
        assert worker_a["revision"]==2
        assert [t["id"] for t in worker_a["threads"]]==["threadA","threadB"]
        assert worker_a["currentId"]=="threadB"
        assert station._refresh_account_chat(worker_a) is False

        # Another remote write during local inference must not evict A's active
        # generation, but becomes visible immediately once A finishes it.
        worker_a["activeGeneration"]={"requestId":"ongoing-A","terminal":False}
        worker_b=store.load_chat(OWNER)
        third=make_thread("Third account chat")
        third["id"]="threadC"
        worker_b["threads"].append(third)
        worker_b["revision"]=3
        assert store.save_chat(OWNER,worker_b,2)
        assert station._refresh_account_chat(worker_a) is False
        assert worker_a["activeGeneration"]["requestId"]=="ongoing-A"
        assert len(worker_a["threads"])==2
        worker_a["activeGeneration"]["terminal"]=True
        assert station._refresh_account_chat(worker_a) is True
        assert [t["id"] for t in worker_a["threads"]]==["threadA","threadB","threadC"]

        # An old revision is never allowed to replace either browser's work.
        stale={"revision":3,"ownerGoogleId":OWNER,"currentId":"threadA",
               "threads":[make_thread("Stale overwrite attempt")]}
        assert not store.save_chat(OWNER,stale,1)
        assert len(store.load_chat(OWNER)["threads"])==3
        assert store.load_chat(OTHER) is None
        station._sessions.clear()


def test_limits_enforced_no_silent_truncation_and_identity_isolation():
    kv,redis=fake_store()
    with mock.patch.object(gh,"_settings",return_value=config()),mock.patch.object(gh,"_redis",side_effect=redis):
        assert store.load_chat(OTHER) is None
        try: store.save_chat("anonymous",{"revision":1,"ownerGoogleId":"anonymous","threads":[],"currentId":""},0)
        except Exception:pass
        else:raise AssertionError("anonymous account must be rejected")
        try: store._encrypt(store._config(),{"history":"x"*(store.MAX_BYTES+1)})
        except Exception as exc:assert getattr(exc,"status_code",None)==413
        else:raise AssertionError("Oversized chat cannot be silently truncated")
        assert not kv

def test_source_wiring_and_sync_contract():
    source=Path(__file__).with_name("station.py").read_text()
    for required in ("account_chat_store.save_login(sid,user)","account_chat_store.load_login(sid)",
                     "account_chat_store.revoke_login(sid)","account_chat_store.load_chat(owner)",
                     "account_chat_store.save_chat(owner,s,expected_revision)",
                     'if owner.startswith("google:"):',"_commit_revision(s)",
                     "encrypted-google-account-redis"):
        assert required in source,required
    assert "with _lock:_hf_accounts[sid]=user" not in source
    assert "account_chat_store.save_login(sid,user)" in source
    assert "project_thread_memory" in source
    assert source.count("_refresh_account_chat(s)")>=4
    assert "account_chat_store.load_chat(owner)" in source
    assert "github_connection.install(app, _account_session)" in source

if __name__=="__main__":
    test_google_cookie_redis_rehydrates_and_revokes()
    test_account_owner_chat_after_restart_and_conflicts()
    test_two_browser_cached_worker_refresh_and_non_destructive_conflicts()
    test_limits_enforced_no_silent_truncation_and_identity_isolation()
    test_source_wiring_and_sync_contract()
    print("Durable Google account chat persistence, restart and CAS checks passed")
