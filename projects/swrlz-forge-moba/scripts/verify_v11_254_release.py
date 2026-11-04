#!/usr/bin/env python3
"""Verify sealed v11.254 Particle Studio dock/preview/camera hotfix without broad browser suites."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
SHA="aa768eb37c7a27f0252eff14b3e2a0f50b9754fb536af95e5036cd826883cb2c"
SIZE=8004949
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_254_PARTICLE_DOCK_PREVIEW_CAMERA"
parser=argparse.ArgumentParser()
parser.add_argument("--output",required=True)
parser.add_argument("--request",action="store_true")
args=parser.parse_args()
manifest=json.loads((ROOT/"source-manifest.json").read_text("utf8"))
assert manifest["name"]=="§wyrl§ Engine v11.254"
assert manifest["finalArtifact"]=="swyrl_engine_v11_254.html"
assert manifest["patches"][-1]=="patches/v11_254_particle_dock_preview_camera.py"
assert len(manifest["patches"])==285
assert manifest["finalBytes"]==SIZE and manifest["finalSha256"]==SHA
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/"build_space.py"),"--output",str(out)],check=True)
raw=(out/"index.html").read_bytes()
assert raw==(out/"modeler.html").read_bytes()
assert len(raw)==SIZE and hashlib.sha256(raw).hexdigest()==SHA
html=raw.decode("utf8")
for term in (
    MARKER,
    "<title>§wyrl§ Engine · Maker v11.254</title>",
    "window.SWRLZ_FORGE_BUILD={version:'v11.254'",
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
    "se250DesktopDocksStyle",
    "window.SWYRL_ENGINE_PARTICLE_DOCKS_250",
    "window.SWYRL_ENGINE_PARTICLE_TRACKS_250",
    "se250Handle-left",
    "se250LayoutMode",
    "vRibbonUV",
    "se251UnifiedStudiosStyle",
    "window.SWYRL_ENGINE_PARTICLE_CURVE_RUNTIME_251",
    "window.SWYRL_ENGINE_PARTICLE_CURVES_251",
    "window.SWYRL_ENGINE_PARAMETER_TIMELINE_251",
    "window.SWYRL_ENGINE_SHARED_WORKSTATIONS_251",
    "window.SWYRL_ENGINE_NEBULA_251",
    "window.SWYRL_ENGINE_NEBULA_SETTINGS_251",
    "se251CurveGraph",
    "se251MaterialLibrary",
    "se251ModelLibrary",
    "se251NebulaControls",
    "window.SWYRL_ENGINE_MODEL_STRESS_252",
    "window.SWYRL_ENGINE_STRESS_TEST_252",
    "se252StressDiagnosticsStyle",
    "se254ParticleDockHotfix",
    "window.SWYRL_ENGINE_PARTICLE_DOCKS_250?.init?.();",
    "const active=stageActive?!!se223State.preview:",
    "zoomDistance:state.distance",
    "const mounted=records.some(record=>",
    "if((!modelOpen&&!particleOpen&&!state.particle)||q('#seReleaseNotesDialog')?.open)",
    "Diagnostic high-poly specimen",
    "Diagnostic particle cloud",
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
assert "const observer=new MutationObserver(()=>{\n if(!q('#se251ModelLibrary')" not in html
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
    assert request["releaseVersion"]=="v11.254"
    assert request["deployMarker"]==MARKER
    assert request["sourceIntegritySha256"]==SHA
    assert isinstance(request.get("sourceCommit"),str) and len(request["sourceCommit"])==40
print(json.dumps({"status":"SEALED_SOURCE_VERIFIED",
 "version":"v11.254","patches":285,"htmlBytes":SIZE,"sha256":SHA,
 "assets":len(receipt["assets"]),"preview":"Particle dock ownership, live VFX preview and immediate zoom",
 "ownerQuestAcceptance":False},indent=2))
