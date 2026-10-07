"""Native gallery assets and height-aware walking on project-owned surfaces.

Apply after the v8.0 primitive, layer integrity, and workspace patches. This
module changes engine capabilities only; projects choose their own geometry.
"""


def _once(html, old, new):
    if html.count(old) != 1:
        raise RuntimeError("walkable levels expected one anchor: " + old[:120])
    return html.replace(old, new, 1)


GEOMETRY = r"""
  if(kind==='ramp'){
    // Actor origin is the low landing's height. North (-Z) is the ascent.
    // A thin slab leaves the space underneath usable, unlike a solid wedge.
    const vertices=[-1.5,0,5,1.5,0,5,1.5,3.4,-5,-1.5,3.4,-5,
      -1.5,-.18,5,1.5,-.18,5,1.5,3.22,-5,-1.5,3.22,-5];
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
    geometry.setIndex([0,1,2,0,2,3,4,6,5,4,7,6,0,4,5,0,5,1,
      1,5,6,1,6,2,2,6,7,2,7,3,3,7,4,3,4,0]);
    // Non-indexed faces keep the flat top normal independent of the edges.
    const flat=geometry.toNonIndexed();geometry.dispose();flat.computeVertexNormals();
    const slab=new THREE.Mesh(flat,concrete);slab.castShadow=slab.receiveShadow=true;g.add(slab);
  }else if(kind==='galleryDeck'){
    // Scaling in X/Z controls the deck footprint; actor Y is its finished top.
    box(1,.18,1,stone,0,-.09,0);
  }else if(kind==='galleryRail'){
    // Local X is the run; rotate around Y for rails along local Z.
    for(const x of [-.48,.48])box(.12,1.05,.12,stone,x,.525,0);
    box(1,.09,.12,concrete,0,1.005,0);box(1,.065,.08,arcane,0,.52,0);
  }else
"""


SUPPORT = r"""
// Walking support is explicitly tagged: decorative props never become floors.
// Heights are world-space feet heights, including the small ground clearance.
const walkingSurfaceRay=new THREE.Raycaster();
const walkingSurfaceDown=new THREE.Vector3(0,-1,0);
const walkingSurfaceNormal=new THREE.Vector3();
const walkingSurfaceNormalMatrix=new THREE.Matrix3();
const walkingSurfaceOrigin=new THREE.Vector3();
const walkingBlockerBounds=new THREE.Box3();
const walkingRailInverse=new THREE.Matrix4();
const walkingRailLocal=new THREE.Vector3();
const walkingRailHead=new THREE.Vector3();
const walkingRailScale=new THREE.Vector3();
const walkingRailBounds=new THREE.Box3(new THREE.Vector3(-.54,0,-.06),new THREE.Vector3(.54,1.05,.06));
let physicalContactFrameActive=false,physicalContactFrameId=0,physicalContactSnapshot=null;
const physicalContactBoundsCache=new WeakMap();
function beginPhysicalContactFrame(){
  physicalContactFrameActive=true;physicalContactFrameId++;physicalContactSnapshot=null;
  scene.updateMatrixWorld(true);
}
function endPhysicalContactFrame(){physicalContactFrameActive=false;physicalContactSnapshot=null;}
function walkingObjectVisible(object){
  for(let p=object;p;p=p.parent)if(p.visible===false)return false;
  return true;
}
function walkingPhysicalMesh(object){
  if(!object.isMesh)return false;
  for(let p=object;p;p=p.parent)if(p.visible===false||p.userData.editorOnly||p.userData.helper)return false;
  return true;
}
function physicalContactMeshes(){
  if(physicalContactFrameActive&&physicalContactSnapshot)return physicalContactSnapshot;
  const meshes=[],seen=new Set();
  if(!physicalContactFrameActive)scene.updateMatrixWorld(true);
  for(const actor of actors){
    if(!walkingObjectVisible(actor)||['dragon','hero'].includes(actor.userData.actorType))continue;
    actor.traverse(node=>{
      if(seen.has(node)||!walkingPhysicalMesh(node))return;
      for(let p=node;p;p=p.parent)if(['dragon','hero'].includes(p.userData.actorType))return;
      seen.add(node);meshes.push(node);
    });
  }
  if(physicalContactFrameActive)physicalContactSnapshot=meshes;
  return meshes;
}
function physicalContactWorldBounds(mesh){
  // Animated and instanced geometry needs its own dynamic bounds; preserve
  // its existing narrow-phase behavior rather than assuming a static slab.
  if(mesh.isSkinnedMesh||mesh.isInstancedMesh||mesh.morphTargetInfluences?.some(v=>v!==0))return null;
  const geometry=mesh.geometry,position=geometry?.attributes?.position;if(!position)return null;
  let cached=physicalContactBoundsCache.get(mesh);
  if(cached&&physicalContactFrameActive&&cached.frame===physicalContactFrameId)return cached.bounds;
  const elements=mesh.matrixWorld.elements,version=position.version;
  let changed=!cached||cached.geometry!==geometry||cached.version!==version;
  if(!changed)for(let i=0;i<16;i++)if(cached.matrix[i]!==elements[i]){changed=true;break;}
  if(changed){
    if(!cached||cached.geometry!==geometry||cached.version!==version||!geometry.boundingBox)geometry.computeBoundingBox();
    if(!cached)cached={bounds:new THREE.Box3(),matrix:new Array(16)};
    cached.bounds.copy(geometry.boundingBox).applyMatrix4(mesh.matrixWorld);
    for(let i=0;i<16;i++)cached.matrix[i]=elements[i];
    cached.geometry=geometry;cached.version=version;physicalContactBoundsCache.set(mesh,cached);
  }
  cached.frame=physicalContactFrameActive?physicalContactFrameId:-1;
  return cached.bounds;
}
function physicalContactRayCandidates(meshes,origin,far){
  // A vertical ray cannot hit meshes outside its X/Z column or Y interval.
  // Bounds are conservative; the real triangle raycast still decides contact.
  const candidates=[],epsilon=.00001;
  for(const mesh of meshes){
    const b=physicalContactWorldBounds(mesh);if(!b){candidates.push(mesh);continue;}
    if(origin.x>=b.min.x-epsilon&&origin.x<=b.max.x+epsilon&&origin.z>=b.min.z-epsilon&&origin.z<=b.max.z+epsilon&&origin.y>=b.min.y-epsilon&&origin.y-far<=b.max.y+epsilon)candidates.push(mesh);
  }
  return candidates;
}
function walkingSurfaceActors(){
  return actors.filter(a=>a.userData.baked&&(a.userData.tags||[]).includes('walkable-surface')&&walkingObjectVisible(a));
}
function walkingSupportY(x,z,maxFeetY){
  let support=terrainHeight(x,z)+HERO_GROUND_OFFSET;
  if(!Number.isFinite(maxFeetY))return support;
  const surfaces=walkingSurfaceActors();if(!surfaces.length)return support;
  const meshes=[];
  for(const a of surfaces){
    a.updateWorldMatrix(true,true);
    a.traverse(node=>{if(walkingPhysicalMesh(node))meshes.push(node);});
  }
  if(!meshes.length)return support;
  walkingSurfaceOrigin.set(x,maxFeetY+.04,z);
  walkingSurfaceRay.set(walkingSurfaceOrigin,walkingSurfaceDown);
  walkingSurfaceRay.near=0;walkingSurfaceRay.far=Math.max(.1,maxFeetY-support+.2);
  // Station labels are Sprites and need a camera to raycast. Only physical
  // meshes can support feet, so never recurse into labels or editor helpers.
  const hits=walkingSurfaceRay.intersectObjects(physicalContactRayCandidates(meshes,walkingSurfaceOrigin,walkingSurfaceRay.far),false);
  for(const hit of hits){
    if(!hit.face||!walkingObjectVisible(hit.object))continue;
    walkingSurfaceNormal.copy(hit.face.normal).applyMatrix3(walkingSurfaceNormalMatrix.getNormalMatrix(hit.object.matrixWorld)).normalize();
    if(walkingSurfaceNormal.y<.45)continue;
    const feet=hit.point.y+HERO_GROUND_OFFSET;
    if(feet<=maxFeetY+.001&&feet>support)support=feet;
  }
  return support;
}
function settleWalkingHero(h,dt){
  if(heroJumpQueued&&heroGrounded){heroVel.y=6.5;heroGrounded=false;}
  heroJumpQueued=false;
  const previousY=h.position.y;
  if(heroGrounded&&heroVel.y<=0){
    const support=walkingSupportY(h.position.x,h.position.z,previousY+.32);
    // Follow modest downward steps; leaving a gallery starts an actual fall.
    if(previousY-support<=.65){h.position.y=support;heroVel.y=0;return;}
    heroGrounded=false;
  }
  heroVel.y-=14*dt;
  const nextY=previousY+heroVel.y*dt;
  if(heroVel.y<=0){
    // Only land on a top crossed this frame. A bridge above the player is
    // never selected, even when the player walks or jumps underneath it.
    const support=walkingSupportY(h.position.x,h.position.z,previousY+.015);
    if(nextY<=support){h.position.y=support;heroVel.y=0;heroGrounded=true;return;}
  }
  h.position.y=nextY;heroGrounded=false;
}
function resolveWalkingRails(pos,radius,h){
  const height=(h.userData.eyeHeight||FP_EYE_HEIGHT)+.18;
  for(const rail of actors){
    if(!rail.userData.baked||!(rail.userData.tags||[]).includes('guardrail')||!walkingObjectVisible(rail))continue;
    rail.updateWorldMatrix(true,true);
    walkingBlockerBounds.setFromObject(rail);
    if(pos.y+height<=walkingBlockerBounds.min.y||pos.y>=walkingBlockerBounds.max.y)continue;
    walkingRailInverse.copy(rail.matrixWorld).invert();
    walkingRailLocal.copy(pos).applyMatrix4(walkingRailInverse);
    walkingRailHead.set(pos.x,pos.y+height,pos.z).applyMatrix4(walkingRailInverse);
    if(Math.max(walkingRailLocal.y,walkingRailHead.y)<=walkingRailBounds.min.y||Math.min(walkingRailLocal.y,walkingRailHead.y)>=walkingRailBounds.max.y)continue;
    rail.getWorldScale(walkingRailScale);
    const rx=radius/Math.max(.001,Math.abs(walkingRailScale.x)),rz=radius/Math.max(.001,Math.abs(walkingRailScale.z));
    const minX=walkingRailBounds.min.x-rx,maxX=walkingRailBounds.max.x+rx,minZ=walkingRailBounds.min.z-rz,maxZ=walkingRailBounds.max.z+rz;
    const p=walkingRailLocal;
    if(p.x<=minX||p.x>=maxX||p.z<=minZ||p.z>=maxZ)continue;
    const penetrations=[p.x-minX,maxX-p.x,p.z-minZ,maxZ-p.z];
    let side=0;for(let i=1;i<4;i++)if(penetrations[i]<penetrations[side])side=i;
    if(side===0)p.x=minX-.001;else if(side===1)p.x=maxX+.001;else if(side===2)p.z=minZ-.001;else p.z=maxZ+.001;
    p.applyMatrix4(rail.matrixWorld);pos.x=p.x;pos.z=p.z;
  }
}
"""


HERO_COLLISION = r"""function resolveHeroCollision(pos,radius){
  const h=heroActor();if(!h)return;
  const height=(h.userData.eyeHeight||FP_EYE_HEIGHT)+.18,wp=new THREE.Vector3();
  for(const b of blockerActors()){
    if(b===h||!walkingObjectVisible(b))continue;
    b.updateWorldMatrix(true,true);walkingBlockerBounds.setFromObject(b);
    // An elevated perch's broad X/Z circle must not block the floor below it.
    if(pos.y+height<=walkingBlockerBounds.min.y||pos.y>=walkingBlockerBounds.max.y)continue;
    worldPos(b,wp);const dx=pos.x-wp.x,dz=pos.z-wp.z,dist=Math.hypot(dx,dz),min=radius+worldColliderRadius(b);
    if(dist<min){if(dist>.0001){const push=min-dist;pos.x+=dx/dist*push;pos.z+=dz/dist*push;}else pos.x+=min;}
  }
  resolveWalkingRails(pos,radius,h);
}"""


def apply(html):
    s = _once(html, "  if(kind==='ceiling'){", GEOMETRY + "  if(kind==='ceiling'){")
    s = _once(s, "tags:['dragon-den','architecture',kind]", "tags:['dragon-den','architecture',kind].concat(['ramp','galleryDeck'].includes(kind)?['walkable-surface']:kind==='galleryRail'?['guardrail']:[])")
    s = _once(s, "  if(type==='denWorkbench')", """  if(type==='denRamp')o=makeDenStructure('ramp',[0,0,0],false,'Gallery Ramp','#85cfe0');
  if(type==='denGalleryDeck')o=makeDenStructure('galleryDeck',[0,0,0],false,'Gallery Deck','#85cfe0');
  if(type==='denGalleryRail')o=makeDenStructure('galleryRail',[0,0,0],false,'Gallery Guardrail','#85cfe0');
  if(type==='denWorkbench')""")
    s = _once(s, "const ASSET_LIBRARY=[", """const ASSET_LIBRARY=[
  {id:'denRamp',name:'Gallery Ramp',path:'/Engine/Architecture',desc:'Walkable 3m-wide ramp: rises 3.4m over 10m toward local -Z'},
  {id:'denGalleryDeck',name:'Gallery Deck',path:'/Engine/Architecture',desc:'Walkable unit slab; actor height is the finished deck top'},
  {id:'denGalleryRail',name:'Gallery Guardrail',path:'/Engine/Architecture',desc:'Height-aware 1m rail; scale X for length, rotate Y for direction'},""")
    s = _once(s, "function beginPlay(fromHere=null){", SUPPORT + "\nfunction beginPlay(fromHere=null){")
    s = _once(s, "    if(fromHere){h.position.x=fromHere.x;h.position.z=fromHere.z;}\n    h.position.y=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET;", """    const requestedFeetY=fromHere?fromHere.y:h.position.y;
    if(fromHere){h.position.x=fromHere.x;h.position.z=fromHere.z;}
    h.position.y=h.userData.hoverFlight?terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET:walkingSupportY(h.position.x,h.position.z,requestedFeetY+.32);""")
    s = _once(s, "beginPlay(selected.position.clone());", "beginPlay(selected.getWorldPosition(new THREE.Vector3()));")
    s = _once(s, "function resolveHeroCollision(pos,radius){resolveCircleCollision(pos,radius,heroActor());}", HERO_COLLISION)
    # Procedural dragon feet use a legacy generic prop raycast. Workstation
    # labels now accompany those props, so use physical meshes here as well.
    s = _once(s, """  const solids=actors.filter(a=>a!==dragon&&a.visible!==false&&a.userData.actorType!=='dragon'&&a.userData.actorType!=='hero');
  const hits=dragonContactRay.intersectObjects(solids,true);""", """  const meshes=physicalContactRayCandidates(physicalContactMeshes(),origin,dragonContactRay.far);
  const hits=dragonContactRay.intersectObjects(meshes,false);""")
    # This frame scope shares physical mesh traversal among all legacy foot
    # queries. Editor events cannot interleave synchronous frame callbacks.
    s = _once(s, "  updateWispVisuals(t);updateDragonRigs(t);updateDragonSurfaceContacts(dt);", "  beginPhysicalContactFrame();updateWispVisuals(t);updateDragonRigs(t);updateDragonSurfaceContacts(dt);endPhysicalContactFrame();")
    s = _once(s, "dragonFootRaycaster.intersectObjects(surfaces,false)[0]", "dragonFootRaycaster.intersectObjects(physicalContactRayCandidates(surfaces,dragonFootOrigin,dragonFootRaycaster.far),false)[0]")
    s = _once(s, "if(!o.isMesh||o.userData?.editorOnly||o.visible===false)return;", "if(!walkingPhysicalMesh(o))return;")
    s = _once(s, "  scene.updateMatrixWorld(true);dragon.updateMatrixWorld(true);", "  if(!physicalContactFrameActive)scene.updateMatrixWorld(true);dragon.updateMatrixWorld(true);")
    s = _once(s, """    if(heroJumpQueued&&heroGrounded){heroVel.y=6.5;heroGrounded=false;}heroJumpQueued=false;
    if(heroGrounded&&heroVel.y<=0&&(h.position.y-groundY)<=HERO_STEP_DOWN){h.position.y=groundY;heroVel.y=0;}
    else{heroVel.y-=14*dt;h.position.y+=heroVel.y*dt;if(h.position.y<=groundY){h.position.y=groundY;heroVel.y=0;heroGrounded=true;}else heroGrounded=false;}""", "    settleWalkingHero(h,dt);")
    return s
