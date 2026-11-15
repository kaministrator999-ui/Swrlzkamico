#!/usr/bin/env python3
"""Calculate actual v11.462 compiled HTML receipt; fail closed on drift."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'source-manifest.json'
m=json.loads(p.read_text())
assert m['name']=='§wyrl§ Engine v11.461'
assert len(m['patches'])==438 and m['patches'][-1]=='patches/v11_461_model_edges_orbit_dock.py'
new='patches/v11_462_model_wire_clarity.py'
assert (ROOT/new).is_file()
m['name']='§wyrl§ Engine v11.462'
m['finalArtifact']='swyrl_engine_v11_462.html'
m['patches'].append(new)
m['finalSha256']=None;m['finalBytes']=None
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
out=ROOT/'_release_v11_462_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
b=(out/'index.html').read_bytes()
assert b==(out/'modeler.html').read_bytes()
m['finalBytes']=len(b);m['finalSha256']=hashlib.sha256(b).hexdigest()
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_462_release.py'),
                '--output',str(ROOT/'_release_v11_462_verified')],check=True)
print(json.dumps({'sealed':'v11.462','bytes':len(b),'sha256':m['finalSha256'],'patches':len(m['patches'])}),flush=True)
