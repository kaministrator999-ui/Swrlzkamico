#!/usr/bin/env python3
"""Verify sealed §E v11.233 native Chat studio host against exact packaged source."""
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
assert manifest["name"] == "§wyrl§ Engine v11.233"
assert manifest["finalArtifact"] == "swyrl_engine_v11_233.html"
assert len(manifest["patches"]) == 265
assert manifest["patches"][-1] == "patches/v11_233_chat_native_studio_bridge.py"
subprocess.run([sys.executable, str(ROOT / "build_space.py"),
                "--output", str(output)], check=True)
raw = (output / "index.html").read_bytes()
assert (output / "modeler.html").read_bytes() == raw
assert len(raw) == manifest["finalBytes"] == 7724884
assert hashlib.sha256(raw).hexdigest() == manifest["finalSha256"] == (
    "8fdfc0275d2b3f87f276e4ee50abe595ca089b23a96bd1bdabef140eb9537771"
)
html = raw.decode("utf8")
required = (
    "SWYRL_ENGINE_DEPLOY_MARKER: V11_233_CHAT_NATIVE_STUDIO_BRIDGE",
    "<title>§wyrl§ Engine · Maker v11.233</title>",
    "swrlz-forge-studio-commands-v1",
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
    assert request["releaseVersion"] == "v11.233"
    assert request["deployMarker"] == "V11_233_CHAT_NATIVE_STUDIO_BRIDGE"
    assert request["sourceIntegritySha256"] == manifest["finalSha256"]
    assert isinstance(request.get("sourceCommit"), str) and len(request["sourceCommit"]) == 40
print(json.dumps({"status": "PASS_SEALED_SOURCE", "version": manifest["name"],
                  "patches": len(manifest["patches"]), "htmlBytes": len(raw),
                  "htmlSha256": manifest["finalSha256"],
                  "studioCommands": "v1", "hostedTest": False, "ownerDeviceTest": False}, indent=2))
