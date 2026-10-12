"""GitHub project workbench v213: checked source, model boundaries, scoped edits."""
import base64
import json
import re
import sys
from pathlib import Path
from unittest import mock
from urllib.parse import unquote
from fastapi import HTTPException

sys.path.insert(0,str(Path(__file__).parent))
import github_connection as gh
import github_project_v213 as gp
import github_workflows_v212 as actions

USER="google:verified"
REPO="team/app"
MAIN="1"*40
FEATURE="a"*40
BLOB="b"*40
FILE="def greet():\n    return 'before'\n"
REC={"repo":REPO,"token":"server-only-token","scopes":"read:user public_repo"}


def _api(_token,path):
    path=unquote(path)
    if path=="/repos/"+REPO:
        return {"full_name":REPO,"default_branch":"main","private":False,
                "language":"Python","open_issues_count":7,"permissions":{"pull":True,"push":True}}
    if path=="/repos/"+REPO+"/git/ref/heads/main":
        return {"object":{"sha":MAIN}}
    if path=="/repos/"+REPO+"/git/ref/heads/feature/test":
        return {"object":{"sha":FEATURE}}
    if path=="/repos/"+REPO+"/git/trees/"+MAIN+"?recursive=1":
        return {"tree":[{"path":"README.md","type":"blob"},
                        {"path":"src","type":"tree"},
                        {"path":"src/demo.py","type":"blob"},
                        {"path":"src/more.py","type":"blob"}],"truncated":False}
    if path.startswith("/search/code?q="):
        return {"total_count":2,"incomplete_results":False,
                "items":[{"path":"src/demo.py","sha":FEATURE,
                          "repository":{"full_name":REPO}}]}
    if path=="/repos/"+REPO+"/commits?path=src%2Fdemo.py&per_page=12" or \
       path=="/repos/"+REPO+"/commits?path=src/demo.py&per_page=12":
        return [{"sha":FEATURE,"commit":{"message":"fix greeting\nextra"}}]
    if path=="/repos/"+REPO+"/compare/main...feature/test?per_page=30":
        return {"status":"ahead","ahead_by":1,"behind_by":0,"total_commits":1,
                "merge_base_commit":{"sha":MAIN},
                "files":[{"filename":"src/demo.py","status":"modified","additions":1,"deletions":1}]}
    if path=="/repos/"+REPO+"/pulls/7":
        return {"number":7,"title":"Demo improvements","state":"open","draft":True,
                "mergeable":None,"changed_files":1,
                "base":{"ref":"main"},"head":{"ref":"feature/test","sha":FEATURE}}
    if path=="/repos/"+REPO+"/pulls/7/files?per_page=30":
        return [{"filename":"src/demo.py","status":"modified","additions":1,"deletions":1}]
    if path in ("/repos/"+REPO+"/commits/"+FEATURE+"/check-runs?per_page=30",
                "/repos/"+REPO+"/commits/"+FEATURE+"/check-runs?per_page=50"):
        return {"check_runs":[{"name":"Syntax check","status":"completed","conclusion":"success"},
                              {"name":"Integration","status":"in_progress","conclusion":None}]}
    if path=="/repos/"+REPO+"/issues/8":
        return {"number":8,"title":"Unexpected behavior","state":"open",
                "labels":[{"name":"bug"}],"body":"Inspect source before fix"}
    if path=="/repos/"+REPO+"/issues/8/comments?per_page=8":
        return [{"user":{"login":"reviewer"},"body":"Reproduced."}]
    if path=="/repos/"+REPO+"/contents/src/demo.py?ref=feature/test":
        return {"type":"file","size":len(FILE),"sha":BLOB,"encoding":"base64",
                "content":base64.b64encode(FILE.encode()).decode(),"html_url":"https://github.com/team/app/blob/feature/test/src/demo.py"}
    raise AssertionError("Unexpected repo URL "+path)


def memory():
    saved={}
    def redis(_cfg,action,key,*args):
        if action=="SET":
            if key in saved:return None
            saved[key]=args[0]
            return "OK"
        if action=="GETDEL":return saved.pop(key,None)
        raise AssertionError(action)
    return redis


def test_bounded_read_research():
    with mock.patch.object(gh,"_api",side_effect=_api):
        overview=gp._summary(gh,REC,REPO,"overview")
        assert "Default branch: main" in overview and "Primary language: Python" in overview
        guide=gp._summary(gh,REC,REPO,"project guide")
        assert "Project engineering loop" in guide and "DRAFT PR" in guide
        tree=gp._summary(gh,REC,REPO,"tree src")
        assert "src/demo.py" in tree and "README.md" not in tree
        code=gp._summary(gh,REC,REPO,"code search greet")
        assert "src/demo.py" in code and "Provider-reported matches" in code
        history=gp._summary(gh,REC,REPO,"file history src/demo.py")
        assert "fix greeting" in history
        diff=gp._summary(gh,REC,REPO,"compare main...feature/test")
        assert "src/demo.py" in diff and "1/0" in diff
        pr=gp._summary(gh,REC,REPO,"pr review 7")
        assert "Integration · in_progress" in pr
        assert "not" not in pr or "No source merge" in pr
        issue=gp._summary(gh,REC,REPO,"issue inspect 8")
        assert "Reproduced" in issue
        checks=gp._summary(gh,REC,REPO,"checks "+FEATURE)
        assert "Integration · in_progress/" in checks
        assert "not successful checks" in checks


def test_command_and_path_guards():
    for cmd in ("@GitHub overview","@GitHub code search greet","@GitHub compare main...feature/test",
                "@GitHub pr review 7", "@GitHub edit file src/demo.py on feature/test replace before :: after",
                "@GitHub pr draft feature/test into main"):
        assert gp.is_command(cmd)
        assert gh.is_github_command(cmd)
    assert not gp.is_command("Please delete the repo")
    for value in ("../oops.py",".deploy/HF_SPACE_REQUEST.txt",".github/workflows/ci.yml",
                  "versions/server-runtime.txt","src/secret.json","VERSION.txt","src/a.png",
                  "src/../module.py"):
        try:gp._path(value,editing=True)
        except HTTPException:pass
        else:raise AssertionError("unsafe edit path "+value)
    for b in ("main","runtime","hotfix","feature/../oops"):
        try:gp._ref(b,feature=True)
        except HTTPException:pass
        else:raise AssertionError("protected branch "+b)


def test_one_use_approved_edit_and_no_secret_model_input():
    redis=memory()
    receipt={"content":{"path":"src/demo.py"},"commit":{"sha":"c"*40}}
    with mock.patch.object(gh,"_config",return_value={}),\
         mock.patch.object(gh,"_load",return_value=REC),\
         mock.patch.object(gh,"_redis",side_effect=redis),\
         mock.patch.object(gh,"_api",side_effect=_api),\
         mock.patch.object(actions,"_write_request",return_value=receipt) as write:
        result=gh._github_command(USER,"@GitHub edit file src/demo.py on feature/test replace before :: after")
        assert "NOT written" in result and not write.called
        assert "Existing blob: "+BLOB in result
        code=re.search(r"@GitHub confirm ([\w-]+)",result).group(1)
        confirmed=gh._github_command(USER,"@GitHub confirm "+code)
        assert "GitHub confirmed one file changed" in confirmed and write.call_count==1
        args=write.call_args.args
        assert args[1]=="PUT" and args[3]["sha"]==BLOB
        assert "after" in base64.b64decode(args[3]["content"]).decode()
        assert "before" not in base64.b64decode(args[3]["content"]).decode()
        duplicate=gh._github_command(USER,"@GitHub confirm "+code)
        assert "already used" in duplicate and write.call_count==1
    with mock.patch.object(gh,"_api",side_effect=_api),\
         mock.patch.object(gh,"_config",return_value={}),\
         mock.patch.object(gh,"_load",return_value=REC),\
         mock.patch.object(gh,"_redis",side_effect=AssertionError("No store")):
        denied=gp._edit_proposal(gh,{},REC,USER,REPO,"edit file src/demo.py on feature/test replace nonexistent :: change")
        assert "exactly once" in denied


def test_branch_staleness_and_repo_role_guard():
    pending={"kind":"project-edit","path":"src/demo.py","branch":"feature/test",
             "headSha":"d"*40,"blobSha":BLOB,"old":"before","new":"after"}
    with mock.patch.object(gh,"_api",side_effect=_api),\
         mock.patch.object(actions,"_write_request") as write:
        result=gp.confirm(gh,{},REC,USER,REPO,pending)
        assert "Branch advanced" in result and not write.called
    with mock.patch.object(gh,"_api",side_effect=_api),\
         mock.patch.object(gh,"_config",return_value={}),\
         mock.patch.object(gh,"_load",return_value={**REC,"scopes":"read:user"}),\
         mock.patch.object(gh,"_redis",side_effect=AssertionError("No proposal")):
        reply=gp.execute(gh,USER,"@GitHub edit file src/demo.py on feature/test replace before :: after")
        assert "cannot authorize" in reply.lower() and "public_repo" in reply


def test_draft_pr_confirmation_and_no_merge():
    redis=memory()
    with mock.patch.object(gh,"_config",return_value={}),\
         mock.patch.object(gh,"_load",return_value=REC),\
         mock.patch.object(gh,"_redis",side_effect=redis),\
         mock.patch.object(gh,"_api",side_effect=_api),\
         mock.patch.object(actions,"_write_request",return_value={
            "number":9,"html_url":"https://github.com/team/app/pull/9"}) as write:
        candidate=gh._github_command(USER,"@GitHub pr draft feature/test into main")
        assert "NOT created" in candidate and not write.called and "src/demo.py" in candidate
        code=re.search(r"@GitHub confirm ([\w-]+)",candidate).group(1)
        confirmed=gh._github_command(USER,"@GitHub confirm "+code)
        assert "DRAFT PR #9" in confirmed and "Not merged" in confirmed
        assert write.call_count==1
        body=write.call_args.args[3]
        assert body["draft"] is True and body["head"]=="feature/test"
        assert "already used" in gh._github_command(USER,"@GitHub confirm "+code)


def test_protected_diff_never_generates_pr():
    def altered(token,path):
        if "/compare/" in path:
            return {"total_commits":1,"files":[{"filename":".github/workflows/deploy.yml"}]}
        return _api(token,path)
    with mock.patch.object(gh,"_api",side_effect=altered),\
         mock.patch.object(gh,"_redis",side_effect=AssertionError("PR proposal not allowed")):
        got=gp._pr_proposal(gh,{},REC,USER,REPO,"pr draft feature/test into main")
        assert "protected paths" in got


def test_project_progress_and_model_read_ownership():
    with mock.patch.object(gh,"_config",return_value={}),\
         mock.patch.object(gh,"_load",return_value=REC),\
         mock.patch.object(gh,"_api",side_effect=_api):
        events=list(gh.agent_events({"userId":USER,"prompt":"@GitHub overview"}))
    phases=[e["phase"] for e in events if e.get("type")=="STATUS"]
    assert phases==["GITHUB_PROJECT_ACCESS_CHECK","GITHUB_PROJECT_SOURCE_INSPECTION","GITHUB_PROJECT_RESULT"]
    assert "Primary language" in "".join(x.get("text","") for x in events)
    assert gh._agent_allowed_tool("overview","show my repo overview")=="overview"
    assert gh._agent_allowed_tool("tree","show my repo map")=="tree"
    assert gh._agent_allowed_tool("edit file src/demo.py","edit my repo file") is None
    assert "server-only-token" not in str(events)
    root=Path(__file__).parent.parent
    station=(root/"hf_space/station.py").read_text()
    assert "github_connection.agent_events(" in station
    assert "github_project_v213.confirm" in (root/"hf_space/github_connection.py").read_text()


if __name__=="__main__":
    test_bounded_read_research()
    test_command_and_path_guards()
    test_one_use_approved_edit_and_no_secret_model_input()
    test_branch_staleness_and_repo_role_guard()
    test_draft_pr_confirmation_and_no_merge()
    test_protected_diff_never_generates_pr()
    test_project_progress_and_model_read_ownership()
    print("v213 GitHub project evidence and confirmed edit tests passed")
