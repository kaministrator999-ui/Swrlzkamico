"""v229: exported Android conversation regression; no Google secrets or network."""
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parent))
import github_connection as gh
import brain_programming as bp
import private_account_facts_v208 as facts

SHA="a"*40

def test_source_report_does_not_trigger_startup():
    report=("Using only the verified GitHub source report below, explain what the "
            "selected components appear to do.\n\n"
            "# §wyrlz §tart READ THIS FIRST\n\nKind: Documentation · 916 lines")
    assert not gh.is_start_request(report)
    assert gh.is_start_request("Can you read and follow through the §tart doc for me in the @github repo")
    assert gh.is_start_request("read the §tart doc and follow through")
    assert not gh.is_start_request("I read a §tart report yesterday and wanted to discuss it")
    assert not gh.is_start_request("Create a §tart project image")
    assert not bp.programming_intent(report,[],[])["codingTask"]

def test_repo_followup_is_not_memory_or_coding():
    ctx={"repo":"owner/repo","branch":"main","sourceSha":SHA,
         "directory":"","lastFile":"","kind":"directory"}
    ask="Can you tell me where we are at with the chat in the repo?"
    assert gh.is_repo_chat_status_request(ask)
    assert gh.is_github_conversation(ask)
    assert gh._implicit_repo_command(ask,ctx)=="@GitHub chat status"
    assert gh._implicit_repo_command("How many files are there in the repo",ctx)=="@GitHub stats"
    assert gh._implicit_repo_command("How many files are in the repo",ctx)=="@GitHub stats"
    for prompt in (ask,"How many files are there in the repo",
                   "@github how many files are in the repo"):
        assert not bp.programming_intent(prompt,[],[],{"intentContract":{"originalRequest":"write a program"}})["codingTask"], prompt
    assert gh.is_github_command("@github how many files are in the repo")
    assert gh._read_stage_command("@GitHub chat status")
    assert not gh.is_repo_chat_status_request("Do you remember our previous chat in the repository?")
    assert gh._implicit_repo_command("Delete files in the repo",ctx) is None

def test_status_uses_account_pinned_repository_sources():
    paths=[]
    def api(token,url):
        paths.append(url)
        if "/commits/runtime" in url:return {"sha":"b"*40}
        if "/commits?sha=" in url:
            return [{"sha":SHA,"commit":{"message":"fix(chat): correct report routing"}}]
        if "/commits/main" in url:return {"sha":SHA}
        raise AssertionError("Unexpected GitHub API "+url)
    def read(token,repo,path,rev,limit=0):
        assert repo=="owner/repo" and rev in (SHA,"b"*40)
        if path.startswith("versions/"):
            return {"body":"ID="+path+"\nVERSION=1.2.3\n"}
        return {"body":"source","sha":"c"*40}
    rec={"token":"private-token"}
    with mock.patch.object(gh,"_api",side_effect=api), mock.patch.object(gh,"_read_optional",side_effect=read):
        result=gh._verified_chat_status(rec,"owner/repo","main")
    assert "verified source" in result and SHA[:12] in result
    assert "**web-chat:** 1.2.3" in result
    assert "do not, by themselves, confirm" in result
    assert any("chat%2F%C2%A7wyrlz" in x for x in paths)
    assert "private-token" not in result

def test_import_span_uses_message_timestamps_not_hashes():
    prompt="What's the date span between the start and end date of the chatgpt import"
    assert facts.classify(prompt)=="imported-date-span"
    owner="google:owner"
    first=datetime(2024,5,8,tzinfo=timezone.utc).timestamp()
    last=datetime(2026,9,16,tzinfo=timezone.utc).timestamp()
    with mock.patch.object(facts.account_chat_store,"_config",return_value={}),mock.patch.object(
        facts.archive,"_owner"),mock.patch.object(facts.gh,"_redis",return_value=2),mock.patch.object(facts,"_count_status",return_value={
        "state":"ready","total":2,"stamped":200,"earliest":first,"latest":last
    }):
        actual=facts.answer(owner,[],prompt)
    assert "2024-05-08" in actual and "2026-09-16" in actual
    assert "ZIP upload/import job" in actual
    assert "4db0b78" not in actual
    with mock.patch.object(facts.account_chat_store,"_config",return_value={}),mock.patch.object(
        facts.archive,"_owner"),mock.patch.object(facts.gh,"_redis",return_value=2),mock.patch.object(facts,"_count_status",return_value={
        "state":"counting","total":2,"done":1
    }):
        waiting=facts.answer(owner,[],prompt)
    assert "Git commit hashes" in waiting

def test_export_prompts_route_read_only():
    assert gh._read_stage_command("@GitHub stats")
    assert not gh._read_stage_command("@GitHub create branch should-never-run from main")
    assert gh.is_repo_chat_status_request("What's the status of our chat in the GitHub repo?")
    assert not gh.is_repo_chat_status_request("What did we talk about in a previous chat in the repo?")
    assert bp.programming_intent("Please write Python code to count repo files",[],[])["codingTask"]

if __name__=="__main__":
    test_source_report_does_not_trigger_startup()
    test_repo_followup_is_not_memory_or_coding()
    test_status_uses_account_pinned_repository_sources()
    test_import_span_uses_message_timestamps_not_hashes()
    test_export_prompts_route_read_only()
    print("v229 GitHub conversation and imported date-source regression PASS")
