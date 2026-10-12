// Placement guides are temporary render objects in the native Play session.
// They use the collision footprint returned by stCanBuild, never saved actors.
const stPlacementGridState = {guide:null,created:0,disposed:0};

function stPlacementGridPositions(object, positions, indices = null) {
  let geometry = object.geometry, attribute=geometry.getAttribute('position');
  const matching = attribute?.count===positions.length/3 &&
    (indices ? geometry.index?.count===indices.length : !geometry.index);
  if (!matching) {
    // Replacing uploaded attributes without disposing their old geometry leaks
    // GPU buffers. Reuse matching arrays; dispose before changing their size.
    geometry.dispose(); geometry=object.geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
    geometry.setIndex(indices);
  } else {
    attribute.array.set(positions); attribute.needsUpdate=true;
    if (indices) {geometry.index.array.set(indices);geometry.index.needsUpdate=true;}
  }
  geometry.computeBoundingSphere();
}
function stPlacementGridPoint(x,z,lift) {
  return [x,terrainHeight(x,z)+lift,z];
}
function stPlacementGridLine(positions,a,b,lift) {
  const distance = Math.hypot(b[0]-a[0],b[1]-a[1]);
  const segments = Math.max(1,Math.ceil(distance/.3));
  for (let index=0;index<segments;index++) {
    for (const t of [index/segments,(index+1)/segments])
      positions.push(...stPlacementGridPoint(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,lift));
  }
}
function stPlacementGridCreate() {
  const root = new THREE.Group();
  root.name = 'Sheep Tag ground placement grid';
  root.userData.sheepTagPreview = true;
  const mesh = (name,opacity,order) => {
    const object = new THREE.Mesh(new THREE.BufferGeometry(),new THREE.MeshBasicMaterial({
      color:0x96ffd0,transparent:true,opacity,side:THREE.DoubleSide,
      depthWrite:false,depthTest:false,fog:false
    }));
    object.name = name; object.userData.sheepTagPreview = true; object.renderOrder = order;
    root.add(object); return object;
  };
  const lines = (name,opacity,order) => {
    const object = new THREE.LineSegments(new THREE.BufferGeometry(),new THREE.LineBasicMaterial({
      color:0x8cddd6,transparent:true,opacity,depthWrite:false,depthTest:false,fog:false
    }));
    object.name = name; object.userData.sheepTagPreview = true; object.renderOrder = order;
    root.add(object); return object;
  };
  const guide = {root,fill:mesh('Full building ground footprint',.2,101),
    grid:lines('Snapped ground placement grid',.55,102),
    ticks:lines('Fine placement boundary ticks',.82,103),
    boundary:mesh('Solid building footprint boundary',.98,104),cornerIndices:[]};
  scene.add(root); stPlacementGridState.guide = guide; stPlacementGridState.created++;
  return guide;
}
function stPlacementGridClear() {
  const guide = stPlacementGridState.guide; if (!guide) return;
  scene.remove(guide.root);
  for (const object of guide.root.children) {object.geometry.dispose(); object.material.dispose();}
  stPlacementGridState.guide = null; stPlacementGridState.disposed++;
}
function stPlacementGridUpdate() {
  const fit = stUi.placement;
  if (!stSession || !stUi.build || !stUi.preview || !fit?.corners?.length) {stPlacementGridClear(); return;}
  if (fit.corners.some(point => point.some(value => !Number.isFinite(value)))) {stPlacementGridClear(); return;}
  const guide = stPlacementGridState.guide || stPlacementGridCreate();
  const corners = fit.corners, snap = stUiRules().buildSnap || .15, gridStep = snap===3 ? 3 : .6;
  const width = Math.hypot(corners[1][0]-corners[0][0],corners[1][1]-corners[0][1]);
  const depth = Math.hypot(corners[3][0]-corners[0][0],corners[3][1]-corners[0][1]);
  const color = fit.ok ? 0x96ffd0 : 0xff7777;
  guide.kind = stUi.build; guide.valid = !!fit.ok; guide.snap = snap; guide.gridStep = gridStep;
  guide.fill.material.color.set(color); guide.boundary.material.color.set(color);
  guide.ticks.material.color.set(color); guide.grid.material.color.set(fit.ok ? 0x8cddd6 : 0xf5a39b);
  // The preview model and its ground guide agree with the actual build height.
  stUi.preview.position.y = terrainHeight(fit.x,fit.z);
  if (stUi.footprint) stUi.footprint.visible = false;

  const nx = Math.max(1,Math.ceil(width/.3)), nz = Math.max(1,Math.ceil(depth/.3));
  const fill = [], indices = [];
  for (let row=0;row<=nz;row++) for (let column=0;column<=nx;column++) {
    const u=column/nx,v=row/nz;
    fill.push(...stPlacementGridPoint(corners[0][0]+(corners[1][0]-corners[0][0])*u+(corners[3][0]-corners[0][0])*v,
      corners[0][1]+(corners[1][1]-corners[0][1])*u+(corners[3][1]-corners[0][1])*v,.038));
    if (column<nx&&row<nz) {
      const start=row*(nx+1)+column;
      indices.push(start,start+1,start+nx+1,start+1,start+nx+2,start+nx+1);
    }
  }
  guide.cornerIndices = [0,nx,nz*(nx+1)+nx,nz*(nx+1)];
  stPlacementGridPositions(guide.fill,fill,indices);

  // A mesh strip stays legible on phone GPUs, where native WebGL lines are one pixel.
  const boundary = [], tickPositions = [], thickness = .12;
  for (let edge=0;edge<4;edge++) {
    const a=corners[edge],b=corners[(edge+1)%4],dx=b[0]-a[0],dz=b[1]-a[1],length=Math.hypot(dx,dz);
    const normal=[-dz/length,dx/length],segments=Math.max(1,Math.ceil(length/.3));
    for (let index=0;index<segments;index++) {
      const p=[a[0]+dx*index/segments,a[1]+dz*index/segments];
      const q=[a[0]+dx*(index+1)/segments,a[1]+dz*(index+1)/segments];
      const p0=[p[0]-normal[0]*thickness/2,p[1]-normal[1]*thickness/2];
      const p1=[p[0]+normal[0]*thickness/2,p[1]+normal[1]*thickness/2];
      const q0=[q[0]-normal[0]*thickness/2,q[1]-normal[1]*thickness/2];
      const q1=[q[0]+normal[0]*thickness/2,q[1]+normal[1]*thickness/2];
      for (const point of [p0,p1,q0,p1,q1,q0]) boundary.push(...stPlacementGridPoint(...point,.072));
    }
    if (snap!==3) for (let index=1;index<Math.round(length/snap);index++) {
      const t=index*snap/length,p=[a[0]+dx*t,a[1]+dz*t];
      stPlacementGridLine(tickPositions,[p[0]-normal[0]*.11,p[1]-normal[1]*.11],
        [p[0]+normal[0]*.11,p[1]+normal[1]*.11],.066);
    }
  }
  stPlacementGridPositions(guide.boundary,boundary);
  stPlacementGridPositions(guide.ticks,tickPositions); guide.ticks.visible = snap!==3;

  const margin = snap===3 ? 3 : 1.2, bounds=stUiRules().bounds || 40;
  const minX=Math.max(-bounds,Math.floor((Math.min(...corners.map(p=>p[0]))-margin)/gridStep)*gridStep);
  const maxX=Math.min(bounds,Math.ceil((Math.max(...corners.map(p=>p[0]))+margin)/gridStep)*gridStep);
  const minZ=Math.max(-bounds,Math.floor((Math.min(...corners.map(p=>p[1]))-margin)/gridStep)*gridStep);
  const maxZ=Math.min(bounds,Math.ceil((Math.max(...corners.map(p=>p[1]))+margin)/gridStep)*gridStep);
  const grid = [];
  for (let x=Math.ceil(minX/gridStep)*gridStep;x<=maxX+1e-7;x+=gridStep)
    stPlacementGridLine(grid,[x,minZ],[x,maxZ],.052);
  for (let z=Math.ceil(minZ/gridStep)*gridStep;z<=maxZ+1e-7;z+=gridStep)
    stPlacementGridLine(grid,[minX,z],[maxX,z],.052);
  stPlacementGridPositions(guide.grid,grid);
  guide.root.visible = true;
}

function stPlacementGridVisibleSite(fit) {
  const rect = $('viewport').getBoundingClientRect();
  return fit.corners.every(([x,z]) => {
    const point = new THREE.Vector3(x,terrainHeight(x,z)+.08,z).project(camera);
    if (point.z<-1||point.z>1||Math.abs(point.x)>1||Math.abs(point.y)>1) return false;
    const target = document.elementFromPoint(rect.left+(point.x+1)*rect.width/2,rect.top+(1-point.y)*rect.height/2);
    return target===renderer.domElement;
  });
}
function stPlacementGridSeed() {
  const state = stUiView(), unit=state.units.find(item=>item.id===state.controlledId);
  if (!stUi.build||!unit?.pos) return;
  // No hover exists on a phone. Give the player a visible, nearby guide as soon
  // as they choose a building; only their subsequent ground tap places it.
  const centers = [[unit.pos[0],unit.pos[2]],[stUi.focus.x,stUi.focus.z]];
  let fallback = null;
  for (const [baseX,baseZ] of centers) for (const distance of [4.2,6,8.4,10.2]) {
    for (const [dx,dz] of [[1,-.5],[-1,-.5],[0,-1],[1,0],[-1,0],[1,1],[-1,1],[0,1]]) {
      const point=new THREE.Vector3(baseX+dx*distance,0,baseZ+dz*distance);
      const fit=stCanBuild(stUi.build,point.x,point.z,state.controlledId,stUi.rotation);
      if (!stPlacementGridVisibleSite(fit)) continue;
      fallback ||= point;
      if (fit.ok) {stUiPlacePreview(point); return;}
    }
  }
  stUiPlacePreview(fallback || new THREE.Vector3(unit.pos[0],0,unit.pos[2]-4.2));
}
function stPlacementGridStatus() {
  const guide=stPlacementGridState.guide; if (!guide) return null;
  const attribute=guide.fill.geometry.getAttribute('position');
  const corners=guide.cornerIndices.map(index=>[attribute.getX(index),attribute.getZ(index)]);
  const width=Math.hypot(corners[1][0]-corners[0][0],corners[1][1]-corners[0][1]);
  const depth=Math.hypot(corners[3][0]-corners[0][0],corners[3][1]-corners[0][1]);
  const objects=guide.root.children.map(object=>({name:object.name,type:object.type,visible:object.visible,
    vertices:object.geometry.getAttribute('position')?.count||0,color:object.material.color.getHexString(),
    opacity:object.material.opacity,transparent:object.material.transparent,
    depthWrite:object.material.depthWrite,parented:object.parent===guide.root}));
  const terrainConforming=guide.root.children.every(object=>{
    const positions=object.geometry.getAttribute('position');
    for(let index=0;index<(positions?.count||0);index++) {
      const lift=positions.getY(index)-terrainHeight(positions.getX(index),positions.getZ(index));
      if(lift<.03||lift>.085) return false;
    }
    return true;
  });
  return {visible:guide.root.visible&&guide.root.parent===scene,kind:guide.kind,valid:guide.valid,
    snap:guide.snap,gridStep:guide.gridStep,center:[(corners[0][0]+corners[2][0])/2,(corners[0][1]+corners[2][1])/2],
    corners,width,depth,fillVertices:attribute.count,boundaryVertices:guide.boundary.geometry.getAttribute('position').count,
    gridVertices:guide.grid.geometry.getAttribute('position').count,tickVertices:guide.ticks.geometry.getAttribute('position').count,
    fillColor:guide.fill.material.color.getHexString(),boundaryColor:guide.boundary.material.color.getHexString(),
    gridColor:guide.grid.material.color.getHexString(),terrainConforming,objects};
}

const stPlacementGridOriginalClear = stUiClearPreview;
stUiClearPreview = function() {stPlacementGridClear(); return stPlacementGridOriginalClear();};
const stPlacementGridOriginalPreview = stUiPlacePreview;
stUiPlacePreview = function(point) {const result=stPlacementGridOriginalPreview(point); stPlacementGridUpdate(); return result;};
const stPlacementGridOriginalChoose = stUiChooseBuild;
stUiChooseBuild = function(kind) {const result=stPlacementGridOriginalChoose(kind); if(stUi.build)stPlacementGridSeed(); return result;};
const stPlacementGridOriginalStatus = stUiStatus;
stUiStatus = function() {return {...stPlacementGridOriginalStatus(),placementGrid:stPlacementGridStatus(),
  placementGridResources:{created:stPlacementGridState.created,disposed:stPlacementGridState.disposed,
    live:stPlacementGridState.guide?1:0}};};
