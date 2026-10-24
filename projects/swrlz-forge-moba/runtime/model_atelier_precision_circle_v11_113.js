// §E v11.113: manually controlled circular carving for supported primitives.
// Native sphere, box planar face and cylinder end cap; indexed manifold result.
// Other topology meshes are not silently treated as Boolean-safe.
let atelierPrecisionCircleDraft=null;
function atelierPrecisionCircleClear(){
 const draft=atelierPrecisionCircleDraft;
 atelierPrecisionCircleDraft=null;
 if(!draft)return;
 if(draft.ghost){
  draft.ghost.parent?.remove(draft.ghost);
  draft.ghost.geometry?.dispose?.();
  draft.ghost.material?.dispose?.();
 }
 if(draft.sourceMesh)draft.sourceMesh.visible=true;
}
function atelierPrecisionCircleBuild(radius,center,axis,holes,shape={surface:'sphere'}){
 const surface=shape.surface||'sphere';
 if(!['sphere','box','cylinder'].includes(surface))
  return {ok:false,reason:'Use a sphere, flat box face, or cylinder end cap'};
 const halfU=shape.halfU??.5,halfV=shape.halfV??.5,halfDepth=shape.halfDepth??.5;
 if(surface!=='sphere'&&(![halfU,halfV,halfDepth].every(Number.isFinite)||
    Math.min(halfU,halfV,halfDepth)<.1||Math.max(halfU,halfV,halfDepth)>4))
  return {ok:false,reason:'Invalid primitive face size'};
 if(!THREE.ShapeUtils?.triangulateShape)
  return {ok:false,reason:'Browser mesh triangulator is unavailable'};
 if(!Number.isFinite(radius)||radius<.2||radius>4||
   !Array.isArray(center)||center.length!==3||!center.every(Number.isFinite)||
   !Array.isArray(axis)||axis.length!==3||!axis.every(Number.isFinite)||
   !Array.isArray(holes)||holes.length<1||holes.length>(surface==='sphere'?3:6))
  return {ok:false,reason:'Select a sphere, box face or cylinder cap and place each cut yourself'};
 if(holes.some(h=>!h||![h.x,h.y,h.r,h.depth,h.cap].every(Number.isFinite)||
   h.r<radius*.025||h.r>radius*.29||h.cap<0||h.cap>1||
   h.depth<h.r*h.cap+.01||
   h.depth>(surface==='sphere'?radius*.82:halfDepth*1.8)))
  return {ok:false,reason:'Radius 2.5–29% of local size; depth must exceed cap thickness and leave the back intact'};
 for(let i=0;i<holes.length;i++){
  const h=holes[i];
  if(surface==='box'?
    (Math.abs(h.x)+h.r>halfU*.94||Math.abs(h.y)+h.r>halfV*.94):
    (Math.hypot(h.x,h.y)+h.r>radius*.90))
   return {ok:false,reason:'Circular cut crosses the supported surface boundary'};
  for(let j=0;j<i;j++){
   const o=holes[j];
   if(Math.hypot(h.x-o.x,h.y-o.y)<h.r+o.r+radius*.025)
    return {ok:false,reason:'Circular cuts overlap; reposition or reduce radius'};
  }
 }
 const n=new THREE.Vector3(...axis).normalize();
 if(n.lengthSq()<.99)return {ok:false,reason:'Pick a valid facing direction'};
 const helper=Math.abs(n.y)<.9?new THREE.Vector3(0,1,0):new THREE.Vector3(1,0,0);
 const u=new THREE.Vector3().crossVectors(helper,n).normalize();
 const v=new THREE.Vector3().crossVectors(n,u).normalize();
 const origin=new THREE.Vector3(...center);
 let xy=[],front=[],index=[],lip=[],outer=[];
 const edge=(a,b)=>a<b?a+':'+b:b+':'+a;
 function boundaryCircle(cx,cy,r,num,clockwise){
  const ring=[];
  for(let k=0;k<num;k++){
   const t=(clockwise?-1:1)*2*Math.PI*k/num;
   ring.push(xy.length);xy.push([cx+r*Math.cos(t),cy+r*Math.sin(t)]);
  }
  return ring;
 }
 if(surface==='box'){
  for(const p of [[-halfU,-halfV],[halfU,-halfV],[halfU,halfV],[-halfU,halfV]]){
   outer.push(xy.length);xy.push(p);
  }
 }else outer=boundaryCircle(0,0,radius,72,false);
 lip=holes.map(h=>boundaryCircle(h.x,h.y,h.r,40,true));
 const contour=outer.map(i=>new THREE.Vector2(...xy[i]));
 const islands=lip.map(ring=>ring.map(i=>new THREE.Vector2(...xy[i])));
 const tris=THREE.ShapeUtils.triangulateShape(contour,islands);
 if(!tris.length)return {ok:false,reason:'Circular front patch triangulation failed'};
 front=tris.map(t=>{
  const a=t[0],b=t[1],c=t[2],p=xy[a],q=xy[b],r=xy[c];
  return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])>0?[a,b,c]:[a,c,b];
 });
 // Two conforming, stitched refinement passes keep the visible sphere
 // rounded between manually placed circular openings. This fixes the large
 // warped outer triangles visible in the original three-hole preview.
 const boundary=new Map(),midpoint=new Map();
 function tag(ring,cx,cy,r){
  for(let i=0;i<ring.length;i++)
   boundary.set(edge(ring[i],ring[(i+1)%ring.length]),{cx,cy,r});
 }
 function mid(a,b){
  const key=edge(a,b);
  if(midpoint.has(key))return midpoint.get(key);
  let x=(xy[a][0]+xy[b][0])/2,y=(xy[a][1]+xy[b][1])/2;
  const circle=boundary.get(key);
  if(circle){
   const dx=x-circle.cx,dy=y-circle.cy,len=Math.hypot(dx,dy);
   if(len<1e-9)throw Error('Collapsed radial edge');
   x=circle.cx+dx*circle.r/len;
   y=circle.cy+dy*circle.r/len;
  }
  const id=xy.length;xy.push([x,y]);midpoint.set(key,id);return id;
 }
 function splitLoop(loop){
  const next=[];
  for(let i=0;i<loop.length;i++)
   next.push(loop[i],mid(loop[i],loop[(i+1)%loop.length]));
  return next;
 }
 for(let level=0;level<(surface==='sphere'?2:1);level++){
  boundary.clear();midpoint.clear();
  if(surface!=='box')tag(outer,0,0,radius);
  lip.forEach((ring,k)=>tag(ring,holes[k].x,holes[k].y,holes[k].r));
  const children=[];
  for(const [a,b,c] of front){
   const ab=mid(a,b),bc=mid(b,c),ca=mid(c,a);
   children.push([a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]);
  }
  front=children;
  outer=splitLoop(outer);
  lip=lip.map(splitLoop);
 }
 const positions=[],uvs=[],faces=[];
 function add(x,y,z){
  const p=origin.clone().addScaledVector(u,x).addScaledVector(v,y).addScaledVector(n,z);
  const id=positions.length/3;
  positions.push(p.x,p.y,p.z);
  uvs.push(.5+x/(2*radius),.5+y/(2*radius));
  return id;
 }
 for(const [x,y] of xy){
  const z=surface==='sphere'?
    Math.sqrt(Math.max(0,radius*radius-x*x-y*y)):halfDepth;
  add(x,y,z);
 }
 function face(a,b,c){faces.push(a,b,c);}
 for(const tri of front)face(...tri);
 // Close the solid using SHARED front-boundary vertices and oriented walls.
 let previous=outer;
 if(surface==='sphere'){
  for(let row=1;row<10;row++){
   const phi=Math.PI/2+Math.PI/2*row/10;
   const current=outer.map(i=>{
    const a=Math.atan2(xy[i][1],xy[i][0]);
    return add(radius*Math.sin(phi)*Math.cos(a),
      radius*Math.sin(phi)*Math.sin(a),radius*Math.cos(phi));
   });
   for(let k=0;k<previous.length;k++){
    const q=(k+1)%previous.length;
    face(previous[k],current[k],current[q]);
    face(previous[k],current[q],previous[q]);
   }
   previous=current;
  }
 }else{
  const back=outer.map(i=>add(xy[i][0],xy[i][1],-halfDepth));
  for(let k=0;k<previous.length;k++){
   const q=(k+1)%previous.length;
   face(previous[k],back[k],back[q]);
   face(previous[k],back[q],previous[q]);
  }
  previous=back;
 }
 const pole=add(0,0,surface==='sphere'?-radius:-halfDepth);
 for(let k=0;k<previous.length;k++)
  face(previous[k],pole,previous[(k+1)%previous.length]);
 // Each hole is a closed, open-at-the-surface drill channel:
 // smooth wall (3 levels) + hemispherical bottom (4 levels and a tip).
 for(let hIndex=0;hIndex<holes.length;hIndex++){
  const h=holes[hIndex],opening=lip[hIndex];
  let top=opening;
  const capHeight=h.r*h.cap;
  const zCenter=surface==='sphere'?Math.sqrt(radius*radius-h.x*h.x-h.y*h.y):halfDepth;
  const wallEnd=zCenter-h.depth+capHeight;
  const baseZ=opening.map(i=>surface==='sphere'?
    Math.sqrt(Math.max(0,radius*radius-xy[i][0]*xy[i][0]-xy[i][1]*xy[i][1])):
    halfDepth);
  function stitch(next){
   for(let k=0;k<top.length;k++){
    const j=(k+1)%top.length;
    face(top[k],next[k],next[j]);
    face(top[k],next[j],top[j]);
   }
   top=next;
  }
  for(let row=1;row<=3;row++){
   const f=row/3;
   const ring=opening.map((id,k)=>{
    const [x,y]=xy[id];
    return add(x,y,baseZ[k]*(1-f)+wallEnd*f);
   });
   stitch(ring);
  }
  for(let row=1;row<4;row++){
   const phi=Math.PI*row/8;
   const shrink=Math.cos(phi),z=wallEnd-capHeight*Math.sin(phi);
   const ring=opening.map(id=>{
    const dx=xy[id][0]-h.x,dy=xy[id][1]-h.y;
    return add(h.x+dx*shrink,h.y+dy*shrink,z);
   });
   stitch(ring);
  }
  const tip=add(h.x,h.y,wallEnd-capHeight);
  for(let k=0;k<top.length;k++)
   face(top[k],tip,top[(k+1)%top.length]);
 }
 const data={positions,uvs,indices:faces};
 if(!atelierTopologyValid({kind:'topologyMesh',topologyMesh:data}))
  return {ok:false,reason:'New hole mesh exceeds the mobile indexed-mesh budget'};
 const audit=atelierTopologyAudit(data);
 if(!audit.ok||audit.nonManifoldEdges||audit.boundaryEdges||
    audit.oppositeWindingErrors||audit.zeroAreaFaces)
  return {ok:false,reason:'Bore mesh topology audit rejected: '+audit.boundaryEdges+
     ' boundaries, '+audit.nonManifoldEdges+' nonmanifold edges, '+
     audit.oppositeWindingErrors+' winding conflicts, '+audit.zeroAreaFaces+' degenerate faces'};
 return {ok:true,data,holes:holes.length,vertices:positions.length/3,triangles:faces.length/3};
}
// Saved, validated recipe allows one at a time edits on the SAME mesh.
function atelierBorePlanValid(part){
 const p=part?.roundHolePlan;
 if(p===undefined)return true;
 if(part.kind!=='topologyMesh'||!p||typeof p!=='object'||
   !Number.isFinite(p.radius)||p.radius<.2||p.radius>4||
   !Array.isArray(p.center)||p.center.length!==3||!p.center.every(Number.isFinite)||
   !Array.isArray(p.axis)||p.axis.length!==3||!p.axis.every(Number.isFinite)||
   !Array.isArray(p.holes)||p.holes.length<1||
   (p.surface&&!['sphere','box','cylinder'].includes(p.surface))||
   p.holes.length>(p.surface&&p.surface!=='sphere'?6:3))return false;
 if(p.surface&&p.surface!=='sphere'&&
   (![p.halfU,p.halfV,p.halfDepth].every(x=>Number.isFinite(x)&&x>=.1&&x<=4)))return false;
 const surface=p.surface||'sphere',limit=surface==='sphere'?p.radius*.82:p.halfDepth*1.8;
 return p.holes.every(h=>h&&[h.x,h.y,h.r,h.depth,h.cap].every(Number.isFinite)&&
   h.r>=p.radius*.025&&h.r<=p.radius*.29&&h.cap>=0&&h.cap<=1&&
   h.depth>=h.r*h.cap+.01&&h.depth<=limit);
}
const atelierBeforeBoreCheckPart=checkPart;
checkPart=function(p){return atelierBeforeBoreCheckPart(p)&&atelierBorePlanValid(p);};
function atelierBoreCoordinates(plan,point){
 const n=new THREE.Vector3(...plan.axis).normalize();
 const helper=Math.abs(n.y)<.9?new THREE.Vector3(0,1,0):new THREE.Vector3(1,0,0);
 const u=new THREE.Vector3().crossVectors(helper,n).normalize();
 const v=new THREE.Vector3().crossVectors(n,u).normalize();
 const offset=new THREE.Vector3(...point).sub(new THREE.Vector3(...plan.center));
 if(offset.dot(n)<=0)return null;
 return {x:offset.dot(u),y:offset.dot(v)};
}
function atelierPrecisionCircleInstall(){
 const pick=$m('SculptBrushPick');
 if(!pick||document.getElementById('modelAtelierBoreTools'))return;
 const panel=document.createElement('fieldset');
 panel.id='modelAtelierBoreTools';
 panel.setAttribute('aria-label','Precision circle cuts on spheres, box faces and cylinder end caps');
 panel.innerHTML='<legend>⭕ Precision circle cut · reusable shape tool</legend>'+
  '<p><b>Design every circle yourself.</b> Pick a point on a sphere, flat box face or cylinder end cap; set the radius, depth and bottom finish. Useful for sockets, holes, recesses, vents and similar shapes.</p>'+
  '<label>Circular cut to create or adjust<select id="modelAtelierBoreWhich"><option value="new">+ New circular cut at picked spot</option></select></label>'+
  '<div class="atelier-pair"><label>Cut radius · local units<input id="modelAtelierBoreRadius" type="number" min=".02" max=".29" step=".005" value=".12"></label>'+
  '<label>Cut depth · local units<input id="modelAtelierBoreDepth" type="number" min=".02" max=".9" step=".01" value=".36"></label></div>'+
  '<label>Bottom finish · 0 flat / 1 rounded<input id="modelAtelierBoreCap" type="number" min="0" max="1" step=".1" value=".8"></label>'+
  '<label><input id="modelAtelierBoreRelocate" type="checkbox"> Reposition selected saved cut using a new picked point</label><small>Carve individually: up to 3 cuts on a sphere or 6 on one flat face. Cuts on a part share the first selected face direction. Native box faces and cylinder ends are supported; arbitrary imported mesh Boolean cuts are not. First cut replaces any prior sculpt strokes on that part; Undo restores them.</small>'+
  '<div class="atelier-inspector-actions"><button id="modelAtelierBorePreview" type="button">Preview this hole</button>'+
  '<button id="modelAtelierBoreApply" type="button">Apply this hole</button>'+
  '<button id="modelAtelierBoreHide" type="button">Hide preview</button></div>'+
  '<output id="modelAtelierBoreInfo" role="status">Pick a surface point to start the first precision cut.</output>';
 pick.closest('.atelier-inspector-actions')?.insertAdjacentElement('afterend',panel);
 const el=name=>document.getElementById('modelAtelierBore'+name);
 function clear(reason='Preview cleared. Saved holes unchanged.'){
  atelierPrecisionCircleClear();
  el('Info').textContent=reason;
 }
 function refreshChoices(){
  const old=el('Which').value;
  const p=partById(selection),holes=p?.roundHolePlan?.holes||[];
  el('Which').replaceChildren(new Option('+ New circular cut at picked spot','new'));
  for(let i=0;i<holes.length;i++)
   el('Which').add(new Option('Adjust hole '+(i+1),'hole-'+i));
  el('Which').value=[...el('Which').options].some(o=>o.value===old)?old:'new';
  const max=p?.roundHolePlan?.surface&&p.roundHolePlan.surface!=='sphere'?6:3;
  if(holes.length>=max&&el('Which').value==='new')
   el('Info').textContent='Maximum '+max+' saved cuts on this face. Select one to edit.';
 }
 el('Which').addEventListener('change',()=>{
  clear();
  const p=partById(selection),idx=Number(el('Which').value.slice(5));
  if(el('Which').value.startsWith('hole-')&&p?.roundHolePlan?.holes[idx]){
   const h=p.roundHolePlan.holes[idx];
   el('Radius').value=h.r;el('Depth').value=h.depth;el('Cap').value=h.cap;el('Relocate').checked=false;
   el('Info').textContent='Editing saved circle '+(idx+1)+'. Change dimensions; optionally pick a new center.';
  }
 });
 for(const id of ['Radius','Depth','Cap','Relocate'])el(id).addEventListener('input',()=>clear('Settings changed. Preview again before Apply.'));
 el('Hide').addEventListener('click',()=>clear());
 el('Preview').addEventListener('click',()=>{
  clear();
  const p=partById(selection);
  if(!p||!(['sphere','box','cylinder'].includes(p.kind)||
    p.kind==='topologyMesh'&&p.roundHolePlan)){
   status('Select a native sphere, box, cylinder or previously edited precision-cut mesh.',true);
   return;
  }
  const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===p.id);
  if(!mesh)return;
  const existing=p.roundHolePlan?structuredClone(p.roundHolePlan):null;
  const hit=atelierSculptHit?.partId===p.id?atelierSculptHit:null;
  if(!existing&&!hit){
   status('First tap Pick center on mesh, then tap exactly where your first hole goes.',true);return;
  }
  mesh.geometry.computeBoundingSphere();
  const bound=mesh.geometry.boundingSphere,origin=bound.center.toArray();
  let plan=existing;
  if(!plan){
   const surface=p.kind;
   const initialAxis=new THREE.Vector3(...(hit?.axis||[0,0,1]));
   if(surface==='sphere')initialAxis.fromArray(hit.center).sub(new THREE.Vector3(...origin));
   if(surface==='box'){
    const index=initialAxis.toArray().map(Math.abs).indexOf(Math.max(...initialAxis.toArray().map(Math.abs)));
    initialAxis.set(index===0?Math.sign(initialAxis.x):0,
      index===1?Math.sign(initialAxis.y):0,index===2?Math.sign(initialAxis.z):0);
   }
   if(surface==='cylinder'&&Math.abs(initialAxis.y)<.86){
    status('For cylinders, tap the FLAT top or bottom cap, not the curved side.',true);return;
   }
   if(initialAxis.lengthSq()<1e-10)initialAxis.set(0,0,1);
   const radius=surface==='box'?.5:surface==='cylinder'?1:bound.radius;
   plan={surface,radius,center:origin,axis:initialAxis.normalize().toArray(),
     halfU:.5,halfV:.5,halfDepth:.5,holes:[]};
  }
  const idxStr=el('Which').value,editing=idxStr.startsWith('hole-');
  const index=editing?Number(idxStr.slice(5)):-1;
  if(editing&&!plan.holes[index]){status('Select a saved hole to edit.',true);return;}
  if(!editing&&!hit){status('Use Pick center on mesh to place the next hole.',true);return;}
  const max=plan.surface==='sphere'||!plan.surface?3:6;
  if(!editing&&plan.holes.length>=max){status('This face supports '+max+' individual cuts within the mobile mesh budget.',true);return;}
  const relocate=editing&&el('Relocate').checked;
  if(relocate&&!hit){status('Use Pick center on mesh to choose the NEW position of this cut.',true);return;}
  const position=editing&&!relocate?
    {x:plan.holes[index].x,y:plan.holes[index].y}:
    hit?atelierBoreCoordinates(plan,hit.center):null;
  if(!position){status('Pick the same compatible face/direction as the first cut.',true);return;}
  const r=Number(el('Radius').value),depth=Number(el('Depth').value),cap=Number(el('Cap').value);
  const hole={x:position.x,y:position.y,r,depth,cap};
  if(editing)plan.holes[index]=hole;
  else plan.holes.push(hole);
  const made=atelierPrecisionCircleBuild(plan.radius,plan.center,plan.axis,plan.holes,plan);
  if(!made.ok){status('Circle carve rejected: '+made.reason,true);return;}
  const candidate={
   id:p.id,name:(p.roundHolePlan?p.name:p.name+' · precision cuts').slice(0,64),
   group:p.group,kind:'topologyMesh',topologyMesh:made.data,
   roundHolePlan:plan,
   position:[...p.position],rotation:[...p.rotation],scale:[...p.scale],
   color:p.color,material:p.material
  };
  if(!checkPart(candidate)){status('Precision hole geometry failed native validation.',true);return;}
  const geometry=atelierTopologyGeometry(candidate);
  const ghost=new THREE.Mesh(geometry,mesh.material.clone());
  mesh.updateMatrixWorld(true);
  ghost.matrixAutoUpdate=false;
  ghost.matrix.copy(mesh.matrixWorld);
  ghost.userData.atelierHelper=true;
  ghost.name='Temporary user-controlled precision circular cut geometry';
  world.add(ghost);
  mesh.visible=false;
  atelierPrecisionCircleDraft={candidate,originalId:p.id,baseline:JSON.stringify(p),sourceMesh:mesh,ghost};
  el('Info').textContent=(editing?'Adjusting hole '+(index+1):'Adding hole '+plan.holes.length)+
    ' · '+made.holes+' individually designed · '+made.vertices+' vertices / '+made.triangles+
    ' triangles. Rotate to inspect. Apply commits; Undo restores.';
  status('Previewing your individually positioned cylindrical carve and rounded bottom; nothing saved yet.');
 });
 el('Apply').addEventListener('click',()=>{
  const d=atelierPrecisionCircleDraft,p=partById(selection);
  if(!d||!p||p.id!==d.originalId||JSON.stringify(p)!==d.baseline){
   status('Preview this current mesh before applying a hole.',true);return;
  }
  const index=model().parts.findIndex(x=>x.id===p.id);
  if(index<0||!checkPart(d.candidate))return;
  const committed=d.candidate;
  atelierPrecisionCircleClear();
  checkpoint();
  model().parts[index]=committed;
  atelierSculptHit=null;
  signalEdited();select(committed.id);
  el('Which').value='new';el('Relocate').checked=false;
  refreshChoices();
  el('Info').textContent='Hole committed. '+committed.roundHolePlan.holes.length+
    ' saved. Pick another position, or select a saved hole to edit.';
  status('Saved your hand-placed round cut with Undo. Pick another point or edit an earlier circular feature.');
 });
 el('Which').addEventListener('focus',refreshChoices);
 // Keep the edit picker synchronized after each selection or prior Undo.
 document.getElementById('modelAtelierParts')?.addEventListener('change',()=>{clear();refreshChoices();});
 document.getElementById('modelAtelierUndo')?.addEventListener('click',()=>{clear();refreshChoices();});
 refreshChoices();
}
