#!/usr/bin/env python3
"""§E v11.471 UV stretch correction + full packaged source verification."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--request',action='store_true')
a=parser.parse_args()
m=json.loads((ROOT/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.471'
assert m['finalArtifact']=='swyrl_engine_v11_471.html'
assert len(m['patches'])==448 and m['patches'][-1]=='patches/v11_471_uv_render_project_delete.py'
assert isinstance(m['finalBytes'],int) and isinstance(m['finalSha256'],str)
for name in ['model_ring_kernel_v11_466.js','model_ring_bridge_v11_466.js','model_ring_ui_v11_466.js','model_quest_browser_input_v11_467.js','studio_standalone_assets_v11_468.js','model_uv_distortion_math_v11_469.js','model_uv_shape_fit_v11_469.js','uv_latitude_math_v11_471.js','uv_fine_fit_v11_471.js','project_delete_confirm_v11_471.js']:
 subprocess.run(['node','--check',str(ROOT/'runtime'/name)],check=True)
subprocess.run(['node',str(ROOT/'tests/model_ring_kernel_v11_466.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_uv_shape_fit_v11_469.mjs')],check=True)
subprocess.run(['node',str(ROOT/'tests/uv_latitude_math_v11_471.mjs')],check=True)
out=Path(a.output).resolve()
subprocess.run([sys.executable,str(ROOT/'build_space.py'),'--output',str(out)],check=True)
data=(out/'index.html').read_bytes()
subprocess.run(['node',str(ROOT/'tests/model_uv_save_v11_471.mjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/uv_view_project_delete_v11_471.mjs'),str(out/'index.html')],check=True)
assert data==(out/'modeler.html').read_bytes()
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
html=data.decode('utf8')
for token in [
 "window.SWRLZ_FORGE_BUILD={version:'v11.471'",
 '<title>§wyrl§ Engine · Maker v11.471</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_471_UV_VISIBLE_PROJECT_DELETE',
 'SE466_RING_KERNEL_START','SE466_RING_BRIDGE_START','SE466_RING_UI_START',
 'SE465_NARROW_INSPECTOR_START',
 'SE467_QUEST_BROWSER_INPUT_START','SE468_STANDALONE_STUDIO_ASSETS_START','SE467_QUEST_BROWSER_STYLES_START',
 'SE471_UV_LATITUDE_MATH_START','SE471_UV_FINE_FIT_START','SE471_PROJECT_DELETE_CONFIRM_START','SE471_PROJECT_DELETE_STYLES_START',
 'SE469_UV_DISTORTION_MATH_START','SE469_UV_SHAPE_FIT_START','SE469_UV_SHAPE_FIT_STYLES_START','SE464_MODEL_VISUAL_POLISH_START',
 'SE436_SATCHEL_CAVITY_START',
 'modelAtelierWorkshopExtrudeScale','setRingAnchor','selectRing',
 'modelAtelierWorkshopPreview','modelAtelierWorkshopApply']:
 assert token in html,token
assert html.count(" source.engine='§wyrl§ Engine · Maker v11.471';source.version=11.471;")==5
subprocess.run([sys.executable,str(ROOT/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/studio_asset_isolation_v11_468.mjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/model_quest_browser_input_v11_467.mjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(ROOT/'tests/studio_project_routing_v11_320.cjs')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for k,v in [('sourceVersion',m['name']),('finalBytes',len(data)),('finalSha256',m['finalSha256']),('patches',m['patches'])]:
 assert receipt[k]==v,(k,receipt.get(k))
assert len(receipt['assets'])==77
for filename,r in receipt['assets'].items():
 b=(out/filename).read_bytes()
 assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],filename
if a.request:
 req=json.loads((ROOT/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert req['releaseVersion']=='v11.471'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_471_UV_VISIBLE_PROJECT_DELETE'
 assert req['target']=='kamiloki/swrlz-forge-moba'
 assert req['sourceIntegritySha256']==m['finalSha256']
 assert req['sourceCommit']
print(json.dumps({'status':'SOURCE_VERIFIED','version':'v11.471','sha256':m['finalSha256'],
 'bytes':m['finalBytes'],'patches':448,'assets':77,
 'phoneTested':False,'vrTested':False}),flush=True)
