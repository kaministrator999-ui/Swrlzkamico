#!/usr/bin/env python3
"""One-off source measurement for §E v11.232; no hosted deployment or engine writes."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
from build_space import load_patch

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
assert manifest["name"] == "§wyrl§ Engine v11.231"
assert manifest["patches"][-1] == "patches/v11_231_sheep_house_camera_fit.py"
encoded = "".join((ROOT / entry).read_text().strip() for entry in manifest["chunks"])
base = gzip.decompress(base64.b64decode(encoded))
assert len(base) == manifest["baseBytes"]
assert hashlib.sha256(base).hexdigest() == manifest["baseSha256"]
text = base.decode("utf-8")
for entry in manifest["patches"]:
    text = load_patch(ROOT / entry)(text)
text = load_patch(ROOT / "patches/v11_232_chat_native_studio_bridge.py")(text)
raw = text.encode("utf-8")
assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_232_CHAT_NATIVE_STUDIO_BRIDGE" in text
assert "<title>§wyrl§ Engine · Maker v11.232</title>" in text
for marker in ("function seChatRigApply(op)", "function studioSnapshot(workspace)",
               "function validateStudioOperation(op,ctx)", "function executeStudio(op)",
               "swrlz-forge-studio-commands-v1", "material.create", "particle.create",
               "rig.pose", "rig.keyframe"):
    assert marker in text, marker
assert text.count("function executeStudio(op)") == 1
assert text.count("function studioSnapshot(workspace)") == 1
print(json.dumps({
    "measurement": "CANDIDATE_NOT_SEALED_OR_DEPLOYED",
    "version": "v11.232", "patches": len(manifest["patches"]) + 1,
    "finalBytes": len(raw), "finalSha256": hashlib.sha256(raw).hexdigest(),
    "nativeStudioCommandSchema": "swrlz-forge-studio-commands-v1",
    "hostedTest": False, "deviceTest": False
}, indent=2))
