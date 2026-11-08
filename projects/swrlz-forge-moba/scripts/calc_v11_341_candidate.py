#!/usr/bin/env python3
"""Compute the exact v11.341 candidate HTML seal without changing main."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/'source-manifest.json'
manifest=json.loads(manifest_path.read_text('utf8'))
assert manifest['name']=='§wyrl§ Engine v11.340'
assert manifest['patches'][-1]=='patches/v11_340_immersive_model_studio.py'
manifest['name']='§wyrl§ Engine v11.341'
manifest['finalArtifact']='swyrl_engine_v11_341.html'
manifest['patches'].append('patches/v11_341_model_vr_hover_orbit.py')
# The build prints actual computed integrity before it is committed as source
# truth. A missing expected hash is allowed only in this ephemeral candidate.
manifest['finalSha256']=''
manifest['finalBytes']=0
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
dist=ROOT/'_candidate_v11_341'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(dist)],check=True)
data=(dist/'index.html').read_bytes()
assert data==(dist/'modeler.html').read_bytes()
assert b'V11_341_MODEL_VR_HOVER_ORBIT' in data
assert b'record.nextHoverAt=now+55' in data
assert b'cast.ray.intersectsBox' in data
print('V11_341_FINAL_BYTES='+str(len(data)),flush=True)
print('V11_341_FINAL_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
print('V11_341_PATCH_COUNT='+str(len(manifest['patches'])),flush=True)
