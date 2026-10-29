#!/usr/bin/env python3
"""Verify byte-sealed §E v11.71 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = '44ae1de39f81874ccf2a06cfae8e067b06633053656283562523579850034c6b'
assert manifest['name']=='§wyrl§ Engine v11.71'
assert manifest['finalArtifact']=='swyrl_engine_v11_71.html'
assert len(manifest['patches'])==103
assert manifest['patches'][-2:]==['patches/v11_70_precision_ui.py','patches/v11_71_rotation_ruler.py']
assert manifest['finalBytes']==3029622 and manifest['finalSha256']==sha
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==3029622 and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_71_ARC_ROTATION_RULER')==1
assert '<title>§wyrl§ Engine · Maker v11.71</title>' in html
assert 'ENGINE · MAKER v11.71' in html
assert 'v11.71 · arc rotation ruler' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.71'" in html
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
    'MODEL_ATELIER_CANONICAL_PROJECT'
):
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name']
assert source['patches']==manifest['patches'] and len(source['assets'])==43
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1171_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)
