#!/usr/bin/env python3
"""Seal v11.507 without weakening the v11.505 inherited integrity checks."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
root=Path(__file__).resolve().parents[1]
manifest=root/'source-manifest.json'
m=json.loads(manifest.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.507'
assert m['patches'][-2:]==['patches/v11_506_uv_button_ownership.py','patches/v11_507_model_tool_rail_recovery.py']
assert len(m['patches'])==484
assert m['finalSha256'] is None and m['finalBytes'] is None
subprocess.run([sys.executable,str(root/'tests/model_tool_rail_recovery_v11_507.py')],check=True)
subprocess.run([sys.executable,'-m','py_compile',str(root/'patches/v11_507_model_tool_rail_recovery.py')],check=True)
with tempfile.TemporaryDirectory(prefix='se507-rail-') as tmp:
 out=Path(tmp)/'dist'
 subprocess.run([sys.executable,str(root/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'V11_507_MODEL_TOOL_RAIL_RECOVERY' in raw
 assert b'SE507_MODEL_TOOL_RAIL_RECOVERY_STYLES_END' in raw
 assert b'SE505_ACTION_PREREQUISITES_START' in raw
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(root/'build_space.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(root/'scripts/package_static_delivery_v11_507.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.507.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print('SE507_RAIL_SEALED',json.dumps({'sha256':m['finalSha256'],'bytes':m['finalBytes'],'patches':len(m['patches'])}),flush=True)
