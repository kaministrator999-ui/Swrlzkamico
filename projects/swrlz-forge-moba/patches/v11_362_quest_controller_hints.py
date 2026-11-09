"""§E v11.362 · Quest Touch native controller visuals and contextual button labels."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_362_QUEST_CONTROLLER_HINTS'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.362',label,count,old[:110]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/model_vr_controller_hints_v11_362.js').read_text('utf8')
    assert 'SE362_CONTROLLER_HINTS_START' in js
    assert 'se362ControllerConnected' in js and 'se362Frame' in js
    html=once(html,'function se340MakeController(index){',
      js+'\nfunction se340MakeController(index){','controller visuals before XR controller creation')
    html=once(html,
      'r.connected=e=>{r.input=e.data||null;r.blockGrip=true;r.buttons=[];};',
      'r.connected=e=>{r.input=e.data||null;r.blockGrip=true;r.buttons=[];se362ControllerConnected(r);};',
      'attach tracked controller model when hardware connects')
    html=once(html,
      'r.disconnected=()=>{if(se340XR.gesture?.record===r)se340CancelGesture(\'Controller disconnected; preview canceled.\');r.input=null;r.targetTracked=false;r.gripTracked=false;};',
      'r.disconnected=()=>{if(se340XR.gesture?.record===r)se340CancelGesture(\'Controller disconnected; preview canceled.\');se362ControllerDisconnected(r);r.input=null;r.targetTracked=false;r.gripTracked=false;};',
      'dispose model and label resources on disconnect')
    html=once(html,
      'record.ray.visible=record.targetTracked;record.dot.visible=record.targetTracked;record.body.visible=record.gripTracked;',
      'record.ray.visible=record.targetTracked;record.dot.visible=record.targetTracked;record.body.visible=record.gripTracked&&!record.se362Visual?.ready;',
      'hide old capsule when the actual hardware model is available')
    html=once(html,
      'se360AdvanceMenu(dt);renderer.render(s.scene,s.camera);',
      'se360AdvanceMenu(dt);se362Frame(s);renderer.render(s.scene,s.camera);',
      'refresh controller labels in the existing XR frame loop')
    # The labels are strictly editor-only and never touch the saved model document.
    start=html.index('function se340Cleanup(expected){')
    end=html.index('async function se340ModelXRExit(){',start)
    cleanup=html[start:end]
    cleanup=once(cleanup,'for(const r of s.controllers){',
      'for(const r of s.controllers){\n  se362ControllerDisconnected(r);',
      'release controller GPU allocations on session exit')
    html=html[:start]+cleanup+html[end:]
    for before,after,label in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_361_WEBXR_STARTERS_OPEN_AND_TOUCH',MARKER,'deployment marker'),
      ('ENGINE · MAKER v11.361','ENGINE · MAKER v11.362','visible build'),
      ('v11.361 · fixed WebXR hands and Quest 2 controller model starters',
       'v11.362 · live Quest Touch controllers and tool-aware labels','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.361'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.362'",'runtime build'),
      ('<title>§wyrl§ Engine · Maker v11.361</title>',
       '<title>§wyrl§ Engine · Maker v11.362</title>','browser title')
    ]:
      html=once(html,before,after,label)
    source=" source.engine='§wyrl§ Engine · Maker v11.361';source.version=11.361;"
    if html.count(source)!=4:
        raise AssertionError(('v11.362 provenance',html.count(source)))
    html=html.replace(source," source.engine='§wyrl§ Engine · Maker v11.362';source.version=11.362;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version')=='v11.361' for item in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.361','changes':notes.get('changes',[])})
    notes.update(version='v11.362',date='2026-11-08',
      title='Native Quest Touch controller hints for Model VR',
      changes=[
        'Immersive Model Studio now reuses the locally bundled MIT-licensed WebXR oculus-touch-v3 left/right controller model geometry, following the native grip tracking for each hand. If assets cannot load, retain the existing simple grip model.',
        'Tiny controller-attached labels show what trigger, grip, thumbstick and face buttons actually do. Labels face the headset and react to presses while preserving the existing frame, pointer, raycast and menu budgets.',
        'Controller hints derive from the active controller profile and the actual Model VR operation. Inspect, Move, Rotate, Scale, Sculpt brushes, Draw, Extrude, Lasso and Two-hand update their text as tools change; quick-wheel and guide states show secondary bindings.',
        'Use native input/profile resolution; do not reassign the Meta button, replace the right-stick camera orbit, introduce hand-tracking gesture requirements, or add another XR renderer/frame loop.',
        'The visual controller model and labels are editor-only, not authored geometry. Disconnect, tracking loss and VR exit clean up visual resources. No model parts, UVs, materials or stored projects are modified.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+length:]
