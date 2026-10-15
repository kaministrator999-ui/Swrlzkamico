"""Strictly scoped GitHub sandbox text creation; no model-generated action executes here."""
from __future__ import annotations
import base64
import hashlib
import json
import os
import re
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

OWNER = "kaministrator999-ui"
REPO = "Swrlzing-core"
BRANCH = "main"
ROOT = "write-action-tests/"
MAX_BYTES = 4096
_pending = {}
_lock = threading.RLock()
_ttl = 300


class WriteError(Exception):
    def __init__(self, code, status=400):
        super().__init__(code)
        self.code, self.status = code, status


def _authorized(user):
    # The trusted Station supplies a verified Google account identity. The
    # existing encrypted per-account GitHub OAuth authority checks grant+role.
    from github_connection import _sandbox_authorize_user
    from fastapi import HTTPException
    try:
        return _sandbox_authorize_user(user)
    except HTTPException as exc:
        raise WriteError(str(exc.detail), exc.status_code) from None


def _path(filename):
    if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.txt", filename, re.ASCII):
        raise WriteError("INVALID_TXT_FILENAME")
    if filename.startswith(".") or ".." in filename:
        raise WriteError("INVALID_TXT_FILENAME")
    return ROOT + filename


def _content(content):
    if not isinstance(content, str) or not content or len(content.encode("utf-8")) > MAX_BYTES:
        raise WriteError("INVALID_TEXT_CONTENT")
    return content


def _request(method, path, token, data=None):
    url = "https://api.github.com/repos/" + OWNER + "/" + REPO + "/contents/" + urllib.parse.quote(path, safe="/") + "?ref=" + BRANCH if method == "GET" else "https://api.github.com/repos/" + OWNER + "/" + REPO + "/contents/" + urllib.parse.quote(path, safe="/")
    headers = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "swrlz-sandbox-create-txt-v1"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, method=method, headers=headers, data=json.dumps(data).encode("utf-8") if data is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return 404, None
        if error.code in (409, 422):
            raise WriteError("GITHUB_CONFLICT_OR_EXISTS", 409) from None
        raise WriteError("GITHUB_WRITE_UNAVAILABLE", 502) from None
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise WriteError("GITHUB_WRITE_UNAVAILABLE", 502) from None


def prepare(user, filename, content):
    token = _authorized(user)
    path = _path(filename)
    content = _content(content)
    status, _ = _request("GET", path, token)
    if status != 404:
        raise WriteError("FILE_ALREADY_EXISTS", 409)
    ticket = secrets.token_urlsafe(32)
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    now = time.monotonic()
    with _lock:
        for key, item in list(_pending.items()):
            if item["expires"] < now:
                del _pending[key]
        _pending[ticket] = {"userId": user["id"], "path": path, "content": content, "digest": digest, "expires": now + _ttl}
    return {"approvalToken": ticket, "expiresInSeconds": _ttl, "operation": "CREATE_FILE", "repo": OWNER + "/" + REPO, "branch": BRANCH, "path": path, "preview": content, "sha256": digest}


def confirm(user, ticket, approved):
    token = _authorized(user)
    if not isinstance(ticket, str) or not ticket:
        raise WriteError("INVALID_APPROVAL_TOKEN")
    with _lock:
        item = _pending.pop(ticket, None)
    if not item or item["expires"] < time.monotonic() or item["userId"] != user["id"]:
        raise WriteError("APPROVAL_EXPIRED_OR_INVALID", 403)
    if approved is not True:
        return {"ok": False, "code": "USER_DECLINED"}
    status, _ = _request("GET", item["path"], token)
    if status != 404:
        raise WriteError("FILE_ALREADY_EXISTS", 409)
    # Contents API requires SHA for updates; omit it deliberately to prohibit overwrite.
    content_bytes = item["content"].encode("utf-8")
    status, response = _request("PUT", item["path"], token, {"message": "test(sandbox): approved CREATE_FILE " + item["path"].split("/")[-1], "branch": BRANCH, "content": base64.b64encode(content_bytes).decode("ascii")})
    if status not in (200, 201):
        raise WriteError("GITHUB_WRITE_UNAVAILABLE", 502)
    commit = str((response or {}).get("commit", {}).get("sha") or "")
    status, fetched = _request("GET", item["path"], token)
    if status != 200 or not isinstance(fetched, dict):
        raise WriteError("GITHUB_READBACK_FAILED", 502)
    try:
        observed = base64.b64decode(fetched["content"].replace("\n", ""), validate=False)
    except (KeyError, TypeError, ValueError):
        raise WriteError("GITHUB_READBACK_FAILED", 502) from None
    verified = hashlib.sha256(observed).hexdigest() == item["digest"] and observed == content_bytes
    if not verified:
        raise WriteError("GITHUB_READBACK_MISMATCH", 502)
    receipt = {"ok": True, "operation": "CREATE_FILE", "repo": OWNER + "/" + REPO, "branch": BRANCH, "path": item["path"], "commitSha": commit, "verified": True, "url": "https://github.com/" + OWNER + "/" + REPO + "/blob/" + BRANCH + "/" + item["path"]}
    # Visual data is derived only from confirmed bytes and the exact commit.
    # Optional GitHub diff statistics are fetched separately and never invented.
    from github_connection import _api
    from github_work_summary_v260 import make_work_widget
    receipt["widget"] = make_work_widget(receipt, item["content"], token, github_get=_api)
    return receipt



def create_requested_test_file(user, request_id, prompt):
    """Exactly one CREATE_FILE for a direct, owner-authorized Chat test request.

    No generated/model/retrieved text enters this path. The filename is stable
    for the accepted request ID to avoid duplicate files on retries. This is
    the narrow exception to the separate preview/confirm panel; unrelated
    writes still require that panel, and the GitHub scope check is unchanged.
    """
    from github_txt_intent_v256 import wants_direct_github_test_txt
    if not wants_direct_github_test_txt(prompt):
        raise WriteError("DIRECT_TEST_FILE_REQUEST_REQUIRED", 403)
    if not isinstance(user, dict) or not isinstance(user.get("id"), str) or not user["id"].startswith("google:"):
        raise WriteError("SANDBOX_WRITE_OWNER_REQUIRED", 403)
    if not isinstance(request_id, str) or not 0 < len(request_id) <= 160:
        raise WriteError("INVALID_REQUEST_ID", 400)
    # The caller is the trusted Station: the prompt was submitted directly by
    # this account as its user turn, not ingested from GitHub or model output.
    suffix = hashlib.sha256((user["id"] + "\0" + request_id).encode("utf-8")).hexdigest()[:16]
    filename = "chat-test-" + suffix + ".txt"
    contents = (
        "Hello from §wyrlz Chat!\n"
        "This is a harmless GitHub text-file creation test, requested directly "
        "in Chat by the connected repository owner.\n"
        "Target: Swrlzing-core / main / write-action-tests/\n"
    )
    # Preserve existing owner Google OAuth, scoped GitHub permissions, no
    # overwrites, create-only PUT and exact-byte remote readback checks.
    preview = prepare(user, filename, contents)
    return confirm(user, preview["approvalToken"], True)
