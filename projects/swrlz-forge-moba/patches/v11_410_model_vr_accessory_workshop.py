"""§E v11.410 — native editable hip-pouch workshop and spatial tools."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_410_MODEL_VR_ACCESSORY_WORKSHOP'
def one(src,old,new):
    assert src.count(old)==1,('v11.410 anchor',old[:100],src.count(old))
    return src.replace(old,new,1)
def apply(html):
    native=(ROOT/'runtime/model_accessory_bridge_v11_410.js').read_text('utf8')
    html=one(html,'/* ATELIER_BRIDGE_END */',native+'\n/* ATELIER_BRIDGE_END */')
    html=one(html,'vrCreate:se390ModelCreate,chatAction:',
             'vrCreate:se390ModelCreate,vrAccessory:se410ModelAccessory,chatAction:')
    a=html.index('/* SE360_MODEL_VR_UI_START */');b=html.index('/* SE360_MODEL_VR_UI_END */',a)+len('/* SE360_MODEL_VR_UI_END */')
    html=html[:a]+(ROOT/'runtime/model_studio_vr_ui_v11_410.js').read_text('utf8').rstrip()+html[b:]
    runtime='\n'.join((ROOT/'runtime'/n).read_text('utf8') for n in ['model_accessory_geometry_v11_410.js','model_vr_accessory_workshop_v11_410.js'])
    html=one(html,'/* SE390_MODEL_VR_FLUENT_TOOLS_END */','/* SE390_MODEL_VR_FLUENT_TOOLS_END */\n'+runtime)
    hints="""const se410PreviousHintLabel=se362CleanLabel;
se362CleanLabel=function(action,s){
 if(s.se410Accessory){
  if(action==='select')return 'Place hip pouch';
  if(action==='orbit')return 'Pouch: turn / size';
  if(action==='cancel'||action==='undo')return 'Cancel pouch preview';
  if(['grab','pan','multiselect','fine'].includes(action))return '';
 }
 return se410PreviousHintLabel(action,s);
};"""
    html=one(html,'/* SE390_MODEL_VR_HOTKEY_HINTS_END */','/* SE390_MODEL_VR_HOTKEY_HINTS_END */\n'+hints)
    html=one(html,'se390CreationFrame(s,dt);se350Dispatch(sample);se350Navigate(sample,dt);',
             'se390CreationFrame(s,dt);se410AccessoryFrame(s,dt);se350Dispatch(sample);se350Navigate(sample,dt);')
    html=one(html,'const state={creationActive:','const state={...se410AccessoryUI(),creationActive:')
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_391_SHEEP_QUEST_Y_TOOLS_RADIAL',MARKER),
        ('ENGINE · MAKER v11.391','ENGINE · MAKER v11.410'),
        ('v11.391 · Quest Sheep Tag Y quick tools radial','v11.410 · shape and fit editable hip pouches in VR'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.391'","window.SWRLZ_FORGE_BUILD={version:'v11.410'"),
        ('<title>§wyrl§ Engine · Maker v11.391</title>','<title>§wyrl§ Engine · Maker v11.410</title>')]:html=one(html,before,after)
    previous=" source.engine='§wyrl§ Engine · Maker v11.391';source.version=11.391;"
    assert html.count(previous)==5,('v11.410 native provenance',html.count(previous))
    html=html.replace(previous," source.engine='§wyrl§ Engine · Maker v11.410';source.version=11.410;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key);notes,size=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.391' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.391','changes':notes.get('changes',[])})
    notes.update(version='v11.410',date='2026-11-11',title='Shape a hip pouch with an orderly VR accessory workshop',changes=[
        'Create > Accessories opens a native hip-pouch workshop. Body, Details and Fit panels adjust real hollow leather-style geometry, curved flap, loops, clasp, stitching and leaf/star emblem using readable dimensions and coordinated color swatches.',
        'Preview every change before placement. Free placement or upright surface fitting positions the bag; menu interaction holds its last placement visible. The selection-hand stick turns and sizes the draft. A fresh primary Trigger places it; B or the first Undo cancels.',
        'Placement inserts editable component meshes as one native Undo transaction and selects the complete pouch ready for Grab. Tracking, controller-profile, source-document and VR-exit changes discard uncommitted previews.',
        'Existing modeling, sculpt, drawing, selection, native save formats, game-camera behavior and the Quest Sheep Tag Y tools shortcut remain available. Physical-headset comfort remains owner-tested.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+size:]
