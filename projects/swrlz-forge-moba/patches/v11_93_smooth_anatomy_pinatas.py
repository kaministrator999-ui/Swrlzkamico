"""Smooth exposed anatomy and eye contours; keep hair piñatas visible by default."""
from pathlib import Path
import json

def once(html,old,new):
    assert html.count(old)==1,(old[:90],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    html=once(html,'function atelierFestivalRefineFace(project){','function atelierFestivalRefineFaceV1192(project){')
    html=once(html,'function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){','function atelierAnimeGirlProjectV1192(original=MODEL_ATELIER_CANONICAL_PROJECT){')
    html=once(html,"function atelierAnimeFrame(mode='body',view='three'){","function atelierAnimeFrameV1192(mode='body',view='three'){")
    modules=['model_atelier_portrait_v11_93.js','model_atelier_legs_v11_93.js','model_atelier_skin_v11_93.js','model_atelier_festival_finish_v11_93.js','model_atelier_pinata_frame_v11_93.js','model_atelier_coverage_v11_93.js']
    js='\n'.join((root/'runtime'/name).read_text() for name in modules)
    wrapper='''
const atelierOriginalGripsV1193=new WeakMap();
function atelierFestivalRefineFace(scene){
 const parts=scene.project.modelAtelier.parts,original=parts.find(p=>p.id==='girl-organic-body').topologyMesh.positions.slice(),grips=parts.filter(p=>/^hair-grip-/.test(p.id)).map(p=>structuredClone(p));
 atelierFestivalRefineFaceV1192(scene);atelierPortraitRefinementV1193(scene,original);atelierOriginalGripsV1193.set(scene,grips);return scene;
}
function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){
 const scene=atelierAnimeGirlProjectV1192(original);atelierSmoothLegsV1193(scene);atelierSmoothExposedSkinV1193(scene);atelierFestivalFinishV1193(scene,atelierOriginalGripsV1193.get(scene)||[]);atelierFestivalCoverageV1193(scene);
 const model=scene.project.modelAtelier;model.meshGroups=[];const groups=new Map();
 for(const part of model.parts){const region=part.organicSurface?.region,key=part.group!=='Character'?'Companions':part.id==='girl-organic-body'?'Anatomy':['hair','splitHair'].includes(region)?'Hair':['eye','iris','lid','lip','brow'].includes(region)?'Face and eyes':'Costume';if(!groups.has(key))groups.set(key,[]);groups.get(key).push(part.id);}
 for(const [name,ids] of groups)for(let i=0;i<ids.length;i+=30)if(ids.slice(i,i+30).length>1)model.meshGroups.push({id:'smooth-group-'+name.replaceAll(' ','-')+'-'+i,name:name+(i?' '+(i/30+1):''),members:ids.slice(i,i+30)});
 model.appearanceRevision='v11.93';if(model.referenceProfile)model.referenceProfile.version='v11.93';
 model.name='Prism · Smooth Festival Girl and Hair Piñatas';scene.project.name=model.name;scene.engine='§wyrl§ Engine · Maker v11.93';
 model.artDirection='Visible attached cyan/coral piñatas, low inner-to-high outer almond eyes, smooth cheeks and rounded chin, continuous shoulder/arm muscles and calf transitions, compact swept hair and angular layered festival tailoring.';return scene;
}
const atelierSmoothMaterialBaseV1193=material;
material=function(part){const value=atelierSmoothMaterialBaseV1193(part);if(part.id==='girl-organic-body')value.roughness=.62;return value;};
'''
    html=once(html,'  function refreshList(){',js+wrapper+'\n  function refreshList(){')
    html=once(html,"'scenes/model-atelier-reference-girl-v11-92.swyrl.json'","'scenes/model-atelier-smooth-girl-v11-93.swyrl.json'")
    html=once(html,'return Object.freeze({createAnimeGirl:', 'return Object.freeze({presentationStatus:atelierGirlPresentationV1193,createAnimeGirl:')
    html=once(html,'createGirlProject:()=>ModelAtelier.createAnimeGirl(),','presentation:()=>ModelAtelier.presentationStatus(),createGirlProject:()=>ModelAtelier.createAnimeGirl(),')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_92_FESTIVAL_REFERENCE','SWYRL_ENGINE_DEPLOY_MARKER: V11_93_SMOOTH_ANATOMY_PINATAS'),('ENGINE · MAKER v11.92','ENGINE · MAKER v11.93'),('v11.92 · swept hair and layered festival dress','v11.93 · smooth anatomy and restored hair piñatas'),("window.SWRLZ_FORGE_BUILD={version:'v11.92'","window.SWRLZ_FORGE_BUILD={version:'v11.93'"),('<title>§wyrl§ Engine · Maker v11.92</title>','<title>§wyrl§ Engine · Maker v11.93</title>')]:html=once(html,old,new)
    html=once(html,'<strong>Prism · Festival Reference Girl</strong>','<strong>Prism · Festival Girl and Hair Piñatas</strong>')
    html=once(html,'Soft cheeks and chin, almond amber eyes, swept cyan/coral hair and a longer layered festival dress. Native edit, save and textured export retained.','Attached hair piñatas, smooth face and exposed muscle contours, upward-sloping almond eyes, compact swept hair and layered festival tailoring. Native editing and export retained.')
    prefix='const SE_RELEASE_NOTES=';start=html.index(prefix)+len(prefix);notes,size=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Smooth anatomy · restored hair piñatas',date='2026-10-23',changes=[
      'Both original piñatas are visible on her hair in the normal opening view, with their braid grips and native attachment controls restored.',
      'Eyes rise from low inner corners near the nose to higher outer corners, with fitted amber irises, flatter round pupils and stronger upper lashes.',
      'Cheeks, chin and jaw blend smoothly; exposed shoulders, arms and torso follow softer continuous muscle contours.',
      'Thighs, knees and calves form a smooth continuous leg silhouette, with natural ankle taper and preserved feet.',
      'Compact swept hair, sharper layered dress panels, fitted armor linings and an opaque festival underlayer keep the costume detailed and covered.'
    ])
    html=html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    return html
