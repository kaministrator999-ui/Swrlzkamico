"""§wyrlz Server 2.1.5 release entrypoint.

2.1.5 preserves the proven 2.1.4 local R39 execution path, resolves producer-specific
byte-level BPE tokenizer labels from structural evidence, and ships the mobile Chat
toolbar cleanup in Chat 1.3.1.
"""
from __future__ import annotations

from api import server_v213 as _server

VERSION = "2.1.5"
_server.VERSION = VERSION
_server.app.version = VERSION
_server.CAPABILITIES["local-r39-inference"] = {
    "kind": "runtime-execution",
    "ready": True,
    "engineId": "swrlz_r39_python_reference_v1",
    "boundary": "canonical LFM2 reference profile; tokenizer aliases require structural BPE evidence; fails closed across tokenizer families",
}
_server._write_server_state()

app = _server.app

INSTANCE = _server.INSTANCE
ROOT = _server.ROOT
LIVE = _server.LIVE
WEB = _server.WEB
RUNTIME = _server.RUNTIME
CAPABILITIES = _server.CAPABILITIES
