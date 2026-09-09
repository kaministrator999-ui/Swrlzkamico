from __future__ import annotations

import importlib.util
import sys
import threading
from pathlib import Path
from types import ModuleType

HOT_ROOT = Path("/tmp/swrlz-admin/runtime/hot")
HOT_CHAT = HOT_ROOT / "chat"
HOT_INFERENCE_DIR = HOT_ROOT / "inference"
HOT_INFERENCE = HOT_INFERENCE_DIR / "r39_engine.py"

_lock = threading.RLock()
_cached_module: ModuleType | None = None
_cached_signature: tuple[int, int] | None = None


def hot_chat_path(name: str, bundled: Path) -> Path:
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
