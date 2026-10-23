"""Roomier 0.75 m building lanes; sheep align through narrow house passages instead of steering away. Much larger, inset joystick and two spaced rings of skill/building buttons scale to phone and wide Android viewports. Original Astra wolf design returns with its cape, satchel, lantern and curled comet tail preserved, plus welded organic anatomy and the original 4K textures."""
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1,(old[:100],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    r=Path(__file__).resolve().parents[1]
    html=once(html,'const ST_LANE_GAP = .6;','const ST_LANE_GAP = .75;')
    # A fresh joystick destination must not keep following a previous corner.
    html=once(html,'else{unit.order.x=target.x;unit.order.z=target.z;unit.destination.copy(target);}', 'else{unit.order.x=target.x;unit.order.z=target.z;unit.destination.copy(target);unit.path=[];unit.pathVersion=-1;unit.repathAt=0;}')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',(r/'runtime/sheep_passage_controls_v11_88.js').read_text()+'\nwindow.SWRLZ_FORGE_BUILD=')
    html=once(html,'ModelAtelier.install();',(r/'runtime/model_atelier_courier_organic_v11_88.js').read_text()+'\nModelAtelier.install();')
    html=once(html,'  function refreshList(){',"""  const atelierCourierAnimalStatusBase=atelierAnimalStatus;
  atelierAnimalStatus=function(){
    if(!model()?.parts.some(p=>p.organicSurface?.species==='courier'))return atelierCourierAnimalStatusBase();
    const meshes=modelRoot.children.filter(m=>m.isMesh&&m.userData.atelierId).map(m=>({id:m.userData.atelierId,vertices:m.geometry.attributes.position.count,triangles:(m.geometry.index?.count||m.geometry.attributes.position.count)/3,baseColorSize:[m.material.map?.image?.width||0,m.material.map?.image?.height||0],normalSize:[m.material.normalMap?.image?.width||0,m.material.normalMap?.image?.height||0]}));
    return {valid:validParts(model().parts)&&atelierGroupsValid(model().meshGroups||[],model().parts),species:'courier',parts:model().parts.length,triangles:meshes.reduce((n,m)=>n+m.triangles,0),meshes};
  };
  function refreshList(){""")
    html=once(html,'<strong>Fen · Wildwood Wolf</strong>','<strong>Astra · Comet Courier</strong>')
    html=once(html,'A natural quadruped with a fused torso, shoulder blades, tapered muzzle, hocks, paws and a flowing brush tail.','The original blue courier: sculpted anatomy, expressive amber eyes, traveling gear and a huge curled comet tail. Native editable surfaces and 4K textures.')
    html=html.replace('</head>','<style id="sheepReachableControls">'+(r/'runtime/sheep_reachable_controls_v11_88.css').read_text()+'</style>\n</head>',1)
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_87_ORGANIC_ANIMAL_STARTERS','SWYRL_ENGINE_DEPLOY_MARKER: V11_88_PASSAGES_CONTROLS_ORIGINAL_WOLF'),('ENGINE · MAKER v11.87','ENGINE · MAKER v11.88'),('v11.87 · organic sheep & wolf model starters','v11.88 · roomier lanes, reachable controls & original Astra'),("window.SWRLZ_FORGE_BUILD={version:'v11.87'","window.SWRLZ_FORGE_BUILD={version:'v11.88'"),('<title>§wyrl§ Engine · Maker v11.87</title>','<title>§wyrl§ Engine · Maker v11.88</title>')]:html=once(html,old,new)
    return html
