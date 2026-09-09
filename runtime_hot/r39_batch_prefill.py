"""Vectorized R39 prompt prefill with a persistent dense-weight fast path.

The direct-quantized matmat kernel remains the safe fallback. For block prefill, eligible
weights are decoded once per warm worker and retained as float32 matrices, allowing
NumPy/BLAS GEMM to reuse them across every subsequent prompt block/request instead of
re-decoding quantized rows on every call.
"""
from __future__ import annotations

import threading
import numpy as np

_DENSE_LOCK = threading.RLock()
_DENSE_CACHE: dict[tuple[int, str], np.ndarray] = {}
_DENSE_CACHE_BYTES = 0
_DENSE_CACHE_HITS = 0
_DENSE_CACHE_MISSES = 0
_DENSE_CACHE_BUDGET = 384 * 1024 * 1024
_DENSE_ITEM_MAX = 48 * 1024 * 1024
_DENSE_MATERIALIZE_MIN_BATCH = 32


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

    # model.matrix is the engine's canonical dequantizer, so this preserves exact tensor
    # interpretation while retaining the decoded matrix beyond the engine's smaller
    # generic tensor-cache budget.
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
    dense = _dense_matrix(model, name, int(value.shape[1]))
    if dense is not None:
        return np.asarray(dense @ value, dtype=np.float32)
    out = bridge.matmat(model, name, value)
    if out is None:
        raise RuntimeError(f"R39_BATCH_MATMAT_UNAVAILABLE:{name}")
    return np.asarray(out, dtype=np.float32)


def _rms_cols(x: np.ndarray, weight: np.ndarray) -> np.ndarray:
    a = np.asarray(x, dtype=np.float32)
    denom = np.sqrt(np.mean(a * a, axis=0, dtype=np.float32, keepdims=True) + np.float32(1e-5), dtype=np.float32)
    return (a / denom * np.asarray(weight, dtype=np.float32).reshape(-1, 1)).astype(np.float32)


def _head_rms_cols(x: np.ndarray, heads: int, weight: np.ndarray) -> np.ndarray:
    tokens = int(x.shape[1])
    a = np.asarray(x, dtype=np.float32).reshape(int(heads), 64, tokens)
    denom = np.sqrt(np.mean(a * a, axis=1, dtype=np.float32, keepdims=True) + np.float32(1e-5), dtype=np.float32)
    return (a / denom * np.asarray(weight, dtype=np.float32).reshape(1, 64, 1)).astype(np.float32).reshape(int(heads) * 64, tokens)


def _rope_cols(x: np.ndarray, heads: int, start_pos: int, theta: float = 1_000_000.0) -> np.ndarray:
    tokens = int(x.shape[1])
    y = np.asarray(x, dtype=np.float32).T.reshape(tokens, int(heads), 64).copy()
    half = 32
    inv = 1.0 / (float(theta) ** (np.arange(half, dtype=np.float64) * 2.0 / 64.0))
    positions = np.arange(int(start_pos), int(start_pos) + tokens, dtype=np.float64)
    angles = positions[:, None] * inv[None, :]
    c = np.cos(angles).astype(np.float32)[:, None, :]
    s = np.sin(angles).astype(np.float32)[:, None, :]
    a = y[:, :, :half].copy()
    b = y[:, :, half:].copy()
    y[:, :, :half] = a * c - b * s
    y[:, :, half:] = b * c + a * s
    return y.reshape(tokens, int(heads) * 64).T.copy()


def _causal_gqa(q: np.ndarray, k: np.ndarray, v: np.ndarray, old_entries: list[tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    tokens = int(q.shape[1])
    qh = q.T.reshape(tokens, 16, 64)
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
    out = np.empty((tokens, 16, 64), dtype=np.float32)
    for t in range(tokens):
        end = prefix + t + 1
        qg = qh[t].reshape(8, 2, 64)
        scores = np.einsum("hqd,lhd->hql", qg, keys[:end], optimize=True) / np.float32(8.0)
        weights = np.exp(scores - scores.max(axis=2, keepdims=True), dtype=np.float32)
        weights /= weights.sum(axis=2, keepdims=True, dtype=np.float32)
        out[t] = np.einsum("hql,lhd->hqd", weights, values[:end], optimize=True).astype(np.float32).reshape(16, 64)
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
        ff_input = (base._silu(gate) * up).astype(np.float32)
        ff = _matmat(bridge, model, f"blk.{i}.ffn_down.weight", ff_input)
        x = (residual + ff).astype(np.float32)

    hidden = _rms_cols(x, model.vector("token_embd_norm.weight"))
    state.pos = start_pos + count
    return hidden[:, -1].copy()
