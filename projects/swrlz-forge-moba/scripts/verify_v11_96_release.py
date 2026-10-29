#!/usr/bin/env python3
"""Verify v11.96 browser-input accessibility and true-sphere blank starter."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
args=parser.parse_args()
out=Path(args.output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.96'
assert m['finalArtifact']=='swyrl_engine_v11_96.html'
assert len(m['patches'])==128
assert m['patches'][-2:]==['patches/v11_95_fitted_skirt_waist.py','patches/v11_96_mobile_input_round_blank.py']
old=(ROOT/'tests/fitted_skirt_baseline_v11_94.json')
baseline=json.loads(old.read_text())
assert m['patches'][:-2]==baseline['patches']
for path,digest in baseline['sources'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
last=(ROOT/'patches/v11_95_fitted_skirt_waist.py').read_bytes()
assert b'function atelierAnimeGirlProjectV1194' in last and b'v11.95' in last, 'Historical patch changed'
# Do not suppress the build log: the final patch emits independent length
# and SHA-256 measurements, useful if an integrity receipt requires repair.
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes()
html=raw.decode('utf8')
receipt=json.loads((out/'SOURCE.json').read_text())
assert len(raw)==m['finalBytes']==receipt['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==receipt['finalSha256']
assert receipt['patches']==m['patches']
assert len(receipt['assets'])==68
assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_96_MOBILE_INPUT_ROUND_BLANK' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.96'" in html
assert '<title>§wyrl§ Engine · Maker v11.96</title>' in html
assert 'id="se-v1196-mobile-input-size"' in html
assert 'font-size: 16px !important;' in html
assert "id:'model-seed',name:'Model blockout',kind:'sphere',position:[0,1.5,0],rotation:[0,0,0],scale:[.6,.6,.6]" in html
assert "id:'model-seed',name:'Model blockout',kind:'sphere',position:[0,1.5,0],rotation:[0,0,0],scale:[.5,.6,.8]" not in html
assert len(receipt['assets'])==68 and 'scenes/model-atelier-fitted-waist-v11-95.swyrl.json' in receipt['assets']
for path,meta in receipt['assets'].items():
    b=(out/path).read_bytes()
    assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256'],path
Path(str(out)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1196_RELEASE_VERIFIED',len(raw),m['finalSha256'],'128_PATCHES_68_ASSETS',
      'OLDER_SOURCE_AND_PACKAGED_ASSETS_PRESERVED','ROUND_BLANK_MODEL','MOBILE_INPUT_16PX')
