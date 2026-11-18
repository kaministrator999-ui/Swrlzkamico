#!/usr/bin/env python3
"""Seal §E v11.505: test safe native prerequisites, build exact bytes, pin SHA."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'source-manifest.json'
m=json.loads(manifest.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.504',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_504.html'
assert len(m['patches'])==481
assert m['patches'][-1]=='patches/v11_504_smooth_witch_hat.py'
for file in (
 'runtime/model_action_prerequisites_v11_505.js',
 'patches/v11_505_action_prerequisites.py',
 'tests/model_action_prerequisites_v11_505.cjs',
):
 assert (ROOT/file).is_file(),file
for file in ('runtime/model_action_prerequisites_v11_505.js',):
 subprocess.run(['node','--check',str(ROOT/file)],check=True)
subprocess.run([sys.executable,'-m','py_compile',
 str(ROOT/'patches/v11_505_action_prerequisites.py')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_action_prerequisites_v11_505.cjs')],check=True)
subprocess.run([sys.executable,str(ROOT/'tests/source_release_notes_baseline_v11_505.py')],check=True)
m['name']='§wyrl§ Engine v11.505'
m['finalArtifact']='swyrl_engine_v11_505.html'
m['patches'].append('patches/v11_505_action_prerequisites.py')
m['releaseNotesBaseline']={'version':'v11.504','patchCount':481}
m['finalBytes']=None
m['finalSha256']=None
manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='se505-prerequisites-seal-') as temp:
 out=Path(temp)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'SE505_ACTION_PREREQUISITES_START' in raw
 assert b'SWYRLZ_E_REQUIREMENTS_505' in raw
 assert b'V11_505_ACTION_PREREQUISITES' in raw
 assert b'SE503_UV_ISLAND_UI_START' in raw
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_505_release.py'),
                 '--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_505.py'),
                 '--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.505.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print('SE505_PREREQUISITES_SEALED',json.dumps({
  'sha256':m['finalSha256'],'bytes':m['finalBytes'],
  'patches':len(m['patches']),
  'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
