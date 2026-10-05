"""§wyrl§ Engine v5.4: Dragon's Den default Wisp avatar inspired by classic Warcraft III/Sheep Tag readability."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v5.4 patch token missing: " + old[:180])
    return s.replace(old, new, 1)

def _before(s: str, marker: str, block: str) -> str:
    i=s.find(marker)
    if i<0: raise RuntimeError("v5.4 insert marker missing: "+marker[:180])
    return s[:i]+block+s[i:]

def apply(html: str) -> str:
    s=html
    repl={
      "<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_3_GROUPS_IMMERSIVE_DEN -->":"<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_4_WISP_AVATAR -->",
      "<title>§wyrl§ Engine · Maker v5.3</title>":"<title>§wyrl§ Engine · Maker v5.4</title>",
      '<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.3</div>':'<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.4</div>',
      '<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.3 · GROUPS + DEN</div>':'<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.4 · WISP AVATAR</div>',
      "window.SWRLZ_FORGE_BUILD={version:'v5.3',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',grouping:'hierarchical'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;":
        "window.SWRLZ_FORGE_BUILD={version:'v5.4',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',grouping:'hierarchical',defaultDenAvatar:'wisp'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;",
      "version:'swyrl-engine-agent-v3.3',":"version:'swyrl-engine-agent-v3.4',",
      "editorLog('§wyrl§ Engine v5.3 initialized · hierarchical groups · immersive Den pass','ok')":
        "editorLog('§wyrl§ Engine v5.4 initialized · Dragon Den Wisp visitor avatar','ok')",
      "engine:'§wyrl§ Engine · Maker v5.3',":"engine:'§wyrl§ Engine · Maker v5.4',",
      "version:5.3,":"version:5.4,"
    }
    for a,b in repl.items(): s=_once(s,a,b)

    wisp=r"""
const wispTextureCache=new Map();
function wispGlowTexture(color='#80dfff'){
  if(wispTextureCache.has(color))return wispTextureCache.get(color);
  const c=document.createElement('canvas');c.width=c.height=128;const x=c.getContext('2d');
  const g=x.createRadialGradient(64,64,2,64,64,62);
  g.addColorStop(0,'rgba(255,255,255,1)');
  g.addColorStop(.12,'rgba(225,250,255,.98)');
  g.addColorStop(.34,color);
  g.addColorStop(.62,'rgba(70,180,255,.32)');
  g.addColorStop(1,'rgba(70,160,255,0)');
  x.fillStyle=g;x.fillRect(0,0,128,128);
  const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;wispTextureCache.set(color,tex);return tex;
}
function makeWispHero(team,pos,baked=true,name='Wisp Visitor'){
  const g=new THREE.Group(),visual=new THREE.Group();visual.name='WispVisual';g.add(visual);
  const glowColor=team==='red'?'#ff84a1':'#72d7ff',coreColor=team==='red'?'#fff0f4':'#effcff';
  const sprite=(scale,opacity=1)=>{
    const m=new THREE.SpriteMaterial({map:wispGlowTexture(glowColor),transparent:true,opacity,depthWrite:false,blending:THREE.AdditiveBlending});
    const q=new THREE.Sprite(m);q.scale.set(scale,scale,1);visual.add(q);return q;
  };
  const outer=sprite(2.15,.72);outer.name='WispOuterGlow';outer.userData.wispPulse=1;
  const inner=sprite(1.18,.95);inner.name='WispInnerGlow';
  const core=new THREE.Mesh(new THREE.SphereGeometry(.19,16,12),new THREE.MeshBasicMaterial({color:coreColor,transparent:true,opacity:.94,blending:THREE.AdditiveBlending,depthWrite:false}));
  core.name='WispCore';visual.add(core);
  const eye=new THREE.Mesh(new THREE.SphereGeometry(.07,10,8),new THREE.MeshBasicMaterial({color:'#ffffff'}));eye.position.set(0,.01,-.17);visual.add(eye);
  const arcMat=new THREE.MeshBasicMaterial({color:glowColor,transparent:true,opacity:.58,side:THREE.DoubleSide,depthWrite:false,blending:THREE.AdditiveBlending});
  for(let i=0;i<3;i++){
    const arc=new THREE.Mesh(new THREE.TorusGeometry(.48+i*.08,.025,6,34,Math.PI*(1.05+i*.13)),arcMat.clone());
    arc.position.y=-.04+i*.04;arc.rotation.set(Math.PI/2+i*.18,i*.82,i*1.35);arc.userData.wispArc=i;visual.add(arc);
  }
  for(let i=0;i<6;i++){
    const q=sprite(.38-(i*.025),.72-(i*.065));q.name='WispMote';q.userData.wispOrbit={phase:i*Math.PI*2/6,radius:.42+i*.055,speed:.72+(i%3)*.18,y:(i-2.5)*.09};
  }
  for(let i=0;i<4;i++){
    const q=sprite(.30-i*.035,.55-i*.07);q.name='WispTrail';q.userData.wispTrail={phase:i*.72,depth:.42+i*.23,side:i%2?-1:1};
  }
  const ring=new THREE.Mesh(new THREE.RingGeometry(.38,.48,40),new THREE.MeshBasicMaterial({color:glowColor,transparent:true,opacity:.34,side:THREE.DoubleSide,depthWrite:false,blending:THREE.AdditiveBlending}));
  ring.name='WispTeamGlow';ring.rotation.x=-Math.PI/2;ring.position.y=-1.02;visual.add(ring);
  const light=new THREE.PointLight(new THREE.Color(glowColor),1.35,6.5,2);light.name='WispLight';visual.add(light);
  visual.position.y=1.08;
  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);
  const o=markActor(g,'hero',{name,team,baked,maxHp:1000,attackRange:2.8,attackDamage:65,attackCooldown:.55,moveSpeed:6.0,colliderRadius:.46,folder:'Dragon Den/Visitors',components:['Transform','Scene','StaticMesh','Collider','Combat','CharacterMovement','WispVisual'],blueprintClass:'BP_WispVisitor',visualColor:glowColor,tags:['dragon-den','player-avatar','wisp-avatar','spirit-form']});
  o.userData.avatarStyle='wisp';o.userData.eyeHeight=1.18;o.userData.wispBaseY=1.08;o.userData.wispPhase=Math.random()*Math.PI*2;
  return o;
}
function updateWispVisuals(t){
  for(const h of actors.filter(a=>a.userData.avatarStyle==='wisp')){
    const v=h.getObjectByName('WispVisual');if(!v)continue;
    const phase=h.userData.wispPhase||0,base=h.userData.wispBaseY||1.08;
    v.position.y=base+Math.sin(t*2.15+phase)*.08;
    const outer=v.getObjectByName('WispOuterGlow');if(outer){const p=1+.08*Math.sin(t*3.4+phase);outer.scale.set(2.15*p,2.15*p,1);outer.material.opacity=.62+.12*Math.sin(t*2.7+phase);}
    for(const q of v.children){
      const o=q.userData.wispOrbit;if(o){const a=t*o.speed+o.phase+phase;q.position.set(Math.cos(a)*o.radius,o.y+Math.sin(a*1.7)*.13,Math.sin(a)*o.radius);}
      const tr=q.userData.wispTrail;if(tr){const a=t*.9+tr.phase+phase;q.position.set(Math.sin(a)*.22*tr.side,-.25-Math.abs(Math.sin(a*.7))*tr.depth,.28+Math.cos(a)*.16);}
      if(q.userData.wispArc!==undefined){const i=q.userData.wispArc;q.rotation.z=t*(.24+i*.07)*(i%2?-1:1)+i;}
    }
  }
}
"""
    s=_before(s,"function makeGroundActor(){",wisp)

    s=_once(
      s,
      "const visitor=makeHero('blue',[0,0,9.1],true,'Visitor / Creator');visitor.userData.folder='Dragon Den/Visitors';visitor.userData.role='human-presence';visitor.rotation.y=Math.PI;",
      "const visitor=makeWispHero('blue',[0,0,9.1],true,'Wisp Visitor / Creator');visitor.userData.folder='Dragon Den/Visitors';visitor.userData.role='player-avatar';visitor.rotation.y=Math.PI;"
    )

    s=_once(
      s,
      "id:a.userData.id, name:a.name, type:a.userData.actorType, team:a.userData.team, baked:a.userData.baked, role:a.userData.role||'', tags:[...(a.userData.tags||[])], visualColor:a.userData.visualColor||'', groupParentId:a.userData.groupParentId||null, groupChildIds:[...(a.userData.groupChildIds||[])],",
      "id:a.userData.id, name:a.name, type:a.userData.actorType, team:a.userData.team, baked:a.userData.baked, role:a.userData.role||'', tags:[...(a.userData.tags||[])], visualColor:a.userData.visualColor||'', avatarStyle:a.userData.avatarStyle||'', eyeHeight:a.userData.eyeHeight||null, groupParentId:a.userData.groupParentId||null, groupChildIds:[...(a.userData.groupChildIds||[])],"
    )
    s=_once(
      s,
      "if(d.type==='hero') o = makeHero(d.team||'blue',[d.position[0],0,d.position[2]], d.baked!==false, d.name);",
      "if(d.type==='hero') o = d.avatarStyle==='wisp'?makeWispHero(d.team||'blue',[d.position[0],0,d.position[2]],d.baked!==false,d.name):makeHero(d.team||'blue',[d.position[0],0,d.position[2]], d.baked!==false, d.name);"
    )
    s=_once(
      s,
      "o.userData.colliderRadius=d.colliderRadius??o.userData.colliderRadius; o.userData.mass=d.mass??1;",
      "o.userData.avatarStyle=d.avatarStyle||o.userData.avatarStyle||'';o.userData.eyeHeight=d.eyeHeight||o.userData.eyeHeight||null;o.userData.colliderRadius=d.colliderRadius??o.userData.colliderRadius; o.userData.mass=d.mass??1;"
    )

    # First-person body hiding must include sprites, not only meshes.
    s=_once(
      s,
      "    if(!o.isMesh)return;",
      "    if(!(o.isMesh||o.isSprite||o.isPoints||o.isLine))return;"
    )

    # Wisp eye height is lower than the old humanoid capsule.
    s=_once(
      s,
      "    const focus=currentProject.kind==='dragons-den'?new THREE.Vector3(0,h.position.y+FP_EYE_HEIGHT,1.5):new THREE.Vector3(0,h.position.y+FP_EYE_HEIGHT,0);",
      "    const eyeHeight=h.userData.eyeHeight||FP_EYE_HEIGHT;const focus=currentProject.kind==='dragons-den'?new THREE.Vector3(0,h.position.y+eyeHeight,1.5):new THREE.Vector3(0,h.position.y+eyeHeight,0);"
    )
    s=_once(
      s,
      "    perspectiveCamera.position.set(h.position.x,h.position.y+FP_EYE_HEIGHT,h.position.z);",
      "    perspectiveCamera.position.set(h.position.x,h.position.y+eyeHeight,h.position.z);"
    )
    s=_once(
      s,
      "  const eye=new THREE.Vector3(h.position.x,h.position.y+FP_EYE_HEIGHT,h.position.z);",
      "  const eyeHeight=h.userData.eyeHeight||FP_EYE_HEIGHT;const eye=new THREE.Vector3(h.position.x,h.position.y+eyeHeight,h.position.z);"
    )
    s=_once(
      s,
      "  resolveHeroCollision(next,0.55);h.position.x=next.x;h.position.z=next.z;",
      "  resolveHeroCollision(next,h.userData.colliderRadius||0.55);h.position.x=next.x;h.position.z=next.z;"
    )

    # Wisp visual continues to breathe and orbit in editor and simulate views.
    s=_once(
      s,
      "  if(!playing)orbit.update();if(selectionBox&&selected)selectionBox.update();renderer.render(scene,camera);",
      "  updateWispVisuals(t);if(!playing)orbit.update();if(selectionBox&&selected)selectionBox.update();renderer.render(scene,camera);"
    )

    return s
