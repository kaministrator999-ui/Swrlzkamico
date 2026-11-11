"""Bounded Hugging Face process-owned dispatcher for durable Chat jobs.

Redis remains canonical for account/job/event state. Execution occurs in the
active HF server process rather than in an external provider queue. An in-flight
job may be interrupted by a server restart; clients detect stale jobs through
existing canonical-state reconciliation.
"""
from __future__ import annotations

import asyncio
import os
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

_TOPIC = "swrlz-generation"
_MAX_WORKERS = max(1, min(int(os.environ.get("SWRLZ_HF_GENERATION_WORKERS", "1")), 4))
_MAX_PENDING = max(_MAX_WORKERS, min(int(os.environ.get("SWRLZ_HF_GENERATION_PENDING_MAX", "32")), 128))
_EXECUTOR = ThreadPoolExecutor(max_workers=_MAX_WORKERS, thread_name_prefix="swrlz-hf-generation")
_LOCK = threading.Lock()
_INFLIGHT: dict[str, Future[None]] = {}


def _run(payload: dict[str, Any]) -> None:
    # Import lazily to avoid circular imports during FastAPI route setup.
    from queues.swrlz_generation_v3 import generate_swrlz_response

    asyncio.run(generate_swrlz_response(payload))


def _finished(request_id: str, future: Future[None]) -> None:
    with _LOCK:
        if _INFLIGHT.get(request_id) is future:
            _INFLIGHT.pop(request_id, None)
    try:
        future.result()
    except Exception as exc:
        # Never log user prompts, chat histories, or account identifiers.
        print(f"SWRLZ_HF_GENERATION_WORKER_FAILED {type(exc).__name__}", flush=True)


async def send(topic: str, payload: dict[str, Any], *, idempotency_key: str | None = None) -> str:
    """Schedule a canonical Redis-recorded job without blocking the HTTP response."""
    if topic != _TOPIC:
        raise ValueError("SWRLZ_HF_GENERATION_TOPIC_INVALID")
    request_id = str(idempotency_key or payload.get("requestId") or "").strip()
    if not request_id or request_id != str(payload.get("requestId") or "").strip():
        raise ValueError("SWRLZ_HF_GENERATION_REQUEST_ID_INVALID")
    with _LOCK:
        existing = _INFLIGHT.get(request_id)
        if existing is not None and not existing.done():
            return "hf:" + request_id
        if len(_INFLIGHT) >= _MAX_PENDING:
            raise RuntimeError("SWRLZ_HF_GENERATION_BACKLOG_FULL")
        future = _EXECUTOR.submit(_run, dict(payload))
        _INFLIGHT[request_id] = future
    future.add_done_callback(lambda completed: _finished(request_id, completed))
    return "hf:" + request_id
