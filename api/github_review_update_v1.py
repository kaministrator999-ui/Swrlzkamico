"""Owner-confirmed, SHA-bound UPDATE_FILE for the current §C GitHub connection.

No model text or widget can authorize a write. GitHub OAuth is checked both
when preparing and when confirming. The original Git blob must still match.
"""
from __future__ import annotations
import base64
import binascii
import difflib
import hashlib
import re
import secrets
import threading
import time
import requests
from urllib.parse import quote

from github_general_create_v262 import CreateFileError, safe_path
import github_general_create_v262 as create

_TTL = 300
_MAX = 260_000
_lock = threading.Lock()
_pending = {}


def _read(auth, path):
    status, response = create._github("GET", auth, path)
    if status != 200 or not isinstance(response, dict):
        raise CreateFileError("FILE_TO_EDIT_NOT_FOUND", 404)
    sha = str(response.get("sha") or "")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
        raise CreateFileError("GITHUB_BLOB_SHA_UNAVAILABLE", 409)
    if response.get("type") != "file" or response.get("encoding") != "base64":
        raise CreateFileError("GITHUB_TEXT_FILE_REQUIRED", 422)
    try:
        raw = base64.b64decode(str(response["content"]).replace("\n", ""), validate=True)
        text = raw.decode("utf-8")
    except (KeyError, ValueError, UnicodeDecodeError, binascii.Error):
        raise CreateFileError("GITHUB_TEXT_FILE_REQUIRED", 422) from None
    if len(raw) > _MAX:
        raise CreateFileError("FILE_TOO_LARGE_FOR_REVIEW", 413)
    return sha.lower(), text


def prepare(user_id, path, content):
    auth = create._authorize(user_id)
    path = safe_path(path)
    if not isinstance(content, str) or not content or len(content.encode("utf-8")) > _MAX:
        raise CreateFileError("INVALID_EDIT_CONTENT", 422)
    sha, before = _read(auth, path)
    after_bytes = content.encode("utf-8")
    digest = hashlib.sha256(after_bytes).hexdigest()
    with _lock:
        now = time.monotonic()
        for key, item in list(_pending.items()):
            if item["expires"] <= now:
                del _pending[key]
        ticket = secrets.token_urlsafe(32)
        _pending[ticket] = {
            "userId": user_id, "repo": auth["repo"], "branch": auth["branch"],
            "path": path, "sha": sha, "content": after_bytes,
            "digest": digest, "expires": now + _TTL,
        }
    diff = "".join(difflib.unified_diff(
        before.splitlines(True), content.splitlines(True),
        fromfile="before/" + path, tofile="after/" + path))
    return {
        "approvalToken": ticket, "operation": "UPDATE_FILE",
        "repo": auth["repo"], "branch": auth["branch"], "path": path,
        "before": before, "content": content, "diff": diff,
        "expectedBlobSha": sha, "sha256": digest,
        "bytes": len(after_bytes), "expiresInSeconds": _TTL,
    }


def confirm(user_id, approval_token, approved):
    if not isinstance(approval_token, str) or type(approved) is not bool:
        raise CreateFileError("INVALID_APPROVAL", 422)
    with _lock:
        item = _pending.get(approval_token)
        if not item or item["userId"] != user_id or item["expires"] <= time.monotonic():
            raise CreateFileError("APPROVAL_EXPIRED_OR_WRONG_ACCOUNT", 403)
        del _pending[approval_token]  # Single use, consumed before first network call.
    if not approved:
        return {"ok": False, "code": "USER_DECLINED"}
    auth = create._authorize(user_id, item["repo"])
    if auth["branch"] != item["branch"]:
        raise CreateFileError("DEFAULT_BRANCH_CHANGED", 409)
    sha, _ = _read(auth, item["path"])
    if sha != item["sha"]:
        raise CreateFileError("SOURCE_CHANGED_SINCE_PREVIEW", 409)
    status, response = create._github("PUT", auth, item["path"], {
        "message": "feat(files): owner-approved UPDATE_FILE " + item["path"][-100:],
        "branch": auth["branch"],
        "content": base64.b64encode(item["content"]).decode("ascii"),
        "sha": item["sha"],
    })
    if status != 200:
        raise CreateFileError("GITHUB_UPDATE_NOT_CONFIRMED", 502)
    commit = str((response or {}).get("commit", {}).get("sha") or "")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise CreateFileError("GITHUB_COMMIT_NOT_VERIFIED", 502)
    # GitHub's successful PUT includes the committed blob SHA. Validate that
    # immutable object first; the branch contents endpoint can lag after PUT.
    content_meta = (response or {}).get("content") or {}
    written_sha = str(content_meta.get("sha") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{40}", written_sha):
        raise CreateFileError("GITHUB_BLOB_SHA_UNAVAILABLE", 502)
    blob_url = ("https://api.github.com/repos/" + auth["repo"] +
                "/git/blobs/" + quote(written_sha, safe=""))
    headers = {"Authorization": "Bearer " + auth["token"],
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "swrlz-owner-confirmed-update-v2"}
    verified = False
    for attempt in range(4):
        try:
            result = requests.get(blob_url, headers=headers, timeout=15)
            if result.status_code == 200:
                obj = result.json()
                if (obj.get("sha", "").lower() == written_sha and
                    obj.get("encoding") == "base64"):
                    raw = base64.b64decode(str(obj["content"]).replace("\\n", ""), validate=True)
                    if raw != item["content"]:
                        raise CreateFileError("GITHUB_READBACK_MISMATCH", 502)
                    verified = True
                    break
        except (requests.RequestException, ValueError, KeyError, binascii.Error):
            pass
        if attempt < 3:
            time.sleep(0.5 * (attempt + 1))
    if not verified:
        # Fallback: branch content may have become consistent while the blob
        # endpoint was temporarily unavailable. Never report success unverified.
        for attempt in range(3):
            try:
                current_sha, text = _read(auth, item["path"])
                if current_sha == written_sha and text.encode("utf-8") == item["content"]:
                    verified = True
                    break
            except CreateFileError:
                pass
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    if not verified:
        raise CreateFileError("GITHUB_READBACK_MISMATCH", 502)
    return {
        "ok": True, "verified": True, "operation": "UPDATE_FILE",
        "repo": auth["repo"], "branch": auth["branch"], "path": item["path"],
        "commitSha": commit, "sha256": item["digest"],
        "bytesWritten": len(item["content"]),
    }
