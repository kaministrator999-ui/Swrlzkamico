#!/usr/bin/env python3
"""§E v11.486: seal the real generated source and validate versioned projects."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source-manifest.json'
m=json.loads(path.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.485',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_485.html'
assert len(m['patches'])==462 and m['patches'][-1]=='patches/v11_485_one_cloth_sorting_hat.py'
for p in ('runtime/project_revisions_v11_486.js','runtime/project_revision_actions_v11_486.js',
          'runtime/studio_asset_revisions_v11_486.js','patches/v11_486_project_revisions.py',
          'tests/project_revisions_v11_486.cjs'):
 assert (ROOT/p).is_file(),p
for name in ('project_revisions_v11_486.js','project_revision_actions_v11_486.js',
             'studio_asset_revisions_v11_486.js'):
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/project_revisions_v11_486.cjs')],check=True)
m['name']='§wyrl§ Engine v11.486'
m['finalArtifact']='swyrl_engine_v11_486.html'
m['patches'].append('patches/v11_486_project_revisions.py')
m['finalBytes']=None;m['finalSha256']=None
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='engine-revisions-486-') as folder:
 out=Path(folder)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'V11_486_PROJECT_REVISIONS' in raw
 assert b'SWYRL_ENGINE_REVISIONS_486' in raw
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_486_release.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_486.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.486.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name'] and receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print(json.dumps({'status':'SE486_SEALED','sha256':m['finalSha256'],
                   'bytes':m['finalBytes'],'patches':len(m['patches']),
                   'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
