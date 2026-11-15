#!/usr/bin/env python3
"""Seal §E v11.455 top Inset rim-to-depth workflow from sealed v11.453 source."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source-manifest.json'
m=json.loads(path.read_text(encoding='utf8'))
prior='patches/v11_454_inset_top_steps.py'
addon='patches/v11_455_model_view_readability.py'
if m['name']!='§wyrl§ Engine v11.454' or m['patches'][-1]!=prior:
 raise SystemExit('Refuse release: v11.454 sealed source not present')
if not (ROOT/addon).is_file():raise SystemExit('Missing viewport readability patch')
m['name']='§wyrl§ Engine v11.455'
m['finalArtifact']='swyrl_engine_v11_455.html'
m['patches'].append(addon)
m['finalSha256']=None;m['finalBytes']=None
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
out=ROOT/'_release_v11_455_candidate'
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
if data!=(out/'modeler.html').read_bytes():raise SystemExit('Two engine page sources diverged')
m['finalBytes']=len(data);m['finalSha256']=hashlib.sha256(data).hexdigest()
path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/verify_v11_455_release.py'),'--output',str(ROOT/'_release_v11_455_verified')],check=True)
print(json.dumps({'release':'v11.455','sealed':True,'sha256':m['finalSha256'],
 'bytes':m['finalBytes'],'patches':len(m['patches'])}),flush=True)
