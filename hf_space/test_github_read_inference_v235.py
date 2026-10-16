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


def test_latest_export_named_file_is_a_verified_read_not_a_404_command():
    scoped={"repo":"kaministrator999-ui/Swrlzing-core","branch":"main",
            "sourceSha":"a"*40,"directory":"write-action-tests","lastFile":""}
    prompt="Can you see the testing.txt file"
    assert read.classify_read(prompt,scoped)=="@GitHub read file testing.txt"
    captured=[]
    def fake_command(data):
        captured.append(data["prompt"])
        yield {"type":"DELTA","text":"## GitHub file: write-action-tests/Testing.txt"}
        yield {"type":"COMPLETED","phase":"COMPLETE"}
    with mock.patch.object(gh,"command_events",side_effect=fake_command):
        events=list(gh.agent_events({"userId":"google:owner","prompt":prompt,
                                     "githubContext":scoped}))
    assert captured==["@GitHub read file testing.txt"],captured
    assert any(e.get("phase")=="GITHUB_READ_EVIDENCE" for e in events)
    assert not any("unavailable (404)" in str(e.get("text","")) for e in events)



def test_export66_verified_root_listing_and_named_file_followups():
    root={"repo":"kaministrator999-ui/Swrlzing-core","branch":"main",
          "sourceSha":"a"*40,"directory":"","lastFile":"","kind":"directory"}
    cases={
        "What files are in the GitHub repo":"@GitHub files",
        "What are the files in the repo":"@GitHub files",
        "What files are in the Github repo?":"@GitHub files",
        "Can you locate the test file in the repo":"@GitHub search test",
        "The test.txt file":"@GitHub read file test.txt",
        "The testing.txt file":"@GitHub read file testing.txt",
    }
    for prompt,command in cases.items():
        assert read.classify_read(prompt,root)==command,(prompt,read.classify_read(prompt,root))
        captured=[]
        def fake_command(payload):
            captured.append(payload["prompt"])
            yield {"type":"DELTA","text":"Verified GitHub read"}
            yield {"type":"COMPLETED","phase":"COMPLETE"}
        # Include the model specialist to prove the read intent wins dispatch.
        with (mock.patch.object(gh,"command_events",side_effect=fake_command),
              mock.patch.object(gh,"_post_github",side_effect=AssertionError("write attempted"))):
            events=list(gh.agent_events({"userId":"google:owner",
                "prompt":prompt,"githubContext":root},
                model_generator=lambda *a,**k: iter(()),
                coder_generator=lambda *a,**k: iter(())))
        assert captured==[command],(prompt,captured)
        assert any(e.get("phase")=="GITHUB_READ_EVIDENCE" for e in events)
    # An unscoped nominal response is not a connected GitHub instruction.
    assert read.classify_read("The testing.txt file") is None
    assert read.classify_read("The testing.txt file",{"repo":root["repo"],
                                 "directory":"","lastFile":"","sourceSha":""}) is None
    for prompt in ("Write code for a GitHub inventory","Rename that file",
                   "Delete testing.txt in the repo","Explain Python paths"):
        assert read.classify_read(prompt,root) is None,prompt
    # Preserve meaningful source-explanation intent, not every query a listing.
    assert read.classify_read("Summarize GitHub repository architecture",root).startswith("@GitHub report")




def test_export67_natural_selection_from_verified_inventory():
    # Most recent Chat export (67): a verified six-file list is already on
    # screen. "The testing one" must read a unique GitHub path, not ask the
    # coder to invent testing directories or create an artifact.
    root = {"repo": "kaministrator999-ui/Swrlzing-core", "branch": "main",
            "sourceSha": "a" * 40, "directory": "", "lastFile": "",
            "kind": "directory"}
    selected = {
        "The testing one": "@GitHub read file testing",
        "The testing.txt": "@GitHub read file testing.txt",
        "The Testing.txt": "@GitHub read file Testing.txt",
        "The test one": "@GitHub read file test",
    }
    for prompt, expected in selected.items():
        assert read.classify_read(prompt, root) == expected, prompt
        commands = []
        def fake_command(data):
            commands.append(data["prompt"])
            yield {"type": "DELTA", "text": "Verified read result"}
            yield {"type": "COMPLETED", "phase": "COMPLETE"}
        with (mock.patch.object(gh, "command_events", side_effect=fake_command),
              mock.patch.object(gh, "_post_github", side_effect=AssertionError("write attempted"))):
            result = list(gh.agent_events({"userId": "google:owner", "prompt": prompt,
                                           "githubContext": root},
                                          model_generator=lambda *a, **k: iter(()),
                                          coder_generator=lambda *a, **k: iter(())))
        assert commands == [expected], (prompt, commands)
        assert any(e.get("phase") == "GITHUB_READ_EVIDENCE" for e in result), prompt

    # Explicit connected context is necessary. General conversation and
    # ambiguous ordinals are not invented as GitHub reads.
    for prompt in ("The testing one", "The testing.txt"):
        assert read.classify_read(prompt) is None
    for prompt in ("The first one", "The other one", "The nice one",
                   "The next one", "The testing one is great",
                   "Rename the testing one", "Delete the testing one"):
        assert read.classify_read(prompt, root) is None, prompt
    file_context = {**root, "kind": "file", "lastFile": "README.md"}
    assert read.classify_read("The testing one", file_context) is None

    # The old source-verified unique filename resolver owns actual selection.
    # An extensionless stem may map to Testing.txt but never to test.txt.
    tree = [{"path": "README.md", "type": "blob", "mode": "100644"},
            {"path": "write-action-tests/Testing.txt", "type": "blob", "mode": "100644"},
            {"path": "write-action-tests/hello-swyrlz.txt", "type": "blob", "mode": "100644"}]
    def fake_api(token, path):
        if "/commits/" in path:
            return {"sha": "a" * 40}
        if "/git/trees/" in path:
            return {"tree": tree, "truncated": False}
        raise AssertionError(path)
    with mock.patch.object(gh, "_api", side_effect=fake_api):
        existing = gh._resolve_repository_file("test-token", root["repo"], "main", "testing")
        missing = gh._resolve_repository_file("test-token", root["repo"], "main", "test")
    assert existing["status"] == "unique", existing
    assert existing["paths"] == ["write-action-tests/Testing.txt"], existing
    assert missing["status"] == "not-found", missing



def test_export68_conversational_filename_followup_is_not_generated_directory():
    # Newest conversation only in owner export (68), using Swrlzing-core as
    # test *target*, not the application source repo. First response was an
    # authenticated GitHub root listing; the reply "Ok so the testing.txt
    # file" incorrectly ran PROGRAMMING_INTENT and invented source paths.
    root = {"repo": "kaministrator999-ui/Swrlzing-core", "branch": "main",
            "sourceSha": "a03a600eab16fc653a3c8b8184e803feccf9b66a",
            "directory": "", "lastFile": "", "kind": "directory"}
    cases = {
        "Ok so the testing.txt file": "@GitHub read file testing.txt",
        "Okay, so the Testing.txt file": "@GitHub read file Testing.txt",
        "So the testing one": "@GitHub read file testing",
        "Ok, the testing.txt": "@GitHub read file testing.txt",
        "The testing.txt file": "@GitHub read file testing.txt",
    }
    for phrase, command in cases.items():
        assert read.classify_read(phrase, root) == command, phrase
        captured = []
        def fake_command(payload):
            captured.append(payload["prompt"])
            yield {"type": "DELTA", "text": "## GitHub file: write-action-tests/Testing.txt"}
            yield {"type": "COMPLETED", "phase": "COMPLETE"}
        with (mock.patch.object(gh, "command_events", side_effect=fake_command),
              mock.patch.object(gh, "_post_github", side_effect=AssertionError("writes forbidden"))):
            events = list(gh.agent_events({"userId": "google:owner", "prompt": phrase,
                                           "githubContext": root},
                                          model_generator=lambda *a, **k: iter(()),
                                          coder_generator=lambda *a, **k: iter(())))
        assert captured == [command], (phrase, captured)
        assert any(e.get("phase") == "GITHUB_READ_EVIDENCE" for e in events), events
    for phrase in ("Ok so the testing.txt file", "Okay, so the Testing.txt file"):
        assert read.classify_read(phrase) is None
        assert read.classify_read(phrase, {**root, "sourceSha": ""}) is None
    for phrase in ("Ok so the testing.txt file is great",
                   "Ok so create the testing.txt file",
                   "Ok so delete the testing.txt file",
                   "Ok so the first one",
                   "Ok so the other one",
                   "Ok so the testing.txt file is under a secret folder"):
        assert read.classify_read(phrase, root) is None, phrase
    # The GitHub provider alone owns actual file presence/contents; no test
    # code writes or substitutes arbitrary paths into the six-file test repo.

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
    with (mock.patch.object(gh, "command_events", side_effect=fake_execute),
          mock.patch.object(gh, "_post_github", side_effect=AssertionError("write forbidden"))):
        events = list(gh.agent_events({"userId": "google:owner", "prompt": prompt}))
    assert captured == ["@GitHub report deep src/main.py"], captured
    assert any(e.get("phase") == "GITHUB_READ_EVIDENCE" for e in events)
    assert any("Verified bounded" in e.get("text", "") for e in events)
    assert gh.GITHUB_CAPABILITY_STAGE == "read-repository"
    with mock.patch.object(gh, "command_events", side_effect=AssertionError("write attempted")):
        assert not list(gh.agent_events({"userId": "google:owner",
                                         "prompt": "Delete src/main.py in our repo"}))
        events = list(gh.agent_events({"userId": "google:owner",
                                       "prompt": "@GitHub create issue something"}))
    assert any(e.get("phase") == "GITHUB_STAGE_LOCKED" for e in events), events


if __name__ == "__main__":
    test_natural_read_tool_selection()
    test_verified_thread_scope_and_general_chatter()
    test_latest_export_named_file_is_a_verified_read_not_a_404_command()
    test_export66_verified_root_listing_and_named_file_followups()
    test_export68_conversational_filename_followup_is_not_generated_directory()
    test_model_education_is_inference_not_unverified_facts()
    test_stage_one_executes_only_read_command()
    print("v235 scoped GitHub source inference and Stage-1 lock tests PASS")
