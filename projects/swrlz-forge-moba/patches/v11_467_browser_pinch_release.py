"""§E browser-mode two-pointer camera release guard (candidate, not released)."""
def one(s, old, new):
    n=s.count(old)
    assert n==1,(old[:100],n)
    return s.replace(old,new,1)

def apply(html):
    # A completed pinch must not become a fresh one-controller orbit.
    html=one(html,
      """  if(atelierCameraTouches.size===1){
   const [id,pt]=atelierCameraTouches.entries().next().value;
   if(atelierCameraConsumedTouches.has(id)){
    atelierCameraConsumedTouches.delete(id);
    pressed={x:pt.x,y:pt.y,yaw:orbit.yaw,pitch:orbit.pitch,moved:true};
   }
  }""",
      """  // Keep remaining pointers consumed until their own release.
  // Never synthesize a new pressed/orbit gesture from a finished pinch.
  if(atelierCameraTouches.size===1)pressed=null;""")
    # Cancel must not call the ordinary release transition and accidentally
    # re-arm another pointer; clear camera ownership for the interrupted gesture.
    html=one(html,
      """function atelierCameraPointerCancel(e){
 atelierCameraPointerUp(e);
 pressed=null;
}""",
      """function atelierCameraPointerCancel(e){
 const tracked=atelierCameraTouches.has(e.pointerId);
 atelierCameraTouches.delete(e.pointerId);
 atelierCameraConsumedTouches.delete(e.pointerId);
 if(tracked){
  for(const id of atelierCameraTouches.keys())atelierCameraConsumedTouches.add(id);
  atelierCameraGesture=null;
 }
 if(atelierCameraMousePan?.id===e.pointerId)atelierCameraMousePan=null;
 pressed=null;
}""")
    return html
