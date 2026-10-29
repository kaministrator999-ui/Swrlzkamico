"""Lossless, encrypted Google-owner storage for native §E project snapshots.

The encrypted catalog is the single CAS publication point. It indexes every
planned upload chunk before that chunk can be written. Upload cancellation and
old-revision cleanup remain journaled until all chunk deletions are confirmed.
Project bytes are data: this module never evaluates project scripts or geometry.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import math
import re
import secrets
import time
import zlib
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.concurrency import run_in_threadpool

import account_chat_store as accounts
import github_connection as gh

SCHEMA = "swrlz-forge-project-catalog-v1"
PART_SCHEMA = "swrlz-forge-project-part-v1"
RAW_MAX = 96 * 1024 * 1024
COMPRESSED_MAX = 64 * 1024 * 1024
PART_BYTES = 512 * 1024
MAX_PARTS = RAW_MAX // PART_BYTES
MAX_PROJECTS = 64
MAX_UPLOADS = 4
MAX_GARBAGE = 16
MAX_RECEIPTS = 16
OWNER_ENCODED_MAX = 256 * 1024 * 1024
CATALOG_MAX = 256 * 1024
UPLOAD_TTL = 3600
RECEIPT_TTL = 86400
MAX_RETRIES = 4
ID = re.compile(r"^[0-9a-f]{32}$")
SHA = re.compile(r"^[0-9a-f]{64}$")

_CATALOG_CAS = """-- swrlz-forge-catalog-cas-v1
local current=redis.call('GET',KEYS[1]) or '';
if current~=ARGV[1] then return 0 end;
redis.call('SET',KEYS[1],ARGV[2]); return 1
"""
_PART_CAS = """-- swrlz-forge-part-cas-v1
local current=redis.call('GET',KEYS[1]) or '';
if current~=ARGV[1] then return 0 end;
if redis.call('EXISTS',KEYS[2])==1 then return -1 end;
redis.call('SET',KEYS[2],ARGV[3]);
redis.call('SET',KEYS[1],ARGV[2]); return 1
"""


def _fail(code: int, detail: str):
    raise HTTPException(code, detail)


def _integer(value, minimum=0, maximum=2**53-1):
    return type(value) is int and minimum <= value <= maximum


def _owner(owner):
    if not isinstance(owner, str) or not accounts.OWNER.fullmatch(owner):
        _fail(401, "Verified Google identity required")
    return owner


def _root(owner):
    # Catalog and part publication use one atomic multi-key Lua transaction.
    # Keep every key for this owner in the same Redis Cluster hash slot.
    return "swrlz:google:forge:v1:{" + hashlib.sha256(_owner(owner).encode()).hexdigest() + "}"


def _chunk_key(owner, nonce, index):
    if not isinstance(nonce, str) or not ID.fullmatch(nonce) or not _integer(index, 0, MAX_PARTS-1):
        _fail(503, "Stored project chunk reference is invalid")
    return _root(owner) + ":part:" + nonce + ":" + str(index)


def _json(value):
    try:
        result = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        result.encode("utf-8")
        return result
    except (ValueError, TypeError, UnicodeError, RecursionError):
        _fail(400, "Project storage metadata must be finite JSON")


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite JSON number")
    return result


def _parse_json(value):
    return json.loads(value, object_pairs_hook=_unique_pairs, parse_float=_finite_float,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))


def _command(c, *args):
    try:
        return gh._redis(c, *args)
    except Exception as exc:
        raise HTTPException(503, "Project storage unavailable; refresh before retrying") from exc


def _empty(owner):
    return {"schema": SCHEMA, "owner": owner, "revision": 0,
            "projects": {}, "uploads": {}, "garbage": {}, "receipts": {}}


def _catalog(c, owner):
    raw = _command(c, "GET", _root(owner))
    if raw is None:
        return "", _empty(owner)
    try:
        if not isinstance(raw, str) or len(raw) > CATALOG_MAX*2:
            raise ValueError()
        envelope = _parse_json(raw)
        if (not isinstance(envelope, dict) or set(envelope) != {"schema", "revision", "encrypted"}
                or not _integer(envelope.get("revision")) or not isinstance(envelope.get("encrypted"), str)):
            raise ValueError()
        cipher = envelope["encrypted"]
        plaintext = Fernet(c["fernet"].encode("ascii")).decrypt(cipher.encode("ascii"))
        if len(plaintext) > CATALOG_MAX:
            raise ValueError()
        data = _parse_json(plaintext)
        if not isinstance(data, dict):
            raise ValueError()
        if (envelope.get("schema") != SCHEMA or data.get("schema") != SCHEMA
                or data.get("owner") != owner or not _integer(data.get("revision"))
                or data["revision"] != envelope.get("revision")):
            raise ValueError()
        for key, limit in (("projects", MAX_PROJECTS), ("uploads", MAX_UPLOADS),
                           ("garbage", MAX_GARBAGE), ("receipts", MAX_RECEIPTS)):
            if not isinstance(data.get(key), dict) or len(data[key]) > limit:
                raise ValueError()
        if set(data) != {"schema", "owner", "revision", "projects", "uploads", "garbage", "receipts"}:
            raise ValueError()
        for key, value in data["projects"].items():
            if not ID.fullmatch(key) or _manifest(value)["id"] != key:
                raise ValueError()
        for key in data["uploads"]:
            _upload(data, key, allow_closed=True)
        for key, value in data["garbage"].items():
            if not ID.fullmatch(key) or _manifest(value)["uploadId"] != key:
                raise ValueError()
        for key, value in data["receipts"].items():
            if (not ID.fullmatch(key) or not isinstance(value, dict)
                    or set(value) != {"projectId", "expiresAt"}
                    or not ID.fullmatch(str(value["projectId"])) or not _integer(value["expiresAt"], 1)):
                raise ValueError()
        return raw, data
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError, InvalidToken, HTTPException):
        _fail(503, "Stored project catalog cannot be read; no changes were made")


def _encoded_catalog(c, data):
    raw = _json(data).encode("utf-8")
    if len(raw) > CATALOG_MAX:
        _fail(413, "Account project catalog reached its bounded capacity")
    return _json({"schema": SCHEMA, "revision": data["revision"],
                  "encrypted": Fernet(c["fernet"].encode("ascii")).encrypt(raw).decode("ascii")})


def _cas(c, owner, prior, data, part=None):
    if not _integer(data["revision"], 0, 2**53-2):
        _fail(409, "Project catalog revision limit reached; no update was attempted")
    data["revision"] += 1
    encoded = _encoded_catalog(c, data)
    if part is None:
        value = _command(c, "EVAL", _CATALOG_CAS, "1", _root(owner), prior, encoded)
    else:
        key, cipher = part
        value = _command(c, "EVAL", _PART_CAS, "2", _root(owner), key, prior, encoded, cipher)
    if type(value) in (int, str) and value in (1, "1"):
        return True
    if type(value) in (int, str) and value in (0, "0"):
        return False
    if type(value) in (int, str) and value in (-1, "-1"):
        _fail(503, "Upload part already exists without a confirmed catalog receipt; cancel and retry")
    _fail(503, "Project storage did not confirm atomic publication; refresh before retrying")


def _id(value, label="Project"):
    if not isinstance(value, str) or not ID.fullmatch(value):
        _fail(404, label + " not found")
    return value


def _descriptor(data, *, stored=False):
    code = 503 if stored else 400
    if not isinstance(data, dict):
        _fail(code, "Project storage metadata is invalid")
    codec = data.get("codec")
    raw = data.get("rawBytes")
    encoded = data.get("encodedBytes")
    if codec not in ("identity", "gzip"):
        _fail(code, "Project upload codec must be identity or gzip")
    if not _integer(raw, 1, RAW_MAX):
        _fail(503 if stored else 413, "Native project exceeds the 96 MiB raw limit")
    maximum = COMPRESSED_MAX if codec == "gzip" else RAW_MAX
    if not _integer(encoded, 1, maximum):
        _fail(503 if stored else 413, "Project upload exceeds its encoded size limit")
    for field in ("rawSha256", "encodedSha256"):
        if not isinstance(data.get(field), str) or not SHA.fullmatch(data[field]):
            _fail(code, "Project upload requires exact SHA-256 digests")
    if codec == "identity" and (raw != encoded or data["rawSha256"] != data["encodedSha256"]):
        _fail(code, "Identity project size and digests must agree")
    return math.ceil(encoded / PART_BYTES)


def _upload(data, upload_id, now=None, *, allow_closed=False):
    _id(upload_id, "Upload")
    value = data["uploads"].get(upload_id)
    if not isinstance(value, dict):
        _fail(404, "Upload not found")
    parts = _descriptor(value, stored=True)
    if (value.get("uploadId") != upload_id or value.get("parts") != parts
            or not isinstance(value.get("received"), dict) or len(value["received"]) > parts
            or not ID.fullmatch(str(value.get("projectId") or ""))
            or not _integer(value.get("expectedRevision"))
            or not _integer(value.get("expiresAt"), 1)
            or value.get("state") not in ("active", "cancelled")
            or not isinstance(value.get("name"), str) or not 1 <= len(value["name"]) <= 160):
        _fail(503, "Stored upload metadata is invalid")
    for key, receipt in value["received"].items():
        if (not isinstance(key, str) or not key.isascii() or not key.isdigit() or len(key) > 3
                or str(int(key)) != key or int(key) >= parts or not isinstance(receipt, dict)
                or set(receipt) != {"bytes", "sha256"}
                or not _integer(receipt["bytes"], 1, PART_BYTES)
                or not isinstance(receipt["sha256"], str) or not SHA.fullmatch(receipt["sha256"])):
            _fail(503, "Stored upload part receipt is invalid")
    if not allow_closed and (value.get("state") != "active" or value["expiresAt"] <= (now or int(time.time()))):
        _fail(410, "Upload expired or cancelled; previous cloud project was preserved")
    return value


def _manifest(value):
    if not isinstance(value, dict):
        _fail(503, "Stored project manifest is invalid")
    parts = _descriptor(value, stored=True)
    if (not ID.fullmatch(str(value.get("id") or ""))
            or not ID.fullmatch(str(value.get("uploadId") or ""))
            or value.get("parts") != parts or not _integer(value.get("revision"), 1)
            or not isinstance(value.get("name"), str) or len(value["name"]) > 160
            or not _integer(value.get("updatedAt"), 1)):
        _fail(503, "Stored project manifest is invalid")
    return value


def _public(value):
    return {key: value[key] for key in ("id", "name", "revision", "rawBytes", "rawSha256",
                                       "encodedBytes", "encodedSha256", "updatedAt")}


def limits():
    return {"rawBytes": RAW_MAX, "compressedBytes": COMPRESSED_MAX,
            "partBytes": PART_BYTES, "projects": MAX_PROJECTS, "pendingUploads": MAX_UPLOADS,
            "ownerEncodedBytes": OWNER_ENCODED_MAX, "uploadSeconds": UPLOAD_TTL}


def list_projects(owner):
    c = accounts._config()
    _, data = _catalog(c, _owner(owner))
    projects = [_public(_manifest(value)) for value in data["projects"].values()]
    return {"projects": sorted(projects, key=lambda p: (-p["updatedAt"], p["id"])), "limits": limits()}


def _references(data, nonce):
    return any(_manifest(p)["uploadId"] == nonce for p in data["projects"].values())


def _cleanup(c, owner):
    """Cleanup journals remain indexed after every unconfirmed deletion/CAS."""
    for _ in range(MAX_RETRIES):
        prior, data = _catalog(c, owner)
        now = int(time.time())
        changed = False
        for upload_id, value in list(data["uploads"].items()):
            upload = _upload(data, upload_id, allow_closed=True)
            if upload.get("state") == "active" and upload["expiresAt"] <= now:
                upload["state"] = "cancelled"
                changed = True
        if changed:
            if not _cas(c, owner, prior, data):
                continue
        break
    else:
        _fail(409, "Project catalog changed; refresh before retrying")
    # A cancelled/expired upload can no longer write: part CAS checks the same
    # catalog pointer and new requests check the active state before writing.
    _, current = _catalog(c, owner)
    journals = [("uploads", key) for key, value in current["uploads"].items()
                if value.get("state") == "cancelled"] + [("garbage", key) for key in current["garbage"]]
    for section, journal_id in journals:
        _, data = _catalog(c, owner)
        value = data[section].get(journal_id)
        if value is None:
            continue
        if section == "uploads":
            record = _upload(data, journal_id, allow_closed=True)
            if record.get("state") != "cancelled":
                continue
            nonce, count = journal_id, record["parts"]
        else:
            record = _manifest(value)
            nonce, count = record["uploadId"], record["parts"]
        if _references(data, nonce):
            _fail(503, "Cleanup reference is still used by a current cloud project")
        for index in range(count):
            deleted = _command(c, "DEL", _chunk_key(owner, nonce, index))
            if type(deleted) not in (int, str) or deleted not in (0, 1, "0", "1"):
                _fail(503, "Project cleanup is not confirmed; its journal was retained")
        for _ in range(MAX_RETRIES):
            prior, data = _catalog(c, owner)
            if journal_id not in data[section]:
                break
            if _references(data, nonce):
                _fail(503, "Project cleanup reference changed; journal was retained")
            del data[section][journal_id]
            if _cas(c, owner, prior, data):
                break
        else:
            _fail(409, "Project cleanup journal changed; retry later")


def begin_upload(owner, body):
    _owner(owner)
    allowed = {"name", "projectId", "expectedRevision", "codec", "rawBytes", "rawSha256",
               "encodedBytes", "encodedSha256"}
    if not isinstance(body, dict) or set(body) - allowed:
        _fail(400, "Unsupported project upload fields")
    parts = _descriptor(body)
    name = body.get("name")
    if not isinstance(name, str) or not name.strip() or len(name) > 160 or any(ord(x) < 32 for x in name):
        _fail(400, "Project name must contain 1–160 visible characters")
    expected = body.get("expectedRevision")
    if not _integer(expected):
        _fail(400, "Expected project revision is required")
    if expected == 2**53-1:
        _fail(409, "Project revision limit reached; no update was attempted")
    project_id = body.get("projectId")
    if project_id is not None:
        _id(project_id)
    elif expected != 0:
        _fail(409, "A new project must start at expected revision0")
    c = accounts._config()
    _cleanup(c, owner)
    for _ in range(MAX_RETRIES):
        prior, data = _catalog(c, owner)
        if project_id is not None:
            old = data["projects"].get(project_id)
            if old is None:
                _fail(404, "Project not found")
            if _manifest(old)["revision"] != expected:
                _fail(409, "Cloud project revision changed; local work was preserved")
        elif len(data["projects"]) >= MAX_PROJECTS:
            _fail(413, "Account reached its project-count limit")
        if len(data["uploads"]) >= MAX_UPLOADS or len(data["garbage"]) >= MAX_GARBAGE:
            _fail(429, "Finish or cancel pending cloud saves before starting another")
        reserved = sum(_manifest(v)["encodedBytes"] for v in data["projects"].values())
        reserved += sum(_descriptor(v, stored=True) and v["encodedBytes"] for v in data["uploads"].values())
        reserved += sum(_manifest(v)["encodedBytes"] for v in data["garbage"].values())
        if reserved + body["encodedBytes"] > OWNER_ENCODED_MAX:
            _fail(413, "Account project-storage budget reached; local work was preserved")
        upload_id = secrets.token_hex(16)
        assigned_id = project_id or secrets.token_hex(16)
        used_nonces = set(data["uploads"]) | set(data["receipts"]) | set(data["garbage"])
        used_nonces.update(_manifest(p)["uploadId"] for p in data["projects"].values())
        if upload_id in used_nonces or assigned_id in data["projects"] and project_id is None:
            continue
        now = int(time.time())
        record = {key: body[key] for key in ("codec", "rawBytes", "rawSha256", "encodedBytes", "encodedSha256")}
        record.update(uploadId=upload_id, projectId=assigned_id, name=name,
                      expectedRevision=expected, parts=parts, received={}, state="active",
                      createdAt=now, expiresAt=now+UPLOAD_TTL)
        data["uploads"][upload_id] = record
        data["receipts"] = {k: v for k, v in data["receipts"].items()
                            if _integer(v.get("expiresAt"), now+1)}
        if len(data["receipts"]) >= MAX_RECEIPTS:
            oldest = min(data["receipts"], key=lambda k: data["receipts"][k]["expiresAt"])
            del data["receipts"][oldest]
        if _cas(c, owner, prior, data):
            return {"uploadId": upload_id, "projectId": assigned_id, "partBytes": PART_BYTES,
                    "parts": parts, "expiresAt": record["expiresAt"]}
    _fail(409, "Project catalog changed; retry the save from fresh metadata")


def _part_cipher(c, owner, upload_id, index, raw):
    header = _json({"schema": PART_SCHEMA, "owner": owner, "uploadId": upload_id,
                    "index": index, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}).encode()
    return Fernet(c["fernet"].encode("ascii")).encrypt(len(header).to_bytes(4, "big") + header + raw).decode("ascii")


def _read_part(c, owner, upload_id, index, expected=None):
    value = _command(c, "GET", _chunk_key(owner, upload_id, index))
    try:
        if not isinstance(value, str) or not 0 < len(value) < PART_BYTES*2:
            raise ValueError()
        plaintext = Fernet(c["fernet"].encode("ascii")).decrypt(value.encode("ascii"))
        header_bytes = int.from_bytes(plaintext[:4], "big")
        if not 0 < header_bytes <= 2048:
            raise ValueError()
        header = _parse_json(plaintext[4:4+header_bytes])
        raw = plaintext[4+header_bytes:]
        sha = hashlib.sha256(raw).hexdigest()
        if (not isinstance(header, dict) or header.get("schema") != PART_SCHEMA or header.get("owner") != owner
                or header.get("uploadId") != upload_id or header.get("index") != index
                or header.get("bytes") != len(raw) or header.get("sha256") != sha
                or not 0 < len(raw) <= PART_BYTES):
            raise ValueError()
        if expected and (expected.get("bytes") != len(raw) or expected.get("sha256") != sha):
            raise ValueError()
        return raw
    except (ValueError, TypeError, KeyError, UnicodeError, InvalidToken):
        _fail(503, "Stored project part is missing or corrupt; no project was overwritten")


def put_part(owner, upload_id, index, raw):
    _owner(owner)
    _id(upload_id, "Upload")
    if not _integer(index, 0, MAX_PARTS-1) or not isinstance(raw, bytes) or not 0 < len(raw) <= PART_BYTES:
        _fail(400, "Invalid project upload part")
    c = accounts._config()
    digest = hashlib.sha256(raw).hexdigest()
    for _ in range(MAX_RETRIES):
        prior, data = _catalog(c, owner)
        upload = _upload(data, upload_id)
        expected_bytes = min(PART_BYTES, upload["encodedBytes"]-index*PART_BYTES)
        if index >= upload["parts"] or len(raw) != expected_bytes:
            _fail(400, "Project part length/index does not match the upload plan")
        receipt = upload["received"].get(str(index))
        if receipt is not None:
            if receipt != {"bytes": len(raw), "sha256": digest}:
                _fail(409, "A different part already occupies that upload index")
            if _read_part(c, owner, upload_id, index, receipt) != raw:
                _fail(503, "Project upload part integrity failed")
            return {"index": index, "bytes": len(raw), "sha256": digest, "confirmed": True}
        upload["received"][str(index)] = {"bytes": len(raw), "sha256": digest}
        cipher = _part_cipher(c, owner, upload_id, index, raw)
        if _cas(c, owner, prior, data, (_chunk_key(owner, upload_id, index), cipher)):
            return {"index": index, "bytes": len(raw), "sha256": digest, "confirmed": True}
    _fail(409, "Project upload changed; refresh before retrying this part")


def _decode_native(encoded, descriptor, *, stored=False):
    code = 503 if stored else 400
    if len(encoded) != descriptor["encodedBytes"] or hashlib.sha256(encoded).hexdigest() != descriptor["encodedSha256"]:
        _fail(code, "Project upload encoded size/hash does not match")
    if descriptor["codec"] == "gzip":
        try:
            decoder = zlib.decompressobj(16+zlib.MAX_WBITS)
            raw = decoder.decompress(encoded, descriptor["rawBytes"]+1)
            if len(raw) > descriptor["rawBytes"]:
                _fail(503 if stored else 413, "Project decompression exceeds the declared raw limit")
            if not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:
                raise ValueError()
        except (ValueError, zlib.error):
            _fail(code, "Project gzip stream is incomplete or contains trailing data")
    else:
        raw = encoded
    if len(raw) != descriptor["rawBytes"] or hashlib.sha256(raw).hexdigest() != descriptor["rawSha256"]:
        _fail(code, "Project raw size/hash does not match")
    try:
        native = _parse_json(raw.decode("utf-8"))
        if (not isinstance(native, dict) or not isinstance(native.get("engine"), str)
                or not native["engine"] or len(native["engine"]) > 256
                or not isinstance(native.get("project"), dict)
                or not isinstance(native.get("editor"), dict) or not isinstance(native.get("scene"), dict)
                or not isinstance(native["scene"].get("actors"), list)
                or isinstance(native.get("version"), bool)
                or not isinstance(native.get("version"), (str, int, float))):
            raise ValueError()
    except (ValueError, TypeError, UnicodeError, RecursionError):
        _fail(code, "Uploaded data is not a complete native §E project envelope")
    return raw


def _encoded_parts(c, owner, nonce, parts, received=None):
    pieces = []
    for index in range(parts):
        receipt = None if received is None else received.get(str(index))
        if received is not None and receipt is None:
            _fail(409, "Project upload is incomplete; previous cloud revision was preserved")
        pieces.append(_read_part(c, owner, nonce, index, receipt))
    return b"".join(pieces)


def commit_upload(owner, upload_id):
    _owner(owner)
    _id(upload_id, "Upload")
    c = accounts._config()
    for _ in range(MAX_RETRIES):
        prior, data = _catalog(c, owner)
        completed = data["receipts"].get(upload_id)
        if completed:
            current = data["projects"].get(completed.get("projectId"))
            if current and _manifest(current)["uploadId"] == upload_id:
                # An unknown transport outcome is recoverable without a second
                # publication or overwriting a later revision.
                load_project(owner, current["id"])
                return {"project": _public(current), "durable": True, "alreadyCommitted": True}
            _fail(409, "This upload committed previously; refresh the current cloud catalog")
        upload = _upload(data, upload_id)
        project_id = upload["projectId"]
        old = data["projects"].get(project_id)
        actual_revision = _manifest(old)["revision"] if old else 0
        if actual_revision != upload["expectedRevision"]:
            _fail(409, "Cloud project revision changed; uploaded and local work were preserved")
        if old is None and len(data["projects"]) >= MAX_PROJECTS:
            _fail(413, "Account reached its project-count limit")
        if old and len(data["garbage"]) >= MAX_GARBAGE:
            _fail(429, "Cloud cleanup is pending; previous project was preserved")
        encoded = _encoded_parts(c, owner, upload_id, upload["parts"], upload["received"])
        _decode_native(encoded, upload)
        now = int(time.time())
        manifest = {key: upload[key] for key in ("name", "codec", "parts", "rawBytes", "rawSha256",
                                                "encodedBytes", "encodedSha256", "uploadId")}
        manifest.update(id=project_id, revision=actual_revision+1, updatedAt=now)
        data["projects"][project_id] = manifest
        del data["uploads"][upload_id]
        if old:
            data["garbage"][old["uploadId"]] = old
        data["receipts"][upload_id] = {"projectId": project_id, "expiresAt": now+RECEIPT_TTL}
        while len(data["receipts"]) > MAX_RECEIPTS:
            del data["receipts"][min(data["receipts"], key=lambda k: data["receipts"][k]["expiresAt"])]
        if not _cas(c, owner, prior, data):
            continue
        cleanup_pending = False
        try:
            _cleanup(c, owner)
        except HTTPException:
            # Publication is already confirmed. Keep indexed cleanup journals;
            # do not misreport the successful atomic save as an uncommitted one.
            cleanup_pending = True
        return {"project": _public(manifest), "durable": True, "cleanupPending": cleanup_pending}
    _fail(409, "Cloud catalog changed during commit; refresh before retrying")


def load_project(owner, project_id):
    _owner(owner)
    _id(project_id)
    c = accounts._config()
    for attempt in range(2):
        _, data = _catalog(c, owner)
        manifest = data["projects"].get(project_id)
        if manifest is None:
            _fail(404, "Project not found")
        _manifest(manifest)
        try:
            encoded = _encoded_parts(c, owner, manifest["uploadId"], manifest["parts"])
            return _decode_native(encoded, manifest, stored=True), _public(manifest)
        except HTTPException:
            _, latest = _catalog(c, owner)
            if attempt == 0 and latest["projects"].get(project_id) != manifest:
                continue  # A concurrently superseded revision was reclaimed.
            raise
    _fail(503, "Cloud project changed while loading; refresh the catalog")


def cancel_upload(owner, upload_id):
    _owner(owner)
    _id(upload_id, "Upload")
    c = accounts._config()
    for _ in range(MAX_RETRIES):
        prior, data = _catalog(c, owner)
        upload = _upload(data, upload_id, allow_closed=True)
        upload["state"] = "cancelled"
        if _cas(c, owner, prior, data):
            _cleanup(c, owner)
            return {"ok": True, "uploadId": upload_id}
    _fail(409, "Upload changed; refresh before retrying cancellation")


def delete_project(owner, project_id, expected_revision):
    _owner(owner)
    _id(project_id)
    if not _integer(expected_revision, 1):
        _fail(400, "Expected project revision is required")
    c = accounts._config()
    _cleanup(c, owner)
    for _ in range(MAX_RETRIES):
        prior, data = _catalog(c, owner)
        old = data["projects"].get(project_id)
        if old is None:
            _fail(404, "Project not found")
        if _manifest(old)["revision"] != expected_revision:
            _fail(409, "Cloud project changed; deletion was not applied")
        if len(data["garbage"]) >= MAX_GARBAGE:
            _fail(429, "Cloud cleanup is pending; deletion was not applied")
        del data["projects"][project_id]
        data["garbage"][old["uploadId"]] = old
        if _cas(c, owner, prior, data):
            pending = False
            try:
                _cleanup(c, owner)
            except HTTPException:
                pending = True
            return {"ok": True, "projectId": project_id, "deletedRevision": expected_revision,
                    "cleanupPending": pending}
    _fail(409, "Cloud catalog changed; deletion was not applied")


async def _body(request, maximum, *, json_body=False, allow_empty=False):
    parts, total = [], 0
    async for part in request.stream():
        total += len(part)
        if total > maximum:
            _fail(413, "Project request body exceeds its bounded limit")
        parts.append(part)
    raw = b"".join(parts)
    if not json_body:
        return raw
    if not raw and allow_empty:
        return {}
    try:
        return _parse_json(raw)
    except (ValueError, UnicodeError, RecursionError):
        _fail(400, "Project request must contain valid finite JSON")


def install(app, authenticate, write_guard):
    """Register account-owned routes; callbacks are the Station authority."""
    async def owner_for(request, write=False):
        async def invoke(callback):
            if inspect.iscoroutinefunction(callback):
                value = await callback(request)
            else:
                value = await run_in_threadpool(callback, request)
            return await value if inspect.isawaitable(value) else value
        account = await invoke(authenticate)
        if not isinstance(account, tuple) or len(account) != 2 or not isinstance(account[1], dict):
            _fail(401, "Verified Google identity required")
        owner = _owner(account[1].get("id"))
        if write:
            allowed = await invoke(write_guard)
            if allowed is not None and allowed is not True:
                _fail(403, "Account project mutation denied")
        return owner

    @app.get("/api/forge/projects")
    async def cloud_list(request: Request):
        return JSONResponse(await run_in_threadpool(list_projects, await owner_for(request)),
                            headers={"Cache-Control": "no-store, private"})

    @app.post("/api/forge/projects/uploads")
    async def cloud_begin(request: Request):
        owner = await owner_for(request, True)
        if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
            _fail(415, "Project upload plans require application/json")
        body = await _body(request, 16384, json_body=True)
        return JSONResponse(await run_in_threadpool(begin_upload, owner, body),
                            headers={"Cache-Control": "no-store, private"})

    @app.put("/api/forge/projects/uploads/{upload_id}/parts/{index}")
    async def cloud_part(upload_id: str, index: int, request: Request):
        owner = await owner_for(request, True)
        if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/octet-stream":
            _fail(415, "Project parts require application/octet-stream")
        raw = await _body(request, PART_BYTES)
        return JSONResponse(await run_in_threadpool(put_part, owner, upload_id, index, raw),
                            headers={"Cache-Control": "no-store, private"})

    @app.post("/api/forge/projects/uploads/{upload_id}/commit")
    async def cloud_commit(upload_id: str, request: Request):
        owner = await owner_for(request, True)
        if await _body(request, 1024, json_body=True, allow_empty=True) != {}:
            _fail(400, "Commit uses the immutable upload plan; extra fields are not accepted")
        return JSONResponse(await run_in_threadpool(commit_upload, owner, upload_id),
                            headers={"Cache-Control": "no-store, private"})

    @app.delete("/api/forge/projects/uploads/{upload_id}")
    async def cloud_cancel(upload_id: str, request: Request):
        return JSONResponse(await run_in_threadpool(cancel_upload, await owner_for(request, True), upload_id),
                            headers={"Cache-Control": "no-store, private"})

    @app.get("/api/forge/projects/{project_id}")
    async def cloud_load(project_id: str, request: Request):
        raw, metadata = await run_in_threadpool(load_project, await owner_for(request), project_id)
        return StreamingResponse((raw[start:start+65536] for start in range(0, len(raw), 65536)),
            media_type="application/json", headers={"Cache-Control": "no-store, private",
            "Vary": "Authorization, Cookie", "X-SWRLZ-Project-Revision": str(metadata["revision"]),
            "X-SWRLZ-Project-SHA256": metadata["rawSha256"],
            "Content-Disposition": 'attachment; filename="project-'+project_id+'.swyrl.json"'})

    @app.delete("/api/forge/projects/{project_id}")
    async def cloud_delete(project_id: str, request: Request):
        value = request.query_params.get("expectedRevision", "")
        if not value.isascii() or not value.isdigit() or len(value) > 16:
            _fail(400, "Expected project revision is required")
        return JSONResponse(await run_in_threadpool(delete_project, await owner_for(request, True),
                                                    project_id, int(value)),
                            headers={"Cache-Control": "no-store, private"})
