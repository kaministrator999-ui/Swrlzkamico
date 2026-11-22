#!/usr/bin/env python3
"""Verify the sealed §E v11.539 native startup pairing proof and Chat reference imports."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v11.539"
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_539_IMMERSIVE_SCULPT_LOAD"


def run(*command):
    subprocess.run(command, check=True)


def verify(output, manifest, check_request=False):
    assert manifest["name"] == "§wyrl§ Engine v11.539"
    assert manifest["finalArtifact"] == "swyrl_engine_v11_537.html"
    assert len(manifest["patches"]) == 516
    assert manifest["patches"][-2:] == [
        "patches/v11_538_smooth_uv_humanoid.py", "patches/v11_539_immersive_sculpt_load.py",
    ]
    index = output / "index.html"
    raw = index.read_bytes()
    assert raw == (output / "modeler.html").read_bytes()
    assert len(raw) == manifest["finalBytes"]
    assert hashlib.sha256(raw).hexdigest() == manifest["finalSha256"]
    html = raw.decode("utf8")
    for token in (MARKER, "window.SWRLZ_FORGE_BUILD={version:'v11.539'",
                  "<title>§wyrl§ Engine · Maker v11.539</title>",
                  "swrlz-forge-mesh-shape-edit-v1", "RESHAPE_REQUIRES_SEPARATE_BATCH",
                  "SE533_PROJECT_ACCOUNT_OPEN_START", "SE532_PROJECT_ACCOUNT_SAVE_RECEIPT_START",
                  "SE521_PERSISTENT_EDIT_JOURNAL_END",
                  "SE537_HUMANOID_END", "SE538_SMOOTH_HUMANOID_END", "SE539_IMMERSIVE_SCULPT_REPAIR_END", "smooth-witch-hat", "robotic-humanoid-mannequin",
                  "signIn:()=>se536PrepareLogin(),",
                  "id=\"se536RecoveryCode\"", "host.reference.import", "importFromChat:async offer=>"):
        assert token in html, token
    assert html.count(" source.engine='§wyrl§ Engine · Maker v11.539';source.version=11.539;") == 5
    run("node", "--check", str(ROOT / "runtime/robotic_humanoid_mannequin_v11_537.js"))
    run("node", "--check", str(ROOT / "runtime/model_vr_sculpt_preview_v11_539.js"))
    run("node", str(ROOT / "tests/model_vr_sculpt_preview_v11_539.cjs"))
    run("node", str(ROOT / "tests/robotic_humanoid_mannequin_v11_537.cjs"))
    run("node", "--check", str(ROOT / "runtime/chat_mesh_shape_edit_v11_534.js"))
    run(sys.executable, str(ROOT / "scripts/check_inline_js_syntax_v11_266.py"), str(index))
    for name in ("engine_native_login_reference_v11_537.cjs", "chat_mesh_shape_edit_v11_534.cjs", "project_account_receipt_v11_532.cjs", "project_account_open_v11_533.cjs"):
        run("node", str(ROOT / "tests" / name), str(index))
    for name in ("model_project_edit_journal_v11_521.cjs", "engine_cloud_revision_cache_v11_518.cjs"):
        run("node", str(ROOT / "tests" / name))

    receipt = json.loads((output / "SOURCE.json").read_text("utf8"))
    for key, value in (("sourceVersion", manifest["name"]), ("finalBytes", len(raw)),
                       ("finalSha256", manifest["finalSha256"]), ("patches", manifest["patches"])):
        assert receipt[key] == value, key
    assert len(receipt["assets"]) == 78
    for rel, expected in receipt["assets"].items():
        asset = (output / rel).read_bytes()
        assert len(asset) == expected["bytes"] and hashlib.sha256(asset).hexdigest() == expected["sha256"], rel
    if check_request:
        request = json.loads((ROOT / "DEPLOY_REQUEST.json").read_text("utf8"))
        assert request["releaseVersion"] == VERSION and request["target"] == "kamiloki/swrlz-forge-moba"
        assert request["deployMarker"] == MARKER and request["sourceIntegritySha256"] == manifest["finalSha256"]
        assert len(request["sourceCommit"]) == 40
    print("SE539_SOURCE_VERIFIED", json.dumps({"version": VERSION, "patches": 516, "bytes": len(raw),
          "sha256": manifest["finalSha256"], "assets": len(receipt["assets"]), "liveAccountWriteTested": False}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--request", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    manifest = json.loads((ROOT / "source-manifest.json").read_text("utf8"))
    run(sys.executable, str(ROOT / "build_space.py"), "--output", str(output))
    verify(output, manifest, args.request)


if __name__ == "__main__":
    main()
