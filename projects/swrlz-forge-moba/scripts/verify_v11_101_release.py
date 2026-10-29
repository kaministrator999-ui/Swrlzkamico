#!/usr/bin/env python3
"""Verify §E v11.101 compact quarter-screen mobile overlays."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);o=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.101'
assert m['finalArtifact']=='swyrl_engine_v11_101.html'
assert len(m['patches'])==133
assert m['patches'][-2:]==['patches/v11_100_hold_scroll_gutters.py','patches/v11_101_compact_quarter_panel.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(o)],check=True)
raw=(o/'index.html').read_bytes();html=raw.decode('utf-8')
receipt=json.loads((o/'SOURCE.json').read_text())
assert len(raw)==m['finalBytes']==receipt['finalBytes']
assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==receipt['finalSha256']
assert receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches']
assert len(receipt['assets'])==68
for path,meta in receipt['assets'].items():
 b=(o/path).read_bytes()
 assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256'],path
for needle in [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_101_COMPACT_QUARTER_PANEL',
 '<title>§wyrl§ Engine · Maker v11.101</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.101'",
 'id="se-v11101-compact-quarter-panel"',
 'height:min(26dvh,255px)!important;',
 'max-height:min(26dvh,255px)!important;',
 'width:min(320px,calc(100vw - 56px))!important;',
 'height:min(38dvh,385px)!important;',
 '.atelier-mobile-upgrade.se-mobile-inspector-expanded',
 'const holdMilliseconds=380;',
 'function seMobileInspectorSizeInstall()',
 "scale:[.6,.6,.6]",
]:assert needle in html,needle
head=html[:html.lower().find('</head>')]
assert head.count('id="se-v11101-compact-quarter-panel"')==1
assert head.index('id="se-v11100-mobile-panel-ergonomics"')<head.index('id="se-v11101-compact-quarter-panel"')
Path(str(o)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11101_VERIFIED',len(raw),m['finalSha256'],'133_PATCHES_68_ASSETS')
