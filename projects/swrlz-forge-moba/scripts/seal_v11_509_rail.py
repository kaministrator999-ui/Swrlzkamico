from pathlib import Path
import json,hashlib,subprocess,sys,tempfile
r=Path(__file__).resolve().parents[1]
p=r/'source-manifest.json';m=json.loads(p.read_text())
assert m['name']=='§wyrl§ Engine v11.509' and len(m['patches'])==486
assert m['patches'][-2:]==['patches/v11_508_uv_degenerate_preview.py','patches/v11_509_rail_reexpand.py']
assert m['finalSha256'] is None and m['finalBytes'] is None
subprocess.run([sys.executable,'-m','py_compile',str(r/'patches/v11_509_rail_reexpand.py')],check=True)
with tempfile.TemporaryDirectory() as d:
 out=Path(d)/'dist'
 subprocess.run([sys.executable,str(r/'build_space.py'),'--output',str(out)],check=True)
 raw=(out/'index.html').read_bytes()
 assert b'V11_509_RAIL_REEXPAND' in raw and b'SE509_RAIL_REEXPAND_END' in raw
 assert raw==(out/'modeler.html').read_bytes()
 m['finalBytes']=len(raw);m['finalSha256']=hashlib.sha256(raw).hexdigest()
 p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
 subprocess.run([sys.executable,str(r/'build_space.py'),'--output',str(out)],check=True)
 subprocess.run([sys.executable,str(r/'scripts/package_static_delivery_v11_509.py'),'--output',str(out)],check=True)
 subprocess.run(['node','--check',str(out/'swrlz-engine-v11.509.js')],check=True)
 print('SE509_RAIL_REEXPAND_SEALED',m['finalSha256'])
