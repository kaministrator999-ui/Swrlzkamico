#!/usr/bin/env python3
"""Verify the sealed Chat character-tool engine package and native JS syntax."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_294_VANGUARD_SOCKET_LOAD_FIX"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--request", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "source-manifest.json").read_text())
    assert manifest["name"] == "§wyrl§ Engine v11.294"
    assert manifest["finalArtifact"] == "swyrl_engine_v11_294.html"
    assert len(manifest["patches"]) == 325
    assert manifest["patches"][-2:] == ["patches/v11_293_chat_character_tools.py", "patches/v11_294_vanguard_socket_loader_fix.py"]
    assert isinstance(manifest["finalBytes"], int) and manifest["finalBytes"] > 0
    assert len(manifest["finalSha256"]) == 64
    out = Path(args.output).resolve()
    subprocess.run([sys.executable, str(ROOT / "build_space.py"), "--output", str(out)], check=True)
    raw = (out / "index.html").read_bytes()
    assert raw == (out / "modeler.html").read_bytes()
    assert len(raw) == manifest["finalBytes"]
    assert hashlib.sha256(raw).hexdigest() == manifest["finalSha256"]
    html = raw.decode()
    for term in (
        MARKER,
        "<title>§wyrl§ Engine · Maker v11.294</title>",
        "window.SWRLZ_FORGE_BUILD={version:'v11.294'",
        "host.progress",
        "swrlz-forge-mesh-tools-v2",
        "function seChatAtelierApply(op)",
        "function validateOperation(op,ctx)",
        "function applyBatch(payload)",
        "function atelierTopologyValid(part)",
        "window.SWYRL_ENGINE_VIEWPORT_NERD_STATS_274=Object.freeze",
        "function updateContinuousSwirl(flow,cfg,rec,origin,dt)",
        "swrlz-forge-studio-commands-v1",
        "window.SWYRL_ENGINE_QUEST_LEFT_WRIST_STATS_276=Object.freeze",
        "window.SWYRL_ENGINE_CURVE_LIVE_277=api;",
        "window.SWYRL_ENGINE_QUEST_MENU_CADENCE_278=Object.freeze",
        "window.SWYRL_ENGINE_BLANK_VR_HANDS=Object.freeze",
        "window.SWYRL_ENGINE_MAGE_SPELL_LAB=Object.freeze",
        "se280MageSpellLibrary",
        "window.SWYRL_ENGINE_ROCK_HAND=Object.freeze",
        "function se281RockScene(){",
        "window.SWYRL_ENGINE_ROCK_CLIFF_HAND=Object.freeze",
        "function se282FullRockScene(){",
        "se281RockScene=se282FullRockScene;",
        "function se292WristMossKnuckleMaterial(part){",
        "window.SWYRL_ENGINE_PROJECT_HUB_285=Object.freeze",
        "Hooded Vanguard",
        "model.parts=parts;model.meshGroups=[];model.assemblies=null;",
    ):
        assert term in html, term
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.294';source.version=11.293;") == 3
    assert html.count("function seChatAtelierApply(op)") == 1
    assert html.count("model.parts=parts;model.meshGroups=[];model.assemblies=null;") == 1
    assert html.count("function applyBatch(payload)") == 1
    assert html.count("renderer.setAnimationLoop(tick);") == 1
    subprocess.run([sys.executable, str(ROOT / "scripts/check_inline_js_syntax_v11_266.py"),
                    str(out / "index.html")], check=True)
    subprocess.run(["node", str(ROOT / "tests/chat_character_tools_v11_293.mjs"),
                    str(out / "index.html")], check=True)
    receipt = json.loads((out / "SOURCE.json").read_text())
    for field in ("finalSha256", "finalBytes", "patches"):
        assert receipt[field] == manifest[field], field
    assert receipt["sourceVersion"] == manifest["name"]
    assert len(receipt["assets"]) == 71
    for name, metadata in receipt["assets"].items():
        data = (out / name).read_bytes()
        assert len(data) == metadata["bytes"], name
        assert hashlib.sha256(data).hexdigest() == metadata["sha256"], name
    if args.request:
        request = json.loads((ROOT / "DEPLOY_REQUEST.json").read_text())
        assert request["releaseVersion"] == "v11.294"
        assert request["deployMarker"] == MARKER
        assert request["sourceIntegritySha256"] == manifest["finalSha256"]
        assert len(request["sourceCommit"]) == 40
    print(json.dumps({"status": "SEALED_SOURCE_VERIFIED", "version": "v11.294",
                      "patches": 324, "htmlBytes": len(raw),
                      "sha256": manifest["finalSha256"], "assets": 71,
                      "ownerDeviceAcceptance": False}, indent=2))


if __name__ == "__main__":
    main()
