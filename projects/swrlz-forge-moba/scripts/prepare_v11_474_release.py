#!/usr/bin/env python3
"""Measure and seal §E v11.474 using the canonical ordered 451-patch build."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/'source-manifest.json'
m=json.loads(manifest_path.read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.474'
assert m['finalArtifact']=='swyrl_engine_v11_474.html'
assert len(m['patches'])==451 and m['patches'][-1]=='patches/v11_474_progressive_model_tools.py'
for name in ('model_progressive_tools_v11_474.js','model_progressive_tools_v11_474.css'):
 assert (ROOT/'runtime'/name).is_file()
subprocess.run(['node','--check',str(ROOT/'runtime/model_progressive_tools_v11_474.js')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_progressive_tools_v11_474.mjs')],check=True)
m['finalBytes']=None
m['finalSha256']=None
manifest_path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
out=ROOT/'_release_v11_474_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
built=(out/'index.html').read_bytes()
assert built==(out/'modeler.html').read_bytes()
m['finalBytes']=len(built)
m['finalSha256']=hashlib.sha256(built).hexdigest()
manifest_path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_474_release.py'),
 '--output',str(ROOT/'_release_v11_474_verified')],check=True)
print('SE474_MEASURED_RECEIPT='+json.dumps({
 'version':'v11.474','bytes':m['finalBytes'],'sha256':m['finalSha256'],
 'patches':len(m['patches'])
},sort_keys=True),flush=True)
