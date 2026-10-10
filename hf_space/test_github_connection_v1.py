"""Deterministic, offline GitHub link / project startup boundary tests."""
import importlib
import json
import os
import sys
from pathlib import Path
from unittest import mock

from cryptography.fernet import Fernet
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).parent))
import github_connection as gh

def _mock_config(key):
    return dict(client="test-id", secret="test-secret",
                callback="https://example.test/api/github/callback",
                redis="https://example-redis.test", redis_token="opaque",
                fernet=key.decode("ascii"))

def test_prompt_routing():
    for prompt in ("§§", "@GitHub §§", "read the §tart doc and follow through", "Read the §tart document and follow the project startup contract"):
        assert gh.is_start_request(prompt), prompt
    for prompt in ("Hello", "Create a §tart project image", "what is GitHub?", ""):
        assert not gh.is_start_request(prompt), prompt

def test_no_untrusted_repository_paths():
    for path in ("owner/repo", "my-org/my-repo", "a.b/c_d"):
        assert gh._repo_name(path) == path
    for bad in ("", "../repo", "a/../b", "https://github.com/a/b", "a/b/other", "a/.", "a/..", "a/repo?x=1"):
        try:gh._repo_name(bad)
        except HTTPException as exc:assert exc.status_code == 422
        else:raise AssertionError(bad)

def test_account_isolation_encryption_persistence():
    key=Fernet.generate_key()
    config=_mock_config(key)
    records={}
    def redis(_, command, name, *args):
        if command=="SET":
            records[name]=args[0];return "OK"
        if command=="GET":return records.get(name)
        if command=="DEL":records.pop(name,None);return 1
        raise AssertionError(command)
    with mock.patch.object(gh, "_redis", side_effect=redis):
        gh._save(config, "google:alice", {"token":"secret-alice","githubId":11,"login":"alice","repo":"alice/public"})
        gh._save(config, "google:bob", {"token":"secret-bob","githubId":22,"login":"bob","repo":"bob/public"})
        assert "secret-alice" not in str(records) and "secret-bob" not in str(records)
        assert gh._load(config,"google:alice")["login"]=="alice"
        assert gh._load(config,"google:bob")["login"]=="bob"
        assert gh._load(config,"google:unknown") is None
        assert gh._load(config,"google:alice")["repo"]=="alice/public"

def test_oauth_state_cookie_google_binding_and_one_use():
    from starlette.testclient import TestClient
    from fastapi import FastAPI
    app=FastAPI()
    user={"id":"google:alice"}
    gh.install(app, lambda req:(None,user))
    key=Fernet.generate_key()
    c=_mock_config(key)
    seen={}
    def redis(_, command, name, *args):
        if command=="SET":
            seen[name]=args[0];return "OK"
        if command=="GETDEL":
            return seen.pop(name,None)
        raise AssertionError(command)
    with mock.patch.object(gh,"_config",return_value=c), mock.patch.object(gh,"_redis",side_effect=redis):
        client=TestClient(app,base_url="https://example.test")
        resp=client.get("/api/github/start",follow_redirects=False)
        assert resp.status_code==303
        assert "code_challenge_method=S256" in resp.headers["location"]
        cookie=client.cookies.get("swrlz_github_oauth")
        assert cookie and cookie not in resp.headers["location"].split("state=")[0]
        # Callback subject cannot silently switch to another Google account.
        user["id"]="google:bob"
        denied=client.get("/api/github/callback",params={"state":cookie,"code":"anything"},follow_redirects=False)
        assert denied.status_code==403
        user["id"]="google:alice"
        replay=client.get("/api/github/callback",params={"state":cookie,"code":"anything"},follow_redirects=False)
        assert replay.status_code==403

def test_startup_source_evidence_no_write_and_no_fake_activation():
    token="fake-token"
    def fake_api(_, path):
        if path=="/repos/test/repo":return {"default_branch":"main"}
        raise AssertionError(path)
    def optional(_, repo, path, ref, max_bytes=100000):
        if path=="§wyrlz_§tart.md":return {"body":"# §wyrlz §tart\nread canonical docs","sha":"a","path":path}
        if path=="SWRLZ_SERVER_ROADMAP.md":
            return {"body":"## UPDATE FINISHED — 2026-10-09 — test project acceptance\n\nStatus: source complete, live pending\n", "sha":"b","path":path}
        if path=="VERSION.txt":return {"body":"REPOSITORY_WORK=versions/repository-work.txt","sha":"c"}
        if path=="versions/repository-work.txt":return {"body":"VERSION=1.0.1\nSTATUS=active","sha":"d"}
        return None
    with mock.patch.object(gh,"_config",return_value={}),mock.patch.object(gh,"_load",return_value={"token":token,"repo":"test/repo"}),mock.patch.object(gh,"_api",side_effect=fake_api),mock.patch.object(gh,"_read_optional",side_effect=optional):
        # A missing source pin is a HARD failure, not invented version truth.
        try:gh.project_start_report("google:user")
        except AssertionError:pass
        else:raise AssertionError("Expected exact source revision validation")
    source=Path(__file__).with_name("github_connection.py").read_text()
    assert 'GITHUB_SCOPE = "read:user"' in source
    assert "requests.put(" not in source and "requests.patch(" not in source and "requests.delete(" not in source
    assert "SWRLZ_GITHUB_ENCRYPTION_KEY" in source and 'Fernet(' in source
    assert "GETDEL" in source
    assert "Project startup" not in source or "source evidence" in source.lower()

if __name__=="__main__":
    test_prompt_routing()
    test_no_untrusted_repository_paths()
    test_account_isolation_encryption_persistence()
    test_oauth_state_cookie_google_binding_and_one_use()
    test_startup_source_evidence_no_write_and_no_fake_activation()
    print("GitHub account/source boundary tests passed")
