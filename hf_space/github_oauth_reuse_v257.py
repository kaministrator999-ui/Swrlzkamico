"""Account-scoped GitHub OAuth bridge, compatible with the existing encrypted Chat connection.

Only the bounded, explicitly approved Swrlzing-core TXT sandbox can write. A
GitHub login, an OAuth scope, and repository push permission are different facts.
This module never passes GitHub bearer tokens to the browser or the LALM.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
from urllib.parse import urlencode, urlparse

import requests
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter()
OWNER = "kaministrator999-ui"
REPO = "Swrlzing-core"
TARGET = OWNER + "/" + REPO
GITHUB_API = "https://api.github.com"
SCOPE_READ = "read:user"
SCOPE_SANDBOX = "read:user public_repo"
_account_lookup = None


def install(app, account_lookup):
    global _account_lookup
    _account_lookup = account_lookup
    app.include_router(router)


def _account(request):
    if _account_lookup is None:
        raise HTTPException(503, "GitHub account integration unavailable")
    _sid, user = _account_lookup(request)
    if not isinstance(user, dict) or not str(user.get("id") or "").startswith("google:"):
        raise HTTPException(401, "Sign in with Google first")
    return user


def _settings():
    # Keep these exact names: existing OAuth records use these credentials.
    return {
        "client": os.getenv("SWRLZ_GITHUB_OAUTH_CLIENT_ID", "").strip(),
        "secret": os.getenv("SWRLZ_GITHUB_OAUTH_CLIENT_SECRET", "").strip(),
        "callback": os.getenv("SWRLZ_GITHUB_OAUTH_CALLBACK_URL", "").strip(),
        "fernet": os.getenv("SWRLZ_GITHUB_ENCRYPTION_KEY", "").strip(),
        "redis": os.getenv("UPSTASH_REDIS_REST_URL", "").strip().rstrip("/"),
        "redis_token": os.getenv("UPSTASH_REDIS_REST_TOKEN", "").strip(),
    }


def _config():
    cfg = _settings()
    if not all(cfg.values()):
        raise HTTPException(503, "Existing GitHub OAuth connection configuration unavailable")
    callback = urlparse(cfg["callback"])
    redis = urlparse(cfg["redis"])
    if (callback.scheme != "https" or not callback.netloc or callback.username
            or callback.password or callback.query or callback.fragment
            or not callback.path.endswith("/api/github/callback")
            or redis.scheme != "https" or not redis.netloc):
        raise HTTPException(503, "GitHub OAuth callback or secure storage misconfigured")
    try:
        Fernet(cfg["fernet"].encode("ascii"))
    except (ValueError, TypeError):
        raise HTTPException(503, "Stored GitHub connection encryption unavailable") from None
    return cfg


def _redis(cfg, *command):
    try:
        response = requests.post(
            cfg["redis"], json=list(command),
            headers={"Authorization": "Bearer " + cfg["redis_token"]},
            timeout=12,
        )
        response.raise_for_status()
        value = response.json()
        if "error" in value:
            raise ValueError("Redis reported an error")
        return value.get("result")
    except (requests.RequestException, ValueError):
        raise HTTPException(503, "Encrypted GitHub account storage unavailable") from None


def _record_key(user_id):
    # Identical to the existing GitHub connection's durable key scheme.
    return "swrlz:github:account:" + hashlib.sha256(user_id.encode("utf-8")).hexdigest()


def _state_key(state):
    return "swrlz:github:oauth:" + hashlib.sha256(state.encode("ascii")).hexdigest()


def _load(cfg, user_id):
    encrypted = _redis(cfg, "GET", _record_key(user_id))
    if not encrypted:
        return None
    try:
        raw = Fernet(cfg["fernet"].encode("ascii")).decrypt(encrypted.encode("ascii"))
        record = json.loads(raw)
        if record.get("owner") != user_id or not record.get("token"):
            raise ValueError("Invalid account-bound token record")
        return record
    except (InvalidToken, ValueError, TypeError, KeyError):
        raise HTTPException(503, "Stored GitHub connection could not be verified") from None


def _save(cfg, user_id, record):
    # Preserve the original OAuth schema for backward compatibility.
    item = {
        "owner": user_id,
        "token": record["token"],
        "githubId": int(record["githubId"]),
        "login": str(record["login"])[:100],
        "repo": str(record.get("repo") or "")[:202],
        "scopes": str(record.get("scopes") or "")[:400],
        "connectedAt": int(record.get("connectedAt") or __import__("time").time()),
    }
    value = Fernet(cfg["fernet"].encode("ascii")).encrypt(
        json.dumps(item, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    if _redis(cfg, "SET", _record_key(user_id), value) != "OK":
        raise HTTPException(503, "GitHub account authorization could not be stored")


def _api(token, path):
    # No URL, host or path comes directly from the user.
    assert path in ("/user", "/repos/" + TARGET,
                    "/user/repos?sort=updated&per_page=60&affiliation=owner,collaborator,organization_member")
    try:
        response = requests.get(
            GITHUB_API + path,
            headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=14,
        )
        if response.status_code in (401, 403, 404):
            raise HTTPException(response.status_code, "GitHub connection or repository access unavailable")
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        raise HTTPException(502, "GitHub permission verification failed") from None


def _github_scopes(record):
    return set(re.split(r"[\s,]+", str(record.get("scopes") or "").strip()))


def _write_state(record):
    """Check the existing OAuth grant and repo role, not a separate token."""
    if not record:
        return {"allowed": False, "reason": "GITHUB_NOT_CONNECTED", "authorizeUrl": "/api/github/start?access=public-write"}
    if str(record.get("repo") or "").casefold() != TARGET.casefold():
        return {"allowed": False, "reason": "SANDBOX_REPOSITORY_NOT_SELECTED"}
    # The owner login is a verified GitHub OAuth /user identity, never a chat claim.
    if str(record.get("login") or "").casefold() != OWNER.casefold():
        return {"allowed": False, "reason": "SANDBOX_OWNER_REQUIRED"}
    scopes = _github_scopes(record)
    if not ({"repo", "public_repo"} & scopes):
        return {"allowed": False, "reason": "GITHUB_WRITE_SCOPE_REQUIRED",
                "authorizeUrl": "/api/github/start?access=public-write"}
    info = _api(record["token"], "/repos/" + TARGET)
    if not isinstance(info, dict) or str(info.get("full_name") or "").casefold() != TARGET.casefold():
        return {"allowed": False, "reason": "SANDBOX_REPOSITORY_UNVERIFIED"}
    if info.get("private"):
        return {"allowed": False, "reason": "SANDBOX_MUST_BE_PUBLIC"}
    permissions = info.get("permissions") if isinstance(info.get("permissions"), dict) else {}
    if not (permissions.get("push") or permissions.get("admin") or permissions.get("maintain")):
        return {"allowed": False, "reason": "GITHUB_REPOSITORY_WRITE_PERMISSION_REQUIRED"}
    return {"allowed": True, "reason": "GITHUB_WRITE_PERMISSION_VERIFIED"}


def authorize_sandbox_write(user):
    """Return an existing encrypted-account token only after positive authorization."""
    if not isinstance(user, dict) or not str(user.get("id") or "").startswith("google:"):
        raise HTTPException(401, "Sign in with Google first")
    cfg = _config()
    record = _load(cfg, user["id"])
    state = _write_state(record)
    if not state["allowed"]:
        raise HTTPException(403, state["reason"])
    return record["token"]


@router.get("/api/github/status")
def status(request: Request):
    user = _account(request)
    cfg = _config()
    record = _load(cfg, user["id"])
    return {
        "configured": True, "linked": bool(record), "durable": True,
        "capabilityStage": "read-plus-sandbox-txt-create",
        "login": record.get("login") if record else None,
        "repo": record.get("repo") if record else None,
        "scope": SCOPE_READ,
        "writeAction": "sandbox-create-txt",
    }


@router.get("/api/github/repositories")
def repositories(request: Request):
    user = _account(request)
    record = _load(_config(), user["id"])
    if not record:
        raise HTTPException(409, "Connect GitHub first")
    data = _api(record["token"], "/user/repos?sort=updated&per_page=60&affiliation=owner,collaborator,organization_member")
    if not isinstance(data, list):
        raise HTTPException(502, "GitHub repository list unavailable")
    return {"repositories": [{
        "fullName": str(x.get("full_name") or "")[:202],
        "private": bool(x.get("private")),
        "defaultBranch": str(x.get("default_branch") or "main"),
    } for x in data if isinstance(x, dict)][:60]}


@router.post("/api/github/default-repo")
async def choose_repository(request: Request):
    user = _account(request)
    cfg = _config()
    _origin_guard(request, cfg)
    record = _load(cfg, user["id"])
    if not record:
        raise HTTPException(409, "Connect GitHub first")
    body = await request.json()
    if not isinstance(body, dict) or body.get("repository") != TARGET:
        # This narrow adapter is only for the fixed sandbox write/read repository.
        raise HTTPException(422, "Only the named GitHub sandbox repository is supported")
    info = _api(record["token"], "/repos/" + TARGET)
    if not isinstance(info, dict) or info.get("full_name") != TARGET:
        raise HTTPException(404, "Sandbox GitHub repository not available")
    record["repo"] = TARGET
    _save(cfg, user["id"], record)
    return {"ok": True, "repo": TARGET}


def _origin_guard(request, cfg):
    origin = request.headers.get("origin", "")
    callback = urlparse(cfg["callback"])
    if origin != "https://" + callback.netloc:
        raise HTTPException(403, "GitHub account action origin rejected")


@router.get("/api/github/start")
def start(request: Request, access: str = "read"):
    user = _account(request)
    cfg = _config()
    if access not in ("read", "public-write"):
        raise HTTPException(422, "Unsupported OAuth access level")
    # Explicitly requesting public-write is still not a write instruction.
    if access == "public-write":
        record = _load(cfg, user["id"])
        if record and record.get("repo", "").casefold() != TARGET.casefold():
            raise HTTPException(409, "Select Swrlzing-core before requesting write permission")
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(48)
    challenge = __import__("base64").urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).decode("ascii").rstrip("=")
    saved = {"owner": user["id"], "verifier": verifier, "access": access}
    if _redis(cfg, "SET", _state_key(state), json.dumps(saved), "EX", 600, "NX") != "OK":
        raise HTTPException(503, "GitHub OAuth flow unavailable")
    url = "https://github.com/login/oauth/authorize?" + urlencode({
        "client_id": cfg["client"], "redirect_uri": cfg["callback"],
        "scope": SCOPE_READ if access == "read" else SCOPE_SANDBOX,
        "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
    })
    response = RedirectResponse(url, status_code=303)
    response.set_cookie("swrlz_github_oauth", state, httponly=True, secure=True,
                        samesite="lax", max_age=600, path="/api/github/callback")
    return response


@router.get("/api/github/callback")
def callback(request: Request, code: str = "", state: str = "", error: str = ""):
    user = _account(request)
    cfg = _config()
    cookie = request.cookies.get("swrlz_github_oauth", "")
    if not state or not cookie or not secrets.compare_digest(cookie, state):
        raise HTTPException(403, "GitHub OAuth state mismatch")
    encoded = _redis(cfg, "GETDEL", _state_key(state))
    try:
        pending = json.loads(encoded or "null")
    except (ValueError, TypeError):
        pending = None
    if not isinstance(pending, dict) or pending.get("owner") != user["id"] or pending.get("access") not in ("read", "public-write"):
        raise HTTPException(403, "GitHub authorization expired or belongs to another user")
    if error or not code or len(code) > 512:
        raise HTTPException(400, "GitHub authorization declined or expired")
    try:
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            data={"client_id": cfg["client"], "client_secret": cfg["secret"],
                  "code": code, "redirect_uri": cfg["callback"],
                  "code_verifier": pending["verifier"]},
            headers={"Accept": "application/json"}, timeout=14,
        )
        response.raise_for_status()
        result = response.json()
        token = result.get("access_token")
        if not isinstance(token, str) or not 0 < len(token) <= 1024 or result.get("error"):
            raise ValueError("Invalid GitHub OAuth response")
    except (requests.RequestException, ValueError, KeyError):
        raise HTTPException(502, "GitHub OAuth authorization failed") from None
    identity = _api(token, "/user")
    if not isinstance(identity, dict) or not identity.get("id") or not identity.get("login"):
        raise HTTPException(502, "GitHub identity could not be verified")
    old = _load(cfg, user["id"])
    selected = old.get("repo", "") if old and old.get("githubId") == int(identity["id"]) else ""
    grants = str(result.get("scope") or "")
    # Never count the requested scope as granted; inspect exchange response only.
    _save(cfg, user["id"], {
        "token": token, "githubId": identity["id"], "login": identity["login"],
        "repo": selected, "scopes": grants,
    })
    response = RedirectResponse("/chat/§wyrlz#github=connected", status_code=303)
    response.delete_cookie("swrlz_github_oauth", path="/api/github/callback")
    return response


@router.post("/api/github/disconnect")
def disconnect(request: Request):
    user = _account(request)
    cfg = _config()
    _origin_guard(request, cfg)
    _redis(cfg, "DEL", _record_key(user["id"]))
    return {"ok": True, "linked": False}


@router.get("/api/github/sandbox/write-status")
def sandbox_write_status(request: Request):
    user = _account(request)
    record = _load(_config(), user["id"])
    permission = _write_state(record)
    return {
        "linked": bool(record),
        "repo": record.get("repo") if record else None,
        "operation": "CREATE_FILE",
        "target": TARGET,
        "pathPrefix": "write-action-tests/",
        "allowed": permission["allowed"],
        "reason": permission["reason"],
        "authorizeUrl": permission.get("authorizeUrl"),
    }
