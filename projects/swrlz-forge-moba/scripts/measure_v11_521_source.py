#!/usr/bin/env python3
"""Build v11.521 from the full ordered append-only source with temporary, local-only
unsealed manifest fields, then print actual HTML SHA and size for resealing.
Never push this temporary manifest or bypass the final release verifier.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'source-manifest.json';original=p.read_text('utf8')
m=json.loads(original)
assert m['name']=='§wyrl§ Engine v11.521'
assert len(m['patches'])==498
assert m['patches'][-1]=='patches/v11_521_model_labs_persistent_history.py'
m['finalBytes']=0;m['finalSha256']=''
try:
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 out=root/'_measure_v11_521'
 subprocess.run([sys.executable,str(root/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 text=raw.decode('utf8')
 for needle in ['V11_521_LABS_PROJECT_JOURNAL','SE521_PERSISTENT_EDIT_JOURNAL_END',
                'SE521_MODEL_VR_LABS_END',"['labs','Labs','labs']",
                'swyrl-edit-journal-v1']:
  assert needle in text,needle
 subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),
                 str(out/'index.html')],check=True)
 print('SE521_MEASURED_BYTES',len(raw),flush=True)
 print('SE521_MEASURED_SHA256',hashlib.sha256(raw).hexdigest(),flush=True)
finally:
 p.write_text(original,encoding='utf8')
