#!/usr/bin/env python3
"""Production v11.62 source verifier and extracted JS parser input."""
import argparse,hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument("--output",required=True)
args=ap.parse_args()
out=Path(args.output).resolve()
manifest=json.loads((root/"source-manifest.json").read_text())
assert manifest["name"]=="§wyrl§ Engine v11.62"
assert len(manifest["patches"])==94
assert manifest["patches"][-1]=="patches/v11_62_mobile_tool_layout.py"
assert manifest["finalBytes"]==2967658
assert manifest["finalSha256"]=="9c8217359926e76c6140439a0f58343eee7bfb736b396d1d9daf667ce7dee9a4"
subprocess.run(["python",str(root/"build_space.py"),"--output",str(out)],check=True)
payload=(out/"index.html").read_bytes()
assert len(payload)==manifest["finalBytes"]
assert hashlib.sha256(payload).hexdigest()==manifest["finalSha256"]
s=payload.decode("utf-8")
assert s.count("SWYRL_ENGINE_DEPLOY_MARKER: V11_62_MOBILE_ADAPTIVE_TOOL_LAYOUT")==1
assert "<title>§wyrl§ Engine · Maker v11.62</title>" in s
assert "ENGINE · MAKER v11.62" in s
assert "v11.62 · mobile adaptive Model Atelier tools" in s
assert "window.SWRLZ_FORGE_BUILD={version:'v11.62'" in s
assert "ENGINE · MAKER v11.20" not in s
assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_21_VERTEX_SPHERE_BRUSH_PREVIEW" not in s
for token in ("atelierMobileOpenTools","atelierMobileCollapse","atelierMobileExpand","atelier-mobile-tools","atelierContextWorkbench","atelierAdaptiveInstall","atelierContextOperations","atelierContextFields","modelAtelierToolRail","modelAtelierInspectorDock","atelierToolDockInstall","visible-geodesic","modelAtelierReferenceFloatOpen","modelAtelierLassoPaintAtXYZ",
              "modelAtelierFaceCutoutApply","modelAtelierGroupViewportMode",
              "modelAtelierLODProtectUV","modelAtelierSculptBrushCurveEnabled"):
 assert token in s,token
receipt=json.loads((out/"SOURCE.json").read_text())
assert len(receipt["patches"])==94 and len(receipt["assets"])==43
assert receipt["finalSha256"]==manifest["finalSha256"]
module=s.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+"-module.mjs").write_text(module,encoding="utf-8")
print("V1162_PRODUCTION_RELEASE_SOURCE_VERIFIED",len(payload),hashlib.sha256(payload).hexdigest(),
      len(receipt["patches"]),len(receipt["assets"]))
