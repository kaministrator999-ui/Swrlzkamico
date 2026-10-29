"""§wyrl§ Engine v5.6: detailed dragon wings + reusable foot contact grounding."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v5.6 patch token missing: " + old[:220])
    return s.replace(old, new, 1)

def _before(s: str, marker: str, block: str) -> str:
    i=s.find(marker)
    if i<0: raise RuntimeError("v5.6 insert marker missing: "+marker[:200])
    return s[:i]+block+s[i:]

def _replace_block(s: str, start: str, end: str, block: str) -> str:
    a=s.find(start)
    if a<0: raise RuntimeError("v5.6 block start missing: "+start[:200])
    b=s.find(end,a)
    if b<0: raise RuntimeError("v5.6 block end missing: "+end[:200])
    return s[:a]+block+s[b:]

def apply(html: str) -> str:
    s=html

    repl={
      "<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_5_DRAGONS_NATURAL_LOOK -->":"<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_6_DRAGON_GROUND_CONTACT -->",
      "<title>§wyrl§ Engine · Maker v5.5</title>":"<title>§wyrl§ Engine · Maker v5.6</title>",
      '<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.5</div>':'<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.6</div>',
      '<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.5 · DRAGON PASS</div>':'<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.6 · CONTACT PASS</div>',
      "window.SWRLZ_FORGE_BUILD={version:'v5.5',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',lookMode:'natural',grouping:'hierarchical',defaultDenAvatar:'wisp',dragonModel:'anatomy-v2'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;":
        "window.SWRLZ_FORGE_BUILD={version:'v5.6',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',lookMode:'natural',grouping:'hierarchical',defaultDenAvatar:'wisp',dragonModel:'anatomy-v3',surfaceContact:'raycast-feet'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;",
      "version:'swyrl-engine-agent-v3.5',":"version:'swyrl-engine-agent-v3.6',",
      "editorLog('§wyrl§ Engine v5.5 initialized · natural look · Dragon anatomy v2','ok')":
        "editorLog('§wyrl§ Engine v5.6 initialized · dragon wing detail · surface contact grounding','ok')",
      "engine:'§wyrl§ Engine · Maker v5.5',":"engine:'§wyrl§ Engine · Maker v5.6',",
      "version:5.5,":"version:5.6,"
    }
    for a,b in repl.items(): s=_once(s,a,b)

    grounding=r"""
const dragonFootRaycaster=new THREE.Raycaster();
const dragonFootDown=new THREE.Vector3(0,-1,0);
const dragonFootWorld=new THREE.Vector3();
const dragonFootOrigin=new THREE.Vector3();
const dragonFootLocal=new THREE.Vector3();
const dragonFootNormal=new THREE.Vector3();
const dragonFootQuat=new THREE.Quaternion();
const dragonFootUp=new THREE.Vector3(0,1,0);

function surfaceContactMeshes(ignoreActor=null){
  const out=[];
  for(const a of actors){
    if(a===ignoreActor||a.visible===false||a.userData?.editorOnly)continue;
    if(a.userData?.actorType==='dragon'||a.userData?.actorType==='hero'||a.userData?.actorType==='group')continue;
    if(a.userData?.baked===false)continue;
    a.traverse?.(o=>{
      if(!o.isMesh||o.userData?.editorOnly||o.visible===false)return;
      // Ignore transparent helper rings / non-ground visual FX.
      const n=(o.name||'').toLowerCase();
      if(n.includes('glow')||n.includes('selection')||n.includes('rune'))return;
      out.push(o);
    });
  }
  return out;
}

function setCylinderBetween(mesh,a,b){
  const va=a instanceof THREE.Vector3?a:new THREE.Vector3(...a),vb=b instanceof THREE.Vector3?b:new THREE.Vector3(...b);
  const dir=vb.clone().sub(va),len=Math.max(.001,dir.length()),mid=va.clone().add(vb).multiplyScalar(.5);
  mesh.position.copy(mid);mesh.scale.y=len/(mesh.userData.baseLength||len);
  mesh.quaternion.setFromUnitVectors(dragonFootUp,dir.normalize());
}

function groundDragonFeet(dragon,dt=.016){
  const rig=dragon.userData?.dragonRig;
  if(!rig?.legs?.length)return;
  const surfaces=surfaceContactMeshes(dragon);
  if(!surfaces.length)return;

  dragon.updateMatrixWorld(true);
  for(const leg of rig.legs){
    const foot=leg.foot;
    foot.getWorldPosition(dragonFootWorld);
    dragonFootOrigin.copy(dragonFootWorld);
    dragonFootOrigin.y+=Math.max(2.5,dragon.scale.y*3.0);

    dragonFootRaycaster.set(dragonFootOrigin,dragonFootDown);
    dragonFootRaycaster.far=Math.max(7,dragon.scale.y*8);
    const hit=dragonFootRaycaster.intersectObjects(surfaces,false)[0];

    let targetY=leg.restFootY;
    let targetNormalY=1;
    if(hit){
      dragonFootLocal.copy(hit.point);dragon.worldToLocal(dragonFootLocal);
      targetY=dragonFootLocal.y+leg.soleOffset;
      if(hit.face){
        dragonFootNormal.copy(hit.face.normal).transformDirection(hit.object.matrixWorld);
        targetNormalY=Math.max(.18,dragonFootNormal.y);
      }
    }else{
      // Fall back to terrain when no mesh exists below the foot.
      const wp=foot.getWorldPosition(new THREE.Vector3());
      const localTerrain=new THREE.Vector3(wp.x,terrainHeight(wp.x,wp.z),wp.z);
      dragon.worldToLocal(localTerrain);targetY=localTerrain.y+leg.soleOffset;
    }

    // Clamp so a bad ray hit cannot stretch a leg across the whole room.
    targetY=THREE.MathUtils.clamp(targetY,leg.restFootY-.75,leg.restFootY+1.45);
    const alpha=1-Math.exp(-dt*18);
    leg.contactY=THREE.MathUtils.lerp(leg.contactY??leg.restFootY,targetY,alpha);
    foot.position.y=leg.contactY;

    // Keep claws/sole aligned to sloped rock surfaces without over-tilting.
    if(hit?.face){
      const worldNormal=dragonFootNormal.normalize();
      const localNormal=worldNormal.clone().transformDirection(dragon.matrixWorld.clone().invert()).normalize();
      dragonFootQuat.setFromUnitVectors(dragonFootUp,localNormal);
      const maxTilt=.42;
      const e=new THREE.Euler().setFromQuaternion(dragonFootQuat,'XYZ');
      e.x=THREE.MathUtils.clamp(e.x,-maxTilt,maxTilt);e.z=THREE.MathUtils.clamp(e.z,-maxTilt,maxTilt);e.y=0;
      foot.quaternion.slerp(new THREE.Quaternion().setFromEuler(e),alpha*.7);
    }

    // Re-aim lower shin at planted foot. Upper leg remains authored, giving a simple 2-bone IK feel.
    const knee=new THREE.Vector3(...leg.knee);
    const ankle=foot.position.clone();ankle.y+=.18;
    setCylinderBetween(leg.lower,knee,ankle);
  }
}

function updateDragonSurfaceContacts(dt){
  for(const a of actors){
    if(a.userData?.actorType==='dragon'&&a.userData?.dragonRig)groundDragonFeet(a,dt);
  }
}
"""
    s=_before(s,"function makeDragon(pos",grounding)

    dragon=r"""function makeDragon(pos,color='#9b6cff',baked=true,name='Dragon Avatar',scale=1){
  const g=new THREE.Group();
  const base=new THREE.Color(color),shadeColor=base.clone().multiplyScalar(.48),bellyColor=base.clone().lerp(new THREE.Color('#d9c7e5'),.32);
  const skin=mat(base),shade=mat(shadeColor),belly=mat(bellyColor),horn=mat('#d9d0bd'),claw=mat('#c9c1ad'),glow=glowMat(color,1.0);
  const membraneBase=shadeColor.clone().lerp(base,.42);
  const membrane=new THREE.MeshStandardMaterial({color:membraneBase,roughness:.88,metalness:.01,side:THREE.DoubleSide,transparent:true,opacity:.91,flatShading:true});
  const membraneInner=new THREE.MeshStandardMaterial({color:membraneBase.clone().lerp(new THREE.Color('#ffffff'),.12),roughness:.9,metalness:0,side:THREE.DoubleSide,transparent:true,opacity:.78,flatShading:true});
  const boneMat=mat(shadeColor.clone().multiplyScalar(.72));

  const mesh=(geo,material,namePart,parent=g)=>{const m=new THREE.Mesh(geo,material);m.name=namePart||'';m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;};
  const segment=(a,b,r1,r2,material,namePart,parent=g)=>{
    const va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),mid=va.clone().add(vb).multiplyScalar(.5),dir=vb.clone().sub(va),len=dir.length();
    const m=mesh(new THREE.CylinderGeometry(r2,r1,len,7,1,false),material,namePart,parent);
    m.position.copy(mid);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());m.userData.baseLength=len;return m;
  };
  const coneBetween=(a,b,r,material,namePart,parent=g)=>{
    const va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),mid=va.clone().add(vb).multiplyScalar(.5),dir=vb.clone().sub(va),len=dir.length();
    const m=mesh(new THREE.ConeGeometry(r,len,7),material,namePart,parent);
    m.position.copy(mid);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());return m;
  };
  const triangleMesh=(verts,material,namePart,parent=g)=>{
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(verts.flat(),3));geo.computeVertexNormals();
    return mesh(geo,material,namePart,parent);
  };

  const chest=mesh(new THREE.IcosahedronGeometry(.92,1),skin,'DragonChest');chest.position.set(0,2.25,-.02);chest.scale.set(.98,1.24,.92);
  const bellyPlate=mesh(new THREE.IcosahedronGeometry(.72,1),belly,'DragonBelly');bellyPlate.position.set(0,2.05,-.56);bellyPlate.scale.set(.72,1.0,.52);
  const haunch=mesh(new THREE.IcosahedronGeometry(.88,1),skin.clone(),'DragonHaunch');haunch.position.set(0,1.75,.92);haunch.scale.set(1.05,.92,1.28);

  segment([0,2.85,-.28],[0,3.55,-.72],.54,.44,skin.clone(),'NeckLower');
  segment([0,3.48,-.70],[0,4.10,-1.10],.43,.33,skin.clone(),'NeckUpper');
  const head=mesh(new THREE.DodecahedronGeometry(.62),skin.clone(),'DragonHead');head.position.set(0,4.45,-1.43);head.scale.set(1.0,.78,1.18);
  const muzzle=mesh(new THREE.BoxGeometry(.72,.38,.88),skin.clone(),'DragonMuzzle');muzzle.position.set(0,4.28,-2.06);muzzle.rotation.x=-.06;
  const nose=mesh(new THREE.BoxGeometry(.62,.24,.30),shade.clone(),'DragonNose');nose.position.set(0,4.30,-2.58);
  const jaw=mesh(new THREE.BoxGeometry(.65,.18,.83),belly.clone(),'DragonJaw');jaw.position.set(0,4.05,-2.03);jaw.rotation.x=.06;

  for(const side of [-1,1]){
    const brow=mesh(new THREE.ConeGeometry(.13,.58,5),shade.clone(),'DragonBrow');brow.position.set(side*.35,4.63,-1.82);brow.rotation.set(Math.PI/2,0,side*.22);
    const eye=mesh(new THREE.SphereGeometry(.085,9,7),glow.clone(),'DragonEye');eye.position.set(side*.34,4.48,-1.95);
    coneBetween([side*.28,4.83,-1.28],[side*.48,5.55,-.75],.15,horn.clone(),'DragonHorn');
    coneBetween([side*.40,4.70,-1.18],[side*.73,5.13,-.72],.10,horn.clone(),'DragonHornSide');
    const ear=mesh(new THREE.ConeGeometry(.16,.62,5),skin.clone(),'DragonEar');ear.position.set(side*.58,4.57,-1.24);ear.rotation.set(0,0,side*-1.02);
    const tooth=mesh(new THREE.ConeGeometry(.055,.25,5),claw.clone(),'DragonTooth');tooth.position.set(side*.22,3.98,-2.26);tooth.rotation.x=Math.PI;
  }

  // Four explicit legs. Rear legs are intentionally larger and farther back so all four feet remain visible/readable.
  const rigLegs=[];
  const legDefs=[
    {side:-1,kind:'front',hip:[-.58,2.04,-.50],knee:[-.77,1.24,-.76],foot:[-.72,.42,-.72]},
    {side: 1,kind:'front',hip:[ .58,2.04,-.50],knee:[ .77,1.24,-.76],foot:[ .72,.42,-.72]},
    {side:-1,kind:'rear', hip:[-.72,1.78, 1.05],knee:[-.98,1.08, 1.42],foot:[-.90,.40, 1.62]},
    {side: 1,kind:'rear', hip:[ .72,1.78, 1.05],knee:[ .98,1.08, 1.42],foot:[ .90,.40, 1.62]}
  ];
  for(const def of legDefs){
    const rear=def.kind==='rear';
    segment(def.hip,def.knee,rear?.32:.26,rear?.24:.21,skin.clone(),rear?'DragonRearUpperLeg':'DragonFrontUpperLeg');
    const lower=segment(def.knee,[def.foot[0],def.foot[1]+.18,def.foot[2]],rear?.23:.20,rear?.14:.13,shade.clone(),rear?'DragonRearLowerLeg':'DragonFrontLowerLeg');

    const footGroup=new THREE.Group();footGroup.name=rear?'DragonRearFoot':'DragonFrontFoot';footGroup.position.set(...def.foot);g.add(footGroup);
    const foot=mesh(new THREE.BoxGeometry(rear?.62:.50,.20,rear?.78:.68),shade.clone(),rear?'DragonRearPaw':'DragonFrontPaw',footGroup);foot.position.y=.10;foot.position.z=-.04;
    // heel makes rear paws unmistakable from side/back views
    if(rear){
      const heel=mesh(new THREE.BoxGeometry(.48,.18,.38),skin.clone(),'DragonHeel',footGroup);heel.position.set(0,.16,.29);
    }
    for(let c=-1;c<=1;c++){
      const x=c*(rear?.16:.13);
      const talon=mesh(new THREE.ConeGeometry(.06,rear?.34:.28,6),claw.clone(),'DragonClaw',footGroup);
      talon.position.set(x,.04,-(rear?.48:.42));talon.rotation.x=-Math.PI/2;
    }
    rigLegs.push({kind:def.kind,side:def.side,foot:footGroup,lower,knee:def.knee,restFootY:def.foot[1],soleOffset:.10,contactY:def.foot[1]});
  }

  const tailPts=[[0,1.72,1.62],[.12,1.55,2.65],[.42,1.42,3.62],[.72,1.34,4.47],[.58,1.24,5.18],[.28,1.16,5.75]];
  for(let i=0;i<tailPts.length-1;i++)segment(tailPts[i],tailPts[i+1],.40-i*.055,.32-i*.05,i<3?skin.clone():shade.clone(),'DragonTail');
  coneBetween(tailPts.at(-1),[.04,1.12,6.35],.16,shade.clone(),'DragonTailTip');

  // Wing v3: explicit hand/finger skeleton and multiple membrane panels with lighter inner webbing.
  for(const side of [-1,1]){
    const root=[side*.58,3.12,.15];
    const elbow=[side*1.62,4.02,.02];
    const wrist=[side*2.55,3.95,.10];
    const tip1=[side*4.20,3.62,.35];
    const tip2=[side*3.95,3.00,.68];
    const tip3=[side*3.48,2.40,.98];
    const tip4=[side*2.82,1.98,1.18];
    const rearRoot=[side*.72,2.48,.72];

    segment(root,elbow,.13,.095,boneMat.clone(),'WingUpperArm');
    segment(elbow,wrist,.105,.075,boneMat.clone(),'WingForearm');
    segment(wrist,tip1,.075,.035,boneMat.clone(),'WingFingerPrimary');
    segment(wrist,tip2,.068,.032,boneMat.clone(),'WingFingerSecondary');
    segment(wrist,tip3,.060,.030,boneMat.clone(),'WingFingerTertiary');
    segment(wrist,tip4,.052,.027,boneMat.clone(),'WingFingerQuaternary');
    segment(root,rearRoot,.10,.055,boneMat.clone(),'WingRoot');

    triangleMesh([root,elbow,wrist, root,wrist,rearRoot],membrane.clone(),'WingMembraneRoot');
    triangleMesh([wrist,tip1,tip2],membrane.clone(),'WingMembranePanel1');
    triangleMesh([wrist,tip2,tip3],membraneInner.clone(),'WingMembranePanel2');
    triangleMesh([wrist,tip3,tip4],membrane.clone(),'WingMembranePanel3');
    triangleMesh([wrist,tip4,rearRoot],membraneInner.clone(),'WingMembranePanel4');

    // Vein struts give the membrane readable detail without adding expensive textures.
    const veinPairs=[[root,tip3],[elbow,tip2],[rearRoot,tip4]];
    for(const [a,b] of veinPairs)segment(a,b,.026,.018,boneMat.clone(),'WingMembraneVein');
  }

  const spines=[[0,5.03,-1.19,.34],[0,4.28,-.82,.30],[0,3.70,-.48,.27],[0,3.10,-.05,.25],[0,2.55,.45,.23],[0,2.05,1.02,.20],[0,1.66,1.65,.17]];
  for(const [x,y,z,r] of spines){
    const sp=mesh(new THREE.ConeGeometry(r,r*3.2,5),horn.clone(),'DragonSpine');sp.position.set(x,y,z);sp.rotation.x=.18;
  }

  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);g.scale.setScalar(scale);
  const actor=markActor(g,'dragon',{name,baked,colliderRadius:1.18*scale,folder:'Dragon Den/Dragons',components:['Transform','Scene','StaticMesh','Collider','BobMovement','AgentAvatar','SurfaceFootContact'],blueprintClass:'BP_DragonAvatarV3',componentSpeed:.42,bobAmplitude:.012,visualColor:color,role:'lalm-agent-avatar',tags:['dragon-den','agent-avatar','voice-anchor-hook','dragon-anatomy-v3','surface-foot-contact']});
  actor.userData.dragonRig={legs:rigLegs};
  return actor;
}

"""
    s=_replace_block(s,"function makeDragon(pos","function addPath(name, points){",dragon)

    # Update planted feet every frame after procedural Wisp animation and before render.
    s=_once(
      s,
      "  updateWispVisuals(t);if(!playing)orbit.update();if(selectionBox&&selected)selectionBox.update();renderer.render(scene,camera);",
      "  updateWispVisuals(t);updateDragonSurfaceContacts(dt);if(!playing)orbit.update();if(selectionBox&&selected)selectionBox.update();renderer.render(scene,camera);"
    )

    return s
