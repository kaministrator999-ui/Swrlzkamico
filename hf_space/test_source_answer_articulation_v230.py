"""v230 source-answer articulation: exported question semantics and verified prose.

All response examples are non-private templates. Mocked metadata tests ensure
only fetched GitHub facts appear as numeric/commit details in final replies.
"""
from pathlib import Path
import re
import sys
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parent))
import source_answer_articulation_v230 as teach
import github_connection as github
import brain_programming

ROOT=Path(__file__).resolve().parent

def test_example_guidance_is_only_contextual():
    samples={
        "repo-count":"How many files are there in the repo?",
        "repo-status":"Can you tell me where we are at with the chat in the repo?",
        "archive-span":"What's the date span between the start and end date of the chatgpt import",
        "source-report":("Using only the verified GitHub source report below, explain what "
          "the selected components appear to do, how they relate, and their evidence gaps."
          "\n\n# §wyrlz_§tart.md\nKind: Documentation · 916 lines")
    }
    for kind,prompt in samples.items():
        assert teach.lesson_kind(prompt)==kind,(kind,prompt)
        style=teach.articulation_lesson(prompt)
        assert "verified" in style.casefold()
        assert "[SOURCE-ANSWER ARTICULATION LESSON" in style
        assert len(style)<=1850
        assert not brain_programming.programming_intent(prompt,[],[])["codingTask"],prompt
    for ordinary in ("How is today going?", "Write a Python program that counts local files",
                     "Design a §tart project icon", "Hello"):
        assert teach.lesson_kind(ordinary)==""
        assert teach.articulation_lesson(ordinary)==""
    # Generic universal examples must never import an owner's private archive or profile.
    source=ROOT.joinpath("source_answer_articulation_v230.py").read_text()
    assert "Kami" not in source and "4db0b78" not in source and "578 files" not in source

def test_700m_receives_lesson_as_instructions_not_fake_evidence():
    engine=ROOT.joinpath("lfm2_700m_engine.py").read_text()
    assert "from source_answer_articulation_v230 import articulation_lesson" in engine
    assert 'lesson=articulation_lesson(prompt)' in engine
    assert 'if not programming.get("codingTask"):' in engine
    assert 'system+="\\n"+lesson' in engine

def test_natural_repo_counts_are_sha_pinned_and_have_machine_lines():
    sha="a"*40
    def api(token,url):
        assert token=="redacted",url
        if url.endswith("/commits/main"):return {"sha":sha}
        if "git/trees/" in url:
            return {"truncated":False,"tree":[
              {"path":"README.md","type":"blob","size":100},
              {"path":"src","type":"tree"},
              {"path":"src/hello.py","type":"blob","size":50},
              {"path":"docs","type":"tree"},
              {"path":"docs/guide.md","type":"blob","size":75},
            ]}
        raise AssertionError(url)
    with mock.patch.object(github,"_api",side_effect=api):
        reply=github._github_repo_stats({"token":"redacted"},"owner/repo","main")
    assert "**3 files**" in reply and "**2 directories**" in reply,reply
    assert "recursive Git-tree count" in reply
    assert "Files: 3\nDirectories: 2" in reply
    assert sha in reply
    assert "redacted" not in reply
    with mock.patch.object(github,"_api",side_effect=lambda token,url:
       {"sha":sha} if "/commits/" in url else {"truncated":True,"tree":[]}):
        partial=github._github_repo_stats({"token":"redacted"},"owner/repo","main")
    assert "exact totals cannot be verified" in partial and "3 files" not in partial

def test_repo_status_is_evidence_not_deployment_claim():
    sha="a"*40
    def api(token,url):
        if "/commits/runtime" in url:return {"sha":"b"*40}
        if "/commits?sha=" in url:return [{"sha":sha,"commit":{"message":"fix(chat): resolve preview issue"}}]
        if "/commits/main" in url:return {"sha":sha}
        raise AssertionError(url)
    def read(token,repo,path,rev,cap=0):
        if path.startswith("versions/"):return {"body":"VERSION=1.5.116\n"}
        return {"body":"source","sha":"c"*40}
    with mock.patch.object(github,"_api",side_effect=api),mock.patch.object(github,"_read_optional",side_effect=read):
        reply=github._verified_chat_status({"token":"redacted"},"owner/repo","main")
    assert "Where the Chat project stands" in reply
    assert "chat/§wyrlz" in reply and "resolve preview issue" in reply
    assert "**web-chat:** 1.5.116" in reply
    assert "do not, by themselves, confirm" in reply
    assert "works on your phone" in reply
    assert "production is fully verified" not in reply.lower()

def test_real_user_export_does_not_become_example_facts():
    source=teach.articulation_lesson("How many files are there in the repo?")
    assert "[verified number]" in source and "578" not in source
    report=teach.articulation_lesson(
      "Using only the verified GitHub source report below, explain the inspected components.\n\n# §wyrlz §tart")
    assert "UNTRUSTED DATA" in report
    assert "uninspected" in report.lower()
    assert teach.lesson_kind("What's the date span between the start and end date of the chatgpt import")=="archive-span"

if __name__=="__main__":
    test_example_guidance_is_only_contextual()
    test_700m_receives_lesson_as_instructions_not_fake_evidence()
    test_natural_repo_counts_are_sha_pinned_and_have_machine_lines()
    test_repo_status_is_evidence_not_deployment_claim()
    test_real_user_export_does_not_become_example_facts()
    print("v230 source-answer model lesson and grounded prose contracts PASS")
