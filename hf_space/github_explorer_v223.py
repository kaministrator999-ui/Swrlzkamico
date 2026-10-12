"""Read-only GitHub repository explorer over pinned, verified Git trees.

No OAuth tokens or repository file content are persisted here. All supplied
GitHub API requests are read-only, bounded, path-validated and evidence-scoped.
"""
from __future__ import annotations
import re
from urllib.parse import quote

SHA = re.compile(r"^[a-f0-9]{40}$")
REF = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._/-]{0,120}$")
MAX_ENTRIES = 20000
MAX_HISTORY_PAGES = 5


class ExplorerError(ValueError):
    pass


def safe_path(path, *, allow_root=True):
    value = str(path or "").strip()
    if value in ("", "/") and allow_root:
        return ""
    if (not value or len(value) > 220 or value.startswith("/")
            or any(part in ("", ".", "..") for part in value.split("/"))
            or re.search(r"[\x00-\x1f\\?#%*{}\[\]<>|]", value)):
        raise ExplorerError("Invalid relative GitHub path")
    return value


def safe_branch(ref):
    value = str(ref or "").strip()
    if not REF.fullmatch(value) or any(part in ("", ".", "..") for part in value.split("/")):
        raise ExplorerError("Invalid GitHub branch or ref")
    return value


def pinned_tree(api, token, repo, branch):
    branch = safe_branch(branch)
    revision = api(token, "/repos/" + repo + "/commits/" + quote(branch, safe=""))
    sha = revision.get("sha") if isinstance(revision, dict) else None
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ExplorerError("Source revision cannot be verified")
    body = api(token, "/repos/" + repo + "/git/trees/" + sha + "?recursive=1")
    if not isinstance(body, dict) or not isinstance(body.get("tree"), list):
        raise ExplorerError("Repository tree could not be verified")
    rows = body["tree"]
    complete = not body.get("truncated") and len(rows) <= MAX_ENTRIES
    if not complete:
        raise ExplorerError("Repository tree is incomplete; cannot report exact totals")
    items = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        kind = item.get("type")
        if not isinstance(path, str) or len(path) > 220 or kind not in ("blob", "tree"):
            continue
        try:
            safe_path(path, allow_root=False)
        except ExplorerError:
            continue
        size = item.get("size")
        items.append({"path": path, "type": "file" if kind == "blob" else "dir",
                      "sizeBytes": max(0, int(size or 0)) if kind == "blob" and isinstance(size, (int, float)) else None,
                      "sha": str(item.get("sha") or "") if SHA.fullmatch(str(item.get("sha") or "")) else ""})
    return {"repository": repo, "branch": branch, "sourceSha": sha,
            "complete": True, "items": items}


def scope_stats(snapshot, path=""):
    root = safe_path(path)
    entries = snapshot["items"]
    if root and not any(x["path"] == root and x["type"] == "dir" for x in entries):
        raise ExplorerError("Directory not present in verified source tree")
    prefix = root + "/" if root else ""
    contained = [x for x in entries if x["path"].startswith(prefix)]
    files = [x for x in contained if x["type"] == "file"]
    dirs = [x for x in contained if x["type"] == "dir"]
    measured = [x["sizeBytes"] for x in files if isinstance(x["sizeBytes"], int)]
    known = len(measured) == len(files)
    return {"path": root, "recursiveFiles": len(files), "recursiveDirectories": len(dirs),
            "gitBlobBytes": sum(measured) if known else None,
            "sizeComplete": known}


def directory(snapshot, path=""):
    root = safe_path(path)
    stats = scope_stats(snapshot, root)
    prefix = root + "/" if root else ""
    candidates = [x for x in snapshot["items"] if x["path"].startswith(prefix)]
    children = [x for x in candidates if "/" not in x["path"][len(prefix):]]
    enriched = []
    for child in children:
        if child["type"] == "dir":
            sub = scope_stats(snapshot, child["path"])
            enriched.append({**child, "name": child["path"].split("/")[-1],
                             "sizeBytes": sub["gitBlobBytes"],
                             "sizeComplete": sub["sizeComplete"],
                             "fileCount": sub["recursiveFiles"], "directoryCount": sub["recursiveDirectories"]})
        else:
            enriched.append({**child, "name": child["path"].split("/")[-1],
                             "sizeComplete": isinstance(child["sizeBytes"], int),
                             "fileCount": None, "directoryCount": None})
    enriched.sort(key=lambda x: (x["type"] != "dir", x["name"].casefold(), x["path"]))
    return {key: snapshot[key] for key in ("repository", "branch", "sourceSha", "complete")} | {
        "path": root, "stats": stats, "entries": enriched,
        "count": len(enriched), "measuredAtSource": True,
        "sizeLabel": "Git blob bytes, excluding Git history, Git LFS payloads and checkout overhead"}


def find_files(snapshot, term, path="", limit=50):
    scope = safe_path(path)
    term = str(term or "").strip().casefold()
    if len(term) < 2 or len(term) > 100 or re.search(r"[\x00-\x1f\\?#%*{}\[\]<>|]", term):
        raise ExplorerError("Search requires a valid filename term (2–100 characters)")
    prefix = scope + "/" if scope else ""
    found = [x for x in snapshot["items"] if x["type"] == "file"
             and x["path"].startswith(prefix)
             and (term in x["path"].split("/")[-1].casefold() or term in x["path"].casefold())]
    found.sort(key=lambda x: (term not in x["path"].split("/")[-1].casefold(), x["path"].casefold()))
    return {"repository": snapshot["repository"], "branch": snapshot["branch"], "sourceSha": snapshot["sourceSha"],
            "query": term, "path": scope, "total": len(found), "truncatedResults": len(found) > limit,
            "matches": found[:limit]}


def history(api, token, repo, branch, path):
    path = safe_path(path, allow_root=False)
    branch = safe_branch(branch)
    records = []
    fully_scanned = False
    for page in range(1, MAX_HISTORY_PAGES + 1):
        route = ("/repos/" + repo + "/commits?sha=" + quote(branch, safe="") +
                 "&path=" + quote(path, safe="") + "&per_page=100&page=" + str(page))
        chunk = api(token, route)
        if not isinstance(chunk, list):
            raise ExplorerError("GitHub did not return a commit history list")
        for item in chunk:
            commit = item.get("commit") if isinstance(item, dict) else None
            if not isinstance(commit, dict):
                continue
            person = commit.get("committer") or commit.get("author") or {}
            date = person.get("date") if isinstance(person, dict) else None
            ident = str(item.get("sha") or "")
            if SHA.fullmatch(ident):
                records.append({"sha": ident, "date": str(date or "")[:40],
                                "summary": str(commit.get("message") or "").split("\n")[0][:240]})
        if len(chunk) < 100:
            fully_scanned = True
            break
    return {"repository": repo, "branch": branch, "path": path,
            "lastCommit": records[0] if records else None,
            "firstSeenPathCommit": records[-1] if records and fully_scanned else None,
            "firstSeenComplete": fully_scanned, "commitsScanned": len(records),
            "caution": "Git path history is not a filesystem creation timestamp; renames may hide earlier history."}


def comparison(api, token, repo, base, head):
    base = safe_branch(base)
    head = safe_branch(head)
    record = api(token, "/repos/" + repo + "/compare/" + quote(base, safe="") +
                 "..." + quote(head, safe="") + "?per_page=30")
    if not isinstance(record, dict) or not isinstance(record.get("files"), list):
        raise ExplorerError("GitHub did not return a verifiable comparison")
    files = []
    for entry in record["files"][:30]:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("filename") or "")[:220]
        try:
            safe_path(name, allow_root=False)
        except ExplorerError:
            continue
        files.append({"path": name, "status": str(entry.get("status") or "")[:40],
                      "additions": int(entry.get("additions") or 0),
                      "deletions": int(entry.get("deletions") or 0),
                      "patch": str(entry.get("patch") or "")[:10000]})
    return {"repository": repo, "base": base, "head": head,
            "baseSha": str((record.get("base_commit") or {}).get("sha") or ""),
            "headSha": str((record.get("head_commit") or {}).get("sha") or ""),
            "totalCommits": int(record.get("total_commits") or 0),
            "files": files, "partial": len(record["files"]) >= 30,
            "caution": "Up to 30 files and 10,000 patch characters each; not a complete merge review."}
