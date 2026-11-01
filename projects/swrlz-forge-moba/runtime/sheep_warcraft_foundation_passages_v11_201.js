// §E v11.201 — Warcraft-like Sheep Tag foundations and truthful passage guides.
// Presentation only: native stCanBuild, stSegmentClear, unit radii, fog and
// gameplay remain authoritative. No extra renderer loop or saved actor state.
const st201={
  root:null,preview:null,previewKey:'',baseKey:'',baseRebuilds:0,
  previewRebuilds:0,resourcesDisposed:0,gapCount:0,previewGaps:[],
  visualLimit:36
};
function st201World(fp,x,z){
 const c=Math.cos(fp.rotation||0),s=Math.sin(fp.rotation||0);
 return [fp.x+x*c+z*s,fp.z-x*s+z*c];
}
function st201Vertex(target,x,z,lift){
 target.push(x,terrainHeight(x,z)+lift,z);
}
function st201Tri(target,a,b,c,lift){
 st201Vertex(target,a[0],a[1],lift);
 st201Vertex(target,b[0],b[1],lift);
 st201Vertex(target,c[0],c[1],lift);
}
function st201Quad(target,a,b,c,d,lift){
 st201Tri(target,a,b,c,lift);st201Tri(target,b,d,c,lift);
}
function st201Ribbon(target,fp,p,q,inner,outer,lift,step=.38){
 const n=Math.max(1,Math.ceil(Math.hypot(q[0]-p[0],q[1]-p[1])/step));
 for(let j=0;j<n;j++){
  const a=j/n,b=(j+1)/n;
  const local=t=>[p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t];
  const v=local(a),w=local(b);
  st201Quad(target,st201World(fp,v[0]+inner[0],v[1]+inner[1]),
   st201World(fp,v[0]+outer[0],v[1]+outer[1]),
   st201World(fp,w[0]+inner[0],w[1]+inner[1]),
   st201World(fp,w[0]+outer[0],w[1]+outer[1]),lift);
 }
}
function st201Foundation(fp,fill,edge,buffer,trim,sheepRadius){
 const x=fp.localHalfX??fp.halfX,z=fp.localHalfZ??fp.halfZ;
 if(!(x>.02&&z>.02))return;
 // Exact native blocking rectangle: the solid edge is NOT rounded away.
 // Only the inset decorative foundation is softened at the corners.
 const corners=[
  [[-x,-z],[x,-z],[0,1],[0,-1]],
  [[x,-z],[x,z],[-1,0],[1,0]],
  [[x,z],[-x,z],[0,-1],[0,1]],
  [[-x,z],[-x,-z],[1,0],[-1,0]]
 ];
 const stop=Math.max(.01,Number(sheepRadius)||.27);
 for(const [a,b,inward,outward] of corners){
  st201Ribbon(edge,fp,a,b,[0,0],[inward[0]*.073,inward[1]*.073],.091);
  st201Ribbon(buffer,fp,a,b,[0,0],[outward[0]*stop,outward[1]*stop],.05,.42);
 }
 const inset=Math.min(.21,x*.22,z*.22),radius=Math.min(.25,x*.3,z*.3);
 const ix=x-inset,iz=z-inset,r=Math.min(radius,ix*.45,iz*.45);
 const polygon=[[-ix+r,-iz],[ix-r,-iz],[ix,-iz+r],[ix,iz-r],
  [ix-r,iz],[-ix+r,iz],[-ix,iz-r],[-ix,-iz+r]];
 for(let i=0;i<polygon.length;i++)
  st201Tri(fill,st201World(fp,0,0),
    st201World(fp,polygon[i][0],polygon[i][1]),
    st201World(fp,polygon[(i+1)%polygon.length][0],
      polygon[(i+1)%polygon.length][1]),.045);
 // Separate, thin interior trim accents, with no added physical collision.
 for(const [a,b,inward] of corners)
  st201Ribbon(trim,fp,a,b,
   [inward[0]*.12,inward[1]*.12],
   [inward[0]*.15,inward[1]*.15],.08,.55);
}
function st201GapState(gap){
 if(!gap?.sheep)return 'blocked';
 return gap.width>=stSafeLaneWidth()+.35?'clear':'tight';
}
function st201GapMesh(gap,byState,lift=.079){
 if(!Number.isFinite(gap.x)||!Number.isFinite(gap.z)||
    !(gap.width>.028&&gap.length>.26))return false;
 const x=gap.axis==='x'?Math.max(.035,gap.width-.035):Math.max(.10,gap.length-.10);
 const z=gap.axis==='z'?Math.max(.035,gap.width-.035):Math.max(.10,gap.length-.10);
 const cx=gap.x,cz=gap.z,a=[cx-x/2,cz-z/2],b=[cx+x/2,cz-z/2],
   c=[cx-x/2,cz+z/2],d=[cx+x/2,cz+z/2];
 st201Quad(byState[st201GapState(gap)],a,b,c,d,lift);
 return true;
}
function st201Mesh(root,name,color,opacity,order){
 const mesh=new THREE.Mesh(new THREE.BufferGeometry(),new THREE.MeshBasicMaterial({
  color,transparent:true,opacity,depthTest:true,depthWrite:false,
  side:THREE.DoubleSide,fog:false,polygonOffset:true,
  polygonOffsetFactor:-1,polygonOffsetUnits:-1
 }));
 mesh.name=name;mesh.userData.sheepTagPreview=true;mesh.renderOrder=order;
 root.add(mesh);return mesh;
}
function st201Geometry(mesh,positions){
 const existing=mesh.geometry.getAttribute('position');
 if(existing&&existing.count===positions.length/3){
  existing.array.set(positions);existing.needsUpdate=true;
 }else{
  const old=mesh.geometry;
  mesh.geometry=new THREE.BufferGeometry();
  mesh.geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  old.dispose();
 }
 if(positions.length)mesh.geometry.computeBoundingSphere();
 mesh.visible=positions.length>0;
}
function st201Groups(name){
 const root=new THREE.Group();
 root.name=name;root.userData.sheepTagPreview=true;
 const meshes={
  buffer:st201Mesh(root,'Sheep center-stop cushion',0xb99c74,.16,85),
  foundation:st201Mesh(root,'Rounded warm foundation',0x3f594b,.38,86),
  trim:st201Mesh(root,'Subtle inset foundation trim',0x9dbbac,.47,87),
  edge:st201Mesh(root,'Exact solid building boundary',0xe5d59d,.89,88),
  clear:st201Mesh(root,'Sheep traversable lane',0x48d5a3,.38,89),
  tight:st201Mesh(root,'Sheep tight but passable lane',0xffcf74,.43,89),
  blocked:st201Mesh(root,'Blocked narrow lane',0xec6d68,.45,89)
 };
 root.userData.meshes=meshes;scene.add(root);
 return root;
}
function st201DisposeRoot(root){
 if(!root)return;
 scene.remove(root);
 root.traverse(node=>{node.geometry?.dispose();node.material?.dispose();});
 st201.resourcesDisposed++;
}
function st201ConvertBuilding(b){
 return {...b,pos:new THREE.Vector3(...b.pos)};
}
function st201CollectGaps(houses,focus,maxPairs=st201.visualLimit){
 const nearby=houses.filter(b=>Math.hypot(b.pos.x-focus[0],b.pos.z-focus[2])<25)
   .sort((a,b)=>Math.hypot(a.pos.x-focus[0],a.pos.z-focus[2])-
                Math.hypot(b.pos.x-focus[0],b.pos.z-focus[2]))
   .slice(0,maxPairs),gaps=[];
 for(let i=0;i<nearby.length;i++)for(let j=i+1;j<nearby.length;j++){
  const a=nearby[i],b=nearby[j];
  if(Math.abs(a.pos.x-b.pos.x)>9||Math.abs(a.pos.z-b.pos.z)>9)continue;
  const gap=stClarityGap(a,b,houses,stSession.rules);
  if(gap&&gap.width>.028&&gap.length>.26)gaps.push(gap);
 }
 return gaps;
}
// Override only the old hard-edged permanent foundation renderer. The outer
// rectangle is always the same collision footprint as the game, while inset
// corners are aesthetic. Geometry is batched, rebuilt on navigation changes.
stClarityUpdateOverlay=function(state){
 if(!stSession||!stUi.shown||!state)return;
 const visible=(state.buildings||[]).filter(b=>ST_LANE_HOUSES.has(b.kind));
 const focus=state.buildings.find(b=>b.id===state.selectedId)?.pos||
  state.units.find(u=>u.controlled)?.pos||[stUi.focus.x,0,stUi.focus.z];
 const nearby=visible.filter(b=>Math.hypot(b.pos[0]-focus[0],b.pos[2]-focus[2])<25)
  .map(b=>b.id).join(',');
 const key=[stSession,stSession.navVersion,nearby,visible.map(b=>
  b.id+':'+b.kind+':'+b.rotation+':'+b.halfX+':'+b.halfZ).join(','),
  stUnitRadius('sheep'),state.role,stHuntReleased()].join('|');
 if(key===st201.baseKey&&stClarityOverlay){
  stClarityPositionLabel(focus);return;
 }
 stClarityDisposeOverlay();
 st201.baseKey=key;stClarityOverlayKey=key;
 const root=st201Groups('Sheep Tag smooth house foundations and honest paths');
 st201.root=root;stClarityOverlay=root;st201.baseRebuilds++;
 const boxes={foundation:[],edge:[],buffer:[],trim:[],clear:[],tight:[],blocked:[]};
 const converted=visible.map(st201ConvertBuilding),radius=stUnitRadius('sheep');
 for(const b of converted){
  const fp=stBuildingObstacle(b);
  st201Foundation(fp,boxes.foundation,boxes.edge,boxes.buffer,boxes.trim,radius);
 }
 const gaps=st201CollectGaps(converted,focus);
 for(const gap of gaps)st201GapMesh(gap,boxes);
 st201.gapCount=gaps.length;root.userData.gaps=gaps;
 for(const [kind,mesh] of Object.entries(root.userData.meshes))
  st201Geometry(mesh,boxes[kind]);
 // Sanctuary perimeter remains a world-space scene guide, never a saved actor.
 const pen=stSession.pen,rad=stSanctuaryRadius();
 const points=Array.from({length:80},(_,i)=>{
  const angle=i*Math.PI/40;
  const x=pen.x+Math.cos(angle)*rad,z=pen.z+Math.sin(angle)*rad;
  return new THREE.Vector3(x,terrainHeight(x,z)+.085,z);
 });
 const ring=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points),
  new THREE.LineBasicMaterial({color:0xe5c66a,transparent:true,opacity:.67,
   depthWrite:false,depthTest:true}));
 ring.name='Existing sanctuary no-build perimeter';
 ring.userData.sheepTagPreview=true;ring.renderOrder=90;root.add(ring);
 const legend=document.createElement('div');
 legend.id='stClearanceLegend';
 legend.style.cssText='position:fixed;left:12px;top:112px;'+
 'max-width:min(350px,calc(100vw - 45px));padding:5px 9px;'+
 'border:1px solid #8f9d8c;border-radius:9px;'+
 'background:#162921dd;color:#f0f2e4;z-index:39;'+
 'font:11px/1.4 system-ui;pointer-events:none';
 legend.textContent='Foundation edge: solid · Soft rim: sheep stopping distance · '+
  'Teal: clear · Amber: tight · Red: blocked · Passage '+stSafeLaneWidth().toFixed(2)+' m minimum.';
 document.body.append(legend);
 stClarityPositionLabel(focus);stClarityPositionLegend();
};
// When a building ghost moves, sample only visible nearby houses. The sampled
// preview is a temporary obstacle in stClarityGap's exact swept collision test.
function st201PreviewUpdate(){
 const fit=stUi.placement;
 if(!stSession||!stUi.build||!stUi.preview||!fit?.corners?.length||
   !Number.isFinite(fit.x)||!Number.isFinite(fit.z)){
  st201PreviewDispose();return;
 }
 const visible=(stUiView().buildings||[]).filter(b=>ST_LANE_HOUSES.has(b.kind));
 const key=[stSession,stUi.build,fit.x,fit.z,fit.rotation,fit.ok,
   stSession.navVersion,visible.map(b=>b.id+':'+b.kind).join(',')].join('|');
 if(key===st201.previewKey&&st201.preview)return;
 if(!st201.preview)st201.preview=st201Groups('Sheep Tag live sheep-width lane preview');
 st201.previewKey=key;
 st201.previewRebuilds++;
 const meshes=st201.preview.userData.meshes,boxes={
  foundation:[],edge:[],buffer:[],trim:[],clear:[],tight:[],blocked:[]};
 const fp={x:fit.x,z:fit.z,rotation:fit.rotation||0,
   localHalfX:fit.localHalfX??1.2,localHalfZ:fit.localHalfZ??1.2};
 st201Foundation(fp,boxes.foundation,boxes.edge,boxes.buffer,boxes.trim,stUnitRadius('sheep'));
 // The native placement grid already draws the solid preview boundary.
 // This outer clearance rim reveals how close a sheep center may run.
 boxes.foundation.length=0;boxes.edge.length=0;boxes.trim.length=0;
 const preview={id:'st201-placement-only',kind:fit.kind,
  pos:new THREE.Vector3(fit.x,0,fit.z),halfX:fit.halfX,halfZ:fit.halfZ,
  localHalfX:fp.localHalfX,localHalfZ:fp.localHalfZ,
  rotation:fp.rotation,hp:1};
 const close=visible.filter(b=>Math.hypot(b.pos[0]-fit.x,b.pos[2]-fit.z)<9)
  .slice(0,18).map(st201ConvertBuilding),context=[...close,preview];
 const gaps=[];
 for(const house of close){
  const gap=stClarityGap(house,preview,context,stSession.rules);
  if(gap&&gap.width>.028&&gap.length>.26)gaps.push(gap);
 }
 gaps.sort((a,b)=>Math.hypot(a.x-fit.x,a.z-fit.z)-Math.hypot(b.x-fit.x,b.z-fit.z));
 const shown=gaps.slice(0,5);
 for(const g of shown)st201GapMesh(g,boxes,.12);
 st201.previewGaps=shown.map(g=>({width:g.width,axis:g.axis,
  sheep:!!g.sheep,state:st201GapState(g)}));
 for(const [kind,mesh] of Object.entries(meshes))st201Geometry(mesh,boxes[kind]);
 // Keep existing fine/coarse snap coordinates, but mute the noisy ground grid.
 const grid=stPlacementGridState.guide;
 if(grid){
  grid.grid.material.opacity=grid.snap===3?.30:.16;
  grid.ticks.material.opacity=.25;
  grid.fill.material.opacity=.17;
  grid.boundary.material.opacity=.88;
 }
}
function st201PreviewDispose(){
 if(st201.preview)st201DisposeRoot(st201.preview);
 st201.preview=null;st201.previewKey='';st201.previewGaps=[];
}
const st201OldPreview=stUiPlacePreview;
stUiPlacePreview=function(point){
 const result=st201OldPreview(point);st201PreviewUpdate();return result;
};
const st201OldClear=stUiClearPreview;
stUiClearPreview=function(){
 st201PreviewDispose();return st201OldClear();
};
window.SWYRL_ENGINE_SHEEP_WARCRAFT_FOOTPRINTS_201=Object.freeze({
 diagnose:()=>({
  active:!!stClarityOverlay,previewActive:!!st201.preview,
  permanentRebuilds:st201.baseRebuilds,previewRebuilds:st201.previewRebuilds,
  disposed:st201.resourcesDisposed,shownPermanentGaps:st201.gapCount,
  previewGaps:st201.previewGaps.slice(),
  nativeSheepRadius:stSession?stUnitRadius('sheep'):null,
  safeLane:stSession?stSafeLaneWidth():null
 })
});
