"""§wyrlz stable server entrypoint.

Stable infrastructure owns the HTTP/bootstrap/control plane. Runtime application
pages, page-owned assets, and the hot R39 implementation are sourced from the
runtime branch by the dedicated hot/live loaders.

Server 2.3.3 adds startup-time LALM hydration and readiness probing so a newly
started worker warms the local R39 engine before Chat needs it.
"""
from __future__ import annotations

from api import server_v213 as _server
from api.runtime_hot import install as _install_hot_runtime, _safe_auto_sync
from api.hot_loader import get_engine
from api.chat_admin_session import install as _install_chat_admin_session
from api.chat_fast_status import install as _install_chat_fast_status
from api.admin_auth_guard import install as _install_admin_auth_guard
from api.live_source_guard import install as _install_live_source_guard
from api.control_plane import install as _install_control_plane
from api.native_status import install as _install_native_status
from api.contextual_input import install as _install_contextual_input
from api.account_routes_v2 import install as _install_account_routes
import api.chat_extensions as _chat_extensions

VERSION = "2.3.3"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution", "ready": True,
    "engineId": "swrlz_r39_native_qmatvec_v1", "fallbackEngineId": "swrlz_r39_python_reference_v1",
    "boundary": "compiled direct-quantized R39 execution; hot reasoning overlay remains independent of bundled server release",
}
_server.CAPABILITIES["lalm-startup-warm"] = {
    "kind": "runtime-execution",
    "ready": False,
    "phase": "server-start",
    "detail": "LALM/R39 is hydrated from runtime and probed before the worker is exposed to Chat.",
}
_install_admin_auth_guard(_server)
_install_hot_runtime(_server)
_install_chat_admin_session(_server)
_install_chat_fast_status(_server)
_install_control_plane(_server)
_install_native_status(_server)
_install_contextual_input(_server)
_install_account_routes(_server)
_install_live_source_guard(_server)


def _warm_lalm_at_start() -> None:
    """Hydrate and probe the local LALM before Chat handles user traffic."""
    try:
        sync = _safe_auto_sync(_server)
        engine, source = get_engine()
        state = engine.inspect_engine()
        _chat_extensions.LOCAL_READINESS.clear()
        _chat_extensions.LOCAL_READINESS.update({
            "checked": True,
            "engineSource": source,
            **state,
        })
        _server.CAPABILITIES["lalm-startup-warm"] = {
            "kind": "runtime-execution",
            "ready": bool(state.get("interactiveReady", state.get("modelReady", True))),
            "phase": "server-start-complete",
            "engineSource": source,
            "sync": sync,
            "state": state,
        }
        _server.activity("lalm-startup-warm", source=source, ready=True, branch=sync.get("branch", "runtime"))
    except Exception as exc:
        # Startup warmup is fail-open: the existing Chat readiness path remains
        # available as a fallback if hydration or probing cannot complete.
        _server.CAPABILITIES["lalm-startup-warm"] = {
            "kind": "runtime-execution",
            "ready": False,
            "phase": "server-start-fallback",
            "error": f"{type(exc).__name__}: {exc}",
        }
        _server.activity("lalm-startup-warm-failed", error=f"{type(exc).__name__}: {exc}")


_warm_lalm_at_start()
_server._write_server_state()

app = _server.app
INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
