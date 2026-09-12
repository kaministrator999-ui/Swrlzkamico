"""Batched/vectorized R39 prefill adapter for the runtime-hot engine.

The adapter preserves the proven v17 generation loop and replaces only its token
forward primitive. During PREFILL it buffers tokens into checkpoint-aligned blocks,
executes the block through vectorized matmat/RMSNorm/RoPE/causal-GQA/FFN operations,
and commits the trial recurrent state only after a successful block. Decode remains
single-token so inter-token latency is not traded for prefill throughput.

Native direct-quantized matmat is preferred. A bounded dense float32 cache is only a
fallback when the native batch extension is unavailable. Any batch-path failure falls
back to the original serial forward path from an untouched recurrent state.
"""
from __future__ import annotations

import re
import threading
import time
from typing import Any

import numpy as np

_DENSE_LOCK = threading.RLock()
_DENSE_CACHE: dict[tuple[int, str], np.ndarray] = {}
_DENSE_CACHE_BYTES = 0
_DENSE_CACHE_HITS = 0
_DENSE_CACHE_MISSES = 0
_DENSE_CACHE_BUDGET = 128 * 1024 * 1024
_DENSE_ITEM_MAX = 32 * 1024 * 1024
_DENSE_MATERIALIZE_MIN_BATCH = 32
_DEFAULT_BLOCK_TOKENS = 96
_TLS = threading.local()


def cache_stats() -> dict[str, int]:
    with _DENSE_LOCK:
        return {
            "items": len(_DENSE_CACHE),
            "bytes": int(_DENSE_CACHE_BYTES),
            "budgetBytes": int(_DENSE_CACHE_BUDGET),
            "hits": int(_DENSE_CACHE_HITS),
            "misses": int(_DENSE_CACHE_MISSES),
        }


def _dense_matrix(model, name: str, batch: int) -> np.ndarray | None:
    global _DENSE_CACHE_BYTES, _DENSE_CACHE_HITS, _DENSE_CACHE_MISSES
    key = (id(model), str(name))
    with _DENSE_LOCK:
        hit = _DENSE_CACHE.get(key)
        if hit is not None:
            _DENSE_CACHE_HITS += 1
            return hit
        _DENSE_CACHE_MISSES += 1
    d = model.desc[name]
    shape = d["shape"]
    cols = int(shape[0])
    rows = int(shape[1]) if len(shape) > 1 else 1
    decoded_bytes = rows * cols * 4
    if batch < _DENSE_MATERIALIZE_MIN_BATCH or decoded_bytes > _DENSE_ITEM_MAX:
        return None
    with _DENSE_LOCK:
        if _DENSE_CACHE_BYTES + decoded_bytes > _DENSE_CACHE_BUDGET:
            return None
    value = np.ascontiguousarray(model.matrix(name), dtype=np.float32)
    if value.ndim != 2 or value.shape != (rows, cols):
        return None
    with _DENSE_LOCK:
        existing = _DENSE_CACHE.get(key)
        if existing is not None:
            return existing
        if _DENSE_CACHE_BYTES + int(value.nbytes) > _DENSE_CACHE_BUDGET:
            return None
        _DENSE_CACHE[key] = value
        _DENSE_CACHE_BYTES += int(value.nbytes)
        return value


def _matmat(bridge, model, name: str, x: np.ndarray) -> np.ndarray:
    value = np.ascontiguousarray(x, dtype=np.float32)
    # Prefer the bounded-memory direct-quantized batch kernel when the worker has it.
    if callable(getattr(bridge, "matmat_available", None)) and bridge.matmat_available():
        out = bridge.matmat(model, name, value)
        if out is not None:
            return np.asarray(out, dtype=np.float32)
    dense = _dense_matrix(model, name, int(value.shape[1]))
    if dense is not None:
        return np.asarray(dense @ value, dtype=np.float32)
    raise RuntimeError(f"R39_BATCH_MATMAT_UNAVAILABLE:{name}")


def _rms_cols(x, weight):
    a = np.asarray(x, dtype=np.float32)
    denom = np.sqrt(np.mean(a * a, axis=0, dtype=np.float32, keepdims=True) + np.float32(1e-5), dtype=np.float32)
    return (a / denom * np.asarray(weight, dtype=np.float32).reshape(-1, 1)).astype(np.float32)


def _head_rms_cols(x, heads, weight):
    tokens = int(x.shape[1])
    a = np.asarray(x, dtype=np.float32).reshape(int(heads), 64, tokens)
    denom = np.sqrt(np.mean(a * a, axis=1, dtype=np.float32, keepdims=True) + np.float32(1e-5), dtype=np.float32)
    return (a / denom * np.asarray(weight, dtype=np.float32).reshape(1, 64, 1)).astype(np.float32).reshape(int(heads) * 64, tokens)


def _rope_cols(x, heads, start_pos, theta=1_000_000.0):
    tokens = int(x.shape[1])
    y = np.asarray(x, dtype=np.float32).T.reshape(tokens, int(heads), 64).copy()
    half = 32
    inv = 1.0 / (float(theta) ** (np.arange(half, dtype=np.float64) * 2.0 / 64.0))
    angles = np.arange(int(start_pos), int(start_pos) + tokens, dtype=np.float64)[:, None] * inv[None, :]
    c = np.cos(angles).astype(np.float32)[:, None, :]
    s = np.sin(angles).astype(np.float32)[:, None, :]
    a = y[:, :, :half].copy()
    b = y[:, :, half:].copy()
    y[:, :, :half] = a * c - b * s
    y[:, :, half:] = b * c + a * s
    return y.reshape(tokens, int(heads) * 64).T.copy()


def _causal_gqa(q, k, v, old_entries):
    tokens = int(q.shape[1])
    qg = q.T.reshape(tokens, 8, 2, 64)
    kh_new = k.T.reshape(tokens, 8, 64)
    vh_new = v.T.reshape(tokens, 8, 64)
    if old_entries:
        kh_old = np.stack([item[0] for item in old_entries], axis=0).astype(np.float32, copy=False).reshape(len(old_entries), 8, 64)
        vh_old = np.stack([item[1] for item in old_entries], axis=0).astype(np.float32, copy=False).reshape(len(old_entries), 8, 64)
        keys = np.concatenate((kh_old, kh_new), axis=0)
        values = np.concatenate((vh_old, vh_new), axis=0)
        prefix = len(old_entries)
    else:
        keys = kh_new
        values = vh_new
        prefix = 0
    scores = np.einsum("thqd,lhd->thql", qg, keys, optimize=True).astype(np.float32) / np.float32(8.0)
    key_pos = np.arange(prefix + tokens, dtype=np.int32)[None, :]
    limits = (prefix + np.arange(tokens, dtype=np.int32))[:, None]
    causal = (key_pos <= limits)[:, None, None, :]
    scores = np.where(causal, scores, np.float32(-np.inf))
    peak = np.max(scores, axis=3, keepdims=True)
    weights = np.exp(scores - peak, dtype=np.float32)
    weights /= np.sum(weights, axis=3, keepdims=True, dtype=np.float32)
    out = np.einsum("thql,lhd->thqd", weights, values, optimize=True).astype(np.float32)
    return out.reshape(tokens, 1024).T.copy()


def forward_token_block(base, bridge, model, state, tokens: list[int]) -> np.ndarray:
    if not tokens:
        raise ValueError("tokens must be non-empty")
    start_pos = int(state.pos)
    count = len(tokens)
    x = np.stack([model.row("token_embd.weight", int(token)).astype(np.float32) for token in tokens], axis=1)
    for i, kvh in enumerate(base.LAYER_KV):
        n = _rms_cols(x, model.vector(f"blk.{i}.attn_norm.weight"))
        if kvh == 0:
            projected = _matmat(bridge, model, f"blk.{i}.shortconv.in_proj.weight", n)
            b, c, z = np.split(projected, 3, axis=0)
            bx = (b * z).astype(np.float32)
            cw = np.asarray(model.matrix(f"blk.{i}.shortconv.conv.weight"), dtype=np.float32)
            hist = np.asarray(state.conv[i], dtype=np.float32)
            seq = np.concatenate((hist, bx.T), axis=0)
            cv = (seq[0:count].T * cw[:, 0:1] + seq[1:count + 1].T * cw[:, 1:2] + seq[2:count + 2].T * cw[:, 2:3]).astype(np.float32)
            state.conv[i][0] = seq[-2].copy()
            state.conv[i][1] = seq[-1].copy()
            op = _matmat(bridge, model, f"blk.{i}.shortconv.out_proj.weight", (c * cv).astype(np.float32))
        else:
            q = _matmat(bridge, model, f"blk.{i}.attn_q.weight", n)
            k = _matmat(bridge, model, f"blk.{i}.attn_k.weight", n)
            v = _matmat(bridge, model, f"blk.{i}.attn_v.weight", n)
            q = _head_rms_cols(q, 16, model.vector(f"blk.{i}.attn_q_norm.weight"))
            k = _head_rms_cols(k, 8, model.vector(f"blk.{i}.attn_k_norm.weight"))
            q = _rope_cols(q, 16, start_pos)
            k = _rope_cols(k, 8, start_pos)
            old_entries = list(state.kv[i])
            att = _causal_gqa(q, k, v, old_entries)
            state.kv[i].extend((k[:, t].copy(), v[:, t].copy()) for t in range(count))
            op = _matmat(bridge, model, f"blk.{i}.attn_output.weight", att)
        residual = (x + op).astype(np.float32)
        fn = _rms_cols(residual, model.vector(f"blk.{i}.ffn_norm.weight"))
        gate = _matmat(bridge, model, f"blk.{i}.ffn_gate.weight", fn)
        up = _matmat(bridge, model, f"blk.{i}.ffn_up.weight", fn)
        ff = _matmat(bridge, model, f"blk.{i}.ffn_down.weight", (base._silu(gate) * up).astype(np.float32))
        x = (residual + ff).astype(np.float32)
    hidden = _rms_cols(x, model.vector("token_embd_norm.weight"))
    state.pos = start_pos + count
    return hidden[:, -1].copy()


def _metric() -> dict[str, Any] | None:
    value = getattr(_TLS, "metrics", None)
    return value if isinstance(value, dict) else None


def install(impl, block_tokens: int = _DEFAULT_BLOCK_TOKENS) -> dict[str, Any]:
    """Install checkpoint-aligned batch prefill without replacing v17 generation."""
    block_tokens = max(32, int(block_tokens))
    original_forward = impl._forward_hot
    original_generate_hot_events = impl._generate_hot_events

    def patched_forward(model, token, state, *, need_logits: bool):
        pending = getattr(state, "_swrlz_batch_prefill_tokens", None)
        if pending is None:
            pending = []
            setattr(state, "_swrlz_batch_prefill_tokens", pending)
        metrics = _metric()
        phase = str((metrics or {}).get("phase") or "")

        # Decode stays single-token. This preserves ITL and avoids batching a lone token.
        if need_logits and not pending and phase == "GENERATING":
            started = time.monotonic()
            result = original_forward(model, token, state, need_logits=True)
            if metrics is not None:
                metrics["decodeTokens"] += 1
                metrics["decodeComputeSeconds"] += time.monotonic() - started
            return result

        pending.append(int(token))
        if not need_logits and len(pending) < block_tokens:
            return None

        block = list(pending)
        pending.clear()
        # Run against a shadow state. A failed vectorized block can therefore fall
        # back to serial execution without repairing a half-mutated recurrent state.
        trial = impl._clone_state(state)
        batch_started = time.monotonic()
        try:
            hidden = forward_token_block(impl.base, impl.native_bridge, model, trial, block)
            logits = model.matvec("token_embd.weight", hidden) if need_logits else None
            state.conv = trial.conv
            state.kv = trial.kv
            state.pos = trial.pos
            if metrics is not None and phase == "PREFILL":
                metrics["batchBlocks"] += 1
                metrics["batchPrefillTokens"] += len(block)
                metrics["batchComputeSeconds"] += time.monotonic() - batch_started
            return logits
        except Exception as exc:
            if metrics is not None and phase == "PREFILL":
                metrics["batchFallbacks"] += 1
                metrics["lastBatchFallback"] = f"{type(exc).__name__}:{exc}"[:240]
            logits = None
            serial_started = time.monotonic()
            for index, buffered_token in enumerate(block):
                logits = original_forward(
                    model,
                    buffered_token,
                    state,
                    need_logits=bool(need_logits and index == len(block) - 1),
                )
            if metrics is not None and phase == "PREFILL":
                metrics["serialPrefillTokens"] += len(block)
                metrics["serialPrefillSeconds"] += time.monotonic() - serial_started
            return logits

    def instrumented_generate_hot_events(payload, is_cancelled=None):
        metrics = {
            "phase": "START",
            "started": time.monotonic(),
            "prefillStarted": None,
            "prefillFinished": None,
            "newPrefillTokens": 0,
            "cachedTokens": 0,
            "batchBlocks": 0,
            "batchPrefillTokens": 0,
            "batchComputeSeconds": 0.0,
            "serialPrefillTokens": 0,
            "serialPrefillSeconds": 0.0,
            "batchFallbacks": 0,
            "lastBatchFallback": "",
            "decodeTokens": 0,
            "decodeComputeSeconds": 0.0,
            "firstDeltaLatencyMs": None,
        }
        _TLS.metrics = metrics
        try:
            for event in original_generate_hot_events(payload, is_cancelled):
                phase = str(event.get("phase") or "")
                reason = str(event.get("reason") or "")
                if phase == "PREFILL":
                    if metrics["prefillStarted"] is None:
                        metrics["prefillStarted"] = time.monotonic()
                    metrics["phase"] = "PREFILL"
                    hit = re.search(r"reused (\d+) token\(s\); only (\d+) new", reason)
                    if hit:
                        metrics["cachedTokens"] = max(metrics["cachedTokens"], int(hit.group(1)))
                        metrics["newPrefillTokens"] = max(metrics["newPrefillTokens"], int(hit.group(2)))
                    full = re.search(r"Prefilling (\d+) token\(s\)", reason)
                    if full:
                        metrics["newPrefillTokens"] = max(metrics["newPrefillTokens"], int(full.group(1)))
                    progress = re.search(r"Prefill new \d+/(\d+) · cached (\d+)", reason)
                    if progress:
                        metrics["newPrefillTokens"] = max(metrics["newPrefillTokens"], int(progress.group(1)))
                        metrics["cachedTokens"] = max(metrics["cachedTokens"], int(progress.group(2)))
                elif phase == "GENERATING":
                    if metrics["prefillFinished"] is None:
                        metrics["prefillFinished"] = time.monotonic()
                    metrics["phase"] = "GENERATING"
                if event.get("type") == "DELTA" and metrics["firstDeltaLatencyMs"] is None:
                    value = event.get("firstDeltaLatencyMs")
                    if value is not None:
                        metrics["firstDeltaLatencyMs"] = int(value)
                if event.get("type") == "COMPLETED":
                    now = time.monotonic()
                    prefill_start = metrics["prefillStarted"] or metrics["started"]
                    prefill_finish = metrics["prefillFinished"] or now
                    prefill_seconds = max(0.0, prefill_finish - prefill_start)
                    new_tokens = int(metrics["newPrefillTokens"] or (metrics["batchPrefillTokens"] + metrics["serialPrefillTokens"]))
                    prefill_tps = (new_tokens / prefill_seconds) if new_tokens and prefill_seconds > 0 else 0.0
                    decode_seconds = float(metrics["decodeComputeSeconds"])
                    decode_tokens = int(metrics["decodeTokens"])
                    decode_tps = (decode_tokens / decode_seconds) if decode_tokens and decode_seconds > 0 else 0.0
                    yield {
                        "type": "STATUS",
                        "phase": "PERF_METRICS",
                        "reason": (
                            f"TTFT={metrics['firstDeltaLatencyMs']}ms; cached={metrics['cachedTokens']}; "
                            f"uncached={new_tokens}; prefill={prefill_seconds:.3f}s/{prefill_tps:.2f} tok/s; "
                            f"batch={metrics['batchPrefillTokens']} tok/{metrics['batchBlocks']} blocks; "
                            f"serial-prefill={metrics['serialPrefillTokens']} tok; fallbacks={metrics['batchFallbacks']}; "
                            f"decode-compute={decode_tokens} tok/{decode_seconds:.3f}s/{decode_tps:.2f} tok/s."
                        ),
                    }
                yield event
        finally:
            try:
                delattr(_TLS, "metrics")
            except Exception:
                pass

    impl._forward_hot = patched_forward
    impl._generate_hot_events = instrumented_generate_hot_events
    return {
        "installed": True,
        "blockTokens": block_tokens,
        "nativeBatchAvailable": bool(callable(getattr(impl.native_bridge, "matmat_available", None)) and impl.native_bridge.matmat_available()),
        "safeSerialFallback": True,
        "decodeRemainsSingleToken": True,
        "telemetry": ["TTFT", "cachedTokens", "uncachedPrefillTokensPerSecond", "batchBlocks", "decodeComputeTokensPerSecond"],
    }


def diagnostics(impl) -> dict[str, Any]:
    return {
        "batchPrefillAdapter": True,
        "nativeBatchAvailable": bool(callable(getattr(impl.native_bridge, "matmat_available", None)) and impl.native_bridge.matmat_available()),
        "denseFallbackCache": cache_stats(),
        "defaultBlockTokens": _DEFAULT_BLOCK_TOKENS,
        "safeSerialFallback": True,
    }
