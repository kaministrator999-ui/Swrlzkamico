#!/usr/bin/env python3
"""Verify the sealed §E v11.542 native startup pairing proof and Chat reference imports."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VERSION = "v11.542"
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_542_HUMANOID_RELAXED_UV_ATLAS"


def run(*command):
    subprocess.run(command, check=True)


def verify(output, manifest, check_request=False):
    assert manifest["name"] == "§wyrl§ Engine v11.542"
    assert manifest["finalArtifact"] == "swyrl_engine_v11_541.html"
    assert len(manifest["patches"]) == 519
    assert manifest["patches"][-2:] == [
        "patches/v11_541_humanoid_starter_category.py", "patches/v11_542_humanoid_relaxed_uv.py",
    ]
    index = output / "index.html"
    raw = index.read_bytes()
    assert raw == (output / "modeler.html").read_bytes()
    assert len(raw) == manifest["finalBytes"]
    assert hashlib.sha256(raw).hexdigest() == manifest["finalSha256"]
    html = raw.decode("utf8")
    for token in (MARKER, "window.SWRLZ_FORGE_BUILD={version:'v11.542'",
                  "<title>§wyrl§ Engine · Maker v11.542</title>",
                  "swrlz-forge-mesh-shape-edit-v1", "RESHAPE_REQUIRES_SEPARATE_BATCH",
                  "SE533_PROJECT_ACCOUNT_OPEN_START", "SE532_PROJECT_ACCOUNT_SAVE_RECEIPT_START",
                  "SE521_PERSISTENT_EDIT_JOURNAL_END",
                  "SE537_HUMANOID_END", "SE538_SMOOTH_HUMANOID_END", "SE539_IMMERSIVE_SCULPT_REPAIR_END", "SE540_HUMANOID_HANDS_END", "V11_542_HUMANOID_RELAXED_UV_ATLAS",
                  "se537OpenMannequin=se538OpenHumanoid", "se537OpenMannequin=se540OpenHumanoid", "se537OpenMannequin=se542OpenHumanoid", "SE542_HUMANOID_UV_GUARD_END", "robotic-humanoid-mannequin",
                  "signIn:()=>se536PrepareLogin(),",
                  "id=\"se536RecoveryCode\"", "host.reference.import", "importFromChat:async offer=>"):
        assert token in html, token
    assert html.count(" source.engine='§wyrl§ Engine · Maker v11.542';source.version=11.542;") == 5
    run("node", "--check", str(ROOT / "runtime/robotic_humanoid_mannequin_v11_537.js"))
    run("node", str(ROOT / "tests/robotic_humanoid_mannequin_v11_537.cjs"))
    run("node", "--check", str(ROOT / "runtime/model_vr_sculpt_preview_v11_539.js"))
    run("node", str(ROOT / "tests/model_vr_sculpt_preview_v11_539.cjs"))
    run("node", "--check", str(ROOT / "runtime/smooth_humanoid_starter_v11_538.js"))
    run(sys.executable, str(ROOT / "scripts/check_futuristic_humanoid_v11_538.py"))
    run("node", str(ROOT / "tests/smooth_humanoid_starter_v11_538.cjs"))
    run("node", "--check", str(ROOT / "runtime/futuristic_humanoid_five_digit_v11_540.js"))
    run(sys.executable, str(ROOT / "scripts/check_futuristic_humanoid_v11_540.py"))
    run("node", str(ROOT / "tests/futuristic_humanoid_five_digit_v11_540.cjs"))
    run("node", str(ROOT / "tests/humanoid_starter_category_v11_542.cjs"), str(index))
    run("node", "--check", str(ROOT / "runtime/humanoid_uv_starter_v11_542.js"))
    run("node", "--check", str(ROOT / "runtime/humanoid_uv_guard_v11_542.js"))
    run(sys.executable, str(ROOT / "scripts/check_humanoid_uv_atlas_v11_542.py"))
    run("node", str(ROOT / "tests/humanoid_uv_starter_v11_542.cjs"))
    run("node", "--check", str(ROOT / "runtime/chat_mesh_shape_edit_v11_534.js"))
    run(sys.executable, str(ROOT / "scripts/check_inline_js_syntax_v11_266.py"), str(index))
    for name in ("engine_native_login_reference_v11_542.cjs", "chat_mesh_shape_edit_v11_534.cjs", "project_account_receipt_v11_532.cjs", "project_account_open_v11_533.cjs"):
        run("node", str(ROOT / "tests" / name), str(index))
    for name in ("model_project_edit_journal_v11_521.cjs", "engine_cloud_revision_cache_v11_518.cjs"):
        run("node", str(ROOT / "tests" / name))

    receipt = json.loads((output / "SOURCE.json").read_text("utf8"))
    for key, value in (("sourceVersion", manifest["name"]), ("finalBytes", len(raw)),
                       ("finalSha256", manifest["finalSha256"]), ("patches", manifest["patches"])):
        assert receipt[key] == value, key
    assert len(receipt["assets"]) == 82
    for rel, expected in receipt["assets"].items():
        asset = (output / rel).read_bytes()
        assert len(asset) == expected["bytes"] and hashlib.sha256(asset).hexdigest() == expected["sha256"], rel
    if check_request:
        request = json.loads((ROOT / "DEPLOY_REQUEST.json").read_text("utf8"))
        assert request["releaseVersion"] == VERSION and request["target"] == "kamiloki/swrlz-forge-moba"
        assert request["deployMarker"] == MARKER and request["sourceIntegritySha256"] == manifest["finalSha256"]
        assert len(request["sourceCommit"]) == 40
    print("SE542_SOURCE_VERIFIED", json.dumps({"version": VERSION, "patches": 519, "bytes": len(raw),
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
