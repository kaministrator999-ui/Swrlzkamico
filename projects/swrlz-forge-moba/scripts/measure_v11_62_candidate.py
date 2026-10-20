#!/usr/bin/env python3
"""Independently verify the current v11.62 governed source seal."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'source-manifest.json').read_text())
assert manifest['name']=='§wyrl§ Engine v11.62'
assert len(manifest['patches'])==94
assert manifest['patches'][-1]=='patches/v11_62_mobile_tool_layout.py'
with tempfile.TemporaryDirectory() as d:
 subprocess.run(['python',str(root/'build_space.py'),'--output',d],check=True,stdout=subprocess.DEVNULL)
 src=(Path(d)/'index.html').read_bytes()
 assert len(src)==manifest['finalBytes'],(len(src),manifest['finalBytes'])
 assert hashlib.sha256(src).hexdigest()==manifest['finalSha256']
 receipt=json.loads((Path(d)/'SOURCE.json').read_text())
 assert len(receipt['patches'])==94 and len(receipt['assets'])==43
 assert receipt['finalSha256']==manifest['finalSha256']
 print('V1162_RELEASE_MEASURE '+json.dumps({'bytes':len(src),'sha256':hashlib.sha256(src).hexdigest(),'patches':94,'assets':43},sort_keys=True),flush=True)
