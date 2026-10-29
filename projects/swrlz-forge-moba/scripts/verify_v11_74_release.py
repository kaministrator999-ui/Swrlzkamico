#!/usr/bin/env python3
"""Verify byte-sealed §E v11.74 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = '25ca54b95366258f3bc76912f90299aca42667c8f1938ea37a0a789da4399cc6'
assert manifest['name']=='§wyrl§ Engine v11.74'
assert manifest['finalArtifact']=='swyrl_engine_v11_74.html'
assert len(manifest['patches'])==106
assert manifest['patches'][-2:]==['patches/v11_73_gizmo_touch.py','patches/v11_74_mesh_groups.py']
assert manifest['finalBytes']==3056562 and manifest['finalSha256']==sha
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==3056562 and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_74_NONDESTRUCTIVE_MESH_GROUPS')==1
assert '<title>§wyrl§ Engine · Maker v11.74</title>' in html
assert 'ENGINE · MAKER v11.74' in html
assert 'v11.74 · reversible mesh assemblies' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.74'" in html
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
    'MODEL_ATELIER_CANONICAL_PROJECT'
):
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name']
assert source['patches']==manifest['patches'] and len(source['assets'])==43
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1174_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)
