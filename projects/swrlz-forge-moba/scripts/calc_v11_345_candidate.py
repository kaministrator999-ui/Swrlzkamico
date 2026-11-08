#!/usr/bin/env python3
"""One-off v11.345 source integrity/UV atlas and display-mode regression."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
mp=ROOT/'source-manifest.json';m=json.loads(mp.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.344' and len(m['patches'])==355
m.update(name='§wyrl§ Engine v11.345',finalArtifact='swyrl_engine_v11_345.html',
         finalSha256='',finalBytes=0)
m['patches'].append('patches/v11_345_model_multi_uv_vr_display.py')
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
out=ROOT/'_candidate_v11_345'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes();assert raw==(out/'modeler.html').read_bytes()
for b in [b'V11_345_MODEL_MULTI_UV_VR_DISPLAY',b'SE345_MODEL_VR_DISPLAY_MODES_START',
          b'swyrl-model-uv-atlas-v1',b'UV atlas guide exported',b'displayMode:s.displayMode']:
 assert b in raw,b
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),
                str(out/'index.html')],check=True)
for filename in ['model_atelier_multi_uv_atlas_v11_345.js',
                 'model_vr_display_modes_v11_345.js','model_studio_vr_ui_v11_345.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/filename)],check=True)
subprocess.run(['npm','install','--silent','--prefix',str(out/'three-runtime'),
 '--no-audit','--no-fund','--no-save','three@0.169.0'],check=True)
three=out/'three-runtime/node_modules/three/build/three.module.js'
subprocess.run(['node',str(ROOT/'tests/model_multi_uv_atlas_v11_345.mjs'),str(three)],check=True)
print('V11_345_FINAL_BYTES='+str(len(raw)),flush=True)
print('V11_345_FINAL_SHA256='+hashlib.sha256(raw).hexdigest(),flush=True)
print('V11_345_PATCH_COUNT='+str(len(m['patches'])),flush=True)
