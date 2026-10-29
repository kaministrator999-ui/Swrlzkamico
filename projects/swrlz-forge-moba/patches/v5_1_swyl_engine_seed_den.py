"""§wyrl§ Engine v5.1: rename the engine maker and make Dragon's Den Seed Chamber the default starter world."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v5.1 patch token missing: " + old[:160])
    return s.replace(old, new, 1)

def _before(s: str, marker: str, block: str) -> str:
    i = s.find(marker)
    if i < 0:
        raise RuntimeError("v5.1 insert marker missing: " + marker[:160])
    return s[:i] + block + s[i:]

def _replace_block(s: str, start: str, end: str, block: str) -> str:
    a = s.find(start)
    if a < 0:
        raise RuntimeError("v5.1 block start missing: " + start[:160])
    b = s.find(end, a)
    if b < 0:
        raise RuntimeError("v5.1 block end missing: " + end[:160])
    return s[:a] + block + s[b:]

def apply(html: str) -> str:
    s = html

    replacements = {
        "<!-- SWRLZ_FORGE_DEPLOY_MARKER: V5_PROJECT_TEMPLATES_DRAGONS_DEN -->":
            "<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_1_SEED_DEN -->",
        "<title>SWRLZ Forge · Editor v5</title>":
            "<title>§wyrl§ Engine · Maker v5.1</title>",
        '<div class="brand"><b>SWRLZ</b> FORGE · EDITOR v5</div>':
            '<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.1</div>',
        '<div class="build-stamp" id="buildStamp">FORGE v5 · PROJECT SYSTEM</div>':
            '<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.1 · SEED DEN</div>',
        '<div class="project-head"><b>◫ SWRLZ Forge Projects</b><small>Templates create independent editable project state.</small><button id="projectClose">×</button></div>':
            '<div class="project-head"><b>◫ §wyrl§ Engine Projects</b><small>Create, edit, save, load, inhabit.</small><button id="projectClose">×</button></div>',
        "let currentProject={name:'Starter World',template:'default',kind:'sandbox',environment:'starter'};":
            "let currentProject={name:\"Dragon's Den — Seed Chamber\",template:'dragons-den',kind:'dragons-den',environment:'dragon-den'};",
        "engine:'SWRLZ Forge · Editor v5',":
            "engine:'§wyrl§ Engine · Maker v5.1',",
        "version:5,":
            "version:5.1,",
        "saveBlob(safeProjectName()+'.forge.json'":
            "saveBlob(safeProjectName()+'.swyrl.json'",
        "saveBlob('swrlz-forge-playable-v5.html'":
            "saveBlob('swyrl-engine-playable-v5-1.html'",
        "<title>SWRLZ Forge v5 Playable</title>":
            "<title>§wyrl§ Engine v5.1 Playable</title>",
        "<b>SWRLZ Forge v5 Playable</b>":
            "<b>§wyrl§ Engine v5.1 Playable</b>",
        "version:'forge-agent-v3',":
            "version:'swyrl-engine-agent-v3.1',",
        "return (currentProject.name||'forge-project').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'forge-project';":
            "return (currentProject.name||'swyrl-engine-project').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'swyrl-engine-project';",
    }
    for old, new in replacements.items():
        s = _once(s, old, new)

    cards_old = """<button class="project-card" data-project-template="default"><span class="project-icon">🧰</span><strong>Starter World</strong><span class="template-tag">DEFAULT</span><p>Neutral Forge sandbox: terrain, river, pawn, physics prop and component examples. No MOBA rules.</p><span class="hint">Create fresh starter project</span></button>
            <button class="project-card moba" data-project-template="moba"><span class="project-icon">⚔️</span><strong>MOBA Arena</strong><span class="template-tag">EXAMPLE PROJECT</span><p>The original three-lane Forge MOBA, now isolated as a project template instead of being the engine itself.</p><span class="hint">Create MOBA example</span></button>
            <button class="project-card den" data-project-template="dragons-den"><span class="project-icon">🐉</span><strong>Dragon's Den</strong><span class="template-tag">EXAMPLE PROJECT</span><p>Arcane collaborative LALM world with dragon avatars, council dais, memory crystal, portals, runes and agent anchor roles.</p><span class="hint den-glow">Enter the Den</span></button>"""
    cards_new = """<button class="project-card den" data-project-template="dragons-den"><span class="project-icon">🐉</span><strong>Dragon's Den — Seed Chamber</strong><span class="template-tag">DEFAULT STARTER</span><p>Immersive under-realm seed chamber: wake nook, council floor, throne side, dragon perch, creator alcove, and exits to future deeper systems.</p><span class="hint den-glow">Wake up in the Den</span></button>
            <button class="project-card" data-project-template="default"><span class="project-icon">🧰</span><strong>Blank Starter World</strong><span class="template-tag">TEMPLATE</span><p>Neutral §wyrl§ Engine sandbox with terrain, pawn, physics and component examples.</p><span class="hint">Create blank project</span></button>
            <button class="project-card moba" data-project-template="moba"><span class="project-icon">⚔️</span><strong>MOBA Arena</strong><span class="template-tag">EXAMPLE PROJECT</span><p>The original three-lane MOBA remains a loadable example project, separate from the engine and the Den.</p><span class="hint">Create MOBA example</span></button>"""
    s = _once(s, cards_old, cards_new)

    s = _once(s, '<div id="currentProjectName" class="project-nameplate">Starter World</div>',
                 '<div id="currentProjectName" class="project-nameplate">Dragon\'s Den — Seed Chamber</div>')
    s = _once(s, '<span id="projectStatus" class="status-pill">Starter World</span>',
                 '<span id="projectStatus" class="status-pill">Dragon\'s Den — Seed Chamber</span>')

    s = _once(
        s,
        "return {ground:'▱', tower:'🏰', base:'💎', spawner:'⚔', camp:'👹', bush:'🌿', wall:'🧱', rock:'🪨', hero:'🦸', tree:'🌲', dragon:'🐉', crystal:'🔮', portal:'🌀', throne:'♛', pedestal:'◉'}[type] || '◆';",
        "return {ground:'▱', tower:'🏰', base:'💎', spawner:'⚔', camp:'👹', bush:'🌿', wall:'🧱', rock:'🪨', hero:'🦸', tree:'🌲', dragon:'🐉', crystal:'🔮', portal:'🌀', throne:'♛', pedestal:'◉', denStructure:'▰'}[type] || '◆';"
    )

    den_structure = r"""
function makeDenStructure(kind,pos=[0,0,0],baked=true,name='Den Structure',color='#6f5b82'){
  const g=new THREE.Group();
  const stone=mat('#2d2a33'),concrete=mat('#4a4851'),wood=mat('#5b3f2f'),cloth=mat('#5b244f'),warm=glowMat('#ffb45f',1.25),arcane=glowMat(color,.7);
  const box=(w,h,d,m,x=0,y=0,z=0)=>{const q=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);q.position.set(x,y,z);q.castShadow=q.receiveShadow=true;g.add(q);return q;};
  if(kind==='ceiling'){
    const ceiling=new THREE.Mesh(new THREE.PlaneGeometry(40,31),new THREE.MeshStandardMaterial({color:0x24242b,roughness:1,metalness:0,side:THREE.BackSide}));
    ceiling.rotation.x=-Math.PI/2;ceiling.position.y=10.8;ceiling.receiveShadow=true;g.add(ceiling);
    for(const x of [-14,-7,0,7,14])box(2.0,.65,30,concrete,x,10.35,0);
  }else if(kind==='arch'){
    box(1.2,5.4,1.4,stone,-2.5,2.7,0);box(1.2,5.4,1.4,stone,2.5,2.7,0);box(6.2,1.1,1.5,stone,0,5.15,0);
    const rune=new THREE.Mesh(new THREE.TorusGeometry(1.25,.08,8,36),arcane);rune.position.set(0,3.2,-.76);g.add(rune);
  }else if(kind==='perch'){
    box(7.6,1.0,5.8,stone,0,.5,0);box(6.4,.7,4.6,concrete,0,1.28,0);
    for(const x of [-2.6,2.6]){const r=new THREE.Mesh(new THREE.DodecahedronGeometry(1.35),stone.clone());r.position.set(x,2.15,.6);r.scale.set(1.5,1.15,1.3);r.castShadow=true;g.add(r);}
  }else if(kind==='throneTerrace'){
    box(8.2,.65,6.5,stone,0,.33,0);box(6.8,.55,5.2,concrete,0,.92,0);box(5.2,.5,3.9,stone,0,1.44,0);
    for(const x of [-3.2,3.2]){const c=new THREE.Mesh(new THREE.CylinderGeometry(.28,.38,3.2,7),arcane.clone());c.position.set(x,2.25,1.6);g.add(c);}
  }else if(kind==='wakeNook'){
    box(9,.32,6.4,stone,0,.16,0);box(6.3,.12,4.5,cloth,0,.38,.25);box(3.9,.42,2.2,wood,-1.2,.68,.55);box(3.45,.22,1.85,mat('#82706e'),-1.2,1.0,.55);
    box(1.0,1.1,1.0,wood,3.15,.72,.9);box(1.35,.9,1.05,wood,2.85,.58,-1.1);
    for(const x of [-3.7,3.7]){const orb=new THREE.Mesh(new THREE.SphereGeometry(.16,8,6),warm.clone());orb.position.set(x,1.25,-1.8);g.add(orb);const l=new THREE.PointLight(0xffad5f,.8,8,2);l.position.copy(orb.position);g.add(l);}
  }else if(kind==='creatorAlcove'){
    box(8,.35,6,stone,0,.18,0);box(5.4,.25,1.55,wood,0,1.15,-1.45);box(.25,1.15,1.4,wood,-2.1,.62,-1.45);box(.25,1.15,1.4,wood,2.1,.62,-1.45);
    for(const x of [-1.55,0,1.55]){const screen=box(1.25,.8,.08,glowMat(x===0?'#68d9ff':'#a875ff',.75),x,2.05,-1.78);screen.rotation.x=-.08;}
    const lamp=new THREE.PointLight(0x66cfff,.75,8,2);lamp.position.set(0,2.5,-.6);g.add(lamp);
    box(5.2,.08,3.7,mat('#4a244c'),0,.39,.6);
  }else if(kind==='walkway'){
    box(7.5,.25,2.5,concrete,0,.12,0);const stripe=box(6.8,.035,.16,arcane,0,.27,0);
  }else if(kind==='lantern'){
    const post=new THREE.Mesh(new THREE.CylinderGeometry(.09,.14,1.5,7),stone);post.position.y=.75;g.add(post);
    const orb=new THREE.Mesh(new THREE.SphereGeometry(.18,10,8),warm);orb.position.y=1.6;g.add(orb);const l=new THREE.PointLight(0xffa95b,.9,7,2);l.position.y=1.6;g.add(l);
  }
  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);
  const collider=kind==='perch'?3.2:kind==='throneTerrace'?3.0:kind==='arch'?2.0:0;
  return markActor(g,'denStructure',{name,baked,colliderRadius:collider,folder:"Dragon Den/Architecture",components:['Transform','Scene','StaticMesh'].concat(collider?['Collider']:[]),blueprintClass:'DEN_'+kind,visualColor:color,tags:['dragon-den','architecture',kind]});
}
"""
    s = _before(s, "function makeDragon(pos", den_structure)

    dragon_block = r"""function makeDragon(pos,color='#9b6cff',baked=true,name='Dragon Avatar',scale=1){
  const g=new THREE.Group(),skin=mat(color),dark=mat('#211929'),glow=glowMat(color,.9);
  const body=new THREE.Mesh(new THREE.CapsuleGeometry(.72,2.35,7,12),skin);body.position.set(0,2.25,.35);body.rotation.x=-.22;body.castShadow=true;g.add(body);
  const chest=new THREE.Mesh(new THREE.SphereGeometry(.86,12,9),dark);chest.position.set(0,2.25,-.4);chest.scale.set(1,1.1,.8);g.add(chest);
  const neck=new THREE.Mesh(new THREE.CylinderGeometry(.34,.58,2.25,9),skin.clone());neck.position.set(0,3.65,-.72);neck.rotation.x=-.34;neck.castShadow=true;g.add(neck);
  const head=new THREE.Mesh(new THREE.DodecahedronGeometry(.7),skin.clone());head.position.set(0,4.62,-1.25);head.scale.set(1.05,.82,1.28);head.castShadow=true;g.add(head);
  const snout=new THREE.Mesh(new THREE.BoxGeometry(.72,.38,1.0),dark.clone());snout.position.set(0,4.42,-2.0);snout.rotation.x=-.08;g.add(snout);
  const jaw=new THREE.Mesh(new THREE.BoxGeometry(.62,.16,.82),dark.clone());jaw.position.set(0,4.18,-1.94);jaw.rotation.x=.10;g.add(jaw);
  const wingShape=new THREE.Shape();wingShape.moveTo(0,0);wingShape.lineTo(2.1,1.75);wingShape.lineTo(4.15,1.15);wingShape.lineTo(3.15,.1);wingShape.lineTo(4.4,-1.15);wingShape.lineTo(1.7,-.72);wingShape.lineTo(0,0);
  const wingGeo=new THREE.ShapeGeometry(wingShape),wingMat=new THREE.MeshStandardMaterial({color:new THREE.Color(color),roughness:.72,metalness:.05,side:THREE.DoubleSide,flatShading:true});
  for(const side of [-1,1]){const w=new THREE.Mesh(wingGeo,wingMat.clone());w.position.set(side*.62,3.2,.15);w.scale.x=side;w.rotation.set(-.12,side*.22,side*.10);w.castShadow=true;g.add(w);const bone=new THREE.Mesh(new THREE.CylinderGeometry(.07,.11,4.0,6),dark.clone());bone.position.set(side*1.72,3.5,.18);bone.rotation.z=side*1.05;g.add(bone);}
  for(const side of [-1,1])for(const front of [-.6,.75]){const leg=new THREE.Mesh(new THREE.CylinderGeometry(.18,.25,1.45,7),skin.clone());leg.position.set(side*.62,1.15,front);leg.rotation.z=side*.16;leg.castShadow=true;g.add(leg);const foot=new THREE.Mesh(new THREE.BoxGeometry(.42,.2,.72),dark.clone());foot.position.set(side*.66,.38,front-.24);g.add(foot);}
  const tail1=new THREE.Mesh(new THREE.ConeGeometry(.43,3.7,8),skin.clone());tail1.position.set(0,1.95,2.45);tail1.rotation.x=Math.PI/2;g.add(tail1);
  const tail2=new THREE.Mesh(new THREE.ConeGeometry(.22,2.7,7),dark.clone());tail2.position.set(.35,1.45,4.95);tail2.rotation.set(Math.PI/2,0,-.18);g.add(tail2);
  for(let i=0;i<5;i++){const spine=new THREE.Mesh(new THREE.ConeGeometry(.14,.72,5),glow.clone());spine.position.set(0,4.7-i*.55,-.45+i*.55);spine.rotation.x=.18;g.add(spine);}
  for(const x of [-.34,.34]){const horn=new THREE.Mesh(new THREE.ConeGeometry(.15,1.05,6),glow.clone());horn.position.set(x,5.28,-1.05);horn.rotation.x=-.32;horn.rotation.z=x<0?-.18:.18;g.add(horn);const eye=new THREE.Mesh(new THREE.SphereGeometry(.09,8,6),glow.clone());eye.position.set(x*.68,4.7,-1.9);g.add(eye);}
  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);g.scale.setScalar(scale);
  return markActor(g,'dragon',{name,baked,colliderRadius:1.25*scale,folder:'Dragon Den/Dragons',components:['Transform','Scene','StaticMesh','Collider','BobMovement','AgentAvatar'],blueprintClass:'BP_DragonAvatar',componentSpeed:.55,bobAmplitude:.035,visualColor:color,role:'lalm-agent-avatar',tags:['dragon-den','agent-avatar','voice-anchor-hook']});
}

"""
    s = _replace_block(s, "function makeDragon(pos", "function addPath(name, points){", dragon_block)

    den_build = r"""function buildDragonsDenProject(){
  clearAll();applyProjectMeta({name:"Dragon's Den — Seed Chamber",template:'dragons-den',kind:'dragons-den',environment:'dragon-den'});setProjectBackground('#05030b');rebuildTerrain();makeGroundActor();clearGroup(waterGroup);

  // The Seed Chamber is an immersive place first: no launch pad, no MOBA scenery, no open-field composition.
  const ceiling=makeDenStructure('ceiling',[0,0,0],true,'Seed Chamber Ceiling','#40364d');ceiling.userData.role='den-ceiling';

  // Dense perimeter = enclosed den. Gaps intentionally line up with deeper-room exits.
  const wallPoints=[
    [-19,-14],[-15,-15],[-10,-15],[-5,-15],[5,-15],[10,-15],[15,-15],[19,-13],
    [20,-9],[20,-4],[20,2],[20,7],[19,12],[15,15],[10,16],[5,16],[-5,16],[-10,16],[-15,15],[-19,12],
    [-20,8],[-20,3],[-20,-3],[-20,-8]
  ];
  wallPoints.forEach((p,i)=>{const rock=makeRock([p[0],0,p[1]],[2.5+(i%3)*.3,4.7+(i%4)*.65,2.4+(i%2)*.35],true,'Cavern Wall '+String(i+1));rock.userData.folder='Dragon Den/Cavern Shell';rock.userData.tags=['dragon-den','cavern-shell'];});

  // Under-bridge ancestry: concrete ribs cross the chamber overhead without turning the space into an outdoor map.
  for(const z of [-10,-2,6]){const rib=makeDenStructure('walkway',[0,0,z],true,'Overhead Concrete Rib','#51515b');rib.position.y=9.1;rib.rotation.y=Math.PI/2;rib.scale.set(1.0,2.0,4.7);rib.userData.role='ceiling-rib';rib.userData.colliderRadius=0;}

  // Human-scale wake point: where a person "wakes up" inside the Den.
  const wake=makeDenStructure('wakeNook',[0,0,12.6],true,'Wake Nook','#ff9d66');wake.userData.role='wake-nook';
  const visitor=makeHero('blue',[0,0,10.0],true,'Visitor / Creator');visitor.userData.folder='Dragon Den/Visitors';visitor.userData.role='human-presence';visitor.rotation.y=Math.PI;

  // Main chamber / council floor.
  const dais=makePedestal([0,0,1.5],'#9d72ff',true,'Council Rune Dais',5.2);dais.userData.role='council-center';dais.userData.folder='Dragon Den/Main Chamber';
  const memory=makeCrystal([0,0,1.5],'#d49bff',true,'Memory Crystal',1.65);memory.userData.role='memory-anchor';memory.userData.tags.push('memory-hook','council-center');

  // Creator alcove: actual work/computing side of the den.
  const creator=makeDenStructure('creatorAlcove',[-10.8,0,7.1],true,'Creator Alcove','#61cfff');creator.rotation.y=.18;creator.userData.role='creator-workspace';
  const forgeCore=makeCrystal([-10.8,0,4.1],'#56d7ff',true,'Forge Workspace Core',.9);forgeCore.userData.role='world-builder-interface';

  // Throne side and dragon perch are elevated architecture, not props dropped on a field.
  const terrace=makeDenStructure('throneTerrace',[8.7,0,-8.2],true,'Throne Terrace','#d49bff');terrace.rotation.y=-.18;terrace.userData.role='throne-side';
  const throne=makeThrone([8.7,0,-8.7],'#d49bff',true,'Kamilion Throne');throne.position.y+=1.75;throne.rotation.y=Math.PI;throne.userData.role='human-author-seat';throne.userData.folder='Dragon Den/Throne Side';

  const perch=makeDenStructure('perch',[10.7,0,-.8],true,'Primary Dragon Perch','#9e70ff');perch.rotation.y=-.28;perch.userData.role='dragon-perch';
  const sw=makeDragon([10.5,0,-1.3],'#9e70ff',true,'§wyrl§ Dragon',2.05);sw.position.y+=2.2;sw.rotation.y=-1.45;sw.userData.role='primary-lalm-avatar';
  const forge=makeDragon([-13.0,0,-2.7],'#56d7ff',true,'Forge Dragon',1.55);forge.position.y+=1.15;forge.rotation.y=1.28;forge.userData.role='world-builder-agent';
  const coder=makeDragon([-10.6,0,7.3],'#ff8b55',true,'Coder Dragon',1.25);coder.position.y+=.65;coder.rotation.y=.38;coder.userData.role='coding-reasoner-agent';

  // Three deeper-world exits from the concept board. They are architectural/dormant in v5.1.
  const portalHall=makeDenStructure('arch',[-10.2,0,-10.6],true,'Portal Hall Exit','#a86cff');portalHall.rotation.y=.35;portalHall.userData.role='portal-hall-exit';portalHall.userData.tags.push('dormant-exit');
  const memoryExit=makeDenStructure('arch',[0,0,-13.0],true,'Memory Vault Exit','#6fb7ff');memoryExit.userData.role='memory-vault-exit';memoryExit.userData.tags.push('dormant-exit');
  const inferenceExit=makeDenStructure('arch',[11.6,0,8.0],true,'Inference Core Exit','#59f0c0');inferenceExit.rotation.y=-.62;inferenceExit.userData.role='inference-core-exit';inferenceExit.userData.tags.push('dormant-exit');

  const voice=makeCrystal([-4.8,0,-5.3],'#ff75cf',true,'Spatial Voice Anchor',.8);voice.userData.role='spatial-voice-hook';
  const inference=makeCrystal([8.0,0,6.1],'#65f6c1',true,'Inference Core',1.0);inference.userData.role='lalm-inference-hook';

  // Warm lamps make the under-bridge seed chamber feel inhabited.
  for(const p of [[-5,9],[5,9],[-6,3],[6,3],[-8,-6],[5,-7]]){const l=makeDenStructure('lantern',[p[0],0,p[1]],true,'Den Lantern','#ffb45f');l.userData.folder='Dragon Den/Lighting';}

  // Crystal veins / landmarks guide the person through the chamber.
  for(const cfg of [[-15,5,'#5ccfff'],[15,4,'#b36cff'],[-14,-8,'#ff5fc9'],[14,-9,'#62ffc6'],[-4,-11,'#6fb7ff'],[5,12,'#d49bff']]){const c=makeCrystal([cfg[0],0,cfg[1]],cfg[2],true,'Cavern Crystal',.72);c.userData.folder='Dragon Den/Crystals';}

  finishTemplate('hero');
  orbit.target.set(0,2,1);perspectiveCamera.position.set(20,12,25);orbit.update();
  toast("Welcome to Dragon's Den — Seed Chamber. 🐉");
}
"""
    s = _replace_block(s, "function buildDragonsDenProject(){", "function inferProjectMeta(p){", den_build)

    s = _once(
        s,
        "  if(d.type==='pedestal') o = makePedestal([d.position[0],0,d.position[2]],d.visualColor||'#a76dff',d.baked!==false,d.name,2.3);",
        "  if(d.type==='pedestal') o = makePedestal([d.position[0],0,d.position[2]],d.visualColor||'#a76dff',d.baked!==false,d.name,2.3);\n  if(d.type==='denStructure') o = makeDenStructure((d.blueprintClass||'DEN_walkway').replace(/^DEN_/,''),[d.position[0],0,d.position[2]],d.baked!==false,d.name,d.visualColor||'#6f5b82');"
    )

    s = _once(
        s,
        "  if(type==='pedestal') o = makePedestal([0,0,0],'#a76dff',false,'Ghost Pedestal',2.3);",
        "  if(type==='pedestal') o = makePedestal([0,0,0],'#a76dff',false,'Ghost Pedestal',2.3);\n"
        "  if(type==='denArch') o = makeDenStructure('arch',[0,0,0],false,'Ghost Den Arch','#9d72ff');\n"
        "  if(type==='denPerch') o = makeDenStructure('perch',[0,0,0],false,'Ghost Dragon Perch','#9d72ff');\n"
        "  if(type==='denNook') o = makeDenStructure('wakeNook',[0,0,0],false,'Ghost Wake Nook','#ff9d66');\n"
        "  if(type==='denWorkbench') o = makeDenStructure('creatorAlcove',[0,0,0],false,'Ghost Creator Alcove','#61cfff');"
    )

    s = _once(
        s,
        "{id:'dragon',name:'BP_DragonAvatar',path:'/Examples/DragonsDen',desc:'Embodied LALM dragon avatar'}, {id:'crystal',name:'Arcane Crystal',path:'/Examples/DragonsDen',desc:'Animated memory/inference anchor'}, {id:'portal',name:'Arcane Portal',path:'/Examples/DragonsDen',desc:'World/interface portal actor'}, {id:'throne',name:'Dragon Throne',path:'/Examples/DragonsDen',desc:'Den architecture'}, {id:'pedestal',name:'Rune Pedestal',path:'/Examples/DragonsDen',desc:'Council dais / rune platform'}",
        "{id:'dragon',name:'BP_DragonAvatar',path:'/Examples/DragonsDen',desc:'Embodied LALM dragon avatar'}, {id:'crystal',name:'Arcane Crystal',path:'/Examples/DragonsDen',desc:'Memory/inference anchor'}, {id:'throne',name:'Dragon Throne',path:'/Examples/DragonsDen',desc:'Den architecture'}, {id:'pedestal',name:'Rune Pedestal',path:'/Examples/DragonsDen',desc:'Council dais'}, {id:'denArch',name:'Den Exit Arch',path:'/Examples/DragonsDen/Architecture',desc:'Dormant deeper-room exit'}, {id:'denPerch',name:'Dragon Perch',path:'/Examples/DragonsDen/Architecture',desc:'Elevated dragon resting platform'}, {id:'denNook',name:'Wake Nook',path:'/Examples/DragonsDen/Architecture',desc:'Cozy human-scale den nook'}, {id:'denWorkbench',name:'Creator Alcove',path:'/Examples/DragonsDen/Architecture',desc:'Spatial coding/build workspace'}"
    )

    s = _once(
        s,
        "return actors.filter(a => a.userData.baked && ['tower','base','camp','rock','wall','tree'].includes(a.userData.actorType) && a.visible !== false);",
        "return actors.filter(a => a.userData.baked && ['tower','base','camp','rock','wall','tree','denStructure'].includes(a.userData.actorType) && (a.userData.colliderRadius||0)>0 && a.visible !== false);"
    )

    s = _once(
        s,
        "editorLog('Forge v5 editor initialized · project templates · Dragon Den · MOBA decoupled','ok')",
        "editorLog('§wyrl§ Engine v5.1 initialized · Dragon Den Seed Chamber default · project templates active','ok')"
    )
    s = _once(
        s,
        "buildDefaultProject();refreshAssetList();initializeHistory('Initial Starter World');setCameraView('perspective');",
        "buildDragonsDenProject();refreshAssetList();initializeHistory(\"Initial Dragon's Den — Seed Chamber\");setCameraView('perspective');"
    )

    # Compatibility aliases: keep legacy integrations working while exposing the new engine name.
    s = _once(
        s,
        "window.SWRLZ_FORGE_AGENT={",
        "window.SWRLZ_FORGE_AGENT={"
    )
    s = _once(
        s,
        "  openProjects:()=>{showProjectHub();return true;}\n};",
        "  openProjects:()=>{showProjectHub();return true;}\n};\nwindow.SWYRL_ENGINE_AGENT=window.SWRLZ_FORGE_AGENT;"
    )
    s = _once(
        s,
        "window.SWRLZ_FORGE_BUILD={version:'v5',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates'};",
        "window.SWRLZ_FORGE_BUILD={version:'v5.1',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;"
    )

    return s
