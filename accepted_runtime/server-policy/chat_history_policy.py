"""Runtime-hot canonical Chat history reconstruction policy.

This module is intentionally read-only with respect to durable Chat state. The
stable Server remains authoritative for authentication, Redis durability, turn
creation, and terminal commits. This policy only decides how already-authoritative
server message records are enumerated into bounded LALM history.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from api.durable_chat_contract import MessageRecord

CONTRACT_ID = "swrlz-hot-chat-history-policy-v1"
HOT_REVISION = "1.0.0-runtime-history-compat-v1"
CURRENT_INDEX = "message_index"
LEGACY_INDEX = "messages"
MAX_INDEX_SCAN = 1000
MAX_HISTORY = 32
MAX_TEXT = 2000


def _camera(stage: str, **fields: Any) -> None:
    record = {
        "contract": CONTRACT_ID,
        "revision": HOT_REVISION,
        "stage": stage,
        "atUnixMs": int(time.time() * 1000),
    }
    for key, value in fields.items():
        if value is None or isinstance(value, (str, int, float, bool)):
            record[str(key)[:64]] = value
    print("SWRLZ_CHAT_HISTORY_HOT " + json.dumps(record, ensure_ascii=False, separators=(",", ":")), flush=True)


def _bounded_count(value: Any, maximum: int = MAX_INDEX_SCAN) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 1
    return max(1, min(parsed, maximum))


def _message(redis: Any, *, user_id: str, message_id: str) -> MessageRecord | None:
    value = redis._get_json(redis._key("message", user_id, message_id), MessageRecord)
    if value is None:
        return None
    if value.user_id != user_id:
        return None
    return value


def _index_messages(redis: Any, *, user_id: str, thread_id: str, index_name: str, limit: int) -> list[MessageRecord]:
    count = _bounded_count(limit)
    ids = redis._command("ZRANGE", redis._key(index_name, user_id, thread_id), -count, -1) or []
    out: list[MessageRecord] = []
    for raw_id in ids:
        message = _message(redis, user_id=user_id, message_id=str(raw_id))
        if message is not None and message.thread_id == thread_id:
            out.append(message)
    return out


def _merged_records(redis: Any, *, user_id: str, thread_id: str, limit: int) -> tuple[list[MessageRecord], int, int]:
    scan = max(64, _bounded_count(limit) * 4)
    current = _index_messages(redis, user_id=user_id, thread_id=thread_id, index_name=CURRENT_INDEX, limit=scan)
    legacy = _index_messages(redis, user_id=user_id, thread_id=thread_id, index_name=LEGACY_INDEX, limit=scan)
    merged: dict[str, MessageRecord] = {}
    for message in [*legacy, *current]:
        existing = merged.get(message.message_id)
        if existing is None or float(message.updated_at or 0) >= float(existing.updated_at or 0):
            merged[message.message_id] = message
    ordered = sorted(merged.values(), key=lambda item: (float(item.created_at or 0), str(item.message_id)))
    return ordered[-MAX_INDEX_SCAN:], len(current), len(legacy)


def resolve_history(
    *,
    redis: Any,
    user_id: str,
    thread_id: str,
    request_id: str,
    limit: int = MAX_HISTORY,
) -> dict[str, Any]:
    """Return bounded canonical history plus non-content telemetry.

    No browser/client history is accepted here. Every selected turn is resolved
    from the durable server-owned message record after its ID is discovered in a
    current or legacy Redis sorted-set index.
    """
    history_limit = max(1, min(int(limit), MAX_HISTORY))
    records, current_count, legacy_count = _merged_records(
        redis, user_id=user_id, thread_id=thread_id, limit=history_limit
    )
    history: list[dict[str, str]] = []
    for message in records:
        if message.request_id == request_id:
            continue
        if message.role not in {"USER", "ASSISTANT"}:
            continue
        if message.state in {"STREAMING", "FAILED", "CANCELLED"}:
            continue
        text = str(message.committed_text or "").strip()
        if not text:
            continue
        history.append({"role": message.role, "text": text[:MAX_TEXT]})
    selected = history[-history_limit:]
    meta = {
        "contract": CONTRACT_ID,
        "revision": HOT_REVISION,
        "source": "runtime-hot",
        "currentIndexedMessages": current_count,
        "legacyIndexedMessages": legacy_count,
        "mergedMessages": len(records),
        "selectedMessages": len(selected),
    }
    _camera(
        "history-resolved",
        requestId=request_id,
        threadId=thread_id,
        currentIndexedMessages=current_count,
        legacyIndexedMessages=legacy_count,
        mergedMessages=len(records),
        selectedMessages=len(selected),
    )
    return {"history": selected, "meta": meta}


@dataclass
class _FakeRecord:
    message_id: str
    thread_id: str
    user_id: str
    role: str
    committed_text: str
    state: str
    request_id: str
    created_at: float
    updated_at: float


class _FakeRedis:
    def __init__(self) -> None:
        self.indexes: dict[str, list[str]] = {}
        self.messages: dict[str, _FakeRecord] = {}

    def _key(self, kind: str, *parts: str) -> str:
        return ":".join((kind, *parts))

    def _command(self, command: str, key: str, start: int, end: int):
        assert command == "ZRANGE"
        values = list(self.indexes.get(key, []))
        if start < 0:
            start = max(0, len(values) + start)
        if end < 0:
            end = len(values) + end
        return values[start : end + 1]

    def _get_json(self, key: str, _cls: Any):
        return self.messages.get(key)


def _self_test() -> dict[str, Any]:
    redis = _FakeRedis()
    user = "u"
    thread = "t"
    records = [
        _FakeRecord("m1", thread, user, "USER", "write code", "COMPLETE", "r1", 1.0, 1.0),
        _FakeRecord("m2", thread, user, "ASSISTANT", "```python\nprint('ok')\n```", "COMPLETE", "r1", 2.0, 2.0),
        _FakeRecord("m3", thread, user, "USER", "current", "COMPLETE", "r2", 3.0, 3.0),
        _FakeRecord("m4", thread, user, "ASSISTANT", "ignore failed", "FAILED", "old-failed", 4.0, 4.0),
    ]
    for item in records:
        redis.messages[redis._key("message", user, item.message_id)] = item
    redis.indexes[redis._key(LEGACY_INDEX, user, thread)] = ["m1", "m2", "m4"]
    redis.indexes[redis._key(CURRENT_INDEX, user, thread)] = ["m2", "m3"]
    result = resolve_history(redis=redis, user_id=user, thread_id=thread, request_id="r2", limit=32)
    history = result.get("history") or []
    meta = result.get("meta") or {}
    checks = {
        "legacyRecovered": len(history) == 2,
        "ordered": [item.get("role") for item in history] == ["USER", "ASSISTANT"],
        "deduplicated": meta.get("mergedMessages") == 4,
        "currentRequestExcluded": all(item.get("text") != "current" for item in history),
        "failedExcluded": all(item.get("text") != "ignore failed" for item in history),
        "countsBounded": meta.get("legacyIndexedMessages") == 3 and meta.get("currentIndexedMessages") == 2,
    }
    return {"ok": all(checks.values()), "checks": checks, "contract": CONTRACT_ID, "revision": HOT_REVISION}


_SELF_TEST = _self_test()
if not _SELF_TEST.get("ok"):
    raise RuntimeError("HOT_CHAT_HISTORY_POLICY_SELF_TEST_FAILED")


def inspect_policy() -> dict[str, Any]:
    return {
        "ok": True,
        "contract": CONTRACT_ID,
        "revision": HOT_REVISION,
        "readOnly": True,
        "serverAuthorityPreserved": True,
        "legacyIndexCompatibility": True,
        "currentIndexCompatibility": True,
        "selfTest": dict(_SELF_TEST),
    }
