#!/usr/bin/env python3
"""Governed §E v11.12: validate exact 811-part scene and anchored-shoe pose runtime."""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--package',required=True)
a=p.parse_args()
root=Path(__file__).resolve().parent.parent
m=json.loads((root/'source-manifest.json').read_text('utf8'))
dist=Path(a.package)
receipt=json.loads((dist/'SOURCE.json').read_text('utf8'))
raw=(dist/'index.html').read_bytes()
assert len(m['patches'])==82 and m['patches'][-1]=='patches/v11_12_grounded_stance_poses.py'
assert len(receipt['assets'])==35 and m['patches']==receipt['patches']
assert len(raw)==receipt['finalBytes']==m['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==receipt['finalSha256']
html=raw.decode('utf8')
for x in ('V11_12_GROUNDED_STANCE_POSES','modelAtelierPoseDeck',
          'function atelierGroundedLeg(','function atelierGroundedFoot(',
          'atelierGroundedStances','atelierFootParts','v11.12 · grounded anatomical pose studio'):
    assert x in html,x
assert 'function atelierBendNativeLeg(' not in html, 'Old rubber-knee logic survived'
found=re.search(r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)',html,re.S)
assert found
canon=json.loads(found.group(1))
assert len(canon['project']['modelAtelier']['parts'])==811
historical='scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json'
assert (dist/historical).read_bytes()==(root/historical).read_bytes()
print('GROUNDED_POSE_82_PATCHES_35_ASSETS_811_MODEL_PARTS_PASS')
