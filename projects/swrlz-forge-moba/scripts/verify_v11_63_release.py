#!/usr/bin/env python3
"""Verify byte-sealed §E v11.63 release candidate (not a deploy action)."""
import argparse, hashlib, json, subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
manifest = json.loads((root/'source-manifest.json').read_text())
sha = '6adbda8d53e0b11fe6e98ae59605176362e0fc2b159c558e52087e96ed1274ec'
assert manifest['name']=='§wyrl§ Engine v11.63'
assert manifest['finalArtifact']=='swyrl_engine_v11_63.html'
assert len(manifest['patches'])==95
assert manifest['patches'][-2:]==['patches/v11_62_mobile_adaptive.py','patches/v11_63_version_smoke.py']
assert manifest['finalBytes']==2976568 and manifest['finalSha256']==sha
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert len(data)==2976568 and hashlib.sha256(data).hexdigest()==sha
html=data.decode('utf-8')
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_63_VERSION_SMOKE_TEST')==1
assert '<title>§wyrl§ Engine · Maker v11.63</title>' in html
assert 'ENGINE · MAKER v11.63' in html
assert 'v11.63 · mobile adaptive Model Atelier tools' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.63'" in html
for token in (
    'function atelierMobileLayoutInstall(panel)',
    'atelierMobileSheetSize','atelierMobileHand','atelierMobileBrowseModes',
    'atelierContextWorkbench','atelierAdaptiveInstall','atelierToolDockInstall',
    'modelAtelierToolRail','modelAtelierInspectorDock','modelAtelierLassoPaintAtXYZ',
    'modelAtelierFaceCutoutApply','modelAtelierLODProtectUV','modelAtelierGroupViewportMode',
    'MODEL_ATELIER_CANONICAL_PROJECT'
):
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name']
assert source['patches']==manifest['patches'] and len(source['assets'])==43
assert source['finalSha256']==sha and source['finalBytes']==len(data)
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module,encoding='utf-8')
print('SWRLZ_V1163_RELEASE_VERIFIED',len(data),sha,len(source['patches']),len(source['assets']),flush=True)
