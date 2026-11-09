"""§E v11.362 · tracked Touch controllers with tool-adaptive floating labels."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_362_CONTROLLER_TOOL_LABELS'

def once(html,old,new,label):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.362',label,n,old[:110]))
    return html.replace(old,new,1)

def apply(html):
    helper=(ROOT/'runtime/model_vr_controller_labels_v11_362.js').read_text('utf8')
    for token in ('SE362_MODEL_VR_CONTROLLER_LABELS_START',
                  'assets/models/webxr-touch-v3/','se362ControllerLabels=',
                  'function renderAsset(entry,asset,side,epoch)',
                  'function bindings(s)','function repaint(b,key,description)',
                  'function dispose()'):
        if token not in helper:raise AssertionError(('missing controller labels feature',token))
    # One existing XR renderer, native controller grips and input resolver.
    html=once(html,'/* SE340_MODEL_VR_WORKSPACE_START */',
              helper+'\n/* SE340_MODEL_VR_WORKSPACE_START */','install labels module')
    html=once(html,'s.controllers=[se340MakeController(0),se340MakeController(1)];',
              's.controllers=[se340MakeController(0),se340MakeController(1)];se362ControllerLabels.setup(s.controllers);',
              'attach to tracked controller grips')
    html=once(html,'record.body.visible=record.gripTracked;',
              'record.body.visible=record.gripTracked&&!se362ControllerLabels.hasModel(record);',
              'hide synthetic capsule when source-faithful controller loads')
    html=once(html,'se350UpdateBrush();se350UpdateLassoGuide();se340SyncUI();se360AdvanceMenu(dt);renderer.render(s.scene,s.camera);',
              'se350UpdateBrush();se350UpdateLassoGuide();se340SyncUI();se360AdvanceMenu(dt);se362ControllerLabels.frame(s);renderer.render(s.scene,s.camera);',
              'update controller labels in existing XR frame')
    html=once(html,'se350Input.reset();s.inputSample=null;s.wheel=null;',
              'se362ControllerLabels.dispose();se350Input.reset();s.inputSample=null;s.wheel=null;',
              'dispose controller models and GPU label textures on exit')
    html=once(html,'lastAction:se340XR.lastAction,error:se340XR.error,menu:se340XR.ui?.inspect?.()||null,',
              'lastAction:se340XR.lastAction,error:se340XR.error,menu:se340XR.ui?.inspect?.()||null,controllerLabels:se362ControllerLabels.inspect(),',
              'expose label diagnostics')
    for old,new,label in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_361_WEBXR_STARTERS_OPEN_AND_TOUCH',MARKER,'marker'),
        ('ENGINE · MAKER v11.361','ENGINE · MAKER v11.362','visible title'),
        ('v11.361 · fixed WebXR hands and Quest 2 controller model starters',
         'v11.362 · tracked Quest controllers with adaptive button labels','headline'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.361'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.362'",'build id'),
        ('<title>§wyrl§ Engine · Maker v11.361</title>',
         '<title>§wyrl§ Engine · Maker v11.362</title>','browser title')
    ]:html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.361';source.version=11.361;"
    if html.count(old)!=4:raise AssertionError(('v11.362 project provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.362';source.version=11.362;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.361' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.361','changes':notes.get('changes',[])})
    notes.update(version='v11.362',date='2026-11-08',
      title='Touch controller models and live tool labels in Model VR',
      changes=[
        'In immersive Model Studio, each tracked Quest 2 Touch grip renders its bundled MIT-licensed WebXR input-profile controller housing, ring, trigger, squeeze, thumbstick and X/Y or A/B button meshes.',
        'Small, camera-facing, controller-attached floating labels show the actual active controller-profile mapping, including tool/brush-specific selection, sculpting, tracing, extrusion and transform actions.',
        'Button labels highlight when pressed and refresh on active tool, sculpt brush, menu page and custom controller-profile changes. Only the physical buttons on each side are labeled.',
        'All model assets and label textures are loaded lazily once for each controller, stay in the existing XR session renderer, and are cleaned up when VR ends. The synthetic capsule remains as fallback if the bundled models cannot load.',
        'No hand-tracking requirement, extra XR session, model document changes, camera remapping, or fabricated UV/rigging actions; owner Quest 2 visual and tracking testing follows deployment.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+count:]

