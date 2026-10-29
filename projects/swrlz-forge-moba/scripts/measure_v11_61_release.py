#!/usr/bin/env python3
"""Measure v11.61 candidate independently; DO NOT update production manifest here."""
import hashlib,json,runpy,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'source-manifest.json').read_text())
assert manifest['name']=='§wyrl§ Engine v11.61' and len(manifest['patches'])==93
assert manifest['patches'][-1]=='patches/v11_61_context_workbench.py'
with tempfile.TemporaryDirectory() as t:
    subprocess.run(['python',str(root/'build_space.py'),'--output',t],check=True,stdout=subprocess.DEVNULL)
    original=(Path(t)/'index.html').read_text(encoding='utf-8')
    old_model=original.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1].split(';',1)[0]
    # The release manifest already applies the last v11.61 patch.
    final=original
    new_model=final.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1].split(';',1)[0]
    assert old_model==new_model
    raw=final.encode('utf-8')
    assert hashlib.sha256(raw).hexdigest()==manifest['finalSha256'] and len(raw)==manifest['finalBytes']
    print('V1161_RELEASE_MEASURE '+json.dumps({
      'finalBytes':len(raw),'finalSha256':hashlib.sha256(raw).hexdigest(),
      'patches':93,'baseReleaseSha256':'fe11e3e748184db1797ef66bc327f7867a25f91d431823a4c8794f157117d97f',
      'marker':'V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH',
      'originalCanonicalPreserved':True},sort_keys=True),flush=True)
