"""§wyrl§ Engine v5.2: first-person PIE with mobile twin-stick move/look controls."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v5.2 patch token missing: " + old[:180])
    return s.replace(old, new, 1)

def _before(s: str, marker: str, block: str) -> str:
    i=s.find(marker)
    if i<0: raise RuntimeError("v5.2 insert marker missing: "+marker[:180])
    return s[:i]+block+s[i:]

def _replace_block(s: str, start: str, end: str, block: str) -> str:
    a=s.find(start)
    if a<0: raise RuntimeError("v5.2 block start missing: "+start[:180])
    b=s.find(end,a)
    if b<0: raise RuntimeError("v5.2 block end missing: "+end[:180])
    return s[:a]+block+s[b:]

def apply(html: str) -> str:
    s=html

    repl={
      "<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_1_SEED_DEN -->":"<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_2_FIRST_PERSON_TWIN_STICK -->",
      "<title>§wyrl§ Engine · Maker v5.1</title>":"<title>§wyrl§ Engine · Maker v5.2</title>",
      '<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.1</div>':'<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.2</div>',
      '<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.1 · SEED DEN</div>':'<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.2 · FIRST PERSON</div>',
      "window.SWRLZ_FORGE_BUILD={version:'v5.1',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;":
        "window.SWRLZ_FORGE_BUILD={version:'v5.2',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;",
      "version:'swyrl-engine-agent-v3.1',":"version:'swyrl-engine-agent-v3.2',",
      "editorLog('§wyrl§ Engine v5.1 initialized · Dragon Den Seed Chamber default · project templates active','ok')":
        "editorLog('§wyrl§ Engine v5.2 initialized · first-person PIE · twin-stick mobile controls','ok')",
    }
    for a,b in repl.items(): s=_once(s,a,b)

    css=r"""
.first-person-hud{position:absolute;inset:0;z-index:12;display:none;pointer-events:none}
.app.runtime-play .first-person-hud{display:block}
.fp-reticle{position:absolute;left:50%;top:50%;width:8px;height:8px;border:1px solid #ffffffc9;border-radius:50%;transform:translate(-50%,-50%);box-shadow:0 0 8px #7ee7ff88}
.fp-reticle:before,.fp-reticle:after{content:"";position:absolute;background:#ffffffaa}
.fp-reticle:before{width:16px;height:1px;left:-5px;top:3px}.fp-reticle:after{width:1px;height:16px;left:3px;top:-5px}
.touch-controls{position:absolute;inset:0;display:none;pointer-events:none}
.joy{position:absolute;bottom:20px;width:116px;height:116px;border-radius:50%;border:1px solid #b7eaff70;background:radial-gradient(circle,#18314a77 0 24%,#0b172777 25% 63%,#8adfff22 64% 100%);box-shadow:inset 0 0 30px #0008,0 0 18px #43cfff22;pointer-events:auto;touch-action:none;user-select:none}
.joy-left{left:18px}.joy-right{right:18px}
.joy-knob{position:absolute;left:50%;top:50%;width:52px;height:52px;border-radius:50%;transform:translate(-50%,-50%);background:#8fdfff48;border:1px solid #d9f6ff99;box-shadow:0 0 14px #64d8ff44;pointer-events:none}
.joy-label{position:absolute;left:0;right:0;bottom:-19px;text-align:center;font:700 10px system-ui;color:#b9d7e8;letter-spacing:.12em;text-shadow:0 1px 3px #000}
@media (pointer:coarse),(max-width:900px){.app.runtime-play .touch-controls{display:block}}
@media (max-width:620px){
  .app.runtime-play .badgeBox,.app.runtime-play .build-stamp{display:none}
  .app.runtime-play .banner{top:10px;bottom:auto;left:50%;right:auto;transform:translateX(-50%);width:auto;max-width:74vw;white-space:nowrap}
  .joy{width:104px;height:104px;bottom:18px}.joy-knob{width:46px;height:46px}.joy-left{left:14px}.joy-right{right:14px}
}
"""
    s=_once(s,"</style>",css+"\n</style>")

    hud="""      <div id="firstPersonHud" class="first-person-hud">
        <div class="fp-reticle"></div>
        <div class="touch-controls">
          <div id="moveStick" class="joy joy-left"><div class="joy-knob"></div><div class="joy-label">MOVE</div></div>
          <div id="lookStick" class="joy joy-right"><div class="joy-knob"></div><div class="joy-label">LOOK</div></div>
        </div>
      </div>
"""
    s=_once(s,'      <div id="playBanner" class="banner">PIE · WASD / ARROWS · SPACE jump · click terrain to move</div>',
            '      <div id="playBanner" class="banner">PIE · FIRST PERSON · left stick move · right stick look</div>\n'+hud)

    s=_once(
      s,
      "let heroJumpQueued = false;\nconst HERO_GROUND_OFFSET = 0.03;",
      "let heroJumpQueued = false;\nlet fpYaw=0,fpPitch=0;const fpMove={x:0,y:0},fpLook={x:0,y:0};const FP_EYE_HEIGHT=1.62,FP_LOOK_SPEED=2.35,FP_MOUSE_SENS=.0022;\nconst HERO_GROUND_OFFSET = 0.03;"
    )

    controls=r"""
function clampPitch(){fpPitch=THREE.MathUtils.clamp(fpPitch,-1.38,1.38);}
function setHeroBodyVisible(h,visible){
  if(!h)return;
  h.traverse(o=>{
    if(!o.isMesh)return;
    if(!visible){if(o.userData._fpPrevVisible===undefined)o.userData._fpPrevVisible=o.visible;o.visible=false;}
    else if(o.userData._fpPrevVisible!==undefined){o.visible=o.userData._fpPrevVisible;delete o.userData._fpPrevVisible;}
  });
}
function resetStick(el,state){state.x=0;state.y=0;const k=el?.querySelector('.joy-knob');if(k)k.style.transform='translate(-50%,-50%)';}
function bindVirtualStick(id,state){
  const el=$(id);if(!el)return;let active=null;
  const update=e=>{const r=el.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,limit=r.width*.34;let dx=e.clientX-cx,dy=e.clientY-cy,d=Math.hypot(dx,dy);if(d>limit){dx*=limit/d;dy*=limit/d;}state.x=dx/limit;state.y=dy/limit;const k=el.querySelector('.joy-knob');k.style.transform=`translate(calc(-50% + ${dx}px),calc(-50% + ${dy}px))`;};
  el.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();active=e.pointerId;el.setPointerCapture?.(active);update(e);});
  el.addEventListener('pointermove',e=>{if(e.pointerId!==active)return;e.preventDefault();e.stopPropagation();update(e);});
  const end=e=>{if(active!==null&&e.pointerId!==undefined&&e.pointerId!==active)return;active=null;resetStick(el,state);};
  el.addEventListener('pointerup',end);el.addEventListener('pointercancel',end);el.addEventListener('lostpointercapture',end);
}
bindVirtualStick('moveStick',fpMove);bindVirtualStick('lookStick',fpLook);
document.addEventListener('mousemove',e=>{
  if(!playing||document.pointerLockElement!==$('viewport'))return;
  fpYaw-=e.movementX*FP_MOUSE_SENS;fpPitch-=e.movementY*FP_MOUSE_SENS;clampPitch();
});
document.addEventListener('pointerlockchange',()=>{if(!playing)return;});
"""
    s=_before(s,"function heroActor(){",controls)

    begin=r"""function beginPlay(fromHere=null){
  preSessionCameraView=editorCameraView;setActiveCamera(perspectiveCamera);orbit.enableRotate=true;
  playing=true;simulating=false;paused=false;keepSimulationChanges=false;savePlaySnapshot();transform.detach();if(selectionBox)selectionBox.visible=false;orbit.enabled=false;heroClickTarget=null;heroVel.set(0,0,0);heroGrounded=true;lastWave=-999;beginRuntimeComponents();
  $('mobileDrawer').classList.remove('show');$('mobileToolsPanel').classList.remove('show');$('contentDrawer').classList.remove('show');
  resetStick($('moveStick'),fpMove);resetStick($('lookStick'),fpLook);
  const h=heroActor();
  if(h){
    if(fromHere){h.position.x=fromHere.x;h.position.z=fromHere.z;}
    h.position.y=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET;
    const focus=currentProject.kind==='dragons-den'?new THREE.Vector3(0,h.position.y+FP_EYE_HEIGHT,1.5):new THREE.Vector3(0,h.position.y+FP_EYE_HEIGHT,0);
    fpYaw=Math.atan2(focus.x-h.position.x,-(focus.z-h.position.z));fpPitch=0;
    setHeroBodyVisible(h,false);
    perspectiveCamera.fov=72;perspectiveCamera.updateProjectionMatrix();
    perspectiveCamera.position.set(h.position.x,h.position.y+FP_EYE_HEIGHT,h.position.z);
  }
  $('playBanner').classList.add('show');$('playBanner').textContent='FIRST PERSON · left stick move · right stick look';$('viewLabel').textContent='First Person PIE';setSessionButtons();editorLog('First-person Play In Editor started','ok');toast('First-person mode · twin sticks active');
  setTimeout(()=>{if(playing)$('playBanner').classList.remove('show');},2600);
  if(matchMedia('(pointer:fine)').matches)$('viewport').requestPointerLock?.();
}
"""
    s=_replace_block(s,"function beginPlay(fromHere=null){","function beginSimulate(){",begin)

    stop=r"""function stopSession(){
  const restoreView=preSessionCameraView||editorCameraView;
  const kept=keepSimulationChanges?actors.map(a=>({a,pos:a.position.clone(),rot:a.rotation.clone(),scale:a.scale.clone()})):null;
  const h=heroActor();setHeroBodyVisible(h,true);resetStick($('moveStick'),fpMove);resetStick($('lookStick'),fpLook);if(document.pointerLockElement)document.exitPointerLock?.();
  perspectiveCamera.fov=55;perspectiveCamera.updateProjectionMatrix();
  playing=false;simulating=false;paused=false;restorePlaySnapshot();
  if(kept){for(const k of kept){k.a.position.copy(k.pos);k.a.rotation.copy(k.rot);k.a.scale.copy(k.scale);k.a.userData.spawnPos=k.a.position.toArray();}commitTransaction('Keep Simulation Changes');}
  setCameraView(restoreView);orbit.enabled=true;if(selectionBox)selectionBox.visible=true;if(selected)transform.attach(selected);$('playBanner').classList.remove('show');updateViewLabel();setSessionButtons();editorLog('Editor session stopped','ok');toast('Returned to editor.');
}
"""
    s=_replace_block(s,"function stopSession(){","$('playBtn').onclick",stop)

    hero=r"""function updateHero(dt, t){
  const h=heroActor();if(!h||h.visible===false)return;

  fpYaw-=fpLook.x*FP_LOOK_SPEED*dt;fpPitch-=fpLook.y*FP_LOOK_SPEED*dt;clampPitch();

  const keyRight=(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0);
  const keyForward=(keys.has('w')||keys.has('arrowup')?1:0)-(keys.has('s')||keys.has('arrowdown')?1:0);
  const rightInput=THREE.MathUtils.clamp(keyRight+fpMove.x,-1,1);
  const forwardInput=THREE.MathUtils.clamp(keyForward-fpMove.y,-1,1);
  const forward=new THREE.Vector3(Math.sin(fpYaw),0,-Math.cos(fpYaw));
  const right=new THREE.Vector3(Math.cos(fpYaw),0,Math.sin(fpYaw));
  const move=new THREE.Vector3().addScaledVector(forward,forwardInput).addScaledVector(right,rightInput);
  if(move.lengthSq()>1)move.normalize();
  if(move.lengthSq()>0.0001)heroClickTarget=null;

  const speed=h.userData.moveSpeed||6;
  const next=h.position.clone().add(move.multiplyScalar(speed*dt));
  resolveHeroCollision(next,0.55);h.position.x=next.x;h.position.z=next.z;

  const groundY=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET;
  if(heroJumpQueued&&heroGrounded){heroVel.y=6.5;heroGrounded=false;}
  heroJumpQueued=false;
  if(heroGrounded&&heroVel.y<=0&&(h.position.y-groundY)<=HERO_STEP_DOWN){h.position.y=groundY;heroVel.y=0;}
  else{heroVel.y-=14*dt;h.position.y+=heroVel.y*dt;if(h.position.y<=groundY){h.position.y=groundY;heroVel.y=0;heroGrounded=true;}else heroGrounded=false;}

  h.rotation.y=fpYaw;
  attackLogic(h,t);

  const eye=new THREE.Vector3(h.position.x,h.position.y+FP_EYE_HEIGHT,h.position.z);
  const cp=Math.cos(fpPitch),look=new THREE.Vector3(Math.sin(fpYaw)*cp,Math.sin(fpPitch),-Math.cos(fpYaw)*cp);
  perspectiveCamera.position.copy(eye);perspectiveCamera.lookAt(eye.clone().add(look));
}
"""
    s=_replace_block(s,"function updateHero(dt, t){","function updateTowers(t){",hero)

    pointer=r"""$('viewport').addEventListener('pointerdown', e=>{
  if(playing){
    if(e.pointerType==='mouse'&&document.pointerLockElement!==$('viewport'))$('viewport').requestPointerLock?.();
    return;
  }
  const rect = $('viewport').getBoundingClientRect();
  pointer.x = ((e.clientX - rect.left)/rect.width)*2 - 1;
  pointer.y = -((e.clientY - rect.top)/rect.height)*2 + 1;
  raycaster.setFromCamera(pointer, camera);
  if(transform.dragging) return;
  const hits = raycaster.intersectObjects(actors, true);
  if(hits.length){
    let o = hits[0].object;
    while(o.parent && !actors.includes(o)) o = o.parent;
    if(actors.includes(o)) selectActor(o);
  }
});

"""
    s=_replace_block(s,"$('viewport').addEventListener('pointerdown', e=>{","window.addEventListener('keydown', e=>{",pointer)

    # Update exported runtime to first-person desktop controls too; mobile exported twin-stick is intentionally kept in editor/runtime scope for this pass.
    export_old="""function moveHero(dt,t){ let h=hero(); if(!h) return; let x=(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0), z=(keys.has('s')||keys.has('arrowdown')?1:0)-(keys.has('w')||keys.has('arrowup')?1:0), move=new THREE.Vector3(x,0,z); if(move.lengthSq()>0){move.normalize(); clickTarget=null}else if(clickTarget){move.copy(clickTarget).sub(h.position); move.y=0; if(move.length()>0.25) move.normalize(); else clickTarget=null}
 let speed=h.userData.moveSpeed||6; let next=h.position.clone().add(move.multiplyScalar(speed*dt)); resolveCollision(next,.55); h.position.x=next.x; h.position.z=next.z;
 let groundY=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET; if(jumpQueued && heroGrounded){heroVel.y=6.5; heroGrounded=false} jumpQueued=false; if(heroGrounded&&heroVel.y<=0&&(h.position.y-groundY)<=HERO_STEP_DOWN){h.position.y=groundY;heroVel.y=0}else{heroVel.y-=14*dt;h.position.y+=heroVel.y*dt;if(h.position.y<=groundY){h.position.y=groundY;heroVel.y=0;heroGrounded=true}else heroGrounded=false} attack(h,t); C.position.lerp(new THREE.Vector3(h.position.x,h.position.y+12,h.position.z+10),.08); C.lookAt(h.position.x,h.position.y+1,h.position.z)}"""
    export_new="""let fpYaw=0,fpPitch=0;const FP_EYE_HEIGHT=1.62;
addEventListener('mousemove',e=>{if(document.pointerLockElement!==R.domElement)return;fpYaw-=e.movementX*.0022;fpPitch=Math.max(-1.38,Math.min(1.38,fpPitch-e.movementY*.0022))});
R.domElement.addEventListener('pointerdown',()=>R.domElement.requestPointerLock?.());
function moveHero(dt,t){let h=hero();if(!h)return;let r=(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0),f=(keys.has('w')||keys.has('arrowup')?1:0)-(keys.has('s')||keys.has('arrowdown')?1:0),forward=new THREE.Vector3(Math.sin(fpYaw),0,-Math.cos(fpYaw)),right=new THREE.Vector3(Math.cos(fpYaw),0,Math.sin(fpYaw)),move=new THREE.Vector3().addScaledVector(forward,f).addScaledVector(right,r);if(move.lengthSq()>1)move.normalize();let speed=h.userData.moveSpeed||6,next=h.position.clone().add(move.multiplyScalar(speed*dt));resolveCollision(next,.55);h.position.x=next.x;h.position.z=next.z;let groundY=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET;if(jumpQueued&&heroGrounded){heroVel.y=6.5;heroGrounded=false}jumpQueued=false;if(heroGrounded&&heroVel.y<=0&&(h.position.y-groundY)<=HERO_STEP_DOWN){h.position.y=groundY;heroVel.y=0}else{heroVel.y-=14*dt;h.position.y+=heroVel.y*dt;if(h.position.y<=groundY){h.position.y=groundY;heroVel.y=0;heroGrounded=true}else heroGrounded=false}h.rotation.y=fpYaw;attack(h,t);let eye=new THREE.Vector3(h.position.x,h.position.y+FP_EYE_HEIGHT,h.position.z),cp=Math.cos(fpPitch),look=new THREE.Vector3(Math.sin(fpYaw)*cp,Math.sin(fpPitch),-Math.cos(fpYaw)*cp);C.position.copy(eye);C.lookAt(eye.clone().add(look))}"""
    s=_once(s,export_old,export_new)

    return s
