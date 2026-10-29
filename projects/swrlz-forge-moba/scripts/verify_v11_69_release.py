#!/usr/bin/env python3
"""Verify byte-sealed §E v11.69 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = '6ed5ae18211945d86d2a73db45aadb173b377d656c57eeab6714105c26d8e471'
assert manifest['name']=='§wyrl§ Engine v11.69'
assert manifest['finalArtifact']=='swyrl_engine_v11_69.html'
assert len(manifest['patches'])==101
assert manifest['patches'][-2:]==['patches/v11_68_live_mesh_drag.py','patches/v11_69_live_touch_preview.py']
assert manifest['finalBytes']==3012114 and manifest['finalSha256']==sha
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==3012114 and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_69_DRAG_PREVIEW_RENDER')==1
assert '<title>§wyrl§ Engine · Maker v11.69</title>' in html
assert 'ENGINE · MAKER v11.69' in html
assert 'v11.69 · direct live drag rendering' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.69'" in html
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
    'MODEL_ATELIER_CANONICAL_PROJECT'
):
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name']
assert source['patches']==manifest['patches'] and len(source['assets'])==43
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1169_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)
