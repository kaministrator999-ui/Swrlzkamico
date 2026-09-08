"""§wyrlz Server 2.2.8 release entrypoint.

2.2.8 keeps the 2.2.7 authenticated draft-prefill bridge, tightens long-prefill
stream heartbeats to three seconds, and supports the hot R39 shared speculative draft
cursor experiment. Chat live-source assets remain independent from the base deployment.
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
from api.chat_draft_prefill import install as _install_chat_draft_prefill
from api.chat_liveness import install as _install_chat_liveness
from api.admin_auth_guard import install as _install_admin_auth_guard
from api.live_source_guard import install as _install_live_source_guard
from api.control_plane import install as _install_control_plane
from api.native_status import install as _install_native_status

VERSION = "2.2.8"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_native_qmatvec_v1",
    "fallbackEngineId": "swrlz_r39_python_reference_v1",
    "boundary": "compiled direct-quantized matvec kernels for f32/f16/bf16/q4_0/q8_0/q4_k/q6_k with corrected fp16 subnormal scaling, float32 hot accumulators, parallel cold transport hydration, single-pass raw verification, Fluid Compute/fixed-region worker reuse, region-shared conversation cursor support through Vercel Runtime Cache, speculative unsent-draft prefill with exact-prefix promotion, and 3-second transport heartbeats during long compute waits; Python reference remains correctness/fallback oracle; LALM runtime override remains independent of Chat assets",
}
_install_admin_auth_guard(_server)
_install_hot_runtime(_server)
_install_page_runtime_guard()
_install_page_runtime(_server)
_install_live_runtime_routes(_server)
_install_chat_admin_session(_server)
_install_chat_fast_status(_server)
_install_chat_draft_prefill(_server)
_install_chat_liveness(_server)
_install_chat_ui_guard(_server)
_install_page_manager_ui(_server)
_install_control_plane(_server)
_install_native_status(_server)
# Install last so this parent middleware owns GitHub-backed live reads across Vercel instances.
_install_live_source_guard(_server)
_server._write_server_state()

app = _server.app

INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
