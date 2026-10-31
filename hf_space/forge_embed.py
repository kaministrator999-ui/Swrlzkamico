"""Account pairing and short-lived live §E capabilities.

Only encrypted records use the existing Redis transport. Account credentials stay
inside Chat-origin memory; the §E parent receives a different, narrow host token.
No client flag, historical message or model dictionary is an editor capability.
"""
from __future__ import annotations

import base64
import copy
from dataclasses import dataclass, field
import hashlib
import json
import math
import re
import secrets
import time
from typing import Any

from cryptography.fernet import Fernet
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response

import account_chat_store as accounts
import github_connection as gh

SCHEMA = "swrlz-forge-chat-v1"
CHAT_ORIGIN = "https://kamiloki-swyrlz.hf.space"
PARENT_ORIGINS = frozenset({"https://kamiloki-swrlz-forge-moba.hf.space",
                            "https://kamiloki-swrlz-forge-moba.static.hf.space"})
PAIR_TTL = 300
SESSION_TTL = 3600
REMEMBER_TTL = 7 * 86400
REMEMBER_COOKIE = "swrlz_forge_remember"
PRESENCE_TTL = 30
LEASE_TTL = 20
BATCH_TTL = 300
DESIGN_TTL = 900  # bounded owner-approved window; heartbeat/scene validation remains mandatory
MAX_CONTEXT_BYTES = 32768
MAX_OPERATIONS = 16
MAX_RECORD_BYTES = 196608
_HEX = re.compile(r"^[0-9a-f]{32}$")
_BINDING = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
_PKCE = re.compile(r"^[A-Za-z0-9_-]{43,128}$")
_CHALLENGE = re.compile(r"^[A-Za-z0-9_-]{43}$")
_TOKEN = re.compile(r"^(sfe1|sfh1|sfp1|sfr1|sfm1)_[A-Za-z0-9_-]{43}$")
_TOKEN_TEXT = re.compile(r"\b(?:sfe1|sfh1|sfp1|sfr1|sfm1)_[A-Za-z0-9_-]{43}\b")
_SENSITIVE_KEYS = frozenset({"authorization", "credential", "credentials", "cookie", "cookies",
                            "token", "hosttoken", "receiptnonce", "sid", "sessionid", "googleidtoken"})
_SEAL = object()
_legacy_authenticate = None
_chat_origin = CHAT_ORIGIN
_parent_origins = PARENT_ORIGINS
_diagnostic_hook = None
router = APIRouter()

# Every key belongs to the same Redis hash slot; comparison and publication are
# one transaction even when the configured Redis service uses clustering.
_TX = """-- swrlz-forge-embed-transaction-v1
local expected=cjson.decode(ARGV[1]);
for _,item in ipairs(expected) do
  if redis.call('GET',KEYS[item[1]])~=item[2] then return 0 end;
end;
local writes=cjson.decode(ARGV[2]);
for _,item in ipairs(writes) do redis.call('SET',KEYS[item[1]],item[2],'EX',item[3]); end;
local deletes=cjson.decode(ARGV[3]);
for _,index in ipairs(deletes) do redis.call('DEL',KEYS[index]); end;
return 1
"""


def _now():
    return time.time()


def _error(status, code):
    _observe("boundary.rejected", status=status, code=code)
    raise HTTPException(status, code)


def _observe(event, **fields):
    """Optional bounded camera; never receives accounts, payloads or grants."""
    if _diagnostic_hook is None:
        return
    allowed = {"status", "code", "pairId", "leaseId", "batchId", "proposalId", "operationCount", "receiptCount"}
    document = {key: value for key, value in fields.items() if key in allowed}
    document["schema"] = "swrlz-forge-boundary-camera-v1"
    document["event"] = event
    try:
        _diagnostic_hook(document)
    except Exception:
        # Observation is not part of authorization or transaction success.
        pass


def _key(kind, value):
    return "swrlz:forge:{embed-v1}:" + kind + ":" + hashlib.sha256(str(value).encode()).hexdigest()


def _token(kind):
    return kind + "_" + secrets.token_urlsafe(32)


def _encode(value):
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()
    if len(raw) > MAX_RECORD_BYTES:
        _error(413, "FORGE_RECORD_TOO_LARGE")
    return Fernet(accounts._config()["fernet"].encode("ascii")).encrypt(raw).decode("ascii")


def _read_key(key):
    c = accounts._config()
    raw = gh._redis(c, "GET", key)
    if raw is None:
        return None, None
    try:
        value = accounts._decrypt(c, raw)
    except HTTPException:
        _error(503, "FORGE_STORED_RECORD_INVALID")
    if (not isinstance(value, dict) or value.get("schema") != SCHEMA
            or value.get("recordKey") != key):
        _error(503, "FORGE_STORED_RECORD_INVALID")
    return value, raw


def _read(kind, value):
    return _read_key(_key(kind, value))


def _ttl(record, cap=SESSION_TTL):
    return max(1, min(cap, int(math.ceil(float(record["expiresAt"]) - _now()))))


def _txn(expected, writes=(), deletes=()):
    keys = list(dict.fromkeys([k for k, _ in expected] + [k for k, _, _ in writes] + list(deletes)))
    index = {key: n + 1 for n, key in enumerate(keys)}
    e = [[index[key], raw if raw is not None else False] for key, raw in expected]
    # Bind ciphertext to its exact hashed key as well as its schema/kind. A
    # copied encrypted record must not turn another bearer into its owner.
    w = [[index[key], _encode({**value, "recordKey": key}), ttl] for key, value, ttl in writes]
    result = gh._redis(accounts._config(), "EVAL", _TX, str(len(keys)), *keys,
                       json.dumps(e, separators=(",", ":")), json.dumps(w, separators=(",", ":")),
                       json.dumps([index[key] for key in deletes], separators=(",", ":")))
    if (type(result) is int and result == 1) or result == "1":
        return True
    if (type(result) is int and result == 0) or result == "0":
        return False
    _error(503, "FORGE_ATOMIC_COMMIT_NOT_CONFIRMED")


def _new(kind, identity, record, ttl):
    key = _key(kind, identity)
    if not _txn([(key, None)], [(key, record, ttl)]):
        _error(409, "FORGE_RECORD_CHANGED")


def _id(value, name):
    if not isinstance(value, str) or not 0 < len(value) <= 160 or any(ord(c) < 32 for c in value):
        _error(400, "FORGE_INVALID_" + name.upper())
    return value


def _binding(value):
    if not isinstance(value, str) or not _BINDING.fullmatch(value):
        _error(400, "FORGE_INVALID_BINDING")
    return value


def _safe_json(value, maximum=MAX_CONTEXT_BYTES):
    def visit(item, depth=0):
        if depth > 12:
            _error(400, "FORGE_CONTEXT_TOO_DEEP")
        if item is None or isinstance(item, (bool, str)):
            return
        if type(item) in (int, float):
            try:
                finite = math.isfinite(item)
            except OverflowError:
                finite = False
            if not finite:
                _error(400, "FORGE_NONFINITE_VALUE")
            return
        if isinstance(item, list):
            if len(item) > 512:
                _error(413, "FORGE_CONTEXT_TOO_LARGE")
            for child in item:
                visit(child, depth + 1)
            return
        if isinstance(item, dict):
            if len(item) > 256:
                _error(413, "FORGE_CONTEXT_TOO_LARGE")
            for key, child in item.items():
                if (not isinstance(key, str) or key in ("__proto__", "constructor", "prototype")
                        or key.lower().replace("_", "") in _SENSITIVE_KEYS):
                    _error(400, "FORGE_CONTEXT_CREDENTIAL_OR_PROTOTYPE_FIELD")
                visit(child, depth + 1)
            return
        _error(400, "FORGE_INVALID_JSON_VALUE")
    visit(value)
    try:
        raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False).encode()
    except (ValueError, UnicodeError, OverflowError):
        _error(400, "FORGE_INVALID_JSON_VALUE")
    if len(raw) > maximum:
        _error(413, "FORGE_CONTEXT_TOO_LARGE")
    return copy.deepcopy(value), hashlib.sha256(raw).hexdigest()


async def _body(request):
    if not request.headers.get("content-type", "").lower().startswith("application/json"):
        _error(415, "FORGE_JSON_REQUIRED")
    chunks = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_RECORD_BYTES:
            _error(413, "FORGE_REQUEST_TOO_LARGE")
        chunks.append(chunk)
    try:
        value = json.loads(b"".join(chunks))
    except (ValueError, UnicodeError):
        _error(400, "FORGE_INVALID_JSON")
    if not isinstance(value, dict):
        _error(400, "FORGE_JSON_OBJECT_REQUIRED")
    return value


def _response(value, status=200):
    return JSONResponse(value, status_code=status, headers={"Cache-Control": "no-store"})


def _remember_cookie(response, token=""):
    # CHIPS keeps this HttpOnly credential on the Chat origin, partitioned by
    # the top-level §e site. Parent scripts never receive or read it.
    # Browsers lacking partitioned cookies continue to use manual pairing.
    value = (REMEMBER_COOKIE + "=" + token + "; Path=/api/forge/embed;"
             + " HttpOnly; Secure; SameSite=None; Partitioned;"
             + (" Max-Age=" + str(REMEMBER_TTL) if token else " Max-Age=0"))
    response.headers.append("Set-Cookie", value)
    return response


def _new_embed_session(parent, host, channel):
    token = _token("sfe1")
    session = {"schema": SCHEMA, "kind": "session", "audience": "chat-embed",
               "sessionId": secrets.token_hex(16),
               "owner": parent["owner"], "parentSid": parent["parentSid"],
               "parentOrigin": parent["parentOrigin"],
               "hostId": host, "channelId": channel,
               "activePresenceId": "", "activeLeaseId": "",
               "expiresAt": _now() + SESSION_TTL}
    return token, session


def require_write_origin(request):
    if request.headers.get("origin", "") != _chat_origin:
        _error(403, "FORGE_CHAT_ORIGIN_REQUIRED")


def _chat_read_origin(request):
    origin = request.headers.get("origin")
    if origin is not None and origin != _chat_origin:
        _error(403, "FORGE_CHAT_ORIGIN_REQUIRED")


def _live_session(key):
    record, raw = _read_key(key)
    if (not record or record.get("kind") != "session" or record.get("audience") != "chat-embed"
            or float(record.get("expiresAt", 0)) <= _now()):
        _error(401, "FORGE_EMBED_SESSION_INVALID")
    user = accounts.load_login(record.get("parentSid"))
    if not user or user.get("id") != record.get("owner"):
        _error(401, "FORGE_PARENT_LOGIN_REVOKED")
    return record, raw, user


def require_embed(request):
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer sfe1_"):
        _error(401, "FORGE_EMBED_CREDENTIAL_REQUIRED")
    token = authorization[7:]
    if not _TOKEN.fullmatch(token) or not token.startswith("sfe1_"):
        _error(401, "FORGE_EMBED_CREDENTIAL_INVALID")
    _chat_read_origin(request)
    key = _key("session", token)
    record, raw, user = _live_session(key)
    return {"key": key, "record": record, "raw": raw, "user": user}


def resolve_account(request):
    """No supplied credential means no embed account; invalid ones never fall back."""
    if "authorization" not in request.headers:
        return None, None
    session = require_embed(request)
    return "forge:" + session["record"]["sessionId"], copy.deepcopy(session["user"])


@router.post("/api/forge/embed/pair")
async def pair(request: Request):
    require_write_origin(request)
    body = await _body(request)
    origin = body.get("parentOrigin")
    if origin not in _parent_origins:
        _error(403, "FORGE_PARENT_ORIGIN_NOT_ALLOWED")
    host, channel = _binding(body.get("hostId")), _binding(body.get("channelId"))
    challenge = body.get("challenge")
    if not isinstance(challenge, str) or not _CHALLENGE.fullmatch(challenge):
        _error(400, "FORGE_INVALID_PKCE_CHALLENGE")
    pair_id = secrets.token_hex(16)
    # The browser can lose window.opener when a mobile popup becomes a new tab.
    # A separate random, short-lived proof belongs ONLY to the original Chat iframe.
    recovery_code = secrets.token_hex(6)
    record = {"schema": SCHEMA, "kind": "pair", "parentOrigin": origin, "hostId": host,
              "channelId": channel, "challenge": challenge, "approved": False,
              "recoveryHash": hashlib.sha256(recovery_code.encode("ascii")).hexdigest(),
              "expiresAt": _now() + PAIR_TTL}
    _new("pair", pair_id, record, PAIR_TTL)
    _observe("pair.created", pairId=pair_id)
    binding = {k: record[k] for k in ("parentOrigin", "hostId", "channelId")}
    return _response({"pairId": pair_id, "loginUrl": "/forge/login?pairId=" + pair_id,
                      "expiresAt": record["expiresAt"], "binding": binding,
                      "recoveryCode": recovery_code})


def _pair(pair_id):
    if not isinstance(pair_id, str) or not _HEX.fullmatch(pair_id):
        _error(404, "FORGE_PAIR_NOT_FOUND")
    record, raw = _read("pair", pair_id)
    if not record or record.get("kind") != "pair" or record.get("expiresAt", 0) <= _now():
        _error(404, "FORGE_PAIR_NOT_FOUND")
    return record, raw


@router.get("/api/forge/embed/pair/{pair_id}")
def pair_status(pair_id: str):
    record, _ = _pair(pair_id)
    return _response({"pairId": pair_id, **{k: record[k] for k in
                      ("parentOrigin", "hostId", "channelId", "approved", "expiresAt")}})


@router.post("/api/forge/embed/pair/approve")
async def approve(request: Request):
    require_write_origin(request)
    if request.headers.get("authorization"):
        _error(403, "FORGE_FIRST_PARTY_LOGIN_REQUIRED")
    if _legacy_authenticate is None:
        _error(503, "FORGE_ACCOUNT_BRIDGE_UNAVAILABLE")
    sid, user = _legacy_authenticate(request)
    if (not isinstance(user, dict) or not accounts.OWNER.fullmatch(str(user.get("id") or ""))
            or not isinstance(sid, str) or not accounts.SID.fullmatch(sid)):
        _error(401, "FORGE_GOOGLE_LOGIN_REQUIRED")
    verified = accounts.load_login(sid)
    if not verified or verified.get("id") != user["id"]:
        _error(401, "FORGE_GOOGLE_LOGIN_REQUIRED")
    body = await _body(request)
    pair_id = body.get("pairId")
    record, raw = _pair(pair_id)
    if any(body.get(k) != record[k] for k in ("parentOrigin", "hostId", "channelId")):
        _error(403, "FORGE_PAIR_OPENER_BINDING_MISMATCH")
    # Optional recovery path: when the opener was lost, the user types the
    # separate one-time proof visible only in the original Chat iframe.
    # Absence retains the existing verified-opener popup behavior.
    if "recoveryCode" in body:
        proof = body["recoveryCode"]
        if (not isinstance(proof, str) or not re.fullmatch(r"[a-f0-9]{12}", proof)
                or not secrets.compare_digest(hashlib.sha256(proof.encode("ascii")).hexdigest(),
                                              record.get("recoveryHash", ""))):
            _error(403, "FORGE_PAIR_RECOVERY_CODE_INVALID")
    if record.get("approved"):
        _error(409, "FORGE_PAIR_ALREADY_APPROVED")
    new = {**record, "approved": True, "owner": user["id"], "parentSid": sid}
    if not _txn([(_key("pair", pair_id), raw)], [(_key("pair", pair_id), new, _ttl(record, PAIR_TTL))]):
        _error(409, "FORGE_PAIR_CHANGED")
    _observe("pair.approved", pairId=pair_id)
    return _response({"approved": True})


@router.post("/api/forge/embed/pair/exchange")
async def exchange(request: Request):
    require_write_origin(request)
    body = await _body(request)
    pair_id, verifier = body.get("pairId"), body.get("verifier")
    record, raw = _pair(pair_id)
    if not isinstance(verifier, str) or not _PKCE.fullmatch(verifier):
        _error(401, "FORGE_PKCE_VERIFIER_INVALID")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode()
    if not secrets.compare_digest(challenge, record["challenge"]):
        _error(401, "FORGE_PKCE_VERIFIER_INVALID")
    if any(body.get(k) != record[k] for k in ("hostId", "channelId")):
        _error(403, "FORGE_PAIR_BINDING_MISMATCH")
    if not record.get("approved"):
        _error(409, "FORGE_PAIR_NOT_APPROVED")
    user = accounts.load_login(record.get("parentSid"))
    if not user or user.get("id") != record.get("owner"):
        _error(401, "FORGE_PARENT_LOGIN_REVOKED")
    token, session = _new_embed_session(record, record["hostId"], record["channelId"])
    remember = _token("sfm1")
    remember_record = {"schema": SCHEMA, "kind": "remember",
                       "parentSid": record["parentSid"], "owner": user["id"],
                       "parentOrigin": record["parentOrigin"],
                       "expiresAt": _now() + REMEMBER_TTL}
    key, remember_key = _key("session", token), _key("remember", remember)
    if not _txn([(_key("pair", pair_id), raw), (key, None), (remember_key, None)],
                [(key, session, SESSION_TTL), (remember_key, remember_record, REMEMBER_TTL)],
                [_key("pair", pair_id)]):
        _error(409, "FORGE_PAIR_ALREADY_REDEEMED")
    _observe("pair.exchanged", pairId=pair_id)
    response = _response({"token": token, "user": user, "expiresAt": session["expiresAt"],
                          **{k: session[k] for k in ("parentOrigin", "hostId", "channelId")}})
    return _remember_cookie(response, remember)


@router.post("/api/forge/embed/resume")
async def resume(request: Request):
    require_write_origin(request)
    body = await _body(request)
    remember = request.cookies.get(REMEMBER_COOKIE, "")
    if not isinstance(remember, str) or not re.fullmatch(r"sfm1_[A-Za-z0-9_-]{43}", remember):
        _error(401, "FORGE_REMEMBER_COOKIE_REQUIRED")
    record, raw = _read("remember", remember)
    if not record or record.get("kind") != "remember" or record.get("expiresAt", 0) <= _now():
        _error(401, "FORGE_REMEMBER_SESSION_EXPIRED")
    origin = body.get("parentOrigin")
    if origin not in _parent_origins or record.get("parentOrigin") != origin:
        _error(403, "FORGE_PARENT_ORIGIN_NOT_ALLOWED")
    host, channel = _binding(body.get("hostId")), _binding(body.get("channelId"))
    user = accounts.load_login(record.get("parentSid"))
    if not user or user.get("id") != record.get("owner"):
        _error(401, "FORGE_PARENT_LOGIN_REVOKED")
    token, session = _new_embed_session(record, host, channel)
    _new("session", token, session, SESSION_TTL)
    # Fresh Chat-origin bearer lives in memory only; cookie never reaches
    # Javascript, URLs, exported chat messages or the §e parent.
    return _response({"token": token, "user": user, "expiresAt": session["expiresAt"],
                      **{k: session[k] for k in ("parentOrigin", "hostId", "channelId")}})


@router.post("/api/forge/embed/logout")
def logout(request: Request):
    require_write_origin(request)
    session = require_embed(request)
    remember = request.cookies.get(REMEMBER_COOKIE, "")
    remember_key = _key("remember", remember) if isinstance(remember, str) and re.fullmatch(r"sfm1_[A-Za-z0-9_-]{43}", remember) else None
    record, raw = _read_key(remember_key) if remember_key else (None, None)
    owned = bool(record and record.get("kind") == "remember"
                 and record.get("owner") == session["user"]["id"]
                 and record.get("parentSid") == session["record"]["parentSid"])
    expected = [(session["key"], session["raw"])] + ([(remember_key, raw)] if owned else [])
    deleted = [session["key"]] + ([remember_key] if owned else [])
    if not _txn(expected, deletes=deleted):
        _error(409, "FORGE_SESSION_CHANGED")
    return _remember_cookie(_response({"ok": True}))


@router.post("/api/forge/embed/presence")
async def presence(request: Request):
    require_write_origin(request)
    session = require_embed(request)
    body = await _body(request)
    thread, project = _id(body.get("threadId"), "thread"), _id(body.get("projectId"), "project")
    context, digest = _safe_json(body.get("context"))
    if not isinstance(context, dict):
        _error(400, "FORGE_CONTEXT_OBJECT_REQUIRED")
    ticket, presence_id = _token("sfp1"), secrets.token_hex(16)
    record = {"schema": SCHEMA, "kind": "presence", "presenceId": presence_id,
              "sessionKey": session["key"], "owner": session["user"]["id"],
              **{k: session["record"][k] for k in ("parentOrigin", "hostId", "channelId")},
              "threadId": thread, "projectId": project, "context": context, "contextHash": digest,
              "expiresAt": min(_now() + PRESENCE_TTL, session["record"]["expiresAt"])}
    new_session = {**session["record"], "activePresenceId": presence_id, "activeLeaseId": ""}
    ticket_key = _key("presence", ticket)
    if not _txn([(session["key"], session["raw"]), (ticket_key, None)],
                [(session["key"], new_session, _ttl(new_session)), (ticket_key, record, PRESENCE_TTL)]):
        _error(409, "FORGE_SESSION_CHANGED")
    return _response({"ticket": ticket, "expiresAt": record["expiresAt"],
                      **{k: record[k] for k in ("parentOrigin", "hostId", "channelId", "threadId", "projectId")}})


def _host_origin(request, expected=None):
    origin = request.headers.get("origin", "")
    if origin not in _parent_origins or (expected is not None and origin != expected):
        _error(403, "FORGE_HOST_ORIGIN_REQUIRED")
    return origin


@router.post("/api/forge/embed/host/activate")
async def activate(request: Request):
    origin = _host_origin(request)
    body = await _body(request)
    ticket = body.get("ticket")
    if not isinstance(ticket, str) or not ticket.startswith("sfp1_") or not _TOKEN.fullmatch(ticket):
        _error(401, "FORGE_PRESENCE_TICKET_INVALID")
    record, raw = _read("presence", ticket)
    if not record or record.get("kind") != "presence" or record.get("expiresAt", 0) <= _now():
        _error(401, "FORGE_PRESENCE_TICKET_INVALID")
    if origin != record["parentOrigin"] or body.get("visible") is not True:
        _error(403, "FORGE_VISIBLE_HOST_REQUIRED")
    if any(body.get(k) != record[k] for k in ("hostId", "channelId", "threadId", "projectId")):
        _error(403, "FORGE_PRESENCE_BINDING_MISMATCH")
    context, digest = _safe_json(body.get("context"))
    if digest != record["contextHash"]:
        _error(409, "FORGE_CONTEXT_CHANGED")
    session, session_raw, _ = _live_session(record["sessionKey"])
    if session.get("activePresenceId") != record["presenceId"]:
        _error(409, "FORGE_PRESENCE_SUPERSEDED")
    lease_id, token = secrets.token_hex(16), _token("sfh1")
    lease = {**record, "kind": "lease", "leaseId": lease_id,
             "hostTokenHash": hashlib.sha256(token.encode()).hexdigest(),
             "expiresAt": min(_now() + LEASE_TTL, session["expiresAt"])}
    session_new = {**session, "activePresenceId": "", "activeLeaseId": lease_id}
    ticket_key, lease_key = _key("presence", ticket), _key("lease", lease_id)
    if not _txn([(ticket_key, raw), (record["sessionKey"], session_raw), (lease_key, None)],
                [(record["sessionKey"], session_new, _ttl(session_new)), (lease_key, lease, 60)], [ticket_key]):
        _error(409, "FORGE_PRESENCE_ALREADY_USED")
    _observe("lease.activated", leaseId=lease_id)
    return _response({"schema": SCHEMA, "leaseId": lease_id, "hostToken": token,
                      "expiresAt": lease["expiresAt"], "heartbeatSeconds": 5})


def _live_lease(lease_id):
    if not isinstance(lease_id, str) or not _HEX.fullmatch(lease_id):
        _error(403, "FORGE_LEASE_REQUIRED")
    lease, raw = _read("lease", lease_id)
    if not lease or lease.get("kind") != "lease" or lease.get("expiresAt", 0) <= _now():
        _error(409, "FORGE_LEASE_EXPIRED")
    session, session_raw, user = _live_session(lease["sessionKey"])
    if (session.get("activeLeaseId") != lease_id or user.get("id") != lease.get("owner")
            or any(session.get(k) != lease.get(k) for k in ("parentOrigin", "hostId", "channelId"))):
        _error(409, "FORGE_LEASE_REVOKED")
    return lease, raw, session, session_raw


def _host(request, lease_id):
    lease, raw, session, session_raw = _live_lease(lease_id)
    _host_origin(request, lease["parentOrigin"])
    token = request.headers.get("x-swrlz-forge-host", "")
    if not token.startswith("sfh1_") or not _TOKEN.fullmatch(token) or not secrets.compare_digest(
            hashlib.sha256(token.encode()).hexdigest(), lease["hostTokenHash"]):
        _error(401, "FORGE_HOST_CREDENTIAL_INVALID")
    return lease, raw, session, session_raw


@router.post("/api/forge/embed/host/heartbeat")
async def heartbeat(request: Request):
    body = await _body(request)
    lease, raw, session, session_raw = _host(request, body.get("leaseId"))
    key = _key("lease", lease["leaseId"])
    if (body.get("visible") is not True or any(body.get(k) != lease[k] for k in
            ("hostId", "channelId", "threadId", "projectId"))):
        _txn([(key, raw)], deletes=[key])
        _error(409, "FORGE_HOST_DETACHED_OR_CHANGED")
    context, digest = _safe_json(body.get("context"))
    if not isinstance(context, dict):
        _error(400, "FORGE_CONTEXT_OBJECT_REQUIRED")
    if context.get("projectId") != lease["projectId"]:
        _error(409, "FORGE_HOST_PROJECT_CHANGED")
    new = {**lease, "context": context, "contextHash": digest,
           "expiresAt": min(_now() + LEASE_TTL, session["expiresAt"])}
    if not _txn([(key, raw), (lease["sessionKey"], session_raw)], [(key, new, 60)]):
        _error(409, "FORGE_HOST_CHANGED")
    return _response({"leaseId": lease["leaseId"], "expiresAt": new["expiresAt"], "contextHash": digest})


@router.post("/api/forge/embed/host/close")
async def close(request: Request):
    body = await _body(request)
    lease, raw, _, session_raw = _host(request, body.get("leaseId"))
    key = _key("lease", lease["leaseId"])
    if not _txn([(key, raw), (lease["sessionKey"], session_raw)], deletes=[key]):
        _error(409, "FORGE_HOST_CHANGED")
    return _response({"ok": True})


@dataclass(frozen=True)
class AuthorizedForgeContext:
    lease_id: str
    thread_id: str
    generation_id: str
    project_id: str
    _summary: dict = field(repr=False)
    _session_key: str = field(repr=False)
    _owner: str = field(repr=False)
    _generation_key: str = field(repr=False)
    _context_hash: str = field(repr=False)
    _seal: object = field(repr=False, compare=False)

    def model_context(self):
        return copy.deepcopy(self._summary)

    def public_binding(self):
        return {"leaseId": self.lease_id, "threadId": self.thread_id,
                "generationId": self.generation_id, "projectId": self.project_id}


def authorize_generation(request, leaseId, threadId, generationId):
    if not leaseId:
        return None
    session = require_embed(request)
    lease, lease_raw, _, session_raw = _live_lease(leaseId)
    thread, generation = _id(threadId, "thread"), _id(generationId, "generation")
    if lease["sessionKey"] != session["key"] or lease["owner"] != session["user"]["id"] or lease["threadId"] != thread:
        _error(403, "FORGE_GENERATION_BINDING_MISMATCH")
    gen_key = _key("generation", leaseId + ":" + generation)
    record = {"schema": SCHEMA, "kind": "generation", "state": "active", "leaseId": leaseId,
              "sessionKey": session["key"], "owner": lease["owner"], "threadId": thread,
              "generationId": generation, "projectId": lease["projectId"], "contextHash": lease["contextHash"],
              "activeBatchId": "", "expiresAt": min(_now() + SESSION_TTL, session["record"]["expiresAt"])}
    if not _txn([(_key("lease", leaseId), lease_raw), (session["key"], session_raw), (gen_key, None)],
                [(gen_key, record, _ttl(record))]):
        _error(409, "FORGE_GENERATION_CHANGED_OR_REUSED")
    return AuthorizedForgeContext(leaseId, thread, generation, lease["projectId"], copy.deepcopy(lease["context"]),
                                  session["key"], lease["owner"], gen_key, lease["contextHash"], _SEAL)


def context_request_matches(request, context):
    """Account-scope a private stream projection, without granting tool access.

    Terminal streams may outlive generation invalidation. Live mutation must
    continue to use revalidate(), never this projection-only predicate.
    """
    if not isinstance(context, AuthorizedForgeContext) or context._seal is not _SEAL:
        return False
    try:
        session = require_embed(request)
    except HTTPException:
        return False
    return (session["key"] == context._session_key
            and session["user"]["id"] == context._owner)


def _generation(context, require_snapshot=False):
    if not isinstance(context, AuthorizedForgeContext) or context._seal is not _SEAL:
        _error(403, "FORGE_SERVER_CONTEXT_REQUIRED")
    lease, lease_raw, session, session_raw = _live_lease(context.lease_id)
    gen, gen_raw = _read_key(context._generation_key)
    if (not gen or gen.get("kind") != "generation" or gen.get("state") != "active"
            or gen.get("expiresAt", 0) <= _now()):
        _error(409, "FORGE_GENERATION_CANCELLED")
    expected = {"leaseId": context.lease_id, "sessionKey": context._session_key, "owner": context._owner,
                "threadId": context.thread_id, "generationId": context.generation_id, "projectId": context.project_id}
    if any(gen.get(k) != v for k, v in expected.items()) or any(lease.get(k) != v for k, v in expected.items()
                                                                             if k not in ("generationId",)):
        _error(403, "FORGE_GENERATION_BINDING_MISMATCH")
    if require_snapshot and lease["contextHash"] != context._context_hash:
        _error(409, "FORGE_NATIVE_CONTEXT_STALE")
    return lease, lease_raw, session, session_raw, gen, gen_raw


def revalidate(context, require_snapshot=True):
    _generation(context, require_snapshot)


def invalidate_generation(context):
    if not isinstance(context, AuthorizedForgeContext) or context._seal is not _SEAL:
        _error(403, "FORGE_SERVER_CONTEXT_REQUIRED")
    gen, raw = _read_key(context._generation_key)
    if not gen:
        return
    if gen.get("state") != "active":
        return
    new = {**gen, "state": "cancelled"}
    if not _txn([(context._generation_key, raw)], [(context._generation_key, new, _ttl(new))]):
        _error(409, "FORGE_GENERATION_CHANGED")



def _design_digest(operations):
    """Stable metadata fingerprint; only server-held operations authorize a write."""
    raw = json.dumps(operations, ensure_ascii=False, sort_keys=True,
                     separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def create_design_proposal(context, operations):
    """Offer an immutable 15-minute proposal without scheduling native work.

    Bound to the active account session, Chat thread, host and native snapshot.
    Model/planner output is independently revalidated at this durable boundary.
    """
    lease, lease_raw, session, session_raw, gen, gen_raw = _generation(context, True)
    operations, _ = _safe_json(operations, 65536)
    from forge_chat_actions import validate_operations
    operations = validate_operations(context, operations)
    if any(op.get("op") == "project.create" for op in operations):
        _error(400, "FORGE_DESIGN_PROJECT_WIZARD_REQUIRED")
    proposal_id = secrets.token_hex(16)
    expires_at = min(_now() + DESIGN_TTL, session["expiresAt"])
    record = {
        "schema": SCHEMA, "kind": "design-proposal", "state": "offered",
        "proposalId": proposal_id, "operations": operations,
        "planDigest": _design_digest(operations),
        **{key: lease[key] for key in
           ("sessionKey", "owner", "threadId", "projectId", "contextHash",
            "parentOrigin", "hostId", "channelId")},
        "expiresAt": expires_at,
    }
    key = _key("design", proposal_id)
    if not _txn([(_key("lease", context.lease_id), lease_raw),
                 (context._session_key, session_raw), (context._generation_key, gen_raw),
                 (key, None)], [(key, record, _ttl(record, DESIGN_TTL))]):
        _error(409, "FORGE_DESIGN_CONTEXT_CHANGED")
    _observe("design.offered", proposalId=proposal_id, operationCount=len(operations))
    return {"proposalId": proposal_id, "planDigest": record["planDigest"],
            "expiresAt": expires_at}


def claim_design_proposal(context, proposal_id):
    """Atomically consume one preview and register the exact original batch.

    The opaque public ID is never a capability: a fresh valid generation,
    matching encrypted owner/session/thread/project/host/snapshot and the same
    server-side native validator are required. A replay cannot register a batch.
    """
    if not isinstance(proposal_id, str) or not _HEX.fullmatch(proposal_id):
        _error(400, "FORGE_DESIGN_ID_INVALID")
    proposal, _ = _read("design", proposal_id)
    if (not proposal or proposal.get("kind") != "design-proposal"
            or proposal.get("state") != "offered" or proposal.get("expiresAt", 0) <= _now()):
        _error(409, "FORGE_DESIGN_EXPIRED_OR_USED")
    lease, _, _, _, _, _ = _generation(context, True)
    bindings = ("sessionKey", "owner", "threadId", "projectId", "contextHash",
                "parentOrigin", "hostId", "channelId")
    if any(proposal.get(key) != lease.get(key) for key in bindings):
        _error(409, "FORGE_DESIGN_CONTEXT_MISMATCH")
    operations = copy.deepcopy(proposal.get("operations"))
    if (not isinstance(operations, list)
            or proposal.get("planDigest") != _design_digest(operations)):
        _error(409, "FORGE_DESIGN_PLAN_CORRUPT")
    batch_id = create_batch(context, operations, proposal_id=proposal_id)
    return batch_id, operations, proposal["planDigest"]


def create_batch(context, operations, *, proposal_id=None):
    lease, lease_raw, _, session_raw, gen, gen_raw = _generation(context, True)
    if not isinstance(operations, list) or not 1 <= len(operations) <= MAX_OPERATIONS or not all(isinstance(op, dict) for op in operations):
        _error(400, "FORGE_INVALID_OPERATION_BATCH")
    operations, _ = _safe_json(operations, 65536)
    # Revalidate the exact native data protocol at the durable authorization
    # boundary too. The inference caller is not itself an operation authority.
    from forge_chat_actions import validate_operations
    operations = validate_operations(context, operations)
    if gen.get("activeBatchId"):
        _error(409, "FORGE_BATCH_ALREADY_REGISTERED")
    # Single atomic Redis transaction consumes the proposal and registers the
    # batch: racing approvals cannot both claim it. No native action is sent
    # if the proposal, host, owner or scene changed.
    proposal_expected, proposal_write, digest = [], [], None
    if proposal_id is not None:
        if not isinstance(proposal_id, str) or not _HEX.fullmatch(proposal_id):
            _error(400, "FORGE_DESIGN_ID_INVALID")
        record, original = _read("design", proposal_id)
        keys = ("sessionKey", "owner", "threadId", "projectId", "contextHash",
                "parentOrigin", "hostId", "channelId")
        if (not record or record.get("kind") != "design-proposal"
                or record.get("state") != "offered" or record.get("expiresAt", 0) <= _now()
                or any(record.get(key) != lease.get(key) for key in keys)
                or record.get("operations") != operations
                or record.get("planDigest") != _design_digest(operations)):
            _error(409, "FORGE_DESIGN_STALE_OR_USED")
        proposal_key = _key("design", proposal_id)
        proposal_expected = [(proposal_key, original)]
        proposal_write = [(proposal_key, {**record, "state": "claimed",
                                           "claimedByGeneration": context.generation_id},
                           _ttl(record, DESIGN_TTL))]
        digest = record["planDigest"]
    batch_id = secrets.token_hex(16)
    batch = {"schema": SCHEMA, "kind": "batch", "state": "pending", "batchId": batch_id,
             "generationKey": context._generation_key, **{k: gen[k] for k in
             ("leaseId", "sessionKey", "owner", "threadId", "generationId", "projectId", "contextHash")},
             "context": copy.deepcopy(lease["context"]), "operations": operations, "receipts": [],
             "expiresAt": min(_now() + BATCH_TTL, gen["expiresAt"])}
    if digest is not None:
        batch["designPlanDigest"] = digest
        batch["designProposalId"] = proposal_id
    key = _key("batch", batch_id)
    new_gen = {**gen, "activeBatchId": batch_id}
    if not _txn([(_key("lease", context.lease_id), lease_raw), (context._session_key, session_raw),
                 (context._generation_key, gen_raw), (key, None), *proposal_expected],
                [(context._generation_key, new_gen, _ttl(new_gen)), (key, batch, _ttl(batch, BATCH_TTL)),
                 *proposal_write]):
        _error(409, "FORGE_BATCH_CONTEXT_CHANGED")
    _observe("batch.registered", leaseId=context.lease_id, batchId=batch_id, operationCount=len(operations))
    return batch_id


def _batch(batch_id, lease):
    if not isinstance(batch_id, str) or not _HEX.fullmatch(batch_id):
        _error(404, "FORGE_BATCH_NOT_FOUND")
    batch, raw = _read("batch", batch_id)
    if (not batch or batch.get("kind") != "batch" or batch.get("expiresAt", 0) <= _now()
            or any(batch.get(k) != lease.get(k) for k in ("leaseId", "sessionKey", "owner", "threadId", "projectId"))):
        _error(404, "FORGE_BATCH_NOT_FOUND")
    gen, gen_raw = _read_key(batch["generationKey"])
    if not gen or gen.get("state") != "active" or gen.get("activeBatchId") != batch_id:
        _error(409, "FORGE_GENERATION_CANCELLED")
    return batch, raw, gen, gen_raw


@router.post("/api/forge/embed/host/batches/{batch_id}/take")
async def take_batch(batch_id: str, request: Request):
    body = await _body(request)
    lease, lease_raw, _, session_raw = _host(request, body.get("leaseId"))
    batch, raw, _, gen_raw = _batch(batch_id, lease)
    if batch.get("state") != "pending":
        _error(409, "FORGE_BATCH_ALREADY_TAKEN")
    if batch["contextHash"] != lease["contextHash"]:
        _error(409, "FORGE_NATIVE_CONTEXT_STALE")
    nonce = _token("sfr1")
    new = {**batch, "state": "taken", "receiptNonceHash": hashlib.sha256(nonce.encode()).hexdigest()}
    key = _key("batch", batch_id)
    if not _txn([(key, raw), (_key("lease", lease["leaseId"]), lease_raw),
                 (lease["sessionKey"], session_raw), (batch["generationKey"], gen_raw)],
                [(key, new, _ttl(new, BATCH_TTL))]):
        _error(409, "FORGE_BATCH_CHANGED")
    _observe("batch.taken", leaseId=lease["leaseId"], batchId=batch_id, operationCount=len(batch["operations"]))
    return _response({"batchId": batch_id, "operations": batch["operations"], "receiptNonce": nonce,
                      "preconditions": {**{k: batch[k] for k in
                      ("leaseId", "threadId", "projectId", "generationId", "contextHash")}, "context": batch["context"]}})


def _redact(value, secrets_to_hide=()):
    if isinstance(value, dict):
        return {k: _redact(v, secrets_to_hide) for k, v in value.items()
                if isinstance(k, str) and k.lower().replace("_", "") not in _SENSITIVE_KEYS
                and k not in ("__proto__", "constructor", "prototype")}
    if isinstance(value, list):
        return [_redact(v, secrets_to_hide) for v in value]
    if isinstance(value, str):
        value = _TOKEN_TEXT.sub("[redacted]", value)
        for secret in secrets_to_hide:
            if secret:
                value = value.replace(secret, "[redacted]")
    return value


@router.post("/api/forge/embed/host/batches/{batch_id}/finish")
async def finish_batch(batch_id: str, request: Request):
    body = await _body(request)
    lease, lease_raw, _, session_raw = _host(request, body.get("leaseId"))
    batch, raw, _, gen_raw = _batch(batch_id, lease)
    nonce = body.get("receiptNonce")
    if (batch.get("state") != "taken" or not isinstance(nonce, str) or not nonce.startswith("sfr1_")
            or not _TOKEN.fullmatch(nonce) or not secrets.compare_digest(hashlib.sha256(nonce.encode()).hexdigest(),
                                                                        batch.get("receiptNonceHash", ""))):
        _error(409, "FORGE_RECEIPT_NONCE_INVALID_OR_USED")
    results = body.get("results")
    if (not isinstance(results, list) or len(results) != len(batch["operations"])
            or not all(isinstance(result, dict) and type(result.get("ok")) is bool for result in results)):
        _error(400, "FORGE_RECEIPTS_MUST_MATCH_OPERATIONS")
    receipts, _ = _safe_json(_redact(results, (nonce, request.headers.get("x-swrlz-forge-host", ""))), 32768)
    context, digest = _safe_json(body.get("context"))
    if not isinstance(context, dict):
        _error(400, "FORGE_CONTEXT_OBJECT_REQUIRED")
    transition = False
    if len(batch["operations"]) == 1 and batch["operations"][0].get("op") == "project.create" and receipts[0]["ok"]:
        operation, receipt = batch["operations"][0], receipts[0]
        project = context.get("project")
        new_id = receipt.get("projectId")
        if (receipt.get("op") != "project.create" or not isinstance(new_id, str) or not _HEX.fullmatch(new_id)
                or new_id == batch["projectId"] or context.get("projectId") != new_id
                or receipt.get("name") != operation["name"] or receipt.get("starterId") != operation["starterId"]
                or not isinstance(project, dict) or project.get("name") != operation["name"]
                or project.get("sourceStarterId") != operation["starterId"] or context.get("mode") != "edit"):
            _error(409, "FORGE_PROJECT_TRANSITION_RECEIPT_INVALID")
        transition = True
    elif context.get("projectId") != batch["projectId"]:
        _error(409, "FORGE_HOST_PROJECT_CHANGED")
    new = {**batch, "state": "finished", "receipts": receipts, "allSucceeded": all(result["ok"] for result in receipts)}
    if transition:
        new["projectTransition"] = True
    new.pop("receiptNonceHash", None)
    new_lease = {**lease, "context": context, "contextHash": digest}
    key, lease_key = _key("batch", batch_id), _key("lease", lease["leaseId"])
    if not _txn([(key, raw), (lease_key, lease_raw), (lease["sessionKey"], session_raw),
                 (batch["generationKey"], gen_raw)],
                [(key, new, _ttl(new, BATCH_TTL)), (lease_key, new_lease, 60)]):
        _error(409, "FORGE_RECEIPT_CONTEXT_CHANGED")
    _observe("batch.finished", leaseId=lease["leaseId"], batchId=batch_id, receiptCount=len(receipts))
    return _response({"batchId": batch_id, "status": "finished", "allSucceeded": new["allSucceeded"], "receipts": receipts})


def _finished_project_transition(context, batch_id):
    """Read an already-stored creation receipt after the host retires its lease.

    This terminal projection grants no edit authority. The original generation,
    account session and complete immutable binding must still match. Closing the
    old host immediately after finish therefore cannot race a truthful response.
    """
    if not isinstance(context, AuthorizedForgeContext) or context._seal is not _SEAL:
        _error(403, "FORGE_SERVER_CONTEXT_REQUIRED")
    if not isinstance(batch_id, str) or not _HEX.fullmatch(batch_id):
        return None
    batch, _ = _read("batch", batch_id)
    if not batch or batch.get("state") != "finished" or batch.get("projectTransition") is not True:
        return None
    _, _, user = _live_session(context._session_key)
    gen, _ = _read_key(context._generation_key)
    expected = {"leaseId": context.lease_id, "sessionKey": context._session_key, "owner": context._owner,
                "threadId": context.thread_id, "generationId": context.generation_id, "projectId": context.project_id}
    if (user.get("id") != context._owner or batch.get("expiresAt", 0) <= _now()
            or not gen or gen.get("state") != "active" or gen.get("activeBatchId") != batch_id
            or gen.get("expiresAt", 0) <= _now()
            or any(batch.get(k) != value or gen.get(k) != value for k, value in expected.items())):
        _error(409, "FORGE_PROJECT_RECEIPT_BINDING_MISMATCH")
    return {"batchId": batch_id, "status": "finished", "allSucceeded": batch["allSucceeded"],
            "receipts": copy.deepcopy(batch["receipts"])}


def wait_batch(context, batchId, timeout=30.0):
    deadline = time.monotonic() + max(0, min(float(timeout), 120))
    while True:
        try:
            terminal = _finished_project_transition(context, batchId)
            if terminal is not None:
                return terminal
            lease, _, _, _, _, _ = _generation(context, False)
            batch, _, _, _ = _batch(batchId, lease)
        except HTTPException as exc:
            status = "expired" if "EXPIRED" in str(exc.detail) else "cancelled"
            return {"batchId": batchId, "status": status, "allSucceeded": False, "receipts": [], "code": str(exc.detail)}
        if batch["state"] == "finished":
            return {"batchId": batchId, "status": "finished", "allSucceeded": batch["allSucceeded"], "receipts": copy.deepcopy(batch["receipts"])}
        if time.monotonic() >= deadline:
            # A delayed host must not perform work after Chat has reported that
            # its bounded receipt wait ended. A retry needs a new generation.
            invalidate_generation(context)
            return {"batchId": batchId, "status": "timeout", "allSucceeded": False, "receipts": []}
        time.sleep(min(0.2, max(0, deadline - time.monotonic())))


def install(app, legacy_authenticate, *, chat_origin=CHAT_ORIGIN, parent_origins=PARENT_ORIGINS, diagnostic_hook=None):
    """Host-only CORS; no general Chat/account CORS or cookie weakening."""
    global _legacy_authenticate, _chat_origin, _parent_origins, _diagnostic_hook
    _legacy_authenticate = legacy_authenticate
    _chat_origin = str(chat_origin)
    _parent_origins = frozenset(parent_origins)
    _diagnostic_hook = diagnostic_hook

    @app.middleware("http")
    async def host_cors(request, call_next):
        if not request.url.path.startswith("/api/forge/embed/host/"):
            return await call_next(request)
        origin = request.headers.get("origin", "")
        if origin not in _parent_origins:
            return _response({"detail": "FORGE_HOST_ORIGIN_REQUIRED"}, 403)
        if request.method == "OPTIONS":
            asked = {part.strip().lower() for part in request.headers.get("access-control-request-headers", "").split(",") if part.strip()}
            if request.headers.get("access-control-request-method", "") != "POST" or not asked <= {"content-type", "x-swrlz-forge-host"}:
                return _response({"detail": "FORGE_HOST_PREFLIGHT_REJECTED"}, 403)
            response = Response(status_code=204)
        else:
            response = await call_next(request)
        response.headers.update({"Access-Control-Allow-Origin": origin,
                                 "Access-Control-Allow-Methods": "POST",
                                 "Access-Control-Allow-Headers": "Content-Type, X-Swrlz-Forge-Host",
                                 "Vary": "Origin", "Cache-Control": "no-store"})
        return response

    app.include_router(router)
