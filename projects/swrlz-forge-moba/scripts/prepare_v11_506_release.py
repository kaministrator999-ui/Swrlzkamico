#!/usr/bin/env python3
"""Build and seal §E v11.506, including real assembled DOM state regression."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'source-manifest.json'
m=json.loads(manifest.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.505',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_505.html'
assert m['finalSha256']=='f79e880e7c6c780fa06dd8ac6d969763faa17e656c41e5508950a832e970c43e'
assert len(m['patches'])==482
assert m['patches'][-1]=='patches/v11_505_action_prerequisites.py'
assert m.get('releaseNotesBaseline')=={'version':'v11.504','patchCount':481}
for file in ('patches/v11_506_uv_button_ownership.py','tests/uv_button_ownership_v11_506.cjs'):
 assert (ROOT/file).is_file(),file
subprocess.run([sys.executable,'-m','py_compile',str(ROOT/'patches/v11_506_uv_button_ownership.py')],check=True)
subprocess.run(['node','--check',str(ROOT/'tests/uv_button_ownership_v11_506.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_action_prerequisites_v11_505.cjs')],check=True)
m['name']='§wyrl§ Engine v11.506'
m['finalArtifact']='swyrl_engine_v11_506.html'
m['patches'].append('patches/v11_506_uv_button_ownership.py')
m['finalBytes']=None;m['finalSha256']=None
manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='se506-uv-buttons-') as temp:
 out=Path(temp)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'V11_506_UV_BUTTON_OWNERSHIP' in raw
 subprocess.run(['node',str(ROOT/'tests/uv_button_ownership_v11_506.cjs'),str(out/'index.html')],check=True)
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_506_release.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_506.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.506.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print('SE506_UV_BUTTONS_SEALED',json.dumps({
  'sha256':m['finalSha256'],'bytes':m['finalBytes'],'patches':len(m['patches']),
  'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
