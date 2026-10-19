#!/usr/bin/env python3
"""Production v11.59 source verifier and extracted JS parser input."""
import argparse,hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument("--output",required=True)
args=ap.parse_args()
out=Path(args.output).resolve()
manifest=json.loads((root/"source-manifest.json").read_text())
assert manifest["name"]=="§wyrl§ Engine v11.59"
assert len(manifest["patches"])==91
assert manifest["patches"][-1]=="patches/v11_59_precision_model_atelier.py"
assert manifest["finalBytes"]==2926239
assert manifest["finalSha256"]=="515478b91b41356f2f74c6ad13318be1e24144da04e0de8bc6875c9608a7e23b"
subprocess.run(["python",str(root/"build_space.py"),"--output",str(out)],check=True)
payload=(out/"index.html").read_bytes()
assert len(payload)==manifest["finalBytes"]
assert hashlib.sha256(payload).hexdigest()==manifest["finalSha256"]
s=payload.decode("utf-8")
assert s.count("SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER")==1
assert "<title>§wyrl§ Engine · Maker v11.59</title>" in s
assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_21_VERTEX_SPHERE_BRUSH_PREVIEW" not in s
for token in ("visible-geodesic","modelAtelierReferenceFloatOpen","modelAtelierLassoPaintAtXYZ",
              "modelAtelierFaceCutoutApply","modelAtelierGroupViewportMode",
              "modelAtelierLODProtectUV","modelAtelierSculptBrushCurveEnabled"):
 assert token in s,token
receipt=json.loads((out/"SOURCE.json").read_text())
assert len(receipt["patches"])==91 and len(receipt["assets"])==43
assert receipt["finalSha256"]==manifest["finalSha256"]
module=s.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+"-module.mjs").write_text(module,encoding="utf-8")
print("V1159_PRODUCTION_RELEASE_SOURCE_VERIFIED",len(payload),hashlib.sha256(payload).hexdigest(),
      len(receipt["patches"]),len(receipt["assets"]))
