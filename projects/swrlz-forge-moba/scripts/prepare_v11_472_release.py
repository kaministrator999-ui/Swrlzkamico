#!/usr/bin/env python3
"""Seal §E v11.472 from the real source bytes, then verify before publication."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manifest_file=ROOT/'source-manifest.json'
request_file=ROOT/'DEPLOY_REQUEST.json'
manifest=json.loads(manifest_file.read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.472'
assert manifest['finalArtifact']=='swyrl_engine_v11_471.html'
assert len(manifest['patches'])==449
assert manifest['patches'][-1]=='patches/v11_472_full_resolution_textures.py'
manifest['finalBytes']=None
manifest['finalSha256']=None
manifest_file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
output=ROOT/'_release_v11_472_candidate'
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
 'releaseVersion':'v11.472',
 'deployMarker':'SWYRL_ENGINE_DEPLOY_MARKER: V11_472_FULL_RES_TEXTURES',
 'reason':'Keep imported PNG/JPEG bytes and original resolution; add user-selected GPU display sizes 4096/2048/1024/512/256, preserving account source and UV adjustments. Existing project/account limit unchanged. Requires Android/Quest acceptance.',
 'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'sourceIntegritySha256':manifest['finalSha256']
})
request_file.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n','utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_472_release.py'),
 '--output',str(ROOT/'_release_v11_472_verified'),'--request'],check=True)
print(json.dumps({'status':'SEALED','version':'v11.472','bytes':len(data),
 'sha256':manifest['finalSha256'],'patches':449}),flush=True)
