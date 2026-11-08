#!/usr/bin/env python3
"""Verify the sealed v11.341 Model Studio VR release; no broad game suites."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_341_MODEL_VR_HOVER_ORBIT'
cli=argparse.ArgumentParser()
cli.add_argument('--output',required=True)
cli.add_argument('--request',action='store_true')
args=cli.parse_args()
manifest=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.341'
assert manifest['finalArtifact']=='swyrl_engine_v11_341.html'
assert len(manifest['patches'])==352
assert manifest['patches'][-1]=='patches/v11_341_model_vr_hover_orbit.py'
assert manifest['finalBytes']==9119871
assert manifest['finalSha256']=='8806d47c59544600e189de33500d38f8c5c19b0dd8a09f20e3438c2492e1e8c0'
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==manifest['finalBytes']
assert hashlib.sha256(raw).hexdigest()==manifest['finalSha256']
html=raw.decode('utf8')
for key in [MARKER,"window.SWRLZ_FORGE_BUILD={version:'v11.341'",
            '<title>§wyrl§ Engine · Maker v11.341</title>',
            'record.nextHoverAt=now+55','cast.ray.intersectsBox',
            's.frameEntries=bridge.projection().meshes','se340XR.pitch+dy*dt',
            'se340Pressed(record,3)','SE340_MODEL_VR_BRIDGE_START',
            'SE330_MATERIAL_STUDIO_LAYOUT_START','SE321_LOS_CORE_START']:
    assert key in html,key
assert 'turnLatched' not in html[html.index('/* SE340_MODEL_VR_WORKSPACE_START */'):html.index('/* SE340_MODEL_VR_WORKSPACE_END */')]
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
for file in ['model_vr_workspace_v11_341.js','model_studio_vr_ui_v11_341.js']:
    subprocess.run(['node','--check',str(ROOT/'runtime'/file)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_vr_hover_orbit_v11_341.cjs')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,expected in [('sourceVersion',manifest['name']),('patches',manifest['patches']),
                      ('finalBytes',manifest['finalBytes']),('finalSha256',manifest['finalSha256'])]:
    assert receipt[key]==expected
assert len(receipt['assets'])==71
for name,meta in receipt['assets'].items():
    data=(out/name).read_bytes()
    assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],name
if args.request:
    request=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
    assert request['releaseVersion']=='v11.341'
    assert request['deployMarker']==MARKER
    assert request['sourceIntegritySha256']==manifest['finalSha256']
    assert len(request['sourceCommit'])==40
print(json.dumps({'status':'SEALED_SOURCE_VERIFIED','version':'v11.341',
                  'patches':352,'bytes':len(raw),'sha256':manifest['finalSha256'],
                  'assets':71,'physicalHeadsetAcceptance':False},indent=2))
