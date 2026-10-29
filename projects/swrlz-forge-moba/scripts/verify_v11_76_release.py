#!/usr/bin/env python3
"""Verify byte-sealed §E v11.76 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = 'ae0764bcdaef131a8d404b43ca20b4a3b6ed9bad66897709919b6f3f1bccf1ef'
assert manifest['name']=='§wyrl§ Engine v11.76'
assert manifest['finalArtifact']=='swyrl_engine_v11_76.html'
assert len(manifest['patches'])==108
assert manifest['patches'][-2:]==['patches/v11_75_component_edit.py','patches/v11_76_desktop_modeling.py']
assert manifest['finalBytes']==3091496 and manifest['finalSha256']==sha
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==3091496 and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_76_DESKTOP_MODELING_REPAIR')==1
assert '<title>§wyrl§ Engine · Maker v11.76</title>' in html
assert 'ENGINE · MAKER v11.76' in html
assert 'v11.76 · precise desktop modeling' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.76'" in html
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
assert source['patches']==manifest['patches'] and len(source['assets'])==43
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1176_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)
