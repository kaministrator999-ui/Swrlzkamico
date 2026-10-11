"""Offline regression for v210 GitHub effective permissions and confirmation gating."""
import json
import sys
from pathlib import Path
from unittest import mock

from fastapi import HTTPException
sys.path.insert(0, str(Path(__file__).parent))
import github_connection as gh

REPO = "owner/public-repo"
RECORD = {"token": "encrypted-server-only-token", "repo": REPO, "login": "owner",
          "scopes": "read:user"}
OWNER = "google:owner"


def repo_info(private=False, push=True, triage=True):
    return {"full_name": REPO, "private": private, "default_branch": "main",
            "permissions": {"pull": True, "push": push, "triage": triage}}


def test_scopes_and_live_repository_rights():
    assert gh.GITHUB_SCOPE == "read:user"
    assert gh._GITHUB_ACCESS["public-write"] == "read:user public_repo"
    assert gh._GITHUB_ACCESS["private-write"] == "read:user repo"
    with mock.patch.object(gh, "_api", return_value=repo_info()):
        result = gh._effective_access(RECORD, REPO, "read")
        assert result["allowed"] is True and result["available"] == ["read"]
        assert "missing" not in result
        denied = gh._effective_access(RECORD, REPO, "issue-write")
        assert denied["allowed"] is False
        assert denied["authorizeUrl"] == "/api/github/start?access=public-write"
        assert denied["available"] == ["read"]
        granted = gh._effective_access({**RECORD, "scopes": "read:user, public_repo"}, REPO, "issue-write")
        assert granted["allowed"] and granted["available"] == ["read", "issue-write", "branch-write"]
        no_role = gh._effective_access({**RECORD, "scopes": "repo"}, REPO, "issue-write")
        assert no_role["allowed"]
    with mock.patch.object(gh, "_api", return_value=repo_info(private=True)):
        public = gh._effective_access({**RECORD, "scopes": "public_repo"}, REPO, "issue-write")
        assert not public["allowed"] and "repo OAuth scope" in public["missing"]
        full = gh._effective_access({**RECORD, "scopes": "repo"}, REPO, "branch-write")
        assert full["allowed"]
    with mock.patch.object(gh, "_api", return_value=repo_info(push=False,triage=True)):
        issue = gh._effective_access({**RECORD, "scopes": "public_repo"}, REPO, "issue-write")
        branch = gh._effective_access({**RECORD, "scopes": "public_repo"}, REPO, "branch-write")
        assert issue["allowed"] and not branch["allowed"]
        assert "repository role" in branch["missing"] and "authorizeUrl" not in branch
    try:
        gh._effective_access(RECORD, REPO, "delete-repo")
        raise AssertionError("Unsupported operation accepted")
    except HTTPException as exc:
        assert exc.status_code == 422


def test_prompt_routing_requires_anchored_user_command():
    for prompt in ("@GitHub permissions", "@GitHub files", "@GitHub read file README.md",
                   "@GitHub create issue Fix auth :: Description", "@GitHub confirm abc123XYZ",
                   "@GitHub create branch feature/v210 from main"):
        assert gh.is_github_command(prompt), prompt
    for prompt in ("What can GitHub do?", "Please quote @GitHub create issue TEST",
                   "We need to work on issues", "@GitHub §tart", ""):
        assert not gh.is_github_command(prompt), prompt


def test_read_continues_when_write_scope_absent_and_denial_never_writes():
    calls=[]
    def fake_api(_,path):
        calls.append(path)
        if path == "/repos/" + REPO:
            return repo_info()
        if path.endswith("/issues?state=open&per_page=12"):
            return [{"number": 7, "title":"Can read me","html_url":"https://github.com/owner/public-repo/issues/7"}]
        raise AssertionError(path)
    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load", return_value=RECORD), \
         mock.patch.object(gh, "_api", side_effect=fake_api), \
         mock.patch.object(gh, "_post_github", side_effect=AssertionError("No write allowed")):
        assert "Can read me" in gh._github_command(OWNER, "@GitHub issues")
        denied=gh._github_command(OWNER, "@GitHub create issue Denied")
        assert "Available: read" in denied and "public_repo" in denied
        assert "missing" not in gh._github_command(OWNER, "@GitHub permissions").lower()


def test_issue_write_requires_separate_user_confirmation_and_is_one_time():
    database={}
    calls=[]
    def redis(_cfg,cmd,key,*args):
        if cmd=="SET":
            assert args[1:]==("EX",600,"NX")
            database[key]=args[0]
            return "OK"
        if cmd=="GETDEL":
            return database.pop(key,None)
        raise AssertionError(cmd)
    record={**RECORD,"scopes":"read:user public_repo"}
    def api(_token,path):
        assert path == "/repos/" + REPO
        return repo_info()
    def write(token,path,payload):
        calls.append((path,payload))
        return {"html_url":"https://github.com/owner/public-repo/issues/18"}
    with mock.patch.object(gh,"_config",return_value={}), \
         mock.patch.object(gh,"_load",return_value=record), \
         mock.patch.object(gh,"_api",side_effect=api), \
         mock.patch.object(gh,"_redis",side_effect=redis), \
         mock.patch.object(gh,"_post_github",side_effect=write):
        proposal=gh._github_command(OWNER,"@GitHub create issue Secure title :: Checked body")
        assert "not executed" in proposal and not calls
        token=proposal.split("@GitHub confirm ",1)[1].split("**",1)[0]
        # A different verified Google owner cannot execute the proposal.
        wrong=gh._github_command("google:intruder","@GitHub confirm "+token)
        assert "mismatch" in wrong and not calls
        assert "already used" in gh._github_command(OWNER,"@GitHub confirm "+token)
        proposal2=gh._github_command(OWNER,"@GitHub create issue Secure title :: Checked body")
        token2=proposal2.split("@GitHub confirm ",1)[1].split("**",1)[0]
        result=gh._github_command(OWNER,"@GitHub confirm "+token2)
        assert "/issues/18" in result and len(calls)==1
        assert calls[0][0].endswith("/issues")
        assert calls[0][1]=={"title":"Secure title","body":"Checked body"}
        assert "already used" in gh._github_command(OWNER,"@GitHub confirm "+token2)


def test_no_silent_approval_or_untrusted_code_execution():
    source=Path(__file__).with_name("github_connection.py").read_text()
    assert "GETDEL" in source and "issue-write" in source and "branch-write" in source
    assert "requests.put(" not in source and "requests.delete(" not in source
    assert "SWRLZ_GITHUB_ENCRYPTION_KEY" in source
    assert "github_connection.command_events(" in Path(__file__).with_name("station.py").read_text()
    assert 'id="githubCheckAccess"' in Path(__file__).parent.parent.joinpath("chat/§wyrlz/index.html").read_text()


if __name__=="__main__":
    test_scopes_and_live_repository_rights()
    test_prompt_routing_requires_anchored_user_command()
    test_read_continues_when_write_scope_absent_and_denial_never_writes()
    test_issue_write_requires_separate_user_confirmation_and_is_one_time()
    test_no_silent_approval_or_untrusted_code_execution()
    print("GitHub v210 scoped permissions and confirmed-write tests passed")
