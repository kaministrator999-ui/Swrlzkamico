#!/usr/bin/env python3
"""Prepare §E v11.443 from its real generated artifact; never invent its hash."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/'source-manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
patch='patches/v11_443_model_vr_vertical_dock.py'
if manifest['name']!='§wyrl§ Engine v11.442' or manifest['patches'][-1]!='patches/v11_442_satchel_mobile_dialog.py':
    raise SystemExit('Refusing to seal an unexpected or already-changed engine manifest')
if not (ROOT/patch).is_file():
    raise SystemExit('Missing v11.443 source patch')
manifest['name']='§wyrl§ Engine v11.443'
manifest['finalArtifact']='swyrl_engine_v11_443.html'
manifest['patches'].append(patch)
manifest['finalSha256']=None
manifest['finalBytes']=None
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
output=ROOT/'_release_v11_443_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes()
assert data==(output/'modeler.html').read_bytes()
manifest['finalBytes']=len(data)
manifest['finalSha256']=hashlib.sha256(data).hexdigest()
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_443_release.py'),'--output',str(ROOT/'_release_v11_443_verified')],check=True)
print(json.dumps({'version':'v11.443','bytes':len(data),'sha256':manifest['finalSha256'],'patches':len(manifest['patches']),'verified':True}))
