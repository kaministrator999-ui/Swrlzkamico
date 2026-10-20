"""Deterministic v288 file intelligence regressions; no OAuth/network/models."""
import hashlib
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import github_file_intelligence_v288 as fi

SHA = "a" * 40
MAIN = "pkg/main.py"
HELP = "pkg/helper.py"
SECRET = "pkg/.env"


def item(path, body):
    return {"path": path, "type": "file", "sha": fi.blob_sha(body),
            "sizeBytes": len(body.encode("utf-8"))}


MAIN_TEXT = "from .helper import work\nimport os\n\nclass App:\n    pass\n\ndef run():\n    return work()\n"
HELP_TEXT = "def work():\n    return 42\n"
OTHER = "const value = 1\n"
SRC = {MAIN: MAIN_TEXT, HELP: HELP_TEXT, "src/config.js": OTHER, SECRET: "SECRET=topsecret"}
TREE = {"sourceSha": SHA, "complete": True, "items": [item(p, s) for p, s in SRC.items()]}
READS = []


def read(path, source, limit):
    READS.append((path, source, limit))
    assert source == SHA
    assert path not in (SECRET,)
    assert len(SRC[path].encode()) <= limit
    return {"sha": fi.blob_sha(SRC[path]), "body": SRC[path]}


def raises(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("Expected value rejection")


def test_ast_dependency_and_plan():
    READS.clear()
    report = fi.inspect(TREE, MAIN, MAIN_TEXT, read, "What breaks if I rename this dependency?")
    assert report["scenario"]["primary"] == "impact", report["scenario"]
    assert report["readOnly"]
    assert [x["name"] for x in report["primary"]["symbols"]] == ["App", "run"]
    assert any(x["ref"] == ".helper" and x["line"] == 1
               and x["targets"] == [HELP] and x["status"] == "resolved"
               for x in report["imports"])
    assert any(x["ref"] == "os" and x["status"] == "external-or-unresolved"
               for x in report["imports"])
    assert [r["path"] for r in report["related"]] == [HELP], report["related"]
    assert READS == [(HELP, SHA, fi.MAX_RELATED_BYTES)], READS
    assert report["coverage"]["filesInspected"] == 2
    markdown = fi.markdown_report(report)
    assert "Scenario:** impact" in markdown and "Exact tree dependencies" in markdown
    assert "no tests, execution, edits or deployments" in markdown
    assert "SECRET=topsecret" not in str(report) + markdown


def test_language_parsing():
    x = fi.parse_structure("lib/core.ts", "import { work } from './helper'\nexport class Core {}\n")
    assert x["language"] == "TypeScript"
    assert x["imports"] == [{"ref": "./helper", "line": 1}], x
    assert x["symbols"][0]["name"] == "Core"
    x = fi.parse_structure("pkg/foo.py", "def invalid(:\n")
    assert x["symbols"] == [] and x["limitations"]
    x = fi.parse_structure("README.md", "# Title\n## Usage\ntext\n")
    assert [s["name"] for s in x["symbols"]] == ["Title", "Usage"]
    x = fi.parse_structure("config.json", '{"key": 1, "other": 2}')
    assert len(x["symbols"]) == 2
    assert fi.candidates("src/a.ts", "../outside") == []
    assert fi.candidates("src/main.py", ".helper") == ["src/helper.py", "src/helper/__init__.py"]


def test_preflight_and_uncertainty():
    raises(lambda: fi.inspect({**TREE, "complete": False}, MAIN, MAIN_TEXT, read))
    raises(lambda: fi.inspect({**TREE, "sourceSha": "bad"}, MAIN, MAIN_TEXT, read))
    raises(lambda: fi.inspect(TREE, MAIN, "tampered", read))
    raises(lambda: fi.inspect(TREE, SECRET, SRC[SECRET], read))
    raises(lambda: fi.inspect(TREE, "../main.py", MAIN_TEXT, read))
    assert fi.scenario_for("Investigate a crash")["primary"] == "debug"
    assert fi.scenario_for("Inspect permissions")["primary"] == "security"
    assert fi.scenario_for("How is this architecture connected")["primary"] == "architecture"
    assert fi.scenario_for("Hi")["primary"] == "explain"


def test_other_blob_is_not_read():
    def corrupted(path, source, limit):
        return {"sha": "f"*40, "body": SRC[path]}
    report = fi.inspect(TREE, MAIN, MAIN_TEXT, corrupted, "trace dependencies")
    assert report["related"] == []
    assert report["coverage"]["filesInspected"] == 1
    assert any(x["status"] == "resolved" for x in report["imports"])
    assert "Related source inspected" not in fi.markdown_report(report)


def test_collision_is_not_a_false_dependency():
    body = "import utility\n"
    repo = {"sourceSha": SHA, "complete": True,
            "items": [item("project/main.py", body),
                      item("utility.py", "pass\n"),
                      item("project/utility.py", "pass\n")]}
    def unavailable(*args):
        raise AssertionError("Ambiguous import must not fetch")
    r = fi.inspect(repo, "project/main.py", body, unavailable)
    assert r["imports"][0]["status"] == "ambiguous", r["imports"]
    assert r["related"] == []


if __name__ == "__main__":
    test_ast_dependency_and_plan()
    test_language_parsing()
    test_preflight_and_uncertainty()
    test_other_blob_is_not_read()
    test_collision_is_not_a_false_dependency()
    print("v288 file intelligence: static parsing, SHA, scenarios, boundaries PASS")
