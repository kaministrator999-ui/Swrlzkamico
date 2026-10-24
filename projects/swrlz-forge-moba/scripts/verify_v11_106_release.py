#!/usr/bin/env python3
"""Verify §E v11.106 viewport display state through mesh regeneration."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
out=Path(parser.parse_args().output).resolve()
manifest=json.loads((ROOT/'source-manifest.json').read_text())
assert manifest['name']=='§wyrl§ Engine v11.106'
assert manifest['finalArtifact']=='swyrl_engine_v11_106.html'
assert len(manifest['patches'])==138
assert manifest['patches'][-2:]==[
 'patches/v11_105_sculpt_undo_view_spacing.py',
 'patches/v11_106_sculpt_render_mode_rebuild.py']
subprocess.run(['python',str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes();html=raw.decode('utf8')
receipt=json.loads((out/'SOURCE.json').read_text())
assert len(raw)==manifest['finalBytes']==receipt['finalBytes']
assert hashlib.sha256(raw).hexdigest()==manifest['finalSha256']==receipt['finalSha256']
assert receipt['sourceVersion']==manifest['name'] and receipt['patches']==manifest['patches']
assert len(receipt['assets'])==68
for path,meta in receipt['assets'].items():
 b=(out/path).read_bytes()
 assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256'],path
for token in [
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_106_SCULPT_RENDER_MODE_REBUILD',
 '<title>§wyrl§ Engine · Maker v11.106</title>',
 "window.SWRLZ_FORGE_BUILD={version:'v11.106'",
 'function atelierViewEnsureAfterGeometryEdit(){',
 'renderParts();atelierViewEnsureAfterGeometryEdit();refreshList();refreshInspector();',
 "mode==='wireframe'&&!mat.wireframe",
 "mode==='xray'&&(!mat.transparent||mat.opacity>.31||mat.depthWrite)",
 "mode==='overlay'&&!hasOverlay",
 'atelierViewModeApply(mesh,part);',
 'atelierHDDirty=true;',
 'function atelierViewRebuild(){if(modelRoot){renderParts();atelierHDDirty=true;}}',
 'const viewGlobalBefore=atelierViewGlobal;',
 'atelierSculptPickMarkerRefresh();',
 'height:min(68dvh,700px)!important;',
 'const holdMilliseconds=380;',
]:assert token in html,token
Path(str(out)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V11106_VERIFIED',len(raw),manifest['finalSha256'],'138_PATCHES_68_ASSETS')
