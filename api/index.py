"""§wyrlz Server 2.3.9 runtime entrypoint.

2.3.9 introduces per-module canonical version files indexed by VERSION.txt and
keeps runtime-owned Chat/LALM behavior on the durable runtime branch. Startup
LALM warming is owned by the stable infrastructure entrypoint; this runtime
entrypoint remains the live application source of truth for hot application
behavior.
"""
from __future__ import annotations

from api import server_v213 as _server
from api.runtime_hot import install as _install_hot_runtime
from api.page_runtime import install as _install_page_runtime
from api.page_runtime_guard import install as _install_page_runtime_guard
from api.live_runtime_routes import install as _install_live_runtime_routes
from api.chat_ui_guard import install as _install_chat_ui_guard
from api.page_manager_ui import install as _install_page_manager_ui
from api.chat_admin_session import install as _install_chat_admin_session
from api.chat_fast_status import install as _install_chat_fast_status
from api.admin_auth_guard import install as _install_admin_auth_guard
from api.live_source_guard import install as _install_live_source_guard
from api.control_plane import install as _install_control_plane
from api.native_status import install as _install_native_status

VERSION = "2.3.9"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_native_qmatvec_v1",
    "fallbackEngineId": "swrlz_r39_python_reference_v1",
    "boundary": "compiled direct-quantized matvec kernels plus packaged optional direct-quantized batched matmul kernel for prompt-prefill experiments; corrected fp16 subnormal scaling, float32 hot accumulators, Fluid Compute/fixed-region reuse, and region-shared exact recurrent cursors remain preserved; live hot engine is not switched to batched prefill until equivalence/performance gates pass",
}
_server.CAPABILITIES["r39-native-batched-prefill-kernel"] = {
    "kind": "runtime-execution",
    "ready": True,
    "activation": "gated-hot-runtime",
    "blockTokens": 64,
    "detail": "Base image packages swyrlz._r39_batch; hot v30 activation remains separate and gated by native diagnostics plus equivalence/performance validation.",
}
_install_admin_auth_guard(_server)
_install_hot_runtime(_server)
_install_page_runtime_guard()
_install_page_runtime(_server)
_install_live_runtime_routes(_server)
_install_chat_admin_session(_server)
_install_chat_fast_status(_server)
_install_chat_ui_guard(_server)
_install_page_manager_ui(_server)
_install_control_plane(_server)
_install_native_status(_server)
_install_live_source_guard(_server)
_server._write_server_state()

app = _server.app
INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
