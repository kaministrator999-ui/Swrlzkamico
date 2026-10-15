"""Owner-confirmed CREATE_FILE for common GitHub file types and binary payloads.

This general action supplements (does not replace) the historical TXT sandbox.
No prompt or generated text is an authorization token. Only an authenticated
Google-linked user may prepare a bounded proposal, then separately confirm it.
"""
from __future__ import annotations
import base64
import binascii
import hashlib
import json
import re
import secrets
import threading
import time
import unicodedata
from urllib.parse import quote
import requests
from fastapi import HTTPException

ALLOWED_REPOS = ("kaministrator999-ui/Swrlzing-core",
                 "kaministrator999-ui/Swrlzkamico")
OWNER = "kaministrator999-ui"
MAX_FILE_BYTES = 1_000_000    # Below GitHub Contents API's 1 MiB JSON read limit
MAX_PATH_BYTES = 512
MAX_FILENAME_BYTES = 255
TICKET_SECONDS = 300
_pending = {}
_lock = threading.RLock()


class CreateFileError(Exception):
    def __init__(self, code, status=400):
        self.code, self.status = code, status
        super().__init__(code)


def safe_path(path):
    """Allow Unicode, dotfiles, paths and extensionless files; block traversal."""
    if not isinstance(path, str) or not path or len(path.encode("utf-8")) > MAX_PATH_BYTES:
        raise CreateFileError("INVALID_FILE_PATH", 422)
    if unicodedata.normalize("NFC", path) != path:
        raise CreateFileError("PATH_MUST_USE_NFC_UNICODE", 422)
    if path.startswith("/") or path.endswith("/") or "\\" in path or "//" in path:
        raise CreateFileError("INVALID_FILE_PATH", 422)
    for segment in path.split("/"):
        if (segment in ("", ".", "..") or segment.lower() == ".git"
                or len(segment.encode("utf-8")) > MAX_FILENAME_BYTES
                or any(unicodedata.category(ch) in ("Cc", "Cf", "Cs") for ch in segment)):
            raise CreateFileError("INVALID_FILE_PATH", 422)
    return path


def decode_file(content_base64):
    if not isinstance(content_base64, str) or len(content_base64) > 1_340_000:
        raise CreateFileError("FILE_TOO_LARGE_OR_INVALID", 413)
    try:
        raw = base64.b64decode(content_base64, validate=True)
    except (binascii.Error, ValueError):
        raise CreateFileError("INVALID_BASE64_FILE", 422) from None
    if len(raw) > MAX_FILE_BYTES:
        raise CreateFileError("FILE_TOO_LARGE", 413)
    if base64.b64encode(raw).decode("ascii") != content_base64:
        raise CreateFileError("INVALID_BASE64_FILE", 422)
    return raw


def _authorize(user_id, expected_repo=None):
    from github_connection import _config, _load, _api, GITHUB_CAPABILITY_STAGE
    if not isinstance(user_id, str) or not user_id.startswith("google:"):
        raise CreateFileError("GOOGLE_SIGN_IN_REQUIRED", 401)
    if GITHUB_CAPABILITY_STAGE != "read-repository":
        raise CreateFileError("FILE_CREATE_STAGE_LOCKED", 403)
    cfg = _config()
    record = _load(cfg, user_id)
    if not isinstance(record, dict):
        raise CreateFileError("GITHUB_NOT_CONNECTED", 403)
    repo = str(record.get("repo") or "")
    if repo not in ALLOWED_REPOS or (expected_repo and repo != expected_repo):
        raise CreateFileError("SELECTED_REPOSITORY_CHANGED_OR_UNSUPPORTED", 403)
    if str(record.get("login") or "").casefold() != OWNER.casefold():
        raise CreateFileError("GITHUB_OWNER_REQUIRED", 403)
    granted = set(re.split(r"[\s,]+", str(record.get("scopes") or "").strip()))
    if not {"repo", "public_repo"}.intersection(granted):
        raise CreateFileError("GITHUB_WRITE_SCOPE_REQUIRED", 403)
    token = record.get("token")
    if not isinstance(token, str) or not token:
        raise CreateFileError("GITHUB_CONNECTION_INVALID", 403)
    try:
        detail = _api(token, "/repos/" + repo)
    except HTTPException as exc:
        raise CreateFileError("GITHUB_REPOSITORY_UNAVAILABLE", exc.status_code) from None
    if (not isinstance(detail, dict)
            or str(detail.get("full_name") or "") != repo
            or detail.get("private") is not False):
        raise CreateFileError("PUBLIC_OWNER_REPOSITORY_REQUIRED", 403)
    roles = detail.get("permissions") if isinstance(detail.get("permissions"), dict) else {}
    if not any(roles.get(k) is True for k in ("push", "admin", "maintain")):
        raise CreateFileError("GITHUB_PUSH_PERMISSION_REQUIRED", 403)
    branch = str(detail.get("default_branch") or "")
    # Use the actual default branch, never an arbitrary branch supplied by Chat.
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,99}", branch)
            or any(s in ("", ".", "..") for s in branch.split("/"))):
        raise CreateFileError("INVALID_DEFAULT_BRANCH", 403)
    return {"token": token, "repo": repo, "branch": branch}


def _github(method, auth, path, data=None):
    repo, branch = auth["repo"], auth["branch"]
    url = ("https://api.github.com/repos/" + repo + "/contents/" + quote(path, safe="/"))
    headers = {"Authorization": "Bearer " + auth["token"],
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "swrlz-owner-confirmed-create-v262"}
    try:
        response = requests.request(
            method, url, params={"ref": branch} if method == "GET" else None,
            json=data, headers=headers, timeout=25,
        )
        if response.status_code == 404:
            return 404, None
        if response.status_code in (409, 422):
            raise CreateFileError("GITHUB_FILE_EXISTS_OR_CONFLICT", 409)
        if response.status_code in (401, 403):
            raise CreateFileError("GITHUB_WRITE_PERMISSION_DENIED", 403)
        response.raise_for_status()
        return response.status_code, response.json()
    except CreateFileError:
        raise
    except (requests.RequestException, ValueError):
        raise CreateFileError("GITHUB_API_UNAVAILABLE", 502) from None


def prepare(user_id, path, content_base64, media_type="application/octet-stream"):
    auth = _authorize(user_id)
    path = safe_path(path)
    data = decode_file(content_base64)
    if not isinstance(media_type, str) or len(media_type) > 100 or any(ord(c) < 32 for c in media_type):
        raise CreateFileError("INVALID_MEDIA_TYPE", 422)
    status, _ = _github("GET", auth, path)
    if status != 404:
        raise CreateFileError("FILE_ALREADY_EXISTS", 409)
    ticket = secrets.token_urlsafe(32)
    digest = hashlib.sha256(data).hexdigest()
    now = time.monotonic()
    with _lock:
        for key, item in list(_pending.items()):
            if item["expires"] < now:
                del _pending[key]
        _pending[ticket] = {
            "userId": user_id, "repo": auth["repo"], "branch": auth["branch"],
            "path": path, "content": data, "digest": digest,
            "mediaType": media_type, "expires": now + TICKET_SECONDS,
        }
    return {
        "approvalToken": ticket, "expiresInSeconds": TICKET_SECONDS,
        "operation": "CREATE_FILE", "repo": auth["repo"], "branch": auth["branch"],
        "path": path, "mediaType": media_type,
        "bytes": len(data), "sha256": digest, "overwrite": False,
    }


def confirm(user_id, approval_token, approved):
    if not isinstance(approval_token, str) or not approval_token:
        raise CreateFileError("INVALID_APPROVAL_TOKEN", 422)
    with _lock:
        item = _pending.get(approval_token)
        if not item or item["expires"] < time.monotonic() or item["userId"] != user_id:
            raise CreateFileError("APPROVAL_EXPIRED_OR_WRONG_ACCOUNT", 403)
        # Wrong accounts cannot consume a different user's pending approval.
        _pending.pop(approval_token, None)  # Consume before any network call.
    if approved is not True:
        return {"ok": False, "code": "USER_DECLINED"}
    auth = _authorize(user_id, item["repo"])
    if auth["branch"] != item["branch"]:
        raise CreateFileError("DEFAULT_BRANCH_CHANGED", 409)
    status, _ = _github("GET", auth, item["path"])
    if status != 404:
        raise CreateFileError("FILE_ALREADY_EXISTS", 409)
    encoded = base64.b64encode(item["content"]).decode("ascii")
    status, response = _github("PUT", auth, item["path"], {
        "message": "feat(files): owner-approved CREATE_FILE " + item["path"][-100:],
        "branch": auth["branch"], "content": encoded,
        # No 'sha' field: updating existing files is forbidden.
    })
    if status != 201:
        raise CreateFileError("GITHUB_CREATE_NOT_CONFIRMED", 502)
    commit = str((response or {}).get("commit", {}).get("sha") or "")
    if not re.fullmatch(r"[a-fA-F0-9]{40}", commit):
        raise CreateFileError("GITHUB_COMMIT_NOT_VERIFIED", 502)
    status, response = _github("GET", auth, item["path"])
    if status != 200 or not isinstance(response, dict) or response.get("encoding") != "base64":
        raise CreateFileError("GITHUB_READBACK_NOT_AVAILABLE", 502)
    try:
        result = base64.b64decode(str(response["content"]).replace("\n", ""), validate=True)
    except (KeyError, binascii.Error, ValueError):
        raise CreateFileError("GITHUB_READBACK_NOT_AVAILABLE", 502) from None
    if result != item["content"] or hashlib.sha256(result).hexdigest() != item["digest"]:
        raise CreateFileError("GITHUB_CONTENT_MISMATCH", 502)
    return {
        "ok": True, "verified": True, "operation": "CREATE_FILE",
        "repo": auth["repo"], "branch": auth["branch"], "path": item["path"],
        "bytesWritten": len(result), "sha256": item["digest"],
        "mediaType": item["mediaType"], "commitSha": commit,
        "url": "https://github.com/" + auth["repo"] + "/blob/" + quote(auth["branch"], safe="/") + "/" + quote(item["path"], safe="/"),
    }
