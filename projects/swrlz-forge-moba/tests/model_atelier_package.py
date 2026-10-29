#!/usr/bin/env python3
"""§E v11.3 independent native Model Atelier source + package acceptance."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser()
ap.add_argument('--package',required=True)
args=ap.parse_args()
out=Path(args.package)
manifest=json.loads((ROOT/'source-manifest.json').read_text())
source=(out/'index.html').read_bytes()
receipt=json.loads((out/'SOURCE.json').read_text())
scene_path='scenes/model-atelier-prism-jester.swyrl.json'
scene=json.loads((ROOT/scene_path).read_text())
served=json.loads((out/scene_path).read_text())
model=scene['project']['modelAtelier']
parts=model['parts']
assert scene==served,'Packaged original model differs from source'
assert scene['project']['kind']=='model-atelier'
assert scene['project']['canonicalId']=='model-atelier-prism-jester'
assert scene['version']==11.3
assert model['schema']=='swyrl-model-atelier-v1'
assert len(parts)>=200 and len({p['id'] for p in parts})==len(parts)
assert set(p['group'] for p in parts)>={'Coral flare','Azure frost','Character'}
assert all(p['kind'] in {'sphere','box','cone','cylinder'} for p in parts)
assert all(p['material'] in {'matte','silk','gloss','metal','emissive'} for p in parts)
assert all(len(p[field])==3 for p in parts for field in ('position','rotation','scale'))
assert 'data-project-template="model-atelier"' in source.decode()
for needle in (b'MODEL_ATELIER_V11_3_BEGIN',b'modelAtelierPanel',
               b'model-atelier-prism-jester',b'V11_62_MOBILE_ADAPTIVE_TOOL_SHEET',
               b'SWYRL_ENGINE_MODEL_ATELIER',b'modelAtelierImportFile'):
    assert needle in source,needle
assert receipt['patches']==manifest['patches']
assert len(receipt['patches'])==94
assert receipt['patches'][-1]=='patches/v11_62_mobile_adaptive.py'
assert scene_path in receipt['assets']
assert len(receipt['assets'])==43
assert receipt['assets'][scene_path]['sha256']==hashlib.sha256((ROOT/scene_path).read_bytes()).hexdigest()
assert receipt['assets'][scene_path]['bytes']==(ROOT/scene_path).stat().st_size
assert hashlib.sha256(source).hexdigest()==manifest['finalSha256']==receipt['finalSha256']
assert len(source)==manifest['finalBytes']==receipt['finalBytes']
print('MODEL_ATELIER_NATIVE_SCENE_MATCH '+str(len(parts))+' editable components')
# The newly authored scene is independent and must ship alongside all older variants.
new_scene='scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json'
new_raw=(ROOT/new_scene).read_bytes()
assert new_scene in receipt['assets']
assert receipt['assets'][new_scene]['sha256']==hashlib.sha256(new_raw).hexdigest()
assert receipt['assets'][new_scene]['bytes']==len(new_raw)
new_model=json.loads(new_raw)['project']['modelAtelier']['parts']
assert len(new_model)==811 and len({p['id'] for p in new_model})==811
assert sum(p.get('surfaceStyle')=='pinata-twisted' for p in new_model)==2
assert sum(p.get('surfaceStyle')=='fabric-panel' for p in new_model)==8
print('MODEL_ATELIER_PACKAGE_90_PATCHES_43_ASSETS_PASS')
