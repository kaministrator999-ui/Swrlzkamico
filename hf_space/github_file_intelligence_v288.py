"""v288: read-only, bounded, source-verified GitHub file intelligence.

Deterministic parsing and graph edges complement the existing source specialist.
Neither repository text nor model output can authorize a tool call or mutation.
"""
from __future__ import annotations

import ast
import hashlib
import json
import posixpath
import re
from pathlib import PurePosixPath

SHA = re.compile(r"^[a-f0-9]{40}$")
SECRET = re.compile(r"(?i)(^|/)(?:secrets?|credentials?|tokens?|keys?|certificates?|id_rsa|id_ed25519)(/|$)")
EXTS = {".py", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".kt", ".java",
        ".go", ".rs", ".md", ".txt", ".json", ".yml", ".yaml", ".toml"}
MAX_FILES = 4
MAX_TREE = 20000
MAX_RELATED_BYTES = 32000
TOTAL_RELATED_BYTES = 96000

SCENARIOS = (
    ("security", r"\b(?:security|vulnerab|injection|permissions?|auth|secret|unsafe|exploit)\b",
     ("inspect-boundaries", "trace-imports", "identify-unverified-risks")),
    ("regression", r"\b(?:regression|broke|stopped working|since the update|before.?after)\b",
     ("trace-imports", "identify-related-code", "request-commit-diff")),
    ("impact", r"\b(?:impact|break if|dependenc|references?|rename|change this|affected)\b",
     ("extract-symbols", "trace-imports", "map-potential-impact")),
    ("debug", r"\b(?:bug|error|fail|crash|debug|diagnos|not working|exception)\b",
     ("extract-symbols", "trace-imports", "identify-test-targets")),
    ("architecture", r"\b(?:architect|how (?:it|this) works|connected|flow|relationship|integrat)\b",
     ("extract-symbols", "trace-imports", "map-components")),
)


def scenario_for(goal):
    """Select reusable read-only skills, not arbitrary provider operations."""
    matches = [(name, ops) for name, pattern, ops in SCENARIOS
               if re.search(pattern, str(goal or "")[:700], re.I)]
    if not matches:
        return {"primary": "explain", "secondary": [],
                "capabilities": ["extract-symbols", "trace-imports", "explain-evidence"]}
    ops = list(dict.fromkeys(x for _, steps in matches[:2] for x in steps))
    return {"primary": matches[0][0], "secondary": [x[0] for x in matches[1:2]],
            "capabilities": ops[:6]}


def safe_source_path(path):
    if not isinstance(path, str) or len(path) > 240 or path.startswith("/") or "\\" in path:
        return False
    if any(x in ("", ".", "..") or x.startswith(".") for x in path.split("/")):
        return False
    return not SECRET.search(path) and PurePosixPath(path).suffix.lower() in EXTS


def blob_sha(source):
    data = source.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def parse_structure(path, source):
    """Python AST is exact; JS/TS is best-effort; other formats disclose limits."""
    ext = PurePosixPath(path).suffix.lower()
    rows = source.splitlines()
    symbols, imports, limitations = [], [], []
    if ext == ".py":
        try:
            tree = ast.parse(source)
        except (SyntaxError, ValueError) as exc:
            return {"language": "Python", "lines": len(rows), "symbols": [], "imports": [],
                    "limitations": ["AST unavailable: " + type(exc).__name__]}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                symbols.append({"name": node.name, "line": node.lineno,
                                "kind": "class" if isinstance(node, ast.ClassDef) else "function"})
            elif isinstance(node, ast.Import):
                imports.extend({"ref": alias.name, "line": node.lineno} for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                ref = "." * node.level + (node.module or "")
                imports.append({"ref": ref, "line": node.lineno})
                if node.level and not node.module:
                    imports.extend({"ref": ref + alias.name, "line": node.lineno}
                                   for alias in node.names if alias.name != "*")
        language = "Python"
    elif ext in (".js", ".jsx", ".mjs", ".ts", ".tsx"):
        language = "TypeScript" if ext in (".ts", ".tsx") else "JavaScript"
        sym = re.compile(r"\b(?:function|class|interface|type|enum)\s+([A-Za-z_$][\w$]*)")
        imp = re.compile(r"(?:\b(?:import|export)\s+(?:[^;]*?\s+from\s+)?|\brequire\s*\(|"
                         r"\bimport\s*\()\s*['\"]([^'\"\n]+)['\"]")
        for n, row in enumerate(rows, 1):
            if len(row) > 2000:
                continue
            symbols.extend({"name": m.group(1), "line": n, "kind": "declaration"} for m in sym.finditer(row))
            imports.extend({"ref": m.group(1), "line": n} for m in imp.finditer(row))
        limitations.append("JavaScript/TypeScript uses lexical extraction, not a full parser")
    elif ext in (".md", ".txt"):
        language = "Markdown" if ext == ".md" else "Text"
        if ext == ".md":
            for n, row in enumerate(rows, 1):
                if re.match(r"^#{1,4}\s", row):
                    symbols.append({"name": row.lstrip("# ").strip()[:100], "line": n, "kind": "heading"})
    elif ext == ".json":
        language = "JSON"
        try:
            obj = json.loads(source)
            if isinstance(obj, dict):
                symbols = [{"name": str(k)[:90], "line": None, "kind": "key"}
                           for k in list(obj)[:40]]
        except (ValueError, TypeError):
            limitations.append("Invalid JSON")
    else:
        language = ext.lstrip(".").upper()
        limitations.append("No syntax parser for this language")
    return {"language": language, "lines": len(rows), "symbols": symbols[:40],
            "imports": imports[:35], "limitations": limitations}


def candidates(path, ref):
    """Only exact, existing tree entries can become verified dependency edges."""
    folder = posixpath.dirname(path)
    ext = PurePosixPath(path).suffix.lower()
    if ext == ".py":
        if ref.startswith("."):
            level = len(ref) - len(ref.lstrip("."))
            parts = folder.split("/") if folder else []
            if level > len(parts) + 1:
                return []
            base = "/".join(parts[:len(parts) - level + 1])
            names = [posixpath.join(base, ref[level:].replace(".", "/"))]
        else:
            stem = ref.replace(".", "/")
            names = [stem, posixpath.join(folder, stem)]
        paths = [p for n in names for p in (n + ".py", n + "/__init__.py")]
    elif ext in (".js", ".jsx", ".mjs", ".ts", ".tsx") and ref.startswith("."):
        stem = posixpath.normpath(posixpath.join(folder, ref))
        paths = [stem + suffix for suffix in ("", ".js", ".ts", ".jsx", ".tsx", ".mjs",
                                              "/index.js", "/index.ts", "/index.tsx")]
    else:
        paths = []
    return list(dict.fromkeys(p for p in paths if safe_source_path(p)))


def inspect(snapshot, path, source, read_file, goal=""):
    """Inspect a single verified file plus up to four verified direct dependencies."""
    if (not isinstance(snapshot, dict) or snapshot.get("complete") is not True
            or not isinstance(snapshot.get("items"), list)
            or len(snapshot["items"]) > MAX_TREE
            or not SHA.fullmatch(str(snapshot.get("sourceSha") or ""))):
        raise ValueError("Complete SHA-pinned Git tree required")
    index = {row["path"]: row for row in snapshot["items"] if isinstance(row, dict)
             and isinstance(row.get("path"), str) and row.get("type") == "file"}
    if not safe_source_path(path) or path not in index or not isinstance(source, str):
        raise ValueError("Invalid or unsupported selected file")
    primary = index[path]
    if (not SHA.fullmatch(str(primary.get("sha") or ""))
            or len(source.encode("utf-8")) > 256000 or blob_sha(source) != primary["sha"]):
        raise ValueError("Primary source blob mismatch or oversized")
    structure = parse_structure(path, source)
    links = []
    for imp in structure["imports"]:
        targets = [p for p in candidates(path, imp["ref"]) if p in index and p != path]
        links.append({"ref": imp["ref"], "line": imp["line"],
                      "status": "resolved" if len(targets) == 1 else
                                "ambiguous" if targets else "external-or-unresolved",
                      "targets": targets[:4]})
    related, visited, consumed = [], {path}, 0
    for link in links:
        if link["status"] != "resolved":
            continue
        target = link["targets"][0]
        if target in visited:
            continue
        visited.add(target)
        row = index[target]
        size = row.get("sizeBytes")
        if (len(related) >= MAX_FILES or not isinstance(size, int)
                or size > MAX_RELATED_BYTES or consumed + size > TOTAL_RELATED_BYTES
                or not SHA.fullmatch(str(row.get("sha") or ""))):
            continue
        try:
            doc = read_file(target, snapshot["sourceSha"], MAX_RELATED_BYTES)
        except Exception:
            continue
        if not isinstance(doc, dict) or doc.get("sha") != row["sha"]:
            continue
        body = doc.get("body")
        if (not isinstance(body, str) or len(body.encode("utf-8")) > MAX_RELATED_BYTES
                or blob_sha(body) != row["sha"]):
            continue
        consumed += len(body.encode("utf-8"))
        extra = parse_structure(target, body)
        related.append({"path": target, "blobSha": row["sha"], "language": extra["language"],
                        "symbols": extra["symbols"][:12], "lines": extra["lines"]})
    return {"schema": "swrlz-file-intelligence-v1", "readOnly": True,
            "sourceSha": snapshot["sourceSha"], "path": path, "blobSha": primary["sha"],
            "scenario": scenario_for(goal), "primary": structure,
            "imports": links, "related": related,
            "coverage": {"filesInTree": len(index), "filesInspected": 1 + len(related),
                         "relatedBytes": consumed, "repositoryComplete": False}}


def markdown_report(data):
    """Bounded display/model evidence; no raw dependency source is returned."""
    if data.get("schema") != "swrlz-file-intelligence-v1":
        raise ValueError("Unexpected intelligence schema")
    q = chr(96)
    safe = lambda x: str(x).replace(q, "'").replace("\n", " ")[:130]
    info = data["primary"]
    plan = data["scenario"]
    out = ["### File intelligence · static evidence",
           "**Scenario:** " + safe(plan["primary"]) + " · **Capabilities:** " +
           ", ".join(plan["capabilities"]),
           "**File:** " + q + safe(data["path"]) + q + " · " + safe(info["language"]) +
           " · " + str(info["lines"]) + " lines"]
    if info["symbols"]:
        out.append("**Structures:** " + ", ".join(
            q + safe(x["name"]) + q + (" (line " + str(x["line"]) + ")" if x.get("line") else "")
            for x in info["symbols"][:8]))
    linked = [x for x in data["imports"] if x["status"] == "resolved"]
    if linked:
        out.append("**Exact tree dependencies:** " + "; ".join(
            q + safe(x["ref"]) + q + " → " + q + safe(x["targets"][0]) + q +
            " (source line " + str(x["line"]) + ")" for x in linked[:7]))
    else:
        out.append("**Exact tree dependencies:** none resolved")
    if data["related"]:
        out.append("**Related source inspected:** " + ", ".join(q + safe(x["path"]) + q for x in data["related"]))
    unresolved = sum(x["status"] != "resolved" for x in data["imports"])
    if unresolved:
        out.append("**Ambiguous/external/unresolved imports:** " + str(unresolved) +
                   " (not confirmed missing or broken)")
    if info["limitations"]:
        out.append("**Parser limit:** " + "; ".join(info["limitations"][:2]))
    cover = data["coverage"]
    out.append("**Coverage:** " + str(cover["filesInspected"]) + " inspected of " +
               str(cover["filesInTree"]) + " paths in pinned tree. Not a full repo audit; " +
               "no tests, execution, edits or deployments.")
    return "\n\n".join(out)
