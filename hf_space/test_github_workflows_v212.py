"""v212 GitHub Actions read, manual dispatch and reviewed workflow authoring gates."""
import base64
import json
import re
import sys
from urllib.parse import unquote
from pathlib import Path
from unittest import mock
from fastapi import HTTPException
sys.path.insert(0,str(Path(__file__).parent))
import github_connection as gh
import github_workflows_v212 as w

OWNER = "google:owner"
REPO = "owner/repository"
RECORD = {"token":"private-test-token", "repo":REPO, "scopes":"read:user public_repo workflow"}
SHA = "a"*40
YAML = w._TEMPLATES["python-check"]


def info(path):
    path = unquote(path)
    if path == "/repos/" + REPO:
        return {"full_name":REPO,"private":False,"default_branch":"main",
                "permissions":{"push":True,"admin":True,"triage":True}}
    if path.startswith("/repos/" + REPO + "/git/ref/heads/"):
        return {"object":{"sha":SHA}}
    if path == "/repos/" + REPO + "/actions/workflows?per_page=35":
        return {"workflows":[{"name":"Python syntax checks","path":".github/workflows/check.yml","state":"active"}]}
    if path == "/repos/" + REPO + "/actions/runs?per_page=12":
        return {"workflow_runs":[{"id":1234,"name":"Test CI","status":"completed",
                                  "conclusion":"success"}]}
    if path == "/repos/" + REPO + "/actions/runs/1234":
        return {"id":1234,"name":"Test CI","head_branch":"main",
                "status":"completed","conclusion":"success"}
    if path == "/repos/" + REPO + "/actions/runs/9876":
        return {"id":9876,"name":"Unit tests","head_branch":"main",
                "status":"completed","conclusion":"failure"}
    if path == "/repos/" + REPO + "/actions/runs/1234/jobs?per_page=25":
        return {"jobs":[{"name":"test","status":"completed","conclusion":"success","steps":[]}]}
    if path == "/repos/" + REPO + "/actions/workflows/check.yml":
        return {"id":42,"name":"Unit tests","path":".github/workflows/check.yml","state":"active"}
    if path.endswith("/contents/.github/workflows?ref=feature/test"):
        return [{"path":".github/workflows/check.yml","type":"file"}]
    if "/contents/.github/workflows/" in path:
        if path.endswith("check.yml?ref=main"):
            return {"type":"file","size":len(YAML),"sha":"b"*40,
                    "content":base64.b64encode(YAML.encode()).decode(),"encoding":"base64"}
        if path.endswith("check.yml?ref=feature/test"):
            raise HTTPException(404,"File not found")
        if path.endswith("syntax.yml?ref=feature/test"):
            raise HTTPException(404,"File not found")
    raise AssertionError("Unexpected GitHub API path: " + path)


def test_capability_scopes_and_exact_oauth_modes():
    with mock.patch.object(gh,"_api",side_effect=lambda token,path:info(path)):
        got=gh._effective_access(RECORD,REPO,"workflow-create")
        assert got["allowed"] and "workflow-create" in got["available"]
        dispatch=gh._effective_access(RECORD,REPO,"workflow-dispatch")
        assert dispatch["allowed"]
        without=dict(RECORD,scopes="read:user public_repo")
        denied=gh._effective_access(without,REPO,"workflow-create")
        assert not denied["allowed"] and denied["authorizeUrl"].endswith("public-workflow")
        assert "workflow scope" in denied["missing"]
        assert gh._effective_access(without,REPO,"workflow-dispatch")["allowed"]
        read=gh._effective_access({"token":"t","scopes":"read:user","repo":REPO},REPO,"read")
        assert read["allowed"]
    assert "workflow" in gh._GITHUB_ACCESS["public-workflow"]
    assert "workflow" in gh._GITHUB_ACCESS["private-workflow"]
    assert "workflow" not in gh._GITHUB_ACCESS["read"]


def test_read_workflows_and_exact_run_status():
    with mock.patch.object(gh,"_api",side_effect=lambda token,path:info(path)):
        assert "check.yml" in w._read(gh,RECORD,REPO,"workflows")
        assert "success" in w._read(gh,RECORD,REPO,"workflow runs")
        assert "test" in w._read(gh,RECORD,REPO,"run status 1234")
        report=w._read(gh,RECORD,REPO,"workflow inspect check.yml")
        assert "workflow_dispatch" in report and "untrusted data" in report
        assert "OAuth workflow scope" in w._read(gh,RECORD,REPO,"workflow guide")
    assert w.is_command("@GitHub workflow create python-check as syntax.yml on feature/test")
    assert w.is_command("@GitHub workflow dispatch check.yml on main")
    assert w.is_command("@GitHub workflow pr feature/test into main")
    assert w.is_command("@GitHub run retry 9876")


def test_reviewed_template_creation_is_two_step_and_no_overwrite():
    saved = {}
    def redis(_,action,key,*args):
        if action=="SET":
            saved[key]=args[0]
            return "OK"
        if action=="GETDEL":
            return saved.pop(key,None)
        raise AssertionError(action)
    with mock.patch.object(gh,"_api",side_effect=lambda token,path:info(path)), \
         mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_redis",side_effect=redis), \
         mock.patch.object(w,"_write_request",side_effect=lambda *a:{"content":{"path":".github/workflows/syntax.yml"}}) as write:
        preview=gh._github_command(OWNER,"@GitHub workflow create python-check as syntax.yml on feature/test")
        assert "NOT written" in preview and "workflow_dispatch" in preview and not write.called
        code=re.search(r"@GitHub confirm ([\w-]+)",preview).group(1)
        receipt=gh._github_command(OWNER,"@GitHub confirm "+code)
        assert "file creation" in receipt and write.call_count==1
        assert "NOT merged" in receipt
        again=gh._github_command(OWNER,"@GitHub confirm "+code)
        assert "already used" in again and write.call_count==1


def test_reject_invalid_paths_protected_targets_and_inferred_scripts():
    for name in ("../danger.yml","a/b.yml","deploy.yml/","bad.yml?"):
        try:w._safe_workflow(name)
        except HTTPException:pass
        else:raise AssertionError("Unsafe workflow filename allowed: "+name)
    for name in ("main","runtime","release/bad","feature/../bad"):
        try:w._safe_ref(name,authoring=True)
        except HTTPException:pass
        else:raise AssertionError("Protected branch allowed: "+name)
    assert w._parse_dispatch_inputs("mode=check,seed=12")=={"mode":"check","seed":"12"}
    for arg in ("script=$(rm)", "key=hello world", "password='abc'", "key=x,key=y"):
        try:w._parse_dispatch_inputs(arg)
        except HTTPException:pass
        else:raise AssertionError("Unbounded input accepted")
    assert not w._triggers_manually("name: not dispatched\non: push\n")
    assert w._triggers_manually(YAML)
    assert not gh._agent_allowed_tool("workflow dispatch check.yml on main",
                                       "Run my workflow now")


def test_dispatch_is_explicit_and_accepted_is_not_success():
    saved={}
    def redis(_,operation,key,*args):
        if operation=="SET":saved[key]=args[0];return "OK"
        if operation=="GETDEL":return saved.pop(key,None)
        raise AssertionError(operation)
    with mock.patch.object(gh,"_api",side_effect=lambda token,path:info(path)), \
         mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_redis",side_effect=redis), \
         mock.patch.object(w,"_write_request",return_value={"accepted":True,"workflowRunId":None}) as write:
        preview=gh._github_command(OWNER,"@GitHub workflow dispatch check.yml on main")
        assert "NOT triggered" in preview and not write.called
        code=re.search(r"@GitHub confirm ([\w-]+)",preview).group(1)
        receipt=gh._github_command(OWNER,"@GitHub confirm "+code)
        assert write.call_count==1
        assert "accepted" in receipt and "NOT yet confirmed" in receipt
        assert "inspect the workflow runs" in receipt


def test_cross_owner_and_stale_branch_never_execute():
    action={"owner":"google:someone-else","repo":REPO,"kind":"workflow-file","template":"python-check",
            "name":"syntax.yml","branch":"feature/test","baseSha":SHA}
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=RECORD), \
         mock.patch.object(gh,"_redis",return_value=json.dumps(action)), \
         mock.patch.object(w,"_write_request") as write:
        assert "ownership mismatch" in gh._github_command(OWNER,"@GitHub confirm Abcdefghi1")
        assert not write.called
    with mock.patch.object(gh,"_api",side_effect=lambda token,path:info(path)), \
         mock.patch.object(w,"_write_request") as write:
        action["owner"]=OWNER
        action["baseSha"]="c"*40
        result=w.confirm(gh,{},RECORD,OWNER,REPO,action)
        assert "Branch moved" in result and not write.called


def test_protected_workflows_cannot_dispatch():
    with mock.patch.object(gh,"_api",side_effect=lambda token,path:(
            {"id":30,"name":"Production deploy","path":".github/workflows/deploy.yml","state":"active"}
            if path.endswith("/actions/workflows/deploy.yml") else info(path))), \
         mock.patch.object(gh,"_redis",side_effect=AssertionError("Must not propose protected action")):
        got=w._propose(gh,{},RECORD,OWNER,REPO,"workflow dispatch deploy.yml on main")
        assert "Protected" in got


def test_workflow_draft_pr_and_failed_jobs_retry_require_second_confirmation():
    saved = {}
    def redis(_cfg, op, key, *args):
        if op == "SET":
            saved[key] = args[0]
            return "OK"
        if op == "GETDEL":
            return saved.pop(key, None)
        raise AssertionError("unexpected state mutation " + op)
    replies = iter([
        {"number": 73, "html_url": "https://github.com/owner/repository/pull/73"},
        {"accepted": True}
    ])
    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load", return_value=RECORD), \
         mock.patch.object(gh, "_api", side_effect=lambda token, path: info(path)), \
         mock.patch.object(gh, "_redis", side_effect=redis), \
         mock.patch.object(w, "_write_request", side_effect=lambda *args: next(replies)) as write:
        proposal=gh._github_command(OWNER, "@GitHub workflow pr feature/test into main")
        assert "NOT created" in proposal and not write.called
        code=re.search(r"@GitHub confirm ([\w-]+)", proposal).group(1)
        done=gh._github_command(OWNER, "@GitHub confirm " + code)
        assert "DRAFT PR #73" in done and "NOT merged" in done and write.call_count == 1
        proposal=gh._github_command(OWNER, "@GitHub run retry 9876")
        assert "NOT executed" in proposal and write.call_count == 1
        code=re.search(r"@GitHub confirm ([\w-]+)", proposal).group(1)
        accepted=gh._github_command(OWNER, "@GitHub confirm " + code)
        assert "accepted a retry request" in accepted
        assert "NOT a completed run" in accepted
        assert write.call_count == 2
        assert "already used" in gh._github_command(OWNER, "@GitHub confirm " + code)


def test_read_only_guidance_never_requests_oauth_upgrade():
    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load", return_value=RECORD), \
         mock.patch.object(gh, "_api", side_effect=lambda token, path: info(path)):
        report=gh._github_command(OWNER, "@GitHub workflow guide")
        assert "workflow_dispatch" in report
        assert "OAuth workflow scope" in report
        assert "Authorize" not in report
    ui=(Path(__file__).parent.parent/"chat/§wyrlz/index.html").read_text()
    assert 'id="githubWorkflowGuide"' in ui
    assert 'prompt.value="@GitHub workflow guide"' in ui


def test_static_station_progress_and_read_only_model_plan():
    station=(Path(__file__).parent/"station.py").read_text()
    chat=(Path(__file__).parent.parent/"chat/§wyrlz/index.html").read_text()
    assert "github_connection.agent_events(" in station
    assert "GITHUB_WORKFLOW_PERMISSION_CHECK" in Path(w.__file__).read_text()
    assert 'id="githubCheckOperation"' in chat
    assert "workflow-create" in chat
    assert "workflow-dispatch" in chat
    assert "workflow_dispatch" in w._TEMPLATES["repo-audit"]
    assert "workflow" not in gh._GITHUB_ACCESS["read"]


if __name__=="__main__":
    test_capability_scopes_and_exact_oauth_modes()
    test_read_workflows_and_exact_run_status()
    test_reviewed_template_creation_is_two_step_and_no_overwrite()
    test_reject_invalid_paths_protected_targets_and_inferred_scripts()
    test_dispatch_is_explicit_and_accepted_is_not_success()
    test_cross_owner_and_stale_branch_never_execute()
    test_protected_workflows_cannot_dispatch()
    test_workflow_draft_pr_and_failed_jobs_retry_require_second_confirmation()
    test_read_only_guidance_never_requests_oauth_upgrade()
    test_static_station_progress_and_read_only_model_plan()
    print("v212 GitHub Actions workflow workbench regressions passed")
