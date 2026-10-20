#!/usr/bin/env python3
"""Measure exact v11.62 release candidate before updating its source manifest."""
import hashlib,json,subprocess,runpy,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'source-manifest.json').read_text())
assert manifest['name']=='§wyrl§ Engine v11.61' and len(manifest['patches'])==93
with tempfile.TemporaryDirectory() as t:
    subprocess.run(['python',str(root/'build_space.py'),'--output',t],check=True,stdout=subprocess.DEVNULL)
    before=(Path(t)/'index.html').read_text(encoding='utf-8')
    b=before.encode()
    assert len(b)==manifest['finalBytes'] and hashlib.sha256(b).hexdigest()==manifest['finalSha256']
    final=runpy.run_path(str(root/'patches/v11_62_mobile_tool_layout.py'))['apply'](before)
    data=final.encode()
    assert before.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1].split(';',1)[0]==final.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1].split(';',1)[0]
    print('V1162_RELEASE_MEASURE '+json.dumps({'finalBytes':len(data),'finalSha256':hashlib.sha256(data).hexdigest(),'patches':94,'priorSha256':manifest['finalSha256']},sort_keys=True),flush=True)
