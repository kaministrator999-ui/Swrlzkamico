/* SE441_SATCHEL_WORKFLOW_START */
// Explicit Verify only. Read native descriptors; never create model parts,
// change selection, invoke tools, or write source/history from this inspector.
const se441SatchelWorkflow=(()=>{
 const LIMITS=Object.freeze({parts:400,verticesPerPart:9000,trianglesPerPart:16000,totalVertices:48000,totalTriangles:80000});
 const finite3=v=>Array.isArray(v)&&v.length===3&&v.every(Number.isFinite);
 const result=(ok,message,extra={})=>({ok,message,...extra});
 const stage=message=>result(false,message);
 const plainBox=box=>({min:box.min.toArray(),max:box.max.toArray(),center:box.getCenter(new THREE.Vector3()).toArray(),size:box.getSize(new THREE.Vector3()).toArray()});
 const deformed=p=>!!(p?.sculptVertexEdits?.length||p?.sculptBrushes?.length||p?.sculptLassos?.some(r=>r.enabled&&r.morph)||p?.refinementLayers?.some(r=>r.enabled));
 const matrix=p=>new THREE.Matrix4().compose(new THREE.Vector3(...p.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...p.rotation)),new THREE.Vector3(...p.scale));
 function descriptor(p,budget){
  if(deformed(p))return null;
  if(!p||typeof p.id!=='string'||!finite3(p.position)||!finite3(p.rotation)||!finite3(p.scale)||p.scale.some(n=>n<=.005||n>20))return null;
  let points,indices=null,closed=false;
  if(p.kind==='topologyMesh'){
   const d=p.topologyMesh;
   if(!d||!Array.isArray(d.positions)||!Array.isArray(d.indices)||d.positions.length/3>LIMITS.verticesPerPart||d.indices.length/3>LIMITS.trianglesPerPart)return null;
   const audit=typeof se430MeshOps!=='undefined'?se430MeshOps.audit(d):null;
   if(!audit?.ok||audit.zeroAreaFaces||audit.nonManifoldEdges||audit.oppositeWindingErrors)return null;
   points=Array.from({length:d.positions.length/3},(_,i)=>new THREE.Vector3(...d.positions.slice(i*3,i*3+3)));
   indices=d.indices;let volume=0;
   for(let i=0;i<indices.length;i+=3){const a=points[indices[i]],b=points[indices[i+1]],c=points[indices[i+2]];volume+=a.dot(b.clone().cross(c))/6;}
   closed=audit.boundaryEdges===0&&Math.abs(volume)>1e-10;
  }else if(p.kind==='box'){
   points=[];for(const x of [-.5,.5])for(const y of [-.5,.5])for(const z of [-.5,.5])points.push(new THREE.Vector3(x,y,z));closed=true;
  }else if(p.kind==='sphere'){
   // Sphere clasp bounds use actual transformed surface samples. Its native
   // primitive is closed; this read-only temporary geometry is disposed here.
   // Native sphere parts have radius 1; descriptor scale is their radius,
   // unlike BoxGeometry's unit-wide dimensions.
   const g=new THREE.SphereGeometry(1,20,16),a=g.attributes.position;points=[];
   for(let i=0;i<a.count;i++)points.push(new THREE.Vector3().fromBufferAttribute(a,i));g.dispose();closed=true;
  }else return null;
  budget.vertices+=points.length;budget.triangles+=(indices?.length||0)/3;
  if(budget.vertices>LIMITS.totalVertices||budget.triangles>LIMITS.totalTriangles){budget.exceeded=true;return null;}
  const m=matrix(p),world=points.map(v=>v.clone().applyMatrix4(m)),bounds=new THREE.Box3().setFromPoints(world);
  if(bounds.isEmpty()||!world.every(v=>[v.x,v.y,v.z].every(Number.isFinite)))return null;
  return {p,points,indices,closed,matrix:m,world,bounds};
 }
 function legacyBody(entries){
  // Preserve already-saved five-piece learners; new lessons never teach this.
  const boxes=entries.filter(e=>e.p.kind==='box'&&e.p.rotation.every(n=>Math.abs(n)<.25));
  for(const floor of boxes){
   const f=plainBox(floor.bounds);if(f.size[0]<.85||f.size[2]<.35||f.size[1]>.23)continue;
   const candidates=boxes.filter(e=>e!==floor).map(e=>({e,b:plainBox(e.bounds)}));
   const elevated=b=>b.center[1]>f.center[1]+.18&&b.min[1]<=f.max[1]+.2&&b.size[1]>.42;
   const side=(axis,sign)=>candidates.find(({b})=>elevated(b)&&b.size[axis]<.25&&b.size[axis===0?2:0]>(axis===0?.3:.62)&&
    (b.center[axis]-f.center[axis])*sign>=f.size[axis]*(axis===0?.34:.25));
   const walls=[side(0,-1),side(0,1),side(2,-1),side(2,1)];if(walls.some(w=>!w)||new Set(walls.map(w=>w.e.p.id)).size!==4)continue;
   const ids=new Set([floor.p.id,...walls.map(w=>w.e.p.id)]);
   const roof=candidates.some(({e,b})=>!ids.has(e.p.id)&&b.size[0]>.7&&b.size[2]>.32&&b.size[1]<.24&&b.center[1]>f.center[1]+.5&&Math.abs(b.center[2]-f.center[2])<f.size[2]*.3);
   if(roof)continue;
   const bounds=floor.bounds.clone();for(const w of walls)bounds.union(w.e.bounds);
   return {ids,bounds,matrix:new THREE.Matrix4(),localBox:bounds.clone(),legacy:true};
  }
  return null;
 }
 function inBody(entry,body){
  const inverse=body.matrix.clone().invert(),box=body.localBox,center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3());
  if(size.x<1e-6||size.y<1e-6||size.z<1e-6)return null;
  const points=entry.world.map(p=>p.clone().applyMatrix4(inverse).sub(center).divide(size));
  return {entry,points,box:plainBox(new THREE.Box3().setFromPoints(points))};
 }
 const overlaps=(a,b,c,d)=>Math.max(a,c)<=Math.min(b,d);
 function containsXY(record,x,y){
  if(!record.entry.indices)return false;
  const ids=record.entry.indices,p=record.points;
  for(let i=0;i<ids.length;i+=3){
   const a=p[ids[i]],b=p[ids[i+1]],c=p[ids[i+2]],area=(b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x);
   if(Math.abs(area)<1e-9)continue;
   const u=((b.x-x)*(c.y-y)-(b.y-y)*(c.x-x))/area;
   const v=((c.x-x)*(a.y-y)-(c.y-y)*(a.x-x))/area,w=1-u-v;
   if(u>=-1e-8&&v>=-1e-8&&w>=-1e-8)return true;
  }
  return false;
 }
 function inspect(parts,options={}){
  if(!options||typeof options!=='object'||Array.isArray(options))options={};
  const checks={body:stage('Make one editable cube into an inset rim and inward-extruded cavity first.'),
   flap:stage('Draw one separate flap outline, add thickness, then fit it across the upper front of the bag.'),
   strap:stage('Draw one U-shaped strap outline with an empty middle, add thickness, and bring both ends to the bag sides.'),
   clasp:stage('Add a small clasp on the flap front. Its metal finish is checked in the materials step.'),
   materials:stage('Finish the body/flap in colored matte leather and the clasp in metal.')};
  let manualReviewParts=[];
  const finish=extra=>({manualReviewParts,ok:Object.values(checks).every(c=>c.ok),...checks,checks,limits:LIMITS,visualReviewRequired:true,...extra});
  if(!Array.isArray(parts)||!parts.length||parts.length>LIMITS.parts)return finish({message:'Open a bounded native satchel model before checking it.'});
  if(new Set(parts.map(p=>p?.id)).size!==parts.length)return finish({message:'Part IDs must be unique before tutorial inspection.'});
  manualReviewParts=parts.filter(deformed).map(p=>p.id);
  const budget={vertices:0,triangles:0,exceeded:false},entries=parts.map(p=>descriptor(p,budget)).filter(Boolean);
  if(budget.exceeded)return finish({message:'This model exceeds the lightweight lesson inspection budget. Inspect it manually; no project data was changed.',budget});
  const recognized=typeof se436SatchelCavity!=='undefined'?se436SatchelCavity.inspect(options.bodyPartId?parts.filter(p=>p.id===options.bodyPartId):parts):null;
  let body=entries.find(e=>e.p.id===recognized?.partId&&recognized?.ok&&e.closed);
  if(body){
   const localBox=new THREE.Box3().setFromPoints(body.points);
   body={ids:new Set([body.p.id]),bounds:body.bounds,matrix:body.matrix,localBox,legacy:false};
  }else if(options.allowLegacy!==false)body=legacyBody(entries);
  if(!body){if(recognized?.ok&&manualReviewParts.includes(recognized.partId))checks.body=stage('The body has sculpt/deformation layers. Inspect the rendered cavity manually; this bounded checker does not approve its undeformed base mesh.');return finish({message:checks.body.message,budget});}
  checks.body=result(true,body.legacy?'Your previously saved floor-and-wall body remains supported; new lessons use one connected cavity.':'One connected inset rim, inner walls and recessed floor are present.',{partId:[...body.ids][0],partIds:[...body.ids],bounds:plainBox(body.bounds),legacy:body.legacy});
  const candidates=entries.filter(e=>!body.ids.has(e.p.id)).map(e=>inBody(e,body)).filter(Boolean);
  const flap=candidates.find(r=>r.entry.closed&&Math.abs(r.box.center[0])<.35&&(
   ['topologyMesh','box'].includes(r.entry.p.kind)&&r.box.size[0]>=.5&&r.box.size[0]<=1.6&&r.box.size[1]>=.12&&r.box.size[1]<=.85&&r.box.size[2]>.005&&r.box.size[2]<=.45&&
    r.box.max[1]>=.30&&r.box.min[1]<.48&&r.box.center[2]>=.42&&r.box.center[2]<=.95&&r.box.min[2]<=.72&&overlaps(r.box.min[1],r.box.max[1],-.15,.5)||
   options.allowLegacy!==false&&r.entry.p.kind==='box'&&r.box.size[0]>=.5&&r.box.size[0]<=1.6&&r.box.size[1]>.005&&r.box.size[1]<.3&&r.box.size[2]>.3&&r.box.size[2]<1.2&&r.box.center[1]>.3&&r.box.center[1]<.8&&r.box.center[2]>.15&&r.box.center[2]<.9));
  if(flap)checks.flap=result(true,'A separate closed thin flap overlaps the upper front. Inspect its hinge/rim contact from the side.',{partId:flap.entry.p.id,bounds:plainBox(flap.entry.bounds)});
  const strap=candidates.find(r=>r!==flap&&r.entry.closed&&r.entry.p.kind==='topologyMesh'&&r.box.size[0]>=.75&&r.box.size[0]<=2.2&&r.box.max[1]>.85&&r.box.min[1]<.65&&r.box.size[2]<=.5&&Math.abs(r.box.center[2])<=.85&&
   r.points.some(p=>p.x<-.32&&p.x>-.78&&p.y<.65&&p.y>-.35&&Math.abs(p.z)<.8)&&
   r.points.some(p=>p.x>.32&&p.x<.78&&p.y<.65&&p.y>-.35&&Math.abs(p.z)<.8)&&
   !containsXY(r,0,(.5+r.box.max[1])/2));
  let strapIds=strap?[strap.entry.p.id]:[];
  if(!strap&&options.allowLegacy!==false){
   const segments=candidates.filter(r=>r!==flap&&r.entry.p.kind==='box'&&r.box.size.filter(n=>n<.3).length>=2&&r.box.max[1]>.5);
   const left=segments.find(r=>r.box.center[0]<-.32&&r.box.min[1]<.65&&Math.abs(r.box.center[2])<.85),right=segments.find(r=>r.box.center[0]>.32&&r.box.min[1]<.65&&Math.abs(r.box.center[2])<.85),top=segments.find(r=>r.box.center[1]>.85&&r.box.min[0]<-.25&&r.box.max[0]>.25);
   if(left&&right&&top&&new Set([left,right,top]).size===3)strapIds=[left.entry.p.id,right.entry.p.id,top.entry.p.id];
  }
  if(strapIds.length)checks.strap=result(true,'A thick strap spans both bag sides, with an elevated arch and an empty middle. Visually check the actual joins and side view.',{partId:strapIds[0],partIds:strapIds,legacy:!strap,bounds:strap?plainBox(strap.entry.bounds):null});
  const reserved=new Set([...body.ids,...strapIds,flap?.entry.p.id]);
  const clasp=candidates.find(r=>!reserved.has(r.entry.p.id)&&r.entry.closed&&r.box.size[0]>=.025&&r.box.size[0]<=.38&&r.box.size[1]>=.025&&r.box.size[1]<=.4&&r.box.size[2]>=.008&&r.box.size[2]<=.4&&Math.abs(r.box.center[0])<.42&&r.box.center[1]>-.25&&r.box.center[1]<.55&&r.box.center[2]>=.35&&r.box.center[2]<=1.05&&(!flap||overlaps(r.box.min[0],r.box.max[0],flap.box.min[0],flap.box.max[0])&&overlaps(r.box.min[1],r.box.max[1],flap.box.min[1],flap.box.max[1])&&r.box.min[2]<=flap.box.max[2]+.18&&r.box.max[2]>=flap.box.min[2]-.08));
  if(clasp)checks.clasp=result(true,'A separate small closed clasp sits on the flap front. Apply its metal finish in Materials.',{partId:clasp.entry.p.id,bounds:plainBox(clasp.entry.bounds)});
  const leather=p=>p&&['matte','silk'].includes(p.material)&&/^#[0-9a-f]{6}$/i.test(p.color||'')&&p.color.toLowerCase()!=='#ffffff';
  const bodyLeather=[...body.ids].some(id=>leather(parts.find(p=>p.id===id))),flapLeather=!!flap&&leather(flap.entry.p),metal=!!clasp&&clasp.entry.p.material==='metal';
  if(bodyLeather&&flapLeather&&metal)checks.materials=result(true,'The actual body and flap use colored matte leather; the detected clasp uses metal.',{bodyLeather,flapLeather,claspMetal:metal});
  else checks.materials=stage(!bodyLeather?'Select the bag body and apply Leather.':!flapLeather?'Select the separate flap and apply Leather.':'Select the detected clasp and apply Metal. Geometry completion does not require metal before this finishing step.');
  return finish({message:manualReviewParts.length?'Some sculpted/deformed parts require manual rendered-geometry review; inspect fit, silhouette and saving yourself.':'Shape and material checks are guidance; inspect fit, silhouette and saving yourself.',budget});
 }
 return Object.freeze({inspect,limits:LIMITS});
})();
window.SWYRL_E_SATCHEL_WORKFLOW_441=se441SatchelWorkflow;
/* SE441_SATCHEL_WORKFLOW_END */
