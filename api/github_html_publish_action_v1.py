"""Owner-authenticated, commit-pinned §C HTML project deployment proposals.

Never publish from model text. OAuth identifies the existing repository owner,
a one-time same-thread Yes/No approves a specific project and immutable SHA,
and GitHub Actions (not the chat server) owns the Hugging Face deploy secret.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import threading
import time
from urllib.parse import quote

import requests
import github_general_create_v262 as github

REPO = "kaministrator999-ui/Swrlzkamico"
WORKFLOW = "hf-html-project-publish-v1.yml"
SPACE_URL = "https://kamiloki-swyrlz.hf.space"
WORKFLOW_URL = "https://github.com/" + REPO + "/actions/workflows/" + WORKFLOW
COMMAND = re.compile(
    r"^\s*@github\s+(publish|deploy|status)\s+(?:html\s+)?project\s+"
    r"([a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?)\s*[.!]?\s*$", re.I)
SAFE_PART = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
ALLOWED = frozenset((".html", ".htm", ".css", ".js", ".mjs", ".json", ".svg",
                     ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2"))
MAX_FILES = 48
MAX_BYTES = 1_000_000
TTL = 300
_lock = threading.RLock()
_pending = {}


class PublishActionError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def command(prompt):
    if not isinstance(prompt, str) or len(prompt) > 500:
        return None
    match = COMMAND.fullmatch(prompt)
    return (match.group(1).lower(), match.group(2).lower()) if match else None


def is_request(prompt):
    return command(prompt) is not None


def _url(slug):
    return SPACE_URL + "/api/html-projects/" + slug + "/index.html"


def _github(auth, method, path, *, params=None, data=None):
    headers = {
        "Authorization": "Bearer " + auth["token"],
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "SWRLZ-Owner-HTML-Publish/1",
    }
    try:
        response = requests.request(
            method, "https://api.github.com/repos/" + REPO + "/" + path,
            headers=headers, params=params, json=data, timeout=22)
    except requests.RequestException as exc:
        raise PublishActionError("GITHUB_UNAVAILABLE") from exc
    if response.status_code in (401, 403):
        raise PublishActionError("GITHUB_ACTIONS_PERMISSION_REQUIRED")
    if response.status_code == 404:
        raise PublishActionError("GITHUB_RESOURCE_NOT_FOUND")
    if response.status_code >= 400:
        raise PublishActionError("GITHUB_REQUEST_FAILED_" + str(response.status_code))
    if response.status_code == 204:
        return None
    try:
        return response.json()
    except ValueError as exc:
        raise PublishActionError("GITHUB_RESPONSE_INVALID") from exc


def _authorized(user_id):
    try:
        auth = github._authorize(user_id, REPO)
    except github.CreateFileError as exc:
        raise PublishActionError(str(exc.code)) from None
    if auth["repo"] != REPO or auth["branch"] != "main":
        raise PublishActionError("EXPECTED_OWNER_MAIN_REPOSITORY")
    return auth


def _head(auth):
    info = _github(auth, "GET", "branches/" + quote(auth["branch"], safe=""))
    sha = str((info.get("commit") or {}).get("sha") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise PublishActionError("GITHUB_HEAD_UNVERIFIED")
    return sha


def _manifest(auth, sha, slug):
    commit = _github(auth, "GET", "git/commits/" + sha)
    tree_sha = str((commit.get("tree") or {}).get("sha") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", tree_sha):
        raise PublishActionError("GITHUB_TREE_UNVERIFIED")
    tree = _github(auth, "GET", "git/trees/" + tree_sha, params={"recursive": "1"})
    if not isinstance(tree, dict) or tree.get("truncated") is not False:
        raise PublishActionError("GITHUB_TREE_UNAVAILABLE")
    prefix = "html-projects/" + slug + "/"
    files = []
    total = 0
    for entry in tree.get("tree") or []:
        path = str(entry.get("path") or "")
        if not path.startswith(prefix):
            continue
        rel = path[len(prefix):]
        if entry.get("type") != "blob":
            continue
        if entry.get("mode") == "120000":
            raise PublishActionError("PROJECT_SYMLINK_FORBIDDEN")
        parts = rel.split("/")
        if (len(parts) > 8 or not all(
                part and not part.startswith(".") and SAFE_PART.fullmatch(part)
                for part in parts)
                or "." not in parts[-1]
                or "." + parts[-1].rsplit(".", 1)[-1].lower() not in ALLOWED):
            raise PublishActionError("PROJECT_PATH_NOT_PUBLISHABLE")
        size = entry.get("size")
        if type(size) is not int or size < 0:
            raise PublishActionError("PROJECT_SIZE_UNVERIFIED")
        total += size
        files.append({"path": rel, "bytes": size})
        if total > MAX_BYTES or len(files) > MAX_FILES:
            raise PublishActionError("PROJECT_EXCEEDS_LIMIT")
    if not any(entry["path"] == "index.html" for entry in files):
        raise PublishActionError("PROJECT_INDEX_HTML_MISSING")
    index_entry = next((item for item in (tree.get("tree") or [])
                        if item.get("path") == prefix + "index.html" and
                           item.get("type") == "blob"), None)
    index_sha = str((index_entry or {}).get("sha") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{40}", index_sha):
        raise PublishActionError("PROJECT_INDEX_BLOB_UNVERIFIED")
    return {"repo": REPO, "branch": auth["branch"], "project": slug, "sourceSha": sha,
            "files": sorted(files, key=lambda x: x["path"]), "bytes": total,
            "indexGitBlobSha": index_sha,
            "url": _url(slug), "workflowUrl": WORKFLOW_URL,
            "destinationPrefix": "published-html-projects/" + slug + "/"}


def expire(user_id, thread_id):
    with _lock:
        _pending.pop((user_id, thread_id), None)


def has_pending(user_id, thread_id):
    with _lock:
        entry = _pending.get((user_id, thread_id))
        if entry and entry["expires"] > time.monotonic():
            return True
        _pending.pop((user_id, thread_id), None)
    return False


def prepare(user_id, thread_id, slug):
    auth = _authorized(user_id)
    sha = _head(auth)
    preview = _manifest(auth, sha, slug)
    with _lock:
        ticket = secrets.token_urlsafe(24)
        _pending[(user_id, thread_id)] = {
            "token": ticket, "sha": sha, "project": slug,
            "expires": time.monotonic() + TTL,
        }
    return {**preview, "expiresInSeconds": TTL}


def confirm(user_id, thread_id, approved):
    if type(approved) is not bool:
        raise PublishActionError("EXPLICIT_BOOLEAN_REQUIRED")
    with _lock:
        pending = _pending.pop((user_id, thread_id), None)
    if not pending or pending["expires"] <= time.monotonic():
        raise PublishActionError("APPROVAL_EXPIRED")
    if not approved:
        return {"approved": False, "dispatched": False}
    auth = _authorized(user_id)
    if _head(auth) != pending["sha"]:
        raise PublishActionError("SOURCE_CHANGED_REPREPARE")
    # The one-time owner confirmation is consumed before network dispatch.
    _github(auth, "POST", "actions/workflows/" + WORKFLOW + "/dispatches",
            data={"ref": auth["branch"], "inputs": {
                "source_sha": pending["sha"],
                "project": pending["project"],
                "approved": "yes",
            }})
    return {
        "approved": True, "dispatched": True, "project": pending["project"],
        "sourceSha": pending["sha"], "url": _url(pending["project"]),
        "workflowUrl": WORKFLOW_URL,
    }


def status(user_id, slug):
    auth = _authorized(user_id)
    data = _github(auth, "GET", "actions/workflows/" + WORKFLOW + "/runs",
                   params={"event": "workflow_dispatch", "per_page": "50"})
    selected = None
    for run in data.get("workflow_runs") or []:
        title = str(run.get("display_title") or "")
        if re.fullmatch(r"HTML " + re.escape(slug) + r" \u00b7 [0-9a-f]{40}", title):
            selected = run
            break
    if selected is None:
        return {"project": slug, "status": "unobserved", "verified": False,
                "workflowUrl": WORKFLOW_URL, "url": _url(slug)}
    state = str(selected.get("status") or "unknown")
    conclusion = str(selected.get("conclusion") or "")
    run_url = str(selected.get("html_url") or WORKFLOW_URL)
    result = {"project": slug, "status": state, "conclusion": conclusion,
              "verified": False, "runUrl": run_url, "url": _url(slug)}
    if state != "completed" or conclusion != "success":
        return result
    match = re.fullmatch(r"HTML " + re.escape(slug) + r" \u00b7 ([0-9a-f]{40})",
                         str(selected.get("display_title") or ""))
    sha = match.group(1)
    file = _github(auth, "GET",
                   "contents/html-projects/" + quote(slug, safe="") + "/index.html",
                   params={"ref": sha})
    if file.get("encoding") != "base64":
        raise PublishActionError("SOURCE_BYTES_UNAVAILABLE")
    try:
        expected = base64.b64decode(str(file["content"]).replace("\n", ""), validate=True)
        response = requests.get(_url(slug), timeout=20, headers={"Cache-Control": "no-cache"})
    except (ValueError, KeyError, requests.RequestException) as exc:
        raise PublishActionError("LIVE_VERIFICATION_UNAVAILABLE") from exc
    csp = response.headers.get("Content-Security-Policy", "")
    result["verified"] = (
        response.status_code == 200 and response.content == expected
        and "sandbox allow-scripts" in csp and "allow-same-origin" not in csp
        and "connect-src 'none'" in csp
        and response.headers.get("X-Content-Type-Options", "").lower() == "nosniff")
    if result["verified"]:
        result["sourceSha"] = sha
        result["sha256"] = hashlib.sha256(expected).hexdigest()
    return result
