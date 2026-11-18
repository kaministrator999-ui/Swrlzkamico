"""§E v11.515 — deterministic 3-stage native XR menu layering, stable world
anchors, smaller controller-linked button labels/glows. Integrates current
v11.445 spatial rail/operation/settings + v11.362 Quest controller visual.
No new menu, no independent menu input, no change to persistent model data.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_515_XR_MENU_CONTROLLER_CLARITY'
def one(text,old,new,description):
 n=text.count(old)
 if n!=1:raise AssertionError(('v11.515',description,n,old[:130]))
 return text.replace(old,new,1)
def apply(html):
 assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_514_NATIVE_XR_RIG' in html
 runtime=(ROOT/'runtime/model_vr_spatial_polish_v11_515.js').read_text('utf8')
 assert 'SE515_SPATIAL_VR_POLISH_END' in runtime
 html=one(html,'installPerformanceSettings();se189InstallPerfUI();',
              runtime+'\ninstallPerformanceSettings();se189InstallPerfUI();',
              'extend the sole native WebXR frame pipeline')
 start=html.index('/* SE445_VR_PROGRESSIVE_TOOLS_START */')
 end=html.index('/* SE445_VR_PROGRESSIVE_TOOLS_END */',start)
 stage=html[start:end]
 # Critical: Three.js sorts transparent planes with identical renderOrder by
 # camera depth. Looking up/down can make the backplate paint OVER its own
 # UI buttons. Explicit render layers keep hit targets and drawn controls
 # coherent regardless of head angle.
 stage=one(stage,'mesh.renderOrder=8400;mesh.frustumCulled=false;',
   """mesh.renderOrder=name.includes('background')?8380:
    name.startsWith('Close ')?8660:name.startsWith('Quick ')?8610:8520;
   mesh.frustumCulled=false;""",'deterministic stage plane layer ordering')
 # Keep rigging reachable through the ACTUAL three-stage menu (v11.445),
 # not merely the hidden original console whose horizontal tabs are obsolete.
 stage=one(stage,'  const presets={',
   """  const presets={
   rig:[['rig','Bone posing'],['rig-prev','Previous joint'],['rig-next','Next joint'],
    ['rig-weights','Weight painting'],['rig-undo','Undo rig edit'],
    ['rig-pose-x-minus','Rotate X −5°'],['rig-pose-x-plus','Rotate X +5°'],
    ['rig-pose-y-minus','Rotate Y −5°'],['rig-pose-y-plus','Rotate Y +5°'],
    ['rig-pose-z-minus','Rotate Z −5°'],['rig-pose-z-plus','Rotate Z +5°']],
   'rig-weights':[['rig-weight-add','Add influence'],['rig-weight-erase','Erase influence'],
    ['rig-radius-minus','Radius −'],['rig-radius-plus','Radius +'],
    ['rig-strength-minus','Weight −'],['rig-strength-plus','Weight +'],
    ['rig-prev','Previous joint'],['rig-next','Next joint'],
    ['rig-undo','Undo rig edit'],['rig-weight-stop','Stop painting'],['rig','Bone posing']],
""",'native rigging submenu group')
 stage=one(stage,"   ['delete-selected','Delete',null]",
   "   ['rig','Rigging','rig'],['delete-selected','Delete',null]",
   'visible Rigging on existing stage primary tool rail')
 stage=one(stage,"  function choosePage(action){",
   """  function choosePage(action){
   if(action==='rig'||action.startsWith('rig-'))
    return action==='rig-weights'||action.startsWith('rig-weight-')||
     action.startsWith('rig-radius-')||action.startsWith('rig-strength-')
     ?'rig-weights':'rig';""",
   'existing operation stage maps Rigging to native rig pages')
 html=html[:start]+stage+html[end:]
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_514_NATIVE_XR_RIG',MARKER),
  ('ENGINE · MAKER v11.514','ENGINE · MAKER v11.515'),
  ('v11.514 · native spatial Rigging and Weight Painting in immersive WebXR',
   'v11.515 · stable XR menus and precise controller button guides'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.514'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.515'"),
  ('<title>§wyrl§ Engine · Maker v11.514</title>',
   '<title>§wyrl§ Engine · Maker v11.515</title>')
 ]:html=one(html,before,after,'release version identity')
 prior=" source.engine='§wyrl§ Engine · Maker v11.514';source.version=11.514;"
 assert html.count(prior)==5,('v11.515 model provenance',html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.515';source.version=11.515;")
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[item for item in notes.get('history',[]) if item.get('version')!='v11.514']
 notes['history'].insert(0,{'version':'v11.514','changes':notes.get('changes',[])})
 notes.update(version='v11.515',date='2026-11-18',
 title='Stable immersive tool menus and mapped controller button guidance',
 changes=[
  'Existing immersive three-stage tool rail, operation list and native modifier panel now use explicit transparent draw layers: backdrop, labels/cards, quick controls and close buttons. Controls are not overdrawn by their own transparent background when looking up or down.',
  'The native spatial menu preserves its actual world-space anchor when the model camera orbits, while its front billboards toward the headset. User Grab/Grip menu placement remains writable to the existing saved placement key; no head-follow translation.',
  'The existing far-right §E tool rail and middle operation submenu now expose Rigging and Weight Painting from v11.514, mapping to the existing native menu pages and controller actions rather than a hidden legacy horizontal tab.',
  'Quest 2 Touch controller-attached key labels become smaller and are connected to each corresponding hardware actuator by a thin color-matched guide line and subtle matching pressed/rest glow; controller model or fallback anchors are reused.',
  'Previous native controller profiles remain authoritative, including contextual Rigging/Weight Painting labels, ray hover/Trigger/Grip priority, native cancel/Undo, menu repositioning and on-exit visual cleanup.',
  'Source geometry, UVs, starter models, project revision history and account behavior are untouched. Actual Quest headset viewing-angle, hand comfort and visibility acceptance remain owner-device QA.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
