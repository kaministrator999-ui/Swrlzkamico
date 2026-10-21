#!/usr/bin/env python3
"""Verify byte-sealed §E v11.66 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = 'ab960990d91641c0a03c453181710ae2a6739c247a632e238e4aa1745e16e35f'
assert manifest['name']=='§wyrl§ Engine v11.66'
assert manifest['finalArtifact']=='swyrl_engine_v11_66.html'
assert len(manifest['patches'])==98
assert manifest['patches'][-2:]==['patches/v11_65_selection_mesh_gizmos.py','patches/v11_66_selection_ux.py']
assert manifest['finalBytes']==3008188 and manifest['finalSha256']==sha
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==3008188 and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_66_MESH_SELECTION_UX_REPAIR')==1
assert '<title>§wyrl§ Engine · Maker v11.66</title>' in html
assert 'ENGINE · MAKER v11.66' in html
assert 'v11.66 · cyber mesh gizmos' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.66'" in html
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
    'MODEL_ATELIER_CANONICAL_PROJECT'
):
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name']
assert source['patches']==manifest['patches'] and len(source['assets'])==43
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1166_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)
