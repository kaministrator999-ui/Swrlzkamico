// §E v11.111: specialized, light indexed bowling-ball bore builder.
// NOT a general mesh Boolean. Operates only on a spherical primitive.
// Constructs real round openings, cylinder walls and hemispherical bottoms.
let atelierBowlingDraft=null;
function atelierBowlingClear(){
 const draft=atelierBowlingDraft;
 atelierBowlingDraft=null;
 if(!draft)return;
 if(draft.ghost){
  draft.ghost.parent?.remove(draft.ghost);
  draft.ghost.geometry?.dispose?.();
  draft.ghost.material?.dispose?.();
 }
 if(draft.sourceMesh)draft.sourceMesh.visible=true;
}
function atelierBowlingBuild(radius,center,axis,number,smallRadius,depth){
 if(!THREE.ShapeUtils?.triangulateShape)
  return {ok:false,reason:'Browser mesh triangulator is unavailable'};
 if(![radius,smallRadius,depth].every(Number.isFinite)||radius<.2||
   radius>4||smallRadius<radius*.07||smallRadius>radius*.22||
   depth<smallRadius*1.6||depth>radius*.75||
   ![1,3].includes(number))
  return {ok:false,reason:'Choose a circle radius 7–22% of ball size and depth at least 1.6 times the hole radius (max 75% of ball size)'};
 const holes=number===3?[
  {x:-radius*.255,y:radius*.23,r:smallRadius},
  {x: radius*.255,y:radius*.23,r:smallRadius},
  {x:0,y:-radius*.36,r:smallRadius*1.2}
 ]:[{x:0,y:0,r:smallRadius}];
 for(let i=0;i<holes.length;i++){
  const h=holes[i];
  if(Math.hypot(h.x,h.y)+h.r>radius*.84)
   return {ok:false,reason:'Hole too large for selected ball'};
  for(let j=0;j<i;j++){
   const o=holes[j];
   if(Math.hypot(h.x-o.x,h.y-o.y)<h.r+o.r+radius*.05)
    return {ok:false,reason:'Finger holes overlap; reduce the hole radius'};
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
 outer=boundaryCircle(0,0,radius,72,false);
 lip=holes.map(h=>boundaryCircle(h.x,h.y,h.r,40,true));
 const contour=outer.map(i=>new THREE.Vector2(...xy[i]));
 const islands=lip.map(ring=>ring.map(i=>new THREE.Vector2(...xy[i])));
 const tris=THREE.ShapeUtils.triangulateShape(contour,islands);
 if(!tris.length)return {ok:false,reason:'Circular front patch triangulation failed'};
 front=tris.map(t=>{
  const a=t[0],b=t[1],c=t[2],p=xy[a],q=xy[b],r=xy[c];
  return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])>0?[a,b,c]:[a,c,b];
 });
 // One exact stitched subdivision pass keeps round lip/equator edges circular.
 const boundary=new Map();
 function tag(ring,cx,cy,r){
  for(let i=0;i<ring.length;i++)
   boundary.set(edge(ring[i],ring[(i+1)%ring.length]),{cx,cy,r});
 }
 tag(outer,0,0,radius);
 lip.forEach((r,k)=>tag(r,holes[k].x,holes[k].y,holes[k].r));
 const midpoint=new Map();
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
 const children=[];
 for(const [a,b,c] of front){
  const ab=mid(a,b),bc=mid(b,c),ca=mid(c,a);
  children.push([a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]);
 }
 front=children;
 function splitLoop(loop){
  const next=[];
  for(let i=0;i<loop.length;i++){
   next.push(loop[i],mid(loop[i],loop[(i+1)%loop.length]));
  }
  return next;
 }
 outer=splitLoop(outer);
 lip=lip.map(splitLoop);
 const positions=[],uvs=[],faces=[];
 function add(x,y,z){
  const p=origin.clone().addScaledVector(u,x).addScaledVector(v,y).addScaledVector(n,z);
  const id=positions.length/3;
  positions.push(p.x,p.y,p.z);
  uvs.push(.5+x/(2*radius),.5+y/(2*radius));
  return id;
 }
 for(const [x,y] of xy){
  const z=Math.sqrt(Math.max(0,radius*radius-x*x-y*y));
  add(x,y,z);
 }
 function face(a,b,c){faces.push(a,b,c);}
 for(const tri of front)face(...tri);
 // Back half: connect to the SAME outer equator, close at south pole.
 let previous=outer;
 const rearSteps=10;
 for(let row=1;row<rearSteps;row++){
  const phi=(Math.PI/2)+(Math.PI/2)*row/rearSteps;
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
 const pole=add(0,0,-radius);
 for(let k=0;k<previous.length;k++)
  face(previous[k],pole,previous[(k+1)%previous.length]);
 // Each hole is a closed, open-at-the-surface drill channel:
 // smooth wall (3 levels) + hemispherical bottom (4 levels and a tip).
 for(let hIndex=0;hIndex<holes.length;hIndex++){
  const h=holes[hIndex],opening=lip[hIndex];
  let top=opening;
  const zCenter=Math.sqrt(radius*radius-h.x*h.x-h.y*h.y);
  const wallEnd=zCenter-depth+h.r;
  const baseZ=opening.map(i=>Math.sqrt(Math.max(0,radius*radius-
    xy[i][0]*xy[i][0]-xy[i][1]*xy[i][1])));
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
   const shrink=Math.cos(phi),z=wallEnd-h.r*Math.sin(phi);
   const ring=opening.map(id=>{
    const dx=xy[id][0]-h.x,dy=xy[id][1]-h.y;
    return add(h.x+dx*shrink,h.y+dy*shrink,z);
   });
   stitch(ring);
  }
  const tip=add(h.x,h.y,wallEnd-h.r);
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
 return {ok:true,data,holes:number,vertices:positions.length/3,triangles:faces.length/3};
}
function atelierBowlingInstall(){
 const sculpt=$m('SculptBrush'),pick=$m('SculptBrushPick');
 if(!sculpt||!pick||document.getElementById('modelAtelierBowlingKit'))return;
 const panel=document.createElement('fieldset');
 panel.id='modelAtelierBowlingKit';
 panel.setAttribute('aria-label','Precision round bowling ball holes');
 panel.innerHTML='<legend>🎳 Round hole maker · bowling ball</legend>'+
  '<p>Actual circular openings, cylindrical walls and rounded bottoms—not a triangular sculpt dent. Pick the ball to orient the holes, or use the front as default.</p>'+
  '<label>Hole layout<select id="modelAtelierBowlingCount"><option value="3">3 holes · bowling ball</option><option value="1">1 hole · practice drill</option></select></label>'+
  '<div class="atelier-pair"><label>Finger radius (local units)<input id="modelAtelierBowlingRadius" type="number" min=".07" max=".22" step=".01" value=".15"></label>'+
  '<label>Total depth (local units)<input id="modelAtelierBowlingDepth" type="number" min=".15" max=".75" step=".01" value=".45"></label></div>'+
  '<small>Thumb is 20% wider in the three-hole preset. The bottom is hemispherical. Rebuilds a clean spherical part into an editable indexed mesh; any earlier sculpt strokes on that part are replaced. Undo restores the original.</small>'+
  '<div class="atelier-inspector-actions"><button type="button" id="modelAtelierBowlingPreview">Preview real holes</button><button type="button" id="modelAtelierBowlingApply">Apply hole geometry</button><button type="button" id="modelAtelierBowlingCancel">Hide preview</button></div>'+
  '<output id="modelAtelierBowlingStatus" role="status">Select a spherical part, then preview before applying.</output>';
 pick.closest('.atelier-inspector-actions')?.insertAdjacentElement('afterend',panel);
 const el=name=>document.getElementById('modelAtelierBowling'+name);
 function invalidate(){atelierBowlingClear();el('Status').textContent='Settings changed. Preview the hole geometry again.';}
 ['Count','Radius','Depth'].forEach(key=>{el(key).addEventListener('input',invalidate);el(key).addEventListener('change',invalidate);});
 el('Cancel').addEventListener('click',()=>{
  atelierBowlingClear();el('Status').textContent='Preview hidden. Original mesh unchanged.';
 });
 el('Preview').addEventListener('click',()=>{
  atelierBowlingClear();
  const part=partById(selection);
  if(part?.kind!=='sphere'){
   status('Select a native sphere (Model blockout) for the simplified bowling-hole maker.',true);
   return;
  }
  const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===part.id);
  if(!mesh)return;
  mesh.geometry.computeBoundingSphere();
  const bound=mesh.geometry.boundingSphere;
  const radius=bound.radius,center=bound.center.toArray();
  const hit=atelierSculptHit?.partId===part.id?atelierSculptHit:null;
  const axis=hit?new THREE.Vector3(...hit.center).sub(new THREE.Vector3(...center)).normalize().toArray():[0,0,1];
  const count=Number(el('Count').value),finger=Number(el('Radius').value),depth=Number(el('Depth').value);
  const made=atelierBowlingBuild(radius,center,axis,count,finger,depth);
  if(!made.ok){status('Bowling hole preview rejected: '+made.reason,true);return;}
  const candidate={
   id:part.id,name:(part.name+' · round holes').slice(0,64),
   group:part.group,kind:'topologyMesh',topologyMesh:made.data,
   position:[...part.position],rotation:[...part.rotation],
   scale:[...part.scale],color:part.color,material:part.material
  };
  if(!checkPart(candidate)){
   status('Generated round-hole mesh failed native validation.',true);return;
  }
  const geometry=atelierTopologyGeometry(candidate);
  const ghost=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({
   color:0xc0e6fa,metalness:.15,roughness:.52,side:THREE.DoubleSide
  }));
  mesh.updateMatrixWorld(true);
  ghost.matrixAutoUpdate=false;
  ghost.matrix.copy(mesh.matrixWorld);
  ghost.userData.atelierHelper=true;
  ghost.name='Temporary precision bowling-hole mesh preview';
  world.add(ghost);
  mesh.visible=false;
  atelierBowlingDraft={candidate,originalId:part.id,baseline:JSON.stringify(part),sourceMesh:mesh,ghost};
  el('Status').textContent=made.holes+' real rounded holes · '+made.vertices+
   ' vertices, '+made.triangles+' triangles. Original hidden only for comparison. Apply to replace; Undo restores it.';
  status('Previewing true circular drilled openings. Inspect the hollow interiors before applying.');
 });
 el('Apply').addEventListener('click',()=>{
  const draft=atelierBowlingDraft,part=partById(selection);
  if(!draft||!part||part.id!==draft.originalId||JSON.stringify(part)!==draft.baseline){
   status('Preview the current unchanged sphere before applying.',true);return;
  }
  if(!checkPart(draft.candidate)){status('Hole geometry validation failed.',true);return;}
  const idx=model().parts.findIndex(p=>p.id===part.id);
  if(idx<0)return;
  atelierBowlingClear();
  checkpoint();
  model().parts[idx]=draft.candidate;
  signalEdited();select(draft.candidate.id);
  el('Status').textContent='Real round holes saved in indexed topology. Undo restores the original sphere.';
  status('Created '+Number(el('Count').value)+' hollow round bowling-ball holes with rounded bottoms. Undo available.');
 });
}
