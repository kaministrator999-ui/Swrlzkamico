"""§E browser two-pointer camera release guard, applied to assembled HTML."""
import re

def replace_once(html, pattern, replacement):
    updated,n=re.subn(pattern,lambda _:replacement,html,count=1,flags=re.MULTILINE)
    assert n==1,(pattern[:90],n)
    return updated

def apply(html):
    # Never re-arm orbit for the pointer remaining after pinch.
    html=replace_once(html,
      r"if\s*\(atelierCameraTouches\.size===1\)\s*\{\s*const\s*\[id,pt\]=atelierCameraTouches\.entries\(\)\.next\(\)\.value;\s*if\s*\(atelierCameraConsumedTouches\.has\(id\)\)\s*\{\s*atelierCameraConsumedTouches\.delete\(id\);\s*pressed=\{x:pt\.x,y:pt\.y,yaw:orbit\.yaw,pitch:orbit\.pitch,moved:true\};\s*\}\s*\}",
      "// Keep the remaining pointer consumed until its own release.\n  if(atelierCameraTouches.size===1)pressed=null;")
    html=replace_once(html,
      r"function atelierCameraPointerCancel\(e\)\s*\{\s*atelierCameraPointerUp\(e\);\s*pressed=null;\s*\}",
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
