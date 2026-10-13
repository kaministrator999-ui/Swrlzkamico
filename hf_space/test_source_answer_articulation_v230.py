"""v230 source-answer articulation: exported question semantics and verified prose.

All response examples are non-private templates. Mocked metadata tests ensure
only fetched GitHub facts appear as numeric/commit details in final replies.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast
import re
import sys
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parent))
import source_answer_articulation_v230 as teach
import github_connection as github
import brain_programming
import private_account_facts_v208 as facts

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

def test_v231_actual_response_mode_is_source_explanation_not_code():
    # Extract only the actual 700M pure function, without importing GPU or
    # heavyweight HF runtime dependencies into the source-validation CI.
    engine=ROOT.joinpath("lfm2_700m_engine.py").read_text()
    assert "import articulation_lesson, lesson_kind" in engine
    ast_tree=ast.parse(engine)
    fn=next(x for x in ast_tree.body if isinstance(x,ast.FunctionDef) and x.name=="_response_mode")
    namespace={"re":re,"lesson_kind":teach.lesson_kind}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),"lfm2_700m_engine.py","exec"),namespace)
    mode=namespace["_response_mode"]
    prompts=(
        "How many files are there in the repo?",
        "Can you tell me where we are at with the chat in the repo?",
        "What's the date span between the start and end date of the chatgpt import",
        ("Using only the verified GitHub source report below, explain what the "
         "selected file does.\\n\\n# §wyrlz §tart\\n"
         "Kind: Documentation. 916 lines. Important functions."),
    )
    for prompt in prompts:
        programming=brain_programming.programming_intent(prompt,[],[])
        assert not programming["codingTask"],prompt
        result=mode(prompt,programming)
        assert result.startswith("RESPONSE MODE: SOURCE-FACTS-FIRST"),(prompt,result)
        assert "never emit unsolicited code" in result
    code=mode("Write a Python function to count files",{"codingTask":True})
    assert code.startswith("RESPONSE MODE: CODE-")
    assert 'mode.startswith("RESPONSE MODE: SOURCE-FACTS-FIRST")' in engine


def test_v231_imported_archive_date_is_calendar_span():
    first=datetime(2024,5,8,23,tzinfo=timezone.utc).timestamp()
    last=datetime(2024,5,10,1,tzinfo=timezone.utc).timestamp()
    prompt="What's the date span between the start and end date of the ChatGPT import?"
    assert facts.classify(prompt)=="imported-date-span"
    with mock.patch.object(facts.archive,"_owner"),mock.patch.object(
        facts.account_chat_store,"_config",return_value={}),mock.patch.object(
        facts.gh,"_redis",return_value=2),mock.patch.object(
        facts,"_count_status",return_value={
          "state":"ready","total":2,"stamped":70,"earliest":first,"latest":last
        }):
        answer=facts.answer("google:fixture",[],prompt)
    assert "2024-05-08" in answer and "2024-05-10" in answer
    assert "**2 calendar days**" in answer,answer
    assert "ZIP upload/import job" in answer
    assert "4db0b78" not in answer


def test_v232_same_thread_source_report_followup_and_coding_boundary():
    evidence=(
      "Using only the verified GitHub source report below, explain what the selected "
      "components appear to do.\n\n# GitHub source analysis · example/repo\n"
      "Branch: main · commit " + "a"*40 + "\n"
      "Scopes: docs/guide.md\nDepth: structure\n"
      "Complete Git-tree inventory: 1 unique files\n"
      "Content inspected: 1/1\nReviewed source files: docs/guide.md"
    )
    history=[
      {"role":"user","text":evidence},
      {"role":"assistant","text":"The inspected Markdown describes the project setup."},
    ]
    prompts=(
      "What does that file do?",
      "How do they relate?",
      "Can you explain it further?",
      "Which function handles the setup?",
    )
    engine=ROOT.joinpath("lfm2_700m_engine.py").read_text()
    fn=next(x for x in ast.parse(engine).body
            if isinstance(x,ast.FunctionDef) and x.name=="_response_mode")
    scope={"re":re,"lesson_kind":teach.lesson_kind}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),"lfm2_700m_engine.py","exec"),scope)
    mode=scope["_response_mode"]
    prior={"intentContract":{"originalRequest":"Create a Python source code artifact"}}
    for question in prompts:
        assert teach.lesson_kind(question,history)=="source-report-followup",question
        assert "SAME verified report" in teach.articulation_lesson(question,history)
        intent=brain_programming.programming_intent(question,history,[],prior)
        assert not intent["codingTask"],question
        assert mode(question,intent,history).startswith("RESPONSE MODE: SOURCE-FACTS-FIRST")
    assert teach.lesson_kind("What's the weather?",history)==""
    assert teach.lesson_kind("Write Python code to modify that file",history)==""
    assert brain_programming.programming_intent("Write Python code to modify that file",history,[],prior)["codingTask"]
    assert mode("Write Python code to modify that file",{"codingTask":True},history).startswith("RESPONSE MODE: CODE-")
    assert teach.lesson_kind("What does that file do?",[])==""
    older=history+[{"role":"user","text":"Another question"},{"role":"assistant","text":"Answer"},
                   {"role":"user","text":"One more"},{"role":"assistant","text":"Answer"},
                   {"role":"user","text":"Third unrelated topic"}]
    assert teach.lesson_kind("What does that file do?",older)==""


if __name__=="__main__":
    test_example_guidance_is_only_contextual()
    test_700m_receives_lesson_as_instructions_not_fake_evidence()
    test_natural_repo_counts_are_sha_pinned_and_have_machine_lines()
    test_repo_status_is_evidence_not_deployment_claim()
    test_real_user_export_does_not_become_example_facts()
    test_v231_actual_response_mode_is_source_explanation_not_code()
    test_v231_imported_archive_date_is_calendar_span()
    test_v232_same_thread_source_report_followup_and_coding_boundary()
    print("v232 source-report followup, noncoding response mode and archive calendar-date contracts PASS")
