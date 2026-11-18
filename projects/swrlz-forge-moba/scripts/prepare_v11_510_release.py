#!/usr/bin/env python3
"""Build and seal §E v11.510, including real assembled DOM state regression."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'source-manifest.json'
m=json.loads(manifest.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.509',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_509.html'
assert m['finalSha256']=='26367c6cc6273c1017aeaa2a428ce5c51cf21a50a637adaf7067fab3f9c1b03e'
assert len(m['patches'])==486
assert m['patches'][-1]=='patches/v11_509_rail_reexpand.py'
assert m.get('releaseNotesBaseline')=={'version':'v11.504','patchCount':481}
for file in ('patches/v11_510_cone_aware_uv.py','tests/model_uv_cone_aware_v11_510.cjs'):
 assert (ROOT/file).is_file(),file
subprocess.run([sys.executable,'-m','py_compile',str(ROOT/'patches/v11_510_cone_aware_uv.py')],check=True)
subprocess.run(['node','--check',str(ROOT/'tests/model_uv_cone_aware_v11_510.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_action_prerequisites_v11_505.cjs')],check=True)
subprocess.run(['node','--check',str(ROOT/'runtime/model_uv_cone_metric_v11_510.js')],check=True)
m['name']='§wyrl§ Engine v11.510'
m['finalArtifact']='swyrl_engine_v11_510.html'
m['patches'].append('patches/v11_510_cone_aware_uv.py')
m['finalBytes']=None;m['finalSha256']=None
manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='se510-uv-degenerate-') as temp:
 out=Path(temp)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'V11_510_CONE_AWARE_UV' in raw
 subprocess.run(['node',str(ROOT/'tests/model_uv_cone_aware_v11_510.cjs'),str(out/'index.html')],check=True)
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_510_release.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_510.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.510.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print('SE510_CONE_AWARE_UV_SEALED',json.dumps({
  'sha256':m['finalSha256'],'bytes':m['finalBytes'],'patches':len(m['patches']),
  'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
