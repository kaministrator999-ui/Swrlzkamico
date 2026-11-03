#!/usr/bin/env python3
"""Verify exact §E v11.240 Sheep Tag grass PBR release source."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA = "8a5b1e310f3359cb0dbd97a50b7ca1e0831af097f4a2123def5e96fe47d476bf"
EXPECTED_BYTES = 7770423
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_240_SHEEP_GRASS_PBR"
cli = argparse.ArgumentParser()
cli.add_argument("--output", required=True)
cli.add_argument("--request", action="store_true")
args = cli.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf8"))
assert manifest["name"] == "§wyrl§ Engine v11.240"
assert manifest["finalArtifact"] == "swyrl_engine_v11_240.html"
assert len(manifest["patches"]) == 271
assert manifest["patches"][-1] == "patches/v11_240_sheep_grass_pbr.py"
assert manifest["finalBytes"] == EXPECTED_BYTES
assert manifest["finalSha256"] == EXPECTED_SHA
subprocess.run([sys.executable,str(ROOT/"build_space.py"),"--output",str(out)],check=True)
raw = (out/"index.html").read_bytes()
assert (out/"modeler.html").read_bytes() == raw
assert len(raw) == EXPECTED_BYTES
assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA
html = raw.decode("utf8")
for needle in (
    MARKER,
    "<title>§wyrl§ Engine · Maker v11.240</title>",
    "SWYRL_ENGINE_QUEST_RADIAL_STABILITY_238",
    "SWYRL_ENGINE_QUEST_HEADTURN_239",
    "SWYRL_ENGINE_SHEEP_GRASS_PBR_240",
    "function se240PreparePBR(image)",
    "function se240ApplyOneGround(mesh)",
    "grass-source-color-quest.webp",
    "se181XRRaycast=function(record)",
    "se239XR.legacyActorRaycastsSkipped++",
    "SWYRL_ENGINE_QUEST_WORKSPACE_238",
    "function se238NativeMenuOpen()",
    "se238Radial.slowAppFrames++",
    "const se238LabelTextures=new Map()",
    'id="se238QuestBrowserLayout"',
    "se238ModelActions",
    "se238GameToolsToggle",
    "se238-tool-rail-open",
    "SWYRL_ENGINE_QUEST_OS_STABILITY_211",
    "function se236GableInfill(w,depth,eave,rise)",
    "function studioSnapshot(workspace)",
    "function executeStudio(op)",
):
    assert needle in html, needle
assert html.count("renderer.setAnimationLoop(tick);") == 1
receipt = json.loads((out/"SOURCE.json").read_text(encoding="utf8"))
assert receipt["sourceVersion"] == manifest["name"]
assert receipt["finalSha256"] == EXPECTED_SHA
assert receipt["finalBytes"] == EXPECTED_BYTES
assert receipt["patches"] == manifest["patches"]
assert len(receipt["assets"]) == 69
for path, metadata in receipt["assets"].items():
    data=(out/path).read_bytes()
    assert len(data) == metadata["bytes"] and hashlib.sha256(data).hexdigest() == metadata["sha256"], path
assert "assets/sheep-tag/grass-source-color-quest.webp" in receipt["assets"]
with (out/"assets/sheep-tag/grass-source-color-quest.webp").open("rb") as f:
    assert f.read(4)==b"RIFF","Invalid grass source"
if args.request:
    request=json.loads((ROOT/"DEPLOY_REQUEST.json").read_text(encoding="utf8"))
    assert request["releaseVersion"] == "v11.240"
    assert request["deployMarker"] == MARKER
    assert request["sourceIntegritySha256"] == EXPECTED_SHA
    assert isinstance(request.get("sourceCommit"),str) and len(request["sourceCommit"]) == 40
print(json.dumps({
    "status":"PASS_SEALED_SOURCE","version":"v11.240",
    "patches":len(receipt["patches"]),"assets":len(receipt["assets"]),
    "htmlBytes":len(raw),"htmlSha256":EXPECTED_SHA,
    "questMenu":"v11.238","questBrowserWorkspace":"v11.238","headturnBudget":"v11.239",
    "sheepGrassMaterial":"albedo + computed normal + matte roughness",
    "ownerHeadsetAcceptance":False
},indent=2))
