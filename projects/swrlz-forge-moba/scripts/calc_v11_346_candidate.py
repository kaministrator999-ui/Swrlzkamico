#!/usr/bin/env python3
"""Rebuild v11.346 from sealed source and test 811-part multi-sheet atlas."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'source-manifest.json';m=json.loads(p.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.345' and len(m['patches'])==356
m.update(name='§wyrl§ Engine v11.346',finalArtifact='swyrl_engine_v11_346.html',finalBytes=0,finalSha256='')
m['patches'].append('patches/v11_346_model_multi_uv_sheets.py')
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
out=ROOT/'_candidate_v11_346'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
assert data==(out/'modeler.html').read_bytes()
for needle in [b'V11_346_MODEL_MULTI_UV_SHEETS',b'SE346_MULTI_UV_SHEETS_START',
 b'SE345_MODEL_VR_DISPLAY_MODES_START',b'Previous sheet',b'Next sheet',
 b'se346AtlasSuffix(plan)']:
 assert needle in data,needle
subprocess.run(['node','--check',str(ROOT/'runtime/model_multi_uv_sheets_v11_346.js')],check=True)
subprocess.run(['npm','install','--silent','--prefix',str(out/'three-runtime'),
                '--no-audit','--no-fund','--no-save','three@0.169.0'],check=True)
three=out/'three-runtime/node_modules/three/build/three.module.js'
subprocess.run(['node',str(ROOT/'tests/model_multi_uv_sheets_v11_346.mjs'),str(three)],check=True)
print('V11_346_FINAL_BYTES='+str(len(data)),flush=True)
print('V11_346_FINAL_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
print('V11_346_PATCH_COUNT='+str(len(m['patches'])),flush=True)
