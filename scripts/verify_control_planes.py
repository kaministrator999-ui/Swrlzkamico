from pathlib import Path
import json, py_compile
root=Path(__file__).resolve().parents[1]
for p in ('api/index.py','api/server_v213.py','api/chat_extensions.py','swyrlz/r39_inference.py'):
    py_compile.compile(str(root/p),doraise=True)
wrapper=(root/'api/index.py').read_text('utf-8')
base=(root/'api/server_v213.py').read_text('utf-8')
ext=(root/'api/chat_extensions.py').read_text('utf-8')
admin=(root/'web/admin.html').read_text('utf-8')
js=(root/'web/chat_enhancements.js').read_text('utf-8')
css=(root/'web/chat_enhancements.css').read_text('utf-8')
vercel=json.loads((root/'vercel.json').read_text('utf-8'))
checks={
    'server_2_1_6':'VERSION = "2.1.6"' in wrapper,
    'preserved_2_1_3_base':'from api import server_v213 as _server' in wrapper and 'VERSION = "2.1.3"' in base,
    'chat_1_3_2':'chat.APP_VERSION="1.3.2"' in ext or 'chat.APP_VERSION = "1.3.2"' in ext,
    'local_r39':'local-r39-inference' in wrapper and '_local_stream' in ext,
    'chat_extensions':'import api.chat_extensions' in base,
    'auto_init':'_probe_local_once' in ext and 'manualGate5Required' in ext,
    'stream_heartbeat':'COMPUTE_HEARTBEAT' in ext and 'ThreadPoolExecutor' in ext,
    'token_generate':'chat-token-generate' in base and 'GENERATE + SAVE' in admin,
    'token_set':'chat-token-set' in base and 'SAVE / CHANGE TOKEN' in admin,
    'live_web':'live-web-list' in base and '/live/' in admin,
    'snapshots':'snapshot-create' in base and 'snapshot-restore' in base,
    'activity':'activity.jsonl' in base,
    'capabilities':'CAPABILITIES' in base,
    'release_status':'release-status' in base,
    'evidence':'swrlz-evidence' in js,
    'context':'Context inspector' in js,
    'stream_camera_copy':'COPY TEXT' in js and 'cameraText' in js,
    'new_thread_repair':'newConversation' in js,
    'delete_thread_repair':'deleteConversation' in js,
    'ready_paint':'paintMode' in js and 'Local R39 ready' in js,
    'drawer_layering':'swrlz-sidebar-dimmer' in js and 'swrlz-sidebar-dimmer' in css,
    'fork':'forkAt' in js,
    'retry':'retryMessage' in js,
    'workbench':'sendWorkbench' in js,
    'dev_deploy_disabled':vercel.get('git',{}).get('deploymentEnabled',{}).get('dev') is False,
}
failed=[k for k,v in checks.items() if not v]
print(json.dumps({'ok':not failed,'checks':checks,'failed':failed},indent=2))
raise SystemExit(1 if failed else 0)
