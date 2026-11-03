#!/usr/bin/env python3
"""Verify sealed §E v11.236 solid Sheep Tag houses, wolf root preview and starter category tabs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
cli = argparse.ArgumentParser()
cli.add_argument("--output", required=True)
cli.add_argument("--request", action="store_true")
args = cli.parse_args()
output = Path(args.output).resolve()
manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf8"))
assert manifest["name"] == "§wyrl§ Engine v11.236"
assert manifest["finalArtifact"] == "swyrl_engine_v11_235.html"
assert len(manifest["patches"]) == 268
assert manifest["patches"][-1] == "patches/v11_236_sheep_gables_wolf_root_starter_groups.py"
subprocess.run([sys.executable, str(ROOT / "build_space.py"),
                "--output", str(output)], check=True)
raw = (output / "index.html").read_bytes()
assert (output / "modeler.html").read_bytes() == raw
assert len(raw) == manifest["finalBytes"]
assert hashlib.sha256(raw).hexdigest() == manifest["finalSha256"]
html = raw.decode("utf8")
required = (
    "SWYRL_ENGINE_DEPLOY_MARKER: V11_236_SHEEP_GABLES_WOLF_ROOT_STARTER_GROUPS",
    "<title>§wyrl§ Engine · Maker v11.236</title>",
    "swrlz-forge-studio-commands-v1",
    "function se236GableInfill(w,depth,eave,rise)",
    "se236GableInfill(w+.12,depth,tall+.25",
    "function se236InstallStarterGroups()",
    "se236StarterModels",
    "se236WolfPreviewOptions",
    "root.position.set(base[0],base[1]+(inPlace?0:bob),base[2])",
    "Gable · ",
    "Ruff · cheek",
    "function se224WolfVertexWeights(pos,rig,part,indexById=null)",
    "root.updateMatrixWorld(true);se224WolfSkeleton.update();atelierHDDirty=true;",
    "panel.classList.add('se-inspector-mode-view','se-wolf-motion-focus')",
    "const se235SaveKey=ui.querySelector('#modelAtelierWolfSaveKey')",
    "if(category==='Motion'&&window.SWYRL_ENGINE_WOLF_RIG?.status?.().available)",
    "function studioSnapshot(workspace)",
    "function validateStudioOperation(op,ctx)",
    "function executeStudio(op)",
    "function seChatRigApply(op)",
    "function se232ActivateSelectedModelWorkspace()",
    "function se225MaterialAssign(actorId,materialId)",
    "function se223Create(key='magic')",
    "const PROTOCOL='swrlz-forge-chat-v1'",
)
for needle in required:
    assert needle in html, needle
assert html.count("function executeStudio(op)") == 1
assert html.count("renderer.setAnimationLoop(tick);") == 1
receipt = json.loads((output / "SOURCE.json").read_text(encoding="utf8"))
assert receipt["sourceVersion"] == manifest["name"]
assert receipt["finalBytes"] == manifest["finalBytes"]
assert receipt["finalSha256"] == manifest["finalSha256"]
assert receipt["patches"] == manifest["patches"]
assert len(receipt["assets"]) == 68
for path, metadata in receipt["assets"].items():
    content = (output / path).read_bytes()
    assert len(content) == metadata["bytes"] and hashlib.sha256(content).hexdigest() == metadata["sha256"], path
if args.request:
    request = json.loads((ROOT / "DEPLOY_REQUEST.json").read_text(encoding="utf8"))
    assert request["releaseVersion"] == "v11.236"
    assert request["deployMarker"] == "SWYRL_ENGINE_DEPLOY_MARKER: V11_236_SHEEP_GABLES_WOLF_ROOT_STARTER_GROUPS"
    assert request["sourceIntegritySha256"] == manifest["finalSha256"]
    assert isinstance(request.get("sourceCommit"), str) and len(request["sourceCommit"]) == 40
print(json.dumps({"status": "PASS_SEALED_SOURCE", "version": manifest["name"],
                  "patches": len(manifest["patches"]), "htmlBytes": len(raw),
                  "htmlSha256": manifest["finalSha256"],
                  "studioCommands": "v1", "wolfMotionMenu": "v11.235", "houseModels": "v11.236", "rootPreview": "v11.236", "starterCategories": "v11.236", "hostedTest": False, "ownerDeviceTest": False}, indent=2))
