#!/usr/bin/env python3
"""Compute exact §E v11.144 HTML seal without trusting the manifest candidate."""
import base64,gzip,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text(encoding='utf8'))
assert m['name']=='§wyrl§ Engine v11.144' and len(m['patches'])==176
assert m['patches'][-1]=='patches/v11_144_menu_sheep_camera.py'
parts=''.join((ROOT/f).read_text(encoding='utf8').strip() for f in m['chunks'])
html=gzip.decompress(base64.b64decode(parts)).decode('utf8')
for rel in m['patches']:
 html=load_patch(ROOT/rel)(html)
raw=html.encode('utf8')
size,digest=len(raw),hashlib.sha256(raw).hexdigest()
print('SE144_EXACT_SEAL_BYTES',size,flush=True)
print('SE144_EXACT_SEAL_SHA256',digest,flush=True)
if (m['finalBytes'],m['finalSha256'])!=(size,digest):
 print('SE144_NEEDS_MANIFEST_SEAL: update only to exact measured bytes/hash, then repeat',flush=True)
 sys.exit(0)
print('SE144_MANIFEST_SEAL_MATCH',flush=True)
subprocess.run(['python',str(ROOT/'scripts/verify_v11_144_release.py'),'--output','dist/swrlz-forge-moba'],check=True)
subprocess.run(['node','--check','dist/swrlz-forge-moba-module.mjs'],check=True)
subprocess.run(['node',str(ROOT/'tests/sheep_menu_portrait_camera_v11_144.mjs')],check=True)
for filename in ['sheep_editable_project_levels_v11_141.mjs','sheep_level_menu_runtime_v11_141.mjs','editor_menu_stop_gait_v11_142.mjs']:
 subprocess.run(['node',str(ROOT/'tests'/filename)],check=True)
print('SE144_FINAL_SOURCE_AND_TARGETED_REGRESSIONS_PASS',flush=True)
