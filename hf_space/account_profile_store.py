"""Explicitly saved Google-owner settings on the existing encrypted transport.

Reading absent settings returns defaults without writing. This module neither
resolves legacy identities nor grants inference, editor or provider authority.
"""
from __future__ import annotations

import copy
import hashlib
import inspect
import json
import math
import time

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

import account_chat_store as storage

SCHEMA = "swrlz-google-profile-v1"
ENVELOPE_SCHEMA = "swrlz-google-profile-envelope-v1"
MAX_BODY_BYTES = 32_768
MAX_RECORD_BYTES = 65_536
MAX_VERSION = 9_007_199_254_740_991
POLICY_CATEGORIES = (
    "USER_PROFILE", "COMPANION_PROFILE", "USER_FACT", "USER_LORE",
    "COMPANION_SELF_LORE", "SHARED_LORE", "SHARED_RAPPORT",
)
_CAS = (
    "local raw=redis.call('GET',KEYS[1]);local expected=tonumber(ARGV[1]);"
    "if raw then local ok,old=pcall(cjson.decode,raw);"
    "if not ok or type(old)~='table' or old['schema']~=ARGV[4] "
    "or tonumber(old['version'])~=expected or raw~=ARGV[2] then return 0 end;"
    "elseif expected~=0 or ARGV[2]~='' then return 0 end;"
    "redis.call('SET',KEYS[1],ARGV[3]);return 1"
)


def _defaults():
    return {
        "display_name": None,
        "preferences": {
            "general": {"enterToSend": True, "personalityProfile": "default"},
            "profile": {"pronouns": "", "role": "", "communicationStyle": "adaptive", "outputStyle": "adaptive"},
            "proposalPolicy": {category: "ASK" for category in POLICY_CATEGORIES},
        },
        "model_preferences": {"defaultModel": "700m", "effort": "auto", "responseLength": "adaptive"},
        "ui_preferences": {
            "density": "compact", "glass": "standard", "motion": "system",
            "fontScale": "1", "highContrast": False, "reducedTransparency": False,
        },
        "companion_profile": {
            "name": "§wyrlz", "title": "Glitch Dragon Kompanion", "form": "Glitch Dragon", "pronouns": "",
            "warmth": "adaptive", "directness": "adaptive", "humor": "adaptive", "loreDensity": "adaptive",
        },
        "version": 0,
        "updated_at": 0,
    }


def _invalid(path="profile"):
    raise HTTPException(400, "Invalid account settings field: " + path)


def _text(limit, *, nullable=False):
    def validate(value, path):
        if value is None and nullable:
            return None
        if not isinstance(value, str):
            _invalid(path)
        value = value.strip()
        if len(value) > limit:
            _invalid(path)
        return (value or None) if nullable else value
    return validate


def _enum(*choices):
    def validate(value, path):
        if not isinstance(value, str) or value.strip() not in choices:
            _invalid(path)
        return value.strip()
    return validate


def _boolean(value, path):
    if type(value) is not bool:
        _invalid(path)
    return value


def _font_scale(value, path):
    if type(value) in (int, float):
        if not math.isfinite(value):
            _invalid(path)
        value = format(value, "g")
    return _enum("0.9", "1", "1.1", "1.2")(value, path)


def _object(fields):
    def validate(value, path):
        if not isinstance(value, dict) or set(value) - set(fields):
            _invalid(path)
        return {key: fields[key](item, path + "." + key) for key, item in value.items()}
    return validate


_INPUT_FIELDS = {
    "displayName": ("display_name", _text(120, nullable=True)),
    "preferences": ("preferences", _object({
        "general": _object({"enterToSend": _boolean, "personalityProfile": _enum("default", "gegd")}),
        "profile": _object({
            "pronouns": _text(80), "role": _text(160),
            "communicationStyle": _enum("adaptive", "direct", "collaborative", "technical", "playful"),
            "outputStyle": _enum("adaptive", "compact", "structured", "deep"),
        }),
        "proposalPolicy": _object({category: _enum("ASK", "AUTO_LOW_RISK", "SESSION_ONLY", "NEVER") for category in POLICY_CATEGORIES}),
    })),
    "modelPreferences": ("model_preferences", _object({
        "defaultModel": _enum("700m", "r39", "stock", "coder"),
        "effort": _enum("auto", "fast", "deep"),
        "responseLength": _enum("adaptive", "concise", "expanded"),
    })),
    "uiPreferences": ("ui_preferences", _object({
        "density": _enum("compact", "comfortable"), "glass": _enum("standard", "low"),
        "motion": _enum("system", "full", "reduced", "off"), "fontScale": _font_scale,
        "highContrast": _boolean, "reducedTransparency": _boolean,
    })),
    "companionProfile": ("companion_profile", _object({
        "name": _text(120), "title": _text(160), "form": _text(120), "pronouns": _text(80),
        "warmth": _enum("adaptive", "low", "medium", "high"),
        "directness": _enum("adaptive", "gentle", "direct", "very-direct"),
        "humor": _enum("adaptive", "low", "medium", "high"),
        "loreDensity": _enum("adaptive", "minimal", "balanced", "mythic"),
    })),
}


def _json(value, limit=MAX_BODY_BYTES):
    try:
        result = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        size = len(result.encode("utf-8"))
    except (TypeError, ValueError, UnicodeError, RecursionError):
        _invalid()
    if size > limit:
        raise HTTPException(413, "Account settings exceed the bounded storage size")
    return result


def _version(value):
    if type(value) is not int or not 0 <= value <= MAX_VERSION:
        _invalid("version")
    return value


def _normalize(body):
    _json(body)
    if not isinstance(body, dict) or set(body) - (set(_INPUT_FIELDS) | {"version"}) or "version" not in body:
        _invalid()
    expected = _version(body["version"])
    patch = {}
    for key, value in body.items():
        if key != "version":
            target, validate = _INPUT_FIELDS[key]
            patch[target] = validate(value, key)
    return expected, patch


def _merge(current, patch):
    result = copy.deepcopy(current)
    for key, value in patch.items():
        result[key] = _merge(result[key], value) if isinstance(value, dict) else value
    return result


def _key(owner):
    if not isinstance(owner, str) or not storage.OWNER.fullmatch(owner):
        raise HTTPException(401, "Verified Google identity required for account settings")
    return "swrlz:google:profile:v1:" + hashlib.sha256(owner.encode("utf-8")).hexdigest()


def _command(config, *args):
    try:
        return storage.gh._redis(config, *args)
    except Exception as exc:
        raise HTTPException(503, "Account settings storage unavailable; reload before retrying") from exc


def _full_shape(value, defaults):
    if isinstance(defaults, dict):
        if not isinstance(value, dict) or set(value) != set(defaults):
            raise ValueError("Stored settings shape mismatch")
        for key in defaults:
            _full_shape(value[key], defaults[key])


def _read(config, owner, key):
    raw = _command(config, "GET", key)
    if raw is None:
        return _defaults(), ""
    try:
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_RECORD_BYTES:
            raise ValueError("Invalid profile envelope")
        outer = json.loads(raw)
        if (not isinstance(outer, dict) or set(outer) != {"schema", "version", "encrypted"}
                or outer["schema"] != ENVELOPE_SCHEMA or type(outer["version"]) is not int
                or not 1 <= outer["version"] <= MAX_VERSION
                or not isinstance(outer["encrypted"], str) or not outer["encrypted"]):
            raise ValueError("Invalid profile envelope")
        decrypted = storage._decrypt(config, outer["encrypted"])
        if (not isinstance(decrypted, dict) or set(decrypted) != {"schema", "owner", "profile"}
                or decrypted["schema"] != SCHEMA or decrypted["owner"] != owner):
            raise ValueError("Stored profile owner mismatch")
        profile = decrypted["profile"]
        _full_shape(profile, _defaults())
        if (type(profile["version"]) is not int or profile["version"] != outer["version"]
                or type(profile["updated_at"]) not in (int, float)
                or not math.isfinite(profile["updated_at"]) or profile["updated_at"] <= 0):
            raise ValueError("Stored profile version mismatch")
        body = {name: profile[target] for name, (target, _) in _INPUT_FIELDS.items()}
        _, normalized = _normalize({**body, "version": profile["version"]})
        _json(profile)
        return {**normalized, "version": profile["version"], "updated_at": profile["updated_at"]}, raw
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, HTTPException) as exc:
        raise HTTPException(503, "Stored account settings failed validation; no defaults were substituted") from exc


def load_profile(owner):
    """Load the verified owner's full settings; an absent record is read-only."""
    key = _key(owner)
    config = storage._config()
    profile, _ = _read(config, owner, key)
    return profile


def save_profile(owner, body):
    """Save an explicit bounded partial update only at the expected revision."""
    key = _key(owner)
    expected, patch = _normalize(body)
    if expected == MAX_VERSION:
        raise HTTPException(409, "Account settings version limit reached; no update was attempted")
    config = storage._config()
    current, raw = _read(config, owner, key)
    if current["version"] != expected:
        raise HTTPException(409, "Account settings changed; reload before saving")
    profile = _merge(current, patch)
    now = time.time()
    if type(now) not in (int, float) or not math.isfinite(now) or now <= 0:
        raise HTTPException(503, "Account settings timestamp unavailable; no update was attempted")
    profile.update(version=expected + 1, updated_at=now)
    _json(profile)
    encrypted = storage._encrypt(config, {"schema": SCHEMA, "owner": owner, "profile": profile})
    envelope = _json({"schema": ENVELOPE_SCHEMA, "version": profile["version"], "encrypted": encrypted}, MAX_RECORD_BYTES)
    result = _command(config, "EVAL", _CAS, "1", key, str(expected), raw, envelope, ENVELOPE_SCHEMA)
    if type(result) in (int, str) and result in (0, "0"):
        raise HTTPException(409, "Account settings changed; reload before saving")
    if type(result) not in (int, str) or result not in (1, "1"):
        raise HTTPException(503, "Account settings save was not confirmed; reload before retrying")
    return profile


async def _call(callback, request):
    value = await callback(request) if inspect.iscoroutinefunction(callback) else await run_in_threadpool(callback, request)
    return await value if inspect.isawaitable(value) else value


async def _owner(authenticate, request):
    account = await _call(authenticate, request)
    if not isinstance(account, tuple) or len(account) != 2 or not isinstance(account[1], dict):
        raise HTTPException(401, "Verified Google identity required for account settings")
    owner = account[1].get("id")
    _key(owner)
    return owner


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate settings key")
        result[key] = value
    return result


async def _body(request):
    if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
        raise HTTPException(415, "Account settings require JSON")
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_BODY_BYTES:
            raise HTTPException(413, "Account settings exceed the bounded request size")
        chunks.append(chunk)
    try:
        return json.loads(b"".join(chunks).decode("utf-8"), object_pairs_hook=_unique_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise HTTPException(400, "Invalid account settings JSON") from exc


def install(app, authenticate, write_guard):
    """Register routes using existing verified-account and mutation owners.

    Both callbacks may be synchronous or async. authenticate returns (sid,user);
    write_guard returns None/True on success and raises to deny mutation.
    """
    @app.get("/api/account/profile")
    async def get_profile(request: Request):
        owner = await _owner(authenticate, request)
        profile = await run_in_threadpool(load_profile, owner)
        return JSONResponse({"ok": True, "profile": profile, "durable": True, "saved": profile["version"] > 0},
                            headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})

    @app.put("/api/account/profile")
    async def put_profile(request: Request):
        owner = await _owner(authenticate, request)
        guarded = await _call(write_guard, request)
        if guarded is not None and guarded is not True:
            raise HTTPException(403, "Account settings mutation denied")
        profile = await run_in_threadpool(save_profile, owner, await _body(request))
        return JSONResponse({"ok": True, "profile": profile, "durable": True, "saved": True},
                            headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})
