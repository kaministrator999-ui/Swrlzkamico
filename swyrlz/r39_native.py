from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import numpy as np

_native = None
_batch = None
_import_error = ""
_batch_import_error = ""
_loaded_from = ""
_batch_loaded_from = ""
_candidates: list[str] = []
_batch_candidates: list[str] = []


def _load_module(module_name: str, patterns: tuple[str, ...]):
    search_dirs = [Path(__file__).resolve().parent]
    for entry in sys.path:
        try: candidate_dir = Path(entry).resolve() / "swyrlz"
        except Exception: continue
        if candidate_dir not in search_dirs: search_dirs.append(candidate_dir)
    found: list[Path] = []
    for directory in search_dirs:
        for pattern in patterns:
            try: found.extend(sorted(directory.glob(pattern)))
            except OSError: pass
    unique=[]; seen=set()
    for path in found:
        key=str(path)
        if key not in seen: seen.add(key); unique.append(path)
    last_error=""
    for candidate in unique:
        try:
            spec=importlib.util.spec_from_file_location(module_name,candidate)
            if spec is None or spec.loader is None: continue
            mod=importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod)
            return mod,str(candidate),[str(x) for x in unique],""
        except Exception as exc: last_error=f"{type(exc).__name__}: {exc}"
    return None,"",[str(x) for x in unique],last_error


def _load_native() -> None:
    global _native,_batch,_import_error,_batch_import_error,_loaded_from,_batch_loaded_from,_candidates,_batch_candidates
    try:
        from swyrlz import _r39_native as mod
        _native=mod; _loaded_from=str(getattr(mod,"__file__","package-import"))
    except Exception as exc:
        _import_error=f"{type(exc).__name__}: {exc}"
        _native,_loaded_from,_candidates,retry=_load_module("swyrlz._r39_native",("_r39_native*.so","_r39_native*.pyd","_r39_native*.dylib"))
        if retry: _import_error=retry
        elif _native is not None: _import_error=""
    try:
        from swyrlz import _r39_batch as mod
        _batch=mod; _batch_loaded_from=str(getattr(mod,"__file__","package-import"))
    except Exception as exc:
        _batch_import_error=f"{type(exc).__name__}: {exc}"
        _batch,_batch_loaded_from,_batch_candidates,retry=_load_module("swyrlz._r39_batch",("_r39_batch*.so","_r39_batch*.pyd","_r39_batch*.dylib"))
        if retry: _batch_import_error=retry
        elif _batch is not None: _batch_import_error=""

_load_native()

def available()->bool: return _native is not None
def matmat_available()->bool: return _batch is not None and callable(getattr(_batch,"matmat",None))

def diagnostics()->dict[str,Any]:
    return {"available":available(),"loadedFrom":_loaded_from,"importError":_import_error,"candidateBinaries":list(_candidates),"batchAvailable":matmat_available(),"batchLoadedFrom":_batch_loaded_from,"batchImportError":_batch_import_error,"batchCandidateBinaries":list(_batch_candidates),"packageDir":str(Path(__file__).resolve().parent),"pythonVersion":sys.version.split()[0]}

def matvec(model:Any,name:str,x:np.ndarray)->np.ndarray|None:
    if _native is None:return None
    d=model.desc[name]; shape=d["shape"]; cols=int(shape[0]); rows=int(shape[1]) if len(shape)>1 else 1
    if x.size!=cols:return None
    try: out=_native.matvec(d["kind"],model._raw(name),cols,rows,np.asarray(x,dtype=np.float32))
    except Exception:return None
    out=np.asarray(out,dtype=np.float32); return out if out.shape==(rows,) else None

def matmat(model:Any,name:str,x:np.ndarray)->np.ndarray|None:
    if not matmat_available():return None
    d=model.desc[name]; shape=d["shape"]; cols=int(shape[0]); rows=int(shape[1]) if len(shape)>1 else 1
    value=np.ascontiguousarray(x,dtype=np.float32)
    if value.ndim!=2 or value.shape[0]!=cols:return None
    try: out=_batch.matmat(d["kind"],model._raw(name),cols,rows,value)
    except Exception:return None
    out=np.asarray(out,dtype=np.float32); return out if out.shape==(rows,value.shape[1]) else None
