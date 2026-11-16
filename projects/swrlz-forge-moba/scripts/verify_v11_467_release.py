#!/usr/bin/env python3
"""§E v11.467 native ring/arc kernel + full packaged source verification."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--request',action='store_true')
a=parser.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.467'
assert m['finalArtifact']=='swyrl_engine_v11_467.html'
assert len(m['patches'])==444 and m['patches'][-1]=='patches/v11_467_ring_arc_modeling.py'
assert isinstance(m['finalBytes'],int) and isinstance(m['finalSha256'],str)
for name in ['model_ring_kernel_v11_467.js','model_ring_bridge_v11_467.js','model_ring_ui_v11_467.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_ring_kernel_v11_467.mjs')],check=True)
out=Path(a.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode('utf8')
for token in [
 "window.SWRLZ_FORGE_BUILD={version:'v11.467'",
 '<title>§wyrl§ Engine · Maker v11.467</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_467_VR_GRIP_RELEASE',
 'SE466_RING_KERNEL_START','SE466_RING_BRIDGE_START','SE466_RING_UI_START',
 'SE465_NARROW_INSPECTOR_START','SE464_MODEL_VISUAL_POLISH_START',
 'SE436_SATCHEL_CAVITY_START',
 'modelAtelierWorkshopExtrudeScale','setRingAnchor','selectRing',
 'modelAtelierWorkshopPreview','modelAtelierWorkshopApply']:
 assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.467';source.version=11.466;")==5
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for k,v in [('sourceVersion',m['name']),('finalBytes',len(data)),('finalSha256',m['finalSha256']),('patches',m['patches'])]:
 assert receipt[k]==v,(k,receipt.get(k))
assert len(receipt['assets'])==77
for filename,r in receipt['assets'].items():
 b=(out/filename).read_bytes()
 assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],filename
if a.request:
 req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert req['releaseVersion']=='v11.467'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_467_VR_GRIP_RELEASE'
 assert req['target']=='kamiloki/swrlz-forge-moba'
 assert req['sourceIntegritySha256']==m['finalSha256']
 assert req['sourceCommit']
print(json.dumps({'status':'SOURCE_VERIFIED','version':'v11.467','sha256':m['finalSha256'],
 'bytes':m['finalBytes'],'patches':444,'assets':77,
 'phoneTested':False,'vrTested':False}),flush=True)
