from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
import urllib.parse
import urllib.request
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

SESSION_COOKIE = "swrlz_session"
SESSION_TTL = 60 * 60 * 24 * 30
MAX_THREADS = 80
MAX_MESSAGES_PER_THREAD = 200
_MEM: dict[str, str] = {}


def _store_configured() -> bool:
    return bool((os.getenv("KV_REST_API_URL") or os.getenv("UPSTASH_REDIS_REST_URL")) and (os.getenv("KV_REST_API_TOKEN") or os.getenv("UPSTASH_REDIS_REST_TOKEN")))


def _store_url() -> str:
    return (os.getenv("KV_REST_API_URL") or os.getenv("UPSTASH_REDIS_REST_URL") or "").rstrip("/")


def _store_token() -> str:
    return os.getenv("KV_REST_API_TOKEN") or os.getenv("UPSTASH_REDIS_REST_TOKEN") or ""


def _redis(command: str, *args: str) -> Any:
    if not _store_configured():
        return None
    url = _store_url() + "/" + command.lower() + "/" + "/".join(urllib.parse.quote(str(a), safe="") for a in args)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + _store_token()})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("result") if isinstance(data, dict) else data


def get_json(key: str, default: Any = None) -> Any:
    try:
        raw = _redis("get", key) if _store_configured() else _MEM.get(key)
        if raw in (None, ""):
            return default
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return default


def set_json(key: str, value: Any, ttl: int | None = None) -> bool:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    try:
        if _store_configured():
            if ttl:
                _redis("set", key, raw, "EX", str(ttl))
            else:
                _redis("set", key, raw)
        else:
            _MEM[key] = raw
        return True
    except Exception:
        return False


def delete(key: str) -> None:
    try:
        if _store_configured():
            _redis("del", key)
        else:
            _MEM.pop(key, None)
    except Exception:
        _MEM.pop(key, None)


def _auth_secret() -> str:
    return os.getenv("SWRLZ_AUTH_SECRET", "").strip()


def _session_signature(session_id: str) -> str:
    return hmac.new(_auth_secret().encode(), session_id.encode(), hashlib.sha256).hexdigest()


def _session_cookie(session_id: str) -> str:
    return f"{session_id}.{_session_signature(session_id)}"


def _read_session(request: Request) -> dict[str, Any] | None:
    if not _auth_secret():
        return None
    raw = request.cookies.get(SESSION_COOKIE, "")
    try:
        session_id, sig = raw.split(".", 1)
    except ValueError:
        return None
    if not hmac.compare_digest(sig, _session_signature(session_id)):
        return None
    return get_json("swrlz:session:" + session_id)


def _set_session(response, user: dict[str, Any]) -> None:
    session_id = secrets.token_urlsafe(32)
    set_json("swrlz:session:" + session_id, user, SESSION_TTL)
    response.set_cookie(SESSION_COOKIE, _session_cookie(session_id), max_age=SESSION_TTL, httponly=True, secure=True, samesite="lax", path="/")


def _clear_session(response, request: Request) -> None:
    raw = request.cookies.get(SESSION_COOKIE, "")
    session_id = raw.split(".", 1)[0] if "." in raw else ""
    if session_id:
        delete("swrlz:session:" + session_id)
    response.delete_cookie(SESSION_COOKIE, path="/")


def current_user(request: Request) -> dict[str, Any] | None:
    return _read_session(request)


def _google_tokeninfo(token: str) -> dict[str, Any]:
    url = "https://oauth2.googleapis.com/tokeninfo?id_token=" + urllib.parse.quote(token.strip(), safe="")
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "swrlz-auth/1"})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("GOOGLE_TOKENINFO_INVALID")
    return data


def authenticate_google(token: str) -> dict[str, Any]:
    if not _auth_secret():
        raise ValueError("SWRLZ_AUTH_SECRET_NOT_CONFIGURED")
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    if not client_id:
        raise ValueError("GOOGLE_OAUTH_CLIENT_ID_NOT_CONFIGURED")
    claims = _google_tokeninfo(token)
    if claims.get("aud") != client_id:
        raise ValueError("GOOGLE_AUDIENCE_MISMATCH")
    if claims.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise ValueError("GOOGLE_ISSUER_INVALID")
    if str(claims.get("email_verified", "")).lower() != "true":
        raise ValueError("GOOGLE_EMAIL_NOT_VERIFIED")
    sub = str(claims.get("sub") or "").strip()
    email = str(claims.get("email") or "").strip().lower()
    if not sub or not email:
        raise ValueError("GOOGLE_IDENTITY_INCOMPLETE")
    now = time.time()
    existing = get_json("swrlz:user:" + sub, {}) or {}
    user = {"userId": sub, "provider": "google", "email": email, "name": claims.get("name") or email.split("@", 1)[0], "givenName": claims.get("given_name"), "familyName": claims.get("family_name"), "picture": claims.get("picture"), "emailVerified": True, "createdAt": existing.get("createdAt", now), "updatedAt": now, "profile": existing.get("profile") or {}, "settings": existing.get("settings") or {}, "organization": existing.get("organization") or {"id": "personal", "name": "Personal"}}
    set_json("swrlz:user:" + sub, user)
    return user


def auth_response(request: Request):
    user = current_user(request)
    return JSONResponse({"authenticated": bool(user), "persistentStore": _store_configured(), "googleConfigured": bool(os.getenv("GOOGLE_OAUTH_CLIENT_ID")), "user": user}, headers={"Cache-Control": "no-store"})


def login_response(request: Request, credential: str):
    try:
        user = authenticate_google(credential)
    except Exception as exc:
        return JSONResponse({"ok": False, "code": str(exc), "detail": "Google authentication could not be verified."}, status_code=401)
    response = JSONResponse({"ok": True, "user": user, "persistentStore": _store_configured()})
    _set_session(response, user)
    return response


def logout_response(request: Request):
    response = JSONResponse({"ok": True})
    _clear_session(response, request)
    return response


def load_user_data(user_id: str) -> dict[str, Any]:
    profile = get_json("swrlz:user:" + user_id, {}) or {}
    index = get_json("swrlz:user:" + user_id + ":thread-index", []) or []
    threads = []
    for thread_id in index[:MAX_THREADS]:
        thread = get_json("swrlz:user:" + user_id + ":thread:" + str(thread_id))
        if thread:
            threads.append(thread)
    threads.sort(key=lambda item: int(item.get("updatedAt", 0)), reverse=True)
    return {"profile": profile.get("profile") or {}, "settings": profile.get("settings") or {}, "organization": profile.get("organization") or {"id": "personal", "name": "Personal"}, "threads": threads, "persistentStore": _store_configured()}


def save_user_data(user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    existing = get_json("swrlz:user:" + user_id, {}) or {}
    existing["profile"] = dict(payload.get("profile") or existing.get("profile") or {})
    existing["settings"] = dict(payload.get("settings") or existing.get("settings") or {})
    existing["organization"] = dict(payload.get("organization") or existing.get("organization") or {"id": "personal", "name": "Personal"})
    existing["updatedAt"] = time.time()
    set_json("swrlz:user:" + user_id, existing)
    threads = payload.get("threads") or []
    if not isinstance(threads, list):
        threads = []
    ids = []
    for thread in threads[:MAX_THREADS]:
        if not isinstance(thread, dict) or not thread.get("id"):
            continue
        clean = dict(thread)
        clean["messages"] = list(clean.get("messages") or [])[-MAX_MESSAGES_PER_THREAD:]
        clean["updatedAt"] = int(clean.get("updatedAt") or time.time() * 1000)
        tid = str(clean["id"])
        ids.append(tid)
        set_json("swrlz:user:" + user_id + ":thread:" + tid, clean)
    set_json("swrlz:user:" + user_id + ":thread-index", ids[:MAX_THREADS])
    return load_user_data(user_id)
