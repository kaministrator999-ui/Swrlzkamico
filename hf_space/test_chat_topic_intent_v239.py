"""v239: topic-only messages clarify; explicit reads remain safe; writes locked.

These tests are a sanitized replay of the owner's real "Files" 404 follow-up.
No account keys or network access.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import github_connection as gh

CTX = {"repo": "owner/demo", "branch": "fix/example", "sourceSha": "a" * 40,
       "directory": "hf_space", "lastFile": "hf_space/github_connection.py",
       "kind": "file"}


def test_short_subjects_ask_instead_of_guessing():
    for subject in ("Files", "file?", "Folders", "Directories", "Statistics", "Stats"):
        answer = gh.ambiguous_topic_reply(subject, CTX)
        assert answer is not None and "Did you want" in answer, subject
        assert "hf_space" in answer and "fix/example" in answer
        assert gh._implicit_repo_command(subject, CTX) is None
    assert gh.ambiguous_topic_reply("Files", None) is None
    assert gh.ambiguous_topic_reply("Files", {**CTX, "sourceSha": "fake"}) is None
    assert gh.ambiguous_topic_reply("Music", CTX) is None
    assert gh.ambiguous_topic_reply("Please list files", CTX) is None
    assert gh.ambiguous_topic_reply("@GitHub files", CTX) is None


def test_no_hidden_io_for_ambiguous_topic():
    with mock.patch.object(gh, "command_events", side_effect=AssertionError("Tool must not execute")):
        rows = list(gh.agent_events({"prompt": "Files", "githubContext": CTX,
                                     "userId": "google:owner"}))
    assert [x["type"] for x in rows] == ["STATUS", "DELTA", "COMPLETED"]
    assert rows[0]["phase"] == "GITHUB_CONTEXT_CLARIFICATION"
    assert "Did you want" in rows[1]["text"]
    assert not any(x["type"] == "GITHUB_CONTEXT" for x in rows)


def test_explicit_read_still_works_and_branch_is_kept():
    assert gh._read_stage_command("@GitHub files hf_space on branch fix/example")
    assert gh._implicit_repo_command("List files in this folder", CTX) == (
        "@GitHub files hf_space on branch fix/example")
    assert gh._implicit_repo_command("When was that original file last modified?", CTX) == (
        "@GitHub history hf_space/github_connection.py on branch fix/example")
    with mock.patch.object(gh, "command_events",
                           return_value=iter(({"type": "DELTA", "text": "source"}, {"type": "COMPLETED"}))) as send:
        list(gh.agent_events({"prompt": "@GitHub files hf_space on branch fix/example",
                              "githubContext": CTX, "userId": "google:owner"}))
    assert send.call_count == 1


def test_write_permissions_cannot_be_inferred_from_context():
    for prompt in ("@GitHub create branch new from main",
                   "@GitHub edit file hf_space/github_connection.py",
                   "@GitHub confirm abcdefgh"):
        assert not gh._read_stage_command(prompt), prompt
        assert gh._stage_blocks(prompt), prompt
    assert gh._implicit_repo_command("Write that file", CTX) is None
    assert gh.ambiguous_topic_reply("Write that file", CTX) is None
    src = (Path(__file__).parent / "station.py").read_text()
    assert "github_connection.ambiguous_topic_reply(prompt,active_github)" in src


if __name__ == "__main__":
    test_short_subjects_ask_instead_of_guessing()
    test_no_hidden_io_for_ambiguous_topic()
    test_explicit_read_still_works_and_branch_is_kept()
    test_write_permissions_cannot_be_inferred_from_context()
    print("v239 ambiguous-topic / explicit read / strict write regressions PASS")
