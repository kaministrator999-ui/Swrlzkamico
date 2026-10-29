#!/usr/bin/env python3
"""Build/seal the Sheep Tag hunter integration and preserve prior source/assets."""
import argparse,hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve()
manifest=json.loads((root/'source-manifest.json').read_text())
baseline=json.loads((root/'tests/sheep_courier_baseline_v11_77.json').read_text())
assert manifest['name']=='§wyrl§ Engine v11.78'
assert manifest['finalArtifact']=='swyrl_engine_v11_78.html'
assert manifest['patches']==baseline['patches']+['patches/v11_78_sheep_courier.py']
assert len(manifest['patches'])==110
for path,digest in baseline['sources'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
data=(out/'index.html').read_bytes();html=data.decode()
assert len(data)==manifest['finalBytes'] and hashlib.sha256(data).hexdigest()==manifest['finalSha256']
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_78_SHEEP_TAG_COURIER')==1
for token in ['<title>§wyrl§ Engine · Maker v11.78</title>','ENGINE · MAKER v11.78',"window.SWRLZ_FORGE_BUILD={version:'v11.78'",'v11.78 · Astra in Sheep Tag','createCourierHunter:atelierCourierHunter',"if(type==='st-wolf')return ModelAtelier.createCourierHunter();",'function stCourierVisualStatus(object)','data-project-template="comet-courier"','function atelierCourierGLB()']:
    assert token in html,token
source=json.loads((out/'SOURCE.json').read_text())
assert source['sourceVersion']==manifest['name'] and source['patches']==manifest['patches']
assert source['finalSha256']==manifest['finalSha256'] and source['finalBytes']==len(data)
assert source['assets']==baseline['assets'] and len(source['assets'])==46
for path,meta in baseline['assets'].items():
    raw=(out/path).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'],path
original=html.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1];_,end=json.JSONDecoder().raw_decode(original)
old=json.loads((root/'tests/comet_courier_baseline_v11_76.json').read_text())
assert hashlib.sha256(original[:end].encode()).hexdigest()==old['originalCanonicalSha256']
model=json.loads((out/'scenes/model-atelier-comet-courier-v11-77.swyrl.json').read_text())['project']['modelAtelier']
assert len(model['parts'])==106 and len(model['meshGroups'])==6
module=html.split('<script type="module">',1)[1].rsplit('</script>',1)[0]
Path(str(out)+'-module.mjs').write_text(module)
print('SWRLZ_V1178_RELEASE_VERIFIED',len(data),manifest['finalSha256'],110,46)
print('SHEEP_COURIER_HISTORICAL_SOURCE_AND_4K_ASSET_PRESERVATION_PASS',len(baseline['sources']))
