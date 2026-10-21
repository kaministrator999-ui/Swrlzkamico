"""Validate the new native model, reusable assembly data and exact release package."""
import argparse,hashlib,json,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--package',required=True);a=ap.parse_args()
r=Path(__file__).resolve().parent.parent;out=Path(a.package);m=json.loads((r/'source-manifest.json').read_text());receipt=json.loads((out/'SOURCE.json').read_text());raw=(out/'index.html').read_bytes()
assert len(m['patches'])==94 and m['patches'][-1]=='patches/v11_62_mobile_adaptive.py'
assert len(receipt['assets'])==43 and receipt['patches']==m['patches']
assert len(raw)==m['finalBytes']==receipt['finalBytes'];assert hashlib.sha256(raw).hexdigest()==m['finalSha256']==receipt['finalSha256']
source=r/'scenes/model-atelier-festival-anatomy-v11-20.swyrl.json';d=json.loads(source.read_text());model=d['project']['modelAtelier'];parts=model['parts'];rig=model['assemblies']
assert len(parts)==283 and len({p['id'] for p in parts})==283
assert sum(p.get('surfaceStyle')=='portrait-head' for p in parts)==1
assert sum(p.get('surfaceStyle')=='paper-plume' for p in parts)==2
assert sum(p['id'].startswith('hair-nape-') for p in parts)==12
assert len(rig['components'])==3 and len(rig['sockets'])==2
for s in rig['sockets']:assert s['partId'] in {p['id'] for p in parts} and len(s['local'])==3
for c in rig['components']:assert sum(p['group']==c['group'] for p in parts)>=24
assert rig['components'][0]['state']==rig['components'][1]['state']=='attached'
assert rig['components'][2]['state']=='free'
assert (out/source.relative_to(r)).read_bytes()==source.read_bytes()
html=raw.decode();needle='const MODEL_ATELIER_CANONICAL_PROJECT=';assert html.count(needle)==1
payload=html.split(needle,1)[1].lstrip()
data,_=json.JSONDecoder().raw_decode(payload)
assert data==d,'Production must preserve exact original 283-part anatomical project'
for key in ['atelierSilkenLock','atelierTailoredPanel','V11_62_MOBILE_ADAPTIVE_TOOL_SHEET','modelAtelierAssemblyDeck','atelierAssemblySample','atelierAssemblySaveKey','atelierValidateAssemblies','MODEL_ATELIER_LEGACY_V1112']:
 assert key in html,key
baseline=json.loads((r/'tests/model_reference_baseline.json').read_text())
for path,sha in baseline['sources'].items():assert hashlib.sha256((r/path).read_bytes()).hexdigest()==sha,path
for path,meta in baseline['assets'].items():assert receipt['assets'][path]==meta,path
print('MODEL_REFERENCE_SOURCE_94_PATCHES_43_ASSETS_283_PARTS_PRESERVED_BASELINE_PASS')

by_id={p['id']:p for p in parts}
assert len([p for p in parts if p.get('surfaceStyle')=='silken-lock'])==26
assert len([p for p in parts if p.get('surfaceStyle')=='tailored-panel'])==9
assert by_id['atelier-v118-right-leg']['path'][-1][0]-by_id['atelier-v118-left-leg']['path'][-1][0]>1.2
assert by_id['festival-shorts']['radii'][-1]>.3
assert by_id['azure-body']['paperVariation'] and by_id['coral-body']['paperVariation']

assert by_id['model-0001']['jawTaper']==.32
assert by_id['skirt-panel-0']['panelCamber']==.018
assert by_id['skirt-panel-0']['panelPleat']==.006
assert by_id['azure-muzzle']['surfaceStyle']==by_id['coral-muzzle']['surfaceStyle']=='tapered-muzzle'
assert by_id['azure-ear--1']['position'][2]==.26
assert by_id['azure-body']['path'][0]==[-.58,4.49,.015]
assert by_id['azure-body']['path'][6][2]<-.5
assert by_id['model-0001']['scale'][1]==.346
assert by_id['hair-cap']['surfaceStyle']=='split-dye-cap'
assert by_id['hair-cap']['dyeAccent']=='#ed6159'

assert by_id['model-0001']['meshDensity']=={'u':192,'v':128}
assert by_id['model-0001']['faceSculpt']['nose']==.04
assert by_id['model-0001']['hdFinish']['style']=='portrait'
assert not any(p['id'] in {'nose','nose-tip','left-cheek','right-cheek','left-pupil','right-pupil'} or p['id'].startswith('sock-fold-') for p in parts)
assert len({p['hdFinish']['style'] for p in parts if 'hdFinish' in p})==15
assert all(0<=p['hdFinish']['relief']<=1 for p in parts if 'hdFinish' in p)
assert all(by_id[n]['hdFinish']['style']=='paper' for n in ['azure-body','coral-body'])
print('HD_NATIVE_SURFACE_PARAMETERS_AND_REMOVED_FLOATING_FACIAL_PARTS_PASS')

assert by_id['hair-cap']['hdFinish']['style']=='crown'
assert all(by_id['hair-bun-'+s]['hdFinish']['style']=='knot' for s in ['-1','1'])
assert all(by_id[side+'-iris']['irisPigments']=={'upper':'#6d3439','lower':'#d9a34f'} for side in ['left','right'])
assert all(by_id['atelier-v118-'+side+'-leg']['legAnatomy']=={'calfFullness':.065,'shinTaper':.012} for side in ['left','right'])
print('REFERENCE_CORRECTED_KNEES_POSTERIOR_CALVES_CROWN_KNOTS_AND_IRIS_PIGMENTS_PASS')

assert by_id['model-0001']['portraitFinish']=={'chinLift':.16,'noseDefinition':.65,'warmth':.7}
assert all(len(by_id[n]['path'])==33 for n in ['smile','lower-lip','left-brow','right-brow'])
print('PORTRAIT_BODY_POLISH_SAVED_CONTOURS_AND_CONTINUOUS_FITTED_LIPS_PASS')

assert len(by_id['model-0001']['headAnatomy']['sections'])==11
assert by_id['model-0002']['path'][0][1]==3.94
assert 'atelierAnatomicalHead' in html and 'modelAtelierHeadAnatomyApply' in html
print('ANATOMICAL_HEAD_SECTION_AUTHORING_AND_JAW_NECK_ATTACHMENT_PASS')
