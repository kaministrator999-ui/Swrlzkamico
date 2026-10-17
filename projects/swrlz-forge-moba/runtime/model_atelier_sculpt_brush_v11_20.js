// V11_20_LOCAL_VERTEX_SPHERE_BRUSH
// Opt-in, native-project-backed geometric sculpting; never imports OBJ files.
// A picked center/normal drives a finite-radius vertex group. Each stroke is
// recorded in its part and deterministically replayed after procedural rebuild.
const atelierSculptMaxStrokes=32;
const atelierSculptModes=['smooth','soft'];
const atelierSculptMaxVertexEdits=64;
function atelierSculptVertexValid(p){
 const edits=p.sculptVertexEdits;
 if(edits===undefined)return true;
 if(!Array.isArray(edits)||edits.length>atelierSculptMaxVertexEdits)return false;
 return edits.every(e=>e&&typeof e==='object'&&!Array.isArray(e)
   &&Object.keys(e).sort().join('|')==='delta|indices|resolution'
   &&Array.isArray(e.indices)&&e.indices.length>0&&e.indices.length<=256
   &&new Set(e.indices).size===e.indices.length
   &&e.indices.every(i=>Number.isInteger(i)&&i>=0&&i<=300000)
   &&Array.isArray(e.delta)&&e.delta.length===3&&e.delta.every(v=>Number.isFinite(v)&&Math.abs(v)<=.5)
   &&Array.isArray(e.resolution)&&e.resolution.length===2
   &&e.resolution.every(v=>Number.isInteger(v)&&v>=0&&v<=512));
}
function atelierSculptResolution(p){
 const d=p.meshDensity;return d?[d.u,d.v]:[0,0];
}

const atelierSculptClamp=(v,low,high)=>Math.min(high,Math.max(low,v));
function atelierSculptValid(p){
 const strokes=p.sculptBrushes;
 if(!atelierSculptVertexValid(p))return false;
 if(strokes===undefined)return true;
 if(!Array.isArray(strokes)||strokes.length>atelierSculptMaxStrokes)return false;
 return strokes.every(s=>{
   if(!s||typeof s!=='object'||Array.isArray(s)
     ||Object.keys(s).sort().join('|')!=='axis|center|falloff|half|pitch|plateau|radius|snap|strength|taper|yaw|level')return false;
   const vec=v=>Array.isArray(v)&&v.length===3&&v.every(x=>Number.isFinite(x)&&Math.abs(x)<=4);
   if(!vec(s.center)||!vec(s.axis))return false;
   const n=Math.hypot(...s.axis);
   return n>.99&&n<1.01
      &&Number.isFinite(s.radius)&&s.radius>=.03&&s.radius<=2.5
      &&Number.isFinite(s.strength)&&Math.abs(s.strength)<=.5
      &&typeof s.half==='boolean'
      &&atelierSculptModes.includes(s.falloff)
      &&Number.isFinite(s.yaw)&&Math.abs(s.yaw)<=Math.PI
      &&Number.isFinite(s.pitch)&&Math.abs(s.pitch)<=Math.PI
      &&Number.isFinite(s.snap)&&s.snap>=0&&s.snap<=.1
      &&Number.isFinite(s.plateau)&&s.plateau>=0&&s.plateau<=1
      &&Number.isFinite(s.taper)&&s.taper>=0&&s.taper<=1
      &&typeof s.level==='boolean';
 });
}
function atelierSculptFalloff(normalizedDistance,mode,plateau=0,taper=.5){
 if(normalizedDistance<=plateau)return 1;
 if(normalizedDistance>=1)return 0;
 const x=(normalizedDistance-plateau)/(1-plateau);
 const expo=.55+4.8*taper; // smaller -> broad fade, larger -> concentrated edge drop
 if(mode==='soft'){
   const k=1.5+6*taper;
   const g=(Math.exp(-k*x*x)-Math.exp(-k))/(1-Math.exp(-k));
   return Math.pow(Math.max(0,g),.55+2*taper);
 }
 return Math.pow(1-x*x,expo);
}
function atelierSculptApply(geometry,part){
 if(!geometry?.attributes?.position||!part?.sculptBrushes?.length)return geometry;
 const a=geometry.attributes.position;
 // Position samples in a UV sphere are duplicated at the seam. Use the SAME
 // position-dependent influence for identical vertices so the seam stays shut.
 for(const s of part.sculptBrushes){
   if(!atelierSculptValid({sculptBrushes:[s]}))continue;
   const origin=new THREE.Vector3(...s.center);
   const axis=new THREE.Vector3(...s.axis).applyEuler(new THREE.Euler(s.pitch,s.yaw,0,'YXZ')).normalize();
   const delta=new THREE.Vector3(),move=new THREE.Vector3(),r=s.radius;
   for(let i=0;i<a.count;i++){
     const x=a.getX(i),y=a.getY(i),z=a.getZ(i);
     delta.set(x-origin.x,y-origin.y,z-origin.z);
     const distance=delta.length();
     if(distance>=r)continue;
     let weight=atelierSculptFalloff(distance/r,s.falloff,s.plateau,s.taper);
     // Rotatable HALF-sphere restricts the influenced group to the chosen
     // side of the brush. Fade through the plane instead of a hard seam.
     if(s.half)weight*=THREE.MathUtils.smoothstep(delta.dot(axis),0,r*.22);
     // Preserve topology/relief or level affected vertices toward one
     // shared brush-aligned plane at center + signed desired depth.
     const signed=delta.dot(axis);
     let amount=weight*(s.level?s.strength-signed:s.strength);
     if(s.snap>0)amount=Math.round(amount/s.snap)*s.snap; // snap the MOVE, not base mesh
     move.copy(axis).multiplyScalar(amount);
     a.setXYZ(i,x+move.x,y+move.y,z+move.z);
   }
 }
 // Explicit index edits are stored in native project data, not transient GPU
 // buffers. They are resolution-bound: changing sampling never silently
 // reassigns an edit to an unrelated face vertex.
 for(const edit of part.sculptVertexEdits||[]){
   const res=atelierSculptResolution(part);
   if(edit.resolution[0]!==res[0]||edit.resolution[1]!==res[1])continue;
   for(const i of edit.indices){
     if(i>=a.count)continue;
     a.setXYZ(i,a.getX(i)+edit.delta[0],a.getY(i)+edit.delta[1],a.getZ(i)+edit.delta[2]);
   }
 }
 a.needsUpdate=true;
 geometry.computeVertexNormals();
 geometry.computeBoundingSphere();
 geometry.computeBoundingBox();
 return geometry;
}
let atelierSculptArmed=false,atelierSculptHit=null;
function atelierSculptRefresh(){
 const p=partById(selection),deck=$m('SculptBrush');
 if(!deck)return;
 deck.hidden=!p;
 if(atelierSculptHit?.partId!==selection)atelierSculptHit=null;
 if(!p)atelierSculptArmed=false;
 const hint=$m('SculptBrushInfo');
 if(hint)hint.textContent=(atelierSculptHit?'Picked surface on '+p.name+'. ':'')
   +(p?.sculptBrushes?.length||0)+' saved strokes. '
   +(atelierSculptArmed?'Tap the mesh to select the brush center.':'Orbit freely; arm to pick a point.');
 const arm=$m('SculptBrushPick');
 if(arm)arm.textContent=atelierSculptArmed?'Cancel picking':'Pick center on mesh';
 const remove=$m('SculptBrushUndoStroke');
 if(remove)remove.disabled=!(p?.sculptBrushes?.length);
}
function atelierSculptPick(hit){
 if(!atelierSculptArmed)return false;
 if(!hit?.object?.isMesh||hit.object.userData.atelierId!==selection){
   status('Sculpt picking: tap the selected mesh. Drag to orbit normally.',true);
   return true;
 }
 const local=hit.object.worldToLocal(hit.point.clone());
 // Raycaster face.normal uses the native triangle's part-local orientation.
 // A two-sided surface may have an inverted triangle; orient toward the view.
 const normal=hit.face?.normal?.clone()||new THREE.Vector3(0,0,1);
 const cameraLocal=hit.object.worldToLocal(camera.position.clone());
 if(normal.dot(cameraLocal.sub(local))<0)normal.negate();
 normal.normalize();
 atelierSculptHit={partId:selection,center:local.toArray(),axis:normal.toArray()};
 for(let i=0;i<3;i++){
   $m('SculptBrushCenter'+i).value=local.getComponent(i).toFixed(4);
   $m('SculptBrushAxis'+i).value=normal.getComponent(i).toFixed(4);
 }
 atelierSculptArmed=false;
 atelierSculptRefresh();
 status('Brush center and outward normal sampled from the selected mesh. Adjust radius, strength and Apply.');
 return true;
}
function atelierSculptForm(){
 const p=partById(selection);
 if(!p)return null;
 const xyz=stem=>[0,1,2].map(i=>Number($m('SculptBrush'+stem+i).value));
 const center=xyz('Center'),axis=xyz('Axis');
 const len=Math.hypot(...axis);
 const amount=Number($m('SculptBrushAmount').value);
 const s={
  center,axis:axis.map(v=>v/len),
  radius:Number($m('SculptBrushRadius').value),
  strength:($m('SculptBrushMode').value==='intrude'?-1:1)*amount,
  half:$m('SculptBrushHalf').checked,
  falloff:$m('SculptBrushFalloff').value,
  plateau:Number($m('SculptBrushPlateau').value),
  taper:Number($m('SculptBrushTaper').value),
  level:$m('SculptBrushLevel').checked,
  yaw:Number($m('SculptBrushYaw').value)*Math.PI/180,
  pitch:Number($m('SculptBrushPitch').value)*Math.PI/180,
  snap:Number($m('SculptBrushSnap').value)
 };
 if(!Number.isFinite(len)||len<1e-5||!atelierSculptValid({sculptBrushes:[s]}))return null;
 return s;
}
function atelierSculptInstall(){
 $m('SculptBrushPick').addEventListener('click',()=>{
   if(!partById(selection)){status('Select a mesh to sculpt first.',true);return;}
   atelierSculptArmed=!atelierSculptArmed;
   atelierSculptRefresh();
 });
 $m('SculptBrushApply').addEventListener('click',()=>{
   const p=partById(selection),s=atelierSculptForm();if(!p)return;
   if(!s){status('Invalid brush data. Radius .03–2.5, amount 0–.5, finite center/direction.',true);return;}
   if((p.sculptBrushes?.length??0)>=atelierSculptMaxStrokes){
     status('Maximum '+atelierSculptMaxStrokes+' strokes for one mesh. Use Undo or remove strokes.',true);return;
   }
   const next={...p,sculptBrushes:[...(p.sculptBrushes||[]),s]};
   if(!checkPart(next)){status('Sculpt geometry data rejected by native validation.',true);return;}
   checkpoint();p.sculptBrushes=next.sculptBrushes;const id=p.id;
   signalEdited();select(id);
   status('Saved '+(s.strength<0?'intrusion':'extrusion')+' as a local vertex falloff stroke. Save JSON to keep it.');
 });
 $m('SculptBrushUndoStroke').addEventListener('click',()=>{
   const p=partById(selection);if(!p?.sculptBrushes?.length)return;
   checkpoint();p.sculptBrushes=p.sculptBrushes.slice(0,-1);
   signalEdited();select(p.id);status('Last sculpt stroke removed; full-model Undo can restore it.');
 });
}
