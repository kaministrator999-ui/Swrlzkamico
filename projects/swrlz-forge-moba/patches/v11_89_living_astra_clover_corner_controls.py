"""Astra's full organic anatomy pass: shaped shoulders, elbows/hocks, continuous four-toed paws, tapered chest, carved eye sockets, canine pupils, cupped ears and nostrils; original traveling gear and comet tail retained. Clover's new organic sheep now populate Sheep Tag with shared 4K textures and animated head/leg/tail joints. Touch controls shrink to roughly 45% of the previous wide-phone size; joystick returns to the bottom-left corner, with compact separated building/skill rings on the right."""
from pathlib import Path
import gzip,json

def once(html,old,new):
    assert html.count(old)==1,(old[:100],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    r=Path(__file__).resolve().parents[1]
    html=once(html,'  function refreshList(){',(r/'runtime/sheep_clover_v11_89.js').read_text()+'\n  function refreshList(){')
    html=once(html,'return Object.freeze({animalStatus:atelierAnimalStatus,','return Object.freeze({createCloverSheep:atelierCloverSheep,animalStatus:atelierAnimalStatus,')
    html=once(html,"if(type==='st-wolf')return ModelAtelier.createCourierHunter();", "if(type==='st-sheep')return ModelAtelier.createCloverSheep();\n  if(type==='st-wolf')return ModelAtelier.createCourierHunter();")
    clover=json.loads(gzip.decompress((r/'payload/clover-game-v11-89.swyrl.json.gz').read_bytes()))['project']['modelAtelier']
    html=once(html,'ModelAtelier.install();','const ST_CLOVER_GAME_MODEL='+json.dumps(clover,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'+(r/'runtime/model_atelier_living_astra_v11_89.js').read_text()+'\nModelAtelier.install();')
    html=once(html,"fetch('scenes/model-atelier-original-wolf-organic-v11-88.swyrl.json')", "fetch('scenes/model-atelier-living-astra-v11-89.swyrl.json')")
    html=once(html,'window.SWRLZ_FORGE_BUILD=',(r/'runtime/sheep_clover_inspect_v11_89.js').read_text()+'\nwindow.SWRLZ_FORGE_BUILD=')
    html=html.replace('</head>','<style id="sheepCornerControls">'+(r/'runtime/sheep_corner_controls_v11_89.css').read_text()+'</style>\n</head>',1)
    html=once(html,'The original blue courier: sculpted anatomy, expressive amber eyes, traveling gear and a huge curled comet tail. Native editable surfaces and 4K textures.','The original blue courier with flowing muscle and fur, sculpted joints, four-toed paws, canine eyes and cupped ears. Traveling gear, comet tail and 4K textures retained.')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_88_PASSAGES_CONTROLS_ORIGINAL_WOLF','SWYRL_ENGINE_DEPLOY_MARKER: V11_89_LIVING_ASTRA_CLOVER'),('ENGINE · MAKER v11.88','ENGINE · MAKER v11.89'),('v11.88 · roomier lanes, reachable controls & original Astra','v11.89 · living Astra, Clover flock & corner controls'),("window.SWRLZ_FORGE_BUILD={version:'v11.88'","window.SWRLZ_FORGE_BUILD={version:'v11.89'"),('<title>§wyrl§ Engine · Maker v11.88</title>','<title>§wyrl§ Engine · Maker v11.89</title>')]:html=once(html,old,new)
    return html
