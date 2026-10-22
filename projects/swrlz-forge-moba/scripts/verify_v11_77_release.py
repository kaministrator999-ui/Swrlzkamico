#!/usr/bin/env python3
"""Verify byte-sealed §E v11.77 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = manifest['finalSha256']
assert manifest['name']=='§wyrl§ Engine v11.77'
assert manifest['finalArtifact']=='swyrl_engine_v11_77.html'
assert len(manifest['patches'])==109
assert manifest['patches'][-2:]==['patches/v11_76_desktop_modeling.py','patches/v11_77_comet_courier.py']
assert manifest['finalBytes']>3091496 and len(sha)==64
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==manifest['finalBytes'] and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_77_COMET_COURIER_MODEL_PROJECT')==1
assert '<title>§wyrl§ Engine · Maker v11.77</title>' in html
assert 'ENGINE · MAKER v11.77' in html
assert 'v11.77 · textured model projects' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.77'" in html
for token in (
    'function atelierMobileLayoutInstall(panel)',
    'atelierMobileSheetSize','atelierMobileHand','atelierMobileBrowseModes',
    'atelierContextWorkbench','atelierAdaptiveInstall','atelierToolDockInstall',
    'modelAtelierToolRail','modelAtelierInspectorDock','modelAtelierLassoPaintAtXYZ',
    'modelAtelierFaceCutoutApply','modelAtelierLODProtectUV','modelAtelierGroupViewportMode',
    'function atelierMeshControlsInstall(panel)','function atelierMeshJoin()',
    'function atelierMeshPrimitiveDensityGeometry(part)',
    'function atelierMeshGizmoDown(e)',
    'function atelierMeshDialogInstall()',
    'function atelierMeshHistoryShortcut(backward)',
    'Native Model Atelier already renders a selection BoxHelper',
    'function atelierMeshTransformOnlyCommit(records)',
    'function atelierMeshRestoreLiveTransforms(records)',
    'function atelierMeshLiveDragPreview(records)',
    'function atelierMeshSelectFast()',
    'window.SWYRL_ENGINE_MESH_DRAG_DIAGNOSTICS',
    'function atelierMeshLiveDragPreview(records)',
    'function atelierMeshPrecisionInstall(strip)',
    'function atelierViewportTopArrange(panel)',
    'function atelierArcBuild(root)',
    'function atelierArcMove(e)',
    'function atelierArcInstall(strip)',
    'function atelierArcCalibratedBuild(root)',
    'function atelierArcCalibratedPointerAngle(d,e)',
    'function atelierArcCalibratedDown(e)',
    'function atelierMeshPaintModeImmediately()',
    'function atelierArcPickOnScreen(e)',
    'function atelierArcEasyDown(e)',
    'function atelierGroupCreate()',
    'function atelierGroupUpdateMembers()',
    'function atelierGroupsInstall(panel)',
    'function atelierComponentInstall()',
    'function atelierComponentHit(e)',
    'function atelierComponentGizmoDown(e)',
    'function atelierComponentRegionPick(points,tool)',
    'function atelierComponentCommit(d)',
    'function atelierDesktopMeshMotion(e)',
    'function atelierDesktopBoundedAmount(d,raw)',
    'function atelierDesktopWireRefresh()',
    'function atelierDesktopWireInstall(panel)',
    'MODEL_ATELIER_CANONICAL_PROJECT'
):
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name']
assert source['patches']==manifest['patches'] and len(source['assets'])==46
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1177_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)

# Freeze historical project/asset/source lineage and measure the actual 4K image files.
baseline=json.loads((root/'tests/comet_courier_baseline_v11_76.json').read_text())
for path,digest in baseline['sources'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
for path,meta in baseline['assets'].items():assert source['assets'][path]==meta,path
original=html.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1]
_,end=json.JSONDecoder().raw_decode(original)
assert hashlib.sha256(original[:end].encode()).hexdigest()==baseline['originalCanonicalSha256']
new=json.loads((root/'scenes/model-atelier-comet-courier-v11-77.swyrl.json').read_text())
assert new['project']['canonicalId']=='comet-courier' and new['project']['kind']=='model-atelier'
parts=new['project']['modelAtelier']['parts'];assert len(parts)>=90 and len(parts)<180
assert len(new['project']['modelAtelier']['meshGroups'])==6
assert sum('textureBinding' in p for p in parts)>80
for token in ['function atelierCourierGLB()','function atelierCourierBindingValid(p)','data-project-template="comet-courier"','data-project-template="blank-model"','modelAtelierAtlasApply']:assert token in html,token
normal=(out/'assets/models/comet-courier/astra-normal-4k.png').read_bytes()
assert normal[:8]==b'\x89PNG\r\n\x1a\n'
assert int.from_bytes(normal[16:20],'big')==4096 and int.from_bytes(normal[20:24],'big')==4096
color=(out/'assets/models/comet-courier/astra-basecolor-4k.jpg').read_bytes();at=2;found=False
while at<len(color):
 if color[at]!=255:at+=1;continue
 marker=color[at+1];at+=2
 if marker in [216,217]:continue
 size=int.from_bytes(color[at:at+2],'big')
 if marker in [192,193,194]:
  assert int.from_bytes(color[at+3:at+5],'big')==4096 and int.from_bytes(color[at+5:at+7],'big')==4096;found=True;break
 at+=size
assert found
print('COURIER_NEW_PROJECT_4K_TEXTURES_AND_HISTORICAL_PRESERVATION_PASS',len(parts),flush=True)
