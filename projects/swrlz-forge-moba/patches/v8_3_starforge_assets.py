"""Reusable floating-workspace assets and serialized environment settings.

Scene placement remains native editor/project data. No starter layout is built
by this patch; it equips the editor to author an open celestial workspace.
"""


def once(s, old, new):
    if s.count(old) != 1:
        raise RuntimeError("v8.3 celestial asset anchor missing: " + old[:110])
    return s.replace(old, new, 1)


GEOMETRY = r"""
  if(kind==='floatingIsland'){
    // Finished top is local Y=0; X/Z scaling sets the island radius.
    const cap=new THREE.Mesh(new THREE.CylinderGeometry(1,1,.18,16),mat('#48596a'));cap.position.y=-.09;cap.castShadow=cap.receiveShadow=true;g.add(cap);
    const root=new THREE.Mesh(new THREE.CylinderGeometry(.95,.28,1.55,7),mat('#263545'));root.position.y=-.9;root.rotation.y=.21;root.castShadow=true;g.add(root);
    const tip=new THREE.Mesh(new THREE.ConeGeometry(.28,.8,5),mat('#30495d'));tip.rotation.z=Math.PI;tip.position.y=-2.02;g.add(tip);
    const rim=new THREE.Mesh(new THREE.TorusGeometry(.975,.009,4,48),glowMat(color,.3));rim.rotation.x=Math.PI/2;rim.position.y=.005;g.add(rim);
  }else if(kind==='constellationDome'){
    // Static points require one draw call and no animated camera motion.
    const xyz=[],rgb=[];
    for(let i=0;i<280;i++){const t=i*2.3999632297,u=.05+.9*((i*.61803398875)%1),r=44,rad=Math.sqrt(1-u*u),c=new THREE.Color(i%7===0?'#d9ba80':i%3===0?'#76abbc':'#c6d6eb');xyz.push(Math.cos(t)*r*rad,12+r*u,Math.sin(t)*r*rad);rgb.push(c.r,c.g,c.b);}
    const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(xyz,3));geo.setAttribute('color',new THREE.Float32BufferAttribute(rgb,3));const stars=new THREE.Points(geo,new THREE.PointsMaterial({size:.14,vertexColors:true,sizeAttenuation:true,fog:false}));g.add(stars);
    const pts=[];for(const p of [[-12,24,-26],[-7,28,-29],[0,26,-30],[7,31,-28],[13,27,-24]])pts.push(new THREE.Vector3(...p));g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color:'#436372',transparent:true,opacity:.55,fog:false})));
  }else if(kind==='astrolabe'){
    const base=new THREE.Mesh(new THREE.CylinderGeometry(.7,.9,.2,12),mat('#344253'));base.position.y=.1;g.add(base);
    const brass=mat('#af9870');for(const [x,y,z] of [[0,0,0],[Math.PI/2,0,0],[.7,.55,.6]]){const ring=new THREE.Mesh(new THREE.TorusGeometry(1.05,.035,6,48),brass);ring.rotation.set(x,y,z);ring.position.y=1.35;g.add(ring);}
    const core=new THREE.Mesh(new THREE.SphereGeometry(.25,14,10),glowMat('#9dc9d2',.65));core.position.y=1.35;g.add(core);
    for(let i=0;i<7;i++){const q=new THREE.Mesh(new THREE.SphereGeometry(.055,6,4),glowMat('#dac49a',.4)),t=i*2.399963;q.position.set(Math.cos(t)*.87,1.35+Math.sin(t*.7)*.5,Math.sin(t)*.87);g.add(q);}
  }else
"""


ENVIRONMENT = r"""
function applyEnvironmentSettings(){
  const e=currentProject.environmentSettings||{};
  const background=/^#[0-9a-f]{6}$/i.test(String(e.background||''))?e.background:null;
  if(background)setProjectBackground(background);
  scene.fog.near=Number.isFinite(Number(e.fogNear))?Math.max(0,Number(e.fogNear)):16;
  scene.fog.far=Number.isFinite(Number(e.fogFar))?Math.max(scene.fog.near+1,Number(e.fogFar)):62;
  renderer.toneMappingExposure=Number.isFinite(Number(e.exposure))?THREE.MathUtils.clamp(Number(e.exposure),.2,3):1.08;
  const terrainVisible=e.showTerrain!==false;
  if(terrainMesh)terrainMesh.visible=terrainVisible;terrainShellGroup.visible=terrainVisible;
  waterGroup.visible=e.showScenery!==false&&currentProject.environment!=='spatial-workspace';
}
"""


def apply(html):
    s = html
    s = once(s, "function applyProjectMeta(meta={}){", ENVIRONMENT + "\nfunction applyProjectMeta(meta={}){")
    s = once(s, "  document.body.dataset.projectKind=currentProject.kind;", "  document.body.dataset.projectKind=currentProject.kind;\n  applyEnvironmentSettings();")
    s = once(s, "function terrainHeight(x,z){\n  if(currentProject?.environment==='dragon-den')", "function terrainHeight(x,z){\n  if(currentProject?.environment==='spatial-workspace')return 0;\n  if(currentProject?.environment==='dragon-den')")
    s = once(s, "  buildTerrainShell();\n}", "  buildTerrainShell();applyEnvironmentSettings();\n}")
    s = once(s, "function buildSceneryExtras(){\n  clearGroup(waterGroup);", "function buildSceneryExtras(){\n  clearGroup(waterGroup);if(currentProject.environment==='spatial-workspace'||currentProject.environmentSettings?.showScenery===false)return;")
    s = once(s, "  if(kind==='vaultCanopy'){", GEOMETRY + "  if(kind==='vaultCanopy'){")
    s = once(s, "['ramp','galleryDeck'].includes(kind)", "['ramp','galleryDeck','floatingIsland'].includes(kind)")
    s = once(s, "  if(type==='hero') o = makeHero('blue',[0,0,0], false, 'Ghost Hero');", """  if(type==='hero') o = makeHero('blue',[0,0,0], false, 'Ghost Hero');
  if(type==='workspaceVisitor'){o=makeHero('blue',[0,0,0],false,'Workspace Visitor');o.userData.moveSpeed=2.8;o.userData.maxHp=0;o.userData.hp=0;o.userData.attackDamage=0;o.userData.eyeHeight=1.62;}
  if(type==='companionWisp'){o=makeWispHero('neutral',[0,0,0],false,'Companion Wisp');o.userData.role='agent-avatar';o.userData.colliderRadius=0;}
  if(type==='floatingIsland')o=makeDenStructure('floatingIsland',[0,0,0],false,'Floating Island','#9abec7');
  if(type==='constellationDome')o=makeDenStructure('constellationDome',[0,0,0],false,'Constellation Sky','#9abec7');
  if(type==='astrolabe')o=makeDenStructure('astrolabe',[0,0,0],false,'Astrolabe','#d8bd89');""")
    s = once(s, "const ASSET_LIBRARY=[", """const ASSET_LIBRARY=[
 {id:'floatingIsland',name:'Floating Island',path:'/Engine/Architecture',desc:'Walkable 2m-wide island; scale X/Z for radius, finished top at local Y=0'},
 {id:'constellationDome',name:'Constellation Sky',path:'/Engine/Environment',desc:'Static star field and quiet constellation; no collision'},
 {id:'astrolabe',name:'Astrolabe',path:'/Engine/Workspace',desc:'Brass armillary landmark for an observatory'},
 {id:'workspaceVisitor',name:'Workspace Visitor',path:'/Engine/Gameplay',desc:'Walking visitor with a 1.62m eye height and no combat'},
 {id:'companionWisp',name:'Companion Wisp',path:'/Engine/Workspace',desc:'Neutral stationary wisp for a companion station'},""")
    # Scene background and freshly built terrain both honor imported settings.
    s = once(s, "  $('waveInterval').value = p.scene.waveInterval || 7;", "  $('waveInterval').value = p.scene.waveInterval || 7;applyEnvironmentSettings();")
    s = once(s, "$('bgColor').oninput = ()=>{ scene.background.set($('bgColor').value); scene.fog.color.set($('bgColor').value); };", "$('bgColor').oninput = ()=>{ scene.background.set($('bgColor').value); scene.fog.color.set($('bgColor').value); if(currentProject.environmentSettings)currentProject.environmentSettings.background=$('bgColor').value;markDirty(); };")
    return s
