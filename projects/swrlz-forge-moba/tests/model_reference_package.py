"""Validate the new native model, reusable assembly data and exact release package."""
import argparse,hashlib,json,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);a=ap.parse_args()
r=Path(__file__).resolve().parent.parent;out=Path(a.package);m=json.loads((r/'source-manifest.json').read_text());receipt=json.loads((out/'SOURCE.json').read_text());raw=(out/'index.html').read_bytes()
assert len(m['patches'])==83 and m['patches'][-1]=='patches/v11_13_reference_assemblies.py'
assert len(receipt['assets'])==36 and receipt['patches']==m['patches']
assert len(raw)==m['finalBytes']==receipt['finalBytes'];assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==receipt['finalSha256']
source=r/'scenes/model-atelier-festival-reference-v11-13.swyrl.json';d=json.loads(source.read_text());model=d['project']['modelAtelier'];parts=model['parts'];rig=model['assemblies']
assert len(parts)==275 and len({p['id'] for p in parts})==275
assert sum(p.get('surfaceStyle')=='portrait-head' for p in parts)==1
assert sum(p.get('surfaceStyle')=='paper-plume' for p in parts)==2
assert sum(p['id'].startswith('hair-nape-') for p in parts)==12
assert len(rig['components'])==3 and len(rig['sockets'])==2
for s in rig['sockets']:assert s['partId'] in {p['id'] for p in parts} and len(s['local'])==3
for c in rig['components']:assert sum(p['group']==c['group'] for p in parts)>=24
assert rig['components'][0]['state']==rig['components'][1]['state']=='attached'
assert rig['components'][2]['state']=='free'
assert (out/source.relative_to(r)).read_bytes()==source.read_bytes()
html=raw.decode();found=re.search(r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)',html,re.S);assert found and json.loads(found.group(1))==d
for key in ['V11_13_REFERENCE_ASSEMBLIES','modelAtelierAssemblyDeck','atelierAssemblySample','atelierAssemblySaveKey','atelierValidateAssemblies','MODEL_ATELIER_LEGACY_V1112']:
 assert key in html,key
baseline=json.loads((r/'tests/model_reference_baseline.json').read_text())
for path,sha in baseline['sources'].items():assert hashlib.sha256((r/path).read_bytes()).hexdigest()==sha,path
for path,meta in baseline['assets'].items():assert receipt['assets'][path]==meta,path
print('MODEL_REFERENCE_SOURCE_83_PATCHES_36_ASSETS_275_PARTS_PRESERVED_BASELINE_PASS')
