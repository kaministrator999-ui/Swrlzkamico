from pathlib import Path
import json, py_compile
root=Path(__file__).resolve().parents[1]
py_compile.compile(str(root/'api/index.py'),doraise=True)
py_compile.compile(str(root/'api/chat_extensions.py'),doraise=True)
index=(root/'api/index.py').read_text('utf-8')
admin=(root/'web/admin.html').read_text('utf-8')
js=(root/'web/chat_enhancements.js').read_text('utf-8')
vercel=json.loads((root/'vercel.json').read_text('utf-8'))
checks={'server_2_1_3':'VERSION = "2.1.3"' in index,'chat_extensions':'import api.chat_extensions' in index,'token_generate':'chat-token-generate' in index and 'GENERATE + SAVE' in admin,'token_set':'chat-token-set' in index and 'SAVE / CHANGE TOKEN' in admin,'live_web':'live-web-list' in index and '/live/' in admin,'snapshots':'snapshot-create' in index and 'snapshot-restore' in index,'activity':'activity.jsonl' in index,'capabilities':'CAPABILITIES' in index,'release_status':'release-status' in index,'evidence':'swrlz-evidence' in js,'context':'Context inspector' in js,'stream_camera':'Stream camera' in js,'fork':'forkAt' in js,'retry':'retryMessage' in js,'workbench':'sendWorkbench' in js,'dev_deploy_disabled':vercel.get('git',{}).get('deploymentEnabled',{}).get('dev') is False}
failed=[k for k,v in checks.items() if not v]
print(json.dumps({'ok':not failed,'checks':checks,'failed':failed},indent=2))
raise SystemExit(1 if failed else 0)
