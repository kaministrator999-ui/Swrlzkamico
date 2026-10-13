"""v235 read-intent inference: deterministic source selection and locked writes.

Mock-only tests. No GitHub credentials, live mutations, model weights or user data.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import github_read_inference_v235 as read
import github_connection as gh
import source_answer_articulation_v230 as teach
import brain_programming as brain

SHA = "a" * 40
CTX = {"repo": "owner/repo", "branch": "main", "sourceSha": SHA,
       "directory": "src", "lastFile": "src/main.py", "kind": "file"}


def test_natural_read_tool_selection():
    examples = {
        "Explain what hf_space/github_connection.py does in our repo": "@GitHub report deep hf_space/github_connection.py",
        "How do hf_space/a.py and hf_space/b.py relate in GitHub?": "@GitHub report deep hf_space/a.py | hf_space/b.py",
        "Summarize the architecture of our GitHub repository": "@GitHub report structure /",
        "@GitHub analyze the docs directory": "@GitHub report deep docs",
        "Show me the files in our GitHub repository": "@GitHub files",
        "How many files are in the GitHub repo?": "@GitHub stats",
        "What was changed in src/main.py in our repo?": "@GitHub history src/main.py",
        "Which file implements authorization in our GitHub repository?": "@GitHub report structure /",
    }
    for prompt, expected in examples.items():
        assert read.classify_read(prompt) == expected, (prompt, read.classify_read(prompt))


def test_verified_thread_scope_and_general_chatter():
    examples = {
        "What does that file do?": "@GitHub report deep src/main.py",
        "Explain how it works": "@GitHub report deep src/main.py",
        "When was that file last modified?": "@GitHub history src/main.py",
        "How many files in this folder?": "@GitHub stats src",
        "Show the largest files in that folder": "@GitHub largest 15 src",
    }
    for prompt, expected in examples.items():
        assert read.classify_read(prompt, CTX) == expected, (prompt, read.classify_read(prompt, CTX))
    for prompt in ("What did we do yesterday?", "Write code to delete that file",
                   "Create a PR in our GitHub repo", "Run build on main",
                   "Do you remember my previous chat in the repo?"):
        assert read.classify_read(prompt, CTX) is None, prompt
    assert read.classify_read("What does that file do?") is None
    assert read.classify_read("What's the weather?") is None
    assert read.classify_read("Read README.md") is None
    assert read.classify_read("@GitHub read file README.md") is None


def test_model_education_is_inference_not_unverified_facts():
    for question in ("Explain what hf_space/brain_programming.py does in our repo",
                     "Which files handle source reports in GitHub?",
                     "@GitHub analyze docs/engineering/overview.md"):
        assert teach.lesson_kind(question) == "repo-read", question
        instruction = teach.articulation_lesson(question)
        assert "verified" in instruction.lower()
        assert "not external facts" in instruction.lower()
        assert len(instruction) <= 1850
        assert not brain.programming_intent(question, [], [])["codingTask"], question
    assert teach.lesson_kind("Write code to modify a GitHub file") == ""
    assert brain.programming_intent("Write Python code to enumerate repo files", [], [])["codingTask"]


def test_stage_one_executes_only_read_command():
    prompt = "Explain what src/main.py does in our GitHub repo"
    captured = []
    def fake_execute(data):
        captured.append(data["prompt"])
        yield {"type": "DELTA", "text": "Verified bounded read receipt"}
        yield {"type": "COMPLETED"}
    with mock.patch.object(gh, "command_events", side_effect=fake_execute), \\
         mock.patch.object(gh, "_post_github", side_effect=AssertionError("write forbidden")):
        events = list(gh.agent_events({"userId": "google:owner", "prompt": prompt}))
    assert captured == ["@GitHub report deep src/main.py"], captured
    assert any(e.get("phase") == "GITHUB_READ_EVIDENCE" for e in events)
    assert any("Verified bounded" in e.get("text", "") for e in events)
    assert gh.GITHUB_CAPABILITY_STAGE == "read-repository"
    for prompt in ("Delete src/main.py in our repo", "@GitHub create issue something"):
        with mock.patch.object(gh, "command_events", side_effect=AssertionError("write attempted")):
            events = list(gh.agent_events({"userId": "google:owner", "prompt": prompt}))
        assert any(e.get("phase") == "GITHUB_STAGE_LOCKED" for e in events), events


if __name__ == "__main__":
    test_natural_read_tool_selection()
    test_verified_thread_scope_and_general_chatter()
    test_model_education_is_inference_not_unverified_facts()
    test_stage_one_executes_only_read_command()
    print("v235 scoped GitHub source inference and Stage-1 lock tests PASS")
