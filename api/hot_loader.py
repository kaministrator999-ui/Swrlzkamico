from __future__ import annotations

import importlib.util
import sys
import threading
import time
from pathlib import Path
from types import ModuleType
from typing import Callable

HOT_ROOT = Path("/tmp/swrlz-admin/runtime/hot")
HOT_CHAT = HOT_ROOT / "chat"
HOT_INFERENCE_DIR = HOT_ROOT / "inference"
HOT_INFERENCE = HOT_INFERENCE_DIR / "r39_engine.py"
AUTO_REFRESH_SECONDS = 30.0

_lock = threading.RLock()
_cached_module: ModuleType | None = None
_cached_signature: tuple[int, int] | None = None
_hot_refresher: Callable[[bool], None] | None = None
_last_refresh_attempt = 0.0


def register_hot_refresher(callback: Callable[[bool], None] | None) -> None:
    """Register the deployment-owned refresher used by hot read paths.

    The callback is intentionally narrow: it may hydrate/update the fixed hot
    allowlist, but it does not own routing/auth contracts. Failures are swallowed
    here so GitHub/network trouble never takes the bundled fallback offline.
    """
    global _hot_refresher, _last_refresh_attempt
    with _lock:
        _hot_refresher = callback
        _last_refresh_attempt = 0.0


def _refresh_if_due(force: bool = False) -> None:
    global _last_refresh_attempt
    callback = _hot_refresher
    if callback is None:
        return
    now = time.monotonic()
    with _lock:
        if not force and _last_refresh_attempt and now - _last_refresh_attempt < AUTO_REFRESH_SECONDS:
            return
        # Claim this refresh window before doing network I/O so simultaneous page
        # asset requests do not all fetch dev independently.
        _last_refresh_attempt = now
    try:
        callback(force)
    except Exception:
        # The hot layer is an optimization/iteration plane. Bundled assets and
        # inference remain the fail-safe source when refresh is unavailable.
        return


def hot_chat_path(name: str, bundled: Path) -> Path:
    _refresh_if_due()
    candidate = HOT_CHAT / name
    return candidate if candidate.is_file() else bundled


def _load_override() -> ModuleType | None:
    global _cached_module, _cached_signature
    if not HOT_INFERENCE.is_file():
        return None
    stat = HOT_INFERENCE.stat()
    signature = (stat.st_mtime_ns, stat.st_size)
    with _lock:
        if _cached_module is not None and _cached_signature == signature:
            return _cached_module
        inference_path = str(HOT_INFERENCE_DIR)
        if inference_path not in sys.path:
            sys.path.insert(0, inference_path)
        spec = importlib.util.spec_from_file_location("swrlz_hot_r39_engine", HOT_INFERENCE)
        if spec is None or spec.loader is None:
            raise RuntimeError("HOT_R39_IMPORT_SPEC_FAILED")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        for required in ("generate_events", "inspect_engine", "ENGINE_ID", "MODEL_SHA256"):
            if not hasattr(module, required):
                raise RuntimeError(f"HOT_R39_CONTRACT_MISSING:{required}")
        _cached_module = module
        _cached_signature = signature
        return module


def get_engine() -> tuple[ModuleType, str]:
    _refresh_if_due()
    override = _load_override()
    if override is not None:
        return override, "runtime-override"
    import swyrlz.r39_inference as bundled
    return bundled, "bundled"


def invalidate_engine() -> None:
    global _cached_module, _cached_signature
    with _lock:
        _cached_module = None
        _cached_signature = None
