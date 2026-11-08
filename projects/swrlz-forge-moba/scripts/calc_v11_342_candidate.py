#!/usr/bin/env python3
"""Calculate candidate v11.342 integrity in isolated GitHub Actions checkout."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'source-manifest.json';m=json.loads(p.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.341'
assert m['patches'][-1]=='patches/v11_341_model_vr_hover_orbit.py'
m.update(name='§wyrl§ Engine v11.342',finalArtifact='swyrl_engine_v11_342.html',finalSha256='',finalBytes=0)
m['patches'].append('patches/v11_342_model_vr_proxy_picking.py')
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
out=ROOT/'_candidate_v11_342'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
for needle in [b'V11_342_MODEL_VR_PROXY_PICKING',b'se340Hit(record,false)']:
 assert needle in data
subprocess.run(['node',str(ROOT/'tests/model_vr_proxy_picking_v11_342.cjs')],check=True)
print('V11_342_FINAL_BYTES='+str(len(data)),flush=True)
print('V11_342_FINAL_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
print('V11_342_PATCH_COUNT='+str(len(m['patches'])),flush=True)
