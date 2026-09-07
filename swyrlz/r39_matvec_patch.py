"""Performance patch for the R39 Python reference executor.

The canonical reference implementation remains the source of truth. This module
only replaces hot-path helpers at import time:

- larger bounded dequantization batches reduce repeated allocation/BLAS overhead;
- small decoded tensors (norm vectors / small matrices) are cached per model;
- the stock Vercel response directive is compacted before tokenization so local
  prefill does not spend scarce function lifetime on bridge instructions that are
  already enforced by the stream contract outside model prose.

The patch deliberately avoids whole-model dequantization so memory remains bounded.
"""
from __future__ import annotations

from typing import Any

import numpy as np

import swyrlz.r39_inference as _r39
from swyrlz.r39_inference import R39InferenceError, R39Model, _deq

TARGET_DEQUANT_BYTES = 16 * 1024 * 1024
SMALL_MATRIX_CACHE_BYTES = 4 * 1024 * 1024
_STOCK_BRIDGE_DIRECTIVE = (
    "Answer directly and truthfully. Stream only committed assistant response text as DELTA. "
    "Keep status, routing, and operational detail outside assistant prose."
)
_COMPACT_LOCAL_DIRECTIVE = "You are §wyrlz. Answer directly and truthfully."


def _cache(self: R39Model) -> dict[str, np.ndarray]:
    value = getattr(self, "_swrlz_decode_cache", None)
    if value is None:
        value = {}
        setattr(self, "_swrlz_decode_cache", value)
    return value


def _cached_matrix(self: R39Model, name: str) -> np.ndarray:
    d = self.desc[name]
    shape = d["shape"]
    elements = int(np.prod(shape, dtype=np.int64)) if shape else 0
    decoded_bytes = elements * 4
    cache = _cache(self)
    key = "m:" + name
    if decoded_bytes <= SMALL_MATRIX_CACHE_BYTES and key in cache:
        return cache[key]
    value = _deq(d["kind"], self._raw(name), shape)
    if decoded_bytes <= SMALL_MATRIX_CACHE_BYTES:
        cache[key] = value
    return value


def _cached_vector(self: R39Model, name: str) -> np.ndarray:
    cache = _cache(self)
    key = "v:" + name
    if key not in cache:
        cache[key] = _cached_matrix(self, name).reshape(-1)
    return cache[key]


def _bounded_matvec(self: R39Model, name: str, x: np.ndarray) -> np.ndarray:
    d = self.desc[name]
    shape = d["shape"]
    cols = int(shape[0])
    rows = int(shape[1]) if len(shape) > 1 else 1
    if x.size != cols:
        raise R39InferenceError("R39_MATVEC_SHAPE_MISMATCH", f"{name}: expected {cols}, got {x.size}")

    decoded_bytes = rows * cols * 4
    if decoded_bytes <= SMALL_MATRIX_CACHE_BYTES:
        return _cached_matrix(self, name) @ x

    rb = self._row_bytes(d["kind"], cols)
    raw = self._raw(name)
    # Keep transient float32 decode buffers bounded while amortizing dequantization
    # and BLAS-call overhead better than the former 4 MiB batches.
    batch_rows = max(1, min(rows, max(64, TARGET_DEQUANT_BYTES // max(4 * cols, 1))))
    out = np.empty(rows, dtype=np.float32)
    for start in range(0, rows, batch_rows):
        count = min(batch_rows, rows - start)
        block = raw[start * rb:(start + count) * rb]
        matrix = _deq(d["kind"], block, (cols, count))
        out[start:start + count] = matrix @ x
    return out


def _compact_render_chat_prompt(payload: dict[str, Any]) -> str:
    parts = ["<|startoftext|>"]
    directive = str(payload.get("responseDirective") or _COMPACT_LOCAL_DIRECTIVE).strip()
    if directive == _STOCK_BRIDGE_DIRECTIVE:
        directive = _COMPACT_LOCAL_DIRECTIVE
    if directive:
        parts.append(f"<|im_start|>system\n{directive}<|im_end|>\n")
    for turn in payload.get("history", []):
        if not isinstance(turn, dict):
            continue
        role = str(turn.get("role", "USER")).upper()
        mapped = "assistant" if role in {"ASSISTANT", "AI", "SWRLZ", "SELF"} else "system" if role == "SYSTEM" else "user"
        text = str(turn.get("text", "")).strip()
        if text:
            parts.append(f"<|im_start|>{mapped}\n{text}<|im_end|>\n")
    parts.append(f"<|im_start|>user\n{str(payload.get('prompt', '')).strip()}<|im_end|>\n<|im_start|>assistant\n")
    return "".join(parts)


R39Model.matrix = _cached_matrix
R39Model.vector = _cached_vector
R39Model.matvec = _bounded_matvec
_r39.render_chat_prompt = _compact_render_chat_prompt
