#!/usr/bin/env python3
"""Verify byte-sealed §E v11.67 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = 'a2122de3a296da3319de5d861875f7c3efd4663d714b31820d4e27acf5ca8017'
assert manifest['name']=='§wyrl§ Engine v11.67'
assert manifest['finalArtifact']=='swyrl_engine_v11_67.html'
assert len(manifest['patches'])==99
assert manifest['patches'][-2:]==['patches/v11_66_selection_ux.py','patches/v11_67_mesh_transform_perf.py']
assert manifest['finalBytes']==3009500 and manifest['finalSha256']==sha
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==3009500 and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_67_MESH_TRANSFORM_PERFORMANCE')==1
assert '<title>§wyrl§ Engine · Maker v11.67</title>' in html
assert 'ENGINE · MAKER v11.67' in html
assert 'v11.67 · fluid mesh transforms' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.67'" in html
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
    'MODEL_ATELIER_CANONICAL_PROJECT'
):
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name']
assert source['patches']==manifest['patches'] and len(source['assets'])==43
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1167_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)
