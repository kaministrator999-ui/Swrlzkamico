"""Account-owned, encrypted, incremental ChatGPT export archive.

This is a separate read-only archive, never a native Station conversation,
model memory, shared training set, or full-snapshot extension.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import time
import zipfile

from cryptography.fernet import Fernet
from fastapi import HTTPException

import account_chat_store
import github_connection as gh

SCHEMA = "swrlz-chatgpt-archive-v1"
ID = re.compile(r"^[a-zA-Z0-9_-]{8,120}$")
ENTRY = re.compile(r"^(?:conversations(?:-\d{3})?|chat)\.json$")
MAX_ZIP = 110 * 1024 * 1024
MAX_EXPANDED = 400 * 1024 * 1024
MAX_ENTRY = 64 * 1024 * 1024
MAX_FILES = 100
MAX_THREADS = 12000
MAX_MESSAGES = 2500
MAX_MESSAGE_CHARS = 200000
MAX_RECORD = 2200000
_CAS = (
    "local raw=redis.call('GET',KEYS[1]); "
    "local want=tonumber(ARGV[1]); "
    "if not raw then if want~=0 then return 0 end; "
    "else local ok,rec=pcall(cjson.decode,raw); "
    "if not ok or type(rec)~='table' or tonumber(rec['revision'])~=want then return 0 end end; "
    "redis.call('SET',KEYS[1],ARGV[2]); return 1"
)


def _owner(owner):
    # Derive solely from Station's verified Google account, never request JSON.
    account_chat_store._chat_key(owner)
    return hashlib.sha256(owner.encode("utf-8")).hexdigest()


def _key(owner, conversation_id):
    if not ID.fullmatch(str(conversation_id or "")):
        raise HTTPException(400, "Invalid ChatGPT conversation identifier")
    return "swrlz:google:chatgpt-archive:v1:" + _owner(owner) + ":" + conversation_id


def _index(owner):
    return "swrlz:google:chatgpt-archive-index:v1:" + _owner(owner)


def _config():
    return account_chat_store._config()


def _encrypted(c, payload):
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(raw) > MAX_RECORD:
        raise HTTPException(413, "Imported conversation exceeds per-conversation storage limit; nothing was discarded")
    return Fernet(c["fernet"].encode("ascii")).encrypt(raw).decode("ascii")


def _read_record(owner, conversation_id, c=None):
    c = c or _config()
    raw = gh._redis(c, "GET", _key(owner, conversation_id))
    if raw is None:
        return None, 0
    try:
        envelope = json.loads(raw)
        rev = envelope["revision"]
        if not isinstance(rev, int) or rev < 1:
            raise ValueError("invalid revision")
        record = account_chat_store._decrypt(c, envelope["encrypted"])
        if record.get("schema") != SCHEMA or record.get("owner") != owner or record.get("id") != conversation_id:
            raise ValueError("invalid owner or schema")
        if record.get("revision") != rev or not isinstance(record.get("messages"), list):
            raise ValueError("invalid record")
        return record, rev
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(503, "Imported conversation storage integrity failed; no overwrite attempted") from exc


def _visible_messages(conv):
    mapping = conv.get("mapping")
    if not isinstance(mapping, dict):
        raise HTTPException(400, "ChatGPT conversation mapping is invalid")
    node_id = conv.get("current_node")
    visited = set()
    selected = []
    # Follow the actual current branch, not all alternate regenerated branches.
    while node_id and node_id in mapping:
        if node_id in visited or len(visited) >= 10000:
            raise HTTPException(400, "Invalid ChatGPT conversation branch")
        visited.add(node_id)
        node = mapping[node_id]
        if not isinstance(node, dict):
            raise HTTPException(400, "Invalid ChatGPT message node")
        message = node.get("message")
        if isinstance(message, dict):
            role = (message.get("author") or {}).get("role")
            body = message.get("content") or {}
            if role in ("user", "assistant") and isinstance(body, dict) and body.get("content_type") in ("text", "multimodal_text"):
                parts = body.get("parts") or []
                if isinstance(parts, list):
                    value = "\n".join(p for p in parts if isinstance(p, str)).strip()
                    msg_id = str(message.get("id") or node_id)
                    if value and ID.fullmatch(msg_id):
                        if len(value) > MAX_MESSAGE_CHARS:
                            raise HTTPException(413, "Imported message exceeds size limit; no silent truncation")
                        selected.append({"id": msg_id, "role": role, "text": value,
                                         "createdAt": message.get("create_time") if isinstance(message.get("create_time"), (int, float)) else None})
        node_id = node.get("parent")
    # Empty/attachment-only conversations in genuine exports are reported as
    # unsupported, not an import-killing exception.
    selected.reverse()
    if len(selected) > MAX_MESSAGES:
        raise HTTPException(413, "Imported conversation has too many messages")
    return selected


def normalize(conv):
    if not isinstance(conv, dict):
        raise HTTPException(400, "Invalid ChatGPT conversation record")
    cid = str(conv.get("conversation_id") or conv.get("id") or "")
    if not ID.fullmatch(cid):
        raise HTTPException(400, "Missing or invalid ChatGPT conversation ID")
    title = str(conv.get("title") or "Untitled ChatGPT conversation")[:240]
    timestamp = conv.get("update_time")
    updated = float(timestamp) if isinstance(timestamp, (int, float)) and 0 <= timestamp < 1e12 else 0
    messages = _visible_messages(conv)
    return {"id": cid, "title": title, "updatedAt": updated, "messages": messages,
            "unsupported": not bool(messages)}


def merge(old, new, owner):
    """Union by message ID; older snapshots cannot erase later imported history."""
    previous = {m["id"]: m for m in (old or {}).get("messages", [])}
    newer = 0
    for message in new["messages"]:
        if message["id"] not in previous:
            previous[message["id"]] = message
            newer += 1
    messages = sorted(previous.values(), key=lambda m: (
        m.get("createdAt") if isinstance(m.get("createdAt"), (float, int)) else 0, m["id"]))
    last = max(new["updatedAt"], (old or {}).get("updatedAt", 0))
    title = new["title"] if not old or new["updatedAt"] >= old.get("updatedAt", 0) else old["title"]
    changed = not old or newer > 0 or (new["updatedAt"] > old.get("updatedAt", 0) and title != old["title"])
    return {"schema": SCHEMA, "owner": owner, "id": new["id"],
            "title": title, "updatedAt": last, "messages": messages}, newer, changed


def upsert(owner, incoming):
    c = _config()
    cid = incoming["id"]
    for attempt in range(5):
        prior, expected = _read_record(owner, cid, c)
        merged, added, changed = merge(prior, incoming, owner)
        if changed:
            merged["revision"] = expected + 1
            env = {"revision": merged["revision"], "encrypted": _encrypted(c, merged)}
            status = gh._redis(c, "EVAL", _CAS, "1", _key(owner, cid), str(expected),
                               json.dumps(env, separators=(",", ":")))
            if status not in (1, "1"):
                if status in (0, "0"):
                    continue
                raise HTTPException(503, "Import storage did not confirm atomic merge")
        # Idempotent index repair is safe after any partial previous write.
        indexed = gh._redis(c, "ZADD", _index(owner), str(merged["updatedAt"]), cid)
        if not isinstance(indexed, int):
            raise HTTPException(503, "Import index update was not confirmed; retry is safe")
        return {"created": prior is None, "updated": prior is not None and changed,
                "skipped": prior is not None and not changed, "addedMessages": added}
    raise HTTPException(409, "Concurrent import changed this conversation; retry the same export")


def archive_entries(path):
    if os.path.getsize(path) > MAX_ZIP:
        raise HTTPException(413, "ChatGPT archive upload exceeds maximum size")
    try:
        with zipfile.ZipFile(path) as z:
            files = [x for x in z.infolist() if not x.is_dir() and ENTRY.fullmatch(x.filename)]
            if not files or len(files) > MAX_FILES:
                raise HTTPException(400, "Archive requires conversations.json or conversations-000.json series")
            if len(z.infolist()) > 5000:
                raise HTTPException(413, "Archive has too many entries")
            if sum(x.file_size for x in z.infolist()) > MAX_EXPANDED:
                raise HTTPException(413, "Archive expanded size exceeds limit")
            for x in files:
                if x.file_size > MAX_ENTRY or x.flag_bits & 0x1:
                    raise HTTPException(413, "Encrypted or oversized archive entry not supported")
                if x.compress_size == 0 or x.file_size > max(x.compress_size * 250, 1048576):
                    raise HTTPException(413, "Archive entry compression ratio exceeds limit")
                try:
                    batch = json.loads(z.read(x))
                except (UnicodeError, ValueError, RuntimeError) as exc:
                    raise HTTPException(400, "ChatGPT archive contains malformed JSON") from exc
                if not isinstance(batch, list):
                    raise HTTPException(400, "ChatGPT conversations JSON must contain a list")
                for conv in batch:
                    yield normalize(conv)
    except (zipfile.BadZipFile, EOFError) as exc:
        raise HTTPException(400, "Invalid ZIP archive") from exc


def import_archive(path, owner):
    # Streaming progress lets a browser acknowledge partial commits and retry.
    seen = set()
    stats = {"conversations": 0, "created": 0, "updated": 0, "skipped": 0,
             "unsupported": 0, "addedMessages": 0}
    for item in archive_entries(path):
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        if item.get("unsupported"):
            stats["unsupported"] += 1
            continue
        if len(seen) > MAX_THREADS:
            raise HTTPException(413, "Too many conversations in archive")
        result = upsert(owner, item)
        stats["conversations"] += 1
        for k in ("created", "updated", "skipped", "addedMessages"):
            stats[k] += int(result[k])
        if stats["conversations"] % 20 == 0:
            yield {"type": "PROGRESS", **stats}
    yield {"type": "COMPLETE", **stats}


def list_archive(owner, offset=0, limit=30):
    c = _config()
    offset = max(0, min(int(offset), 100000))
    limit = max(1, min(int(limit), 50))
    ids = gh._redis(c, "ZREVRANGE", _index(owner), str(offset), str(offset + limit - 1))
    if ids is None:
        raise HTTPException(503, "Imported conversation index unavailable")
    result = []
    for cid in ids:
        rec, _ = _read_record(owner, cid, c)
        if rec:
            result.append({"id": cid, "title": rec["title"],
                           "updatedAt": rec["updatedAt"], "messageCount": len(rec["messages"])})
    count = gh._redis(c, "ZCARD", _index(owner))
    return {"items": result, "offset": offset, "total": int(count or 0), "nextOffset": offset + len(ids) if len(ids) == limit else None}


def read_archive(owner, conversation_id):
    record, _ = _read_record(owner, conversation_id)
    if record is None:
        raise HTTPException(404, "Imported conversation not found")
    return {"id": record["id"], "title": record["title"], "updatedAt": record["updatedAt"],
            "messages": record["messages"]}
