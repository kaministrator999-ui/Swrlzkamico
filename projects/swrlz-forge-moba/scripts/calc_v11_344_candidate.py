#!/usr/bin/env python3
"""Candidate source-seal calculation and focused real-Three aim/view checks."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
mp=ROOT/'source-manifest.json';m=json.loads(mp.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.343' and len(m['patches'])==354
m.update(name='§wyrl§ Engine v11.344',finalArtifact='swyrl_engine_v11_344.html',
         finalBytes=0,finalSha256='')
m['patches'].append('patches/v11_344_model_vr_aim_views_trigger.py')
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
out=ROOT/'_candidate_v11_344'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
for key in [b'V11_344_MODEL_VR_AIM_VIEWS_TRIGGER',b'SE344_MODEL_VR_AIM_VIEWS_START',
 b'const triggerStarted=performance.now();const hit=se340Hit(record,false);',
 b'viewMode:s.viewMode',b'if (selection === id)']:
 assert key in data,key
for file in ['model_vr_aim_views_v11_344.js','model_studio_vr_ui_v11_344.js','model_vr_bridge_v11_344.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/file)],check=True)
subprocess.run(['npm','install','--silent','--prefix',str(out/'three-runtime'),
                '--no-audit','--no-fund','--no-save','three@0.169.0'],check=True)
three=out/'three-runtime/node_modules/three/build/three.module.js'
subprocess.run(['node',str(ROOT/'tests/model_vr_aim_views_trigger_v11_344.mjs'),str(three)],check=True)
print('V11_344_FINAL_BYTES='+str(len(data)),flush=True)
print('V11_344_FINAL_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
print('V11_344_PATCH_COUNT='+str(len(m['patches'])),flush=True)
