#!/usr/bin/env python3
"""Release verification for §E v11.100 touch scrolling and hold-to-edit."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--output',required=True)
out=Path(a.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.100'
assert m['finalArtifact']=='swyrl_engine_v11_100.html'
assert len(m['patches'])==132
assert m['patches'][-2:]==['patches/v11_99_mobile_scroll_size.py','patches/v11_100_hold_scroll_gutters.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(out)],check=True)
b=(out/'index.html').read_bytes();s=b.decode('utf-8')
receipt=json.loads((out/'SOURCE.json').read_text())
assert len(b)==m['finalBytes']==receipt['finalBytes']
assert hashlib.sha256(b).hexdigest()==m['finalSha256']==receipt['finalSha256']
assert receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches']
assert len(receipt['assets'])==68
for path,meta in receipt['assets'].items():
 data=(out/path).read_bytes()
 assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],path
for token in [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_100_HOLD_SCROLL_GUTTERS',
 '<title>§wyrl§ Engine · Maker v11.100</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.100'",
 'id="se-v11100-mobile-panel-ergonomics"',
 'function seMobileInspectorSizeInstall()',
 'seMobileInspectorSizeInstall();',
 'se-mobile-inspector-expanded',
 'height:min(49dvh,470px)!important;',
 'padding:12px 23px 16px!important;',
 'const holdMilliseconds=380;',
 'const holdTravelPixels=10;',
 'scheduleNumberHold(input,event.clientX,event.clientY,event.pointerId);',
 'event.preventDefault();event.stopImmediatePropagation();',
 "input.dispatchEvent(new Event('change',{bubbles:true}));",
 "scale:[.6,.6,.6]",
]:
 assert token in s,token
assert "event.stopImmediatePropagation();\n  open(input);\n },true);" not in s
assert re.findall(r'<meta\b[^>]*\bname\s*=\s*["\x27]viewport["\x27][^>]*>',s[:s.lower().find('</head>')],re.I)==['<meta name="viewport" content="width=device-width, initial-scale=1">']
Path(str(out)+'-module.mjs').write_text(s.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11100_VERIFIED',len(b),m['finalSha256'],'132_PATCHES_68_ASSETS')
