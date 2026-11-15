#!/usr/bin/env python3
"""Build, calculate and verify exact §E v11.450 source before sealing."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/'source-manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
patch='patches/v11_450_camera_inset_preview.py'
if manifest['name']!='§wyrl§ Engine v11.449' or manifest['patches'][-1]!='patches/v11_449_model_touch_layout.py':
    raise SystemExit('Refusing to seal unexpected engine manifest')
if not (ROOT/patch).is_file():raise SystemExit('Missing camera and Inset visibility patch')
manifest['name']='§wyrl§ Engine v11.450'
manifest['finalArtifact']='swyrl_engine_v11_450.html'
manifest['patches'].append(patch)
# Temporary only in this runner checkout; never commit unsealed receipt.
manifest['finalSha256']=None;manifest['finalBytes']=None
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
output=ROOT/'_release_v11_450_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes()
assert data==(output/'modeler.html').read_bytes()
manifest['finalBytes']=len(data)
manifest['finalSha256']=hashlib.sha256(data).hexdigest()
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_450_release.py'),'--output',str(ROOT/'_release_v11_450_verified')],check=True)
print(json.dumps({'version':'v11.450','bytes':len(data),'sha256':manifest['finalSha256'],'patches':len(manifest['patches']),'verified':True}),flush=True)
