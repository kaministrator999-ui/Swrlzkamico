#!/usr/bin/env python3
"""Prepare §E v11.467 from canonical source and measure its actual built bytes."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'source-manifest.json'
m=json.loads(p.read_text('utf8'))
new='patches/v11_467_vr_grip_release.py'
assert (ROOT/new).is_file()
assert m['name']=='§wyrl§ Engine v11.467' and len(m['patches'])==444
assert m['patches'][-1]=='patches/v11_467_vr_grip_release.py'
m['finalBytes']=None;m['finalSha256']=None
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
out=ROOT/'_release_v11_467_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
built=(out/'index.html').read_bytes()
assert built==(out/'modeler.html').read_bytes()
m['finalBytes']=len(built);m['finalSha256']=hashlib.sha256(built).hexdigest()
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_467_release.py'),'--output',str(ROOT/'_release_v11_467_verified')],check=True)
print(json.dumps({'sealed':'v11.467','bytes':len(built),'sha256':m['finalSha256'],'patches':len(m['patches'])}),flush=True)
