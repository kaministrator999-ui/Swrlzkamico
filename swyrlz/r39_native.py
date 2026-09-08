from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import numpy as np

_native = None
_import_error = ""
_loaded_from = ""
_candidates: list[str] = []


def _load_native() -> None:
    global _native, _import_error, _loaded_from, _candidates
    try:
        from swyrlz import _r39_native as mod
        _native = mod
        _loaded_from = str(getattr(mod, "__file__", "package-import"))
        return
    except Exception as exc:
        _import_error = f"{type(exc).__name__}: {exc}"

    package_dir = Path(__file__).resolve().parent
    patterns = ("_r39_native*.so", "_r39_native*.pyd", "_r39_native*.dylib")
    found: list[Path] = []
    for pattern in patterns:
        found.extend(sorted(package_dir.glob(pattern)))
    _candidates = [str(path) for path in found]

    for candidate in found:
        try:
            spec = importlib.util.spec_from_file_location("swyrlz._r39_native", candidate)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)
            _native = mod
            _loaded_from = str(candidate)
            _import_error = ""
            return
        except Exception as exc:
            _import_error = f"{type(exc).__name__}: {exc}"


_load_native()


def available() -> bool:
    return _native is not None


def diagnostics() -> dict[str, Any]:
    return {
        "available": available(),
        "loadedFrom": _loaded_from,
        "importError": _import_error,
        "candidateBinaries": list(_candidates),
        "packageDir": str(Path(__file__).resolve().parent),
        "pythonVersion": sys.version.split()[0],
    }


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
