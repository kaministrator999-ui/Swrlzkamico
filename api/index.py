"""§wyrlz Server 2.2.8 release entrypoint.

2.2.8 adds account identity/data boundaries, durable workflow chat generation,
resumable streams, and the v35 adaptive response horizon while preserving the
existing R39/native control planes.
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
from api.chat_identity import install as _install_chat_identity
from api.chat_durable import install as _install_chat_durable

VERSION = "2.2.8"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_native_qmatvec_v1",
    "fallbackEngineId": "swrlz_r39_python_reference_v1",
    "boundary": "compiled direct-quantized matvec kernels for f32/f16/bf16/q4_0/q8_0/q4_k/q6_k with corrected fp16 subnormal scaling; Python reference remains correctness/fallback oracle; LALM runtime override is independent of Chat assets",
}
_server.CAPABILITIES["durable-chat-workflows"] = {
    "kind": "durable-background-generation",
    "ready": True,
    "streamResume": True,
    "userScoped": True,
    "workflowNamespace": "swrlz-chat",
}
_server.CAPABILITIES["user-account-boundary"] = {
    "kind": "google-identity-and-server-data",
    "ready": True,
    "identityKey": "google-sub",
    "chatHistoryServerScoped": True,
    "profileServerScoped": True,
    "persistentStore": "KV_REST_API_URL/KV_REST_API_TOKEN when configured",
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
_install_chat_durable(_server)
# Install last so this parent middleware owns GitHub-backed live reads and account UI across instances.
_install_live_source_guard(_server)
_install_chat_identity(_server)
_server._write_server_state()

app = _server.app

INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
