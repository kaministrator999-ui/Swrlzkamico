#!/usr/bin/env python3
"""Compile v11.528 source in disposable workspace, then validate scoped immersive fixes."""
from pathlib import Path
import json,hashlib,subprocess,tempfile,sys
root=Path(__file__).resolve().parents[1]
path=root/'source-manifest.json'
original=path.read_text('utf8');manifest=json.loads(original)
assert manifest['name']=='§wyrl§ Engine v11.528'
assert manifest['finalArtifact']=='swyrl_engine_v11_528.html'
assert len(manifest['patches'])==505
assert manifest['patches'][-1]=='patches/v11_528_immersive_ux_account_repair.py'
manifest['finalBytes']=0;manifest['finalSha256']=''
try:
 path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
 with tempfile.TemporaryDirectory(prefix='se528-owner-qa-') as tmp:
  subprocess.run([sys.executable,str(root/'build_space.py'),'--output',tmp],check=True)
  page=Path(tmp)/'index.html';raw=page.read_bytes()
  assert raw==(Path(tmp)/'modeler.html').read_bytes()
  for test in ['model_vr_owner_qa_v11_528.cjs',
               'model_vr_draw_menu_v11_528.cjs',
               'model_vr_select_menu_v11_528.cjs',
               'model_vr_display_menu_v11_528.cjs',
               'model_vr_create_menu_v11_528.cjs',
               'model_vr_sculpt_menu_v11_528.cjs']:
   subprocess.run(['node',str(root/'tests'/test),str(page)],check=True)
  subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(page)],check=True)
  print('SE528_MEASURED_BYTES='+str(len(raw)),flush=True)
  print('SE528_MEASURED_SHA256='+hashlib.sha256(raw).hexdigest(),flush=True)
finally:path.write_text(original,encoding='utf8')
