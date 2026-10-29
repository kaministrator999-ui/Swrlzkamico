"""§wyrl§ Engine v5.5: natural look controls + Dragon anatomy/model pass."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v5.5 patch token missing: " + old[:200])
    return s.replace(old, new, 1)

def _replace_block(s: str, start: str, end: str, block: str) -> str:
    a=s.find(start)
    if a<0: raise RuntimeError("v5.5 block start missing: "+start[:180])
    b=s.find(end,a)
    if b<0: raise RuntimeError("v5.5 block end missing: "+end[:180])
    return s[:a]+block+s[b:]

def apply(html: str) -> str:
    s=html
    repl={
      "<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_4_WISP_AVATAR -->":"<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_5_DRAGONS_NATURAL_LOOK -->",
      "<title>§wyrl§ Engine · Maker v5.4</title>":"<title>§wyrl§ Engine · Maker v5.5</title>",
      '<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.4</div>':'<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.5</div>',
      '<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.4 · WISP AVATAR</div>':'<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.5 · DRAGON PASS</div>',
      "window.SWRLZ_FORGE_BUILD={version:'v5.4',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',grouping:'hierarchical',defaultDenAvatar:'wisp'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;":
        "window.SWRLZ_FORGE_BUILD={version:'v5.5',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',lookMode:'natural',grouping:'hierarchical',defaultDenAvatar:'wisp',dragonModel:'anatomy-v2'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;",
      "version:'swyrl-engine-agent-v3.4',":"version:'swyrl-engine-agent-v3.5',",
      "editorLog('§wyrl§ Engine v5.4 initialized · Dragon Den Wisp visitor avatar','ok')":
        "editorLog('§wyrl§ Engine v5.5 initialized · natural look · Dragon anatomy v2','ok')",
      "engine:'§wyrl§ Engine · Maker v5.4',":"engine:'§wyrl§ Engine · Maker v5.5',",
      "version:5.4,":"version:5.5,"
    }
    for a,b in repl.items(): s=_once(s,a,b)

    # Fix the actually inverted axis: right-stick / mouse right must turn the camera right.
    s=_once(s,
      "fpYaw-=fpLook.x*FP_LOOK_SPEED*dt;fpPitch-=fpLook.y*FP_LOOK_SPEED*dt;clampPitch();",
      "fpYaw+=fpLook.x*FP_LOOK_SPEED*dt;fpPitch-=fpLook.y*FP_LOOK_SPEED*dt;clampPitch();")
    s=_once(s,
      "fpYaw-=e.movementX*FP_MOUSE_SENS;fpPitch-=e.movementY*FP_MOUSE_SENS;clampPitch();",
      "fpYaw+=e.movementX*FP_MOUSE_SENS;fpPitch-=e.movementY*FP_MOUSE_SENS;clampPitch();")

    dragon=r"""function makeDragon(pos,color='#9b6cff',baked=true,name='Dragon Avatar',scale=1){
  const g=new THREE.Group();
  const base=new THREE.Color(color),shadeColor=base.clone().multiplyScalar(.48),bellyColor=base.clone().lerp(new THREE.Color('#d9c7e5'),.32);
  const skin=mat(base),shade=mat(shadeColor),belly=mat(bellyColor),horn=mat('#d9d0bd'),claw=mat('#bdb6a5'),glow=glowMat(color,1.0);
  const membrane=new THREE.MeshStandardMaterial({color:shadeColor.clone().lerp(base,.38),roughness:.88,metalness:.01,side:THREE.DoubleSide,transparent:true,opacity:.90,flatShading:true});
  const boneMat=mat(shadeColor.clone().multiplyScalar(.72));

  const mesh=(geo,material,namePart)=>{const m=new THREE.Mesh(geo,material);m.name=namePart||'';m.castShadow=true;m.receiveShadow=true;g.add(m);return m;};
  const segment=(a,b,r1,r2,material,namePart)=>{
    const va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),mid=va.clone().add(vb).multiplyScalar(.5),dir=vb.clone().sub(va),len=dir.length();
    const m=mesh(new THREE.CylinderGeometry(r2,r1,len,7,1,false),material,namePart);
    m.position.copy(mid);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());return m;
  };
  const coneBetween=(a,b,r,material,namePart)=>{
    const va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),mid=va.clone().add(vb).multiplyScalar(.5),dir=vb.clone().sub(va),len=dir.length();
    const m=mesh(new THREE.ConeGeometry(r,len,7),material,namePart);
    m.position.copy(mid);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());return m;
  };
  const triangleMesh=(verts,material,namePart)=>{
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(verts.flat(),3));geo.computeVertexNormals();
    return mesh(geo,material,namePart);
  };

  // Torso: chest + haunches produce a dragon silhouette instead of a capsule/barrel.
  const chest=mesh(new THREE.IcosahedronGeometry(.92,1),skin,'DragonChest');chest.position.set(0,2.25,-.02);chest.scale.set(.98,1.24,.92);
  const bellyPlate=mesh(new THREE.IcosahedronGeometry(.72,1),belly,'DragonBelly');bellyPlate.position.set(0,2.05,-.56);bellyPlate.scale.set(.72,1.0,.52);
  const haunch=mesh(new THREE.IcosahedronGeometry(.88,1),skin.clone(),'DragonHaunch');haunch.position.set(0,1.75,.92);haunch.scale.set(1.05,.92,1.28);

  // Segmented neck bends naturally toward the head.
  segment([0,2.85,-.28],[0,3.55,-.72],.54,.44,skin.clone(),'NeckLower');
  segment([0,3.48,-.70],[0,4.10,-1.10],.43,.33,skin.clone(),'NeckUpper');
  const head=mesh(new THREE.DodecahedronGeometry(.62),skin.clone(),'DragonHead');head.position.set(0,4.45,-1.43);head.scale.set(1.0,.78,1.18);
  const muzzle=mesh(new THREE.BoxGeometry(.72,.38,.88),skin.clone(),'DragonMuzzle');muzzle.position.set(0,4.28,-2.06);muzzle.rotation.x=-.06;
  const nose=mesh(new THREE.BoxGeometry(.62,.24,.30),shade.clone(),'DragonNose');nose.position.set(0,4.30,-2.58);
  const jaw=mesh(new THREE.BoxGeometry(.65,.18,.83),belly.clone(),'DragonJaw');jaw.position.set(0,4.05,-2.03);jaw.rotation.x=.06;

  // Brows, eyes, horns, ears and teeth give the head a readable dragon face.
  for(const side of [-1,1]){
    const brow=mesh(new THREE.ConeGeometry(.13,.58,5),shade.clone(),'DragonBrow');brow.position.set(side*.35,4.63,-1.82);brow.rotation.set(Math.PI/2,0,side*.22);
    const eye=mesh(new THREE.SphereGeometry(.085,9,7),glow.clone(),'DragonEye');eye.position.set(side*.34,4.48,-1.95);
    const hornA=coneBetween([side*.28,4.83,-1.28],[side*.48,5.55,-.75],.15,horn.clone(),'DragonHorn');
    const hornB=coneBetween([side*.40,4.70,-1.18],[side*.73,5.13,-.72],.10,horn.clone(),'DragonHornSide');
    const ear=mesh(new THREE.ConeGeometry(.16,.62,5),skin.clone(),'DragonEar');ear.position.set(side*.58,4.57,-1.24);ear.rotation.set(0,0,side*-1.02);
    const tooth=mesh(new THREE.ConeGeometry(.055,.25,5),claw.clone(),'DragonTooth');tooth.position.set(side*.22,3.98,-2.26);tooth.rotation.x=Math.PI;
  }

  // Four articulated legs with knees, feet and claws.
  const legDefs=[
    [-1,-.50,2.02,1.25,-.73,.62,-.86,-.56],
    [ 1,-.50,2.02,1.25,-.73,.62,-.86,-.56],
    [-1, 1.02,1.85,1.10, 1.02,.56, .68,-.40],
    [ 1, 1.02,1.85,1.10, 1.02,.56, .68,-.40]
  ];
  for(const [side,z,hipY,kneeY,kneeZ,ankleY,ankleZ,footZ] of legDefs){
    const sx=side*.58,kx=side*.77,ax=side*.70;
    segment([sx,hipY,z],[kx,kneeY,kneeZ],.26,.21,skin.clone(),'DragonUpperLeg');
    segment([kx,kneeY,kneeZ],[ax,ankleY,ankleZ],.20,.13,shade.clone(),'DragonLowerLeg');
    const foot=mesh(new THREE.BoxGeometry(.46,.18,.64),shade.clone(),'DragonFoot');foot.position.set(ax,.47,footZ);
    for(let c=-1;c<=1;c++){
      const talon=coneBetween([ax+c*.12,.44,footZ-.27],[ax+c*.13,.30,footZ-.58],.055,claw.clone(),'DragonClaw');
    }
  }

  // Curved segmented tail.
  const tailPts=[[0,1.72,1.62],[.12,1.55,2.65],[.42,1.42,3.62],[.72,1.34,4.47],[.58,1.24,5.18],[.28,1.16,5.75]];
  for(let i=0;i<tailPts.length-1;i++)segment(tailPts[i],tailPts[i+1],.40-i*.055,.32-i*.05,i<3?skin.clone():shade.clone(),'DragonTail');
  coneBetween(tailPts.at(-1),[.04,1.12,6.35],.16,shade.clone(),'DragonTailTip');

  // Articulated bat-like wings: bone arms plus triangular membrane panels instead of slab polygons.
  for(const side of [-1,1]){
    const root=[side*.58,3.12,.15],elbow=[side*1.70,3.92,.02],tip=[side*4.05,3.56,.36],rearTip=[side*3.05,2.02,1.08],rearRoot=[side*.72,2.50,.72];
    segment(root,elbow,.12,.09,boneMat.clone(),'WingArm');
    segment(elbow,tip,.10,.055,boneMat.clone(),'WingFinger');
    segment(root,rearTip,.095,.045,boneMat.clone(),'WingFinger');
    segment(root,rearRoot,.10,.06,boneMat.clone(),'WingRoot');
    const wing=triangleMesh([root,elbow,tip, root,tip,rearTip, root,rearTip,rearRoot],membrane.clone(),'WingMembrane');
    wing.userData.wingSide=side;
    // secondary finger creates the classic dragon/bat scallop
    const midTip=[side*3.60,2.72,.77];segment(elbow,midTip,.075,.04,boneMat.clone(),'WingFinger');
  }

  // Dorsal spikes run from crown down the neck/back.
  const spines=[[0,5.03,-1.19,.34],[0,4.28,-.82,.30],[0,3.70,-.48,.27],[0,3.10,-.05,.25],[0,2.55,.45,.23],[0,2.05,1.02,.20],[0,1.66,1.65,.17]];
  for(const [x,y,z,r] of spines){
    const s=mesh(new THREE.ConeGeometry(r,r*3.2,5),horn.clone(),'DragonSpine');s.position.set(x,y,z);s.rotation.x=.18;
  }

  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);g.scale.setScalar(scale);
  return markActor(g,'dragon',{name,baked,colliderRadius:1.18*scale,folder:'Dragon Den/Dragons',components:['Transform','Scene','StaticMesh','Collider','BobMovement','AgentAvatar'],blueprintClass:'BP_DragonAvatarV2',componentSpeed:.42,bobAmplitude:.018,visualColor:color,role:'lalm-agent-avatar',tags:['dragon-den','agent-avatar','voice-anchor-hook','dragon-anatomy-v2']});
}

"""
    s=_replace_block(s,"function makeDragon(pos","function addPath(name, points){",dragon)

    return s
