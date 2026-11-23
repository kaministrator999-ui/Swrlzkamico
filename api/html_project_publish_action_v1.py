"""Owner-scoped preview/approve/dispatch/status for §C's HTML project publishing.

No model or prompt text authorizes publishing. Only an explicit authenticated
browser POST with a one-use approval token dispatches the trusted workflow.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastapi import HTTPException, Request as FastAPIRequest
from fastapi.responses import JSONResponse

OWNER = "kaministrator999-ui"
REPO = OWNER + "/Swrlzkamico"
WORKFLOW = "hf-html-project-publish-v1.yml"
GITHUB_API = "https://api.github.com"
LIVE_BASE = "https://kamiloki-swyrlz.hf.space"
SLUG = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
NONCE = re.compile(r"[a-f0-9]{24}\Z")
TTL = 300
_LOCK = threading.RLock()
_PENDING = {}
_DEPLOYMENTS = {}


def _authorize(user):
    # Existing verified Google identity + selected, public owner repo + OAuth.
    from github_general_create_v262 import _authorize as existing_authorize
    return existing_authorize(user, REPO)


def _github(method, token, path, payload=None):
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "swrlz-owner-html-project-release-v1",
    }
    data = None
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":")).encode()
        headers["Content-Type"] = "application/json"
    req = Request(GITHUB_API + path, headers=headers, data=data, method=method)
    try:
        with urlopen(req, timeout=18) as response:
            raw = response.read(5_000_000)
            return response.status, json.loads(raw) if raw else {}
    except HTTPError as exc:
        raise HTTPException(exc.code, "GitHub request rejected: " + str(exc.code)) from None
    except (URLError, TimeoutError, ValueError) as exc:
        raise HTTPException(502, "GitHub unavailable: " + type(exc).__name__) from None


def _head(token, branch):
    status, data = _github("GET", token, "/repos/" + REPO + "/git/ref/heads/" + quote(branch, safe=""))
    sha = str((data.get("object") or {}).get("sha") or "").lower()
    if status != 200 or not SHA.fullmatch(sha):
        raise HTTPException(502, "Verified GitHub branch SHA unavailable")
    return sha


def _manifest(token, source, slug):
    if not SLUG.fullmatch(slug) or not SHA.fullmatch(source):
        raise HTTPException(400, "Invalid project name or source commit")
    status, data = _github("GET", token, "/repos/" + REPO + "/git/trees/" + source + "?recursive=1")
    if status != 200 or data.get("truncated") or not isinstance(data.get("tree"), list):
        raise HTTPException(409, "Complete immutable Git tree unavailable")
    prefix = "html-projects/" + slug + "/"
    files = []
    total = 0
    for entry in data["tree"]:
        path = str(entry.get("path") or "")
        if not path.startswith(prefix):
            continue
        rel = path[len(prefix):]
        if entry.get("type") == "tree":
            continue
        if entry.get("type") != "blob" or entry.get("mode") not in {"100644", "100755"}:
            raise HTTPException(422, "Project contains unsafe Git entries")
        parts = rel.split("/")
        if not 1 <= len(parts) <= 8 or any(not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", p) or p.startswith(".") for p in parts):
            raise HTTPException(422, "Invalid asset path: " + rel[:100])
        ext = rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
        if ext not in {"html", "htm", "css", "js", "mjs", "json", "svg", "png",
                       "jpg", "jpeg", "webp", "gif", "ico", "woff", "woff2"}:
            raise HTTPException(422, "Unsupported asset extension")
        size = entry.get("size")
        if not isinstance(size, int) or size < 0:
            raise HTTPException(422, "Asset size unavailable")
        total += size
        files.append({"path": rel, "bytes": size, "blobSha": entry.get("sha")})
    if not files or not any(f["path"] == "index.html" for f in files):
        raise HTTPException(422, "Project requires html-projects/" + slug + "/index.html")
    if len(files) > 48 or total > 1_000_000:
        raise HTTPException(413, "Project exceeds publication limits")
    return {"project": slug, "sourceSha": source, "files": files,
            "count": len(files), "bytes": total,
            "url": LIVE_BASE + "/projects/" + slug + "/index.html",
            "destination": "kamiloki/Swyrlz:chat/§wyrlz/projects/" + slug + "/"}


def _cleanup():
    now = time.monotonic()
    for key, item in list(_PENDING.items()):
        if item["expires"] <= now:
            del _PENDING[key]
    for key, item in list(_DEPLOYMENTS.items()):
        if item["expires"] <= now:
            del _DEPLOYMENTS[key]


def prepare(user, slug):
    auth = _authorize(user)
    if auth.get("repo") != REPO or auth.get("branch") != "main":
        raise HTTPException(403, "Select the owner repository and main branch before publication")
    sha = _head(auth["token"], "main")
    doc = _manifest(auth["token"], sha, slug)
    ticket = secrets.token_urlsafe(30)
    with _LOCK:
        _cleanup()
        _PENDING[ticket] = {"user": user, "sha": sha, "project": slug,
                            "expires": time.monotonic() + TTL}
    # Show the pinned entry document inside an opaque-origin iframe. External
    # relative assets are not previewed until real browser publication.
    _, entry = _github("GET", auth["token"], "/repos/" + REPO +
                       "/contents/html-projects/" + slug + "/index.html?ref=" + sha)
    try:
        source = base64.b64decode(str(entry["content"]).replace("\
", ""), validate=True).decode("utf-8")
    except (KeyError, ValueError, UnicodeDecodeError):
        raise HTTPException(422, "Project index.html preview unavailable") from None
    if len(source.encode("utf-8")) > 260_000:
        raise HTTPException(413, "HTML preview exceeds limit")
    return {**doc, "previewHtml": source, "approvalToken": ticket, "expiresInSeconds": TTL,
            "approvalRequired": True, "status": "AWAITING_OWNER_APPROVAL"}


def confirm(user, ticket, approved):
    if not isinstance(ticket, str) or type(approved) is not bool:
        raise HTTPException(400, "Invalid approval")
    with _LOCK:
        _cleanup()
        record = _PENDING.pop(ticket, None)
    if not record or record["user"] != user:
        raise HTTPException(403, "Approval expired or belongs to another account")
    if not approved:
        return {"ok": False, "code": "OWNER_DECLINED"}
    auth = _authorize(user)
    if auth.get("repo") != REPO or auth.get("branch") != "main":
        raise HTTPException(403, "Selected repository or branch changed")
    if _head(auth["token"], "main") != record["sha"]:
        raise HTTPException(409, "GitHub branch changed after review; prepare a new approval")
    # Revalidate exact reviewed tree before issuing the one delegated action.
    doc = _manifest(auth["token"], record["sha"], record["project"])
    nonce = secrets.token_hex(12)
    path = "/repos/" + REPO + "/actions/workflows/" + WORKFLOW + "/dispatches"
    status, _ = _github("POST", auth["token"], path, {
        "ref": "main",
        "inputs": {
            "source_sha": record["sha"],
            "project": record["project"],
            "approved": "yes",
            "request_nonce": nonce,
        },
    })
    if status != 204:
        raise HTTPException(502, "GitHub did not accept the Actions dispatch")
    with _LOCK:
        _cleanup()
        _DEPLOYMENTS[(user, nonce)] = {**doc,
            "expires": time.monotonic() + 86400}
    return {"ok": True, "code": "DISPATCH_ACCEPTED",
            "requestNonce": nonce, "sourceSha": record["sha"],
            "project": record["project"], "url": doc["url"],
            "actionsUrl": "https://github.com/" + REPO + "/actions/workflows/" + WORKFLOW}


def status(user, nonce):
    if not NONCE.fullmatch(nonce):
        raise HTTPException(400, "Invalid deployment receipt ID")
    with _LOCK:
        record = _DEPLOYMENTS.get((user, nonce))
    if record is None:
        raise HTTPException(404, "Deployment receipt expired or unavailable; inspect GitHub Actions")
    auth = _authorize(user)
    _, data = _github("GET", auth["token"],
                      "/repos/" + REPO + "/actions/workflows/" + WORKFLOW +
                      "/runs?event=workflow_dispatch&per_page=50")
    matches = [r for r in data.get("workflow_runs", [])
               if isinstance(r, dict) and nonce in str(r.get("display_title") or "")]
    if not matches:
        return {"code": "QUEUED", "requestNonce": nonce,
                "actionsUrl": "https://github.com/" + REPO + "/actions/workflows/" + WORKFLOW}
    run = max(matches, key=lambda r: int(r.get("id") or 0))
    result = {"requestNonce": nonce, "runId": run["id"],
              "actionsUrl": run.get("html_url"),
              "workflowStatus": run.get("status"),
              "conclusion": run.get("conclusion"),
              "sourceSha": record["sourceSha"], "project": record["project"]}
    if run.get("status") != "completed":
        return {**result, "code": "RUNNING"}
    if run.get("conclusion") != "success":
        return {**result, "code": "FAILED"}
    # A successful workflow must have verified exact HF bytes and the live
    # browser route, including its opaque-origin CSP, before marking success.
    with urlopen(Request(record["url"], headers={"Cache-Control": "no-cache"}), timeout=15) as page:
        policy = page.headers.get("Content-Security-Policy", "")
        mime = page.headers.get("Content-Type", "")
        if (page.status != 200 or "text/html" not in mime or
                "sandbox allow-scripts" not in policy or
                "allow-same-origin" in policy):
            return {**result, "code": "RUNTIME_SECURITY_NOT_VERIFIED"}
        return {**result, "code": "PUBLISHED_VERIFIED", "url": record["url"]}


def _guard(request):
    origin = request.headers.get("origin") or ""
    same = str(request.base_url).rstrip("/")
    if (request.headers.get("x-swrlz-project-action") != "v1" or
            origin not in {same, LIVE_BASE} or
            request.headers.get("content-type", "").split(";", 1)[0].lower() != "application/json"):
        raise HTTPException(403, "Same-origin owner approval required")


def install(app, account_session):
    def owned_user(request):
        _, user = account_session(request)
        if not user:
            raise HTTPException(401, "Google sign-in required")
        return user

    @app.post("/api/html-projects/prepare")
    async def prepare_route(request: FastAPIRequest):
        _guard(request)
        user = owned_user(request)
        body = await request.json()
        result = prepare(user, str(body.get("project") or ""))
        return JSONResponse(result, headers={"Cache-Control": "private, no-store"})

    @app.post("/api/html-projects/confirm")
    async def confirm_route(request: FastAPIRequest):
        _guard(request)
        user = owned_user(request)
        body = await request.json()
        result = confirm(user, body.get("approvalToken"), body.get("approved"))
        return JSONResponse(result, headers={"Cache-Control": "private, no-store"})

    @app.get("/api/html-projects/status/{nonce}")
    def status_route(request: FastAPIRequest, nonce: str):
        user = owned_user(request)
        result = status(user, nonce)
        return JSONResponse(result, headers={"Cache-Control": "private, no-store"})
