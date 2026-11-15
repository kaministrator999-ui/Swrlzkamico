#!/usr/bin/env python3
"""Seal §E v11.453 native three-stage flyout source after v11.451 approval."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source-manifest.json'
m=json.loads(path.read_text(encoding='utf8'))
prior='patches/v11_452_native_face_flyouts.py'
addon='patches/v11_453_inset_rim_width.py'
if m['name']!='§wyrl§ Engine v11.452' or m['patches'][-1]!=prior:
 raise SystemExit('Refuse release: v11.452 sealed source not present')
if not (ROOT/addon).is_file():raise SystemExit('Missing Inset rim patch')
m['name']='§wyrl§ Engine v11.453'
m['finalArtifact']='swyrl_engine_v11_453.html'
m['patches'].append(addon)
m['finalSha256']=None;m['finalBytes']=None
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
out=ROOT/'_release_v11_453_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
if data!=(out/'modeler.html').read_bytes():raise SystemExit('Two engine page sources diverged')
m['finalBytes']=len(data);m['finalSha256']=hashlib.sha256(data).hexdigest()
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_453_release.py'),'--output',str(ROOT/'_release_v11_453_verified')],check=True)
print(json.dumps({'release':'v11.453','sealed':True,'sha256':m['finalSha256'],
 'bytes':m['finalBytes'],'patches':len(m['patches'])}),flush=True)
