#!/usr/bin/env python3
"""Governed §E v11.14: validate exact 811-part scene and anchored-shoe pose runtime."""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',required=True)
a=p.parse_args()
root=Path(__file__).resolve().parent.parent
m=json.loads((root/'source-manifest.json').read_text('utf8'))
dist=Path(a.package)
receipt=json.loads((dist/'SOURCE.json').read_text('utf8'))
raw=(dist/'index.html').read_bytes()
assert len(m['patches'])==84 and m['patches'][-1]=='patches/v11_14_reference_refinement.py'
assert len(receipt['assets'])==37 and m['patches']==receipt['patches']
assert len(raw)==receipt['finalBytes']==m['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==receipt['finalSha256']
html=raw.decode('utf8')
for x in ('V11_14_REFERENCE_REFINEMENT','modelAtelierPoseDeck',
          'function atelierGroundedLeg(','function atelierGroundedFoot(',
          'atelierGroundedStances','atelierFootParts','v11.14 · sculpted hair & silhouette refinement'):
    assert x in html,x
assert 'function atelierBendNativeLeg(' not in html, 'Old rubber-knee logic survived'
found=re.search(r'const MODEL_ATELIER_LEGACY_V1112=(.*?);\n(?=const MODEL_ATELIER_CANONICAL_PROJECT=)',html,re.S)
assert found
canon=json.loads(found.group(1))
assert len(canon['project']['modelAtelier']['parts'])==811
historical='scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json'
assert (dist/historical).read_bytes()==(root/historical).read_bytes()
print('GROUNDED_POSE_84_PATCHES_37_ASSETS_811_MODEL_PARTS_PASS')
