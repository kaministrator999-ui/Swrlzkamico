"""Save the original girl starter; add a complete welded anime body, detailed face/hands/calves, layered hair, tailoring and dedicated 4K materials."""
from pathlib import Path
import json

def once(html,old,new):
    assert html.count(old)==1,(old[:90],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    r=Path(__file__).resolve().parents[1]
    js='\n'.join((r/'runtime'/name).read_text() for name in ['model_atelier_anime_girl_v11_91.js','model_atelier_anime_surfaces_v11_91.js'])
    html=once(html,'  function refreshList(){',js+'\n  function refreshList(){')
    html=once(html,'return Object.freeze({createCloverSheep:', 'return Object.freeze({createAnimeGirl:atelierAnimeGirlProject,frameAnimeGirl:atelierAnimeFrame,createCloverSheep:')
    saved='<button class="project-card den" data-project-template="festival-girl-saved"><span class="project-icon">💾</span><strong>Saved Festival Girl · v11.90</strong><span class="template-tag">ORIGINAL STARTER SNAPSHOT</span><p>The preserved 283-part girl, outfit, split-color hair and companions before the organic body pass.</p><span class="hint den-glow">Open saved original</span></button>'
    html=once(html,'<button class="project-card den" data-project-template="model-atelier">',saved+'<button class="project-card den" data-project-template="model-atelier">')
    html=once(html,'<strong>Model Atelier · Prism Jester</strong>','<strong>Prism · Organic Anime Girl</strong>')
    html=once(html,'Original layered character study with coral and cyan ribbon forms. Edit individual 3D meshes, materials and transforms; export JSON or OBJ.','Complete welded anime anatomy, detailed face and hands, layered split-color hair, festival tailoring and 4K materials. Original companions retained.')
    html=once(html,'ModelAtelier.install();' ,(r/'runtime/model_atelier_anime_loader_v11_91.js').read_text()+'\nModelAtelier.install();')
    html=once(html,"animalStatus:()=>ModelAtelier.animalStatus(),","createGirlProject:()=>ModelAtelier.createAnimeGirl(),loadGirl:(options={})=>loadAnimeGirl(!!options.force,options),frameGirl:(mode,view)=>ModelAtelier.frameAnimeGirl(mode,view),animalStatus:()=>ModelAtelier.animalStatus(),")
    html=once(html,"['astra-4k','wildwood-4k'].includes(t.set)","['astra-4k','wildwood-4k','festival-4k'].includes(t.set)")
    html=once(html,"set:p.textureBinding?.set||(p.organicSurface?'wildwood-4k':'astra-4k')","set:p.textureBinding?.set||(p.organicSurface?.species==='anime'?'festival-4k':p.organicSurface?'wildwood-4k':'astra-4k')")
    html=once(html,'atelierLODMaxSourceTriangles=180000,atelierLODSavedVertices=65536,\n  atelierLODSavedTriangles=120000;','atelierLODMaxSourceTriangles=600000,atelierLODSavedVertices=300000,\n  atelierLODSavedTriangles=600000;')
    html=once(html,'const hd=!!model()?.parts.some(p=>p.hdFinish);',"const hd=!!model()?.parts.some(p=>p.hdFinish||p.organicSurface?.species==='anime');")
    html=once(html,'file.size>128_000_000','file.size>256_000_000');html=once(html,'Model file must be JSON below 128 MB.','Model file must be JSON below 256 MB.')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_90_SOLID_BLOCKERS_FURRED_ASTRA','SWYRL_ENGINE_DEPLOY_MARKER: V11_91_ORGANIC_ANIME_GIRL'),('ENGINE · MAKER v11.90','ENGINE · MAKER v11.91'),('v11.90 · solid blockers, furred Astra & smoother matches','v11.91 · organic anime character studio'),("window.SWRLZ_FORGE_BUILD={version:'v11.90'","window.SWRLZ_FORGE_BUILD={version:'v11.91'"),('<title>§wyrl§ Engine · Maker v11.90</title>','<title>§wyrl§ Engine · Maker v11.91</title>')]:html=once(html,old,new)
    prefix='const SE_RELEASE_NOTES=';start=html.index(prefix)+len(prefix);notes,size=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Organic anime girl · saved original and detailed new sculpt',date='2026-10-23',changes=[
        'The previous 283-part girl starter is saved separately and can be opened as Saved Festival Girl.',
        'The new girl has one continuous welded anatomical mesh: face, ears, neck, torso, arms, ten fingers, legs and feet.',
        'Denser face and finger geometry adds orbital wells, upward-canted eyes/lids/brows, tapered jaw, nose, lips, hands, knees, calves and Achilles transitions.',
        'Layered split-color hair filaments, real raised garment stitches and dedicated 4K color/normal materials add surface detail.',
        'Body, face and hand detail views make the sculpt easier to inspect. The asymmetric outfit, paper ferrets and bunny stay editable.'
    ])
    html=html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    return html
