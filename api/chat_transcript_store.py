"""Private cross-worker transcript checkpoints for resumable Chat generation.

The active model/KV state remains owned by the worker that started generation.
This module persists only bounded response-position metadata and generated assistant
text so another worker can answer transcript synchronization requests without
starting a duplicate generation. /tmp is never authoritative.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.parse
import uuid
from typing import Any

import requests
from api.chat_client_debug import _lockdown as _chat_lockdown

BLOB_API = "https://vercel.com/api/blob"
PREFIX = "swrlz/chat/generation-transcripts/v1"
MAX_SNAPSHOT_BYTES = 256 * 1024
TTL_SECONDS = 30 * 60
OWNER_ID = f"{os.environ.get('VERCEL_REGION','region')}:{uuid.uuid4().hex}"


def _compact(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _path(request_id: str) -> str:
    digest = hashlib.sha256(str(request_id).encode("utf-8")).hexdigest()
    return f"{PREFIX}/{digest}.json"


class SharedTranscriptStore:
    def __init__(self) -> None:
        read_write = os.environ.get("BLOB_READ_WRITE_TOKEN", "").strip()
        oidc = os.environ.get("VERCEL_OIDC_TOKEN", "").strip()
        configured_store = os.environ.get("BLOB_STORE_ID", "").strip()
        if read_write:
            pieces = read_write.split("_")
            store_id = pieces[3] if len(pieces) > 3 else ""
            self.token = read_write
            self.store_id = store_id.removeprefix("store_")
            self.auth_kind = "read-write"
        elif oidc and configured_store:
            self.token = oidc
            self.store_id = configured_store.removeprefix("store_")
            self.auth_kind = "oidc"
        else:
            self.token = ""
            self.store_id = ""
            self.auth_kind = "unconfigured"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "swrlz-chat-transcript-store/1"})

    @property
    def configured(self) -> bool:
        return bool(self.token and self.store_id)

    def describe(self) -> dict[str, Any]:
        return {
            "contract": "shared-private-blob-v1",
            "configured": self.configured,
            "access": "private",
            "authKind": self.auth_kind,
            "ttlSeconds": TTL_SECONDS,
            "ownerId": OWNER_ID,
        }

    def _headers(self) -> dict[str, str]:
        if not self.configured:
            raise RuntimeError("CHAT_TRANSCRIPT_BLOB_NOT_CONFIGURED")
        return {
            "authorization": f"Bearer {self.token}",
            "x-vercel-blob-store-id": self.store_id,
            "x-api-version": "12",
            "x-api-blob-request-attempt": "0",
            "x-api-blob-request-id": f"{self.store_id}:{int(time.time()*1000)}:{uuid.uuid4().hex[:12]}",
            "content-type": "application/json; charset=utf-8",
            "x-content-type": "application/json; charset=utf-8",
            "x-vercel-blob-access": "private",
            "x-add-random-suffix": "0",
            "x-allow-overwrite": "1",
            "x-cache-control-max-age": "0",
        }

    def read(self, request_id: str) -> dict[str, Any] | None:
        started=time.perf_counter_ns()
        _chat_lockdown("transcript-read-enter", request_id=request_id, configured=self.configured, authKind=self.auth_kind)
        if not self.configured:
            _chat_lockdown("transcript-read-skip", request_id=request_id, reason="unconfigured")
            return None
        pathname = _path(request_id)
        encoded = urllib.parse.quote(pathname, safe="/-._~")
        url = f"https://{self.store_id}.private.blob.vercel-storage.com/{encoded}?cache=0&t={int(time.time()*1000)}"
        response = self.session.get(url, headers={"authorization": f"Bearer {self.token}"}, timeout=(3, 8))
        _chat_lockdown("transcript-read-response", request_id=request_id, status=response.status_code, bytes=len(response.content), durationNs=time.perf_counter_ns()-started)
        if response.status_code == 404:
            _chat_lockdown("transcript-read-miss", request_id=request_id)
            return None
        response.raise_for_status()
        data = response.content
        if len(data) > MAX_SNAPSHOT_BYTES:
            raise RuntimeError("CHAT_TRANSCRIPT_SNAPSHOT_TOO_LARGE")
        value = json.loads(data.decode("utf-8"))
        if not isinstance(value, dict) or str(value.get("requestId") or "") != str(request_id):
            raise RuntimeError("CHAT_TRANSCRIPT_SNAPSHOT_INVALID")
        updated = float(value.get("updatedAt") or 0)
        if updated and time.time() - updated > TTL_SECONDS:
            _chat_lockdown("transcript-read-expired", request_id=request_id, ageSeconds=time.time()-updated)
            return None
        _chat_lockdown("transcript-read-exit", request_id=request_id, snapshot=value, durationNs=time.perf_counter_ns()-started)
        return value

    def write(self, snapshot: dict[str, Any]) -> None:
        request_id=str(snapshot.get("requestId") or "")[:128]
        started=time.perf_counter_ns()
        _chat_lockdown("transcript-write-enter", request_id=request_id, configured=self.configured, snapshot=snapshot)
        if not self.configured:
            _chat_lockdown("transcript-write-skip", request_id=request_id, reason="unconfigured")
            return
        body = _compact(snapshot)
        if len(body) > MAX_SNAPSHOT_BYTES:
            raise RuntimeError("CHAT_TRANSCRIPT_SNAPSHOT_TOO_LARGE")
        response = self.session.put(
            BLOB_API + "/",
            params={"pathname": _path(str(snapshot.get("requestId") or ""))},
            headers=self._headers(),
            data=body,
            timeout=(3, 10),
        )
        _chat_lockdown("transcript-write-response", request_id=request_id, status=response.status_code, ok=response.ok, bytes=len(body), durationNs=time.perf_counter_ns()-started)
        if not response.ok:
            raise RuntimeError(f"CHAT_TRANSCRIPT_BLOB_WRITE_HTTP_{response.status_code}")
        _chat_lockdown("transcript-write-exit", request_id=request_id, durationNs=time.perf_counter_ns()-started)


STORE = SharedTranscriptStore()
