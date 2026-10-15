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
    if path=="/repos/"+REPO+"/commits/main":
        return {"sha":"b"*40}
    if path=="/repos/"+REPO+"/git/trees/"+("b"*40)+"?recursive=1":
        return {"truncated":False,"tree":[{"type":"blob","mode":"100644","path":"README.md"},
                                         {"type":"blob","mode":"100644","path":"src/app.py"}]}
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
        assert (repo,path,ref)==(REPO,"README.md","b"*40)
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
         mock.patch.object(gh,"_load",return_value=REC), \
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


def test_v222_filename_resolution_and_ambiguous_paths():
    sha="b"*40
    choices=[
        {"path":"README.md","type":"blob","mode":"100644"},
        {"path":"src/app.py","type":"blob","mode":"100644"},
        {"path":"src/config.py","type":"blob","mode":"100644"},
        {"path":"docs/config.json","type":"blob","mode":"100644"},
        {"path":"src/server.toml","type":"blob","mode":"100644"},
        {"path":"lib/server.toml","type":"blob","mode":"100644"},
        {"path":"src/.env","type":"blob","mode":"100644"},
        {"path":"assets/config","type":"tree","mode":"040000"},
    ]
    def api(_token,path):
        if path=="/repos/"+REPO:
            return {"full_name":REPO,"private":False,"default_branch":"main",
                    "permissions":{"pull":True}}
        if path=="/repos/"+REPO+"/commits/main":
            return {"sha":sha}
        if path=="/repos/"+REPO+"/git/trees/"+sha+"?recursive=1":
            return {"tree":choices,"truncated":False}
        raise AssertionError(path)
    reads=[]
    def bounded(_token,repo,path,ref,max_bytes=100000):
        reads.append((repo,path,ref))
        return {"body":"exact source for "+path,"sha":"f"*40,
                "url":"https://github.com/example/demo/blob/"+sha+"/"+path}
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=REC), \
         mock.patch.object(gh,"_api",side_effect=api), \
         mock.patch.object(gh,"_read_optional",side_effect=bounded):
        # Extension isn't required; unique match is read at the verified SHA.
        result=gh._github_command(USER,"@GitHub read the app file")
        assert "src/app.py" in result and reads==[(REPO,"src/app.py",sha)],result
        result=gh._github_command(USER,"@GitHub read file README")
        assert "README.md" in result
        result=gh._github_command(USER,"@GitHub read file src/.env")
        assert "src/.env" in result
        before=len(reads)
        response=gh._github_command(USER,"@GitHub read file config")
        assert "Which one should I read?" in response,response
        assert "src/config.py" in response and "docs/config.json" in response,response
        assert len(reads)==before,"Ambiguous file unexpectedly read"
        response=gh._github_command(USER,"@GitHub read file server.toml")
        assert "src/server.toml" in response and "lib/server.toml" in response
        assert len(reads)==before
        response=gh._github_command(USER,"@GitHub read file src/config")
        assert "src/config.py" in response and len(reads)==before+1
        response=gh._github_command(USER,"@GitHub read file docs/config.json")
        assert "docs/config.json" in response and len(reads)==before+2
        response=gh._github_command(USER,"@GitHub read file nonexistent")
        assert "No matching file was found" in response and len(reads)==before+2
        assert "config" == gh._natural_repo_read_target("Read the config file in our repository")
        assert gh._natural_repo_read_target("Read the config file") is None
        result=list(gh.agent_events({"userId":USER,
                                      "prompt":"Read the config file in our repository"}))
        assert any("Which one should I read?" in str(e.get("text") or "") for e in result)
        assert not any(e.get("phase")=="GITHUB_STAGE_LOCKED" for e in result)
        assert len(reads)==before+2
        assert gh._read_stage_command("@GitHub read file app")
        assert gh._read_stage_command("@GitHub open the app file")
        assert not gh._read_stage_command("@GitHub create file app.py")


def test_v222_incomplete_tree_never_auto_selects():
    sha="b"*40
    def api(_token,path):
        if path=="/repos/"+REPO: return {"full_name":REPO,"private":False,
                                         "default_branch":"main","permissions":{"pull":True}}
        if path=="/repos/"+REPO+"/commits/main": return {"sha":sha}
        if path=="/repos/"+REPO+"/git/trees/"+sha+"?recursive=1":
            return {"tree":[{"path":"src/config.py","type":"blob","mode":"100644"}],
                    "truncated":True}
        raise AssertionError(path)
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=REC), \
         mock.patch.object(gh,"_api",side_effect=api), \
         mock.patch.object(gh,"_read_optional",side_effect=AssertionError("Truncated-tree read")):
        result=gh._github_command(USER,"@GitHub read file config")
        assert "incomplete" in result and "full repository path" in result,result



def test_v223_recursive_stats_are_source_pinned_and_fail_closed():
    sha="b"*40
    rows=[{"path":"src","type":"tree"},
          {"path":"src/app.py","type":"blob","size":120},
          {"path":"src/config.json","type":"blob","size":30},
          {"path":"docs","type":"tree"},
          {"path":"docs/README.md","type":"blob","size":60}]
    def api(_token,path):
        if path=="/repos/"+REPO+"/commits/main":return {"sha":sha}
        if path=="/repos/"+REPO+"/git/trees/"+sha+"?recursive=1":
            return {"tree":rows,"truncated":False}
        raise AssertionError(path)
    with mock.patch.object(gh,"_api",side_effect=api):
        root=gh._github_repo_stats({"token":"test"},REPO,"main")
        assert "Files: 3" in root and "Directories: 2" in root and "Git blob bytes: 210" in root,root
        folder=gh._github_repo_stats({"token":"test"},REPO,"main","src")
        assert "Files: 2" in folder and "Directories: 0" in folder and "Git blob bytes: 150" in folder,folder
        assert "not found" in gh._github_repo_stats({"token":"test"},REPO,"main","missing")
        assert gh._read_stage_command("@GitHub stats")
        assert gh._read_stage_command("@GitHub stats src")
        assert not gh._read_stage_command("@GitHub delete file src/app.py")
    with mock.patch.object(gh,"_api",side_effect=lambda t,p: {"sha":sha} if "/commits/" in p else {"tree":rows,"truncated":True}):
        assert "incomplete" in gh._github_repo_stats({"token":"test"},REPO,"main")


if __name__=="__main__":
    test_stage_one_reading()
    test_locked_writes_even_with_oauth_grants()
    test_oauth_write_and_prior_pending_code()
    test_model_and_commands_cannot_bypass_stage()
    test_v222_filename_resolution_and_ambiguous_paths()
    test_v222_incomplete_tree_never_auto_selects()
    test_v223_recursive_stats_are_source_pinned_and_fail_closed()
    print("GitHub Stage 1 repository reading and locked mutation gates PASS")
