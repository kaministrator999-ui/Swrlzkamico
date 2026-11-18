#!/usr/bin/env python3
"""Build and seal §E v11.507, including real assembled DOM state regression."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'source-manifest.json'
m=json.loads(manifest.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.506',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_506.html'
assert m['finalSha256']=='01d4daf1780e8938a6f8d2ef1f0c94744be5a978171124f0ef51613037beedba'
assert len(m['patches'])==483
assert m['patches'][-1]=='patches/v11_506_uv_button_ownership.py'
assert m.get('releaseNotesBaseline')=={'version':'v11.504','patchCount':481}
for file in ('patches/v11_507_uv_degenerate_preview.py','tests/uv_degenerate_preview_v11_507.cjs'):
 assert (ROOT/file).is_file(),file
subprocess.run([sys.executable,'-m','py_compile',str(ROOT/'patches/v11_507_uv_degenerate_preview.py')],check=True)
subprocess.run(['node','--check',str(ROOT/'tests/uv_degenerate_preview_v11_507.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_action_prerequisites_v11_505.cjs')],check=True)
m['name']='§wyrl§ Engine v11.507'
m['finalArtifact']='swyrl_engine_v11_507.html'
m['patches'].append('patches/v11_507_uv_degenerate_preview.py')
m['finalBytes']=None;m['finalSha256']=None
manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='se507-uv-degenerate-') as temp:
 out=Path(temp)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'V11_507_UV_DEGENERATE_PREVIEW' in raw
 subprocess.run(['node',str(ROOT/'tests/uv_degenerate_preview_v11_507.cjs'),str(out/'index.html')],check=True)
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_507_release.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_507.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.507.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print('SE507_UV_DEGENERATE_PREVIEW_SEALED',json.dumps({
  'sha256':m['finalSha256'],'bytes':m['finalBytes'],'patches':len(m['patches']),
  'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
