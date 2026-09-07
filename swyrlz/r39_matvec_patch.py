"""Bounded-memory matrix-vector path for the R39 Python reference executor.

The base reference implementation is intentionally simple. This release patch keeps
that implementation byte-stable while replacing only R39Model.matvec so quantized
matrices are dequantized in bounded row batches instead of materializing an entire
large matrix at once.
"""
from __future__ import annotations

import numpy as np

from swyrlz.r39_inference import R39InferenceError, R39Model, _deq


def _bounded_matvec(self: R39Model, name: str, x: np.ndarray) -> np.ndarray:
    d = self.desc[name]
    shape = d["shape"]
    cols = int(shape[0])
    rows = int(shape[1]) if len(shape) > 1 else 1
    if x.size != cols:
        raise R39InferenceError("R39_MATVEC_SHAPE_MISMATCH", f"{name}: expected {cols}, got {x.size}")
    rb = self._row_bytes(d["kind"], cols)
    raw = self._raw(name)
    batch_rows = max(1, min(rows, max(64, (4 * 1024 * 1024) // max(4 * cols, 1))))
    out = np.empty(rows, dtype=np.float32)
    for start in range(0, rows, batch_rows):
        count = min(batch_rows, rows - start)
        block = raw[start * rb:(start + count) * rb]
        matrix = _deq(d["kind"], block, (cols, count))
        out[start:start + count] = matrix @ x
    return out


R39Model.matvec = _bounded_matvec
