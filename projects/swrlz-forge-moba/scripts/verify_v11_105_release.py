#!/usr/bin/env python3
"""Verify §E v11.105 sculpt undo view-state isolation and mobile spacing."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);d=Path(p.parse_args().output).resolve()
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.105'
assert m['finalArtifact']=='swyrl_engine_v11_105.html'
assert len(m['patches'])==137
assert m['patches'][-2:]==['patches/v11_104_pick_marker_readable_menus.py','patches/v11_105_sculpt_undo_view_spacing.py']
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
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_105_SCULPT_UNDO_VIEW_MENU',
 '<title>§wyrl§ Engine · Maker v11.105</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.105'",
 'id="se-v11105-menu-spacing"',
 'const viewGlobalBefore=atelierViewGlobal;',
 'const viewOverridesBefore=new Map(atelierViewOverrides);',
 "const viewScopeBefore=$m('ViewportScope')?.value;",
 'atelierViewportControlsRefresh();',
 'signalEdited();\n   const overridesChanged=',
 'width:min(415px,calc(100vw - 24px))!important;',
 'column-gap:12px!important;row-gap:13px!important;',
 'height:min(68dvh,700px)!important;',
 'function atelierSculptPickMarkerRefresh()',
 'const holdMilliseconds=380;',
]:assert x in html,x
assert "signalEdited();select(p.id);status('Last sculpt stroke removed;" not in html
head=html[:html.lower().find('</head>')]
assert head.index('id="se-v11104-clean-menus"')<head.index('id="se-v11105-menu-spacing"')
Path(str(d)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11105_VERIFIED',len(b),m['finalSha256'],'137_PATCHES_68_ASSETS')
