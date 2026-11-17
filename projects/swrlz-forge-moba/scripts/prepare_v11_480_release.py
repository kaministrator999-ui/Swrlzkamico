#!/usr/bin/env python3
"""Build, verify and seal §E v11.480 contextual editable mesh conversion."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/'source-manifest.json'
m=json.loads(manifest_path.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.480'
assert m['finalArtifact']=='swyrl_engine_v11_480.html'
assert len(m['patches'])==457 and m['patches'][-1]=='patches/v11_480_visible_make_editable.py'
for file in ('model_vertex_entry_v11_477.js','model_progressive_hierarchy_v11_477.js',
             'model_progressive_hierarchy_v11_477.css','model_ring_vertex_highlight_v11_478.js',
             'model_ring_height_v11_478.js','model_ring_height_v11_478.css',
             'model_ring_rim_visibility_v11_479.js','model_ring_rim_visibility_v11_479.css',
             'model_editable_entry_v11_480.js','model_editable_entry_v11_480.css'):
 assert (ROOT/'runtime'/file).is_file()
for file in ('model_vertex_entry_v11_477.js','model_progressive_hierarchy_v11_477.js','model_ring_vertex_highlight_v11_478.js','model_ring_height_v11_478.js','model_ring_rim_visibility_v11_479.js','model_editable_entry_v11_480.js'):
 subprocess.run(['node','--check',str(ROOT/'runtime'/file)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_progressive_hierarchy_v11_477.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_ring_vertex_highlight_v11_478.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_ring_rim_visible_side_v11_479.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_editable_entry_v11_480.mjs')],check=True)
m['finalBytes']=None
m['finalSha256']=None
manifest_path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
out=ROOT/'_release_v11_480_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
source=(out/'index.html').read_bytes()
assert source==(out/'modeler.html').read_bytes()
m['finalBytes']=len(source)
m['finalSha256']=hashlib.sha256(source).hexdigest()
manifest_path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_480_release.py'),
 '--output',str(ROOT/'_release_v11_480_verified')],check=True)
print('SE480_MEASURED_RECEIPT='+json.dumps({
 'version':'v11.480','bytes':m['finalBytes'],'sha256':m['finalSha256'],
 'patches':len(m['patches'])
},sort_keys=True),flush=True)
