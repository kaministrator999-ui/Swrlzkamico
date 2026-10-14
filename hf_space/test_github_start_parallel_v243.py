"""v243: bounded, deterministic, account-safe GitHub startup read tests."""
import sys
import time
import threading
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).parent))
import github_connection as gh

USER = "google:startup-test"
REPO = "example/project"
SOURCE = "a" * 40
RUNTIME = "b" * 40

def fake_api(_token, path):
    if path == "/repos/" + REPO:
        return {"default_branch": "main", "full_name": REPO}
    if path == "/repos/" + REPO + "/commits/main":
        return {"sha": SOURCE}
    if path == "/repos/" + REPO + "/commits/runtime":
        return {"sha": RUNTIME}
    raise AssertionError("Unexpected network request: " + path)

def test_parallel_reads_and_ordered_evidence():
    active = 0
    peak = 0
    lock = threading.Lock()
    calls = []
    def fake_read(token, repo, path, ref, max_bytes=100000):
        nonlocal active, peak
        assert token == "test-token" and repo == REPO
        assert ref == (RUNTIME if path == "VERSION.txt" or path.startswith("versions/") else SOURCE)
        with lock:
            active += 1
            peak = max(peak, active)
            calls.append((path, ref, max_bytes))
        try:
            if path in gh._ROOT_FILES:
                time.sleep(0.025)
                if path == "SWRLZ_SERVER_ROADMAP.md":
                    return {"body": "## UPDATE FINISHED — 2026-10-14 — v242 source verified\n**Result:** STAGED VERIFIED.", "sha": "c"}
                return {"body": "# " + path, "sha": "c"}
            if path == "VERSION.txt":
                return {"body": "REPOSITORY_WORK=versions/repository-work.txt\nGOOGLE_ACCOUNT=versions/google-account.txt", "sha": "d"}
            if path == "versions/repository-work.txt":
                time.sleep(0.02)
                return {"body": "VERSION=1.0.183\nSTATUS=active", "sha": "e"}
            if path == "versions/google-account.txt":
                time.sleep(0.01)
                return {"body": "VERSION=1.0.15\nSTATUS=active", "sha": "f"}
            return None
        finally:
            with lock:
                active -= 1
    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load", return_value={"token": "test-token", "repo": REPO}), \
         mock.patch.object(gh, "_api", side_effect=fake_api), \
         mock.patch.object(gh, "_read_optional", side_effect=fake_read):
        report, context = gh.project_start_report(USER, include_context=True)
    assert peak >= 2, "Startup must issue independent source reads concurrently"
    assert context["docsRead"] == gh._ROOT_FILES, "Source startup order must remain canonical"
    assert context["sourceSha"] == SOURCE and context["runtimeSha"] == RUNTIME
    assert context["modules"] == [
        ("REPOSITORY_WORK", "1.0.183", "active"),
        ("GOOGLE_ACCOUNT", "1.0.15", "active")]
    assert context["startupTimingMs"]["documentReads"] >= 0
    assert context["startupTimingMs"]["total"] >= context["startupTimingMs"]["documentReads"]
    assert len([x for x in calls if x[0] in gh._ROOT_FILES]) == len(gh._ROOT_FILES)
    assert any(x[0] == "SWRLZ_SERVER_ROADMAP.md" and x[2] == 1800000 for x in calls)
    assert "No deployment" in report and "Staged Verified" not in report

def test_backend_failure_does_not_claim_verified_startup():
    def fake_read(_, __, path, ref, max_bytes=100000):
        if path == "SWRLZ_HOTFIX_RULES.md":
            raise RuntimeError("simulated network failure")
        return {"body": "# mock", "sha": "f"}
    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load", return_value={"token": "test-token", "repo": REPO}), \
         mock.patch.object(gh, "_api", side_effect=fake_api), \
         mock.patch.object(gh, "_read_optional", side_effect=fake_read):
        events = list(gh.start_events({"userId": USER}))
    assert not any(e.get("type") == "PROJECT_CONTEXT" for e in events)
    assert "retrieval failed" in " ".join(e.get("text", "") for e in events).lower()
    assert events[-1]["type"] == "COMPLETED"

if __name__ == "__main__":
    test_parallel_reads_and_ordered_evidence()
    test_backend_failure_does_not_claim_verified_startup()
    print("v243 GitHub startup parallel-read boundary checks passed")
