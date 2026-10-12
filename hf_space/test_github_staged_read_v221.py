"""Stage 1: source-only GitHub permissions and bounded repository reads."""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import json
from fastapi import HTTPException
sys.path.insert(0, str(Path(__file__).parent))
import github_connection as gh

USER = "google:owner"
REPO = "example/demo"
REC = {"token":"opaque-test-token","repo":REPO,"scopes":"read:user repo workflow"}

def fake_api(_token,path):
    if path=="/repos/"+REPO:
        return {"full_name":REPO,"private":False,"default_branch":"main",
                "permissions":{"pull":True,"push":True,"admin":True}}
    if path=="/repos/"+REPO+"/contents?ref=main":
        return [{"type":"file","path":"README.md"},{"type":"dir","path":"src"}]
    if path=="/repos/"+REPO+"/contents/src?ref=main":
        return [{"type":"file","path":"src/app.py"}]
    raise AssertionError("Unexpected API call "+path)

def test_stage_one_reading():
    assert gh.GITHUB_CAPABILITY_STAGE=="read-repository"
    for cmd in ("@GitHub files","@GitHub files src","@GitHub read file README.md",
                "@GitHub help","@GitHub permissions"):
        assert gh._read_stage_command(cmd),cmd
    for cmd in ("@GitHub confirm abc123XYZ","@GitHub create issue hello",
                "@GitHub create branch feature/name from main",
                "@GitHub edit file README.md on feature/name replace a :: b",
                "@GitHub workflow dispatch build.yml on main",
                "@GitHub engine code task improve editor on feature/name"):
        assert not gh._read_stage_command(cmd),cmd
    def read_file(_token, repo, path, ref, max_bytes=100000):
        assert (repo,path,ref)==(REPO,"README.md","main")
        return {"body":"# Demo\nHello source.","sha":"a"*40,"url":"https://github.com/example/demo"}
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=REC), \
         mock.patch.object(gh,"_api",side_effect=fake_api), \
         mock.patch.object(gh,"_read_optional",side_effect=read_file), \
         mock.patch.object(gh,"_redis",side_effect=AssertionError("A proposal was touched")):
        assert "README.md" in gh._github_command(USER,"@GitHub files")
        assert "src/app.py" in gh._github_command(USER,"@GitHub files src")
        assert "Hello source." in gh._github_command(USER,"@GitHub read file README.md")
        assert "Stage 1" in gh._github_command(USER,"@GitHub help")
        for cmd in ("@GitHub confirm abc123XYZ","@GitHub create issue hello",
                    "@GitHub workflow dispatch build.yml on main",
                    "@GitHub engine code task improve editor on feature/name"):
            result=gh._github_command(USER,cmd)
            assert "disabled" in result.lower() and "No GitHub mutation" in result,cmd

def test_locked_writes_even_with_oauth_grants():
    with mock.patch.object(gh,"_api",side_effect=fake_api):
        assert gh._effective_access(REC,REPO,"read")["allowed"]
        for op in ("issue-write","branch-write","workflow-create","workflow-dispatch"):
            info=gh._effective_access(REC,REPO,op)
            assert not info["allowed"] and info["available"]==["read"]
            assert info["stageLocked"] and "authorizeUrl" not in info
    with mock.patch.object(gh,"_current_connection",return_value=(USER,{},REC)), \
         mock.patch.object(gh,"_api",side_effect=fake_api):
        assert not gh.capabilities(object(),operation="branch-write")["allowed"]
        assert gh.capabilities(object(),operation="read")["allowed"]
    with mock.patch.object(gh.requests,"post",side_effect=AssertionError("Network mutation")):
        try: gh._post_github(REC["token"],"/repos/"+REPO+"/issues",{})
        except HTTPException as exc: assert exc.status_code==403
        else: raise AssertionError("write helper was not blocked")

def test_oauth_write_and_prior_pending_code():
    with mock.patch.object(gh,"_google",return_value=USER), \
         mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_redis",side_effect=AssertionError("OAuth state created")):
        try: gh.start(object(),access="public-write")
        except HTTPException as exc: assert exc.status_code==403
        else: raise AssertionError("write OAuth request started")
    request=SimpleNamespace(cookies={"swrlz_github_oauth":"nonce"})
    pending=json.dumps({"owner":USER,"access":"private-write","verifier":"old"})
    with mock.patch.object(gh,"_google",return_value=USER), \
         mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_redis",return_value=pending), \
         mock.patch.object(gh.requests,"post",side_effect=AssertionError("Token exchange")):
        try: gh.callback(request,code="old",state="nonce")
        except HTTPException as exc: assert exc.status_code==403
        else: raise AssertionError("old write OAuth callback accepted")

def test_model_and_commands_cannot_bypass_stage():
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=REC), \
         mock.patch.object(gh,"_api",side_effect=fake_api), \
         mock.patch.object(gh.engine_code_agent_v217,"events",side_effect=AssertionError("Engine bypass")), \
         mock.patch.object(gh.github_workflows_v212,"events",side_effect=AssertionError("Workflow bypass")):
        actual=list(gh.agent_events({"userId":USER,"prompt":"@GitHub files"}))
        assert any("README.md" in x.get("text","") for x in actual)
        for cmd in ("@GitHub confirm abc123XYZ",
                    "@GitHub workflow dispatch build.yml on main",
                    "@GitHub engine code task improve editor on feature/name",
                    "Can you create a branch in our repository?"):
            result=list(gh.agent_events({"userId":USER,"prompt":cmd}))
            assert any(x.get("phase")=="GITHUB_STAGE_LOCKED" for x in result),cmd
        with mock.patch.object(gh,"GITHUB_CAPABILITY_STAGE","unknown"):
            result=list(gh.agent_events({"userId":USER,"prompt":"@GitHub files"}))
            assert any("fail closed" in x.get("text","") for x in result)
    assert gh.is_start_request("Read the §tart document and follow the project startup contract")

if __name__=="__main__":
    test_stage_one_reading()
    test_locked_writes_even_with_oauth_grants()
    test_oauth_write_and_prior_pending_code()
    test_model_and_commands_cannot_bypass_stage()
    print("GitHub Stage 1 repository reading and locked mutation gates PASS")
