"""Validate the new native model, reusable assembly data and exact release package."""
import argparse,hashlib,json,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);a=ap.parse_args()
r=Path(__file__).resolve().parent.parent;out=Path(a.package);m=json.loads((r/'source-manifest.json').read_text());receipt=json.loads((out/'SOURCE.json').read_text());raw=(out/'index.html').read_bytes()
assert len(m['patches'])==85 and m['patches'][-1]=='patches/v11_15_native_surface_study.py'
assert len(receipt['assets'])==38 and receipt['patches']==m['patches']
assert len(raw)==m['finalBytes']==receipt['finalBytes'];assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==receipt['finalSha256']
source=r/'scenes/model-atelier-festival-surface-v11-15.swyrl.json';d=json.loads(source.read_text());model=d['project']['modelAtelier'];parts=model['parts'];rig=model['assemblies']
assert len(parts)==301 and len({p['id'] for p in parts})==301
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
for key in ['atelierSilkenLock','atelierTailoredPanel','V11_15_NATIVE_SURFACE_STUDY','modelAtelierAssemblyDeck','atelierAssemblySample','atelierAssemblySaveKey','atelierValidateAssemblies','MODEL_ATELIER_LEGACY_V1112']:
 assert key in html,key
baseline=json.loads((r/'tests/model_reference_baseline.json').read_text())
for path,sha in baseline['sources'].items():assert hashlib.sha256((r/path).read_bytes()).hexdigest()==sha,path
for path,meta in baseline['assets'].items():assert receipt['assets'][path]==meta,path
print('MODEL_REFERENCE_SOURCE_85_PATCHES_38_ASSETS_301_PARTS_PRESERVED_BASELINE_PASS')

by_id={p['id']:p for p in parts}
assert len([p for p in parts if p.get('surfaceStyle')=='silken-lock'])==26
assert len([p for p in parts if p.get('surfaceStyle')=='tailored-panel'])==9
assert by_id['atelier-v118-right-leg']['path'][-1][0]-by_id['atelier-v118-left-leg']['path'][-1][0]>1.2
assert by_id['festival-shorts']['radii'][-1]>.3
assert by_id['azure-body']['paperVariation'] and by_id['coral-body']['paperVariation']

assert by_id['model-0001']['jawTaper']==.28
assert by_id['skirt-panel-0']['panelCamber']==.018
assert by_id['skirt-panel-0']['panelPleat']==.006
assert by_id['azure-muzzle']['surfaceStyle']==by_id['coral-muzzle']['surfaceStyle']=='tapered-muzzle'
assert by_id['azure-ear--1']['position'][2]==.26
assert by_id['azure-body']['path'][0]==[-.58,4.49,.015]
assert by_id['azure-body']['path'][6][2]<-.5
assert by_id['model-0001']['scale'][1]==.34
assert by_id['hair-cap']['surfaceStyle']=='split-dye-cap'
assert by_id['hair-cap']['dyeAccent']=='#f65f60'
