#!/usr/bin/env python3
"""Measure the v11.522 candidate without altering the committed sealed manifest.
Only the runner's temporary manifest is unsealed; never deploy that temporary build.
"""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
# This source build validates Sculpt settings as exposed in the current native menu.
root=Path(__file__).resolve().parents[1]
path=root/'source-manifest.json'
original=path.read_text('utf8')
m=json.loads(original)
assert m['name']=='§wyrl§ Engine v11.522'
assert m['finalSha256']=='aa536fec22cbd598d88374e26a57b2d2f4de30521c86826cbcbd90856fe916c9'
assert len(m['patches'])==499
assert m['patches'][-1]=='patches/v11_522_sculpt_brush_menu.py'
m['finalBytes']=0
m['finalSha256']=''
try:
 path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
 with tempfile.TemporaryDirectory(prefix='se522-measure-') as tmp:
  subprocess.run([sys.executable,str(root/'build_space.py'),'--output',tmp],check=True)
  data=(Path(tmp)/'index.html').read_bytes()
  assert data==(Path(tmp)/'modeler.html').read_bytes()
  assert '<title>§wyrl§ Engine · Maker v11.522</title>'.encode('utf8') in data
  subprocess.run(['node',str(root/'tests/model_vr_sculpt_menu_v11_522.cjs'),str(Path(tmp)/'index.html')],check=True)
  subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(Path(tmp)/'index.html')],check=True)
  print('SE522_MEASURED_BYTES='+str(len(data)),flush=True)
  print('SE522_MEASURED_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
finally:
 path.write_text(original,encoding='utf8')
