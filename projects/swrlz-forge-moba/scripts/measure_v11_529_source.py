#!/usr/bin/env python3
"""Compile v11.529 source in disposable workspace, then validate scoped immersive fixes."""
from pathlib import Path
import json,hashlib,subprocess,tempfile,sys
root=Path(__file__).resolve().parents[1]
path=root/'source-manifest.json'
original=path.read_text('utf8');manifest=json.loads(original)
assert manifest['name']=='§wyrl§ Engine v11.529'
assert manifest['finalArtifact']=='swyrl_engine_v11_529.html'
assert len(manifest['patches'])==506
assert manifest['patches'][-1]=='patches/v11_529_native_account_browser_library.py'
manifest['finalBytes']=0;manifest['finalSha256']=''
try:
 path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 with tempfile.TemporaryDirectory(prefix='se528-owner-qa-') as tmp:
  subprocess.run([sys.executable,str(root/'build_space.py'),'--output',tmp],check=True)
  page=Path(tmp)/'index.html';raw=page.read_bytes()
  assert raw==(Path(tmp)/'modeler.html').read_bytes()
  for test in ['model_vr_owner_qa_v11_529.cjs',
               'model_vr_draw_menu_v11_529.cjs',
               'model_vr_select_menu_v11_529.cjs',
               'model_vr_display_menu_v11_529.cjs',
               'model_vr_create_menu_v11_529.cjs',
               'model_vr_sculpt_menu_v11_529.cjs']:
   subprocess.run(['node',str(root/'tests'/test),str(page)],check=True)
  subprocess.run(['node',str(root/'tests/project_account_browser_v11_529.cjs'),str(page)],check=True)
  subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(page)],check=True)
  print('SE529_MEASURED_BYTES='+str(len(raw)),flush=True)
  print('SE529_MEASURED_SHA256='+hashlib.sha256(raw).hexdigest(),flush=True)
finally:path.write_text(original,encoding='utf8')
