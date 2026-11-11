"""Private TTL-bounded, Redis-backed Chat transcript checkpoints.

Active model state remains owned by the Hugging Face generation worker.
Only bounded generated text and synchronization metadata are shared.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from typing import Any

from api.chat_client_debug import _lockdown as _chat_lockdown
from api.durable_redis_store import RedisRestChatStore

MAX_SNAPSHOT_BYTES = 256 * 1024
TTL_SECONDS = 30 * 60
KEY_PREFIX = "swrlz:v1:chat-transcript:"
OWNER_ID = f"{os.environ.get('SPACE_ID', 'hf-server')}:{uuid.uuid4().hex}"


def _compact(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _key(request_id: str) -> str:
    return KEY_PREFIX + hashlib.sha256(str(request_id).encode("utf-8")).hexdigest()


class SharedTranscriptStore:
    @property
    def configured(self) -> bool:
        return RedisRestChatStore.configured()

    def describe(self) -> dict[str, Any]:
        return {
            "contract": "shared-redis-transcript-v1",
            "configured": self.configured,
            "access": "private",
            "authKind": "redis-rest" if self.configured else "unconfigured",
            "ttlSeconds": TTL_SECONDS,
            "ownerId": OWNER_ID,
        }

    def read(self, request_id: str) -> dict[str, Any] | None:
        started = time.perf_counter_ns()
        _chat_lockdown("transcript-read-enter", request_id=request_id, configured=self.configured)
        if not self.configured:
            return None
        raw = RedisRestChatStore.from_env()._command("GET", _key(request_id))
        if raw is None:
            return None
        value = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
        if not isinstance(value, dict) or str(value.get("requestId") or "") != str(request_id):
            raise RuntimeError("CHAT_TRANSCRIPT_SNAPSHOT_INVALID")
        if len(_compact(value)) > MAX_SNAPSHOT_BYTES:
            raise RuntimeError("CHAT_TRANSCRIPT_SNAPSHOT_TOO_LARGE")
        updated = float(value.get("updatedAt") or 0)
        if updated and time.time() - updated > TTL_SECONDS:
            return None
        _chat_lockdown("transcript-read-exit", request_id=request_id, durationNs=time.perf_counter_ns() - started)
        return value

    def write(self, snapshot: dict[str, Any]) -> None:
        request_id = str(snapshot.get("requestId") or "")[:128]
        _chat_lockdown("transcript-write-enter", request_id=request_id, configured=self.configured)
        if not self.configured:
            return
        if not request_id:
            raise ValueError("CHAT_TRANSCRIPT_REQUEST_ID_REQUIRED")
        data = _compact(snapshot)
        if len(data) > MAX_SNAPSHOT_BYTES:
            raise RuntimeError("CHAT_TRANSCRIPT_SNAPSHOT_TOO_LARGE")
        RedisRestChatStore.from_env()._command(
            "SETEX", _key(request_id), TTL_SECONDS, data.decode("utf-8"), sensitive=True
        )
        _chat_lockdown("transcript-write-exit", request_id=request_id, bytes=len(data))


STORE = SharedTranscriptStore()
