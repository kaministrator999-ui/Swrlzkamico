"""New organic sheep starter and rebuilt quadruped wolf starter: continuous welded anatomy, shaped ears and faces, cloven hooves/paws, editable meshes, 4K wool/fur color and normal maps, portable GLB export."""
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1,(old[:100],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    r=Path(__file__).resolve().parents[1]
    html=once(html,'file.size>8_000_000','file.size>64_000_000')
    html=once(html,'Model file must be JSON below 8 MB.','Model file must be JSON below 64 MB.')
    html=once(html,'atelierLODSavedVertices=9000','atelierLODSavedVertices=65536')
    html=once(html,'atelierLODSavedTriangles=16000','atelierLODSavedTriangles=120000')
    html=once(html,"t.set==='astra-4k'","['astra-4k','wildwood-4k'].includes(t.set)")
    html=once(html,"atelierCourierMap('color',b.tile)","atelierCourierMap('color',b.tile,b.set)")
    html=once(html,"atelierCourierMap('normal',b.tile)","atelierCourierMap('normal',b.tile,b.set)")
    html=once(html,"m.userData.atelierAtlas='astra-4k'","m.userData.atelierAtlas=b.set")
    html=once(html,"images.length===2&&images.every", "images.length>=2&&images.every")
    html=once(html,'  function refreshList(){',(r/'runtime/model_atelier_animal_surfaces_v11_87.js').read_text()+'\n  function refreshList(){')
    html=once(html,"currentProject?.canonicalId!=='comet-courier'", "!['comet-courier','sheep-model','wolf-model'].includes(currentProject?.canonicalId)")
    html=once(html,"next.textureBinding={set:'astra-4k',tile,normalStrength:","next.textureBinding={set:p.textureBinding?.set||(p.organicSurface?'wildwood-4k':'astra-4k'),tile,normalStrength:")
    # Embed both atlas sets if users mix legacy and organic materials.
    old="const textured=model().parts.some(p=>p.textureBinding);const images=[];"
    html=once(html,old,"const textureSets=[...new Set(model().parts.filter(p=>p.textureBinding).map(p=>p.textureBinding.set))],textured=textureSets.length>0;const images=[],textures=[],textureIndices=new Map();")
    html=once(html,"if(textured)for(const [type,mime]", "for(const set of textureSets)for(const [type,mime]")
    html=once(html,"fetch(atelierCourierSources[type])", "fetch(atelierAnimalTextureSources(set)[type])")
    html=once(html,"images.push({bufferView:add(new Uint8Array(await response.arrayBuffer())),mimeType:mime,name:type+' 4096px atlas'});", "textureIndices.set(set+'|'+type,textures.length);textures.push({source:images.length,sampler:0});images.push({bufferView:add(new Uint8Array(await response.arrayBuffer())),mimeType:mime,name:set+' '+type+' 4096px atlas'});")
    html=once(html,'baseColorTexture={index:0}',"baseColorTexture={index:textureIndices.get(p.textureBinding.set+'|color')}")
    html=once(html,'normalTexture={index:1,scale:',"normalTexture={index:textureIndices.get(p.textureBinding.set+'|normal'),scale:")
    html=once(html,'emissiveTexture={index:0}',"emissiveTexture={index:textureIndices.get(p.textureBinding.set+'|color')}")
    html=once(html,'doc.textures=[{source:0,sampler:0},{source:1,sampler:0}]','doc.textures=textures')
    html=once(html,"download('astra-comet-courier.glb',output", "download((currentProject.canonicalId||'model')+'.glb',output")
    html=once(html,"generator:'§wyrl§ Engine v11.77 native textured mesh export'","generator:'§wyrl§ Engine v11.87 native textured mesh export'")
    html=once(html,'ModelAtelier.install();',(r/'runtime/model_atelier_animals_v11_87.js').read_text()+'\n'+(r/'runtime/model_atelier_animal_projects_v11_87.js').read_text()+'\nModelAtelier.install();')
    html=once(html,'return Object.freeze({createCourierHunter:', 'return Object.freeze({animalStatus:atelierAnimalStatus,createCourierHunter:')
    html=once(html,'open:()=>ModelAtelier.open(),loadStarter:',"animalStatus:()=>ModelAtelier.animalStatus(),loadAnimal:(species,options={})=>loadAnimalProject(species,!!options.force,!!options.rebuild),open:()=>ModelAtelier.open(),loadStarter:")
    html=once(html,"if(['comet-courier','blank-model'].includes(new URLSearchParams(location.search).get('project')))queueMicrotask(()=>loadCourierProject", "if(new URLSearchParams(location.search).get('project')==='comet-courier')queueMicrotask(()=>loadAnimalProject('wolf',true));\nif(['blank-model'].includes(new URLSearchParams(location.search).get('project')))queueMicrotask(()=>loadCourierProject")
    html=once(html,"if(['comet-courier','blank-model'].includes(currentProject?.canonicalId))", "if(['comet-courier','blank-model','sheep-model','wolf-model'].includes(currentProject?.canonicalId))")
    start=html.index('<button class="project-card den" data-project-template="comet-courier">');end=html.index('</button>',start)+len('</button>')
    cards='''<button class="project-card den" data-project-template="wolf-model"><span class="project-icon">🐺</span><strong>Fen · Wildwood Wolf</strong><span class="template-tag">ORGANIC MODEL · 4K FUR</span><p>A natural quadruped with a fused torso, shoulder blades, tapered muzzle, hocks, paws and a flowing brush tail.</p><span class="hint den-glow">Open wolf model starter</span></button><button class="project-card den" data-project-template="sheep-model"><span class="project-icon">🐑</span><strong>Clover · Meadow Sheep</strong><span class="template-tag">ORGANIC MODEL · 4K WOOL</span><p>Continuous sculpted fleece, folded ears, an ovine muzzle and cloven hooves. Edit the native surface and every detail.</p><span class="hint den-glow">Open new sheep model starter</span></button>'''
    html=html[:start]+cards+html[end:]
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_86_SHEEP_HOUSE_SLIDE','SWYRL_ENGINE_DEPLOY_MARKER: V11_87_ORGANIC_ANIMAL_STARTERS'),('ENGINE · MAKER v11.86','ENGINE · MAKER v11.87'),('v11.86 · sheep steer around houses','v11.87 · organic sheep & wolf model starters'),("window.SWRLZ_FORGE_BUILD={version:'v11.86'","window.SWRLZ_FORGE_BUILD={version:'v11.87'"),('<title>§wyrl§ Engine · Maker v11.86</title>','<title>§wyrl§ Engine · Maker v11.87</title>')]:html=once(html,old,new)
    return html
