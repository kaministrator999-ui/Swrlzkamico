"""Owner-confirmed, atomic GitHub file rename/move (single Git tree commit).

Only the currently selected, verified public owner repo and its default branch
are eligible. A proposal pins current HEAD, source blob and target path. A
separate confirmation creates one new tree+commit and advances one ref with
force=False; no intermediate create/delete commits and no overwrite of target.
"""
from __future__ import annotations
import re
import secrets
import threading
import time
from urllib.parse import quote

import requests
from github_general_create_v262 import _authorize, safe_path, CreateFileError

MAX_TREE_ENTRIES = 20000
TICKET_SECONDS = 300
SHA = re.compile(r"[0-9a-fA-F]{40}\Z")
SCOPED_MODE = {"100644", "100755", "120000"}
_pending = {}
_lock = threading.RLock()


def _api(auth, method, endpoint, body=None):
    """GitHub Git database API. Endpoints built from checked refs and SHA only."""
    if not endpoint.startswith("/repos/" + auth["repo"] + "/git/") or ".." in endpoint:
        raise CreateFileError("INVALID_GIT_ENDPOINT", 500)
    url = "https://api.github.com" + endpoint
    headers = {
        "Authorization": "Bearer " + auth["token"],
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "swrlz-owner-confirmed-rename-v263",
    }
    try:
        response = requests.request(method, url, headers=headers, json=body, timeout=25)
        if response.status_code in (409, 412, 422):
            raise CreateFileError("GITHUB_RENAME_CONFLICT_OR_PROTECTION", 409)
        if response.status_code in (401, 403, 404):
            raise CreateFileError("GITHUB_RENAME_ACCESS_UNAVAILABLE", response.status_code)
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict):
            raise ValueError("Expected a GitHub object")
        return result
    except CreateFileError:
        raise
    except (requests.RequestException, ValueError):
        raise CreateFileError("GITHUB_API_UNAVAILABLE", 502) from None


def _git_endpoint(auth, suffix):
    # Repository identity is an exact server-authorized owner/repo value.
    return "/repos/" + auth["repo"] + "/git/" + suffix


def _head(auth):
    ref = _api(auth, "GET", _git_endpoint(auth, "ref/heads/" + quote(auth["branch"], safe="/")))
    obj = ref.get("object") if isinstance(ref.get("object"), dict) else {}
    sha = obj.get("sha")
    if obj.get("type") != "commit" or not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise CreateFileError("GITHUB_HEAD_NOT_VERIFIED", 502)
    commit = _api(auth, "GET", _git_endpoint(auth, "commits/" + sha))
    root = commit.get("tree") if isinstance(commit.get("tree"), dict) else {}
    tree_sha = root.get("sha")
    if commit.get("sha") != sha or not isinstance(tree_sha, str) or not SHA.fullmatch(tree_sha):
        raise CreateFileError("GITHUB_TREE_NOT_VERIFIED", 502)
    return sha, tree_sha


def _tree(auth, root_sha):
    obj = _api(auth, "GET", _git_endpoint(auth, "trees/" + root_sha + "?recursive=1"))
    records = obj.get("tree")
    if (obj.get("sha") != root_sha or obj.get("truncated") is True
            or not isinstance(records, list) or len(records) > MAX_TREE_ENTRIES):
        raise CreateFileError("GITHUB_TREE_UNAVAILABLE_OR_TRUNCATED", 409)
    result = {}
    for item in records:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise CreateFileError("GITHUB_TREE_MALFORMED", 502)
        result[item["path"]] = item
    return result


def _permission_for_workflows(user_id, paths):
    if not any(p.startswith(".github/workflows/") for p in paths):
        return
    from github_connection import _config, _load
    record = _load(_config(), user_id)
    scopes = set(re.split(r"[\s,]+", str((record or {}).get("scopes") or "").strip()))
    if "workflow" not in scopes:
        raise CreateFileError("GITHUB_WORKFLOW_SCOPE_REQUIRED", 403)


def _checked_source(entries, old, new):
    original = entries.get(old)
    if original is None:
        raise CreateFileError("SOURCE_FILE_NOT_FOUND", 404)
    if original.get("type") != "blob" or str(original.get("mode")) not in SCOPED_MODE:
        raise CreateFileError("SOURCE_IS_NOT_A_RENAMABLE_FILE", 422)
    blob = original.get("sha")
    if not isinstance(blob, str) or not SHA.fullmatch(blob):
        raise CreateFileError("SOURCE_BLOB_NOT_VERIFIED", 502)
    if new in entries:
        raise CreateFileError("DESTINATION_ALREADY_EXISTS", 409)
    for i in range(1, len(new.split("/"))):
        parent = "/".join(new.split("/")[:i])
        record = entries.get(parent)
        if record is not None and record.get("type") != "tree":
            raise CreateFileError("DESTINATION_PARENT_NOT_DIRECTORY", 409)
    # A file cannot move inside a directory that has the same source name.
    if new.startswith(old + "/"):
        raise CreateFileError("DESTINATION_INSIDE_SOURCE_FILE", 422)
    return original


def prepare(user_id, source_path, destination_path):
    auth = _authorize(user_id)
    old = safe_path(source_path)
    new = safe_path(destination_path)
    if old == new:
        raise CreateFileError("SOURCE_AND_DESTINATION_IDENTICAL", 422)
    _permission_for_workflows(user_id, (old, new))
    head_sha, root_sha = _head(auth)
    entries = _tree(auth, root_sha)
    source = _checked_source(entries, old, new)
    ticket = secrets.token_urlsafe(32)
    now = time.monotonic()
    with _lock:
        for key, value in list(_pending.items()):
            if value["expires"] <= now:
                _pending.pop(key, None)
        _pending[ticket] = {
            "userId": user_id, "repo": auth["repo"], "branch": auth["branch"],
            "source": old, "destination": new, "head": head_sha,
            "tree": root_sha, "blob": source["sha"], "mode": source["mode"],
            "size": source.get("size"), "expires": now + TICKET_SECONDS,
        }
    return {
        "approvalToken": ticket, "expiresInSeconds": TICKET_SECONDS,
        "operation": "RENAME_FILE", "repo": auth["repo"], "branch": auth["branch"],
        "sourcePath": old, "destinationPath": new, "sourceBlobSha": source["sha"],
        "sourceMode": source["mode"], "bytes": source.get("size"),
        "headSha": head_sha, "overwrite": False, "atomic": True,
    }


def confirm(user_id, approval_token, approved):
    with _lock:
        item = _pending.get(approval_token) if isinstance(approval_token, str) else None
        if not item or item["expires"] <= time.monotonic() or item["userId"] != user_id:
            raise CreateFileError("APPROVAL_EXPIRED_OR_WRONG_ACCOUNT", 403)
        _pending.pop(approval_token, None)
    if approved is not True:
        return {"ok": False, "code": "USER_DECLINED"}
    auth = _authorize(user_id, item["repo"])
    if auth["branch"] != item["branch"]:
        raise CreateFileError("DEFAULT_BRANCH_CHANGED", 409)
    _permission_for_workflows(user_id, (item["source"], item["destination"]))
    current_head, current_tree = _head(auth)
    if current_head != item["head"] or current_tree != item["tree"]:
        raise CreateFileError("REPOSITORY_CHANGED_REPREPARE_REQUIRED", 409)
    # An exact revision comparison plus a single parented commit ensures that
    # an intervening HEAD advance is rejected by GitHub's non-force ref update.
    updated = _api(auth, "POST", _git_endpoint(auth, "trees"), {
        "base_tree": item["tree"],
        "tree": [
            {"path": item["source"], "mode": item["mode"], "type": "blob", "sha": None},
            {"path": item["destination"], "mode": item["mode"], "type": "blob", "sha": item["blob"]},
        ],
    })
    new_tree_sha = updated.get("sha")
    if not isinstance(new_tree_sha, str) or not SHA.fullmatch(new_tree_sha) or new_tree_sha == item["tree"]:
        raise CreateFileError("GITHUB_RENAME_TREE_NOT_VERIFIED", 502)
    commit = _api(auth, "POST", _git_endpoint(auth, "commits"), {
        "message": "refactor(files): rename " + item["source"] + " to " + item["destination"],
        "tree": new_tree_sha,
        "parents": [item["head"]],
    })
    commit_sha = commit.get("sha")
    if not isinstance(commit_sha, str) or not SHA.fullmatch(commit_sha):
        raise CreateFileError("GITHUB_RENAME_COMMIT_NOT_VERIFIED", 502)
    # force:false does NOT overwrite another collaborator's newer HEAD.
    _api(auth, "PATCH", _git_endpoint(auth, "refs/heads/" + quote(auth["branch"], safe="/")), {
        "sha": commit_sha, "force": False,
    })
    final_head, final_tree = _head(auth)
    if final_head != commit_sha or final_tree != new_tree_sha:
        raise CreateFileError("RENAME_POST_COMMIT_VERIFICATION_INCONCLUSIVE", 502)
    final_files = _tree(auth, final_tree)
    target = final_files.get(item["destination"])
    if (item["source"] in final_files or not isinstance(target, dict)
            or target.get("type") != "blob"
            or target.get("sha") != item["blob"]
            or target.get("mode") != item["mode"]):
        raise CreateFileError("RENAME_POST_COMMIT_BLOB_MISMATCH", 502)
    return {
        "ok": True, "verified": True, "operation": "RENAME_FILE",
        "repo": auth["repo"], "branch": auth["branch"],
        "sourcePath": item["source"], "destinationPath": item["destination"],
        "blobSha": item["blob"], "mode": item["mode"], "bytes": item["size"],
        "commitSha": commit_sha,
        "url": "https://github.com/" + auth["repo"] + "/blob/" +
               quote(auth["branch"], safe="/") + "/" + quote(item["destination"], safe="/"),
        "commitUrl": "https://github.com/" + auth["repo"] + "/commit/" + commit_sha,
        "atomic": True, "overwrite": False,
    }
