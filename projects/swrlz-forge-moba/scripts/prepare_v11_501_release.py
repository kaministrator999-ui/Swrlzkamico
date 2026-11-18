#!/usr/bin/env python3
"""§E v11.501: seal the actual UV diagnostic source after tests and packaging."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source-manifest.json'
m=json.loads(path.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.500',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_500.html'
assert len(m['patches'])==477
assert m['patches'][-1]=='patches/v11_500_connected_rig_weights.py'
for p in ('runtime/model_uv_heatmap_export_v11_501.js',
          'runtime/model_uv_heatmap_export_v11_501.css',
          'patches/v11_501_uv_diagnostic_exports.py',
          'tests/model_uv_heatmap_export_v11_501.cjs'):
 assert (ROOT/p).is_file(),p
subprocess.run(['node','--check',str(ROOT/'runtime/model_uv_heatmap_export_v11_501.js')],check=True)
subprocess.run([sys.executable,'-m','py_compile',str(ROOT/'patches/v11_501_uv_diagnostic_exports.py')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_uv_heatmap_export_v11_501.cjs')],check=True)
m['name']='§wyrl§ Engine v11.501'
m['finalArtifact']='swyrl_engine_v11_501.html'
m['patches'].append('patches/v11_501_uv_diagnostic_exports.py')
m['finalBytes']=None;m['finalSha256']=None
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='engine-uv-diagnostics-501-') as folder:
 out=Path(folder)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 for needle in (b'SE501_UV_HEATMAP_EXPORT_START',b'data-se501-export="overlay"',
                b'V11_501_UV_DIAGNOSTIC_EXPORTS',b'se501UV'):
  assert needle in raw,needle
 m['finalBytes']=len(raw);m['finalSha256']=hashlib.sha256(raw).hexdigest()
 path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_501_release.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_501.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.501.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print(json.dumps({'status':'SE501_UV_DIAGNOSTICS_SEALED','sha256':m['finalSha256'],
   'bytes':m['finalBytes'],'patches':len(m['patches']),
   'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
