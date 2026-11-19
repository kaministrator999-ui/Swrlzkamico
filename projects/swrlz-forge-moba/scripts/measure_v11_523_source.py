#!/usr/bin/env python3
"""Measure v11.523 candidate on a disposable CI runner; never deploy unsealed source."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'source-manifest.json';original=path.read_text('utf8')
m=json.loads(original)
assert m['name']=='§wyrl§ Engine v11.523' and len(m['patches'])==500
assert m['patches'][-1]=='patches/v11_523_sculpt_direction_cleanup.py'
m['finalBytes']=0;m['finalSha256']=''
try:
 path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
 with tempfile.TemporaryDirectory(prefix='se523-candidate-') as tmp:
  subprocess.run([sys.executable,str(root/'build_space.py'),'--output',tmp],check=True)
  data=(Path(tmp)/'index.html').read_bytes()
  assert data==(Path(tmp)/'modeler.html').read_bytes()
  assert b'V11_523_SCULPT_DIRECTION_CLEANUP' in data
  subprocess.run(['node',str(root/'tests/model_vr_sculpt_menu_v11_523.cjs'),str(Path(tmp)/'index.html')],check=True)
  subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(Path(tmp)/'index.html')],check=True)
  print('SE523_MEASURED_BYTES='+str(len(data)),flush=True)
  print('SE523_MEASURED_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
finally:path.write_text(original,encoding='utf8')
