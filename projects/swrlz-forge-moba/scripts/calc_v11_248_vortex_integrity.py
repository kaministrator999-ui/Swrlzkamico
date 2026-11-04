#!/usr/bin/env python3
"""Focused v11.248 candidate calculator: no browser suites, no publish.\nRerun after shader-texture map guard and HTML head insertion repair.\n"""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch

manifest=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert manifest["name"]=="§wyrl§ Engine v11.248"
assert manifest["patches"][-1]=="patches/v11_248_astral_vortex_starters.py"
assert len(manifest["patches"])==279
base=gzip.decompress(base64.b64decode("".join(
 (ROOT/name).read_text("utf8").strip() for name in manifest["chunks"])))
assert len(base)==manifest["baseBytes"]
assert hashlib.sha256(base).hexdigest()==manifest["baseSha256"]
source=base.decode("utf8")
for rel in manifest["patches"]:
    source=load_patch(ROOT/rel)(source)
for word in (
 "SWYRL_ENGINE_DEPLOY_MARKER: V11_248_ASTRAL_VORTEX_STARTERS",
 "se248AstralVortexTheme",
 "se248StarterTab-particles",
 "window.SWYRL_ENGINE_VORTEX_248",
 "Astral Vortex",
):
    assert word in source,word
assert source.count("renderer.setAnimationLoop(tick);")==1
data=source.encode("utf8")
print(json.dumps({"version":"v11.248","patches":len(manifest["patches"]),
 "finalBytes":len(data),"finalSha256":hashlib.sha256(data).hexdigest(),
 "singleRenderer":True},indent=2))
