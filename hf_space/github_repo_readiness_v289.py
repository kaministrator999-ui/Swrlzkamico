"""v289 verified repository maturity classifier.

Operates only on an already-authorized complete SHA-pinned Git tree.
Path metadata is evidence; ZIP contents, source runtime and write permission
are never inferred. No model inference or GitHub mutation is performed.
"""
from __future__ import annotations

from pathlib import PurePosixPath
import re

SOURCE_EXTS = {".py", ".js", ".jsx", ".mjs", ".ts", ".tsx", ".java", ".kt",
               ".go", ".rs", ".cpp", ".c", ".cs", ".swift"}
ARCHIVES = {".zip", ".tar", ".gz", ".tgz", ".7z"}
SHA = re.compile(r"^[a-f0-9]{40}$")
MAX_ENTRIES = 20000


def classify(snapshot):
    """Structured, deterministic classification from verified file metadata."""
    if (not isinstance(snapshot, dict) or snapshot.get("complete") is not True
            or not SHA.fullmatch(str(snapshot.get("sourceSha") or ""))
            or not isinstance(snapshot.get("items"), list)
            or len(snapshot["items"]) > MAX_ENTRIES):
        raise ValueError("Complete SHA-pinned Git tree required")
    rows = snapshot["items"]
    files = [str(x["path"]) for x in rows if isinstance(x, dict)
             and x.get("type") == "file" and isinstance(x.get("path"), str)]
    files = sorted(set(files))
    root_readmes = {p for p in files if "/" not in p and
                    p.casefold() in ("readme.md", "readme.rst", "readme.txt")}
    code = [p for p in files if PurePosixPath(p).suffix.lower() in SOURCE_EXTS]
    archives = [p for p in files if PurePosixPath(p).suffix.lower() in ARCHIVES]
    tests = [p for p in files if p.startswith(("tests/", "test/", "write-action-tests/", "write-lab/"))]
    documents = [p for p in files if p.startswith("docs/") or p in root_readmes]
    marker = "docs/SCENARIO_MATRIX.md" in files and "write-lab/README.md" in files
    if not files:
        category = "empty"
    elif not code and set(files).issubset(root_readmes | {"LICENSE", ".gitignore", ".gitattributes"}):
        category = "onboarding-only"
    elif not code and archives:
        category = "archive-or-fixtures-only"
    elif not code and tests:
        category = "test-data-only"
    elif code and (archives or tests or marker):
        category = "mixed-source-testbed" if marker else "source-with-fixtures"
    elif code:
        category = "source-project"
    elif documents:
        category = "documentation-or-data"
    else:
        category = "data-or-assets"
    actions = {
        "empty": ["The selected branch has no visible tracked files. Do not invent paths.",
                  "Create initial files only after the owner requests and authorizes each supported action."],
        "onboarding-only": ["Read the existing README and ask which project to examine.",
                            "No code dependency analysis is possible from README alone."],
        "archive-or-fixtures-only": ["You can inspect tracked text files and file names.",
                                     "Archive contents have NOT been extracted or analyzed."],
        "test-data-only": ["Inspect existing test files and context as data.",
                           "Do not invent a source application based on tests alone."],
        "mixed-source-testbed": ["Read docs/SCENARIO_MATRIX.md for owner-controlled read/write test cases.",
                                 "Use real source imports for structural analysis; writes still need separate authorization."],
        "source-with-fixtures": ["Inspect selected source and local dependencies.",
                                 "Tests are present but have not been executed by this status check."],
        "source-project": ["Inspect exact source and its dependencies.",
                           "Code presence alone is not proof of runtime behavior or deployment."],
        "documentation-or-data": ["Read verified docs/data first; don't assume runnable source."],
        "data-or-assets": ["Show file types and ask which supported text file to inspect."]
    }[category]
    return {"schema": "swrlz-repo-readiness-v1", "category": category,
            "sourceSha": snapshot["sourceSha"], "branch": snapshot.get("branch") or "",
            "repository": snapshot.get("repository") or "",
            "counts": {"files": len(files), "sourceFiles": len(code), "archives": len(archives),
                       "testFiles": len(tests), "documents": len(documents)},
            "markerVerified": marker, "suggestions": actions,
            "capabilities": {"readAnalysis": bool(code), "archiveContentsRead": False,
                             "writesAuthorizedByThisCheck": False}}


def one_line(data):
    counts = data["counts"]
    return ("Repository readiness: " + data["category"] +
            " (" + str(counts["files"]) + " tracked files; " +
            str(counts["sourceFiles"]) + " source files). " +
            "Read-only inventory; not a permissions or deployment check.")


def report(data):
    if data.get("schema") != "swrlz-repo-readiness-v1":
        raise ValueError("Invalid readiness data")
    counts = data["counts"]
    safe = lambda s: str(s).replace(chr(96), "'").replace("\n", " ")[:135]
    out = ["## GitHub repository readiness",
           "Repository: " + safe(data["repository"]),
           "Branch: " + safe(data["branch"]),
           "Revision: " + safe(data["sourceSha"]),
           "**Classification:** " + safe(data["category"]),
           "**Tracked files:** " + str(counts["files"]) +
           " · **source:** " + str(counts["sourceFiles"]) +
           " · **tests:** " + str(counts["testFiles"]) +
           " · **archives:** " + str(counts["archives"]),
           "### Suggested next steps"]
    out.extend("- " + safe(s) for s in data["suggestions"])
    out.append("Read-only verified tree inspection. No archive extraction, tests, write permission checks, edits or deployments.")
    return "\n".join(out)
