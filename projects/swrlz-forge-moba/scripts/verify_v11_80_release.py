#!/usr/bin/env python3
"""Seal the larger Wildwood map while preserving historical source and artwork."""
import argparse,hashlib,json,subprocess,struct
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output).resolve()
m=json.loads((root/'source-manifest.json').read_text());old=json.loads((root/'tests/vast_wisps_baseline_v11_79.json').read_text())
assert m['name']=='§wyrl§ Engine v11.80' and m['finalArtifact']=='swyrl_engine_v11_80.html'
assert m['patches']==old['patches']+['patches/v11_80_vast_wisps.py'] and len(m['patches'])==112
assert len(old['sources'])==255
for path,digest in old['sources'].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
subprocess.run(['python',str(root/'build_space.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
data=(out/'index.html').read_bytes();html=data.decode();receipt=json.loads((out/'SOURCE.json').read_text())
assert len(data)==m['finalBytes'] and hashlib.sha256(data).hexdigest()==m['finalSha256']
assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_80_VAST_WILDWOOD_WISPS')==1
for token in ['<title>§wyrl§ Engine · Maker v11.80</title>','ENGINE · MAKER v11.80',"window.SWRLZ_FORGE_BUILD={version:'v11.80'",'v11.80 · vast woodland & captive wisps','function stWildwoodVisual()','mapStatus:stWildwoodMapStatus','createCourierHunter:atelierCourierHunter','data-project-template="comet-courier"']:
    assert token in html,token
assert receipt['sourceVersion']==m['name'] and receipt['patches']==m['patches'] and len(receipt['assets'])==49
assert receipt['finalSha256']==m['finalSha256'] and receipt['finalBytes']==len(data)
for path,meta in old['assets'].items():
    assert receipt['assets'][path]==meta,path
    raw=(out/path).read_bytes();assert len(raw)==meta['bytes'] and hashlib.sha256(raw).hexdigest()==meta['sha256'],path
added=set(receipt['assets'])-set(old['assets']);assert added=={'scenes/sheep-tag-vast-wildwood-v11-80.swyrl.json'}
scene=json.loads((out/'scenes/sheep-tag-vast-wildwood-v11-80.swyrl.json').read_text())
assert scene['project']['kind']=='sheep-tag' and scene['project']['sheepTag']['bounds']==128
assert len(scene['scene']['actors'])==196 and len(scene['editor']['layers'])==9
assert sum(a['type']=='st-sheep' for a in scene['scene']['actors'])==8
assert sum(a['type']=='st-wolf' for a in scene['scene']['actors'])==3
assert all(8<(__import__('math').hypot(a['position'][0],a['position'][2]))<11 for a in scene['scene']['actors'] if a['type']=='st-sheep')
assert 'speed:.35,outsideAllowance:2.5' in html and 'function stVastFindPath' in html
assert len({a['id'] for a in scene['scene']['actors']})==196
encoded=html.split('const ST_CANONICAL_PROJECT=',1)[1];decoded,_=json.JSONDecoder().raw_decode(encoded);assert decoded==scene
original=html.split('const MODEL_ATELIER_CANONICAL_PROJECT=',1)[1];_,end=json.JSONDecoder().raw_decode(original)
legacy=json.loads((root/'tests/comet_courier_baseline_v11_76.json').read_text());assert hashlib.sha256(original[:end].encode()).hexdigest()==legacy['originalCanonicalSha256']
# Parse JPEG SOF directly, keeping deployment's minimal Python dependency set.
jpeg=(out/'assets/sheep-tag/moonbell-wildwood-ground-4k.jpg').read_bytes();assert jpeg[:2]==b'\xff\xd8';at=2;found=False
while at<len(jpeg):
    if jpeg[at]!=255:at+=1;continue
    tag=jpeg[at+1];at+=2
    if tag in [216,217]:continue
    n=int.from_bytes(jpeg[at:at+2],'big')
    if tag in [192,193,194]:assert struct.unpack('>HH',jpeg[at+3:at+7])==(4096,4096);found=True;break
    at+=n
assert found
Path(str(out)+'-module.mjs').write_text(html.split('<script type="module">',1)[1].rsplit('</script>',1)[0])
print('SWRLZ_V1180_RELEASE_VERIFIED',len(data),m['finalSha256'],112,49)
print('VAST_256M_CENTRAL_STARTS_WISPS_AND_255_SOURCE_PRESERVATION_PASS')
