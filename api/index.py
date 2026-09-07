"""§wyrlz Server 2.1.8 release entrypoint.

2.1.8 promotes web pages to a live runtime/source-managed layer. Admin, Chat,
the runtime index, and future registered pages can sync from the non-deploying
dev branch into instance-local runtime storage, be edited live, and optionally
be pushed back to dev without redeploying the stable server.
"""
from __future__ import annotations

from api import server_v213 as _server
from api.runtime_hot import install as _install_hot_runtime
from api.page_runtime import install as _install_page_runtime

VERSION = "2.1.8"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_python_reference_v1",
    "boundary": "canonical LFM2 reference profile; runtime override supported with bundled fallback; stream heartbeat timer resets after each engine progress event",
}
_install_hot_runtime(_server)
_install_page_runtime(_server)
_server._write_server_state()

app = _server.app

INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
