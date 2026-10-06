"""§wyrl§ Engine v6.0: researched Glitch Dragon Den variant + dragon presentation pass."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v6.0 token missing: "+old[:220])
    return s.replace(old,new,1)

def apply(html):
    s=html
    for a,b in {
      "V5_9_WISP_SOFT_CONTACT_HISTORY":"V6_0_GLITCH_DRAGON_DEN",
      "Maker v5.9":"Maker v6.0","MAKER v5.9":"MAKER v6.0",
      "v5.9 · SOFT CONTACT + HISTORY":"v6.0 · GLITCH DRAGON DEN",
      "version:'v5.9'":"version:'v6.0'",
      "version:'swyrl-engine-agent-v3.9'":"version:'swyrl-engine-agent-v4.0'",
      "engine:'§wyrl§ Engine · Maker v5.9'":"engine:'§wyrl§ Engine · Maker v6.0'",
      "version:5.9":"version:6.0",
      "editorLog('§wyrl§ Engine v5.9 initialized · soft Wisp · stable foot support · visible history','ok')":"editorLog('§wyrl§ Engine v6.0 initialized · researched Glitch Dragon Den variant','ok')"
    }.items(): s=_once(s,a,b)

    # Preserve the original Seed Chamber; add a second den generated from researched
    # cave/dragon/crystal/forge/glitch design principles rather than imported assets.
    marker="function inferProjectMeta(p){"
    if marker not in s: raise RuntimeError("v6.0 den insertion marker missing")
    block=r'''
function buildGlitchDragonsDenProject(){
  clearAll();applyProjectMeta({name:"Glitch Dragon Den — Fracture Forge",template:'glitch-dragons-den',kind:'dragons-den',environment:'glitch-dragon-den'});
  setProjectBackground('#01030a');scene.fog.near=20;scene.fog.far=92;renderer.toneMappingExposure=1.16;rebuildTerrain();makeGroundActor();clearGroup(waterGroup);

  const floors=[];
  const floorCfg=[[0,0,0,20,15,0],[-14,.08,7,8,7,-.16],[14,.10,6,8,7,.16],[0,.12,-14,10,6,0],[-14,.10,-10,7,6,.18],[14,.12,-10,7,6,-.18]];
  floorCfg.forEach((q,i)=>{const p=makeDenStructure('floorPlate',[q[0],0,q[2]],true,'Fracture Floor '+(i+1),i?'#34275c':'#46306e');p.position.y=q[1];p.scale.set(q[3],.72,q[4]);p.rotation.y=q[5];p.userData.colliderRadius=0;floors.push(p);});
  groupActors(floors,'Fracture Forge Floor',{record:false,select:false,folder:'Glitch Den/Architecture',role:'den-floor',tags:['glitch-den','architecture']});

  const shell=[];
  const ring=30;
  for(let i=0;i<32;i++){const a=i/32*Math.PI*2,r=ring+(i%3-1)*1.4,x=Math.cos(a)*r,z=Math.sin(a)*r;
    const rock=makeRock([x,0,z],[3.5+(i%4)*.35,7+(i%5)*.7,3.1+(i%3)*.42],true,'Fracture Wall '+(i+1));rock.rotation.y=-a+(i%2?.13:-.11);rock.userData.folder='Glitch Den/Cavern Shell';rock.userData.tags=['glitch-den','cavern-shell'];shell.push(rock);
  }
  groupActors(shell,'Fractured Megacavern Shell',{record:false,select:false,folder:'Glitch Den/Cavern Shell',role:'cavern-shell',tags:['glitch-den','cavern-shell']});

  const pillars=[];
  [[-21,-15],[21,-15],[-23,8],[23,8],[-14,20],[14,20]].forEach((p,i)=>{const q=makeDenStructure('pillar',[p[0],0,p[1]],true,'Obsidian Buttress '+(i+1),'#25223b');q.scale.set(2.7,11.5,2.7);q.userData.colliderRadius=1.4;pillars.push(q);});
  groupActors(pillars,'Obsidian Buttresses',{record:false,select:false,folder:'Glitch Den/Architecture',role:'buttresses',tags:['glitch-den','architecture']});

  const crystals=[];
  const cc=[[-19,3,'#55eaff',1.35],[-16,-15,'#8c5cff',1.7],[18,-14,'#ff4fd8',1.45],[21,4,'#57ffd2',1.3],[-10,19,'#6c8dff',1.2],[11,20,'#d765ff',1.4],[-5,-19,'#4edcff',.9],[6,-20,'#ff63d5',.95]];
  cc.forEach((q,i)=>{const c=makeCrystal([q[0],0,q[1]],q[2],true,'Fracture Crystal '+(i+1),q[3]);c.userData.folder='Glitch Den/Crystal Veins';c.userData.tags.push('glitch-den','crystal-vein');crystals.push(c);});
  groupActors(crystals,'Chromatic Fracture Veins',{record:false,select:false,folder:'Glitch Den/Crystal Veins',role:'crystal-veins',tags:['glitch-den','crystals']});

  // Central forge is deliberately human-scale inside the giant chamber.
  const dais=makePedestal([0,0,-1],'#9b65ff',true,'Fracture Forge Dais',6.4);dais.userData.folder='Glitch Den/Forge';dais.userData.role='forge-dais';
  const core=makeCrystal([0,0,-1],'#67e9ff',true,'Glitch Forge Core',2.25);core.userData.role='glitch-forge-core';core.userData.tags.push('glitch-den','forge-core');
  for(let i=0;i<8;i++){const a=i/8*Math.PI*2,p=makeDenStructure('pillar',[Math.cos(a)*7,0,-1+Math.sin(a)*7],true,'Rune Pylon '+(i+1),i%2?'#7d55ff':'#43d9ff');p.scale.set(.58,2.7,.58);p.userData.colliderRadius=.45;p.userData.folder='Glitch Den/Forge';}

  const perchA=makeDenStructure('perch',[17,0,10],true,'§wyrl§ Fracture Perch','#7958ff');perchA.scale.set(1.55,1.25,1.55);perchA.userData.role='dragon-perch';
  const perchB=makeDenStructure('perch',[-18,0,-4],true,'Frost Forge Perch','#42cfff');perchB.scale.set(1.35,1.15,1.35);
  const perchC=makeDenStructure('perch',[13,0,-16],true,'Ember Glitch Perch','#ff5d7e');perchC.scale.set(1.25,1.1,1.25);

  const sw=makeDragon([17,0,10],'#875cff',true,'§wyrl§ Glitch Dragon',2.55);sw.position.y+=3.1;sw.rotation.y=-2.18;sw.userData.role='primary-lalm-avatar';sw.userData.tags.push('glitch-den','apex-dragon');
  const frost=makeDragon([-18,0,-4],'#51d9ff',true,'Frost Forge Dragon',1.85);frost.position.y+=1.85;frost.rotation.y=1.28;frost.userData.role='forge-guardian';frost.userData.tags.push('glitch-den','frost-dragon');
  const ember=makeDragon([13,0,-16],'#ff527f',true,'Ember Glitch Dragon',1.65);ember.position.y+=1.55;ember.rotation.y=-.38;ember.userData.role='fracture-guardian';ember.userData.tags.push('glitch-den','ember-dragon');

  // Traversal loop: readable human-scale paths through an oversized dragon environment.
  const arches=[[-11,0,12,.55,'Creator Gate'],[11,0,13,-.55,'Dragon Gallery Gate'],[-15,0,-14,.72,'Frost Vault Gate'],[15,0,-14,-.72,'Ember Vault Gate'],[0,0,-23,0,'Deep Forge Gate']];
  arches.forEach(q=>{const a=makeDenStructure('arch',[q[0],0,q[2]],true,q[4],'#7654a8');a.rotation.y=q[3];a.userData.folder='Glitch Den/Traversal';a.userData.tags.push('glitch-den','route-marker');});
  addPath('Fracture Circuit',[[0,12],[-10,10],[-16,3],[-13,-10],[0,-15],[13,-11],[17,1],[11,11],[0,12]]);

  const lamps=[];[[-7,8],[7,8],[-12,1],[12,1],[-9,-9],[9,-9],[0,-10],[0,7]].forEach((p,i)=>{const l=makeDenStructure('lantern',[p[0],0,p[1]],true,'Glitch Lantern '+(i+1),i%2?'#b55cff':'#4bdcff');l.userData.folder='Glitch Den/Lighting';lamps.push(l);});
  groupActors(lamps,'Glitch Forge Lighting',{record:false,select:false,folder:'Glitch Den/Lighting',role:'den-lighting',tags:['glitch-den','lighting']});

  finishTemplate('hero');setRuntimeShellVisibility(false);
  orbit.target.set(0,3,0);perspectiveCamera.position.set(31,20,36);orbit.update();
  toast("Glitch Dragon Den · Fracture Forge loaded");
}

'''
    s=s.replace(marker,block+marker,1)

    # Route the new template through the existing project builder without replacing the original den.
    old="if(t==='dragons-den')return buildDragonsDenProject();"
    if old in s:
        s=s.replace(old,"if(t==='glitch-dragons-den')return buildGlitchDragonsDenProject();\n  "+old,1)
    else:
        # tolerate later router spelling by adding a public agent callable instead
        agent="openProjects:()=>{showProjectHub();return true;}"
        if agent not in s: raise RuntimeError("v6.0 project router token missing")
        s=s.replace(agent,"buildGlitchDragonsDen:()=>{buildGlitchDragonsDenProject();return true;},\n  "+agent,1)

    # Expose the second den in the Projects hub while preserving the original Dragon's Den card.
    card='<button class="project-card den" data-project-template="dragons-den"><span class="project-icon">🐉</span><strong>Dragon\'s Den</strong><span class="template-tag">EXAMPLE PROJECT</span><p>Arcane collaborative LALM world with dragon avatars, council dais, memory crystal, portals, runes and agent anchor roles.</p><span class="hint den-glow">Enter the Den</span></button>'
    if card not in s: raise RuntimeError("v6.0 Dragon Den project card token missing")
    glitch='<button class="project-card den" data-project-template="glitch-dragons-den"><span class="project-icon">🐉⚡</span><strong>Glitch Dragon Den</strong><span class="template-tag">V6 FRACTURE FORGE</span><p>Fractured megacavern, chromatic crystal veins, rune pylons, forge core and three procedural glitch dragons.</p><span class="hint den-glow">Enter the Fracture Forge</span></button>'
    s=s.replace(card,card+"\\n            "+glitch,1)
    s=s.replace("Dragon's Den v5.3 · grouped architecture + immersive cavern","Dragon's Den · Seed Chamber",1)
    return s
