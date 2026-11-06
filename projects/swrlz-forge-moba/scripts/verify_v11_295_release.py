#!/usr/bin/env python3
"""Verify the sealed plain Chat loft shading repair and preserved character tools."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_295_CHAT_LOFT_SURFACE_NORMALS"
THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.169.0/+esm"
THREE_BYTES = 684391
THREE_SHA256 = "260fdf7db2ecda0e726a82e37c829cdeb974015c9a4304ea9c51177b2c8b2c1a"


def verify_loft_geometry(html_path, module_path=None):
    # Exercise actual Three.js BufferGeometry/normal generation. Keep this test
    # dependency outside the HF package and pin its exact app-version bytes.
    if module_path is not None:
        module = Path(module_path).resolve()
        data = module.read_bytes()
        assert len(data) == THREE_BYTES and hashlib.sha256(data).hexdigest() == THREE_SHA256
        subprocess.run(["node", str(ROOT / "tests/chat_loft_surface_normals_v11_295.mjs"),
                        str(html_path), str(module)], check=True)
        return
    with tempfile.TemporaryDirectory(prefix="swrlz-three-169-") as directory:
        with urllib.request.urlopen(THREE_URL, timeout=30) as response:
            data = response.read(THREE_BYTES + 1)
        assert len(data) == THREE_BYTES and hashlib.sha256(data).hexdigest() == THREE_SHA256
        module = Path(directory) / "three-0.169.0.mjs"
        module.write_bytes(data)
        subprocess.run(["node", str(ROOT / "tests/chat_loft_surface_normals_v11_295.mjs"),
                        str(html_path), str(module)], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--request", action="store_true")
    parser.add_argument("--three-module", help="Optional local copy of the exact pinned app Three ESM")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "source-manifest.json").read_text())
    assert manifest["name"] == "§wyrl§ Engine v11.295"
    assert manifest["finalArtifact"] == "swyrl_engine_v11_295.html"
    assert len(manifest["patches"]) == 326
    assert manifest["patches"][-3:] == ["patches/v11_293_chat_character_tools.py", "patches/v11_294_vanguard_socket_loader_fix.py", "patches/v11_295_chat_loft_surface_normals.py"]
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
        THREE_URL,
        "<title>§wyrl§ Engine · Maker v11.295</title>",
        "window.SWRLZ_FORGE_BUILD={version:'v11.295'",
        "SE295_CHAT_LOFT_SURFACE_NORMALS_START",
        "SE295_CHAT_LOFT_SURFACE_NORMALS_END",
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
    assert html.count("source.engine='§wyrl§ Engine · Maker v11.295';source.version=11.295;") == 3
    assert html.count("SE295_CHAT_LOFT_SURFACE_NORMALS_START") == 1
    assert html.count("SE295_CHAT_LOFT_SURFACE_NORMALS_END") == 1
    assert html.count("function seChatAtelierApply(op)") == 1
    assert html.count("model.parts=parts;model.meshGroups=[];model.assemblies=null;") == 1
    assert html.count("function applyBatch(payload)") == 1
    assert html.count("renderer.setAnimationLoop(tick);") == 1
    subprocess.run([sys.executable, str(ROOT / "scripts/check_inline_js_syntax_v11_266.py"),
                    str(out / "index.html")], check=True)
    subprocess.run(["node", str(ROOT / "tests/chat_character_tools_v11_293.mjs"),
                    str(out / "index.html")], check=True)
    verify_loft_geometry(out / "index.html", args.three_module)
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
        assert request["releaseVersion"] == "v11.295"
        assert request["deployMarker"] == MARKER
        assert request["sourceIntegritySha256"] == manifest["finalSha256"]
        assert len(request["sourceCommit"]) == 40
    print(json.dumps({"status": "SEALED_SOURCE_VERIFIED", "version": "v11.295",
                      "patches": 326, "htmlBytes": len(raw),
                      "sha256": manifest["finalSha256"], "assets": 71,
                      "ownerDeviceAcceptance": False}, indent=2))


if __name__ == "__main__":
    main()
