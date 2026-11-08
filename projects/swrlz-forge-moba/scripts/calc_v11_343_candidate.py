#!/usr/bin/env python3
"""One-off v11.343 candidate integrity and focused surface test."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
mp=ROOT/'source-manifest.json';m=json.loads(mp.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.342' and len(m['patches'])==353
m.update(name='§wyrl§ Engine v11.343',finalArtifact='swyrl_engine_v11_343.html',finalBytes=0,finalSha256='')
m['patches'].append('patches/v11_343_model_vr_surface_camera.py')
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
out=ROOT/'_candidate_v11_343'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
for needle in [b'V11_343_MODEL_VR_SURFACE_CAMERA',b'se343HoverContact(entry,cast)',b'se340XR.yaw+=dx*dt',b'se340XR.pitch-dy*dt']:
 assert needle in data,needle
subprocess.run(['node','--check',str(ROOT/'runtime/model_vr_surface_pick_v11_343.js')],check=True)
subprocess.run(['npm','install','--silent','--prefix',str(out/'three-runtime'),'--no-audit','--no-fund','--no-save','three@0.169.0'],check=True)
three=out/'three-runtime/node_modules/three/build/three.module.js'
subprocess.run(['node',str(ROOT/'tests/model_vr_surface_v11_343.mjs'),str(three)],check=True)
print('V11_343_FINAL_BYTES='+str(len(data)),flush=True)
print('V11_343_FINAL_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
print('V11_343_PATCH_COUNT='+str(len(m['patches'])),flush=True)
