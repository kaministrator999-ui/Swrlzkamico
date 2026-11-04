#!/usr/bin/env python3
"""Verify sealed v11.249 Astral Vortex native starter package without browser suites."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
SHA="38371bac1f90c7714f1ab117a74288f6b68aa5cbe5d0f78d5821ad51f53b9a47"
SIZE=7889180
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_249_PARTICLE_WORKSTATION"
parser=argparse.ArgumentParser()
parser.add_argument("--output",required=True)
parser.add_argument("--request",action="store_true")
args=parser.parse_args()
manifest=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert manifest["name"]=="§wyrl§ Engine v11.249"
assert manifest["finalArtifact"]=="swyrl_engine_v11_248.html"
assert manifest["patches"][-1]=="patches/v11_249_particle_studio_workstation.py"
assert len(manifest["patches"])==280
assert manifest["finalBytes"]==SIZE and manifest["finalSha256"]==SHA
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/"build_space.py"),"--output",str(out)],check=True)
raw=(out/"index.html").read_bytes()
assert raw==(out/"modeler.html").read_bytes()
assert len(raw)==SIZE and hashlib.sha256(raw).hexdigest()==SHA
html=raw.decode("utf8")
for term in (
    MARKER,
    "<title>§wyrl§ Engine · Maker v11.249</title>",
    "window.SWRLZ_FORGE_BUILD={version:'v11.249'",
    "window.SWYRL_ENGINE_EDITOR_PREVIEW_247=Object.freeze",
    "function se223Frame(dt,t){",
    "SWYRL_ENGINE_EDITOR_PREVIEW_247?.sync?.()",
    'id="se247LivePreviewStyle"',
    "se247PreviewPanel",
    "se247-row",
    "se248AstralVortexTheme",
    "se248StarterTab-particles",
    "window.SWYRL_ENGINE_VORTEX_248",
    "Astral Vortex",
    "vortexCyan",
    "vortexCore",
    "vortexSpark",
    "se249ParticleWorkstationStyle",
    "window.SWYRL_ENGINE_PARTICLE_UI_249",
    "window.SWYRL_ENGINE_RIBBONS_249",
    "se249NativeHolder",
    "se249LayerRows",
    "vortexSpin",
    "vortexPull",
    "vortexGlow",
    "vortexTilt",
    "Edit-mode live previews",
    "se223State.preview=true",
    "storyPreview(0)",
    "storyExitPreview()",
    "animeUpdateCinematic=function(dt)",
    "SWYRL_ENGINE_GUI_STUDIO",
    "SWYRL_ENGINE_PARTICLE_STAGE_240",
    "SWYRL_ENGINE_PARTICLE_BOTTOM_TOGGLE_246",
):
    assert term in html,term
assert html.count("renderer.setAnimationLoop(tick);")==1
receipt=json.loads((out/"SOURCE.json").read_text("utf8"))
assert receipt["sourceVersion"]==manifest["name"]
assert receipt["finalSha256"]==SHA and receipt["finalBytes"]==SIZE
assert receipt["patches"]==manifest["patches"]
assert len(receipt["assets"])==69
for name,metadata in receipt["assets"].items():
    data=(out/name).read_bytes()
    assert len(data)==metadata["bytes"],name
    assert hashlib.sha256(data).hexdigest()==metadata["sha256"],name
if args.request:
    request=json.loads((ROOT/"DEPLOY_REQUEST.json").read_text("utf8"))
    assert request["releaseVersion"]=="v11.249"
    assert request["deployMarker"]==MARKER
    assert request["sourceIntegritySha256"]==SHA
    assert isinstance(request.get("sourceCommit"),str) and len(request["sourceCommit"])==40
print(json.dumps({"status":"SEALED_SOURCE_VERIFIED",
 "version":"v11.249","patches":280,"htmlBytes":SIZE,"sha256":SHA,
 "assets":len(receipt["assets"]),"preview":"Full Particle Studio workstation and native ribbon VFX",
 "ownerQuestAcceptance":False},indent=2))
