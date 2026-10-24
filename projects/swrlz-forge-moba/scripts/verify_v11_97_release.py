#!/usr/bin/env python3
"""Verify §E v11.97 responsive viewport, native sphere and lineage."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);o=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.97'
assert m['finalArtifact']=='swyrl_engine_v11_97.html'
assert len(m['patches'])==129
assert m['patches'][-2:]==['patches/v11_96_mobile_input_round_blank.py','patches/v11_97_mobile_viewport_focus.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(o)],check=True)
raw=(o/'index.html').read_bytes();html=raw.decode()
r=json.loads((o/'SOURCE.json').read_text())
assert len(raw)==m['finalBytes']==r['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==r['finalSha256']
assert r['sourceVersion']==m['name'] and r['patches']==m['patches']
assert len(r['assets'])==68
assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_97_MOBILE_VIEWPORT_FOCUS' in html
assert '<title>§wyrl§ Engine · Maker v11.97</title>' in html
assert "window.SWRLZ_FORGE_BUILD={version:'v11.97'" in html
assert re.findall(r'<meta\b[^>]*\bname\s*=\s*["\x27]viewport["\x27][^>]*>',html,re.I)==['<meta name="viewport" content="width=device-width, initial-scale=1">']
assert 'font-size: 16px !important;' in html
assert "id:'model-seed',name:'Model blockout',kind:'sphere',position:[0,1.5,0],rotation:[0,0,0],scale:[.6,.6,.6]" in html
for path,meta in r['assets'].items():
    data=(o/path).read_bytes()
    assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],path
Path(str(o)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1197_VERIFIED',len(raw),m['finalSha256'],'129_PATCHES_68_ASSETS')
