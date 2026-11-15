#!/usr/bin/env python3
"""Verify the exact next engine release without changing the sealed manifest."""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/'source-manifest.json'
previous=manifest_path.read_bytes()
manifest=json.loads(previous)
assert manifest['name']=='§wyrl§ Engine v11.450'
assert manifest['patches'][-1]=='patches/v11_450_camera_inset_preview.py'
assert manifest['finalArtifact']=='swyrl_engine_v11_450.html'
addon='patches/v11_451_progressive_face_dock.py'
assert (ROOT/addon).is_file()
manifest['name']='§wyrl§ Engine v11.451'
manifest['finalArtifact']='swyrl_engine_v11_451.html'
manifest['patches'].append(addon)
manifest['finalBytes']=None
manifest['finalSha256']=None
try:
 manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 with tempfile.TemporaryDirectory(prefix='swrlz-face-dock-451-') as temp:
  path=Path(temp)/'space'
  subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(path)],check=True)
  html=(path/'index.html').read_bytes()
  assert html==(path/'modeler.html').read_bytes()
  source=html.decode('utf8')
  assert source.count('SE451_FACE_PROGRESSIVE_DOCK_START')==1
  assert source.count('SE451_FACE_PROGRESSIVE_DOCK_CSS_START')==1
  assert source.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_451_PROGRESSIVE_FACE_DOCK')==1
  assert source.count(" source.engine='§wyrl§ Engine · Maker v11.451';source.version=11.451;")==5
  for filename in ['runtime/model_face_progressive_v11_451.js']:
   subprocess.run(['node','--check',str(ROOT/filename)],check=True)
  subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(path/'index.html')],check=True)
  for test in [
   'model_face_progressive_v11_451.mjs',
   'model_camera_inset_v11_450.mjs',
   'model_planar_face_pick_v11_450.mjs',
   'model_inset_dock_v11_450.mjs',
   'model_touch_layout_v11_450.mjs',
   'model_camera_preferences_preserved_v11_450.mjs',
   'model_face_shortcuts_v11_448.mjs',
   'model_studio_workshop_bridge_v11_430.mjs'
  ]:
   subprocess.run(['node',str(ROOT/'tests'/test),str(path/'index.html')],check=True)
  print(json.dumps({'result':'SE451_PREFLIGHT_PASS','release':'v11.451',
   'bytes':len(html),'sha256':hashlib.sha256(html).hexdigest(),
   'patches':len(manifest['patches']),'nativePreview':True,
   'priorCameraAndTouchTests':True,'physicalPhoneAcceptance':False}),flush=True)
finally:
 manifest_path.write_bytes(previous)
