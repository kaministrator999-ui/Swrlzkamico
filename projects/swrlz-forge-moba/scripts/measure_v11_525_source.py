#!/usr/bin/env python3
"""Measure native Display v11.525 on disposable CI workspace, never deploy unsealed HTML."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'source-manifest.json';original=path.read_text('utf8')
m=json.loads(original)
assert m['name']=='§wyrl§ Engine v11.525'
assert len(m['patches'])==502 and m['patches'][-1]=='patches/v11_525_select_menu_cleanup.py'
m['finalBytes']=0;m['finalSha256']=''
try:
 path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf8')
 with tempfile.TemporaryDirectory(prefix='se525-display-measure-') as tmp:
  subprocess.run([sys.executable,str(root/'build_space.py'),'--output',tmp],check=True)
  data=(Path(tmp)/'index.html').read_bytes()
  assert data==(Path(tmp)/'modeler.html').read_bytes()
  assert b'V11_525_DISPLAY_MENU_GROUPS' in data
  subprocess.run(['node',str(root/'tests/model_vr_select_menu_v11_525.cjs'),str(Path(tmp)/'index.html')],check=True)
  subprocess.run(['node',str(root/'tests/model_vr_display_menu_v11_525.cjs'),str(Path(tmp)/'index.html')],check=True)
  subprocess.run(['node',str(root/'tests/model_vr_sculpt_menu_v11_525.cjs'),str(Path(tmp)/'index.html')],check=True)
  subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(Path(tmp)/'index.html')],check=True)
  print('SE525_MEASURED_BYTES='+str(len(data)),flush=True)
  print('SE525_MEASURED_SHA256='+hashlib.sha256(data).hexdigest(),flush=True)
finally:path.write_text(original,encoding='utf8')

# The production manifest is sealed only after this exact source is measured.

# Candidate measurement validates the visible divider and both settings pages.
