"""v244 regression: informative GitHub Stage 1 help without enabling writes."""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import github_connection as gh

USER = "google:read-only"
REPO = "example/project"
SOURCE = "a" * 40
RUNTIME = "b" * 40

def _api(_token, path):
    if path == "/repos/" + REPO:
        return {"default_branch": "main"}
    if path == "/repos/" + REPO + "/commits/main":
        return {"sha": SOURCE}
    if path == "/repos/" + REPO + "/commits/runtime":
        return {"sha": RUNTIME}
    raise AssertionError("Unexpected API call: " + path)

def test_informational_engine_help_is_read_only():
    for prompt, expected in (
        ("@GitHub engine help", "§E engine guide"),
        ("@GitHub engine pack help", "§E atomic starter-pack guide"),
    ):
        assert gh._read_stage_command(prompt)
        with mock.patch.object(gh, "_config", return_value={}), \
             mock.patch.object(gh, "_load", return_value={"token": "test-token", "repo": REPO}), \
             mock.patch.object(gh, "_api", side_effect=AssertionError("Help should not access network")), \
             mock.patch.object(gh, "_redis", side_effect=AssertionError("Help should not mutate")):
            events = list(gh.agent_events({"userId": USER, "prompt": prompt}))
        answer = "".join(e.get("text", "") for e in events if e.get("type") == "DELTA")
        assert expected in answer, (prompt, answer)
        assert "Stage 1" in answer and "not enabled" in answer
        assert not any(e.get("phase") == "GITHUB_STAGE_LOCKED" for e in events)
        assert events[-1]["type"] == "COMPLETED"
    assert gh.GITHUB_CAPABILITY_STAGE == "read-repository"
    assert gh.GITHUB_SCOPE == "read:user"

def test_mutating_engine_commands_stay_locked():
    for prompt in (
        "@GitHub engine clone sheep-tag-meadow as my-scene on feature/test",
        "@GitHub engine review feature/test",
        "@GitHub engine pack sheep-tag-meadow as my-scene on feature/test",
        "@GitHub engine pack verify my-scene on feature/test",
        "@GitHub confirm abcdef12345",
        "@GitHub engine status",
    ):
        assert gh._stage_blocks(prompt), prompt
    assert not gh._stage_blocks("@GitHub engine help")
    assert not gh._stage_blocks("@GitHub engine pack help")

def test_report_documents_use_same_immutable_commit():
    def read(_token, repo, path, ref, max_bytes=100000):
        assert repo == REPO
        assert ref == (RUNTIME if path == "VERSION.txt" or path.startswith("versions/") else SOURCE)
        if path == "VERSION.txt":
            return {"body": "REPOSITORY_WORK=versions/repository-work.txt", "sha": "c"}
        if path == "versions/repository-work.txt":
            return {"body": "VERSION=1.0.184\\nSTATUS=active", "sha": "d"}
        return {"body": "# " + path, "sha": "e"}
    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load", return_value={"token": "test-token", "repo": REPO}), \
         mock.patch.object(gh, "_api", side_effect=_api), \
         mock.patch.object(gh, "_read_optional", side_effect=read):
        report = gh.project_start_report(USER)
    assert "/blob/" + SOURCE + "/SWRLZ_HOTFIX_RULES.md" in report
    assert "/blob/" + SOURCE + "/%C2%A7wyrlz_%C2%A7tart.md" in report
    assert "/blob/main/" not in report
    assert "1.0.184" in report

if __name__ == "__main__":
    test_informational_engine_help_is_read_only()
    test_mutating_engine_commands_stay_locked()
    test_report_documents_use_same_immutable_commit()
    print("v244 Stage-1 help and pinned-link regressions passed")
