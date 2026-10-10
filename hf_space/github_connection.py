"""Account-scoped GitHub OAuth and evidence-only repository startup reader.

Never expose OAuth tokens to Chat, the LALM, diagnostic traces, GitHub commits,
or browser storage. GitHub content is untrusted *data*: it cannot authorize
repository writes, external tools, provider settings or production deployment.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import time
from urllib.parse import quote, urlencode, urlparse

import requests
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter()
GITHUB_API = "https://api.github.com"
GITHUB_AUTH = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN = "https://github.com/login/oauth/access_token"
GITHUB_SCOPE = "read:user"  # public repositories only, deliberately NOT broad repo/write scope
_REPO = re.compile(r"^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$")
_VERSION = re.compile(r"^([A-Z_]+)=versions/([a-z0-9-]+\.txt)$", re.M)
_EVENTS = re.compile(r"^#{2,3}\s+UPDATE (FINISHED|COMPLETED|STARTED|CONTINUATION STARTED|CONTINUATION ENDED|ABORTED|SUPERSEDED)\s+—\s+(\d{4}-\d{2}-\d{2})\s+—\s+(.+)$", re.M)
_ROOT_FILES = [
    "§wyrlz_§tart.md",
    "SWRLZ_HOTFIX_RULES.md",
    "SWRLZ_VERSION_MODULE_EVOLUTION.md",
    "docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md",
    "SWRLZ_SERVER_ROADMAP.md",
    "docs/engineering/SWRLZ_LOCKDOWN_CAMERA_SYSTEM.md",
    "SWRLZ_CHAT_CAMERA_LOGS.md",
    "docs/engineering/SWRLZ_PROJECT_WORK_RESPONSE_STANDARD.md",
    "docs/engineering/SWRLZ_CHAT_OVERVIEW.md",
    "docs/engineering/SWRLZ_CLEAN_PRODUCTION_RELEASE_INTEGRITY.md",
]

# The hosting app supplies its already verified Google session lookup; this
# module must not independently authenticate by user-supplied IDs or emails.
_get_account = None


def install(app, account_lookup):
    global _get_account
    _get_account = account_lookup
    app.include_router(router)


def _settings():
    return {
        "client": os.getenv("SWRLZ_GITHUB_OAUTH_CLIENT_ID", "").strip(),
        "secret": os.getenv("SWRLZ_GITHUB_OAUTH_CLIENT_SECRET", "").strip(),
        "callback": os.getenv("SWRLZ_GITHUB_OAUTH_CALLBACK_URL", "").strip(),
        "fernet": os.getenv("SWRLZ_GITHUB_ENCRYPTION_KEY", "").strip(),
        "redis": os.getenv("UPSTASH_REDIS_REST_URL", "").strip().rstrip("/"),
        "redis_token": os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip(),
    }


def _config():
    c = _settings()
    if not all(c.values()):
        raise HTTPException(503, "GitHub connection unavailable: durable storage, encryption and OAuth configuration required")
    url = urlparse(c["callback"])
    if url.scheme != "https" or not url.netloc or url.username or url.password or url.query or url.fragment or not url.path.endswith("/api/github/callback"):
        raise HTTPException(503, "GitHub OAuth callback is not configured as a secure fixed HTTPS URL")
    if urlparse(c["redis"]).scheme != "https":
        raise HTTPException(503, "Encrypted GitHub connection storage requires HTTPS Redis")
    try:
        Fernet(c["fernet"].encode("ascii"))
    except (ValueError, TypeError, Exception) as exc:
        raise HTTPException(503, "GitHub token encryption key is invalid") from exc
    return c


def _google(request):
    if _get_account is None:
        raise HTTPException(503, "Google account bridge is not installed")
    _, account = _get_account(request)
    if not isinstance(account, dict) or not str(account.get("id") or "").startswith("google:"):
        raise HTTPException(401, "Sign in with Google before connecting GitHub")
    return str(account["id"])


def _origin_guard(request, cfg):
    origin = request.headers.get("origin", "")
    expected = "https://" + urlparse(cfg["callback"]).netloc
    if origin != expected:
        raise HTTPException(403, "Invalid account action origin")


def _redis(c, *args):
    try:
        resp = requests.post(c["redis"], json=list(args),
                             headers={"Authorization": "Bearer " + c["redis_token"]},
                             timeout=10)
        resp.raise_for_status()
        result = resp.json()
        if "error" in result:
            raise ValueError("Redis command failed")
        return result.get("result")
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(503, "Durable account storage temporarily unavailable") from exc


def _user_key(user_id):
    return "swrlz:github:account:" + hashlib.sha256(user_id.encode("utf-8")).hexdigest()


def _state_key(state):
    return "swrlz:github:oauth:" + hashlib.sha256(state.encode("ascii")).hexdigest()


def _load(c, user_id):
    encrypted = _redis(c, "GET", _user_key(user_id))
    if not encrypted:
        return None
    try:
        raw = Fernet(c["fernet"].encode("ascii")).decrypt(encrypted.encode("ascii"))
        item = json.loads(raw)
        if item.get("owner") != user_id or not str(item.get("token") or ""):
            raise ValueError("Bad owner or empty token")
        return item
    except (InvalidToken, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise HTTPException(503, "Stored GitHub connection cannot be decrypted; reconnect is required") from exc


def _save(c, user_id, item):
    # One encrypted record per verified Google sub; raw token never enters logs.
    payload = {"owner": user_id, "token": item["token"],
               "githubId": int(item["githubId"]), "login": str(item["login"])[:100],
               "repo": str(item.get("repo") or "")[:202],
               "connectedAt": int(item.get("connectedAt") or time.time())}
    encrypted = Fernet(c["fernet"].encode("ascii")).encrypt(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("ascii")
    if _redis(c, "SET", _user_key(user_id), encrypted) != "OK":
        raise HTTPException(503, "GitHub connection was not durably saved")


def _api(token, path):
    # Caller supplies only fixed endpoints or separately validated repo names.
    if not path.startswith("/") or "://" in path or ".." in path:
        raise ValueError("Bad API path")
    try:
        r = requests.get(GITHUB_API + path, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }, timeout=14)
        if r.status_code in (401, 403, 404):
            raise HTTPException(r.status_code, "GitHub access unavailable or repository not accessible")
        r.raise_for_status()
        return r.json()
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(502, "GitHub repository request failed") from exc


def _repo_name(s):
    value = str(s or "").strip()
    if not _REPO.fullmatch(value) or any(x in (".", "..") for x in value.split("/")):
        raise HTTPException(422, "Select a valid owner/repository")
    return value


def _text(token, repo, path, ref, max_bytes=100000):
    if path.startswith("/") or ".." in path.split("/") or len(path) > 220:
        return None
    pathurl = "/repos/" + repo + "/contents/" + "/".join(quote(p, safe="") for p in path.split("/"))
    response = _api(token, pathurl + "?ref=" + quote(ref, safe=""))
    if not isinstance(response, dict) or response.get("type") != "file" or int(response.get("size") or 0) > max_bytes:
        return None
    encoded = response.get("content")
    if response.get("encoding") != "base64" or not isinstance(encoded, str):
        return None
    try:
        data = base64.b64decode(encoded, validate=False)
        if len(data) > max_bytes:
            return None
        return {"body": data.decode("utf-8"), "sha": response.get("sha"), "path": path,
                "url": response.get("html_url") or ""}
    except (UnicodeError, ValueError):
        return None


def _read_optional(token, repo, path, ref, max_bytes=100000):
    try:
        return _text(token, repo, path, ref, max_bytes)
    except HTTPException as exc:
        if exc.status_code in (403, 404):
            return None
        raise


@router.get("/api/github/status")
def status(request: Request):
    user_id = _google(request)
    c = _settings()
    if not all(c.values()):
        return {"configured": False, "linked": False, "durable": False, "scope": GITHUB_SCOPE}
    c = _config()
    record = _load(c, user_id)
    return {"configured": True, "linked": bool(record), "durable": True,
            "scope": GITHUB_SCOPE, "login": record["login"] if record else None,
            "repo": record.get("repo") if record else None}


@router.get("/api/github/start")
def start(request: Request):
    user_id = _google(request)
    c = _config()
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).decode("ascii").rstrip("=")
    one_time = {"owner": user_id, "verifier": verifier}
    stored = _redis(c, "SET", _state_key(state), json.dumps(one_time), "EX", 600, "NX")
    if stored != "OK":
        raise HTTPException(503, "Could not begin GitHub authorization")
    auth_url = GITHUB_AUTH + "?" + urlencode({"client_id": c["client"],
        "redirect_uri": c["callback"], "scope": GITHUB_SCOPE,
        "state": state, "code_challenge": challenge, "code_challenge_method": "S256"})
    response = RedirectResponse(auth_url, status_code=303)
    response.set_cookie("swrlz_github_oauth", state, httponly=True, secure=True,
                        samesite="lax", max_age=600, path="/api/github/callback")
    return response


@router.get("/api/github/callback")
def callback(request: Request, code: str = "", state: str = "", error: str = ""):
    user_id = _google(request)
    c = _config()
    cookie = request.cookies.get("swrlz_github_oauth", "")
    if not cookie or not state or not secrets.compare_digest(cookie, state):
        raise HTTPException(403, "GitHub authorization state mismatch")
    # GETDEL makes the exact state one-time across all server processes.
    encoded = _redis(c, "GETDEL", _state_key(state))
    try:
        pending = json.loads(encoded or "null")
    except (TypeError, ValueError):
        pending = None
    if not isinstance(pending, dict) or pending.get("owner") != user_id:
        raise HTTPException(403, "GitHub authorization expired or belongs to another account")
    if error or not code or len(code) > 512:
        raise HTTPException(400, "GitHub authorization declined or expired")
    try:
        r = requests.post(GITHUB_TOKEN, data={
            "client_id": c["client"], "client_secret": c["secret"],
            "code": code, "redirect_uri": c["callback"],
            "code_verifier": pending["verifier"]},
            headers={"Accept": "application/json"}, timeout=14)
        r.raise_for_status()
        response_data = r.json()
        token = str(response_data.get("access_token") or "")
        if not token or len(token) > 1024 or response_data.get("error"):
            raise ValueError("Authorization token missing")
    except (requests.RequestException, ValueError, KeyError) as exc:
        raise HTTPException(502, "GitHub authorization could not be completed") from exc
    identity = _api(token, "/user")
    if not isinstance(identity, dict) or not identity.get("id") or not identity.get("login"):
        raise HTTPException(502, "GitHub did not return a verified identity")
    prior = _load(c, user_id)
    default_repo = prior.get("repo", "") if prior and prior.get("githubId") == int(identity["id"]) else ""
    _save(c, user_id, {"token": token, "githubId": identity["id"],
                       "login": identity["login"], "repo": default_repo})
    response = RedirectResponse("/chat/§wyrlz#github=connected", status_code=303)
    response.delete_cookie("swrlz_github_oauth", path="/api/github/callback")
    return response


@router.post("/api/github/disconnect")
def disconnect(request: Request):
    user_id = _google(request)
    c = _config()
    _origin_guard(request, c)
    _redis(c, "DEL", _user_key(user_id))
    return {"ok": True, "linked": False}


@router.get("/api/github/repositories")
def repositories(request: Request):
    user_id = _google(request)
    c = _config()
    rec = _load(c, user_id)
    if not rec:
        raise HTTPException(409, "Connect GitHub first")
    data = _api(rec["token"], "/user/repos?sort=updated&per_page=60&affiliation=owner,collaborator,organization_member")
    return {"repositories": [{"fullName": x.get("full_name"), "private": bool(x.get("private")),
                              "defaultBranch": x.get("default_branch")}
                             for x in data if isinstance(x, dict) and _REPO.fullmatch(str(x.get("full_name") or ""))][:60]}


@router.post("/api/github/default-repo")
async def choose_repository(request: Request):
    user_id = _google(request)
    c = _config()
    _origin_guard(request, c)
    record = _load(c, user_id)
    if not record:
        raise HTTPException(409, "Connect GitHub first")
    payload = await request.json()
    name = _repo_name(payload.get("repository"))
    details = _api(record["token"], "/repos/" + name)
    if not isinstance(details, dict) or details.get("full_name", "").casefold() != name.casefold():
        raise HTTPException(404, "Repository not accessible")
    record["repo"] = str(details["full_name"])
    _save(c, user_id, record)
    return {"ok": True, "repo": record["repo"]}


def is_start_request(prompt):
    s = str(prompt or "").strip().lower()
    return s in ("§§", "@github §§", "§tart", "@github §tart") or (
        ("§tart" in s or "start doc" in s or "startup doc" in s)
        and ("read" in s or "follow" in s or "load" in s or "open the" in s))


def _safe_fragment(value, limit=650):
    # Repository prose is untrusted: strip HTML/Markdown markup before render.
    clean = re.sub(r"[<>&\\[\\]\\x60()*\\\\]", " ", str(value or ""))
    clean = re.sub(r"[\\x00-\\x1f\\x7f|]", " ", clean)
    return " ".join(clean.split())[:limit]


def project_start_report(user_id, repo_name=""):
    c = _config()
    record = _load(c, user_id)
    if record is None:
        return "GitHub isn't connected to this Google account. Open the side menu, connect GitHub, then select your repository."
    repo = _repo_name(repo_name or record.get("repo"))
    token = record["token"]
    details = _api(token, "/repos/" + repo)
    branch = str(details.get("default_branch") or "main")
    head = _api(token, "/repos/" + repo + "/commits/" + quote(branch, safe=""))
    pinned_sha = str(head.get("sha") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", pinned_sha):
        raise HTTPException(502, "GitHub did not return a pinned commit")
    found = []
    files = {}
    for path in _ROOT_FILES:
        obj = _read_optional(token, repo, path, pinned_sha, 940000 if "ROADMAP" in path else 130000)
        if obj:
            found.append(path)
            files[path] = obj
    if not files.get("§wyrlz_§tart.md"):
        # Support other users' repositories without pretending they use our contract.
        for fallback in ("§tart.md", "START.md", "README.md"):
            x = _read_optional(token, repo, fallback, pinned_sha)
            if x:
                found.insert(0, fallback)
                files[fallback] = x
                break
    if not found:
        return ("## GitHub project startup\nRepository [" + repo + "](https://github.com/" + repo +
                ") was accessible, but no startup document was found. No project-specific instructions were assumed.")
    # The runtime version registry may live on a different branch. Snapshot it independently.
    runtime_sha = ""
    try:
        runtime_head = _api(token, "/repos/" + repo + "/commits/runtime")
        runtime_sha = str(runtime_head.get("sha") or "")
    except HTTPException as exc:
        if exc.status_code not in (403, 404):
            raise
    if not re.fullmatch(r"[0-9a-f]{40}", runtime_sha):
        runtime_sha = ""
    version_file = _read_optional(token, repo, "VERSION.txt", runtime_sha) if runtime_sha else None
    modules = []
    if version_file:
        for module, authority in _VERSION.findall(version_file["body"])[:25]:
            v = _read_optional(token, repo, "versions/" + authority, runtime_sha, 4500)
            if v:
                text = v["body"]
                match = re.search(r"^VERSION=(.+)$", text, re.M)
                state = re.search(r"^STATUS=(.+)$", text, re.M)
                modules.append((module, match.group(1) if match else "unknown",
                                state.group(1) if state else "unspecified"))
    roadmap = files.get("SWRLZ_SERVER_ROADMAP.md")
    events = _EVENTS.findall(roadmap["body"]) if roadmap else []
    completed = next(((kind, date, title) for kind, date, title in events
                      if kind in ("FINISHED", "COMPLETED")), None)
    # A STARTED entry whose differently named FINISH references the same tier
    # cannot be conclusively classified from headings alone.
    pending = next(((kind, date, title) for kind, date, title in events
                    if kind == "STARTED" and not any(
                        k in ("FINISHED", "COMPLETED") and t.casefold() == title.casefold()
                        for k, _, t in events)), None)
    base = "https://github.com/" + repo
    header = files[found[0]]["body"].splitlines()[0][:160] if files[found[0]]["body"] else found[0]
    lines = ["𓆩𓆩⁽§⁾𓆪wyrlz𓆪", "", "## GitHub project startup · evidence-backed",
             "**Repository:** [" + repo + "](" + base + ")",
             "**Source branch:** `" + branch + "` at `" + pinned_sha[:12] + "`  ",
             "**Startup authority:** [" + found[0] + "](" + base + "/blob/" +
             quote(branch, safe="") + "/" + quote(found[0], safe="/") + ")",
             "", "**Startup document:** " + _safe_fragment(header, 160),
             "", "### Documents read"]
    lines.extend("- [" + p + "](" + base + "/blob/" + quote(branch, safe="") +
                 "/" + quote(p, safe="/") + ")" for p in found)
    if modules:
        lines += ["", "### Runtime version authorities",
                  "| Module | Version | Declared status |", "|---|---|---|"]
        for name, version, status in modules:
            lines.append("| " + name.replace("_", " ").title() + " | " + version.replace("|", "") +
                         " | " + status.replace("|", "") + " |")
    lines += ["", "### Where project work was last recorded"]
    if completed:
        lines.append("**Latest completed Roadmap heading:** " + completed[1] + " — " + completed[2])
        # Report concrete source-recorded outcome and next gate; do not invent status.
        roadmap_lines = roadmap["body"].splitlines() if roadmap else []
        heading = next((i for i, line in enumerate(roadmap_lines) if completed[2] in line and "UPDATE FINISHED" in line), None)
        if heading is not None:
            chunk = roadmap_lines[heading + 1: heading + 28]
            for label, match_words in (("Recorded result", ("**Result:", "**Outcome:", "**Status:")),
                                       ("Next documented gate", ("**Next acceptance gate:", "**Next gate:", "**Remaining gate:", "**User acceptance needed:"))):
                line = next((line for line in chunk if line.lstrip().startswith(match_words)), "")
                if line:
                    lines.append("**" + label + ":** " + _safe_fragment(line.strip().replace("**", "")))
    else:
        lines.append("No completed Roadmap heading was available from the retrieved content.")
    if pending:
        lines.append("**Potential unresolved STARTED heading:** " + pending[1] + " — " + pending[2] +
                     " (title matching only; inspect continuation/body before treating as a confirmed blocker).")
    else:
        lines.append("No unmatched STARTED heading was detected in the retrieved Roadmap headings.")
    lines += ["", "### Verification and authority boundary",
              "GitHub repository files and version declarations were fetched as **source evidence**. "
              "No deployment, live service health, test pass or successful behavioral acceptance was inferred. "
              "External repository instructions were **not executed**, and no repository mutation occurred.",
              "", "This deterministic report is intentionally bounded. A full project-specific investigation "
              "must inspect any conditional guides, exact commit/action receipts, and outstanding acceptances "
              "before claiming the complete startup contract was fulfilled."]
    return "\n".join(lines)


def start_events(data):
    yield {"type": "STATUS", "phase": "GITHUB_SOURCE", "reason": "Reading user-authorized GitHub startup documents"}
    try:
        report = project_start_report(data.get("userId", ""), data.get("repo", ""))
    except HTTPException as exc:
        report = "GitHub project startup could not be completed: " + str(exc.detail) + ". No repository or live state was inferred."
    except Exception:
        report = "GitHub source retrieval failed. No startup state was inferred."
    yield {"type": "DELTA", "text": report}
    yield {"type": "COMPLETED", "phase": "COMPLETE"}
