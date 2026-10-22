"""Recoverable building input and connected joystick walkways."""
from pathlib import Path
import json,ast,re

def once(html,old,new):
    assert html.count(old)==1,(old[:120],html.count(old))
    return html.replace(old,new,1)

def release_notes(root,manifest):
    notes=json.loads((root/'runtime/engine_release_notes_v11_84.json').read_text())
    version=manifest['name'].removeprefix('§wyrl§ Engine ')
    known=notes['version'];groups={}
    for name in manifest['patches']:
        match=re.match(r'v(\d+)(?:_(\d+))?',Path(name).stem)
        key='v'+match.group(1)+'.'+(match.group(2) or '0')
        doc=ast.get_docstring(ast.parse((root/name).read_text())) or Path(name).stem.replace('_',' ')
        groups.setdefault(key,[]).append(' '.join(doc.split()))
    if version!=known:
        notes.update(version=version,title='Latest engine update',date='',changes=groups.get(version,['Engine '+version+' update.']))
    groups[known]=json.loads((root/'runtime/engine_release_notes_v11_84.json').read_text())['changes']
    notes['history']=[{'version':key,'changes':items} for key,items in reversed(list(groups.items())) if key!=version]
    return notes

def apply(html):
    r=Path(__file__).resolve().parents[1]
    data=json.loads((r/'scenes/sheep-tag-wide-walkways-v11-84.swyrl.json').read_text())
    prefix='const ST_CANONICAL_PROJECT=';start=html.index(prefix)+len(prefix);_,size=json.JSONDecoder().raw_decode(html[start:])
    html=html[:start]+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    html=once(html,"const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-vast-wildwood-v11-80.swyrl.json';","const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-wide-walkways-v11-84.swyrl.json';")
    html=html.replace('[64,128].includes','[64,128,160].includes')
    html=html.replace('256 × 256 m','320 × 320 m')
    html=once(html,"Math.max(72,Math.min(112,$('viewport').getBoundingClientRect().height*.16))","Math.max(128,Math.min(180,$('viewport').getBoundingClientRect().height*.22))")
    css=(r/'runtime/sheep_skill_rings_v11_84.css').read_text()+(r/'runtime/engine_release_notes_v11_84.css').read_text();at=html.index('</head>');html=html[:at]+'<style id="sheepSkillRings">'+css+'</style>\n'+html[at:]
    # Retire both old window placement owners; native UI commands remain shared.
    for old in ["window.addEventListener('pointerdown',event=>{\n  stTouchPlacementSync();", "window.addEventListener('pointermove',event=>{\n  stTouchPlacementSync();", "window.addEventListener('pointerup',event=>{\n  stTouchPlacementSync();", "window.addEventListener('pointercancel',event=>{\n  stTouchPlacement.touchPointers.delete(event.pointerId);"]:
        html=once(html,old,old.split('\n',1)[0]+'\n  if(stBuildInputOwns())return;\n'+old.split('\n',1)[1])
    for old in ["window.addEventListener('pointerdown',event=>{\n if(stBuildDrag.pointer", "window.addEventListener('pointermove',event=>{\n if(event.pointerId!==stBuildDrag.pointer)", "window.addEventListener('pointerup',event=>{\n if(event.pointerId!==stBuildDrag.pointer)"]:
        html=once(html,old,old.split('\n',1)[0]+'\n if(stBuildInputOwns())return;\n'+old.split('\n',1)[1])
    html=once(html,"if(kind==='st-ramp'){const entry=stRampEntry", "if(kind==='st-ramp'&&!stWalkUpperBuilder(owner)){const entry=stRampEntry")
    js='\n'.join((r/'runtime'/name).read_text() for name in ['sheep_build_recovery_v11_84.js','sheep_walkways_v11_84.js','sheep_skill_rings_v11_84.js','engine_release_notes_v11_84.js'])
    js='const SE_RELEASE_NOTES='+json.dumps(release_notes(r,json.loads((r/'source-manifest.json').read_text())),ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n'+js
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_83_DRAG_BUILD_SOFT_FOG','SWYRL_ENGINE_DEPLOY_MARKER: V11_84_BUILD_RECOVERY_WALKWAYS'),('ENGINE · MAKER v11.83','ENGINE · MAKER v11.84'),('v11.83 · drag building & smooth fog','v11.84 · reliable building & connected walkways'),("window.SWRLZ_FORGE_BUILD={version:'v11.83'","window.SWRLZ_FORGE_BUILD={version:'v11.84'"),('<title>§wyrl§ Engine · Maker v11.83</title>','<title>§wyrl§ Engine · Maker v11.84</title>')]:html=once(html,old,new)
    return html
