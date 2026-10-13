"""v230: question-first articulation, checked against owner-export phrasing.

This tests source-aware instruction selection and actual deterministic GitHub
and archive answers; a passing test is not evidence of model weights learning.
"""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timezone
from unittest import mock
import ast
import re
sys.path.insert(0,str(Path(__file__).resolve().parent))

import brain_programming as bp
import response_articulation_v230 as art
import github_connection as gh
import private_account_facts_v208 as facts
# The test runner deliberately avoids loading GPU/Hugging Face runtime dependencies.
# Extract the actual lightweight response-mode function from the engine source,
# so we still exercise its real body and verify its import wiring.
engine_source=Path(__file__).with_name("lfm2_700m_engine.py").read_text()
assert "from response_articulation_v230 import response_mode as _verified_fact_mode" in engine_source
tree=ast.parse(engine_source)
response_fn=next(node for node in tree.body
                 if isinstance(node,ast.FunctionDef) and node.name=="_response_mode")
namespace={"re":re,"_verified_fact_mode":art.response_mode}
exec(compile(ast.Module(body=[response_fn],type_ignores=[]),"lfm2_700m_engine.py","exec"),namespace)
_response_mode=namespace["_response_mode"]

SHA="a"*40
BLOB="b"*40

PROMPTS={
    "repo-chat-status":"Can you tell me where we are at with the chat in the repo?",
    "repo-count":"How many files are there in the repo?",
    "report-explanation":(
        "Using only the verified GitHub source report below, explain what the "
        "selected components appear to do.\n\n"
        "# GitHub source analysis\nScopes: §wyrlz_§tart.md\n"
        "Depth: structure\nContent inspected: 1/1"
    ),
    "import-date-span":"What's the date span between the start and end date of the chatgpt import",
}

def test_instructions_are_relevant_and_not_hardcoded_user_facts():
    for kind,prompt in PROMPTS.items():
        assert art.intent(prompt)==kind,(kind,prompt)
        hint=art.style_hint(prompt)
        assert "EVIDENCE-FIRST ARTICULATION" in hint
        assert "never" in hint.lower()
        assert "kaministrator999" not in hint
        assert "1.5.116" not in hint and "2026-10-13" not in hint
        assert _response_mode(prompt,bp.programming_intent(prompt,[],[])).startswith(
            "RESPONSE MODE: VERIFIED-FACT-EXPLANATION"),kind
        assert not bp.programming_intent(prompt,[],[])["codingTask"],kind
    for unrelated in ("Write a Python function", "What is my name?", "Hi!", "Make a song"):
        assert not art.style_hint(unrelated),unrelated
    assert art.intent("How many files are in my repo?")=="repo-count"
    assert art.intent("@github how many files are in the repo")=="repo-count"
    assert not gh.is_start_request(PROMPTS["report-explanation"])
    assert "Only X of Y" in art.style_hint(PROMPTS["report-explanation"])

def test_counts_answer_directly_from_complete_tree_only():
    calls=[]
    def api(token,path):
        calls.append(path)
        if "/commits/main" in path:return {"sha":SHA}
        if "/git/trees/" in path:return {"truncated":False,"tree":[
            {"type":"tree","path":"chat"},
            {"type":"tree","path":"docs"},
            {"type":"blob","path":"chat/app.py","size":25},
            {"type":"blob","path":"docs/info.md","size":12},
            {"type":"blob","path":"README.md","size":5},
        ]}
        raise AssertionError(path)
    with mock.patch.object(gh,"_api",side_effect=api):
        reply=gh._github_repo_stats({"token":"private-token"},"owner/repo","main")
    assert reply.startswith("## GitHub repository statistics")
    assert "**3 tracked files**" in reply and "**2 directories**" in reply
    assert "complete verified Git-tree" in reply
    assert "not a local directory listing" in reply
    assert SHA[:12] in reply and "private-token" not in reply
    with mock.patch.object(gh,"_api",side_effect=lambda token,path:(
        {"sha":SHA} if "/commits/" in path else {"truncated":True,"tree":[]}
    )):
        limited=gh._github_repo_stats({"token":"private-token"},"owner/repo","main")
    assert "exact totals cannot be verified" in limited
    assert "**0 tracked files**" not in limited

def test_status_frontloads_meaning_and_does_not_claim_mobile_acceptance():
    def api(token,path):
        if "/commits/runtime" in path:return {"sha":"c"*40}
        if "/commits?sha=" in path:return [{"sha":SHA,"commit":{"message":"fix(chat): remember read-only scope"}}]
        if "/commits/main" in path:return {"sha":SHA}
        raise AssertionError(path)
    def source(token,repo,path,ref,limit):
        if path.startswith("versions/"):return {"body":"ID=web-chat\nVERSION=1.9.9\n"}
        return {"sha":BLOB,"body":"source"}
    with mock.patch.object(gh,"_api",side_effect=api),mock.patch.object(gh,"_read_optional",side_effect=source):
        reply=gh._verified_chat_status({"token":"secret"},"owner/repo","main")
    assert reply.startswith("## Chat project")
    assert "I checked the Chat project" in reply
    assert "main Chat page is present" in reply
    assert "Web Chat version is **1.9.9**" in reply
    assert "**What remains to check:**" in reply
    assert "signed-in Android session" in reply
    assert "secret" not in reply
    assert reply.index("I checked the Chat project") < reply.index("Recent Chat-path commits")

def test_date_span_uses_calendar_dates_not_git_identifiers():
    prompt=PROMPTS["import-date-span"]
    assert facts.classify(prompt)=="imported-date-span"
    first=datetime(2024,5,8,22,tzinfo=timezone.utc).timestamp()
    last=datetime(2024,5,10,1,tzinfo=timezone.utc).timestamp()
    with mock.patch.object(facts.account_chat_store,"_config",return_value={}),\
         mock.patch.object(facts.archive,"_owner"),\
         mock.patch.object(facts.gh,"_redis",return_value=3),\
         mock.patch.object(facts,"_count_status",return_value={
             "state":"ready","total":3,"stamped":22,"earliest":first,"latest":last
         }):
        reply=facts.answer("google:fake",[],prompt)
    assert "2024-05-08" in reply and "2024-05-10" in reply
    assert "**2-day**" in reply,reply
    assert "message" in reply and "ZIP" in reply
    assert "4db0b78" not in reply

if __name__=="__main__":
    test_instructions_are_relevant_and_not_hardcoded_user_facts()
    test_counts_answer_directly_from_complete_tree_only()
    test_status_frontloads_meaning_and_does_not_claim_mobile_acceptance()
    test_date_span_uses_calendar_dates_not_git_identifiers()
    print("v230 source-grounded Chat answer articulation checks PASS")
