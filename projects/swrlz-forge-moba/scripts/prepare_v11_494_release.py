#!/usr/bin/env python3
"""§E v11.494: test cloud update recovery, seal exact browser bytes, package for HF."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source-manifest.json'
m=json.loads(path.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.493',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_493.html'
assert len(m['patches'])==470 and m['patches'][-1]=='patches/v11_493_project_load_diagnostics.py'
for p in ('runtime/model_update_account_workflow_v11_494.js',
          'patches/v11_494_model_update_lifecycle.py',
          'tests/model_update_lifecycle_v11_494.cjs'):
 assert (ROOT/p).is_file(),p
for name in ('model_update_account_workflow_v11_494.js',):
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_project_exports_v11_487.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/account_project_naming_v11_488.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/cloth_rig_project_update_v11_489.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_rig_workspace_v11_490.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/cloud_model_update_recovery_v11_491.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/zip_model_update_v11_492.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/project_load_diagnostics_v11_493.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_update_lifecycle_v11_494.cjs')],check=True)
m['name']='§wyrl§ Engine v11.494'
m['finalArtifact']='swyrl_engine_v11_494.html'
m['patches'].append('patches/v11_494_model_update_lifecycle.py')
m['finalBytes']=None;m['finalSha256']=None
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='engine-update-494-') as folder:
 out=Path(folder)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'V11_494_MODEL_UPDATE_LIFECYCLE' in raw
 assert b'SWYRL_ENGINE_PROJECT_LOAD_493' in raw
 assert b'se494TrustedLoadCache' in raw
 assert b'SWYRL_ENGINE_CLOTH_RIG_489' in raw
 assert b'se487ExportStem()' in raw
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_494_release.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_494.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.494.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print(json.dumps({'status':'SE494_MODEL_UPDATE_LIFECYCLE_SEALED',
  'sha256':m['finalSha256'],'bytes':m['finalBytes'],
  'patches':len(m['patches']),
  'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
