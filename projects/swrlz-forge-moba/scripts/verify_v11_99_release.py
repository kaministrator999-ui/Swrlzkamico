#!/usr/bin/env python3
"""Verify §E v11.99 large scrollable mobile menus and source lineage."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);o=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.99'
assert m['finalArtifact']=='swyrl_engine_v11_99.html'
assert len(m['patches'])==131
assert m['patches'][-2:]==['patches/v11_98_mobile_numpad_touch_fix.py','patches/v11_99_mobile_scroll_size.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(o)],check=True)
raw=(o/'index.html').read_bytes();html=raw.decode('utf8')
r=json.loads((o/'SOURCE.json').read_text())
assert len(raw)==m['finalBytes']==r['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==r['finalSha256']
assert r['sourceVersion']==m['name'] and r['patches']==m['patches']
assert len(r['assets'])==68
for path,meta in r['assets'].items():
    b=(o/path).read_bytes()
    assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256'],path
for token in [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_99_MOBILE_SCROLL_SIZE',
 '<title>§wyrl§ Engine · Maker v11.99</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.99'",
 "matchMedia('(max-width:980px), (pointer:coarse)')",
 '@media (max-width:980px),(pointer:coarse){',
 'id="se-v1199-mobile-scroll-size"',
 'pointer-events:auto!important;',
 'touch-action:pan-y!important;',
 'overflow-y:auto!important;',
 'height:min(64dvh,',
 'width:calc(100vw - 16px)!important;',
 'SculptBrushPick',
 'seMobileNumberPadInstall();',
 "scale:[.6,.6,.6]",
]:
 assert token in html,token
assert re.findall(r'<meta\b[^>]*\bname\s*=\s*["\x27]viewport["\x27][^>]*>',html[:html.lower().find('</head>')],re.I)==['<meta name="viewport" content="width=device-width, initial-scale=1">']
Path(str(o)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1199_VERIFIED',len(raw),m['finalSha256'],'131_PATCHES_68_ASSETS')
