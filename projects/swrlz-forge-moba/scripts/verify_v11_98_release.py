#!/usr/bin/env python3
"""Verify §E v11.98 guarded mobile keypad activation and immutable packaged assets."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);o=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.98'
assert m['finalArtifact']=='swyrl_engine_v11_98.html'
assert len(m['patches'])==130
assert m['patches'][-2:]==['patches/v11_97_mobile_viewport_focus.py','patches/v11_98_mobile_numpad_touch_fix.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(o)],check=True)
raw=(o/'index.html').read_bytes();html=raw.decode('utf8')
r=json.loads((o/'SOURCE.json').read_text())
assert len(raw)==m['finalBytes']==r['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==r['finalSha256']
assert r['sourceVersion']==m['name'] and r['patches']==m['patches']
assert len(r['assets'])==68
for path,meta in r['assets'].items():
    data=(o/path).read_bytes()
    assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],path
for token in [
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_98_MOBILE_NUMPAD_TOUCH_FIX',
  '<title>§wyrl§ Engine · Maker v11.98</title>',
  "window.SWRLZ_FORGE_BUILD={version:'v11.98'",
  "let padPressTarget=null;",
  "box.addEventListener('pointerdown',armPad,true);",
  "const pressed=padPressTarget;",
  "if(event.detail!==0&&pressed!==b){",
  'event.stopPropagation();',
  "input.dispatchEvent(new Event('change',{bubbles:true}));",
  "scale:[.6,.6,.6]",
  'id="se-v1197-numpad-style"',
]:
    assert token in html,token
assert re.findall(r'<meta\b[^>]*\bname\s*=\s*["\x27]viewport["\x27][^>]*>',html[:html.lower().find('</head>')],re.I)==['<meta name="viewport" content="width=device-width, initial-scale=1">']
Path(str(o)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1198_VERIFIED',len(raw),m['finalSha256'],'130_PATCHES_68_ASSETS','NUMPAD_GESTURE_GUARD')
