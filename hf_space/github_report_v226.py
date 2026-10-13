"""Read-only, SHA-pinned GitHub scope reports.

The complete Git tree supplies exhaustive inventory facts. Only a bounded subset
of files is inspected for source structure; these are NEVER called a full code
audit. Nothing from repository content is interpreted as instructions.
"""
from __future__ import annotations

from collections import Counter
import json
import re
from pathlib import PurePosixPath

from github_explorer_v223 import ExplorerError, safe_path, scope_stats

MAX_SCOPES = 12
LIMITS = {"overview": 4, "structure": 12, "deep": 24}
TEXT_LIMIT = 120000
TOTAL_TEXT = {"overview": 45000, "structure": 160000, "deep": 300000}
BINARY_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf",
               ".zip", ".tar", ".gz", ".7z", ".jar", ".wasm", ".ttf", ".otf",
               ".mp3", ".mp4", ".ogg", ".wav", ".db", ".sqlite", ".lock"}
SENSITIVE = re.compile(r"(?i)(^|/)(?:\.env(?:\..*)?|id_rsa|id_ed25519|"
                       r".*(?:private[_-]?key|credentials|secret[_-]?token).*)$")
LANGUAGES = {".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript",
             ".ts": "TypeScript", ".tsx": "TypeScript", ".jsx": "JavaScript",
             ".kt": "Kotlin", ".java": "Java", ".rs": "Rust", ".go": "Go",
             ".c": "C", ".h": "C header", ".cpp": "C++", ".cs": "C#",
             ".html": "HTML", ".css": "CSS", ".scss": "SCSS", ".sh": "Shell",
             ".json": "JSON", ".toml": "TOML", ".yml": "YAML",
             ".yaml": "YAML", ".xml": "XML", ".md": "Markdown",
             ".rst": "reStructuredText", ".sql": "SQL", ".swift": "Swift"}
SYMBOL = re.compile(r"^\s*(?:async\s+)?(?:def|class|function|export\s+(?:default\s+)?(?:async\s+)?function|"
                    r"export\s+class|interface|struct|fn|fun)\s+([A-Za-z_$][\w$]*)\b", re.M)
IMPORT = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w., ]+)|"
                    r"(?:const|let|var)\s+.+?\s*=\s*require\(['\"]([^'\"]+)['\"]\)|"
                    r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"])\s*", re.M)
TASKS = re.compile(r"\b(?:TODO|FIXME|XXX)\b")
SAFE_HEADER = re.compile(r"(?i)(?:token|password|secret|api[_-]?key|private[_-]?key|bearer|credential)\s*[:=]")


def selection_paths(value):
    """Validate an explicit list, a single path, or command-delimited paths."""
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("["):
            try:
                value = json.loads(value)
            except ValueError as exc:
                raise ExplorerError("Report paths must be a JSON array or | separated paths") from exc
        else:
            value = value.split("|")
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_SCOPES:
        raise ExplorerError("Choose between 1 and 12 folders/files")
    normalized = []
    for item in value:
        if not isinstance(item, str):
            raise ExplorerError("Report paths must be strings")
        path = safe_path(item.strip())
        if path not in normalized:
            normalized.append(path)
    return normalized


def file_kind(path):
    name = PurePosixPath(path).name
    extension = PurePosixPath(path).suffix.lower()
    if name.lower() in ("dockerfile", "makefile"):
        return "Build/configuration"
    if name.lower().startswith("readme") or extension in (".md", ".rst"):
        return "Documentation"
    if name.lower().startswith("test_") or name.lower().endswith((".test.js", ".spec.js", ".test.ts", ".spec.ts")):
        return "Automated test"
    if "/tests/" in "/" + path + "/" or "/test/" in "/" + path + "/":
        return "Test/support"
    if name.lower().endswith(".lock") or extension in (".toml", ".yaml", ".yml", ".json", ".xml"):
        return "Configuration / data"
    if extension in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".mp3", ".mp4"):
        return "Asset"
    return LANGUAGES.get(extension, "Unknown/other") + " source or resource"


def safe_heading(text):
    value = " ".join(str(text or "").split())[:180]
    return "" if SAFE_HEADER.search(value) or len(value) < 8 else value


def structure(path, body, depth):
    lines = body.splitlines()
    result = {"language": LANGUAGES.get(PurePosixPath(path).suffix.lower(), "Other"),
              "lineCount": len(lines), "purposeEvidence": "", "symbols": [],
              "imports": [], "todoMarkers": 0, "analysisType": "static-source-structure"}
    # Only short, non-sensitive first-line descriptions; no raw code or credentials.
    for line in lines[:20]:
        stripped = line.strip()
        if stripped.startswith(("# ", "// ", "* ", '"""', "'''")):
            value = safe_heading(stripped.lstrip("#/*'\" ").strip())
            if value and not value.lower().startswith(("copyright", "license", "http", "spdx")):
                result["purposeEvidence"] = value
                break
    if depth == "overview":
        return result
    seen_symbols = set()
    for match in SYMBOL.finditer(body):
        name = match.group(1)
        if name not in seen_symbols and len(result["symbols"]) < (30 if depth == "deep" else 14):
            result["symbols"].append({"name": name, "line": body.count("\n", 0, match.start()) + 1})
            seen_symbols.add(name)
    seen_imports = set()
    for match in IMPORT.finditer(body):
        name = next((x for x in match.groups() if x), "").strip()
        name = name.split(",")[0].strip()
        if name and len(name) <= 100 and name not in seen_imports and len(result["imports"]) < 20:
            result["imports"].append(name)
            seen_imports.add(name)
    result["todoMarkers"] = len(TASKS.findall(body))
    return result


def internal_import_refs(file, full_index):
    """Match declared imports to actual verified repository paths, not guesses."""
    base = PurePosixPath(file["path"]).parent
    links = []
    for ref in file["imports"]:
        targets = []
        if ref.startswith("."):
            joined = str(base / ref)
            if ".." in joined.split("/"):
                continue
            targets.append(joined)
        else:
            targets.append(ref.replace(".", "/"))
        for prefix in targets:
            for target in (prefix, prefix + ".py", prefix + ".js", prefix + ".ts",
                           prefix + ".mjs", prefix + "/__init__.py", prefix + "/index.js"):
                if target in full_index and target != file["path"]:
                    if not any(item["target"] == target for item in links):
                        links.append({"importRef": ref, "target": target})
                    break
    return links[:20]


def build_report(snapshot, requested, depth="structure", read_file=None):
    if depth not in LIMITS:
        raise ExplorerError("Report depth must be overview, structure or deep")
    paths = selection_paths(requested)
    entries = snapshot.get("items")
    if snapshot.get("complete") is not True or not isinstance(entries, list):
        raise ExplorerError("Complete verified Git tree is required for a repository report")
    index = {x["path"]: x for x in entries}
    scopes = []
    union = {}
    explicit_files = []
    for path in paths:
        if path:
            node = index.get(path)
            if not node:
                raise ExplorerError("Selected scope is missing from verified source: " + path)
        else:
            node = {"type": "dir"}
        if node["type"] == "dir":
            stats = scope_stats(snapshot, path)
            prefix = path + "/" if path else ""
            subset = [x for x in entries if x["type"] == "file" and x["path"].startswith(prefix)]
            scopes.append({"path": path or "/", "type": "dir",
                           "files": stats["recursiveFiles"], "directories": stats["recursiveDirectories"],
                           "gitBlobBytes": stats["gitBlobBytes"], "sizeComplete": stats["sizeComplete"]})
        elif node["type"] == "file":
            subset = [node]
            explicit_files.append(path)
            scopes.append({"path": path, "type": "file", "files": 1,
                           "directories": 0, "gitBlobBytes": node["sizeBytes"],
                           "sizeComplete": isinstance(node["sizeBytes"], int)})
        else:
            raise ExplorerError("Unknown scope type")
        for item in subset:
            union[item["path"]] = item
    selected = list(union.values())
    known_sizes = all(isinstance(x.get("sizeBytes"), int) for x in selected)
    extensions = Counter(LANGUAGES.get(PurePosixPath(x["path"]).suffix.lower(), "Other") for x in selected)
    purposes = Counter(file_kind(x["path"]) for x in selected)
    top = Counter(x["path"].split("/")[0] if "/" in x["path"] else "(root files)" for x in selected)
    # Prioritize explicitly named files, then a small representative cross-scope
    # sample. This is not an exhaustive source-content scan for large scopes.
    def priority(item):
        path = item["path"]
        base = PurePosixPath(path).name.lower()
        rank = (0 if path in explicit_files else
                1 if base.startswith(("readme", "architecture", "overview")) else
                2 if base in ("pyproject.toml", "package.json", "requirements.txt", "dockerfile") else
                3 if "/docs/" in "/" + path + "/" else 4)
        return (rank, path.count("/"), path.casefold())
    sorted_candidates = sorted(selected, key=priority)
    # Breadth first: for each directory scope, inspect representatives from
    # distinct direct children before filling remaining source-read slots.
    chosen = []
    chosen_paths = set()
    def add_candidate(item):
        if item["path"] not in chosen_paths:
            chosen.append(item)
            chosen_paths.add(item["path"])
    for item in sorted_candidates:
        if item["path"] in explicit_files:
            add_candidate(item)
    for root in paths:
        if root and index[root]["type"] == "file":
            continue
        prefix = root + "/" if root else ""
        grouped = {}
        for item in sorted_candidates:
            path = item["path"]
            if not path.startswith(prefix):
                continue
            remainder = path[len(prefix):]
            group = remainder.split("/")[0] if "/" in remainder else "(direct files)"
            grouped.setdefault(group, item)
        for item in grouped.values():
            add_candidate(item)
    for item in sorted_candidates:
        add_candidate(item)
    budget = TOTAL_TEXT[depth]
    scanned = []
    skipped = Counter()
    for item in chosen:
        if len(scanned) >= LIMITS[depth]:
            break
        path = item["path"]
        suffix = PurePosixPath(path).suffix.lower()
        if SENSITIVE.search(path) or suffix in BINARY_EXTS:
            skipped["sensitive or non-text paths"] += 1
            continue
        size = item.get("sizeBytes")
        if not isinstance(size, int) or size > TEXT_LIMIT or size > budget:
            skipped["oversize / unknown size / byte budget"] += 1
            continue
        if read_file is None:
            skipped["source reader not provided"] += 1
            continue
        try:
            record = read_file(path, snapshot["sourceSha"], min(TEXT_LIMIT, budget))
        except Exception:
            record = None
        if not isinstance(record, dict) or not isinstance(record.get("body"), str):
            skipped["unavailable UTF-8 source"] += 1
            continue
        if record.get("sha") != item.get("sha"):
            skipped["Git blob SHA mismatch"] += 1
            continue
        body = record["body"]
        if len(body.encode("utf-8")) > budget:
            skipped["source byte budget"] += 1
            continue
        budget -= len(body.encode("utf-8"))
        inspected = structure(path, body, depth)
        scanned.append({"path": path, "blobSha": item["sha"], "sizeBytes": size,
                        "kind": file_kind(path), **inspected})
    for file in scanned:
        file["verifiedLocalImportMatches"] = internal_import_refs(file, index)
    scanned_paths = {x["path"] for x in scanned}
    return {"schema": "swrlz-github-scope-report-v1", "repository": snapshot["repository"],
            "branch": snapshot["branch"], "sourceSha": snapshot["sourceSha"],
            "depth": depth, "scopes": scopes,
            "inventory": {"complete": True, "files": len(selected),
                          "gitBlobBytes": sum(x["sizeBytes"] for x in selected) if known_sizes else None,
                          "sizeComplete": known_sizes,
                          "languageCounts": dict(extensions.most_common(16)),
                          "roleCounts": dict(purposes.most_common(12)),
                          "topLevelCounts": dict(top.most_common(18))},
            "inspection": {"limit": LIMITS[depth], "inspected": len(scanned),
                           "totalFiles": len(selected), "notInspected": len(selected)-len(scanned),
                           "explicitFileCount": len(explicit_files),
                           "explicitFilesNotInspected": [p for p in explicit_files if p not in scanned_paths],
                           "skippedReasons": dict(skipped),
                           "complete": len(scanned) == len(selected),
                           "note": "Complete Git-tree scope inventory; source descriptions and symbols cover only listed inspected UTF-8 files. Purpose and dependency roles are inferred, not execution-verified."},
            "files": scanned, "readOnly": True}


def markdown_report(data, limit=15000):
    """Bounded plain Markdown for explicit Chat @GitHub report commands."""
    inv, cov = data["inventory"], data["inspection"]
    out = ["## GitHub source report · " + data["repository"],
           "Branch: " + data["branch"] + " · commit " + data["sourceSha"],
           "Depth: " + data["depth"],
           "Scopes: " + ", ".join(x["path"] for x in data["scopes"]),
           "Verified Git-tree inventory: " + str(inv["files"]) + " unique files",
           "Source contents inspected: " + str(cov["inspected"]) + "/" + str(cov["totalFiles"]),
           cov["note"],
           "### Source categories"]
    out += [("- " + str(k) + ": " + str(v)) for k,v in inv["languageCounts"].items()]
    out.append("### Inspected files")
    for item in data["files"]:
        out.append("- " + item["path"] + " (" + item["kind"] + ", " + str(item["lineCount"]) +
                   " lines, Git blob " + item["blobSha"][:12] + ")")
        if item["purposeEvidence"]:
            out.append("  - Opening comment: " + item["purposeEvidence"])
        if item["symbols"]:
            out.append("  - Declared symbols: " + ", ".join(s["name"] + ":" + str(s["line"])
                                                      for s in item["symbols"][:15]))
        if item["imports"]:
            out.append("  - Import references: " + ", ".join(item["imports"][:15]))
        if item["verifiedLocalImportMatches"]:
            out.append("  - Confirmed paths matching imports (static): " + ", ".join(x["target"] for x in item["verifiedLocalImportMatches"]))
        if item["todoMarkers"]:
            out.append("  - TODO/FIXME markers: " + str(item["todoMarkers"]))
    if cov["explicitFilesNotInspected"]:
        out.append("Requested files not inspected: " + ", ".join(cov["explicitFilesNotInspected"]))
    out.append("Source inspection is static, not a behavioral or security audit.")
    text = "\n".join(out)
    return text[:limit] + ("\n(Report display truncated; narrow scope in GitHub Explorer for more.)"
                            if len(text) > limit else "")
