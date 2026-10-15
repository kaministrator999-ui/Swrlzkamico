"""Conservative GitHub RENAME_FILE receipt for a verified atomic commit."""
from __future__ import annotations
import re
from urllib.parse import quote
from github_general_create_v262 import ALLOWED_REPOS, safe_path

def make_rename_widget(receipt):
    if not isinstance(receipt, dict) or receipt.get("operation") != "RENAME_FILE" or receipt.get("verified") is not True or receipt.get("atomic") is not True:
        raise ValueError("Verified atomic rename required")
    repo, branch = receipt.get("repo"), receipt.get("branch")
    sha, blob = receipt.get("commitSha"), receipt.get("blobSha")
    source, target = safe_path(receipt.get("sourcePath")), safe_path(receipt.get("destinationPath"))
    if (repo not in ALLOWED_REPOS or not isinstance(branch, str) or
        not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,99}", branch) or
        any(seg in (".", "..", "") for seg in branch.split("/")) or
        not isinstance(sha, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", sha) or
        not isinstance(blob, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", blob) or
        source == target or receipt.get("overwrite") is not False):
        raise ValueError("Invalid GitHub rename receipt")
    data = {
        "operation": "RENAME_FILE", "repo": repo, "branch": branch,
        "sourcePath": source, "destinationPath": target,
        "fileUrl": "https://github.com/" + repo + "/blob/" + quote(branch, safe="/") + "/" + quote(target, safe="/"),
        "commitSha": sha, "commitUrl": "https://github.com/" + repo + "/commit/" + sha,
        "blobSha": blob, "verification": "IDENTICAL_BLOB_AND_MODE",
        "filesRenamed": 1, "overwritten": 0, "atomic": True,
    }
    if isinstance(receipt.get("bytes"), int) and receipt["bytes"] >= 0:
        data["bytesPreserved"] = receipt["bytes"]
    if receipt.get("mode") in ("100644", "100755", "120000"):
        data["gitMode"] = receipt["mode"]
    return {"contract": "swrlz-widget-v1", "kind": "github-rename",
            "title": "GitHub · File renamed", "provider": "GitHub", "data": data}
