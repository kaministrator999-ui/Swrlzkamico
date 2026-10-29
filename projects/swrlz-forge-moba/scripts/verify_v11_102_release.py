#!/usr/bin/env python3
"""Verify §E v11.102 balanced, manually draggable mobile inspector."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--output',required=True);d=Path(a.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.102'
assert m['finalArtifact']=='swyrl_engine_v11_102.html'
assert len(m['patches'])==134
assert m['patches'][-2:]==['patches/v11_101_compact_quarter_panel.py','patches/v11_102_balanced_drag_panel.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(d)],check=True)
b=(d/'index.html').read_bytes();s=b.decode()
receipt=json.loads((d/'SOURCE.json').read_text())
assert len(b)==m['finalBytes']==receipt['finalBytes']
assert hashlib.sha256(b).hexdigest()==m['finalSha256']==receipt['finalSha256']
assert receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches']
assert len(receipt['assets'])==68
for path,meta in receipt['assets'].items():
 blob=(d/path).read_bytes()
 assert len(blob)==meta['bytes'] and hashlib.sha256(blob).hexdigest()==meta['sha256'],path
for token in [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_102_BALANCED_DRAGGABLE_PANEL',
 '<title>§wyrl§ Engine · Maker v11.102</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.102'",
 'id="se-v11102-balanced-drag-panel"',
 'height:min(34dvh,350px)!important;',
 'width:min(390px,calc(100vw - 44px))!important;',
 'height:min(43dvh,440px)!important;',
 'se-mobile-inspector-dragged',
 "inspector.style.setProperty('--se-mobile-drag-left',left+'px');",
 "inspector.style.setProperty('--se-mobile-drag-top',top+'px');",
 "left:var(--se-mobile-drag-left,auto)!important;",
 'const holdMilliseconds=380;',
 'function seMobileInspectorSizeInstall()',
 "scale:[.6,.6,.6]",
]:assert token in s,token
head=s[:s.lower().find('</head>')]
assert head.index('id="se-v11101-compact-quarter-panel"')<head.index('id="se-v11102-balanced-drag-panel"')
Path(str(d)+'-module.mjs').write_text(s.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11102_VERIFIED',len(b),m['finalSha256'],'134_PATCHES_68_ASSETS')
