#!/usr/bin/env python3
"""Measure native Select v11.524 on disposable CI workspace, never deploy unsealed HTML."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'source-manifest.json';original=path.read_text('utf8')
m=json.loads(original)
assert m['name']=='§wyrl§ Engine v11.524'
assert len(m['patches'])==501 and m['patches'][-1]=='patches/v11_524_select_menu_cleanup.py'
m['finalBytes']=0;m['finalSha256']=''
try:
 path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
 with tempfile.TemporaryDirectory(prefix='se524-select-measure-') as tmp:
  subprocess.run([sys.executable,str(root/'build_space.py'),'--output',tmp],check=True)
  data=(Path(tmp)/'index.html').read_bytes()
  assert data==(Path(tmp)/'modeler.html').read_bytes()
  assert b'V11_524_SELECT_MENU_CLEANUP' in data
  subprocess.run(['node',str(root/'tests/model_vr_select_menu_v11_524.cjs'),str(Path(tmp)/'index.html')],check=True)
  subprocess.run(['node',str(root/'tests/model_vr_sculpt_menu_v11_524.cjs'),str(Path(tmp)/'index.html')],check=True)
  subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(Path(tmp)/'index.html')],check=True)
  print('SE524_MEASURED_BYTES='+str(len(data)),flush=True)
  print('SE524_MEASURED_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
finally:path.write_text(original,encoding='utf8')
