from __future__ import annotations

from typing import Any

import numpy as np

try:
    from swyrlz import _r39_native as _native
except Exception:
    _native = None


def available() -> bool:
    return _native is not None


def matvec(model: Any, name: str, x: np.ndarray) -> np.ndarray | None:
    if _native is None:
        return None
    d = model.desc[name]
    shape = d["shape"]
    cols = int(shape[0])
    rows = int(shape[1]) if len(shape) > 1 else 1
    if x.size != cols:
        return None
    try:
        out = _native.matvec(d["kind"], model._raw(name), cols, rows, np.asarray(x, dtype=np.float32))
    except Exception:
        return None
    out = np.asarray(out, dtype=np.float32)
    return out if out.shape == (rows,) else None
