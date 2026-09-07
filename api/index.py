"""§wyrlz Server 2.1.15 release entrypoint.

2.1.15 makes Chat authorization server-managed for normal same-origin browser use.
Loading /api/chat receives a bounded HttpOnly session cookie signed from the
server-side Chat secret; the permanent SWRLZ_WEB_CHAT_TOKEN never enters the UI.
GitHub-backed live page delivery from 2.1.13 remains intact.
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

VERSION = "2.1.15"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_python_reference_v1",
    "boundary": "canonical LFM2 reference profile; runtime override supported with bundled fallback; stream heartbeat timer resets after each engine progress event; status probes never inspect/load the model",
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
# Install last so this parent middleware owns live read resolution across Vercel instances.
_install_live_source_guard(_server)
_server._write_server_state()

app = _server.app

INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
