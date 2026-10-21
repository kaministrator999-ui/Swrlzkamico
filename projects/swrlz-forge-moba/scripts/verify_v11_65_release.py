#!/usr/bin/env python3
"""Verify byte-sealed §E v11.65 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = 'a7e1514e34261d115472e6e6db68b88da8277d4e73e4e31cc19f9f99a138f38f'
assert manifest['name']=='§wyrl§ Engine v11.65'
assert manifest['finalArtifact']=='swyrl_engine_v11_65.html'
assert len(manifest['patches'])==97
assert manifest['patches'][-2:]==['patches/v11_64_version_smoke.py','patches/v11_65_selection_mesh_gizmos.py']
assert manifest['finalBytes']==3000400 and manifest['finalSha256']==sha
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==3000400 and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_65_SELECTION_MESH_GIZMOS')==1
assert '<title>§wyrl§ Engine · Maker v11.65</title>' in html
assert 'ENGINE · MAKER v11.65' in html
assert 'v11.65 · selection mesh gizmos' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.65'" in html
for token in (
    'function atelierMobileLayoutInstall(panel)',
    'atelierMobileSheetSize','atelierMobileHand','atelierMobileBrowseModes',
    'atelierContextWorkbench','atelierAdaptiveInstall','atelierToolDockInstall',
    'modelAtelierToolRail','modelAtelierInspectorDock','modelAtelierLassoPaintAtXYZ',
    'modelAtelierFaceCutoutApply','modelAtelierLODProtectUV','modelAtelierGroupViewportMode',
    'function atelierMeshControlsInstall(panel)','function atelierMeshJoin()',
    'function atelierMeshPrimitiveDensityGeometry(part)',
    'function atelierMeshGizmoDown(e)',
    'MODEL_ATELIER_CANONICAL_PROJECT'
):
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name']
assert source['patches']==manifest['patches'] and len(source['assets'])==43
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1165_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)
