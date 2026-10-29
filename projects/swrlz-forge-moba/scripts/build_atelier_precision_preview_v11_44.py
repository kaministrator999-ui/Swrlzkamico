#!/usr/bin/env python3
"""Build a separate, checksum-verified §E precision preview from sealed v11.20.

No production manifest edits, generated release patch or deployment request.
This candidate overlays the full cumulative v11.21–v11.36 tool implementation
and copies the existing sealed media/scene assets to an isolated preview folder.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/"patches/v11_21_vertex_sphere_brush_preview.py"
MANIFEST=ROOT/"source-manifest.json"
PREVIEW_MARKER="V11_21_VERTEX_SPHERE_BRUSH_PREVIEW"
REQUIRED=[
 "modelAtelierLassoStartFreehand",
 "modelAtelierViewportInsideEnter",
 "modelAtelierSculptBrushMirrorX",
 "modelAtelierSculptDensityPreview",
 "modelAtelierLassoGroupMove",
 "modelAtelierRefineLock",
 "modelAtelierRefineDuplicate",
 "modelAtelierReferencePin",
 "modelAtelierLassoBooleanApply",
 "modelAtelierLassoCurveApply",
 "modelAtelierLassoSegmentMove",
 "atelierLassoSegmentCandidate",
 "atelierLassoCompiledRegionMask",
 "atelierRefineCandidate",
 "modelAtelierLODPreview",
 "modelAtelierLODBake",
 "modelAtelierLODOBJ",
 "atelierTopologyGeometry",
 "modelAtelierFaceLandmarkApply",
 "atelierFaceLandmarkSculpt",
 "modelAtelierTopologySplit",
 "modelAtelierTopologyMove",
 "modelAtelierTopologyRemove",
 "atelierTopologyEditCandidate",
 "modelAtelierFaceContourApply",
 "atelierFaceContourRadius",
 "modelAtelierFaceLandmarkPick",
 "atelierFacePickAtReference",
 "modelAtelierRuntimeLODGenerate",
 "atelierRuntimeLODChoose",
 "atelierRuntimeLODUpdate",
 "modelAtelierTopologyAuditCheck",
 "modelAtelierTopologyAuditRepair",
 "atelierTopologyAudit",
 "atelierTopologyReorientCandidate",
]
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--output",required=True)
 args=parser.parse_args()
 target=Path(args.output).resolve()
 source=target.parent/("_sealed_v1120_"+target.name)
 manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
 assert manifest.get("name")=="§wyrl§ Engine v11.20"
 assert len(manifest["patches"])==90
 assert manifest["patches"][-1]=="patches/v11_20_anatomical_head.py"
 subprocess.run(["python",str(ROOT/"build_space.py"),"--output",str(source)],check=True)
 src=source/"index.html"
 original=src.read_text(encoding="utf-8")
 assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_20_ANATOMICAL_HEAD" in original
 assert hashlib.sha256(src.read_bytes()).hexdigest()==manifest["finalSha256"]
 if target.exists(): shutil.rmtree(target)
 shutil.copytree(source,target)
 result=runpy.run_path(str(PATCH))["apply"](original)
 assert PREVIEW_MARKER in result
 for marker in REQUIRED:
  assert marker in result, ("Precision preview missing control/implementation",marker)
 payload=result.encode("utf-8")
 (target/"index.html").write_bytes(payload)
 receipt=json.loads((source/"SOURCE.json").read_text(encoding="utf-8"))
 assert len(receipt["patches"])==90
 receipt.update(sourceVersion="v11.44-precision-preview",baseRelease="v11.20",
     previewOnly=True,sourceBranch="feature/atelier-topology-audit-v11-44",
     sourceCommit=os.environ.get("GITHUB_SHA","candidate"),
     finalSha256=hashlib.sha256(payload).hexdigest(),finalBytes=len(payload))
 receipt["patches"].append("patches/v11_21_vertex_sphere_brush_preview.py")
 (target/"SOURCE.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 script=result.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
 (target.parent/(target.name+"-module.mjs")).write_text(script,encoding="utf-8")
 print("V1144_FULL_PRECISION_PREVIEW_BUILT",receipt["finalSha256"],len(payload),
   len(receipt["patches"]),len(receipt["assets"]))
if __name__=="__main__":
 main()
