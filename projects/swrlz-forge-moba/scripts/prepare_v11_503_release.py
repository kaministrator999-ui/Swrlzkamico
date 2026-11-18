#!/usr/bin/env python3
"""Seal §E v11.503: test real hat seam-UV atlas, build exact bytes, pin SHA."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'source-manifest.json'
m=json.loads(manifest.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.502',m['name']
assert m['finalArtifact']=='swyrl_engine_v11_502.html'
assert len(m['patches'])==479
assert m['patches'][-1]=='patches/v11_502_uv_touch_resize.py'
for file in (
 'runtime/model_uv_island_math_v11_503.js',
 'runtime/model_uv_island_ui_v11_503.js',
 'runtime/model_uv_island_v11_503.css',
 'patches/v11_503_uv_island_atlas.py',
 'tests/model_uv_island_atlas_v11_503.cjs',
):
 assert (ROOT/file).is_file(),file
for file in ('runtime/model_uv_island_math_v11_503.js',
             'runtime/model_uv_island_ui_v11_503.js'):
 subprocess.run(['node','--check',str(ROOT/file)],check=True)
subprocess.run([sys.executable,'-m','py_compile',
 str(ROOT/'patches/v11_503_uv_island_atlas.py')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_uv_island_atlas_v11_503.cjs')],check=True)
m['name']='§wyrl§ Engine v11.503'
m['finalArtifact']='swyrl_engine_v11_503.html'
m['patches'].append('patches/v11_503_uv_island_atlas.py')
m['finalBytes']=None
m['finalSha256']=None
manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
with tempfile.TemporaryDirectory(prefix='se503-uv-island-seal-') as temp:
 out=Path(temp)/'dist'
 subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert raw==(out/'modeler.html').read_bytes()
 assert b'SE503_UV_ISLAND_MATH_START' in raw
 assert b'SE503_UV_ISLAND_UI_START' in raw
 assert b'V11_503_UV_ISLAND_ATLAS' in raw
 assert b'SE502_UV_TOUCH_RESIZE_START' in raw
 m['finalBytes']=len(raw)
 m['finalSha256']=hashlib.sha256(raw).hexdigest()
 manifest.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n','utf8')
 subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_503_release.py'),
                 '--output',str(out)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/package_static_delivery_v11_503.py'),
                 '--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.503.js')],check=True)
 receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
 assert receipt['sourceVersion']==m['name']
 assert receipt['finalSha256']==m['finalSha256']
 assert receipt['staticDelivery']['verifiedSourceSha256']==m['finalSha256']
 print('SE503_UV_ATLAS_SEALED',json.dumps({
  'sha256':m['finalSha256'],'bytes':m['finalBytes'],
  'patches':len(m['patches']),
  'moduleBytes':receipt['staticDelivery']['moduleBytes']}),flush=True)
