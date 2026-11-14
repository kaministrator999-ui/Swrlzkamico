"""§E v11.447: smooth per-frame orbit in Face mode, including topology preview.

Fix only camera navigation: face-mode tap-drags used to update the camera
solely on pointerup; Inset previews blocked pointerdown entirely. Native mesh
selection/operations, history, gizmos and two-finger pinch/pan stay unchanged.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_447_SMOOTH_FACE_ORBIT'

def one(s,old,new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.447 anchor',old[:130],count))
    return s.replace(old,new,1)

def apply(html):
    helper="""/* SE447_FACE_CAMERA_ORBIT_START */
// Share the same touch inversion and pitch limits as Model Studio's normal
// one-finger orbit. Run at most one camera update per animation frame.
function se447CameraOrbitApply(gesture,x,y){
 const dx=x-gesture.startX,dy=y-gesture.startY;
 const follow=gesture.pointerType==='touch'&&!se433CameraPrefs.inverted;
 orbit.yaw=gesture.yaw+(follow?dx:-dx)*.008;
 orbit.pitch=THREE.MathUtils.clamp(gesture.pitch+(follow?-dy:dy)*.006,
  -Math.PI/2+.001,Math.PI/2-.001);
 cameraUpdate();
}
function se447CameraOrbitStart(event){
 return {pointerId:event.pointerId,pointerType:event.pointerType,
  startX:event.clientX,startY:event.clientY,
  lastX:event.clientX,lastY:event.clientY,yaw:orbit.yaw,pitch:orbit.pitch,
  moved:false,active:true,raf:0};
}
function se447CameraOrbitQueue(gesture,event){
 if(!gesture?.active)return;
 gesture.lastX=event.clientX;gesture.lastY=event.clientY;
 if(gesture.raf)return;
 gesture.raf=requestAnimationFrame(()=>{
  gesture.raf=0;
  if(gesture.active)se447CameraOrbitApply(gesture,gesture.lastX,gesture.lastY);
 });
}
function se447CameraOrbitStop(gesture,event,applyFinal=true){
 if(!gesture)return;
 if(gesture.raf){cancelAnimationFrame(gesture.raf);gesture.raf=0;}
 gesture.active=false;
 if(applyFinal&&gesture.moved)se447CameraOrbitApply(gesture,event.clientX,event.clientY);
}
/* SE447_FACE_CAMERA_ORBIT_END */
"""
    html=one(html,'function atelierComponentPointerDown(e){',
             helper+'function atelierComponentPointerDown(e){')
    html=one(html,
      'atelierComponentGesture={pointerId:e.pointerId,startX:e.clientX,startY:e.clientY,',
      'atelierComponentGesture={...se447CameraOrbitStart(e),')
    html=one(html,
      "if(d.moved&&atelierComponentTool!=='tap'){",
      "if(d.moved&&atelierComponentTool==='tap')se447CameraOrbitQueue(d,e);\n if(d.moved&&atelierComponentTool!=='tap'){")
    html=one(html,
      """else{orbit.yaw-=(e.clientX-d.startX)*.008;
   orbit.pitch=atelierMeshClamp(orbit.pitch+(e.clientY-d.startY)*.006,-.85,1.1);
   cameraUpdate();}""",
      """else se447CameraOrbitStop(d,e);""")
    # The underlying component tap calls remain authoritative; this only
    # stops pending camera frames when a gesture ends or switches modes.
    html=one(html,
      "atelierComponentGesture=null;\n if(atelierComponentTool==='tap'){",
      "atelierComponentGesture=null;\n if(atelierComponentTool==='tap'){")
    # Once a Preview is active, orbit/pan remain navigational and must never
    # select or mutate topology. No history step is created for camera motion.
    old="""const priorPointer=pointerDown;
 pointerDown=function(event,...args){if(active){if(event?.cancelable)event.preventDefault();publish('Apply or Cancel the topology preview before editing the viewport.');return;}return priorPointer.call(this,event,...args);};"""
    new="""const priorPointer=pointerDown,priorPointerMove=pointerMove,priorPointerUp=pointerUp;
 let se447PreviewOrbit=null;
 pointerDown=function(event,...args){
  if(!active)return priorPointer.call(this,event,...args);
  if(atelierCameraPointerDown(event)){
   if(se447PreviewOrbit){se447CameraOrbitStop(se447PreviewOrbit,event,false);se447PreviewOrbit=null;}
   return;
  }
  if(event?.button===0){
   if(se447PreviewOrbit)se447CameraOrbitStop(se447PreviewOrbit,event,false);
   se447PreviewOrbit=se447CameraOrbitStart(event);
   renderer?.domElement?.setPointerCapture?.(event.pointerId);
  }
  if(event?.cancelable)event.preventDefault();
 };
 pointerMove=function(event,...args){
  if(!active&&!se447PreviewOrbit)return priorPointerMove.call(this,event,...args);
  if(atelierCameraPointerMove(event))return;
  const g=se447PreviewOrbit;
  if(g?.pointerId===event.pointerId){
   if(Math.hypot(event.clientX-g.startX,event.clientY-g.startY)>5)g.moved=true;
   if(g.moved)se447CameraOrbitQueue(g,event);
  }
  if(event?.cancelable)event.preventDefault();
 };
 pointerUp=function(event,...args){
  if(!active&&!se447PreviewOrbit)return priorPointerUp.call(this,event,...args);
  const consumed=atelierCameraPointerUp(event),g=se447PreviewOrbit;
  if(g?.pointerId===event.pointerId){
   se447CameraOrbitStop(g,event,!consumed);se447PreviewOrbit=null;
  }
  if(event?.cancelable)event.preventDefault();
 };"""
    html=one(html,old,new)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_446_PLANAR_FACE_PICK',MARKER),
      ('ENGINE · MAKER v11.446','ENGINE · MAKER v11.447'),
      ('v11.446 · whole flat face selection','v11.447 · smooth face and preview camera orbit'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.446'","window.SWRLZ_FORGE_BUILD={version:'v11.447'"),
      ('<title>§wyrl§ Engine · Maker v11.446</title>','<title>§wyrl§ Engine · Maker v11.447</title>')
    ]:html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.446';source.version=11.446;"
    assert html.count(old)==5,('v11.447 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.447';source.version=11.447;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[entry for entry in notes.get('history',[]) if entry.get('version')!='v11.446']
    notes['history'].insert(0,{'version':'v11.446','changes':notes.get('changes',[])})
    notes.update(version='v11.447',date='2026-11-14',
      title='Smooth camera orbit with Inset selected or previewed',
      changes=[
      'Face mode now updates camera yaw and pitch while a drag moves, throttled to one camera update per animation frame instead of rotating only on pointer release.',
      'Camera orbit while previewing Inset, Extrude and other topology operations works again without selecting geometry, changing the pending mesh or committing Undo.',
      'The live camera rotation follows the existing saved Invert touch orbit preference; desktop direction and near-pole limits remain unchanged.',
      'Two-finger pinch/pan, component selection on a tap, gizmo dragging, preview Apply/Cancel and native model history retain their existing owners.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
