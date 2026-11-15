#!/usr/bin/env python3
"""Prepare a real verified v11.465 compiled HTML receipt with no guessed hashes."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'source-manifest.json'
m=json.loads(p.read_text())
assert m['name']=='§wyrl§ Engine v11.464'
assert len(m['patches'])==441 and m['patches'][-1]=='patches/v11_464_model_visual_inspector.py'
new='patches/v11_465_inspector_readability.py'
assert (ROOT/new).is_file()
m['name']='§wyrl§ Engine v11.465'
m['finalArtifact']='swyrl_engine_v11_465.html'
m['patches'].append(new)
m['finalSha256']=None;m['finalBytes']=None
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
out=ROOT/'_release_v11_465_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
b=(out/'index.html').read_bytes()
assert b==(out/'modeler.html').read_bytes()
m['finalBytes']=len(b);m['finalSha256']=hashlib.sha256(b).hexdigest()
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_465_release.py'),
                '--output',str(ROOT/'_release_v11_465_verified')],check=True)
print(json.dumps({'sealed':'v11.465','bytes':len(b),'sha256':m['finalSha256'],
                  'patches':len(m['patches'])}),flush=True)
