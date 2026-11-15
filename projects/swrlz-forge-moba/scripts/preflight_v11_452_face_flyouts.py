#!/usr/bin/env python3
"""Build and test §E v11.452 without changing sealed manifest or HF Space."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'source-manifest.json'
orig=path.read_bytes()
m=json.loads(orig)
guided='patches/v11_451_guided_face_workflow.py'
flyouts='patches/v11_452_native_face_flyouts.py'
if m['name']=='§wyrl§ Engine v11.450':
 assert m['patches'][-1]=='patches/v11_450_camera_inset_preview.py'
 m['patches'].append(guided)
elif m['name']=='§wyrl§ Engine v11.451':
 assert m['patches'][-1]==guided
else:
 raise SystemExit('Unexpected engine source version; refuse to build v11.452')
assert (ROOT/guided).is_file() and (ROOT/flyouts).is_file()
m['patches'].append(flyouts)
m['name']='§wyrl§ Engine v11.452'
m['finalArtifact']='swyrl_engine_v11_452.html'
m['finalSha256']=None;m['finalBytes']=None
try:
 path.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 with tempfile.TemporaryDirectory(prefix='se452-face-flyouts-') as tmp:
  output=Path(tmp)/'out'
  subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(output)],check=True)
  data=(output/'index.html').read_bytes()
  assert data==(output/'modeler.html').read_bytes()
  txt=data.decode('utf8')
  assert txt.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_452_NATIVE_FACE_FLYOUTS')==1
  assert txt.count('SE452_NATIVE_FACE_FLYOUTS_START')==1
  assert txt.count('SE452_NATIVE_FACE_FLYOUTS_CSS_START')==1
  assert txt.count(" source.engine='§wyrl§ Engine · Maker v11.452';source.version=11.452;")==5
  subprocess.run(['node','--check',str(ROOT/'runtime/model_face_flyouts_v11_452.js')],check=True)
  subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(output/'index.html')],check=True)
  for test in [
    'model_face_flyouts_v11_452.mjs',
    'model_guided_face_workflow_v11_451.mjs',
    'model_camera_inset_v11_451.mjs',
    'model_touch_layout_v11_451.mjs',
    'model_inset_dock_v11_451.mjs',
    'model_planar_face_pick_v11_450.mjs'
  ]:
   subprocess.run(['node',str(ROOT/'tests'/test),str(output/'index.html')],check=True)
  print(json.dumps({'status':'SE452_FACE_FLYOUT_PREFLIGHT_PASS','version':'v11.452',
      'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
      'patches':len(m['patches']),'cameraAndUndoPreserved':True,
      'modelDataModified':False,'phoneAndVRPhysicalTests':'not run'}),flush=True)
finally:
 path.write_bytes(orig)
