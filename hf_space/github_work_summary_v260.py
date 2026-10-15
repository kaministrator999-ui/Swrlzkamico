"""Provenance-bounded GitHub work receipt for Chat visualization.

The successful sandbox action is authoritative for creation + byte verification.
Repository-level and GitHub commit diff statistics are optional independent
provider evidence; they are never invented on metadata/network failures.
"""
from __future__ import annotations
from datetime import datetime
import re


def make_work_widget(receipt, content, token, github_get=None):
    if not isinstance(receipt, dict) or receipt.get("verified") is not True or receipt.get("operation") != "CREATE_FILE":
        raise ValueError("Verified GitHub CREATE_FILE receipt required")
    repo = "kaministrator999-ui/Swrlzing-core"
    prefix = "write-action-tests/"
    path = receipt.get("path")
    sha = receipt.get("commitSha")
    if (receipt.get("repo") != repo or receipt.get("branch") != "main"
            or not isinstance(path, str) or not re.fullmatch(
                r"write-action-tests/[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.txt", path)
            or ".." in path or not isinstance(content, str) or not content
            or not isinstance(sha, str) or not sha):
        raise ValueError("GitHub receipt out of bounded scope")
    data = {
        "operation": "CREATE_FILE",
        "repo": repo,
        "branch": "main",
        "path": path,
        "commitSha": sha[:40],
        "fileUrl": "https://github.com/" + repo + "/blob/main/" + path,
        "commitUrl": ("https://github.com/" + repo + "/commit/" + sha
                      if re.fullmatch(r"[0-9a-fA-F]{40}", sha) else None),
        "verification": "EXACT_BYTES_MATCHED",
        "bytesWritten": len(content.encode("utf-8")),
        "textLines": len(content.splitlines()),
        "filesCreated": 1,
        "filesOverwritten": 0,
        "providerStatsAvailable": False,
    }
    if github_get is not None and re.fullmatch(r"[0-9a-fA-F]{40}", sha):
        try:
            obj = github_get(token, "/repos/" + repo + "/commits/" + sha)
            matches = [f for f in obj.get("files", []) if isinstance(f, dict)
                       and f.get("filename") == path and f.get("status") == "added"]
            if isinstance(obj, dict) and str(obj.get("sha") or "").lower() == sha.lower() and len(matches) == 1:
                f = matches[0]
                if (all(isinstance(f.get(k), int) and f[k] >= 0
                        for k in ("additions", "deletions", "changes")) and f["deletions"] == 0):
                    data["providerStatsAvailable"] = True
                    data["additions"] = f["additions"]
                    data["deletions"] = f["deletions"]
                    data["filesChanged"] = len(obj.get("files", []))
                    data["commitVerifiedByProvider"] = True
                    meta = obj.get("commit") if isinstance(obj.get("commit"), dict) else {}
                    info = meta.get("committer") if isinstance(meta.get("committer"), dict) else {}
                    timestamp = str(info.get("date") or "")
                    try:
                        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        data["commitAt"] = timestamp[:35]
                    except ValueError:
                        pass
        except Exception:
            pass  # Verified create/read-back remains true; stats are unavailable.
    return {"contract": "swrlz-widget-v1", "kind": "github-work",
            "title": "GitHub work · file created", "provider": "GitHub",
            "data": data}



def make_general_work_widget(receipt, raw_bytes, token, github_get=None):
    """Owner-repo CREATE_FILE receipt for source, extensionless and binary files."""
    from urllib.parse import quote
    from github_general_create_v262 import ALLOWED_REPOS, safe_path
    if not isinstance(receipt, dict) or receipt.get("verified") is not True or receipt.get("operation") != "CREATE_FILE":
        raise ValueError("Verified GitHub CREATE_FILE required")
    repo = receipt.get("repo")
    branch = receipt.get("branch")
    filename = receipt.get("path")
    sha = receipt.get("commitSha")
    if (repo not in ALLOWED_REPOS or not isinstance(branch, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,99}", branch)
            or ".." in branch or not isinstance(sha, str)
            or not re.fullmatch(r"[0-9a-fA-F]{40}", sha)
            or not isinstance(raw_bytes, bytes)):
        raise ValueError("Untrusted GitHub work receipt")
    filename = safe_path(filename)
    data = {
        "repo": repo, "branch": branch, "path": filename,
        "commitSha": sha, "operation": "CREATE_FILE",
        "fileUrl": "https://github.com/" + repo + "/blob/" + quote(branch, safe="/") + "/" + quote(filename, safe="/"),
        "commitUrl": "https://github.com/" + repo + "/commit/" + sha,
        "verification": "EXACT_BYTES_MATCHED",
        "bytesWritten": len(raw_bytes), "filesCreated": 1,
        "filesOverwritten": 0, "providerStatsAvailable": False,
    }
    media = str(receipt.get("mediaType") or "")
    if media.startswith("text/") or filename.lower().endswith((".py", ".json", ".js", ".ts", ".md", ".css", ".html", ".yml", ".yaml", ".xml", ".csv")):
        try:
            data["textLines"] = len(raw_bytes.decode("utf-8").splitlines())
        except UnicodeDecodeError:
            pass
    if github_get is not None:
        try:
            obj = github_get(token, "/repos/" + repo + "/commits/" + sha)
            files = obj.get("files") if isinstance(obj, dict) else None
            matching = [file for file in files if isinstance(file, dict)
                        and file.get("filename") == filename and file.get("status") == "added"] if isinstance(files, list) else []
            if (obj.get("sha") == sha and len(matching) == 1
                    and isinstance(matching[0].get("additions"), int)
                    and isinstance(matching[0].get("deletions"), int)
                    and matching[0]["additions"] >= 0 and matching[0]["deletions"] == 0):
                data["providerStatsAvailable"] = True
                data["additions"] = matching[0]["additions"]
                data["deletions"] = 0
                data["filesChanged"] = len(files)
                meta = obj.get("commit") if isinstance(obj.get("commit"), dict) else {}
                committer = meta.get("committer") if isinstance(meta.get("committer"), dict) else {}
                date = committer.get("date")
                if isinstance(date, str):
                    try:
                        datetime.fromisoformat(date.replace("Z", "+00:00"))
                        data["commitAt"] = date[:35]
                    except ValueError:
                        pass
        except Exception:
            pass
    return {"contract": "swrlz-widget-v1", "kind": "github-work",
            "title": "GitHub work · file created", "provider": "GitHub", "data": data}
