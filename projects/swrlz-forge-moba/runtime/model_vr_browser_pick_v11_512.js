/* SE512_QUEST_BROWSER_PICK_START */
// Only the Quest's regular 2D page gets ray-pointer jitter compensation.
// Immersive WebXR uses separate controller rays and is unaffected.
function se512QuestBrowser2D(){
 return typeof navigator!=='undefined'&&/(OculusBrowser|QuestBrowser|MetaQuest)/i.test(navigator.userAgent||'')&&
  !renderer?.xr?.isPresenting;
}
function se512QuestTapPick(event,press){
 if(!se512QuestBrowser2D()||!renderer?.domElement||!modelRoot||!camera||!raycaster||!mouse)return null;
 const rect=renderer.domElement.getBoundingClientRect();
 if(!(rect.width>0&&rect.height>0))return null;
 const meshes=modelRoot.children.filter(o=>o.isMesh&&o.visible&&
  !o.userData?.atelierHelper&&!o.userData?.editorOnly&&partById(o.userData?.atelierId));
 if(!meshes.length)return null;
 // Coordinates come from CSS pixels. No devicePixelRatio multiplication.
 camera.updateMatrixWorld(true);modelRoot.updateWorldMatrix(true);
 const x=Number(event.clientX),y=Number(event.clientY);
 const px=Number.isFinite(press?.x)?press.x:x,py=Number.isFinite(press?.y)?press.y:y;
 const cx=(x+px)*.5,cy=(y+py)*.5;
 const offsets=[[x,y],[px,py],[cx,cy],[cx+8,cy],[cx-8,cy],[cx,cy+8],[cx,cy-8],
  [cx+13,cy],[cx-13,cy],[cx,cy+13],[cx,cy-13]];
 for(const [sx,sy] of offsets){
  if(sx<rect.left||sx>rect.right||sy<rect.top||sy>rect.bottom)continue;
  mouse.set(2*(sx-rect.left)/rect.width-1,1-2*(sy-rect.top)/rect.height);
  raycaster.setFromCamera(mouse,camera);
  const hit=raycaster.intersectObjects(meshes,false).find(h=>partById(h.object?.userData?.atelierId));
  if(hit)return hit.object.userData.atelierId;
 }
 return null;
}
/* SE512_QUEST_BROWSER_PICK_END */
