"""v289 repository readiness: exact tree classification and owner-read routing."""
import pathlib
import sys
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import github_repo_readiness_v289 as mature
import github_connection as gh
import github_read_inference_v235 as inference

SHA = "a"*40


def snap(files, complete=True):
    paths = [{"path": p, "type": "file", "sha": "b"*40, "sizeBytes": 100} for p in files]
    return {"repository": "example/repo", "sourceSha": SHA, "branch": "main",
            "complete": complete, "items": paths}


def fail(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected rejected repo state")


def test_exact_categories_and_uncertainty():
    cases = [
        ([], "empty"),
        (["README.md"], "onboarding-only"),
        (["README.md", "project.zip"], "archive-or-fixtures-only"),
        (["write-action-tests/hello.txt"], "test-data-only"),
        (["README.md", "docs/guide.md"], "documentation-or-data"),
        (["src/service.py"], "source-project"),
        (["src/app.py", "tests/test_app.py"], "source-with-fixtures"),
        (["src/app.py", "docs/SCENARIO_MATRIX.md", "write-lab/README.md"],
         "mixed-source-testbed")
    ]
    for files, kind in cases:
        result = mature.classify(snap(files))
        assert result["category"] == kind, (files, result)
        assert result["capabilities"]["archiveContentsRead"] is False
        assert result["capabilities"]["writesAuthorizedByThisCheck"] is False
        assert "not a permissions" in mature.one_line(result)
        assert "No archive extraction" in mature.report(result)
    fail(lambda: mature.classify(snap([], False)))
    fail(lambda: mature.classify({**snap([]), "sourceSha": "model-generated"}))


def test_natural_routing_and_stage_gates():
    for ask in ("Is our GitHub repo empty?", "How ready is our GitHub repository?",
                "Is my repo ready for testing?"):
        assert inference.classify_read(ask) == "@GitHub readiness", ask
    assert inference.classify_read("What is GitHub?") is None
    assert inference.classify_read("Delete my GitHub repo") is None
    assert gh._read_stage_command("@GitHub readiness")
    assert not gh._read_stage_command("@GitHub delete everything")
    assert gh.is_github_command("@GitHub readiness")


def test_real_connection_command_and_explorer():
    calls = []
    entries = snap(["README.md", "src/app.py", "tests/test_app.py"])
    def fake_api(token, endpoint):
        assert token == "test-only"
        calls.append(endpoint)
        if endpoint == "/repos/example/repo/commits/main":
            return {"sha": SHA}
        if endpoint == "/repos/example/repo/git/trees/"+SHA+"?recursive=1":
            return {"sha": SHA, "tree": [
                {"path": x["path"], "type": "blob",
                 "sha": x["sha"], "size": x["sizeBytes"]} for x in entries["items"]
            ], "truncated": False}
        if endpoint == "/repos/example/repo/contents?ref=main":
            return [{"type": "file", "path": "README.md"},
                    {"type": "dir", "path": "src"},
                    {"type": "dir", "path": "tests"}]
        raise AssertionError("Unexpected endpoint: " + endpoint)

    with mock.patch.object(gh, "_config", return_value={}), \
         mock.patch.object(gh, "_load", return_value={"token": "test-only", "repo": "example/repo"}), \
         mock.patch.object(gh, "_effective_access", return_value={
             "allowed": True, "defaultBranch": "main", "tokenAccess": "read"}), \
         mock.patch.object(gh, "_api", side_effect=fake_api):
        report = gh._github_command("google:owner", "@GitHub readiness")
        assert "source-with-fixtures" in report and "example/repo" in report, report
        listing = gh._github_command("google:owner", "@GitHub files")
        assert listing.startswith("## GitHub directory: /\n"), listing
        assert "- dir src" in listing
        assert "Repository readiness: source-with-fixtures" in listing
    assert calls
    assert all("/git/refs" not in x and "/issues" not in x for x in calls)


if __name__ == "__main__":
    test_exact_categories_and_uncertainty()
    test_natural_routing_and_stage_gates()
    test_real_connection_command_and_explorer()
    print("v289 repo readiness: categories, user prompts, root explorer, read-only gates PASS")
