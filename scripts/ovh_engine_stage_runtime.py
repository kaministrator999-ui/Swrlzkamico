#!/usr/bin/env python3
"""Create a static runtime overlay from the exact native-browser-tested package."""
import hashlib,json,shutil,sys
from pathlib import Path
dist=Path(sys.argv[1])
qa=Path(sys.argv[2])
stage=Path('.deploy/engine-runtime/payload')
uv=Path('.deploy/engine-uv/payload')
m=json.loads((uv/'manifest.json').read_text())
receipt=json.loads((dist/'SOURCE.json').read_text())
qa_receipt=json.loads((qa/'receipt.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert qa_receipt['realStarterCard'] and not qa_receipt['errors']
assert qa_receipt['origin']=='https://40.160.61.231'
assert qa_receipt['accountMode']=='explicit-local-workspace' and qa_receipt['accountIntegrationVerified'] is False
assert qa_receipt['info']['frame'] is None
assert qa_receipt['labels']['labels']==22
scene='scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'
assert qa_receipt['hash']==m['assets'][scene]['sha256']
for rel,rec in m['assets'].items():
    assert sha(dist/rel)==rec['sha256'] and (dist/rel).stat().st_size==rec['bytes'],rel
files=['index.html','modeler.html','swrlz-engine-v11.552.js','assets/uv-unwrapper/uv_atlas_core_v11_555.mjs','assets/uv-unwrapper/uv_lscm_core_v11_555.mjs']
assert receipt['finalSha256']=='3fe29516958ea5af2448352fa238eda121cc3031266c61c746380f092d22232e'
assert sha(dist/'index.html')==receipt['staticDelivery']['indexSha256']
assert sha(dist/'modeler.html')==receipt['staticDelivery']['modelerSha256']
assert sha(dist/files[2])==receipt['staticDelivery']['moduleSha256']
assets={}
for rel in files:
    p=dist/rel; dest=stage/'overlay'/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,dest)
    assets[rel]={'sha256':sha(p),'bytes':p.stat().st_size}
manifest={'schema':'swrlz-ovh-runtime-overlay-v1','target':'/var/www/swrlz-engine','sealedSourceSha256':receipt['finalSha256'],'assets':assets,'requiredStarterAssets':m['assets'],'browserReceipt':qa_receipt,'sourceCommit':sys.argv[3],'browserRun':sys.argv[4]}
(stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('SWRLZ_ENGINE_RUNTIME_PAYLOAD_STAGED',json.dumps(assets),flush=True)
