#!/usr/bin/env python3
"""Rebuild and seal §E v11.483 Sorting Hat from the actual full patch lineage.

Only this preparation job writes the new source-integrity SHA. It never guesses
a digest and never silently publishes; a later owner-approved deployment-request
commit explicitly names this completed source commit and SHA.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "source-manifest.json"
manifest = json.loads(manifest_path.read_text("utf8"))
assert manifest["name"] == "§wyrl§ Engine v11.482", manifest["name"]
assert len(manifest["patches"]) == 459
assert manifest["patches"][-1] == "patches/v11_482_geometric_ring_height.py"
assert manifest["finalSha256"] == "dc7f9acad42d387d81935b20971aaf438d2a7c26990bf9bc3d00d2edd52eea36"
assert (ROOT/"runtime/sorting_hat_starter_v11_483.js").is_file()
assert (ROOT/"patches/v11_483_sorting_hat_starter.py").is_file()
assert (ROOT/"scenes/model-atelier-sorting-hat.swyrl.json").is_file()

subprocess.run([sys.executable,str(ROOT/"tests/sorting_hat_scene_v11_483.py")],check=True)
subprocess.run(["node","--check",str(ROOT/"runtime/sorting_hat_starter_v11_483.js")],check=True)

manifest["name"] = "§wyrl§ Engine v11.483"
manifest["finalArtifact"] = "swyrl_engine_v11_483.html"
manifest["patches"].append("patches/v11_483_sorting_hat_starter.py")
# Unsealed temporary state never leaves this workflow checkout. The builder
# must actually regenerate HTML through all 460 patches before the real hash
# and byte count are written back, then build again and verify exact equality.
manifest["finalBytes"] = None
manifest["finalSha256"] = None
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n","utf8")

with tempfile.TemporaryDirectory(prefix="se483-build-") as folder:
    out = Path(folder)/"package"
    subprocess.run([sys.executable,str(ROOT/"build_space.py"),"--output",str(out)],check=True)
    raw = (out/"index.html").read_bytes()
    assert raw == (out/"modeler.html").read_bytes()
    assert b"SE483_SORTING_HAT_END" in raw
    assert b'data-project-template="sorting-hat"' in raw
    manifest["finalBytes"] = len(raw)
    manifest["finalSha256"] = hashlib.sha256(raw).hexdigest()
    manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n","utf8")
    subprocess.run([sys.executable,str(ROOT/"scripts/verify_v11_483_release.py"),
                    "--output",str(out)],check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/package_static_delivery_v11_483.py"),
                    "--output",str(out)],check=True)
    subprocess.run(["node","--check",str(out/"swrlz-engine-v11.483.js")],check=True)
    receipt = json.loads((out/"SOURCE.json").read_text("utf8"))
    assert receipt["finalSha256"] == manifest["finalSha256"]
    assert receipt["staticDelivery"]["verifiedSourceSha256"] == manifest["finalSha256"]
    assert receipt["assets"]["scenes/model-atelier-sorting-hat.swyrl.json"]["bytes"] > 300000
    print(json.dumps({"status":"SE483_SOURCE_SEALED",
                      "version":manifest["name"],
                      "sourceSha256":manifest["finalSha256"],
                      "sourceBytes":manifest["finalBytes"],
                      "patches":len(manifest["patches"]),
                      "assets":len(receipt["assets"]),
                      "staticDelivery":receipt["staticDelivery"]["module"]}),flush=True)
