"""Hot-swappable R39 engine entrypoint.

Performance/tuning boundary for LOCAL_R39. Stable routing/auth/contracts remain bundled;
this dev asset is loaded by /api/hot/sync without a Vercel redeploy.

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
HOT_REVISION = "2.1.16-hot-boundary-v4-warm-prefill"

_ORIGINAL_MATRIX = base.R39Model.matrix
_ORIGINAL_RENDER_CHAT_PROMPT = base.render_chat_prompt

# Per-worker warm model. The mmap/tokenizer/tensor directory stays open for the life of
# this Vercel worker instead of being reconstructed for every request.
_MODEL_LOCK = threading.RLock()
_MODEL: base.R39Model | None = None
_MODEL_READY_AT = 0.0

# Bounded decoded-weight cache. Keep only matrices small enough to be useful without
# materializing the whole model. Large matrices continue through bounded dequant batches.
_TENSOR_CACHE_LOCK = threading.RLock()
_CACHE_BUDGET_BYTES = 96 * 1024 * 1024
_CACHE_ITEM_MAX_BYTES = 12 * 1024 * 1024

# Detached generation registry for reconnect/replay while this worker remains alive.
_JOB_LOCK = threading.RLock()
_JOBS: dict[str, dict[str, Any]] = {}
_JOB_TTL_SECONDS = 15 * 60
_MAX_JOBS = 12


def _cache(self: base.R39Model) -> dict[str, np.ndarray]:
    cache = getattr(self, "_hot_tensor_cache", None)
    if cache is None:
        cache = {}
        self._hot_tensor_cache = cache
        self._hot_tensor_cache_bytes = 0
    return cache


def _hot_matrix(self: base.R39Model, name: str) -> np.ndarray:
    d = self.desc[name]
    elements = 1
    for dim in d["shape"]:
        elements *= int(dim)
    decoded_bytes = elements * 4
    if decoded_bytes <= _CACHE_ITEM_MAX_BYTES:
        with _TENSOR_CACHE_LOCK:
            cache = _cache(self)
            hit = cache.get(name)
            if hit is not None:
                return hit
            used = int(getattr(self, "_hot_tensor_cache_bytes", 0))
            if used + decoded_bytes <= _CACHE_BUDGET_BYTES:
                value = _ORIGINAL_MATRIX(self, name)
                cache[name] = value
                self._hot_tensor_cache_bytes = used + int(value.nbytes)
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

    decoded_bytes = cols * rows * 4
    if decoded_bytes <= _CACHE_ITEM_MAX_BYTES:
        matrix = _hot_matrix(self, name)
        if matrix.ndim == 2:
            return (matrix @ x).astype(np.float32, copy=False)

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


def _get_model() -> base.R39Model:
    global _MODEL, _MODEL_READY_AT
    if _MODEL is not None:
        return _MODEL
    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL
        load = base.ensure_r39()
        if not load.get("modelReady"):
            raise base.R39InferenceError(str(load.get("code", "R39_LOAD_FAILED")), str(load.get("detail", "R39 reconstruction failed.")))
        _MODEL = base.R39Model(base.RAW)
        _MODEL_READY_AT = time.time()
        return _MODEL


def _forward_hot(model: base.R39Model, token: int, state: base.RecurrentState, *, need_logits: bool) -> np.ndarray | None:
    """Reference-equivalent recurrent step with optional vocabulary projection.

    During prompt prefill, only the final token needs logits for sampling. The bundled
    reference projected 1024 hidden units through the full vocabulary after every prompt
    token, then discarded all but the last projection. Skipping those discarded logits is
    the largest safe prefill optimization available inside the hot boundary.
    """
    x = model.row("token_embd.weight", token).astype(np.float32)
    for i, kvh in enumerate(base.LAYER_KV):
        n = base._rms(x, model.vector(f"blk.{i}.attn_norm.weight"))
        if kvh == 0:
            projected = model.matvec(f"blk.{i}.shortconv.in_proj.weight", n)
            b, c, z = np.split(projected, 3)
            bx = (b * z).astype(np.float32)
            cw = model.matrix(f"blk.{i}.shortconv.conv.weight")
            hist = state.conv[i]
            cv = (hist[0] * cw[:, 0] + hist[1] * cw[:, 1] + bx * cw[:, 2]).astype(np.float32)
            state.conv[i][0] = hist[1].copy()
            state.conv[i][1] = bx
            op = model.matvec(f"blk.{i}.shortconv.out_proj.weight", (c * cv).astype(np.float32))
        else:
            q = model.matvec(f"blk.{i}.attn_q.weight", n)
            k = model.matvec(f"blk.{i}.attn_k.weight", n)
            v = model.matvec(f"blk.{i}.attn_v.weight", n)
            qn = model.vector(f"blk.{i}.attn_q_norm.weight")
            kn = model.vector(f"blk.{i}.attn_k_norm.weight")
            q = np.concatenate([base._rms(q.reshape(16, 64)[h], qn) for h in range(16)]).astype(np.float32)
            k = np.concatenate([base._rms(k.reshape(8, 64)[h], kn) for h in range(8)]).astype(np.float32)
            q = base._rope(q, 16, 64, state.pos)
            k = base._rope(k, 8, 64, state.pos)
            state.kv[i].append((k.copy(), v.copy()))
            att = np.zeros((16, 64), np.float32)
            for h in range(16):
                kh = h // 2
                qh = q.reshape(16, 64)[h]
                scores = np.array([np.dot(qh, kk.reshape(8, 64)[kh]) / 8.0 for kk, _ in state.kv[i]], np.float32)
                weights = np.exp(scores - scores.max(), dtype=np.float32)
                weights /= weights.sum(dtype=np.float32)
                for weight, (_, vv) in zip(weights, state.kv[i]):
                    att[h] += weight * vv.reshape(8, 64)[kh]
            op = model.matvec(f"blk.{i}.attn_output.weight", att.reshape(-1))
        residual = (x + op).astype(np.float32)
        fn = base._rms(residual, model.vector(f"blk.{i}.ffn_norm.weight"))
        gate = model.matvec(f"blk.{i}.ffn_gate.weight", fn)
        up = model.matvec(f"blk.{i}.ffn_up.weight", fn)
        ff = model.matvec(f"blk.{i}.ffn_down.weight", (base._silu(gate) * up).astype(np.float32))
        x = (residual + ff).astype(np.float32)
    x = base._rms(x, model.vector("token_embd_norm.weight"))
    state.pos += 1
    if not need_logits:
        return None
    return model.matvec("token_embd.weight", x)


def _generate_hot_events(payload: dict[str, Any], is_cancelled=None):
    request_id = str(payload["requestId"])
    started = time.monotonic()
    try:
        already_warm = _MODEL is not None
        yield {
            "type": "STATUS",
            "phase": "MODEL_LOADING",
            "reason": "Reusing warm server R39 model." if already_warm else "Opening R39 once for this server worker; subsequent requests reuse the warm model.",
        }
        model = _get_model()
        yield {
            "type": "ROUTE",
            "phase": "ROUTE_RESOLVED",
            "reason": "Using hot local R39 Python reference inference with warm-model reuse.",
            "identity": {"route": "LOCAL_R39", "engineId": ENGINE_ID, "modelId": str(model.manifest.get("modelId", "R39")), "modelSha256": MODEL_SHA256},
        }

        prompt = base.render_chat_prompt(payload)
        tokens = model.tokenizer.encode(prompt)
        if not tokens:
            raise base.R39InferenceError("R39_PROMPT_TOKENIZATION_EMPTY", "Prompt tokenization produced no tokens.")
        generation = payload.get("generation") if isinstance(payload.get("generation"), dict) else {}
        max_tokens = min(512, max(1, int(generation.get("maxTokens", 128))))
        temperature = min(2.0, max(0.0, float(generation.get("temperature", 0.1))))
        top_p = min(1.0, max(0.01, float(generation.get("topP", 0.9))))
        state = base.RecurrentState()
        yield {"type": "STATUS", "phase": "PREFILL", "reason": f"Prefilling {len(tokens)} token(s); vocabulary projection is skipped for intermediate prompt tokens."}

        logits: np.ndarray | None = None
        prefill_started = time.monotonic()
        total = len(tokens)
        for ordinal, token in enumerate(tokens, start=1):
            if is_cancelled and is_cancelled():
                raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            token_started = time.monotonic()
            logits = _forward_hot(model, token, state, need_logits=(ordinal == total))
            elapsed = time.monotonic() - prefill_started
            avg = elapsed / ordinal
            eta = max(0.0, avg * (total - ordinal))
            yield {
                "type": "STATUS",
                "phase": "PREFILL",
                "reason": f"Prefill {ordinal}/{total} · {time.monotonic() - token_started:.2f}s token · {avg:.2f}s avg · ETA {eta:.1f}s.",
            }
        assert logits is not None

        decoder = base.IncrementalDecoder(model.tokenizer)
        recent: list[int] = []
        first_ms: int | None = None
        yield {"type": "STATUS", "phase": "GENERATING", "reason": f"R39 prefill complete in {time.monotonic() - prefill_started:.2f}s; decoding locally."}
        for _ in range(max_tokens):
            if is_cancelled and is_cancelled():
                raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            next_token = base._sample(logits, recent[-64:], temperature, top_p, 50, 1.05, hash(request_id) ^ (state.pos * 0x9E3779B9))
            if model.tokenizer.eos is not None and next_token == int(model.tokenizer.eos):
                break
            text = decoder.push(next_token)
            if first_ms is None:
                first_ms = int((time.monotonic() - started) * 1000)
            if text:
                yield {"type": "DELTA", "phase": "GENERATING", "text": text, "firstDeltaLatencyMs": first_ms}
            recent.append(next_token)
            logits = _forward_hot(model, next_token, state, need_logits=True)
            assert logits is not None
        tail = decoder.finish()
        if tail:
            yield {"type": "DELTA", "phase": "GENERATING", "text": tail, "firstDeltaLatencyMs": first_ms}
        yield {"type": "COMPLETED", "phase": "COMPLETE", "reason": "Local R39 generation completed.", "totalLatencyMs": int((time.monotonic() - started) * 1000)}
    except base.R39InferenceError as exc:
        event_type = "CANCELLED" if exc.code == "REQUEST_CANCELLED" else "FAILED"
        phase = "CANCELLED" if event_type == "CANCELLED" else "ERROR"
        yield {"type": event_type, "phase": phase, "reason": exc.detail, "categories": [exc.code], "totalLatencyMs": int((time.monotonic() - started) * 1000)}
    except Exception as exc:
        yield {"type": "FAILED", "phase": "ERROR", "reason": f"Hot local R39 inference failed ({type(exc).__name__}: {exc}).", "categories": ["R39_HOT_INFERENCE_RUNTIME_FAILED"], "totalLatencyMs": int((time.monotonic() - started) * 1000)}


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
        for event in _generate_hot_events(payload, is_cancelled):
            _append_job_event(job, event)
    except Exception as exc:
        _append_job_event(job, {"type": "FAILED", "phase": "ERROR", "reason": f"Detached R39 worker failed: {type(exc).__name__}: {exc}", "categories": ["R39_DETACHED_WORKER_FAILED"]})
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
        job: dict[str, Any] = {"requestId": request_id, "createdAt": time.time(), "updatedAt": time.time(), "events": [], "done": False, "condition": condition}
        worker = threading.Thread(target=_run_job, args=(job, dict(payload), is_cancelled), name=f"swrlz-r39-job-{request_id[-16:]}", daemon=True)
        job["thread"] = worker
        _JOBS[request_id] = job
        worker.start()
        return job


def _job_snapshot() -> list[dict[str, Any]]:
    _cleanup_jobs()
    now = time.time()
    with _JOB_LOCK:
        return [{"requestId": rid, "done": bool(job.get("done")), "eventCount": len(job.get("events", [])), "ageSeconds": round(now - float(job.get("createdAt", now)), 2), "updatedAgoSeconds": round(now - float(job.get("updatedAt", now)), 2)} for rid, job in _JOBS.items()]


def inspect_engine():
    try:
        model = _get_model()
        jobs = _job_snapshot()
        return {
            "ok": True,
            "oneTokenReady": True,
            "interactiveReady": True,
            "engineId": ENGINE_ID,
            "modelId": model.manifest.get("modelId", "R39"),
            "modelSha256": MODEL_SHA256,
            "tocCount": model.header["tocCount"],
            "tensorCount": len(model.desc),
            "tokenCount": len(model.tokenizer.tokens),
            "graphNodeCount": len(model.graph.get("nodes", [])),
            "hotRevision": HOT_REVISION,
            "tuningBoundary": "runtime_hot/dev",
            "warmModelResident": True,
            "warmModelAgeSeconds": round(max(0.0, time.time() - _MODEL_READY_AT), 2),
            "decodedCacheBytes": int(getattr(model, "_hot_tensor_cache_bytes", 0)),
            "decodedCacheBudgetBytes": _CACHE_BUDGET_BYTES,
            "prefillSkipsIntermediateLogits": True,
            "detachedGeneration": True,
            "replayableJobs": jobs,
            "activeDetachedJobs": sum(1 for job in jobs if not job["done"]),
        }
    except base.R39InferenceError as exc:
        return {"ok": False, "oneTokenReady": False, "interactiveReady": False, "code": exc.code, "detail": exc.detail, "hotRevision": HOT_REVISION}
    except Exception as exc:
        return {"ok": False, "oneTokenReady": False, "interactiveReady": False, "code": "R39_HOT_ENGINE_PROBE_FAILED", "detail": f"{type(exc).__name__}: {exc}", "hotRevision": HOT_REVISION}


def generate_events(payload, is_cancelled=None):
    job = _job_for(payload, is_cancelled)
    if job is None:
        yield from _generate_hot_events(payload, is_cancelled)
        return

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
