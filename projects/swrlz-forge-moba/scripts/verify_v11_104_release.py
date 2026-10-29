#!/usr/bin/env python3
"""Validate §E v11.104 picked point overlay and readable menus."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);o=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.104'
assert m['finalArtifact']=='swyrl_engine_v11_104.html'
assert len(m['patches'])==136
assert m['patches'][-2:]==['patches/v11_103_double_inspector_height.py','patches/v11_104_pick_marker_readable_menus.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(o)],check=True)
b=(o/'index.html').read_bytes();html=b.decode()
rec=json.loads((o/'SOURCE.json').read_text())
assert len(b)==m['finalBytes']==rec['finalBytes']
assert hashlib.sha256(b).hexdigest()==m['finalSha256']==rec['finalSha256']
assert rec['sourceVersion']==m['name'] and rec['patches']==m['patches']
assert len(rec['assets'])==68
for path,meta in rec['assets'].items():
 data=(o/path).read_bytes()
 assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],path
for x in [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_104_PICK_MARKER_READABLE_MENUS',
 '<title>§wyrl§ Engine · Maker v11.104</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.104'",
 'id="se-v11104-clean-menus"',
 'function atelierSculptPickMarkerRefresh()',
 'function atelierSculptPickMarkerInstall()',
 'atelierSculptPickMarkerRefresh();',
 'atelierSculptPickMarkerInstall();',
 'Picked sculpt center indicator (editor only)',
 "new THREE.TorusGeometry(radius,.0055,7,40)",
 "mesh.localToWorld(local.clone())",
 'depthTest:false,depthWrite:false',
 'modelAtelierSculptPickedReadout',
 '.atelier-inspector-actions',
 'grid-template-columns:repeat(2,minmax(0,1fr))!important;',
 'height:min(68dvh,700px)!important;',
 'se-mobile-inspector-dragged',
 'const holdMilliseconds=380;',
 "scale:[.6,.6,.6]",
]:assert x in html,x
head=html[:html.lower().find('</head>')]
assert head.index('id="se-v11103-double-inspector-height"')<head.index('id="se-v11104-clean-menus"')
Path(str(o)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11104_VERIFIED',len(b),m['finalSha256'],'136_PATCHES_68_ASSETS')
