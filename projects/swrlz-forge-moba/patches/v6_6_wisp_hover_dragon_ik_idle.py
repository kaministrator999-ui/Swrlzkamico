"""§wyrl§ Engine v6.6: Wisp hover collision + planted animated dragon rig."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v6.6 token missing: "+old[:180])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V6_5_GLITCH_DEN_RUNTIME":"V6_6_HOVER_DRAGON_IK",
      "Maker v6.5":"Maker v6.6","MAKER v6.5":"MAKER v6.6",
      "v6.5 · GLITCH DEN RUNTIME":"v6.6 · HOVER + DRAGON IK",
      "version:'v6.5'":"version:'v6.6'",
      "version:'swyrl-engine-agent-v4.5'":"version:'swyrl-engine-agent-v4.6'",
      "engine:'§wyrl§ Engine · Maker v6.5'":"engine:'§wyrl§ Engine · Maker v6.6'",
      "version:6.5":"version:6.6",
      "editorLog('§wyrl§ Engine v6.5 initialized · Fracture Forge default · Wisp first-person runtime','ok')":"editorLog('§wyrl§ Engine v6.6 initialized · Wisp hover collision · planted dragon idle rig','ok')"
    }.items(): s=_once(s,a,b)

    # Wisp gains explicit hover/collision metadata.
    s=_once(s,"o.userData.avatarStyle='wisp';o.userData.eyeHeight=1.18;o.userData.wispBaseY=1.08;","o.userData.avatarStyle='wisp';o.userData.eyeHeight=1.18;o.userData.wispBaseY=1.08;o.userData.hoverFlight=true;o.userData.hoverHeight=1.15;o.userData.verticalSpeed=4.2;o.userData.colliderRadius=.46;")

    # Replace ground-bound player locomotion with collision-aware free hover for Wisp only.
    old="""  const groundY=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET;
  if(heroJumpQueued&&heroGrounded){heroVel.y=6.5;heroGrounded=false;}
  heroJumpQueued=false;
  if(heroGrounded&&heroVel.y<=0&&(h.position.y-groundY)<=HERO_STEP_DOWN){h.position.y=groundY;heroVel.y=0;}
  else{heroVel.y-=14*dt;h.position.y+=heroVel.y*dt;if(h.position.y<=groundY){h.position.y=groundY;heroVel.y=0;heroGrounded=true;}else heroGrounded=false;}

  h.rotation.y=fpYaw;"""
    new="""  const groundY=terrainHeight(h.position.x,h.position.z)+HERO_GROUND_OFFSET;
  if(h.userData.hoverFlight){
    const rise=(keys.has(' ')||keys.has('e')?1:0)-(keys.has('shift')||keys.has('q')?1:0);
    const minY=groundY+(h.userData.hoverHeight||1.15),targetY=h.position.y+rise*(h.userData.verticalSpeed||4.2)*dt;
    h.position.y=Math.max(minY,targetY);heroVel.y=0;heroGrounded=false;heroJumpQueued=false;
  }else{
    if(heroJumpQueued&&heroGrounded){heroVel.y=6.5;heroGrounded=false;}heroJumpQueued=false;
    if(heroGrounded&&heroVel.y<=0&&(h.position.y-groundY)<=HERO_STEP_DOWN){h.position.y=groundY;heroVel.y=0;}
    else{heroVel.y-=14*dt;h.position.y+=heroVel.y*dt;if(h.position.y<=groundY){h.position.y=groundY;heroVel.y=0;heroGrounded=true;}else heroGrounded=false;}
  }
  h.rotation.y=fpYaw;"""
    s=_once(s,old,new)

    # Re-anchor current v3 lower legs toward the rear/ankle of each paw and register contacts.
    needle="  d.userData.blueprintClass='BP_GlitchDragonV3';d.userData.tags.push('dragon-anatomy-v3','crystal-armor','fracture-energy');return d;"
    anchor=r"""{
  const lower=[],feet=[];d.traverse(o=>{if(o.name==='DragonLowerLeg')lower.push(o);if(o.name==='DragonFoot')feet.push(o);});
  for(let i=0;i<Math.min(lower.length,feet.length);i++){
    const leg=lower[i],foot=feet[i];foot.userData.dragonFoot={restY:foot.position.y};
    const rear=new THREE.Vector3(foot.position.x,foot.position.y+.10,foot.position.z+.24);
    const top=leg.position.clone().multiplyScalar(2).sub(rear),dir=rear.clone().sub(top),len=dir.length();
    leg.position.copy(top.clone().add(rear).multiplyScalar(.5));leg.scale.y=Math.max(.72,len);leg.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());
  }
}"""
    s=_once(s,needle,anchor+"\\n  "+needle)

    # Rig metadata and procedural idle/contact solver.
    marker="function addPath(name, points){"
    rig=r'''const dragonContactRay=new THREE.Raycaster();
function solidContactHeight(dragon,foot){
  dragon.updateMatrixWorld(true);const wp=new THREE.Vector3();foot.getWorldPosition(wp);
  let best=terrainHeight(wp.x,wp.z),origin=new THREE.Vector3(wp.x,wp.y+4,wp.z);
  dragonContactRay.set(origin,new THREE.Vector3(0,-1,0));dragonContactRay.far=10;
  const solids=actors.filter(a=>a!==dragon&&a.visible!==false&&a.userData.actorType!=='dragon'&&a.userData.actorType!=='hero');
  const hits=dragonContactRay.intersectObjects(solids,true);
  if(hits.length)best=Math.max(best,hits[0].point.y);
  return best;
}
function updateDragonRigs(t){
  for(const d of actors.filter(a=>a.userData.actorType==='dragon')){
    const phase=d.userData.dragonIdlePhase||0,s=d.scale.x||1;
    const chest=d.getObjectByName('DragonChest'),head=d.getObjectByName('DragonHead'),haunch=d.getObjectByName('DragonHaunch');
    if(chest)chest.scale.y=(d.userData.dragonChestBaseY||chest.scale.y)*(1+.018*Math.sin(t*1.35+phase));
    if(head){head.rotation.y=.045*Math.sin(t*.72+phase);head.rotation.x=.025*Math.sin(t*.93+phase*.7);}
    if(haunch)haunch.rotation.z=.012*Math.sin(t*.58+phase);
    const tails=[];d.traverse(o=>{if(o.name==='DragonTail'||o.name==='DragonTailTip')tails.push(o);});
    tails.forEach((q,i)=>q.rotation.y=.035*Math.sin(t*.65+phase+i*.42));
    const wings=[];d.traverse(o=>{if(o.name==='WingMembrane'||o.name==='WingArm'||o.name==='WingFinger')wings.push(o);});
    wings.forEach((q,i)=>q.rotation.z+=(.0015*Math.sin(t*.8+phase+i*.17)-q.rotation.z*.0008));
    const feet=[];d.traverse(o=>{if(o.userData.dragonFoot)feet.push(o);});
    for(const foot of feet){
      const contact=solidContactHeight(d,foot),parentY=d.position.y,localTarget=(contact-parentY)/s+.11;
      foot.position.y=THREE.MathUtils.lerp(foot.position.y,localTarget,.32);
    }
  }
}
'''
    if marker not in s: raise RuntimeError("v6.6 rig marker missing")
    s=s.replace(marker,rig+"\n"+marker,1)

    # Seed stable idle phases/base scale on both dragon constructors.
    s=_once(s,"return markActor(g,'dragon',{name,baked,colliderRadius:1.18*scale,folder:'Dragon Den/Dragons',components:['Transform','Scene','StaticMesh','Collider','BobMovement','AgentAvatar'],blueprintClass:'BP_DragonAvatarV2',componentSpeed:.42,bobAmplitude:.018,visualColor:color,role:'lalm-agent-avatar',tags:['dragon-den','agent-avatar','voice-anchor-hook','dragon-anatomy-v2']});",
      "const actor=markActor(g,'dragon',{name,baked,colliderRadius:1.18*scale,folder:'Dragon Den/Dragons',components:['Transform','Scene','StaticMesh','Collider','AgentAvatar','ProceduralIdle','FootContact'],blueprintClass:'BP_DragonAvatarV2',componentSpeed:0,bobAmplitude:0,visualColor:color,role:'lalm-agent-avatar',tags:['dragon-den','agent-avatar','voice-anchor-hook','dragon-anatomy-v2','foot-contact','procedural-idle']});actor.userData.dragonIdlePhase=Math.random()*Math.PI*2;actor.userData.dragonChestBaseY=chest.scale.y;return actor;")

    # Run dragon rig after Wisp visual animation every frame.
    s=_once(s,"updateWispVisuals(t);if(!playing)orbit.update();","updateWispVisuals(t);updateDragonRigs(t);if(!playing)orbit.update();")
    return s
