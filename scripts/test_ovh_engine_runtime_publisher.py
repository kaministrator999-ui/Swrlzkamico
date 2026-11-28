import importlib.util, tempfile, json, hashlib
from pathlib import Path
spec=importlib.util.spec_from_file_location('publisher',Path(__file__).with_name('ovh_engine_publish.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def meta(data):return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
with tempfile.TemporaryDirectory() as t:
    r=Path(t);p.LIVE=r/'live';p.HISTORY=r/'history';p.RUNTIME_PAYLOAD=r/'payload'
    for d in [p.LIVE,p.HISTORY,p.RUNTIME_PAYLOAD]:d.mkdir()
    base=b'original sealed engine';p.SEALED_SOURCE=meta(base)['sha256']
    for name in ['index.html','modeler.html']:(p.LIVE/name).write_bytes(base)
    (p.LIVE/'untouched.txt').write_text('preserve')
    starter={}
    for rel in p.BOOTSTRAP_BASELINE:
        dest=p.LIVE/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b'live optimized starter');starter[rel]=meta(dest.read_bytes())
    (p.LIVE/p.SCOPED).write_text(json.dumps({'assets':starter}))
    html=b'<script type="module" src="./swrlz-engine-v11.552.js"></script>'
    files={'index.html':html,'modeler.html':html,'swrlz-engine-v11.552.js':b'console.log("ready");','assets/uv-unwrapper/uv_atlas_core_v11_555.mjs':b'export {};','assets/uv-unwrapper/uv_lscm_core_v11_555.mjs':b'export {};'}
    for rel,data in files.items():
        f=p.RUNTIME_PAYLOAD/'overlay'/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
    scene='scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'
    m={'schema':'swrlz-ovh-runtime-overlay-v1','target':str(p.LIVE),'sealedSourceSha256':p.SEALED_SOURCE,'requiredStarterAssets':starter,'assets':{k:meta(v) for k,v in files.items()},'browserReceipt':{'realStarterCard':True,'errors':[],'hash':starter[scene]['sha256']}}
    manifest=p.RUNTIME_PAYLOAD/'manifest.json';manifest.write_text(json.dumps(m))
    p.deploy_runtime()
    assert (p.LIVE/'untouched.txt').read_text()=='preserve'
    assert (p.LIVE/'index.html').read_bytes()==html
    for k,v in files.items():assert (p.LIVE/k).read_bytes()==v
    p.deploy_runtime()
    p.rollback()
    assert (p.LIVE/'index.html').read_bytes()==base and not (p.LIVE/'swrlz-engine-v11.552.js').exists()
    (p.LIVE/'index.html').write_bytes(b'unknown')
    try:p.deploy_runtime()
    except RuntimeError as e:assert 'Unknown runtime baseline' in str(e)
    else:raise AssertionError('accepted unknown baseline')
    assert (p.LIVE/'index.html').read_bytes()==b'unknown'
    print('SWRLZ_RUNTIME_PUBLISH_TRANSACTION_PASS')
