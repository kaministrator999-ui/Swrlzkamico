#!/usr/bin/env python3
"""Measure §E v11.527 Draw in a disposable CI directory; do not deploy unsealed output."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=root/'source-manifest.json';original=manifest.read_text('utf8')
m=json.loads(original)
assert m['name']=='§wyrl§ Engine v11.527'
assert m['finalArtifact']=='swyrl_engine_v11_527.html'
assert len(m['patches'])==504 and m['patches'][-1]=='patches/v11_527_draw_menu_cleanup.py'
m['finalBytes']=0;m['finalSha256']=''
try:
 manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
 with tempfile.TemporaryDirectory(prefix='se527-draw-measure-') as tmp:
  subprocess.run([sys.executable,str(root/'build_space.py'),'--output',tmp],check=True)
  page=Path(tmp)/'index.html'
  raw=page.read_bytes()
  assert raw==(Path(tmp)/'modeler.html').read_bytes()
  assert b'V11_527_DRAW_MENU_CLEANUP' in raw
  subprocess.run(['node',str(root/'tests/model_vr_draw_menu_v11_527.cjs'),str(page)],check=True)
  subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(page)],check=True)
  print('SE527_MEASURED_BYTES='+str(len(raw)),flush=True)
  print('SE527_MEASURED_SHA256='+hashlib.sha256(raw).hexdigest(),flush=True)
finally:manifest.write_text(original,encoding='utf8')
