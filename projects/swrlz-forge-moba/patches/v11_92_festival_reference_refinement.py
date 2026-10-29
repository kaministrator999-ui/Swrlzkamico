"""Refine the existing female starter's face, swept hair and longer festival dress."""
from pathlib import Path
import json

def once(html,old,new):
    assert html.count(old)==1,(old[:90],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    html=once(html,'function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){','function atelierAnimeGirlProjectV1191(original=MODEL_ATELIER_CANONICAL_PROJECT){')
    html=once(html,"function atelierAnimeFrame(mode='body',view='three'){","function atelierAnimeFrameV1191(mode='body',view='three'){")
    refiners='\n'.join((root/'runtime'/name).read_text() for name in ['model_atelier_festival_face_v11_92.js','model_atelier_festival_dress_v11_92.js','model_atelier_festival_frame_v11_92.js'])
    wrapper='''
function atelierAnimeGirlProject(original=MODEL_ATELIER_CANONICAL_PROJECT){
 const scene=atelierAnimeGirlProjectV1191(original);
 atelierFestivalRefineFace(scene);atelierFestivalRefineDress(scene);
 const model=scene.project.modelAtelier;
 // Rebuild selection memberships after replacement meshes are added.
 model.meshGroups=[];
 const groups=new Map();
 for(const part of model.parts){const region=part.organicSurface?.region,key=part.group!=='Character'?'Companions':part.id==='girl-organic-body'?'Anatomy':['hair','splitHair'].includes(region)?'Hair':['eye','iris','lid','lip','brow'].includes(region)?'Face and eyes':'Costume';if(!groups.has(key))groups.set(key,[]);groups.get(key).push(part.id);}
 for(const [name,ids] of groups)for(let i=0;i<ids.length;i+=30)if(ids.slice(i,i+30).length>1)model.meshGroups.push({id:'festival-group-'+name.replaceAll(' ','-')+'-'+i,name:name+(i?' '+(i/30+1):''),members:ids.slice(i,i+30)});
 model.name='Prism · Swept Hair and Festival Dress';scene.project.name=model.name;scene.engine='§wyrl§ Engine · Maker v11.92';
 model.artDirection='Reference-refined almond eyes, fine arched brows, soft cheeks and rounded chin, asymmetric cyan/coral swept hair, and a longer layered teal, ivory and yellow festival dress with native pleats, piping and ornaments.';
 return scene;
}
'''
    html=once(html,'  function refreshList(){',refiners+wrapper+'\n  function refreshList(){')
    html=once(html,"'scenes/model-atelier-organic-anime-girl-v11-91.swyrl.json'","'scenes/model-atelier-reference-girl-v11-92.swyrl.json'")
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_91_ORGANIC_ANIME_GIRL','SWYRL_ENGINE_DEPLOY_MARKER: V11_92_FESTIVAL_REFERENCE'),('ENGINE · MAKER v11.91','ENGINE · MAKER v11.92'),('v11.91 · organic anime character studio','v11.92 · swept hair and layered festival dress'),("window.SWRLZ_FORGE_BUILD={version:'v11.91'","window.SWRLZ_FORGE_BUILD={version:'v11.92'"),('<title>§wyrl§ Engine · Maker v11.91</title>','<title>§wyrl§ Engine · Maker v11.92</title>')]:html=once(html,old,new)
    html=once(html,'<strong>Prism · Organic Anime Girl</strong>','<strong>Prism · Festival Reference Girl</strong>')
    html=once(html,'Complete welded anime anatomy, detailed face and hands, layered split-color hair, festival tailoring and 4K materials. Original companions retained.','Soft cheeks and chin, almond amber eyes, swept cyan/coral hair and a longer layered festival dress. Native edit, save and textured export retained.')
    prefix='const SE_RELEASE_NOTES=';start=html.index(prefix)+len(prefix);notes,size=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Festival reference · soft face, swept hair and longer dress',date='2026-10-23',changes=[
      'The female starter has softer cheeks and a rounded chin, almond amber eyes and finer arched eyebrows.',
      'Asymmetric swept coral/cyan bangs, layered side locks and a curved cyan face-framing tendril replace the mirrored fringe.',
      'A longer asymmetric teal, ivory and yellow skirt adds pleated layers, shaped hems, piping and individual ornaments.',
      'All changes are editable native meshes and retain 4K materials, material Undo, JSON save/import and textured GLB.',
      'The saved original starter and both paper-ferret companions and bunny remain preserved.'
    ])
    html=html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    return html
