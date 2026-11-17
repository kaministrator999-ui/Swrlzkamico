#!/usr/bin/env python3
"""§E v11.492: test cloud update recovery, seal exact browser bytes, package for HF."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source-manifest.json'
m=json.loads(path.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.491',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_491.html'
assert len(m['patches'])==468 and m['patches'][-1]=='patches/v11_491_cloud_model_update_recovery.py'
for p in ('runtime/model_zip_update_v11_492.js',
          'patches/v11_492_zip_model_updates.py',
          'tests/zip_model_update_v11_492.cjs'):
 assert (ROOT/p).is_file(),p
for name in ('model_zip_update_v11_492.js',):
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_project_exports_v11_487.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/account_project_naming_v11_488.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/cloth_rig_project_update_v11_489.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_rig_workspace_v11_490.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/cloud_model_update_recovery_v11_491.cjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/zip_model_update_v11_492.cjs')],check=True)
m['name']='§wyrl§ Engine v11.492'
m['finalArtifact']='swyrl_engine_v11_492.html'
m['patches'].append('patches/v11_492_zip_model_updates.py')
m['finalBytes']=None;m['finalSha256']=None
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='engine-zip-model-update-492-') as folder:
 out=Path(folder)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'V11_492_ZIP_MODEL_UPDATES' in raw
 assert b'SWYRL_ENGINE_ZIP_UPDATES_492' in raw
 assert b'SWYRL_ENGINE_CLOTH_RIG_489' in raw
 assert b'se487ExportStem()' in raw
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_492_release.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_492.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.492.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print(json.dumps({'status':'SE492_ZIP_MODEL_UPDATE_SEALED',
  'sha256':m['finalSha256'],'bytes':m['finalBytes'],
  'patches':len(m['patches']),
  'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
