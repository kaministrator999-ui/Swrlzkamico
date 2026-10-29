"""Solid house contact, held-stick pathfinding, rooted ears/3D fur and game performance."""
from pathlib import Path
import gzip,json

def once(html,old,new):
    assert html.count(old)==1,(old[:90],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    r=Path(__file__).resolve().parents[1]
    html=once(html,'  function refreshList(){',(r/'runtime/sheep_furred_wolf_v11_90.js').read_text()+'\n  function refreshList(){')
    game=json.loads(gzip.decompress((r/'payload/furred-game-v11-90.swyrl.json.gz').read_bytes()))['project']['modelAtelier']
    html=once(html,'ModelAtelier.install();','const ST_ASTRA_FURRED_GAME_MODEL='+json.dumps(game,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'+(r/'runtime/model_atelier_furred_astra_v11_90.js').read_text()+'\nModelAtelier.install();')
    html=once(html,"fetch('scenes/model-atelier-living-astra-v11-89.swyrl.json')","fetch('scenes/model-atelier-furred-astra-v11-90.swyrl.json')")
    html=once(html,'window.SWRLZ_FORGE_BUILD=',(r/'runtime/sheep_solid_blockers_v11_90.js').read_text()+'\nwindow.SWRLZ_FORGE_BUILD=')
    html=once(html,'if(!force&&!due&&!run._meaningful)return null;','if(!force&&!due)return null;')
    html=once(html,'file.size>64_000_000','file.size>128_000_000');html=once(html,'Model file must be JSON below 64 MB.','Model file must be JSON below 128 MB.')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_89_LIVING_ASTRA_CLOVER','SWYRL_ENGINE_DEPLOY_MARKER: V11_90_SOLID_BLOCKERS_FURRED_ASTRA'),('ENGINE · MAKER v11.89','ENGINE · MAKER v11.90'),('v11.89 · living Astra, Clover flock & corner controls','v11.90 · solid blockers, furred Astra & smoother matches'),("window.SWRLZ_FORGE_BUILD={version:'v11.89'","window.SWRLZ_FORGE_BUILD={version:'v11.90'"),('<title>§wyrl§ Engine · Maker v11.89</title>','<title>§wyrl§ Engine · Maker v11.90</title>')]:html=once(html,old,new)
    prefix='const SE_RELEASE_NOTES=';start=html.index(prefix)+len(prefix);notes,size=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Solid blockers, furred Astra and smoother matches',date='2026-10-23',changes=[
        'Houses block sheep. Hold the joystick to walk up and find a clear route around; release to stop.',
        'Building placement no longer pushes your sheep out of the footprint; overlapping placement is rejected without charging gold.',
        'Astra has a flowing organic body, attached ears in one welded skull surface and 1,100 closed 3D fur locks.',
        'The detailed wolf keeps its original courier equipment, huge comet tail and 4K textures; game wolves use a lighter animated model.',
        'Game wolves use 29 meshes and about 69k triangles, with shared buffers and cheaper collision queries for larger house mazes.',
        'Phone recordings now sample the world 10 times per second while retaining command and event captures. Compact controls, Clover and seven-minute rounds remain.'
    ])
    html=html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    return html
