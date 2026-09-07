"""§wyrlz Server 2.1.4 release entrypoint.

2.1.4 preserves the proven 2.1.3 Admin/runtime implementation byte-for-byte in
api.server_v213 and advances the authoritative Vercel entrypoint by layering the
local R39 inference bridge through api.chat_extensions.
"""
from __future__ import annotations

from api import server_v213 as _server

VERSION = "2.1.4"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_python_reference_v1",
    "boundary": "canonical LFM2 reference profile; fails closed on incompatible R39 structure",
}
_server._write_server_state()

app = _server.app

# Compatibility exports used by diagnostics/tests and any existing imports.
INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
