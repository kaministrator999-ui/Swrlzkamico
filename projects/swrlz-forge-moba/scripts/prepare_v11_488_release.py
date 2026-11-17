#!/usr/bin/env python3
"""§E v11.488: test named exports, seal real build bytes, and package for HF."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source-manifest.json'
m=json.loads(path.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.487',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_487.html'
assert len(m['patches'])==464 and m['patches'][-1]=='patches/v11_487_model_project_exports.py'
for p in ('runtime/model_export_identity_v11_487.js',
          'runtime/my_projects_export_v11_487.js',
          'patches/v11_487_model_project_exports.py',
          'tests/model_project_exports_v11_487.cjs'):
 assert (ROOT/p).is_file(),p
for name in ('model_export_identity_v11_487.js','my_projects_export_v11_487.js'):
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_project_exports_v11_487.cjs')],check=True)
m['name']='§wyrl§ Engine v11.488'
m['finalArtifact']='swyrl_engine_v11_487.html'
m['patches'].append('patches/v11_487_model_project_exports.py')
m['finalBytes']=None;m['finalSha256']=None
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='engine-exports-487-') as folder:
 out=Path(folder)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'V11_488_ACCOUNT_PROJECT_NAMING' in raw
 assert b'SWYRL_ENGINE_MY_PROJECTS_EXPORT_487' in raw
 assert b'se487ExportStem()' in raw
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_487_release.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_487.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.488.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print(json.dumps({'status':'SE488_ACCOUNT_NAMING_SEALED',
  'sha256':m['finalSha256'],'bytes':m['finalBytes'],
  'patches':len(m['patches']),
  'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
