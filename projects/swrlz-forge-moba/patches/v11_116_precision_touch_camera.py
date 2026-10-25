"""§E v11.116 — precision touch ownership, camera recovery and safe framing.

Forward-only modifications to the assembled v11.115 engine. Historical source
patches remain untouched; temporary preview and camera state never checkpoint.
"""
from pathlib import Path
import hashlib
import json

def once(s, old, new):
    n=s.count(old)
    assert n==1, (old[:110], n)
    return s.replace(old,new,1)

def apply(html):
    # Normal outside-camera navigation is unchanged unless a precision handle
    # is active. Never allow a precision editor zoom to put the camera through
    # the selected object's surface; interior inspection remains opt-in.
    html=once(html,
        "const atelierCameraMinDistance=()=>atelierCameraInterior?.08:.16;",
        """const atelierCameraMinDistance=()=>{
 const baseline=.16;
 if(atelierCameraInterior)return .08;
 if(!atelierPrecisionGizmoEnabled('Radius')&&
    !atelierPrecisionGizmoEnabled('Depth')&&
    !atelierPrecisionGuardActive())return baseline;
 const mesh=modelRoot?.children.find(o=>o.isMesh&&
   o.userData.atelierId===selection);
 if(!mesh?.geometry)return baseline;
 mesh.geometry.computeBoundingSphere();
 mesh.updateMatrixWorld(true);
 const r=mesh.geometry.boundingSphere?.radius*
   mesh.matrixWorld.getMaxScaleOnAxis();
 return Number.isFinite(r)&&r>0?
   Math.max(baseline,Math.min(24,r*2.55)):baseline;
};""")
    # v11.76 deliberately permits extremely close desktop zoom. In precision
    # editing, wheel and plus-button zoom must respect the same safe boundary
    # as a two-finger pinch, or the surface still slices through the camera.
    html=once(html,
        "Math.max(.16,orbit.distance+Math.sign(e.deltaY)*Math.max(.045,orbit.distance*.085))",
        "Math.max(atelierCameraMinDistance(),orbit.distance+Math.sign(e.deltaY)*Math.max(.045,orbit.distance*.085))")
    html=once(html,
        "Math.max(.16,orbit.distance-Math.max(.045,orbit.distance*.12))",
        "Math.max(atelierCameraMinDistance(),orbit.distance-Math.max(.045,orbit.distance*.12))")
    # When a second finger arrives during radius/depth editing, roll back that
    # uncommitted drag and HAND BOTH pointers to native camera pinch/pan. This
    # prevents a hidden first touch from turning into a phantom camera finger.
    html=once(html,
        " if(e.button!==0)return false;\n atelierCameraTouches.set(e.pointerId,{x:e.clientX,y:e.clientY});",
        """ if(e.button!==0)return false;
 if(atelierPrecisionGizmoDrag&&
    e.pointerId!==atelierPrecisionGizmoDrag.id){
  const d=atelierPrecisionGizmoDrag;
  const field=document.getElementById('modelAtelierBore'+d.mode);
  if(field)field.value=d.startValue.toFixed(4);
  atelierPrecisionGizmoDrag=null;
  try{renderer.domElement.releasePointerCapture?.(d.id)}catch(_){}
  if(d.changed)document.getElementById('modelAtelierBorePreview')?.click();
  atelierPrecisionGizmoQueue();
  atelierCameraTouches.set(d.id,
   {x:d.lastX??d.startX,y:d.lastY??d.startY});
  atelierCameraConsumedTouches.add(d.id);
  pressed=null;
 }
 atelierCameraTouches.set(e.pointerId,{x:e.clientX,y:e.clientY});""")
    # A finger remaining after pinch must be able to orbit naturally, rather
    # than being swallowed forever by the multi-touch "consumed" set.
    html=once(html,
        " atelierCameraGesture=atelierCameraTouches.size>=2?atelierCameraTouchMetrics():null;\n if(!atelierCameraTouches.size)atelierCameraConsumedTouches.clear();",
        """ atelierCameraGesture=atelierCameraTouches.size>=2?atelierCameraTouchMetrics():null;
 if(atelierCameraTouches.size===1){
  const [id,pt]=atelierCameraTouches.entries().next().value;
  if(atelierCameraConsumedTouches.has(id)){
   atelierCameraConsumedTouches.delete(id);
   pressed={x:pt.x,y:pt.y,yaw:orbit.yaw,pitch:orbit.pitch,moved:true};
  }
 }
 if(!atelierCameraTouches.size)atelierCameraConsumedTouches.clear();""")
    # The v11.115 preview tap stops propagation before the canvas pointerup;
    # without explicit cleanup, the camera retains a phantom finger.
    html=once(html,
        """ status('Selected the original editable sphere. The hole was a temporary preview; switch to Sculpt → Precision circle cut, preview again, and Apply to save it.');
 event.preventDefault?.();""",
        """ status('Selected the original editable sphere. The hole was a temporary preview; switch to Sculpt → Precision circle cut, preview again, and Apply to save it.');
 atelierCameraPointerUp(event);
 pressed=null;
 event.preventDefault?.();""")
    # Mobile ring picking previously swallowed broad areas of the orbit surface
    # (36 px halo around every ring point). Keep an accessible grip, but narrow
    # the ring itself so swiping nearby orbits as expected.
    html=once(html,
        " const threshold=event.pointerType==='touch'?36:24;",
        """ const threshold=event.pointerType==='touch'?18:12;
 const gripThreshold=event.pointerType==='touch'?32:20;
 const radiusGripPt=atelierPrecisionGizmoScreen(pick.radiusGrip);""")
    html=once(html,
        " let radiusCandidate=null;\n if(atelierPrecisionGizmoEnabled('Radius')){",
        """ let radiusCandidate=null;
 if(atelierPrecisionGizmoEnabled('Radius')&&
     distance(radiusGripPt)<=gripThreshold)
  radiusCandidate={mode:'Radius',point:radiusGripPt,d:distance(radiusGripPt)};
 if(atelierPrecisionGizmoEnabled('Radius')){""")
    html=once(html,
        "    distance(depthPoint)<=threshold?{mode:'Depth',point:depthPoint,d:distance(depthPoint)}:null;",
        "    distance(depthPoint)<=gripThreshold?{mode:'Depth',point:depthPoint,d:distance(depthPoint)}:null;")
    # Completely stop native one-finger orbit for the pointer that actually
    # grabbed the precision handle. No checkpoint or mesh movement on drag.
    html=once(html,
        "   partId:pick.ctx.part.id,changed:false};\n try{renderer.domElement.setPointerCapture?.(event.pointerId)}",
        """   partId:pick.ctx.part.id,changed:false,
   lastX:event.clientX,lastY:event.clientY};
 pressed=null;
 try{renderer.domElement.setPointerCapture?.(event.pointerId)}""")
    html=once(html,
        " const dx=event.clientX-drag.startX,dy=event.clientY-drag.startY;",
        """ drag.lastX=event.clientX;drag.lastY=event.clientY;
 const dx=event.clientX-drag.startX,dy=event.clientY-drag.startY;""")
    # Native XYZ move gizmo and precision radius handles should never visually
    # occupy the same sphere. Hide mesh arrows while precision tools/preview
    # own the viewport; restore their original implementation afterward.
    html=once(html,
        "function atelierMeshGizmoBuild(){\n atelierMeshGizmoClear();",
        """function atelierMeshGizmoBuild(){
 atelierMeshGizmoClear();
 if((atelierPrecisionGizmoEnabled('Radius')||
    atelierPrecisionGizmoEnabled('Depth')||
    atelierPrecisionGuardActive())&&partById(selection))return;""")
    html=once(html,
        "    atelierPrecisionGizmoQueue();\n   });\n  }\n  const schedule=()=>atelierPrecisionGizmoQueue();",
        """    // Changing precision mode also changes ownership of the XYZ arrows.
    atelierMeshGizmoBuild();
    orbit.distance=Math.max(orbit.distance,atelierCameraMinDistance());
    cameraUpdate();
    atelierPrecisionGizmoQueue();
   });
  }
  const schedule=()=>atelierPrecisionGizmoQueue();""")
    # A lost pointer (Android browser cancellation) rolls dimensions back and
    # rebuilds the old candidate, never committing a half-drag.
    html=once(html,
        """ atelierPrecisionGizmoDrag=null;
 try{renderer?.domElement?.releasePointerCapture?.(drag.id)}catch(_){}
 if(drag.changed){
   // Rebuild full validated candidate ONCE after touch release.""",
        """ atelierPrecisionGizmoDrag=null;
 try{renderer?.domElement?.releasePointerCapture?.(drag.id)}catch(_){}
 if(event?.type==='pointercancel'&&drag.changed){
  const field=document.getElementById('modelAtelierBore'+drag.mode);
  if(field)field.value=drag.startValue.toFixed(4);
 }
 if(drag.changed){
   // Rebuild full validated candidate ONCE after touch release.""")
    html=once(html,
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_115_SAFE_PRECISION_PREVIEW_SELECTION',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_116_PRECISION_TOUCH_CAMERA_REPAIR')
    for old,new in [
        ('ENGINE · MAKER v11.115','ENGINE · MAKER v11.116'),
        ('v11.115 · safe precision preview selection','v11.116 · stable precision touch and camera'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.115'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.116'"),
        ('<title>§wyrl§ Engine · Maker v11.115</title>',
         '<title>§wyrl§ Engine · Maker v11.116</title>'),
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(
      title='Stable finger gestures and precision radius/depth controls',
      date='2026-10-24',
      changes=[
        'Fix phantom camera fingers after tapping a temporary hole preview.',
        'Enable smooth orbit with the remaining finger after a two-finger pinch/pan.',
        'Cancel uncommitted radius/depth drag safely when a second finger starts camera navigation.',
        'Keep the exterior camera outside the selected precision mesh so accidental pinch zoom does not clip the sphere into giant white facets.',
        'Use a tighter colored ring hit area, retain a large grip target and hide conflicting native XYZ arrows during precision editing.',
        'Preserve editable native meshes, explicit Apply/Undo, independently positioned circular holes, existing scenes, all 68 assets and historical patches.'
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    raw=html.encode('utf8')
    print('SWRLZ_V11116_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
