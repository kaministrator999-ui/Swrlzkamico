#!/usr/bin/env python3
"""Exact v11.145 source seal and targeted tests (not a deployed-UX claim)."""
import base64,gzip,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_space import load_patch
m=json.loads((ROOT/'source-manifest.json').read_text())
assert m['name']=='§wyrl§ Engine v11.145' and len(m['patches'])==177
assert m['patches'][-1]=='patches/v11_145_play_scene_build_ghost.py'
encoded=''.join((ROOT/p).read_text(encoding='utf8').strip() for p in m['chunks'])
html=gzip.decompress(base64.b64decode(encoded)).decode('utf8')
for patch in m['patches']:html=load_patch(ROOT/patch)(html)
b=html.encode()
size,digest=len(b),hashlib.sha256(b).hexdigest()
print('SE145_EXACT_SEAL_BYTES',size,flush=True)
print('SE145_EXACT_SEAL_SHA256',digest,flush=True)
if m['finalBytes']!=size or m['finalSha256']!=digest:
 print('SE145_NEEDS_MANIFEST_SEAL',flush=True);sys.exit(0)
print('SE145_MANIFEST_SEAL_MATCH',flush=True)
subprocess.run(['python',str(ROOT/'scripts/verify_v11_145_release.py'),'--output','dist/swrlz-forge-moba'],check=True)
subprocess.run(['node','--check','dist/swrlz-forge-moba-module.mjs'],check=True)
for n in ['play_scene_build_ghost_v11_145.mjs',
 'sheep_rapid_corner_snap_v11_139.mjs','sheep_passable_placement_v11_124.mjs',
 'sheep_drag_camera_capture_perf_v11_136.mjs','sheep_level_menu_runtime_v11_141.mjs',
 'editor_menu_stop_gait_v11_142.mjs','sheep_menu_portrait_camera_v11_144.mjs']:
 subprocess.run(['node',str(ROOT/'tests'/n)],check=True)
print('SE145_TARGETED_SOURCE_AND_TESTS_PASS',flush=True)
