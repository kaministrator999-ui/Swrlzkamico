#!/usr/bin/env python3
"""Copy only the exact browser-verified files into a repository staging overlay."""
import hashlib,json,shutil,sys
from pathlib import Path
src=Path(sys.argv[1])
root=Path('.deploy/engine-uv')
m=json.loads((root/'request.json').read_text())
out=root/'payload'
files={
'scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json':'candidate.swyrl.json',
'assets/models/clean-topology-humanoid-v11-554-uv-test.png':'candidate-checker.png',
'assets/models/clean-topology-humanoid-v11-554-uv-guide-2048.png':'candidate-uv.png'}
assert set(files)==set(m['assets'])
assert json.loads((src/'native/native-browser-receipt.json').read_text())['errors']==[]
for rel,name in files.items():
    data=(src/name).read_bytes();meta=m['assets'][rel]
    assert len(data)==meta['bytes'] and hashlib.sha256(data).hexdigest()==meta['sha256'],rel
    dest=out/'overlay'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
out.mkdir(parents=True,exist_ok=True)
shutil.copyfile(root/'request.json',out/'manifest.json')
print('SWRLZ_ENGINE_VERIFIED_PAYLOAD_STAGED')
