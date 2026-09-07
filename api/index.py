"""§wyrlz Server 2.1.6 release entrypoint.

2.1.6 preserves the local R39 execution path, automatically initializes local
readiness on first status/use, keeps long blocking inference stages alive with
stream heartbeats, and ships Chat 1.3.2 thread/mobile control repairs.
"""
from __future__ import annotations

from api import server_v213 as _server

VERSION = "2.1.6"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_python_reference_v1",
    "boundary": "canonical LFM2 reference profile; automatic instance-local initialization; heartbeat-protected streamed execution; fails closed on incompatible structure",
}
_server._write_server_state()

app = _server.app

INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
