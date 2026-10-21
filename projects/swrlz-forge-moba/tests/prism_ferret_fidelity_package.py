#!/usr/bin/env python3
"""Independent v11.4 organic ferret-piñata geometry and native-package contract."""
import argparse
import hashlib
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser()
ap.add_argument('--package',required=True)
args=ap.parse_args()
dest=Path(args.package)
p='scenes/model-atelier-prism-jester-ferret-v11-4.swyrl.json'
old='scenes/model-atelier-prism-jester.swyrl.json'
raw=(ROOT/p).read_bytes()
assert raw==(dest/p).read_bytes(),'Native v11.4 scene not packaged verbatim'
data=json.loads(raw)
model=data['project']['modelAtelier']
parts=model['parts']
assert data['version']==11.4 and model['schema']=='swyrl-model-atelier-v1'
assert data['project']['canonicalId']=='model-atelier-prism-jester'
assert len(parts)==303 and len({v['id'] for v in parts})==303
assert set(v['group'] for v in parts)=={'Character','Azure frost','Coral flare'}
assert len([v for v in parts if 'ferret · velvet head' in v['name']])==2
assert len([v for v in parts if 'ferret · tapered muzzle' in v['name']])==2
assert len([v for v in parts if 'ferret · amber eye' in v['name']])==2
assert len([v for v in parts if 'piñata · paper fringe' in v['name']])>=160
lofts=[v for v in parts if v['kind']=='loft']
assert len(lofts)==2
assert {v['group'] for v in lofts}=={'Azure frost','Coral flare'}
for loft in lofts:
    coords,radii=loft['path'],loft['radii']
    assert 8<=len(coords)<=40 and len(coords)==len(radii)
    assert all(len(p)==3 and all(math.isfinite(x) for x in p) for p in coords)
    assert all(.025<=r<=5 for r in radii)
    assert max(radii)-min(radii)>.15,'Organic body is not visibly tapered'
    assert loft['segments']>=60 and loft['radialSegments']>=12
for v in parts:
    assert v['kind'] in {'sphere','box','cone','cylinder','loft'}
    assert len(v['position'])==len(v['rotation'])==len(v['scale'])==3
    assert all(math.isfinite(x) for key in ('position','rotation','scale') for x in v[key])
receipt=json.loads((dest/'SOURCE.json').read_text())
manifest=json.loads((ROOT/'source-manifest.json').read_text())
assert receipt['sourceVersion']=='§wyrl§ Engine v11.62'
assert len(receipt['patches'])==94 and receipt['patches']==manifest['patches']
assert receipt['patches'][-1]=='patches/v11_62_mobile_adaptive.py'
assert len(receipt['assets'])==43 and p in receipt['assets'] and old in receipt['assets']
for path in (p,old):
    content=(ROOT/path).read_bytes()
    assert receipt['assets'][path]['bytes']==len(content)
    assert receipt['assets'][path]['sha256']==hashlib.sha256(content).hexdigest()
html=(dest/'index.html').read_bytes()
for marker in (b'V11_62_MOBILE_ADAPTIVE_TOOL_SHEET',b'atelierOrganicLoft',b'MODEL_ATELIER_V11_4_FERRET_FIDELITY',b'loft',b'Maker v11.62'):
    assert marker in html, marker
assert len(html)==receipt['finalBytes']==manifest['finalBytes']
assert hashlib.sha256(html).hexdigest()==receipt['finalSha256']==manifest['finalSha256']
print('FERRET_FIDELITY_303_COMPONENTS_2_ORGANIC_LOFTS_PASS')
print('FERRET_FIDELITY_90_PATCHES_43_ASSETS_AND_LEGACY_SCENE_PASS')
