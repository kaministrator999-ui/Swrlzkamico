#!/usr/bin/env python3
"""§E v11.533: composed account opening and canonical source integrity."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--request',action='store_true');args=p.parse_args()
m=json.loads((root/'source-manifest.json').read_text('utf8'))
assert m['name']=='§wyrl§ Engine v11.533'
assert m['finalArtifact']=='swyrl_engine_v11_533.html'
assert len(m['patches'])==510 and m['patches'][-2:]==['patches/v11_532_project_account_save_receipt.py','patches/v11_533_project_account_open.py']
assert m['finalBytes']>1000000 and len(m['finalSha256'])==64
subprocess.run(['node','--check',str(root/'runtime/project_account_open_v11_533.js')],check=True)
for test in ('project_revisions_v11_486.cjs','account_project_naming_v11_488.cjs','engine_cloud_revision_cache_v11_518.cjs','model_project_edit_journal_v11_521.cjs'):
 subprocess.run(['node',str(root/'tests'/test)],check=True)
out=Path(args.output).resolve()
subprocess.run([sys.executable,str(root/'build_space.py'),'--output',str(out)],check=True)
raw=(out/'index.html').read_bytes();assert raw==(out/'modeler.html').read_bytes()
assert len(raw)==m['finalBytes'] and hashlib.sha256(raw).hexdigest()==m['finalSha256']
s=raw.decode('utf8')
for token in ("window.SWRLZ_FORGE_BUILD={version:'v11.533'",'<title>§wyrl§ Engine · Maker v11.533</title>',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_533_PROJECT_ACCOUNT_OPEN','SE533_PROJECT_ACCOUNT_OPEN_START','SE532_PROJECT_ACCOUNT_SAVE_RECEIPT_START',
 'const confirmed=await se532SaveCheckedProjectAccount()===true;','se532PrepareProjectAccountSave','se532ProjectSaveRpc',
 'SE531_QUEST_MENU_GIZMO_ACCOUNT_END','SE529_NATIVE_PROJECT_ACCOUNT_SAVE_START','SE521_PERSISTENT_EDIT_JOURNAL_END',
 'SE503_UV_ISLAND_MATH_START','swyrl-explicit-skin-v1','SE514_NATIVE_XR_RIG_END','SE483_SORTING_HAT_END'):
 assert token in s,token
assert "const confirmed=await se371PreviousSaveCloud()===true;" not in s
assert s.count(" source.engine='§wyrl§ Engine · Maker v11.533';source.version=11.533;")==5
subprocess.run([sys.executable,str(root/'scripts/check_inline_js_syntax_v11_266.py'),str(out/'index.html')],check=True)
# Exercise the actual assembled native writer and wrapper chain. The old v531
# UI test fakes the bypassed function's return and cannot verify this repair.
subprocess.run(['node',str(root/'tests/project_account_receipt_v11_532.cjs'),str(out/'index.html')],check=True)
subprocess.run(['node',str(root/'tests/project_account_open_v11_533.cjs'),str(out/'index.html')],check=True)
receipt=json.loads((out/'SOURCE.json').read_text('utf8'))
for key,value in [('sourceVersion',m['name']),('finalBytes',len(raw)),('finalSha256',m['finalSha256']),('patches',m['patches'])]:assert receipt[key]==value,key
for rel,expected in receipt['assets'].items():
 asset=(out/rel).read_bytes();assert len(asset)==expected['bytes'] and hashlib.sha256(asset).hexdigest()==expected['sha256'],rel
assert len(receipt['assets'])==78
if args.request:
 req=json.loads((root/'DEPLOY_REQUEST.json').read_text('utf8'))
 assert req['releaseVersion']=='v11.533' and req['target']=='kamiloki/swrlz-forge-moba'
 assert req['deployMarker']=='SWYRL_ENGINE_DEPLOY_MARKER: V11_533_PROJECT_ACCOUNT_OPEN'
 assert req['sourceIntegritySha256']==m['finalSha256'] and len(req['sourceCommit'])==40
print('SE533_SOURCE_VERIFIED',json.dumps({'version':'v11.533','patches':510,'bytes':len(raw),'sha256':m['finalSha256'],'assets':len(receipt['assets']),'liveAccountWriteTested':False}),flush=True)
