"""§E v11.450: preserve camera on dock resize; make Inset previews visible/actionable.

Only native workshop geometry is previewed. A tool can be armed until the
user taps a face; camera-only layout changes never frame/rebuild the model.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_450_CAMERA_INSET_PREVIEW'
def one(html,old,new):
 n=html.count(old)
 if n!=1:raise AssertionError(('v11.450 anchor',old[:150],n))
 return html.replace(old,new,1)

def apply(html):
 # Model dock changes already resize the canvas with a native ResizeObserver
 # on the viewport stage. The synthetic global window-resize event dispatched
 # on every pointermove wakes unrelated layout/zoom listeners, and can reset
 # the user's carefully positioned inspection camera.
 source='function dragResize(node,what,side,dir){'
 end='function addSeparator(parent,what,side,dir){'
 a=html.index(source);b=html.index(end,a)
 segment=html[a:b]
 marker="window.dispatchEvent(new Event('resize'))"
 assert segment.count(marker)==3,('native dock resize event count',segment.count(marker))
 segment=segment.replace(marker,"se450NotifyDockResized(what)")
 helper="""/* SE450_MODEL_DOCK_RESIZE_START */
function se450NotifyDockResized(what){
 if(what==='model'){
  // Model Atelier already observes its viewport with ResizeObserver.
  // A dock resize is not a global browser resize or a camera Frame command.
  return;
 }
 window.dispatchEvent(new Event('resize'));
}
/* SE450_MODEL_DOCK_RESIZE_END */
"""
 html=html[:a]+helper+segment+html[b:]
 # A real viewport resize is allowed to change its aspect and projection, not
 # target, pan, azimuth, elevation or distance. The camera module owns this.
 html=one(html,
 """ const previousResize=resize;
 resize=function(){const result=previousResize.apply(this,arguments);refresh();return result;};""",
 """/* SE450_CAMERA_RESIZE_GUARD_START */
 const previousResize=resize;
 resize=function(){
  const before=orbit&&camera?{
   yaw:orbit.yaw,pitch:orbit.pitch,distance:orbit.distance,
   pan:atelierCameraPan.clone(),detail:atelierDetailTarget?.clone?.()||null
  }:null;
  const result=previousResize.apply(this,arguments);
  if(before&&camera&&(orbit.yaw!==before.yaw||orbit.pitch!==before.pitch||orbit.distance!==before.distance||
     !atelierCameraPan.equals(before.pan)||
     (before.detail&&(!atelierDetailTarget||!atelierDetailTarget.equals(before.detail))))){
   orbit.yaw=before.yaw;orbit.pitch=before.pitch;orbit.distance=before.distance;
   atelierCameraPan.copy(before.pan);atelierDetailTarget=before.detail;
   cameraUpdate();
  }
  refresh();return result;
 };
/* SE450_CAMERA_RESIZE_GUARD_END */""")
 # Visible preview edges live only on the native mesh and are disposed on
 # Cancel, Apply or regeneration. No extra mesh is serialized or selectable.
 outline=(ROOT/'runtime/model_face_preview_visibility_v11_450.js').read_text(encoding='utf8')
 html=one(html,'/* SE430_MODEL_WORKSHOP_BRIDGE_START */',outline+'\n/* SE430_MODEL_WORKSHOP_BRIDGE_START */')
 html=one(html,
  " function restore(record){\n  // Restore only the exact geometry still owned by this preview.",
  " function restore(record){\n  se450PreviewOutlineClear(record);\n  // Restore only the exact geometry still owned by this preview.")
 html=one(html,
  "record.operation=operation;record.data=data;record.stats=",
  "se450PreviewOutlineClear(record);\n  record.operation=operation;record.data=data;record.stats=")
 html=one(html,
  "record.geometry=geometry;mesh.geometry=geometry;active=record;",
  "record.geometry=geometry;mesh.geometry=geometry;active=record;\n  se450PreviewOutlineAdd(record);")
 # Arm tool while waiting for an intentional tap; the tap first calls the
 # existing planar region selector and then Preview. Never Apply implicitly.
 armed=(ROOT/'runtime/model_armed_face_preview_v11_450.js').read_text(encoding='utf8')
 html=one(html,'/* SE448_INSET_ACTION_ROUTING_START */',armed+'\n/* SE448_INSET_ACTION_ROUTING_START */')
 html=one(html,
  " const result=se430ModelWorkshop.selectRegion(hitId,selection);",
  " const result=se450AfterPlanarFaceTap(se430ModelWorkshop.selectRegion(hitId,selection),hitId,selection);")
 html=one(html,
 """  if(first.selection.mode!=='face'){
  api.setComponentMode('face');
  say('Face mode selected. Tap a face on the mesh, then choose '+operation+' again to preview.');""",
 """  if(first.selection.mode!=='face'){
  api.setComponentMode('face');
  se450ArmFacePreview(operation,partId);
  say(operation.charAt(0).toUpperCase()+operation.slice(1)+' ready. Tap a square face to display the preview.');""")
 html=one(html,
 """  if(seed===null){
  say('Tap a square face first, then choose '+operation+' again to preview.');""",
 """  if(seed===null){
  se450ArmFacePreview(operation,partId);
  say(operation.charAt(0).toUpperCase()+operation.slice(1)+' ready. Tap a square face to display the preview.');""")
 html=one(html,
  """ let state=api.inspect();
 if(state.convert?.available){""",
  """ let state=api.inspect();
 if(seed!==null&&state.selection.partId===partId&&state.selection.mode==='face'&&
    !state.selection.faceIds?.length&&!state.convert?.available){
  const recovered=api.selectRegion(seed,partId);
  if(recovered?.ok)state=api.inspect();
 }
 if(state.convert?.available){""")
 # UI instructions follow the new actual tool semantics; old static
 # 'tap face and choose Inset again' is no longer accurate.
 html=one(html,
 "Select a face and tap Inset or Extrude to preview. Editable cubes with vertex edits can be safely baked with confirmation.",
 "Choose Inset or Extrude, then tap a square face to preview. Apply commits; Cancel discards. Edited cubes may ask to bake first.")
 for before,after in [
  ('SWYRL_ENGINE_DEPLOY_MARKER: V11_449_MODEL_TOUCH_LAYOUT',MARKER),
  ('ENGINE · MAKER v11.449','ENGINE · MAKER v11.450'),
  ('v11.449 · repaired model layout, grips and multitouch','v11.450 · stable dock zoom and visible Inset preview'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.449'","window.SWRLZ_FORGE_BUILD={version:'v11.450'"),
  ('<title>§wyrl§ Engine · Maker v11.449</title>','<title>§wyrl§ Engine · Maker v11.450</title>')
 ]:html=one(html,before,after)
 previous=" source.engine='§wyrl§ Engine · Maker v11.449';source.version=11.449;"
 assert html.count(previous)==5,('v11.450 provenance',html.count(previous))
 html=html.replace(previous," source.engine='§wyrl§ Engine · Maker v11.450';source.version=11.450;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[r for r in notes.get('history',[]) if r.get('version')!='v11.449']
 notes['history'].insert(0,{'version':'v11.449','changes':notes.get('changes',[])})
 notes.update(version='v11.450',date='2026-11-14',
  title='Preserve camera on dock resize, show Inset preview',
  changes=[
   'Model sidebar drag no longer fires synthetic global browser resize events per pointermove; the existing native stage ResizeObserver updates projection without framing the model or changing the inspection orbit.',
   'The model camera resize handler explicitly preserves yaw, pitch, distance, pan and frame target even if another resize implementation modifies them.',
   'Inset/Extrude Shape shortcuts arm Face mode when no valid face is selected: tapping a complete planar region builds the native geometry preview without requiring the tool to be pressed again. Choosing Inset with a valid selection still previews immediately.',
   'A successful native topology preview now displays a transient mint-colored edge outline, with clean disposal on Apply, Cancel and regeneration. No preview visuals are serialized and no new geometry transaction is created by navigation.',
   'Conversions on compatible primitives/vertex edits continue through existing validated native checks and explicit confirmation; invalid or protected assets remain guarded. Apply remains the only way to commit a preview.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
