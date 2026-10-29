#!/usr/bin/env python3
"""v11.20 source + default facial composition and native frame controls."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--package',required=True);a=p.parse_args()
dist=Path(a.package)
m=json.loads((ROOT/'source-manifest.json').read_text())
receipt=json.loads((dist/'SOURCE.json').read_text())
source=(dist/'index.html').read_bytes()
assert len(m['patches'])==94 and m['patches'][-1]=='patches/v11_62_mobile_adaptive.py'
assert len(receipt['assets'])==43 and receipt['patches']==m['patches']
assert len(source)==m['finalBytes']==receipt['finalBytes']
assert hashlib.sha256(source).hexdigest()==m['finalSha256']==receipt['finalSha256']
html=source.decode('utf8')
for needle in ('SWYRL_ENGINE_DEPLOY_MARKER: V11_62_MOBILE_ADAPTIVE_TOOL_SHEET',
               'Maker v11.62','modelAtelierPoseDeck','modelAtelierPoseSelect',
               'atelierApplyBuiltInPose','atelierApplySavedPose','atelierValidatedFrameStore',
               'modelAtelierPoseViewApply','modelAtelierMetricsBody'):
    assert needle in html,needle
match=re.search(r'const MODEL_ATELIER_LEGACY_V1112=(.*?);\n(?=const MODEL_ATELIER_CANONICAL_PROJECT=)',html,re.S)
assert match,'native canonical figure was not embedded'
scene=json.loads(match.group(1));parts=scene['project']['modelAtelier']['parts'];byid={x['id']:x for x in parts}
assert len(parts)==811 and scene['version']==11.11
assert byid['model-0026']['scale'][0]>.069,'Iris not refined'
assert byid['model-0046']['rotation'][2]>.09,'Smirk not refined'
assert byid['model-0047']['scale'][0]<.05,'Nose not softened'
assert [x for x in parts if x['id'].startswith('atelier-v118-') and x['id'].endswith('-leg')]
old=ROOT/'scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json'
assert (dist/'scenes/model-atelier-prism-jester-festival-v11-9.swyrl.json').read_bytes()==old.read_bytes()
print('NATIVE_FACE_POSE_811_PARTS_90_PATCHES_43_ASSETS_PASS')
