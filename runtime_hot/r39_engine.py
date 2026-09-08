"""Hot-swappable R39 engine entrypoint.

v10 keeps native direct-quantized dispatch, adds recurrent-prefix reuse for follow-up
turns on a warm worker, and guards pathological single-token repetition.
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
HOT_REVISION = "2.1.19-hot-boundary-v10-prefix-cache-repeat-guard"

_ORIGINAL_MATRIX = base.R39Model.matrix
_ORIGINAL_RENDER_CHAT_PROMPT = base.render_chat_prompt

_MODEL_LOCK = threading.RLock()
_MODEL: base.R39Model | None = None
_MODEL_READY_AT = 0.0

_TENSOR_CACHE_LOCK = threading.RLock()
_CACHE_BUDGET_BYTES = 96 * 1024 * 1024
_CACHE_ITEM_MAX_BYTES = 12 * 1024 * 1024

_PREFIX_LOCK = threading.RLock()
_PREFIX_CACHE: list[dict[str, Any]] = []
_PREFIX_CACHE_MAX = 3
_PREFIX_CACHE_MAX_TOKENS = 4096

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
            raise base.R39InferenceError(
                str(load.get("code", "R39_LOAD_FAILED")),
                str(load.get("detail", "R39 reconstruction failed.")),
            )
        _MODEL = base.R39Model(base.RAW)
        _MODEL_READY_AT = time.time()
        return _MODEL


def _clone_state(state: base.RecurrentState) -> base.RecurrentState:
    clone = base.RecurrentState()
    clone.pos = int(state.pos)
    clone.conv = {i: value.copy() for i, value in state.conv.items()}
    clone.kv = {
        i: [(k.copy(), v.copy()) for k, v in entries]
        for i, entries in state.kv.items()
    }
    return clone


def _prefix_get(tokens: list[int]) -> tuple[int, base.RecurrentState | None, np.ndarray | None]:
    if not tokens:
        return 0, None, None
    best: dict[str, Any] | None = None
    with _PREFIX_LOCK:
        for entry in _PREFIX_CACHE:
            cached = entry["tokens"]
            n = len(cached)
            if n <= len(tokens) and tokens[:n] == cached:
                if best is None or n > len(best["tokens"]):
                    best = entry
        if best is None:
            return 0, None, None
        best["usedAt"] = time.time()
        return (
            len(best["tokens"]),
            _clone_state(best["state"]),
            best["logits"].copy() if best.get("logits") is not None else None,
        )


def _prefix_put(tokens: list[int], state: base.RecurrentState, logits: np.ndarray | None) -> None:
    if not tokens or len(tokens) > _PREFIX_CACHE_MAX_TOKENS or logits is None:
        return
    entry = {
        "tokens": list(tokens),
        "state": _clone_state(state),
        "logits": logits.copy(),
        "usedAt": time.time(),
    }
    with _PREFIX_LOCK:
        _PREFIX_CACHE[:] = [item for item in _PREFIX_CACHE if item["tokens"] != entry["tokens"]]
        _PREFIX_CACHE.append(entry)
        _PREFIX_CACHE.sort(key=lambda item: float(item.get("usedAt", 0)), reverse=True)
        del _PREFIX_CACHE[_PREFIX_CACHE_MAX:]


def _forward_hot(
    model: base.R39Model,
    token: int,
    state: base.RecurrentState,
    *,
    need_logits: bool,
) -> np.ndarray | None:
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
                scores = np.array(
                    [np.dot(qh, kk.reshape(8, 64)[kh]) / 8.0 for kk, _ in state.kv[i]],
                    np.float32,
                )
                weights = np.exp(scores - scores.max(), dtype=np.float32)
                weights /= weights.sum(dtype=np.float32)
                for weight, (_, vv) in zip(weights, state.kv[i]):
                    att[h] += weight * vv.reshape(8, 64)[kh]
            op = model.matvec(f"blk.{i}.attn_output.weight", att.reshape(-1))
        residual = (x + op).astype(np.float32)
        fn = base._rms(residual, model.vector(f"blk.{i}.ffn_norm.weight"))
        gate = model.matvec(f"blk.{i}.ffn_gate.weight", fn)
        up = model.matvec(f"blk.{i}.ffn_up.weight", fn)
        ff = model.matvec(
            f"blk.{i}.ffn_down.weight",
            (base._silu(gate) * up).astype(np.float32),
        )
        x = (residual + ff).astype(np.float32)
    x = base._rms(x, model.vector("token_embd_norm.weight"))
    state.pos += 1
    if not need_logits:
        return None
    return model.matvec("token_embd.weight", x)


def _sample_hot(
    logits: np.ndarray,
    recent: list[int],
    temperature: float,
    top_p: float,
    seed: int,
) -> int:
    adjusted = logits
    if len(recent) >= 3 and recent[-1] == recent[-2] == recent[-3]:
        adjusted = logits.copy()
        token = recent[-1]
        if 0 <= token < adjusted.size:
            adjusted[token] = -np.inf
    return base._sample(adjusted, recent[-128:], temperature, top_p, 64, 1.18, seed)


def _generate_hot_events(payload: dict[str, Any], is_cancelled=None):
    request_id = str(payload["requestId"])
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

        prefix_len, cached_state, cached_logits = _prefix_get(tokens)
        state = cached_state if cached_state is not None else base.RecurrentState()
        logits: np.ndarray | None = cached_logits
        total = len(tokens)
        remaining = total - prefix_len
        yield {
            "type": "STATUS",
            "phase": "PREFILL",
            "reason": f"Prefilling {total} token(s); prefix reuse {prefix_len} token(s), {remaining} token(s) remaining; intermediate vocabulary logits skipped; backend={('native-qmatvec' if native else 'python-fallback')}.",
        }

        prefill_started = time.monotonic()
        if remaining:
            for absolute_index in range(prefix_len, total):
                if is_cancelled and is_cancelled():
                    raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
                token_started = time.monotonic()
                ordinal = absolute_index + 1
                logits = _forward_hot(model, tokens[absolute_index], state, need_logits=(ordinal == total))
                token_s = time.monotonic() - token_started
                processed = absolute_index - prefix_len + 1
                elapsed = time.monotonic() - prefill_started
                avg = elapsed / processed
                eta = max(0.0, avg * (total - ordinal))
                yield {
                    "type": "STATUS",
                    "phase": "PREFILL",
                    "reason": f"Prefill {ordinal}/{total} · {token_s:.3f}s token · {avg:.3f}s new-token avg · ETA {eta:.1f}s · reused={prefix_len} · backend={('native' if native else 'python')}.",
                }
        if logits is None:
            raise base.R39InferenceError("R39_PREFIX_CACHE_LOGITS_MISSING", "Prompt prefix cache did not contain final logits.")
        _prefix_put(tokens, state, logits)

        decoder = base.IncrementalDecoder(model.tokenizer)
        recent: list[int] = []
        sequence_tokens = list(tokens)
        first_ms: int | None = None
        prefill_elapsed = time.monotonic() - prefill_started
        yield {
            "type": "STATUS",
            "phase": "GENERATING",
            "reason": f"R39 prefill complete in {prefill_elapsed:.2f}s; reused {prefix_len}/{total} prompt token(s); decoding with {('native direct-quantized matvec' if native else 'Python/Numpy fallback')}.",
        }
        for ordinal in range(1, max_tokens + 1):
            if is_cancelled and is_cancelled():
                raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            next_token = _sample_hot(logits, recent, temperature, top_p, hash(request_id) ^ (state.pos * 0x9E3779B9))
            if model.tokenizer.eos is not None and next_token == int(model.tokenizer.eos):
                break
            text = decoder.push(next_token)
            if first_ms is None:
                first_ms = int((time.monotonic() - started) * 1000)
            if text:
                yield {"type": "DELTA", "phase": "GENERATING", "text": text, "firstDeltaLatencyMs": first_ms}
            recent.append(next_token)
            sequence_tokens.append(next_token)
            decode_started = time.monotonic()
            logits = _forward_hot(model, next_token, state, need_logits=True)
            if logits is None:
                raise base.R39InferenceError("R39_GENERATION_LOGITS_MISSING", "Generation forward pass returned no logits.")
            if ordinal <= 4 or ordinal % 8 == 0:
                yield {"type": "STATUS", "phase": "DECODE_PROGRESS", "reason": f"Decode step {ordinal} · {time.monotonic() - decode_started:.3f}s · backend={('native' if native else 'python')}."}
        _prefix_put(sequence_tokens, state, logits)
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
        native = native_bridge.available()
        with _PREFIX_LOCK:
            prefix_entries = len(_PREFIX_CACHE)
            longest_prefix = max((len(item["tokens"]) for item in _PREFIX_CACHE), default=0)
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
            "prefillPrefixReuse": True,
            "prefixCacheEntries": prefix_entries,
            "longestCachedPrefixTokens": longest_prefix,
            "generationRepeatGuard": True,
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
