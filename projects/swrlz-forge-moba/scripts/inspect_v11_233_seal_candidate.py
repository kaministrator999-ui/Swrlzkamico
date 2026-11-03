#!/usr/bin/env python3
"""Measure final §E source from a temporary checkout with receipt checks disabled.

Only the runner's local source manifest is modified during a try/finally.
This is an *inspection* tool: a measured digest must be committed separately
and pass the unmodified production build/verify before any publication.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "source-manifest.json"
original = path.read_bytes()
manifest = json.loads(original)
assert manifest["name"] == "§wyrl§ Engine v11.233"
assert manifest["patches"][-1] == "patches/v11_233_chat_native_studio_bridge.py"
try:
    manifest["finalBytes"] = 0
    manifest["finalSha256"] = ""
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf8")
    with tempfile.TemporaryDirectory() as output:
        subprocess.run([sys.executable, str(ROOT / "build_space.py"), "--output", output], check=True)
        raw = (Path(output) / "index.html").read_bytes()
        print(json.dumps({"status": "MEASURE_ONLY_NOT_RELEASE",
                          "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                          "patches": len(manifest["patches"]),
                          "manifestChecksumWasTemporarilyDisabled": True,
                          "hostedTest": False}, indent=2))
finally:
    path.write_bytes(original)
