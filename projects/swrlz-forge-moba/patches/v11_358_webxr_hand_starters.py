"""§E v11.358: two real WebXR reference hand starter models, bundled and editable."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_358_WEBXR_HAND_STARTERS'

def once(html,old,new,why):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.358',why,count,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/webxr_reference_hand_starters_v11_358.js').read_text('utf8')
    for expected in [
        'function se358OpenWebXRHand', 'async function se358WebXRHandScene',
        'topologyMesh:structuredClone(asset.mesh)', 'referenceJoints=structuredClone',
        'se358PreviousCreateTemplate', 'se232ActivateSelectedModelWorkspace'
    ]:
        if expected not in js:raise AssertionError(('v11.358 starter',expected))
    for expected in [
        'data-project-template="plain-hand-base"',
        'function se128LaunchStartupProject(){',
        'window.SWRLZ_FORGE_BUILD=',
        'se232ActivateSelectedModelWorkspace',
        'function se336UVLayout(mesh, canvas)'
    ]:
        if expected not in html:raise AssertionError(('v11.358 prerequisite',expected))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=','install native hand starters')
    cards=''.join(
      '<button class="project-card den" data-project-template="webxr-hand-'+side+'">'
      '<span class="project-icon">🖐️</span><strong>WebXR '+side.title()+' Hand</strong>'
      '<span class="template-tag">STARTER MODEL · EDITABLE HAND REFERENCE</span>'
      '<p>Actual '+side+' generic-hand mesh with native polygon editing, original UVs and '
      '25 joint reference landmarks. MIT-licensed; independent project.</p>'
      '<span class="hint den-glow">Sculpt or compare anatomy</span></button>'
      for side in ('left','right'))
    html=once(html,
      '<button class="project-card den" data-project-template="plain-hand-base">',
      cards+'<button class="project-card den" data-project-template="plain-hand-base">',
      'add two Model tab cards')
    html=once(html,'function se128LaunchStartupProject(){',
      """function se128LaunchStartupProject(){
 const hand=new URLSearchParams(location.search).get('project');
 if(hand==='webxr-hand-left'||hand==='webxr-hand-right'){
  se358OpenWebXRHand(hand.slice(-4)==='left'?'left':'right',true);
  window.se128StartupPending=false;return;
 }""",
      'open independent direct starter routes')
    for old,new,label in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_357_UV_GUIDE_FIRST',MARKER,'deploy marker'),
      ('ENGINE · MAKER v11.357','ENGINE · MAKER v11.358','visible label'),
      ('v11.357 · wireframe-first UV import and export',
       'v11.358 · WebXR left and right hand reference starters','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.357'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.358'",'build'),
      ('<title>§wyrl§ Engine · Maker v11.357</title>',
       '<title>§wyrl§ Engine · Maker v11.358</title>','title')
    ]:html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.357';source.version=11.357;"
    count=html.count(old)
    if count!=3:raise AssertionError(('v11.358 model metadata',count))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.358';source.version=11.358;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.357' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.357','changes':notes.get('changes',[])})
    notes.update(version='v11.358',date='2026-11-08',
      title='WebXR left and right hand reference starters',
      changes=[
       'Two separate WebXR Left Hand and WebXR Right Hand cards in Projects → Starter Models; existing models and games are unchanged.',
       'Each project contains the original generic-hand 1,360-vertex anatomical surface with 2,314 real mesh triangles and UV coordinates in native editable topology.',
       'The WebXR source includes 25 joint reference landmarks stored as geometry reference metadata; this is not a live hand-tracking or animated skin rig.',
       'Bundled, offline-ready native reference geometry converted from MIT-licensed public generic-hand GLB assets, with attribution/license and original source blob IDs.',
       'Regular Model Studio sculpt, selection, UV paint/slide, Undo/Redo, JSON save and export remain available; no new VR ray/hand control system.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
