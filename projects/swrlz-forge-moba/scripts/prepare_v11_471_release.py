#!/usr/bin/env python3
"""Seal §E v11.471 from the real source bytes, then verify before publication."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manifest_file=ROOT/'source-manifest.json'
request_file=ROOT/'DEPLOY_REQUEST.json'
manifest=json.loads(manifest_file.read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.471'
assert manifest['finalArtifact']=='swyrl_engine_v11_471.html'
assert len(manifest['patches'])==448
assert manifest['patches'][-1]=='patches/v11_471_uv_render_project_delete.py'
manifest['finalBytes']=None
manifest['finalSha256']=None
manifest_file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
output=ROOT/'_release_v11_471_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
data=(output/'index.html').read_bytes()
assert data==(output/'modeler.html').read_bytes()
manifest['finalBytes']=len(data)
manifest['finalSha256']=hashlib.sha256(data).hexdigest()
manifest_file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
request=json.loads(request_file.read_text('utf8'))
request.update({
 'requestedBy':'ChatGPT (owner-approved)',
 'target':'kamiloki/swrlz-forge-moba',
 'releaseVersion':'v11.471',
 'deployMarker':'SWYRL_ENGINE_DEPLOY_MARKER: V11_471_UV_VISIBLE_PROJECT_DELETE',
 'reason':'Select authored Material view after UV texture import; add opt-in latitude-aware and manual U/V fit; local/account project deletion confirmation with storage receipt validation. No account records removed automatically. Real device acceptance pending.',
 'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'sourceIntegritySha256':manifest['finalSha256']
})
request_file.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_471_release.py'),
 '--output',str(ROOT/'_release_v11_471_verified'),'--request'],check=True)
print(json.dumps({'status':'SEALED','version':'v11.471','bytes':len(data),
 'sha256':manifest['finalSha256'],'patches':448}),flush=True)
