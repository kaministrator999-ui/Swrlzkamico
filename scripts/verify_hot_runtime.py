#!/usr/bin/env python3
from __future__ import annotations
import ast, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
paths=['api/index.py','api/runtime_hot.py','api/hot_loader.py','api/chat_extensions.py','runtime_hot/r39_engine.py']
for rel in paths:
    p=ROOT/rel
    if not p.is_file(): raise SystemExit('MISSING:'+rel)
    if p.suffix=='.py': ast.parse(p.read_text('utf-8'),filename=rel)
index=(ROOT/'api/index.py').read_text('utf-8')
hot=(ROOT/'api/runtime_hot.py').read_text('utf-8')
loader=(ROOT/'api/hot_loader.py').read_text('utf-8')
chat=(ROOT/'api/chat_extensions.py').read_text('utf-8')
manifest=json.loads((ROOT/'runtime_hot/manifest.json').read_text('utf-8'))
checks={
 'server-2.1.7':'VERSION = "2.1.7"' in index,
 'chat-1.3.3':'chat.APP_VERSION = "1.3.3"' in chat,
 'stable-install':'_install_hot_runtime(_server)' in index,
 'admin-auth':'server.auth(request)' in hot,
 'dev-source':'DEFAULT_BRANCH = "dev"' in hot,
 'hot-sync':'/api/hot/sync' in hot,
 'hot-clear':'/api/hot/clear' in hot,
 'hot-rollback':'/api/hot/rollback' in hot,
 'portal':'/live/' in hot and '/api/hot/pages' in hot,
 'chat-fallback':'hot_chat_path' in chat and 'BUNDLED_CHAT_PAGE' in chat,
 'engine-fallback':'get_engine' in chat and 'return bundled, "bundled"' in loader,
 'dynamic-loader':'spec_from_file_location' in loader,
 'idle-reset':'Reset the idle heartbeat timer after every actual engine event/progress event.' in chat,
 'manifest':manifest.get('schema')==1 and 'r39_engine.py' in manifest.get('inferenceFiles',[]),
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS' if v else 'FAIL')+' | '+k)
if failed: raise SystemExit('FAILED:'+','.join(failed))
print(f'RESULT | {len(checks)}/{len(checks)} PASS')
