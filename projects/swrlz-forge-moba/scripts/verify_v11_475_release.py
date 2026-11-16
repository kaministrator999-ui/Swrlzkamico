#!/usr/bin/env python3
"""Verify the native progressive Model Studio release and exact source receipt."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser()
a.add_argument('--output',required=True)
a.add_argument('--request',action='store_true')
args=a.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.475'
assert m['finalArtifact']=='swyrl_engine_v11_475.html'
assert len(m['patches'])==452 and m['patches'][-1]=='patches/v11_475_progressive_rail_visibility.py'
assert isinstance(m['finalBytes'],int) and isinstance(m['finalSha256'],str)
for f in ('model_progressive_rail_fix_v11_475.js','model_progressive_tools_v11_474.js','model_ring_kernel_v11_466.js',
          'model_ring_ui_v11_466.js','model_tool_rail_fold_v11_473.js'):
 subprocess.run(['node','--check',str(ROOT/'runtime'/f)],check=True)
for f in ('model_progressive_rail_fix_v11_475.mjs','model_progressive_tools_v11_474.mjs','model_ring_kernel_v11_466.mjs',
          'model_tool_rail_fold_v11_473.mjs'):
 subprocess.run(['node',str(ROOT/'tests'/f)],check=True)
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
assert len(data)==m['finalBytes']
assert hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode('utf8')
for token in (
 "window.SWRLZ_FORGE_BUILD={version:'v11.475'",
 '<title>§wyrl§ Engine · Maker v11.475</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_475_PROGRESSIVE_RAIL_VISIBILITY',
 'SE474_PROGRESSIVE_MODEL_TOOLS_START',
 'SE474_PROGRESSIVE_MODEL_TOOLS_STYLES_START',
 'SE475_PROGRESSIVE_RAIL_VISIBILITY_START','SE475_PROGRESSIVE_RAIL_VISIBILITY_STYLES_START',
 'SE473_MODEL_TOOL_RAIL_FOLD_START',
 'SE466_RING_KERNEL_START','SE466_RING_UI_START','SE466_RING_BRIDGE_START',
 'SE452_NATIVE_FACE_FLYOUTS_START','SE430_MODEL_BEGINNER_UI_START',
 'se474SpecificModes','se474ToolFlyout','data-se474-settings-open=false',
 'modelAtelierWorkshopOperation','setRingAnchor','selectRing'):
 assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.475';source.version=11.475;")==5
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,value in (
 ('sourceVersion',m['name']),('finalBytes',len(data)),
 ('finalSha256',m['finalSha256']),('patches',m['patches'])
):assert receipt[key]==value,key
assert len(receipt['assets'])==77
for filename,expected in receipt['assets'].items():
 raw=(out/filename).read_bytes()
 assert len(raw)==expected['bytes']
 assert hashlib.sha256(raw).hexdigest()==expected['sha256'],filename
if args.request:
 req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert req['releaseVersion']=='v11.475'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_475_PROGRESSIVE_RAIL_VISIBILITY'
 assert req['target']=='kamiloki/swrlz-forge-moba'
 assert req['sourceIntegritySha256']==m['finalSha256']
 assert req['sourceCommit']
print(json.dumps({'status':'SOURCE_VERIFIED','version':'v11.475',
 'bytes':len(data),'sha256':m['finalSha256'],'patches':452,
 'assets':77,'physicalMobileTested':False,'physicalVRTested':False}),flush=True)
