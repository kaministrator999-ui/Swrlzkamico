#!/usr/bin/env python3
"""Validate the governed v11.246 §E build and its native Particle Studio toggle."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_SHA="__V11_246_SEAL__"
EXPECTED_BYTES=0  # replaced with calculated release bytes before merge
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_246_PARTICLE_BOTTOM_TOGGLE"
p=argparse.ArgumentParser()
p.add_argument("--output",required=True)
p.add_argument("--request",action="store_true")
args=p.parse_args()
manifest=json.loads((ROOT/"source-manifest.json").read_text(encoding="utf8"))
assert manifest["name"]=="§wyrl§ Engine v11.246"
assert manifest["finalArtifact"]=="swyrl_engine_v11_246.html"
assert len(manifest["patches"])==277
assert manifest["patches"][-1]=="patches/v11_246_particle_bottom_toggle.py"
assert manifest["finalSha256"]==EXPECTED_SHA
assert manifest["finalBytes"]==EXPECTED_BYTES
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/"build_space.py"),"--output",str(out)],check=True)
raw=(out/"index.html").read_bytes()
assert raw==(out/"modeler.html").read_bytes()
assert len(raw)==EXPECTED_BYTES
assert hashlib.sha256(raw).hexdigest()==EXPECTED_SHA
html=raw.decode("utf8")
for needle in (
    MARKER,
    "<title>§wyrl§ Engine · Maker v11.246</title>",
    "SWYRL_ENGINE_PARTICLE_BOTTOM_TOGGLE_246",
    'id="se246ParticleBottomToggleStyle"',
    "stopImmediatePropagation()",
    "controller?.collapse?.()",
    "controller?.show?.()",
    "data-se245-particle-collapsed=true",
    "se243InspectorToggle",
    "se245ParticleCollapse",
    "SWYRL_ENGINE_PARTICLE_COLLAPSE_245",
    "SWYRL_ENGINE_PARTICLE_STAGE_240",
    "SWYRL_ENGINE_SHEEP_REMOVAL_PERFORMANCE_244",
    "se240ParticleStageOrbit",
):
    assert needle in html,needle
assert html.count("renderer.setAnimationLoop(tick);")==1
receipt=json.loads((out/"SOURCE.json").read_text(encoding="utf8"))
assert receipt["sourceVersion"]==manifest["name"]
assert receipt["finalSha256"]==EXPECTED_SHA
assert receipt["finalBytes"]==EXPECTED_BYTES
assert receipt["patches"]==manifest["patches"]
assert len(receipt["assets"])==69
for path,metadata in receipt["assets"].items():
    data=(out/path).read_bytes()
    assert len(data)==metadata["bytes"],path
    assert hashlib.sha256(data).hexdigest()==metadata["sha256"],path
if args.request:
    request=json.loads((ROOT/"DEPLOY_REQUEST.json").read_text(encoding="utf8"))
    assert request["releaseVersion"]=="v11.246"
    assert request["deployMarker"]==MARKER
    assert request["sourceIntegritySha256"]==EXPECTED_SHA
    assert isinstance(request.get("sourceCommit"),str) and len(request["sourceCommit"])==40
print(json.dumps({"status":"PASS_SEALED_SOURCE","version":"v11.246",
    "patches":len(receipt["patches"]),"assets":len(receipt["assets"]),
    "htmlBytes":len(raw),"htmlSha256":EXPECTED_SHA,
    "particleBottomToggle":"mobile collapse / show controls",
    "ownerPhoneAcceptance":False},indent=2))
