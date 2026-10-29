#!/usr/bin/env python3
"""Verify §E v11.103 only doubles the mobile inspector height."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);d=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.103'
assert m['finalArtifact']=='swyrl_engine_v11_103.html'
assert len(m['patches'])==135
assert m['patches'][-2:]==['patches/v11_102_balanced_drag_panel.py','patches/v11_103_double_inspector_height.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(d)],check=True)
b=(d/'index.html').read_bytes();html=b.decode()
rec=json.loads((d/'SOURCE.json').read_text())
assert len(b)==m['finalBytes']==rec['finalBytes']
assert hashlib.sha256(b).hexdigest()==m['finalSha256']==rec['finalSha256']
assert rec['sourceVersion']==m['name'] and rec['patches']==m['patches']
assert len(rec['assets'])==68
for path,meta in rec['assets'].items():
 data=(d/path).read_bytes()
 assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],path
for x in [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_103_DOUBLE_INSPECTOR_HEIGHT',
 '<title>§wyrl§ Engine · Maker v11.103</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.103'",
 'id="se-v11103-double-inspector-height"',
 'height:min(68dvh,700px)!important;',
 'max-height:min(68dvh,700px)!important;',
 'height:min(78dvh,800px)!important;',
 'max-height:min(78dvh,800px)!important;',
 'width:min(390px,calc(100vw - 44px))!important;',
 'se-mobile-inspector-dragged',
 "inspector.style.setProperty('--se-mobile-drag-left',left+'px');",
 'const holdMilliseconds=380;',
 'function seMobileInspectorSizeInstall()',
 "scale:[.6,.6,.6]",
]:assert x in html,x
head=html[:html.lower().find('</head>')]
assert head.index('id="se-v11102-balanced-drag-panel"')<head.index('id="se-v11103-double-inspector-height"')
Path(str(d)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11103_VERIFIED',len(b),m['finalSha256'],'135_PATCHES_68_ASSETS')
