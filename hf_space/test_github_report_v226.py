"""v226: verified GitHub scopes, bounded source reporting, no write authority."""
import json
import sys
from pathlib import Path
from unittest import mock

from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).parent))
import github_explorer_v223 as explorer
import github_report_v226 as report
import github_connection as gh

REPO = "example/reports"
SHA = "a" * 40
ROOT = [
    {"path": "README.md", "type": "file", "sha": "1"*40, "sizeBytes": 52},
    {"path": "src", "type": "dir", "sha": "2"*40, "sizeBytes": None},
    {"path": "src/main.py", "type": "file", "sha": "3"*40, "sizeBytes": 80},
    {"path": "src/helper.py", "type": "file", "sha": "4"*40, "sizeBytes": 80},
    {"path": "docs", "type": "dir", "sha": "5"*40, "sizeBytes": None},
    {"path": "docs/overview.md", "type": "file", "sha": "6"*40, "sizeBytes": 60},
    {"path": "docs/large.md", "type": "file", "sha": "7"*40, "sizeBytes": 140000},
    {"path": "src/.env", "type": "file", "sha": "8"*40, "sizeBytes": 30},
    {"path": "src/image.png", "type": "file", "sha": "9"*40, "sizeBytes": 40},
]
BODIES = {
    "README.md": "# Welcome to the repo\nThis is documentation.\n",
    "src/main.py": '"""Main application entrypoint."""\nimport os\nfrom src.helper import work\n'
                   'def main():\n    # TODO validate\n    return work()\n',
    "src/helper.py": '"""Helper calculation functions."""\nimport json\ndef work():\n    return 7\n',
    "docs/overview.md": "# Architecture\nProject structure overview.\n",
}

def snap():
    return {"repository": REPO, "branch": "main", "sourceSha": SHA,
            "complete": True, "items": ROOT}

def reader(path, source, max_bytes):
    assert source == SHA
    assert path not in ("src/.env", "src/image.png")
    assert path in BODIES
    row = next(x for x in ROOT if x["path"] == path)
    assert row["sizeBytes"] <= max_bytes
    return {"sha": row["sha"], "body": BODIES[path]}

def raises(fn, message=""):
    try:
        fn()
    except explorer.ExplorerError as exc:
        if message: assert message in str(exc), str(exc)
    else:
        raise AssertionError("Expected ExplorerError")

def test_selected_paths_and_exact_union():
    r = report.build_report(snap(), ["src", "src/main.py", "docs/overview.md"], "deep", reader)
    assert r["repository"] == REPO and r["sourceSha"] == SHA
    assert r["inventory"]["files"] == 5, r["inventory"]
    assert r["scopes"][0]["files"] == 4 and r["scopes"][1]["files"] == 1
    assert r["inspection"]["inspected"] == 3, r["inspection"]
    assert "src/main.py" in {x["path"] for x in r["files"]}
    assert any(x["path"] == "src/main.py" and any(s["name"] == "main" for s in x["symbols"]) for x in r["files"])
    assert any(x["path"] == "src/main.py" and x["todoMarkers"] == 1 for x in r["files"])
    assert any(x["path"] == "src/main.py" and "src.helper" in x["imports"] for x in r["files"])
    assert any(x["path"] == "src/main.py" and any(y["target"] == "src/helper.py" for y in x["verifiedLocalImportMatches"]) for x in r["files"])
    assert r["inspection"]["explicitFilesNotInspected"] == []
    assert r["inspection"]["notInspected"] == 2
    assert r["inspection"]["complete"] is False
    md = report.markdown_report(r)
    assert "5 unique files" in md and "3/5" in md and "src/main.py" in md
    assert not any("This is documentation." in str(x) for x in r["files"]), "Do not serialize raw source"

def test_root_and_budget_and_modes():
    root = report.build_report(snap(), "/", "overview", reader)
    assert root["inventory"]["complete"]
    assert root["inventory"]["files"] == 7
    assert root["scopes"][0]["directories"] == 2
    assert root["inspection"]["inspected"] <= 4
    assert root["inspection"]["notInspected"] >= 3
    assert root["inventory"]["languageCounts"]["Python"] == 2
    assert not any(x["path"].endswith((".env", ".png")) for x in root["files"])
    small = report.build_report(snap(), "src/main.py", "deep", reader)
    assert small["inspection"]["complete"] and small["inspection"]["inspected"] == 1
    assert small["files"][0]["purposeEvidence"].startswith("Main application")
    assert small["files"][0]["lineCount"] >= 4
    overview = report.build_report(snap(), "src/main.py", "overview", reader)
    assert overview["files"][0]["symbols"] == [] and overview["files"][0]["imports"] == []

def test_rejections_and_identity_boundary():
    for invalid in ("../secrets", "/../bad", "src//bad", "not-here", "http://evil",
                    "[\"docs\", \"../unsafe\"]"):
        raises(lambda: report.build_report(snap(), invalid, "deep", reader))
    raises(lambda: report.build_report(snap(), ["/"] * 13, "deep", reader), "12")
    raises(lambda: report.build_report(snap(), "/", "unlimited", reader), "depth")
    raises(lambda: report.build_report({**snap(), "complete": False}, "/", "deep", reader), "Complete")
    def wrong_sha(path, source, max_bytes):
        return {"sha": "f"*40, "body": "def fake(): pass\n"}
    bad = report.build_report(snap(), "src/main.py", "deep", wrong_sha)
    assert bad["inspection"]["inspected"] == 0
    assert bad["inspection"]["explicitFilesNotInspected"] == ["src/main.py"]
    assert bad["inspection"]["skippedReasons"].get("Git blob SHA mismatch")
    with mock.patch.object(gh, "_explorer_owner", side_effect=HTTPException(403, "No read access")):
        try: gh.explorer_report(object())
        except HTTPException as exc: assert exc.status_code == 403
        else: raise AssertionError("Unauthenticated report allowed")
    with mock.patch.object(gh, "_explorer_owner", return_value=("google:one",{"token":"token"},REPO,"main")), \
         mock.patch.object(gh.explorer, "pinned_tree", return_value=snap()), \
         mock.patch.object(gh, "_read_optional", side_effect=lambda t,r,p,sha,max_bytes:reader(p,sha,max_bytes)):
        data = gh.explorer_report(object(), '["src/main.py", "docs"]', "deep")
        assert data["repository"] == REPO and data["inventory"]["files"] == 3
        assert data["readOnly"] is True
        try: gh.explorer_report(object(), '["../bad"]')
        except HTTPException as exc: assert exc.status_code == 422
        else: raise AssertionError("Bad paths accepted")
    assert gh._read_stage_command("@GitHub report deep src | docs")
    assert gh.is_github_command("@GitHub report overview /")
    assert not gh._read_stage_command("@GitHub create file report.md")

if __name__ == "__main__":
    test_selected_paths_and_exact_union()
    test_root_and_budget_and_modes()
    test_rejections_and_identity_boundary()
    print("v226 GitHub report: scopes, SHA, bounded evidence, read-only auth and analysis depth PASS")
