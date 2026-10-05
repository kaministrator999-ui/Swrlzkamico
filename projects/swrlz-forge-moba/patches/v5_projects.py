"""Forge v5 project-system patch: decouple MOBA, add project templates, add Dragon's Den."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v5 patch source token missing: " + old[:140])
    return s.replace(old, new, 1)

def _before(s: str, marker: str, block: str) -> str:
    i = s.find(marker)
    if i < 0:
        raise RuntimeError("v5 insert marker missing: " + marker[:140])
    return s[:i] + block + s[i:]

def _replace_block(s: str, start: str, end: str, block: str) -> str:
    a = s.find(start)
    if a < 0:
        raise RuntimeError("v5 block start missing: " + start[:140])
    b = s.find(end, a)
    if b < 0:
        raise RuntimeError("v5 block end missing: " + end[:140])
    return s[:a] + block + s[b:]

def apply(html: str) -> str:
    s = html

    replacements = {
        "<!-- SWRLZ_FORGE_DEPLOY_MARKER: V4_1_GROUND_ADHESION_RUNTIME_CLEANUP -->":
            "<!-- SWRLZ_FORGE_DEPLOY_MARKER: V5_PROJECT_TEMPLATES_DRAGONS_DEN -->",
        "<title>SWRLZ Forge · Editor v4.1</title>":
            "<title>SWRLZ Forge · Editor v5</title>",
        '<div class="brand"><b>SWRLZ</b> FORGE · EDITOR v4.1</div>':
            '<div class="brand"><b>SWRLZ</b> FORGE · EDITOR v5</div>',
        '<div class="build-stamp" id="buildStamp">FORGE v4.1 · 2026.10.05</div>':
            '<div class="build-stamp" id="buildStamp">FORGE v5 · PROJECT SYSTEM</div>',
        "const AUTOSAVE_KEY = 'swrlz-forge-v4-autosave';":
            "const AUTOSAVE_KEY = 'swrlz-forge-v5-autosave';",
        "function buildExampleMap(){":
            "function buildMobaProject(){",
        "toast('Rebuilt MOBA Lab v4.1 with grounded movement and cleaned gameplay scenery.');":
            "toast('Created MOBA Arena example project.');",
        "window.SWRLZ_FORGE_BUILD={version:'v4.1',stamp:'2026.10.05',source:'GitHub → Hugging Face'};":
            "window.SWRLZ_FORGE_BUILD={version:'v5',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates'};",
        "version:'forge-agent-v2.1',":
            "version:'forge-agent-v3',",
        "editorLog('Forge v4.1 editor initialized · grounded hero · clean PIE · relocated blockers','ok')":
            "editorLog('Forge v5 editor initialized · project templates · Dragon Den · MOBA decoupled','ok')",
        "Forge v4.1 Tools":
            "Forge v5 Tools",
        "<title>SWRLZ Forge v4.1 Playable</title>":
            "<title>SWRLZ Forge v5 Playable</title>",
        "<b>SWRLZ Forge v4.1 Playable</b>":
            "<b>SWRLZ Forge v5 Playable</b>",
        "saveBlob('swrlz-forge-playable-v4-1.html'":
            "saveBlob('swrlz-forge-playable-v5.html'",
        "return markActor(o,'ground',{name:'Arena Ground',baked:true, colliderRadius:0});":
            "return markActor(o,'ground',{name:'World Ground',baked:true, colliderRadius:0});",
    }
    for old, new in replacements.items():
        s = _once(s, old, new)

    css = """
.project-hub{position:absolute;inset:0;z-index:30;display:none;align-items:center;justify-content:center;padding:18px;background:#05080dbb;backdrop-filter:blur(8px)}
.project-hub.show{display:flex}
.project-window{width:min(900px,96vw);max-height:min(720px,92vh);overflow:auto;background:#101823;border:1px solid #34435b;border-radius:16px;box-shadow:0 24px 80px #000c}
.project-head{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid #28364a}.project-head b{font-size:16px;margin-right:auto}.project-head small{color:var(--muted)}
.project-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;padding:14px}
.project-card{position:relative;text-align:left;min-height:190px;padding:14px;border:1px solid #33425a;border-radius:13px;background:linear-gradient(155deg,#172130,#0e151f);overflow:hidden}
.project-card:hover{border-color:#7167d7;transform:translateY(-1px)}.project-card strong{display:block;font-size:16px;margin:6px 0}.project-card p{color:#9eafc5;min-height:55px}.project-card .project-icon{font-size:35px}.project-card .template-tag{display:inline-block;font-size:10px;padding:3px 7px;border:1px solid #3a4b66;border-radius:999px;color:#aebed2}
.project-card.den{background:radial-gradient(circle at 70% 18%,#59337c55,transparent 36%),linear-gradient(155deg,#1e1730,#0c0a15)}.project-card.moba{background:radial-gradient(circle at 70% 18%,#245f7b55,transparent 36%),linear-gradient(155deg,#122331,#0b1118)}
.project-actions{display:flex;gap:7px;flex-wrap:wrap;padding:0 14px 14px}.project-note{padding:0 14px 14px;color:#8495ac;font-size:11px}
.project-nameplate{padding:7px 8px;border:1px solid #28374b;border-radius:7px;background:#0e151e;color:#c9d4e3;font-weight:700}
.moba-setting.hidden-project-setting{display:none}
.den-glow{color:#c89cff}
@media(max-width:620px){.project-hub{padding:7px}.project-window{max-height:96vh}.project-grid{grid-template-columns:1fr}.project-card{min-height:130px}.project-card p{min-height:0}.project-head small{display:none}}
"""
    s = _once(s, "</style>", css + "\n</style>")

    s = _once(
        s,
        '<button id="buildBtn">🔨 Build</button>',
        '<button id="projectBtn">◫ Projects</button>\n    <button id="buildBtn">🔨 Build</button>'
    )

    old_prefabs = """<section class="section">
        <h3>MOBA Prefabs</h3>
        <div class="section-body asset-grid">
          <button class="asset" data-prefab="tower">🏰 Tower<small>Defense</small></button>
          <button class="asset" data-prefab="base">💎 Core<small>Objective</small></button>
          <button class="asset" data-prefab="spawner">⚔ Spawn<small>Minion source</small></button>
          <button class="asset" data-prefab="camp">👹 Camp<small>Neutral</small></button>
          <button class="asset" data-prefab="bush">🌿 Bush<small>Vision cover</small></button>
          <button class="asset" data-prefab="wall">🧱 Wall<small>Blocker</small></button>
          <button class="asset" data-prefab="rock">🪨 Rock<small>Blocker</small></button>
          <button class="asset" data-prefab="hero">🦸 Hero<small>Playable</small></button>
          <button class="asset" data-prefab="physicsRock">📦 Physics Rock<small>Rigid body</small></button>
          <button class="asset" data-prefab="jumpPad">🟦 BP Jump Pad<small>Blueprint-like</small></button>
          <button class="asset" data-prefab="rotator">🔄 BP Rotator<small>Component actor</small></button>
        </div>
        <div class="section-body hint">New prefabs spawn as translucent ghosts. Move them, then bake them into the map.</div>
      </section>"""
    new_prefabs = """<section class="section">
        <h3>Core Prefabs</h3>
        <div class="section-body asset-grid">
          <button class="asset" data-prefab="hero">🦸 Pawn<small>Playable</small></button>
          <button class="asset" data-prefab="bush">🌿 Bush<small>Environment</small></button>
          <button class="asset" data-prefab="wall">🧱 Wall<small>Blocker</small></button>
          <button class="asset" data-prefab="rock">🪨 Rock<small>Blocker</small></button>
          <button class="asset" data-prefab="physicsRock">📦 Physics Rock<small>Rigid body</small></button>
          <button class="asset" data-prefab="jumpPad">🟦 Jump Pad<small>Component actor</small></button>
          <button class="asset" data-prefab="rotator">🔄 Rotator<small>Component actor</small></button>
          <button class="asset" data-prefab="crystal">🔮 Crystal<small>Animated prop</small></button>
        </div>
        <div class="section-body hint">MOBA actors moved to the example project/content library. New actors still use ghost → Bake.</div>
      </section>"""
    s = _once(s, old_prefabs, new_prefabs)

    old_scene = """<section class="section">
        <h3>Scene</h3>
        <div class="section-body">
          <div class="field"><label>Background</label><input id="bgColor" type="color" value="#0a1420"></div>
          <div class="field"><label>Wave Interval (sec)</label><input id="waveInterval" type="number" min="2" max="30" step="1" value="7"></div>
          <div class="row">
            <button id="resetBtn" class="danger">Reset Example Map</button>
          </div>
        </div>
      </section>"""
    new_scene = """<section class="section">
        <h3>Project / Scene</h3>
        <div class="section-body">
          <div class="field"><label>Current Project</label><div id="currentProjectName" class="project-nameplate">Starter World</div></div>
          <div class="field"><label>Background</label><input id="bgColor" type="color" value="#0a1420"></div>
          <div id="mobaSettings" class="field moba-setting hidden-project-setting"><label>MOBA Wave Interval (sec)</label><input id="waveInterval" type="number" min="2" max="30" step="1" value="7"></div>
          <div class="row">
            <button id="resetBtn" class="danger">Reset Current Project</button>
            <button id="openProjectsBtn">Project Templates</button>
          </div>
        </div>
      </section>"""
    s = _once(s, old_scene, new_scene)

    hub = """      <div id="projectHub" class="project-hub">
        <div class="project-window">
          <div class="project-head"><b>◫ SWRLZ Forge Projects</b><small>Templates create independent editable project state.</small><button id="projectClose">×</button></div>
          <div class="project-grid">
            <button class="project-card" data-project-template="default"><span class="project-icon">🧰</span><strong>Starter World</strong><span class="template-tag">DEFAULT</span><p>Neutral Forge sandbox: terrain, river, pawn, physics prop and component examples. No MOBA rules.</p><span class="hint">Create fresh starter project</span></button>
            <button class="project-card moba" data-project-template="moba"><span class="project-icon">⚔️</span><strong>MOBA Arena</strong><span class="template-tag">EXAMPLE PROJECT</span><p>The original three-lane Forge MOBA, now isolated as a project template instead of being the engine itself.</p><span class="hint">Create MOBA example</span></button>
            <button class="project-card den" data-project-template="dragons-den"><span class="project-icon">🐉</span><strong>Dragon's Den</strong><span class="template-tag">EXAMPLE PROJECT</span><p>Arcane collaborative LALM world with dragon avatars, council dais, memory crystal, portals, runes and agent anchor roles.</p><span class="hint den-glow">Enter the Den</span></button>
          </div>
          <div class="project-actions"><button id="hubSaveBtn">Save Current Project</button><button id="hubLoadBtn">Load Project File</button></div>
          <div class="project-note">Project JSON stores project identity, scene actors, paths and editor state. Templates are starting points; Save/Load produces independent projects.</div>
        </div>
      </div>
"""
    s = _before(s, '      <div id="toast" class="toast"></div>', hub)

    s = _once(
        s,
        '<span id="dirtyStatus" class="status-pill">Saved</span>',
        '<span id="dirtyStatus" class="status-pill">Saved</span>\n    <span id="projectStatus" class="status-pill">Starter World</span>'
    )

    s = _once(
        s,
        ".topbar button:not(#bakeBtn):not(#playBtn):not(#pauseBtn):not(#stopBtn):not(#mobileToolsBtn){display:none}",
        ".topbar button:not(#bakeBtn):not(#playBtn):not(#pauseBtn):not(#stopBtn):not(#mobileToolsBtn){display:none}"
    )

    s = _once(
        s,
        "const HERO_STEP_DOWN = 1.25;",
        "const HERO_STEP_DOWN = 1.25;\nlet currentProject={name:'Starter World',template:'default',kind:'sandbox',environment:'starter'};"
    )

    s = _once(
        s,
        "return {ground:'▱', tower:'🏰', base:'💎', spawner:'⚔', camp:'👹', bush:'🌿', wall:'🧱', rock:'🪨', hero:'🦸', tree:'🌲'}[type] || '◆';",
        "return {ground:'▱', tower:'🏰', base:'💎', spawner:'⚔', camp:'👹', bush:'🌿', wall:'🧱', rock:'🪨', hero:'🦸', tree:'🌲', dragon:'🐉', crystal:'🔮', portal:'🌀', throne:'♛', pedestal:'◉'}[type] || '◆';"
    )

    s = _once(
        s,
        "runtimeVelocity:[0,0,0], runtimeBaseY:null",
        "runtimeVelocity:[0,0,0], runtimeBaseY:null, role:opts.role||'', tags:[...(opts.tags||[])], visualColor:opts.visualColor||''"
    )

    custom_actors = """
function glowMat(color,intensity=1){
  return new THREE.MeshStandardMaterial({color,emissive:new THREE.Color(color),emissiveIntensity:intensity,roughness:.28,metalness:.3,flatShading:true});
}
function makeCrystal(pos,color='#9d72ff',baked=true,name='Arcane Crystal',scale=1){
  const g=new THREE.Group();
  const base=new THREE.Mesh(new THREE.CylinderGeometry(.62,.82,.35,8),mat('#343040'));base.position.y=.18;base.castShadow=base.receiveShadow=true;g.add(base);
  const gem=new THREE.Mesh(new THREE.OctahedronGeometry(.72),glowMat(color,1.4));gem.position.y=1.12;gem.castShadow=true;g.add(gem);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.95,.055,8,40),glowMat(color,.9));ring.rotation.x=Math.PI/2;ring.position.y=.78;g.add(ring);
  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);g.scale.setScalar(scale);
  const o=markActor(g,'crystal',{name,baked,colliderRadius:.55*scale,folder:'Dragon Den/Crystals',components:['Transform','Scene','StaticMesh','Collider','RotatingMovement'],blueprintClass:'BP_ArcaneCrystal',componentSpeed:.28,visualColor:color,tags:['dragon-den','arcane']});
  return o;
}
function makePortal(pos,color='#6ecbff',baked=true,name='Portal'){
  const g=new THREE.Group();
  const base=new THREE.Mesh(new THREE.CylinderGeometry(1.25,1.55,.35,10),mat('#2a3040'));base.position.y=.18;base.castShadow=base.receiveShadow=true;g.add(base);
  const outer=new THREE.Mesh(new THREE.TorusGeometry(1.55,.16,10,48),glowMat(color,1.05));outer.position.y=1.9;g.add(outer);
  const inner=new THREE.Mesh(new THREE.TorusGeometry(1.18,.045,8,48),glowMat('#f1dcff',1.2));inner.position.y=1.9;inner.rotation.y=.35;g.add(inner);
  const core=new THREE.Mesh(new THREE.CircleGeometry(1.12,40),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.12,side:THREE.DoubleSide}));core.position.y=1.9;g.add(core);
  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);
  return markActor(g,'portal',{name,baked,colliderRadius:1.2,folder:'Dragon Den/Portals',components:['Transform','Scene','StaticMesh','Collider','RotatingMovement'],blueprintClass:'BP_ArcanePortal',componentSpeed:.12,visualColor:color,tags:['dragon-den','portal']});
}
function makePedestal(pos,color='#7555aa',baked=true,name='Pedestal',radius=2.3){
  const g=new THREE.Group();
  const low=new THREE.Mesh(new THREE.CylinderGeometry(radius,radius+.35,.35,16),mat('#292534'));low.position.y=.18;low.castShadow=low.receiveShadow=true;g.add(low);
  const top=new THREE.Mesh(new THREE.CylinderGeometry(radius-.25,radius,.22,16),glowMat(color,.18));top.position.y=.46;top.castShadow=top.receiveShadow=true;g.add(top);
  const rune=new THREE.Mesh(new THREE.TorusGeometry(radius-.48,.045,8,64),glowMat(color,.9));rune.rotation.x=Math.PI/2;rune.position.y=.59;g.add(rune);
  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);
  return markActor(g,'pedestal',{name,baked,colliderRadius:0,folder:'Dragon Den/Architecture',components:['Transform','Scene','StaticMesh'],blueprintClass:'BP_RuneDais',visualColor:color,tags:['dragon-den','architecture']});
}
function makeThrone(pos,color='#d49bff',baked=true,name='Kamilion Throne'){
  const g=new THREE.Group();
  const seatMat=mat('#32283f');
  const seat=new THREE.Mesh(new THREE.BoxGeometry(2.2,.55,1.8),seatMat);seat.position.y=.65;seat.castShadow=seat.receiveShadow=true;g.add(seat);
  const back=new THREE.Mesh(new THREE.BoxGeometry(2.35,3.2,.45),seatMat.clone());back.position.set(0,2.05,.62);back.castShadow=true;g.add(back);
  const crown=new THREE.Mesh(new THREE.ConeGeometry(1.35,1.4,5),glowMat(color,.45));crown.position.set(0,4.15,.62);crown.rotation.z=Math.PI;g.add(crown);
  for(const x of [-1.28,1.28]){const arm=new THREE.Mesh(new THREE.CylinderGeometry(.18,.24,1.3,6),glowMat(color,.3));arm.position.set(x,1.3,0);arm.castShadow=true;g.add(arm);}
  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);
  return markActor(g,'throne',{name,baked,colliderRadius:1.3,folder:'Dragon Den/Architecture',components:['Transform','Scene','StaticMesh','Collider'],blueprintClass:'BP_DragonThrone',visualColor:color,tags:['dragon-den','throne']});
}
function makeDragon(pos,color='#9b6cff',baked=true,name='Dragon Avatar',scale=1){
  const g=new THREE.Group(),skin=mat(color),glow=glowMat(color,.7),dark=mat('#241c31');
  const body=new THREE.Mesh(new THREE.SphereGeometry(1.0,12,8),skin);body.scale.set(1,1.05,1.55);body.position.y=1.38;body.castShadow=true;g.add(body);
  const chest=new THREE.Mesh(new THREE.SphereGeometry(.62,10,7),dark);chest.scale.set(1,.85,.85);chest.position.set(0,1.45,-.72);g.add(chest);
  const neck=new THREE.Mesh(new THREE.CylinderGeometry(.38,.62,1.45,8),skin.clone());neck.position.set(0,2.12,-.72);neck.rotation.x=-.28;neck.castShadow=true;g.add(neck);
  const head=new THREE.Mesh(new THREE.DodecahedronGeometry(.68),skin.clone());head.position.set(0,2.78,-1.05);head.scale.set(1,.82,1.12);head.castShadow=true;g.add(head);
  const snout=new THREE.Mesh(new THREE.BoxGeometry(.72,.35,.78),dark.clone());snout.position.set(0,2.62,-1.68);g.add(snout);
  for(const x of [-.72,.72]){const wing=new THREE.Mesh(new THREE.ConeGeometry(1.2,2.9,3),skin.clone());wing.position.set(x*1.2,1.75,.25);wing.rotation.set(Math.PI/2,0,x<0?.52:-.52);wing.scale.set(.65,1,.18);wing.castShadow=true;g.add(wing);}
  const tail=new THREE.Mesh(new THREE.ConeGeometry(.42,2.8,7),skin.clone());tail.position.set(0,1.15,2.25);tail.rotation.x=Math.PI/2;g.add(tail);
  for(const x of [-.32,.32]){const horn=new THREE.Mesh(new THREE.ConeGeometry(.13,.7,6),glow);horn.position.set(x,3.38,-.9);horn.rotation.x=-.2;g.add(horn);const eye=new THREE.Mesh(new THREE.SphereGeometry(.08,8,6),glow.clone());eye.position.set(x*.65,2.89,-1.63);g.add(eye);}
  g.position.set(pos[0],terrainHeight(pos[0],pos[2]),pos[2]);g.scale.setScalar(scale);
  return markActor(g,'dragon',{name,baked,colliderRadius:1.05*scale,folder:'Dragon Den/Dragons',components:['Transform','Scene','StaticMesh','Collider','BobMovement','AgentAvatar'],blueprintClass:'BP_DragonAvatar',componentSpeed:.75,bobAmplitude:.08,visualColor:color,role:'lalM-agent-avatar',tags:['dragon-den','agent-avatar','voice-anchor-hook']});
}

"""
    s = _before(s, "function addPath(name, points){", custom_actors)

    project_system = """
function applyProjectMeta(meta={}){
  currentProject={
    name:meta.name||'Untitled Project',
    template:meta.template||'custom',
    kind:meta.kind||'sandbox',
    environment:meta.environment||'starter'
  };
  const nameEl=$('currentProjectName');if(nameEl)nameEl.textContent=currentProject.name;
  const status=$('projectStatus');if(status)status.textContent=currentProject.name;
  const moba=$('mobaSettings');if(moba)moba.classList.toggle('hidden-project-setting',currentProject.kind!=='moba');
  document.body.dataset.projectKind=currentProject.kind;
}
function setProjectBackground(hex){
  scene.background.set(hex);scene.fog.color.set(hex);$('bgColor').value=hex;
}
function finishTemplate(selectType='hero'){
  rebuildHierarchy();refreshDebug();selectActor(actors.find(a=>a.userData.actorType===selectType)||actors.find(a=>a.userData.actorType==='hero')||null);refreshAssetList();
}
function buildDefaultProject(){
  clearAll();applyProjectMeta({name:'Starter World',template:'default',kind:'sandbox',environment:'starter'});setProjectBackground('#0d1722');rebuildTerrain();makeGroundActor();buildSceneryExtras();
  makeHero('blue',[0,0,7],true,'Player Pawn').userData.folder='Gameplay';
  makeTree([-9,0,-8],[1.2,1.35,1.2],true,'Starter Tree A');makeTree([10,0,8],[1.25,1.35,1.25],true,'Starter Tree B');
  makeBush([-5,0,4],[1.6,1,1.2],true,'Starter Bush');makeRock([6,0,-5],[1.3,1.1,1.2],true,'Starter Rock');
  const p=makeRock([-2,0,2],[.85,.85,.85],true,'Physics Prop');addComponent(p,'PhysicsBody');p.userData.folder='Examples/Physics';
  const j=makeWall([4,0,4],[1.6,.22,1.6],true,'BP_JumpPad');j.userData.blueprintClass='BP_JumpPad';j.userData.folder='Examples/Blueprints';addComponent(j,'LaunchPad');
  finishTemplate('hero');toast('Created Starter World project.');
}
function buildDragonsDenProject(){
  clearAll();applyProjectMeta({name:"Dragon's Den",template:'dragons-den',kind:'dragons-den',environment:'dragon-den'});setProjectBackground('#080512');rebuildTerrain();makeGroundActor();clearGroup(waterGroup);
  const visitor=makeHero('blue',[0,0,11],true,'Visitor Pawn');visitor.userData.folder='Dragon Den/Visitors';
  const dais=makePedestal([0,0,0],'#a76dff',true,'Council Rune Dais',4.3);dais.userData.role='council-center';
  const memory=makeCrystal([0,0,0],'#d49bff',true,'Memory Crystal',1.45);memory.userData.role='memory-anchor';memory.userData.tags.push('memory-hook');
  const sw=makeDragon([-4.6,0,-1.0],'#9e70ff',true,'§wyrlz Dragon',1.08);sw.rotation.y=-.92;sw.userData.role='primary-lalm-avatar';
  const forge=makeDragon([4.6,0,-1.0],'#56d7ff',true,'Forge Dragon',1.02);forge.rotation.y=.92;forge.userData.role='world-builder-agent';
  const coder=makeDragon([0,0,5.5],'#ff8b55',true,'Coder Dragon',.9);coder.rotation.y=Math.PI;coder.userData.role='coding-reasoner-agent';
  const throne=makeThrone([0,0,-7.5],'#d49bff',true,'Kamilion Throne');throne.rotation.y=Math.PI;throne.userData.role='human-author-seat';
  const codePortal=makePortal([-9.0,0,4.5],'#56d7ff',true,'Code Portal');codePortal.rotation.y=.55;codePortal.userData.role='coding-interface';
  const worldPortal=makePortal([9.0,0,4.5],'#9e70ff',true,'World Portal');worldPortal.rotation.y=-.55;worldPortal.userData.role='world-interface';
  const voice=makeCrystal([-6.0,0,-6.0],'#ff75cf',true,'Spatial Voice Anchor',.8);voice.userData.role='spatial-voice-hook';
  const inference=makeCrystal([6.0,0,-6.0],'#65f6c1',true,'Inference Core',.8);inference.userData.role='lalm-inference-hook';
  for(let i=0;i<18;i++){const a=i/18*Math.PI*2,r=17.2,x=Math.cos(a)*r,z=Math.sin(a)*13.2,rock=makeRock([x,0,z],[1.7+(i%3)*.22,2.25+(i%4)*.18,1.7],true,'Cavern Wall '+String(i+1));rock.userData.folder='Dragon Den/Cavern';}
  for(const cfg of [[-10,-7,'#5ccfff'],[10,-7,'#b36cff'],[-12,0,'#ff5fc9'],[12,0,'#62ffc6']]){const c=makeCrystal([cfg[0],0,cfg[1]],cfg[2],true,'Rune Crystal',.7);c.userData.folder='Dragon Den/Runes';}
  for(const cfg of [[-12,8],[12,8],[-13,-9],[13,-9]]){const t=makeTree([cfg[0],0,cfg[1]],[1.2,1.55,1.2],true,'Ancient Den Tree');t.userData.folder='Dragon Den/Cavern';}
  const asc=makeWall([0,0,8],[1.7,.22,1.7],true,'Ascension Pad');asc.userData.blueprintClass='BP_JumpPad';asc.userData.folder='Dragon Den/Architecture';addComponent(asc,'LaunchPad');asc.userData.launchStrength=9.5;
  finishTemplate('hero');toast("Dragon's Den created. 🐉");
}
function inferProjectMeta(p){
  const a=p?.scene?.actors||[];
  if(a.some(x=>x.type==='dragon'))return {name:"Dragon's Den Project",template:'custom',kind:'dragons-den',environment:'dragon-den'};
  if((p?.scene?.paths&&Object.keys(p.scene.paths).length)||a.some(x=>x.type==='base'||x.type==='tower'))return {name:'MOBA Project',template:'custom',kind:'moba',environment:'moba'};
  return {name:'Imported Forge Project',template:'custom',kind:'sandbox',environment:'starter'};
}
function createProjectFromTemplate(template,force=false){
  if(dirty&&!force&&!confirm('Create a new project and discard unsaved scene changes?'))return;
  if(template==='moba')buildMobaProject();else if(template==='dragons-den')buildDragonsDenProject();else buildDefaultProject();
  initializeHistory('Created '+currentProject.name);markSaved();$('projectHub').classList.remove('show');editorLog('Created project template: '+currentProject.name,'ok');
}
function resetCurrentProject(){
  const t=currentProject.template==='custom'?(currentProject.kind==='moba'?'moba':currentProject.kind==='dragons-den'?'dragons-den':'default'):currentProject.template;
  if(!confirm('Reset '+currentProject.name+' to its template?'))return;
  createProjectFromTemplate(t,true);
}
function showProjectHub(){ $('projectHub').classList.add('show'); }
function safeProjectName(){return (currentProject.name||'forge-project').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'forge-project';}

"""
    s = _before(s, "function buildMobaProject(){", project_system)

    s = _once(
        s,
        "function buildMobaProject(){\n  clearAll();",
        "function buildMobaProject(){\n  clearAll();applyProjectMeta({name:'MOBA Arena Example',template:'moba',kind:'moba',environment:'moba'});setProjectBackground('#0a1420');"
    )

    s = _once(
        s,
        "  if(type==='rotator'){ o = makeWall([0,0,0],[1.2,.35,1.2],false,'BP_Rotator'); o.userData.blueprintClass='BP_Rotator'; o.userData.folder='Blueprints'; addComponent(o,'RotatingMovement'); }",
        "  if(type==='rotator'){ o = makeWall([0,0,0],[1.2,.35,1.2],false,'BP_Rotator'); o.userData.blueprintClass='BP_Rotator'; o.userData.folder='Blueprints'; addComponent(o,'RotatingMovement'); }\n"
        "  if(type==='crystal') o = makeCrystal([0,0,0],'#9d72ff',false,'Ghost Arcane Crystal',1);\n"
        "  if(type==='portal') o = makePortal([0,0,0],'#6ecbff',false,'Ghost Portal');\n"
        "  if(type==='dragon') o = makeDragon([0,0,0],'#9e70ff',false,'Ghost Dragon',1);\n"
        "  if(type==='throne') o = makeThrone([0,0,0],'#d49bff',false,'Ghost Throne');\n"
        "  if(type==='pedestal') o = makePedestal([0,0,0],'#a76dff',false,'Ghost Pedestal',2.3);"
    )

    s = _once(
        s,
        "name:a.name, type:a.userData.actorType, team:a.userData.team, baked:a.userData.baked,",
        "name:a.name, type:a.userData.actorType, team:a.userData.team, baked:a.userData.baked, role:a.userData.role||'', tags:[...(a.userData.tags||[])], visualColor:a.userData.visualColor||'',"
    )

    s = _once(
        s,
        "  if(d.type==='tree') o = makeTree([d.position[0],0,d.position[2]], d.scale||[1,1,1], d.baked!==false, d.name);\n  if(!o) return null;",
        "  if(d.type==='tree') o = makeTree([d.position[0],0,d.position[2]], d.scale||[1,1,1], d.baked!==false, d.name);\n"
        "  if(d.type==='crystal') o = makeCrystal([d.position[0],0,d.position[2]],d.visualColor||'#9d72ff',d.baked!==false,d.name,1);\n"
        "  if(d.type==='portal') o = makePortal([d.position[0],0,d.position[2]],d.visualColor||'#6ecbff',d.baked!==false,d.name);\n"
        "  if(d.type==='dragon') o = makeDragon([d.position[0],0,d.position[2]],d.visualColor||'#9e70ff',d.baked!==false,d.name,1);\n"
        "  if(d.type==='throne') o = makeThrone([d.position[0],0,d.position[2]],d.visualColor||'#d49bff',d.baked!==false,d.name);\n"
        "  if(d.type==='pedestal') o = makePedestal([d.position[0],0,d.position[2]],d.visualColor||'#a76dff',d.baked!==false,d.name,2.3);\n"
        "  if(!o) return null;"
    )

    s = _once(
        s,
        "o.userData.colliderRadius=d.colliderRadius??o.userData.colliderRadius; o.userData.mass=d.mass??1; o.userData.restitution=d.restitution??0.25; o.userData.componentSpeed=d.componentSpeed??1; o.userData.bobAmplitude=d.bobAmplitude??0.5; o.userData.launchStrength=d.launchStrength??8; o.visible=d.visible!==false;",
        "o.userData.colliderRadius=d.colliderRadius??o.userData.colliderRadius; o.userData.mass=d.mass??1; o.userData.restitution=d.restitution??0.25; o.userData.componentSpeed=d.componentSpeed??1; o.userData.bobAmplitude=d.bobAmplitude??0.5; o.userData.launchStrength=d.launchStrength??8; o.userData.role=d.role||o.userData.role||''; o.userData.tags=[...(d.tags||o.userData.tags||[])]; o.userData.visualColor=d.visualColor||o.userData.visualColor||''; o.visible=d.visible!==false;"
    )

    project_data = """function projectData(){
  return {
    engine:'SWRLZ Forge · Editor v5',
    version:5,
    project:{...currentProject},
    editor:{transformSpace,snapEnabled,terrainSnapEnabled,viewMode,cameraView:editorCameraView,revision},
    scene:{
      background:'#'+scene.background.getHexString(),
      waveInterval:Number($('waveInterval').value)||7,
      paths:Object.fromEntries(Object.entries(paths).map(([k,v])=>[k,v.map(p=>p.toArray())])),
      actors:actors.map(actorData)
    }
  };
}
"""
    s = _replace_block(s, "function projectData(){", "function loadProject(p, options={}){", project_data)

    load_project = """function loadProject(p, options={}){
  if(!p?.scene?.actors) throw new Error('Invalid project JSON.');
  clearAll();applyProjectMeta(p.project||inferProjectMeta(p));
  scene.background.set(p.scene.background || '#0a1420');scene.fog.color.set(scene.background);
  $('bgColor').value = '#'+scene.background.getHexString();
  $('waveInterval').value = p.scene.waveInterval || 7;
  rebuildTerrain();
  for(const [k,pts] of Object.entries(p.scene.paths||{})) addPath(k,pts);
  Object.values(paths).forEach(v=>addLaneHelpers(v.map(p=>p.toArray())));
  if(currentProject.environment!=='dragon-den')buildSceneryExtras();else clearGroup(waterGroup);
  for(const d of p.scene.actors) fromData(d);
  rebuildHierarchy();refreshDebug();selectActor(actors.find(a=>a.userData.actorType==='hero')||actors.find(a=>a.userData.actorType==='dragon')||null);
  transformSpace=p.editor?.transformSpace||transformSpace;transform.setSpace(transformSpace);$('spaceBtn').textContent=transformSpace[0].toUpperCase()+transformSpace.slice(1);
  terrainSnapEnabled=p.editor?.terrainSnapEnabled??terrainSnapEnabled;$('terrainSnapBtn').classList.toggle('active',terrainSnapEnabled);
  if(p.editor?.cameraView){$('cameraView').value=p.editor.cameraView;setCameraView(p.editor.cameraView);}
  if(!options.preserveHistory)initializeHistory('Loaded '+currentProject.name);refreshAssetList();
}
"""
    s = _replace_block(s, "function loadProject(p, options={}){", "function setMode(m){", load_project)

    s = _once(
        s,
        "$('resetBtn').onclick = ()=>{beginTransaction('Reset Example Map');buildExampleMap();commitTransaction('Reset Example Map');};",
        "$('resetBtn').onclick = resetCurrentProject; $('openProjectsBtn').onclick=showProjectHub;"
    )

    assets = """const ASSET_LIBRARY=[
  {id:'hero',name:'Player Pawn',path:'/Engine/Gameplay',desc:'Playable CharacterMovement pawn'},
  {id:'bush',name:'Bush Cluster',path:'/Engine/Environment',desc:'Foliage / cover prop'}, {id:'wall',name:'Stone Wall',path:'/Engine/Environment',desc:'Static blocker'}, {id:'rock',name:'Rock',path:'/Engine/Environment',desc:'Scenery / blocker'},
  {id:'physicsRock',name:'Physics Rock',path:'/Engine/Physics',desc:'Rigid body component demo'}, {id:'jumpPad',name:'BP_JumpPad',path:'/Engine/Components',desc:'LaunchPad component actor'}, {id:'rotator',name:'BP_Rotator',path:'/Engine/Components',desc:'RotatingMovement actor'},
  {id:'tower',name:'MOBA Tower',path:'/Examples/MOBA',desc:'Example defensive structure'}, {id:'base',name:'MOBA Core / Nexus',path:'/Examples/MOBA',desc:'Example primary objective'}, {id:'spawner',name:'MOBA Minion Spawner',path:'/Examples/MOBA',desc:'Example lane wave origin'}, {id:'camp',name:'MOBA Neutral Camp',path:'/Examples/MOBA',desc:'Example jungle encounter'},
  {id:'dragon',name:'BP_DragonAvatar',path:'/Examples/DragonsDen',desc:'Embodied LALM dragon avatar'}, {id:'crystal',name:'Arcane Crystal',path:'/Examples/DragonsDen',desc:'Animated memory/inference anchor'}, {id:'portal',name:'Arcane Portal',path:'/Examples/DragonsDen',desc:'World/interface portal actor'}, {id:'throne',name:'Dragon Throne',path:'/Examples/DragonsDen',desc:'Den architecture'}, {id:'pedestal',name:'Rune Pedestal',path:'/Examples/DragonsDen',desc:'Council dais / rune platform'}
];
"""
    s = _replace_block(s, "const ASSET_LIBRARY=[", "function refreshAssetList(){", assets)

    validation = """function validateProject(){
  const issues=[];const warns=[];const names=new Map();
  for(const a of actors){names.set(a.name,(names.get(a.name)||0)+1);if(Math.abs(a.position.x)>24||Math.abs(a.position.z)>20)warns.push(a.name+' is outside the nominal world bounds');}
  for(const [name,count] of names)if(count>1)warns.push('Duplicate actor name: '+name+' ×'+count);
  if(currentProject.kind==='moba'){
    const blueBases=actors.filter(a=>a.userData.actorType==='base'&&a.userData.team==='blue').length,redBases=actors.filter(a=>a.userData.actorType==='base'&&a.userData.team==='red').length;
    if(!blueBases)issues.push('MOBA project: Blue team has no Core/Base');if(!redBases)issues.push('MOBA project: Red team has no Core/Base');if(!actors.some(a=>a.userData.actorType==='hero'))issues.push('MOBA project: no Hero actor exists');if(!Object.keys(paths).length)issues.push('MOBA project: no lane paths are defined');
  }else if(currentProject.kind==='dragons-den'){
    if(!actors.some(a=>a.userData.actorType==='hero'))issues.push("Dragon's Den: no visitor/player pawn exists");
    if(!actors.some(a=>a.userData.actorType==='dragon'))issues.push("Dragon's Den: no dragon avatar exists");
    if(!actors.some(a=>a.userData.role==='memory-anchor'))warns.push("Dragon's Den: Memory Crystal anchor is missing");
    if(!actors.some(a=>a.userData.actorType==='portal'))warns.push("Dragon's Den: no portal actors exist");
  }
  const ghosts=actors.filter(a=>!a.userData.baked).length;if(ghosts)warns.push(ghosts+' ghost actor(s) are not baked');
  editorLog('Build validation ['+currentProject.name+']: '+issues.length+' error(s), '+warns.length+' warning(s)',issues.length?'error':warns.length?'warn':'ok');issues.forEach(x=>editorLog(x,'error'));warns.forEach(x=>editorLog(x,'warn'));return {issues,warns};
}
"""
    s = _replace_block(s, "function validateProject(){", "$('buildBtn').onclick", validation)

    s = _once(
        s,
        "$('saveBtn').onclick = ()=>{saveBlob('swrlz-forge-project-v4-1.json', JSON.stringify(projectData(),null,2), 'application/json');markSaved();editorLog('Project saved','ok');};",
        "$('saveBtn').onclick = ()=>{saveBlob(safeProjectName()+'.forge.json', JSON.stringify(projectData(),null,2), 'application/json');markSaved();editorLog('Project saved: '+currentProject.name,'ok');};"
    )

    events = """
$('projectBtn').onclick=showProjectHub;$('projectClose').onclick=()=>$('projectHub').classList.remove('show');
$('projectHub').addEventListener('pointerdown',e=>{if(e.target===$('projectHub'))$('projectHub').classList.remove('show');});
document.querySelectorAll('[data-project-template]').forEach(b=>b.onclick=()=>createProjectFromTemplate(b.dataset.projectTemplate));
$('hubSaveBtn').onclick=()=>{$('saveBtn').click();$('projectHub').classList.remove('show');};
$('hubLoadBtn').onclick=()=>{$('loadBtn').click();};
"""
    s = _before(s, "$('bgColor').oninput", events)

    s = _once(
        s,
        "<b>Content</b>\n            <div class=\"hint\" style=\"margin-top:7px\">/Game<br>/Game/MOBA<br>/Game/Environment<br>/Game/Blueprints</div>",
        "<b>Content</b>\n            <div class=\"hint\" style=\"margin-top:7px\">/Engine<br>/Engine/Environment<br>/Engine/Physics<br>/Examples/MOBA<br>/Examples/DragonsDen</div>"
    )

    s = _once(
        s,
        "<button data-click=\"undoBtn\">↶ Undo</button><button data-click=\"redoBtn\">↷ Redo</button>",
        "<button data-click=\"projectBtn\">◫ Projects</button><button data-click=\"undoBtn\">↶ Undo</button><button data-click=\"redoBtn\">↷ Redo</button>"
    )

    s = _once(
        s,
        "['tower','base','spawner','camp','bush','wall','rock','hero','physicsRock','jumpPad','rotator'].forEach(type=>{",
        "['hero','bush','wall','rock','physicsRock','jumpPad','rotator','crystal','portal','dragon'].forEach(type=>{"
    )

    old_tick = """function tick(){
  requestAnimationFrame(tick); resize(); const dt=Math.min(clock.getDelta(),0.05), t=performance.now()/1000;
  const runtimeActive=playing||simulating;
  if(runtimeActive&&!paused){
    if(t-lastWave>(Number($('waveInterval').value)||7)){lastWave=t;Object.keys(paths).forEach(lane=>{spawnRuntimeMinion('blue',lane);spawnRuntimeMinion('red',lane);});}
    if(playing)updateHero(dt,t);
    updateRuntimeComponents(dt,t);
    for(const u of [...liveUnits])updateMinion(u,dt,t); updateTowers(t);
  }
  if(!playing)orbit.update(); if(selectionBox&&selected)selectionBox.update(); renderer.render(scene,camera);
}
"""
    new_tick = """function tick(){
  requestAnimationFrame(tick);resize();const dt=Math.min(clock.getDelta(),0.05),t=performance.now()/1000;const runtimeActive=playing||simulating;
  if(runtimeActive&&!paused){
    if(currentProject.kind==='moba'&&t-lastWave>(Number($('waveInterval').value)||7)){lastWave=t;Object.keys(paths).forEach(lane=>{spawnRuntimeMinion('blue',lane);spawnRuntimeMinion('red',lane);});}
    if(playing)updateHero(dt,t);updateRuntimeComponents(dt,t);
    if(currentProject.kind==='moba'){for(const u of [...liveUnits])updateMinion(u,dt,t);updateTowers(t);}
  }
  if(!playing)orbit.update();if(selectionBox&&selected)selectionBox.update();renderer.render(scene,camera);
}
"""
    s = _once(s, old_tick, new_tick)

    s = _once(
        s,
        "if(t-lastWave>(P.scene.waveInterval||7)){lastWave=t; Object.keys(paths).forEach(l=>{spawn('blue',l); spawn('red',l)}) } updateComponents(dt,t); moveHero(dt,t); updateUnits(dt,t); updateTowers(t); R.render(S,C)",
        "if(P.project?.kind==='moba'&&t-lastWave>(P.scene.waveInterval||7)){lastWave=t; Object.keys(paths).forEach(l=>{spawn('blue',l); spawn('red',l)}) } updateComponents(dt,t); moveHero(dt,t); if(P.project?.kind==='moba'){updateUnits(dt,t); updateTowers(t)} R.render(S,C)"
    )

    s = _once(
        s,
        "  snapToTerrain:(id)=>{const a=actors.find(x=>x.userData.id===id);if(!a)return false;snapActorToTerrain(a);return true;}",
        "  snapToTerrain:(id)=>{const a=actors.find(x=>x.userData.id===id);if(!a)return false;snapActorToTerrain(a);return true;},\n"
        "  project:()=>({...currentProject}),\n"
        "  createProject:(template)=>{createProjectFromTemplate(template,true);return {...currentProject};},\n"
        "  openProjects:()=>{showProjectHub();return true;}"
    )

    s = _once(
        s,
        "buildExampleMap();refreshAssetList();initializeHistory('Initial MOBA example');setCameraView('perspective');",
        "buildDefaultProject();refreshAssetList();initializeHistory('Initial Starter World');setCameraView('perspective');"
    )

    return s
