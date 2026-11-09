"""§E v11.361 · fix native hand starter opening and add Quest 2 Touch models."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_361_WEBXR_STARTERS_OPEN_AND_TOUCH'

def one(src,old,new,what):
    if src.count(old)!=1:raise AssertionError(('v11.361',what,src.count(old),old[:100]))
    return src.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/webxr_model_starters_v11_361.js').read_text('utf8')
    for item in ['async function se361OpenStarter(id,force=false)','async function se361ControllerScene(side)',
                 'se358WebXRHandScene(spec.side)','se232ActivateSelectedModelWorkspace();',
                 'ModelAtelier.status()', 'se361InstallStarterClicks()', 'se361StarterCheck(asset,spec)']:
        if item not in js:raise AssertionError(('v11.361 missing starter integration',item))
    html=one(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
             'install native model starter loader')
    cards=''.join(
      '<button class="project-card den" data-project-template="webxr-touch-'+side+'">'
      '<span class="project-icon">🎮</span><strong>Quest 2 Touch · '+side.title()+' Controller</strong>'
      '<span class="template-tag">STARTER MODEL · EDITABLE CONTROLLER</span>'
      '<p>Original WebXR Oculus Touch v3 controller shell, button, trigger, grip and thumbstick '
      'meshes with UV-painted textures. MIT-licensed native model.</p>'
      '<span class="hint den-glow">Open model and edit components</span></button>'
      for side in ('left','right'))
    html=one(html,
      '<button class="project-card den" data-project-template="webxr-hand-left">',
      cards+'<button class="project-card den" data-project-template="webxr-hand-left">',
      'add controllers beside the WebXR hand model starters')
    # Startup routes use the same repaired path as a project-card click.
    anchor="  se358OpenWebXRHand(hand.slice(-4)==='left'?'left':'right',true);"
    html=one(html,anchor,"  se361OpenStarter(hand,true);",'hand deep-link project opener')
    html=one(html,"function se128LaunchStartupProject(){\n const hand=new URLSearchParams(location.search).get('project');",
      """function se128LaunchStartupProject(){
 const touch=new URLSearchParams(location.search).get('project');
 if(touch==='webxr-touch-left'||touch==='webxr-touch-right'){
  se361OpenStarter(touch,true);
  window.se128StartupPending=false;return;
 }
 const hand=new URLSearchParams(location.search).get('project');""",
      'controller direct project routes')
    for old,new,why in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_360_MODEL_VR_SPATIAL_MENUS',MARKER,'marker'),
      ('ENGINE · MAKER v11.360','ENGINE · MAKER v11.361','visible title'),
      ('v11.360 · spatial menus, tactile buttons and smooth VR feedback',
       'v11.361 · fixed WebXR hands and Quest 2 controller model starters','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.360'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.361'",'build id'),
      ('<title>§wyrl§ Engine · Maker v11.360</title>',
       '<title>§wyrl§ Engine · Maker v11.361</title>','browser title')
    ]:html=one(html,old,new,why)
    old=" source.engine='§wyrl§ Engine · Maker v11.360';source.version=11.360;"
    if html.count(old)!=4:raise AssertionError(('v11.361 model provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.361';source.version=11.361;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.360' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.360','changes':notes.get('changes',[])})
    notes.update(version='v11.361',date='2026-11-08',
       title='Working hand starter projects and Quest 2 Touch controller models',
       changes=[
         'Projects → Starter Models now includes two original Quest 2 Touch controller reference models alongside the existing left and right WebXR hand starters.',
         'Quest controller models contain source-faithful separately editable shell, trigger, grip, thumbstick and face-button mesh sections, original UVs and their 512px color texture.',
         'Both earlier hand starters and both new controller starters share a reliable native project open route with active Model Studio confirmation and visible error feedback.',
         'Original WebXR controller models are derived from MIT-licensed oculus-touch-v3 GLB assets. The source provenance and attribution are bundled with the model geometry.',
         'Keep existing model projects, materials, UV editor, save/export and Model VR controls unchanged; physical Quest/phone acceptance remains owner testing.'
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+count:]
