"""Hot-swappable R39 engine entrypoint.

v10 keeps the native-dispatch path and adds bounded per-thread recurrent-state reuse
so a continuing conversation prefills only context appended since its last request
when the previous tokenized prompt is an exact prefix. Cache miss, worker restart,
prefix mismatch, or safety bounds fall back to full prefill.
"""
from __future__ import annotations

import threading
import time
from typing import Any

import numpy as np

import swyrlz.r39_inference as base
import swyrlz.r39_tokenizer_patch  # noqa: F401
from swyrlz import r39_native as native_bridge

ENGINE_ID = "swrlz_r39_native_qmatvec_v1" if native_bridge.available() else base.ENGINE_ID
MODEL_SHA256 = base.MODEL_SHA256
HOT_SERVER_VERSION = "2.1.19"
HOT_REVISION = "2.1.19-hot-boundary-v10-thread-prefill-cache"

_ORIGINAL_MATRIX = base.R39Model.matrix
_ORIGINAL_MATVEC = base.R39Model.matvec
_ORIGINAL_RENDER_CHAT_PROMPT = base.render_chat_prompt

_MODEL_LOCK = threading.RLock()
_MODEL: base.R39Model | None = None
_MODEL_READY_AT = 0.0

_TENSOR_CACHE_LOCK = threading.RLock()
_CACHE_BUDGET_BYTES = 96 * 1024 * 1024
_CACHE_ITEM_MAX_BYTES = 12 * 1024 * 1024

_CONTEXT_LOCK = threading.RLock()
_CONTEXTS: dict[str, dict[str, Any]] = {}
_CONTEXT_TTL_SECONDS = 20 * 60
_CONTEXT_MAX_ENTRIES = 2
_CONTEXT_MAX_TOKENS = 2048

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


def _fallback_matvec(self: base.R39Model, name: str, x: np.ndarray) -> np.ndarray:
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


def _hot_matvec(self: base.R39Model, name: str, x: np.ndarray) -> np.ndarray:
    if native_bridge.available():
        out = native_bridge.matvec(self, name, x)
        if out is not None:
            return out
    return _fallback_matvec(self, name, x)


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


def _clone_state(state: base.RecurrentState) -> base.RecurrentState:
    clone = base.RecurrentState()
    clone.pos = int(state.pos)
    clone.conv = {i: value.copy() for i, value in state.conv.items()}
    clone.kv = {i: [(k.copy(), v.copy()) for k, v in values] for i, values in state.kv.items()}
    return clone


def _cleanup_contexts(now: float | None = None) -> None:
    now = time.time() if now is None else now
    with _CONTEXT_LOCK:
        expired = [key for key, value in _CONTEXTS.items() if now - float(value.get("updatedAt", now)) > _CONTEXT_TTL_SECONDS]
        for key in expired:
            _CONTEXTS.pop(key, None)
        if len(_CONTEXTS) > _CONTEXT_MAX_ENTRIES:
            ordered = sorted(_CONTEXTS.items(), key=lambda item: float(item[1].get("updatedAt", 0)))
            for key, _value in ordered[: max(0, len(_CONTEXTS) - _CONTEXT_MAX_ENTRIES)]:
                _CONTEXTS.pop(key, None)


def _resume_context(thread_id: str, tokens: list[int]) -> tuple[base.RecurrentState, int, np.ndarray | None, str]:
    if not thread_id:
        return base.RecurrentState(), 0, None, "no-thread-id"
    _cleanup_contexts()
    with _CONTEXT_LOCK:
        entry = _CONTEXTS.get(thread_id)
        if entry is None:
            return base.RecurrentState(), 0, None, "miss"
        cached_tokens = entry.get("tokens")
        cached_state = entry.get("state")
        cached_logits = entry.get("logits")
        if not isinstance(cached_tokens, tuple) or cached_state is None:
            _CONTEXTS.pop(thread_id, None)
            return base.RecurrentState(), 0, None, "invalid"
        prefix_len = len(cached_tokens)
        if prefix_len > len(tokens) or tuple(tokens[:prefix_len]) != cached_tokens:
            _CONTEXTS.pop(thread_id, None)
            return base.RecurrentState(), 0, None, "prefix-mismatch"
        entry["updatedAt"] = time.time()
        logits = cached_logits.copy() if isinstance(cached_logits, np.ndarray) else None
        return _clone_state(cached_state), prefix_len, logits, "hit"


def _store_context(thread_id: str, tokens: list[int], state: base.RecurrentState, logits: np.ndarray) -> bool:
    if not thread_id or len(tokens) > _CONTEXT_MAX_TOKENS:
        return False
    with _CONTEXT_LOCK:
        _CONTEXTS[thread_id] = {
            "tokens": tuple(tokens),
            "state": state,
            "logits": logits.copy(),
            "updatedAt": time.time(),
        }
    _cleanup_contexts()
    return True


def _context_snapshot() -> list[dict[str, Any]]:
    _cleanup_contexts()
    now = time.time()
    with _CONTEXT_LOCK:
        return [
            {
                "threadId": key,
                "tokenCount": len(value.get("tokens") or ()),
                "ageSeconds": round(now - float(value.get("updatedAt", now)), 2),
            }
            for key, value in _CONTEXTS.items()
        ]


def _forward_hot(model: base.R39Model, token: int, state: base.RecurrentState, *, need_logits: bool) -> np.ndarray | None:
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
    thread_id = str(payload.get("threadId") or "").strip()[:128]
    started = time.monotonic()
    engine_entered_ms = int(time.time() * 1000)
    try:
        client_sent_ms = int(payload.get("clientSentAtMs") or 0)
    except Exception:
        client_sent_ms = 0
    approx_client_to_hot_ms = max(0, engine_entered_ms - client_sent_ms) if client_sent_ms > 0 else None
    try:
        already_warm = _MODEL is not None
        native = native_bridge.available()
        mode = "compiled direct-quantized kernels" if native else "Python/Numpy fallback (native extension not present on this worker)"
        warm_note = "Reusing warm server R39 model." if already_warm else "Opening R39 once for this server worker; subsequent requests reuse the warm model."
        diag = f"Hot engine entered · server {HOT_SERVER_VERSION} · revision {HOT_REVISION} · {mode} · serverEpochMs {engine_entered_ms}"
        if approx_client_to_hot_ms is not None:
            diag += f" · approx client→hot {approx_client_to_hot_ms}ms"
        yield {"type": "STATUS", "phase": "HOT_ENGINE_ENTERED", "reason": f"{diag}. {warm_note}"}
        model = _get_model()
        yield {
            "type": "ROUTE",
            "phase": "ROUTE_RESOLVED",
            "reason": f"Hot loader resolved server {HOT_SERVER_VERSION} / {HOT_REVISION}; inference backend: {mode}.",
            "identity": {"route": "LOCAL_R39", "engineId": "swrlz_r39_native_qmatvec_v1" if native else base.ENGINE_ID, "modelId": str(model.manifest.get("modelId", "R39")), "modelSha256": MODEL_SHA256},
        }

        prompt = base.render_chat_prompt(payload)
        tokens = model.tokenizer.encode(prompt)
        if not tokens:
            raise base.R39InferenceError("R39_PROMPT_TOKENIZATION_EMPTY", "Prompt tokenization produced no tokens.")
        generation = payload.get("generation") if isinstance(payload.get("generation"), dict) else {}
        max_tokens = min(512, max(1, int(generation.get("maxTokens", 128))))
        temperature = min(2.0, max(0.0, float(generation.get("temperature", 0.1))))
        top_p = min(1.0, max(0.01, float(generation.get("topP", 0.9))))

        state, reused, cached_logits, cache_reason = _resume_context(thread_id, tokens)
        pending = tokens[reused:]
        if reused:
            yield {"type": "STATUS", "phase": "PREFILL", "reason": f"Conversation prefill cache hit: reused {reused} token(s); {len(pending)} new token(s) require prefill."}
        elif cache_reason == "prefix-mismatch":
            yield {"type": "STATUS", "phase": "PREFILL", "reason": f"Conversation context changed before the cached boundary; safely rebuilding all {len(tokens)} token(s)."}
        else:
            yield {"type": "STATUS", "phase": "PREFILL", "reason": f"Prefilling {len(tokens)} token(s); intermediate vocabulary logits skipped; backend={('native-qmatvec' if native else 'python-fallback')}."}

        logits: np.ndarray | None = cached_logits if not pending else None
        prefill_started = time.monotonic()
        total_new = len(pending)
        for ordinal, token in enumerate(pending, start=1):
            if is_cancelled and is_cancelled():
                raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            token_started = time.monotonic()
            logits = _forward_hot(model, token, state, need_logits=(ordinal == total_new))
            token_s = time.monotonic() - token_started
            elapsed = time.monotonic() - prefill_started
            avg = elapsed / ordinal
            eta = max(0.0, avg * (total_new - ordinal))
            yield {"type": "STATUS", "phase": "PREFILL", "reason": f"Prefill new {ordinal}/{total_new} · cached {reused} · {token_s:.3f}s token · {avg:.3f}s avg · ETA {eta:.1f}s · backend={('native' if native else 'python')}."}
        if logits is None:
            raise base.R39InferenceError("R39_CONTEXT_CACHE_LOGITS_MISSING", "Conversation context cache did not provide terminal prefill logits.")

        cached = _store_context(thread_id, tokens, state, logits)
        if cached:
            generation_state = _clone_state(state)
        else:
            generation_state = state
        state = generation_state

        decoder = base.IncrementalDecoder(model.tokenizer)
        recent: list[int] = []
        first_ms: int | None = None
        prefill_time = time.monotonic() - prefill_started
        cache_note = f"reused {reused}, prefetched {total_new}" if reused else f"prefetched {total_new}"
        if not cached and len(tokens) > _CONTEXT_MAX_TOKENS:
            cache_note += f"; cache skipped above {_CONTEXT_MAX_TOKENS}-token safety bound"
        yield {"type": "STATUS", "phase": "GENERATING", "reason": f"R39 prefill complete in {prefill_time:.2f}s ({cache_note}); decoding with {('native direct-quantized matvec' if native else 'Python/Numpy fallback')}."}
        for ordinal in range(1, max_tokens + 1):
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
            decode_started = time.monotonic()
            logits = _forward_hot(model, next_token, state, need_logits=True)
            assert logits is not None
            if ordinal <= 4 or ordinal % 8 == 0:
                yield {"type": "STATUS", "phase": "DECODE_PROGRESS", "reason": f"Decode step {ordinal} · {time.monotonic() - decode_started:.3f}s · backend={('native' if native else 'python')}."}
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
        contexts = _context_snapshot()
        native = native_bridge.available()
        return {
            "ok": True,
            "oneTokenReady": True,
            "interactiveReady": True,
            "engineId": "swrlz_r39_native_qmatvec_v1" if native else base.ENGINE_ID,
            "modelId": model.manifest.get("modelId", "R39"),
            "modelSha256": MODEL_SHA256,
            "tocCount": model.header["tocCount"],
            "tensorCount": len(model.desc),
            "tokenCount": len(model.tokenizer.tokens),
            "graphNodeCount": len(model.graph.get("nodes", [])),
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "nativeBackendAvailable": native,
            "nativeDirectQuantizedMatvec": native,
            "pythonReferenceFallback": True,
            "warmModelResident": True,
            "warmModelAgeSeconds": round(max(0.0, time.time() - _MODEL_READY_AT), 2),
            "decodedCacheBytes": int(getattr(model, "_hot_tensor_cache_bytes", 0)),
            "decodedCacheBudgetBytes": _CACHE_BUDGET_BYTES,
            "prefillSkipsIntermediateLogits": True,
            "incrementalConversationPrefill": True,
            "conversationContextCacheMaxTokens": _CONTEXT_MAX_TOKENS,
            "conversationContextCacheTtlSeconds": _CONTEXT_TTL_SECONDS,
            "conversationContextCaches": contexts,
            "connectionDiagnostics": True,
            "detachedGeneration": True,
            "replayableJobs": jobs,
            "activeDetachedJobs": sum(1 for job in jobs if not job["done"]),
        }
    except base.R39InferenceError as exc:
        return {"ok": False, "oneTokenReady": False, "interactiveReady": False, "code": exc.code, "detail": exc.detail, "hotServerVersion": HOT_SERVER_VERSION, "hotRevision": HOT_REVISION}
    except Exception as exc:
        return {"ok": False, "oneTokenReady": False, "interactiveReady": False, "code": "R39_HOT_ENGINE_PROBE_FAILED", "detail": f"{type(exc).__name__}: {exc}", "hotServerVersion": HOT_SERVER_VERSION, "hotRevision": HOT_REVISION}


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
