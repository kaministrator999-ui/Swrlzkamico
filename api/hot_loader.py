from __future__ import annotations

import importlib.util
import sys
import threading
from pathlib import Path
from types import ModuleType
from typing import Callable

HOT_ROOT = Path("/tmp/swrlz-admin/runtime/hot")
HOT_CHAT = HOT_ROOT / "chat"
HOT_INFERENCE_DIR = HOT_ROOT / "inference"
HOT_INFERENCE = HOT_INFERENCE_DIR / "r39_engine.py"
HOT_SERVER_DIR = HOT_ROOT / "server"
HOT_CHAT_HISTORY_POLICY = HOT_SERVER_DIR / "chat_history_policy.py"
PREPARED_ROOT = Path(__file__).resolve().parents[1] / "swrzl_prepared_runtime"
PREPARED_CHAT = PREPARED_ROOT / "legacy-chat"
PREPARED_INFERENCE = PREPARED_ROOT / "lalm" / "r39_engine.py"
PREPARED_CHAT_HISTORY_POLICY = PREPARED_ROOT / "server-policy" / "chat_history_policy.py"

_lock = threading.RLock()
_cached_module: ModuleType | None = None
_cached_signature: tuple[int, int] | None = None
_cached_history_policy: ModuleType | None = None
_cached_history_signature: tuple[int, int] | None = None
_hot_refresher: Callable[[bool], None] | None = None


def register_hot_refresher(callback: Callable[[bool], None] | None) -> None:
    """Register the deployment-owned refresher used by hot read paths.

    The callback is intentionally narrow: it may hydrate/update the fixed hot
    allowlist, but it does not own routing/auth contracts. Failures are swallowed
    here so GitHub/network trouble never takes the bundled fallback offline.
    """
    global _hot_refresher
    with _lock:
        _hot_refresher = callback


def hot_chat_path(name: str, bundled: Path) -> Path:
    """Resolve Chat from explicit hot activation, then prepared deployment generation."""
    candidate = HOT_CHAT / name
    if candidate.is_file():
        return candidate
    prepared = PREPARED_CHAT / name
    return prepared if prepared.is_file() else bundled


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


def _load_history_policy_override() -> ModuleType | None:
    global _cached_history_policy, _cached_history_signature
    if not HOT_CHAT_HISTORY_POLICY.is_file():
        return None
    stat = HOT_CHAT_HISTORY_POLICY.stat()
    signature = (stat.st_mtime_ns, stat.st_size)
    with _lock:
        if _cached_history_policy is not None and _cached_history_signature == signature:
            return _cached_history_policy
        server_path = str(HOT_SERVER_DIR)
        if server_path not in sys.path:
            sys.path.insert(0, server_path)
        spec = importlib.util.spec_from_file_location("swrlz_hot_chat_history_policy", HOT_CHAT_HISTORY_POLICY)
        if spec is None or spec.loader is None:
            raise RuntimeError("HOT_CHAT_HISTORY_POLICY_IMPORT_SPEC_FAILED")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        for required in ("resolve_history", "inspect_policy", "CONTRACT_ID", "HOT_REVISION"):
            if not hasattr(module, required):
                raise RuntimeError(f"HOT_CHAT_HISTORY_POLICY_CONTRACT_MISSING:{required}")
        state = module.inspect_policy()
        if not isinstance(state, dict) or not state.get("ok"):
            raise RuntimeError("HOT_CHAT_HISTORY_POLICY_SELF_TEST_NOT_PROVEN")
        _cached_history_policy = module
        _cached_history_signature = signature
        return module


def get_engine() -> tuple[ModuleType, str]:
    override = _load_override()
    if override is not None:
        return override, "runtime-override"
    if PREPARED_INFERENCE.is_file():
        # Materialize the immutable deployment generation into the existing
        # loader target so contract validation/cache semantics stay singular.
        HOT_INFERENCE.parent.mkdir(parents=True, exist_ok=True)
        HOT_INFERENCE.write_bytes(PREPARED_INFERENCE.read_bytes())
        override = _load_override()
        if override is not None:
            return override, "prepared-deployment"
    import swyrlz.r39_inference as bundled
    return bundled, "bundled"


def get_chat_history_policy() -> tuple[ModuleType | None, str]:
    """Resolve the read-only canonical-history policy from the hot allowlist.

    Stable Server code keeps persistence/auth/write authority. A valid hot module
    may only reconstruct bounded history from already-authoritative server records.
    Missing or invalid runtime source is handled by the caller's bundled fallback.
    """
    override = _load_history_policy_override()
    if override is not None:
        return override, "runtime-override"
    if PREPARED_CHAT_HISTORY_POLICY.is_file():
        HOT_CHAT_HISTORY_POLICY.parent.mkdir(parents=True, exist_ok=True)
        HOT_CHAT_HISTORY_POLICY.write_bytes(PREPARED_CHAT_HISTORY_POLICY.read_bytes())
        override = _load_history_policy_override()
        if override is not None:
            return override, "prepared-deployment"
    return None, "bundled"


def invalidate_engine() -> None:
    global _cached_module, _cached_signature
    with _lock:
        _cached_module = None
        _cached_signature = None


def invalidate_chat_history_policy() -> None:
    global _cached_history_policy, _cached_history_signature
    with _lock:
        _cached_history_policy = None
        _cached_history_signature = None
