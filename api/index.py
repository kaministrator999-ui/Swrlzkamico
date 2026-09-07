"""§wyrlz Server 2.1.7 release entrypoint.

2.1.7 adds a narrow hot-runtime boundary for Chat UI and R39 engine iteration.
Stable server/auth/API contracts remain deployment-controlled; authenticated Admin
syncs approved hot files from the non-deploying dev branch into instance-local /tmp.
"""
from __future__ import annotations

from api import server_v213 as _server
from api.runtime_hot import install as _install_hot_runtime

VERSION = "2.1.7"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_python_reference_v1",
    "boundary": "canonical LFM2 reference profile; runtime override supported with bundled fallback; stream heartbeat timer resets after each engine progress event",
}
_install_hot_runtime(_server)
_server._write_server_state()

app = _server.app

INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
