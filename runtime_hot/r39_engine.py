"""Hot-swappable R39 engine entrypoint.

This module is the performance/tuning boundary for LOCAL_R39. The stable server owns
routing/auth/contracts; inference experiments live here on non-deploying `dev` and are
loaded into /tmp by /api/hot/sync without a Vercel redeploy.

Public contract: ENGINE_ID, MODEL_SHA256, inspect_engine(), generate_events().
"""
from __future__ import annotations

import threading
import time
from typing import Any

import numpy as np

import swyrlz.r39_inference as base
import swyrlz.r39_tokenizer_patch  # noqa: F401

ENGINE_ID = base.ENGINE_ID
MODEL_SHA256 = base.MODEL_SHA256
HOT_REVISION = "2.1.16-hot-boundary-v3-reconnect"

# Keep the bundled implementation as the correctness oracle/fallback ABI, but move
# performance-sensitive policy here so future tuning is a dev hot-sync, not a deploy.
_ORIGINAL_MATRIX = base.R39Model.matrix
_ORIGINAL_RENDER_CHAT_PROMPT = base.render_chat_prompt

# Best-effort detached generation registry. A request starts one worker thread that
# consumes the native engine independently of the browser socket and retains ordered
# raw engine events for reconnect/replay. This survives browser suspension while the
# current Vercel worker remains alive; a platform instance replacement is still a hard
# boundary until the stable server can provide durable cross-instance job storage.
_JOB_LOCK = threading.RLock()
_JOBS: dict[str, dict[str, Any]] = {}
_JOB_TTL_SECONDS = 15 * 60
_MAX_JOBS = 12


def _cache(self: base.R39Model) -> dict[str, np.ndarray]:
    cache = getattr(self, "_hot_tensor_cache", None)
    if cache is None:
        cache = {}
        self._hot_tensor_cache = cache
    return cache


def _hot_matrix(self: base.R39Model, name: str) -> np.ndarray:
    d = self.desc[name]
    shape = d["shape"]
    elements = 1
    for dim in shape:
        elements *= int(dim)
    if elements <= 262_144:
        cache = _cache(self)
        hit = cache.get(name)
        if hit is not None:
            return hit
        value = _ORIGINAL_MATRIX(self, name)
        cache[name] = value
        return value
    return _ORIGINAL_MATRIX(self, name)


def _hot_vector(self: base.R39Model, name: str) -> np.ndarray:
    return _hot_matrix(self, name).reshape(-1)


def _hot_matvec(self: base.R39Model, name: str, x: np.ndarray) -> np.ndarray:
    d = self.desc[name]
    shape = d["shape"]
    cols = int(shape[0])
    rows = int(shape[1]) if len(shape) > 1 else 1
    if x.size != cols:
        raise base.R39InferenceError("R39_MATVEC_SHAPE_MISMATCH", f"{name}: expected {cols}, got {x.size}")
    rb = self._row_bytes(d["kind"], cols)
    raw = self._raw(name)
    target_bytes = 16 * 1024 * 1024
    batch_rows = max(1, min(rows, max(64, target_bytes // max(4 * cols, 1))))
    out = np.empty(rows, dtype=np.float32)
    for start in range(0, rows, batch_rows):
        count = min(batch_rows, rows - start)
        block = raw[start * rb:(start + count) * rb]
        matrix = base._deq(d["kind"], block, (cols, count))
        out[start:start + count] = matrix @ x
    return out


def _hot_render_chat_prompt(payload):
    clone = dict(payload)
    directive = str(clone.get("responseDirective") or "").strip()
    if directive.startswith("Answer directly and truthfully."):
        clone["responseDirective"] = "Answer directly and truthfully."
    return _ORIGINAL_RENDER_CHAT_PROMPT(clone)


base.R39Model.matrix = _hot_matrix
base.R39Model.vector = _hot_vector
base.R39Model.matvec = _hot_matvec
base.render_chat_prompt = _hot_render_chat_prompt


def _cleanup_jobs(now: float | None = None) -> None:
    now = time.time() if now is None else now
    with _JOB_LOCK:
        expired = [rid for rid, job in _JOBS.items() if job.get("done") and now - float(job.get("updatedAt", now)) > _JOB_TTL_SECONDS]
        for rid in expired:
            _JOBS.pop(rid, None)
        if len(_JOBS) > _MAX_JOBS:
            ordered = sorted(_JOBS.items(), key=lambda item: float(item[1].get("updatedAt", 0)))
            for rid, job in ordered:
                if len(_JOBS) <= _MAX_JOBS:
                    break
                if job.get("done"):
                    _JOBS.pop(rid, None)


def _append_job_event(job: dict[str, Any], event: dict[str, Any]) -> None:
    condition: threading.Condition = job["condition"]
    with condition:
        job["events"].append(dict(event))
        job["updatedAt"] = time.time()
        condition.notify_all()


def _run_job(job: dict[str, Any], payload: dict[str, Any], is_cancelled) -> None:
    try:
        for event in base.generate_events(payload, is_cancelled):
            _append_job_event(job, event)
    except Exception as exc:
        _append_job_event(job, {
            "type": "FAILED",
            "phase": "ERROR",
            "reason": f"Detached R39 worker failed: {type(exc).__name__}: {exc}",
            "categories": ["R39_DETACHED_WORKER_FAILED"],
        })
    finally:
        condition: threading.Condition = job["condition"]
        with condition:
            job["done"] = True
            job["updatedAt"] = time.time()
            condition.notify_all()


def _job_for(payload: dict[str, Any], is_cancelled):
    request_id = str(payload.get("requestId") or "").strip()
    if not request_id:
        return None
    _cleanup_jobs()
    with _JOB_LOCK:
        existing = _JOBS.get(request_id)
        if existing is not None:
            return existing
        condition = threading.Condition(threading.RLock())
        job: dict[str, Any] = {
            "requestId": request_id,
            "createdAt": time.time(),
            "updatedAt": time.time(),
            "events": [],
            "done": False,
            "condition": condition,
        }
        worker = threading.Thread(
            target=_run_job,
            args=(job, dict(payload), is_cancelled),
            name=f"swrlz-r39-job-{request_id[-16:]}",
            daemon=True,
        )
        job["thread"] = worker
        _JOBS[request_id] = job
        worker.start()
        return job


def _job_snapshot() -> list[dict[str, Any]]:
    _cleanup_jobs()
    now = time.time()
    with _JOB_LOCK:
        return [
            {
                "requestId": rid,
                "done": bool(job.get("done")),
                "eventCount": len(job.get("events", [])),
                "ageSeconds": round(now - float(job.get("createdAt", now)), 2),
                "updatedAgoSeconds": round(now - float(job.get("updatedAt", now)), 2),
            }
            for rid, job in _JOBS.items()
        ]


def inspect_engine():
    state = base.inspect_engine()
    if isinstance(state, dict):
        jobs = _job_snapshot()
        state = {
            **state,
            "hotRevision": HOT_REVISION,
            "tuningBoundary": "runtime_hot/dev",
            "detachedGeneration": True,
            "replayableJobs": jobs,
            "activeDetachedJobs": sum(1 for job in jobs if not job["done"]),
        }
    return state


def generate_events(payload, is_cancelled=None):
    job = _job_for(payload, is_cancelled)
    if job is None:
        yield from base.generate_events(payload, is_cancelled)
        return

    # Every attachment replays the retained event log from the beginning and then tails
    # new events. The browser de-duplicates by bridge sequence, allowing a resumed POST
    # with the same requestId to reconstruct missed state without restarting the model
    # while this worker still owns the job.
    index = 0
    condition: threading.Condition = job["condition"]
    while True:
        event = None
        with condition:
            while index >= len(job["events"]) and not job.get("done"):
                condition.wait(timeout=1.0)
            if index < len(job["events"]):
                event = dict(job["events"][index])
                index += 1
            elif job.get("done"):
                break
        if event is not None:
            yield event
