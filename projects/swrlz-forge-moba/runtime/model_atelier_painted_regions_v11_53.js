// §E v11.53 — optional brush-painted lasso selection masks.
// These strokes alter only a named region's inclusion test. The native source
// polygon, its 📌 pins, UVs and mesh topology remain unchanged and undoable.
const atelierPaintMaxDabs=64;
function atelierPaintDabsValid(dabs){
 return dabs===undefined||(
  Array.isArray(dabs)&&dabs.length<=atelierPaintMaxDabs&&dabs.every(d=>
   d&&typeof d==='object'&&!Array.isArray(d)&&
   Object.keys(d).sort().join('|')==='axis|center|op|radius'&&
   ['add','subtract'].includes(d.op)&&Number.isFinite(d.radius)&&
   d.radius>=.03&&d.radius<=.6&&
   [d.center,d.axis].every(a=>Array.isArray(a)&&a.length===3&&
     a.every(v=>Number.isFinite(v)&&Math.abs(v)<=4))&&
   Math.abs(Math.hypot(...d.axis)-1)<.02
  )
 );
}
function atelierPaintMaskContains(point,base,dabs=[]){
 let inside=!!base;
 for(const dab of dabs){
  const a=dab.axis;
  const dx=point[0]-dab.center[0],dy=point[1]-dab.center[1],dz=point[2]-dab.center[2];
  const along=dx*a[0]+dy*a[1]+dz*a[2];
  const lateral=Math.hypot(dx-along*a[0],dy-along*a[1],dz-along*a[2]);
  // Restrict painted footprint to the local tangent shell. A nearby
  // opposite wall must not be painted merely because it is inside a ball.
  if(lateral<=dab.radius&&Math.abs(along)<=Math.max(.008,dab.radius*.3))
   inside=dab.op==='add';
 }
 return inside;
}
function atelierPaintMaskEdgeDistance(point,dabs){
 let closest=Infinity;
 for(const d of dabs){
  const dx=point[0]-d.center[0],dy=point[1]-d.center[1],dz=point[2]-d.center[2];
  const z=dx*d.axis[0]+dy*d.axis[1]+dz*d.axis[2];
  if(Math.abs(z)>Math.max(.008,d.radius*.3))continue;
  const r=Math.hypot(dx-z*d.axis[0],dy-z*d.axis[1],dz-z*d.axis[2]);
  closest=Math.min(closest,Math.abs(d.radius-r));
 }
 return closest;
}
function atelierPaintCandidate(region,dab){
 if(!region||!atelierPaintDabsValid([dab]))return {ok:false,reason:'Invalid paint dab'};
 const list=[...(region.paintDabs||[]),dab];
 if(!atelierPaintDabsValid(list))return {ok:false,reason:'Maximum 64 bounded dabs per lasso'};
 return {ok:true,dabs:list};
}
function atelierPaintNativeCommit(part,region,dabs){
 const next={...region,paintDabs:dabs};
 const regions=part.sculptLassos.map(r=>r.id===region.id?next:r);
 if(!atelierLassoValid({...part,sculptLassos:regions})||
    !checkPart({...part,sculptLassos:regions}))return false;
 checkpoint();
 part.sculptLassos=regions;
 const id=part.id,regionId=region.id;
 signalEdited();select(id);atelierLassoActive=regionId;atelierLassoRefresh();
 return true;
}
let atelierPaintArmed=false,atelierPaintDrag=null;
function atelierPaintDabFromPin(pin,region,radius,op){
 if(!pin||!region||!Number.isFinite(radius)||radius<.03||radius>.6)return null;
 return {center:pin.point.slice(),axis:region.axis.slice(),radius,op};
}
function atelierPaintStart(e){
 if(!atelierPaintArmed)return false;
 const part=atelierLassoPart(),region=atelierLassoRegion();
 const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
 if(!part||!region||!mesh){status('Create and select a lasso region first.',true);return true;}
 const pin=atelierLassoPointFromEvent(e,mesh);
 if(!pin){status('Start the paint stroke on the selected mesh surface.',true);return true;}
 const radius=Number($m('LassoPaintRadius').value),op=$m('LassoPaintMode').value;
 const first=atelierPaintDabFromPin(pin,region,radius,op);
 if(!first||!atelierPaintDabsValid([first])){status('Paint radius must be .03 to .60.',true);return true;}
 atelierPaintDrag={id:e.pointerId,mesh,regionId:region.id,lastX:e.clientX,lastY:e.clientY,dabs:[first]};
 renderer.domElement.setPointerCapture?.(e.pointerId);
 pressed=null;return true;
}
function atelierPaintMove(e){
 const t=atelierPaintDrag;
 if(!t||t.id!==e.pointerId)return false;
 if(Math.hypot(e.clientX-t.lastX,e.clientY-t.lastY)<8)return true;
 t.lastX=e.clientX;t.lastY=e.clientY;
 const region=atelierLassoRegion(),pin=atelierLassoPointFromEvent(e,t.mesh);
 if(!region||region.id!==t.regionId||!pin)return true;
 const dab=atelierPaintDabFromPin(pin,region,Number($m('LassoPaintRadius').value),
  $m('LassoPaintMode').value);
 if(dab&&atelierPaintDabsValid([dab])&&t.dabs.length<atelierPaintMaxDabs){
  const prev=t.dabs[t.dabs.length-1],delta=dab.center.map((v,i)=>v-prev.center[i]);
  if(Math.hypot(...delta)>=Math.min(.03,dab.radius*.35))t.dabs.push(dab);
 }
 return true;
}
function atelierPaintFinish(e,cancel=false){
 const t=atelierPaintDrag;if(!t||t.id!==e.pointerId)return false;
 atelierPaintDrag=null;atelierPaintArmed=false;
 if(cancel){status('Paint gesture cancelled; region unchanged.');atelierLassoRefresh();return true;}
 const part=atelierLassoPart(),region=atelierLassoRegion();
 if(!part||!region||region.id!==t.regionId)return true;
 const dabs=[...(region.paintDabs||[]),...t.dabs];
 if(!atelierPaintDabsValid(dabs)||!atelierPaintNativeCommit(part,region,dabs)){
  status('Paint region limit/schema rejected. Source region unchanged.',true);return true;
 }
 status('Painted '+t.dabs.length+' surface dabs in one native Undo transaction.');
 return true;
}
function atelierPaintInstall(){
 const get=id=>$m('LassoPaint'+id);
 get('Arm').addEventListener('click',()=>{
  if(!atelierLassoRegion()){status('Create a named lasso before painting.',true);return;}
  atelierPaintArmed=!atelierPaintArmed;
  atelierLassoArm=null;atelierLassoPending=[];atelierLassoRefresh();
 });
 get('AtXYZ').addEventListener('click',()=>{
  const part=atelierLassoPart(),region=atelierLassoRegion();
  const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
  if(!part||!region||!mesh)return;
  const xyz=[0,1,2].map(i=>Number(get('XYZ'+i).value));
  const pin=atelierLassoProjectXYZ(mesh,xyz);
  const dab=atelierPaintDabFromPin(pin,region,Number(get('Radius').value),get('Mode').value);
  const candidate=atelierPaintCandidate(region,dab);
  if(!candidate.ok||!atelierPaintNativeCommit(part,region,candidate.dabs)){
   status('Paint point must attach to surface and remain within 64 bounded dabs.',true);return;
  }
  status('Added one localized '+dab.op+' selection dab; source geometry unchanged.');
 });
 get('Clear').addEventListener('click',()=>{
  const p=atelierLassoPart(),reg=atelierLassoRegion();
  if(!p||!reg?.paintDabs?.length)return;
  if(atelierPaintNativeCommit(p,reg,[]))status('Cleared paint mask with one Undo checkpoint.');
 });
}
