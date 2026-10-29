"""§wyrl§ Engine v6.3: second Glitch Dragon Den — Apex Nexus."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v6.3 token missing: "+old[:180])
    return s.replace(old,new,1)

def apply(html):
    s=html
    repl={
      "V6_2_GLITCH_DEN_PARITY":"V6_3_GLITCH_DEN_APEX",
      "Maker v6.2":"Maker v6.3","MAKER v6.2":"MAKER v6.3",
      "v6.2 · GLITCH DEN PARITY":"v6.3 · GLITCH DEN APEX",
      "version:'v6.2'":"version:'v6.3'",
      "version:'swyrl-engine-agent-v4.2'":"version:'swyrl-engine-agent-v4.3'",
      "engine:'§wyrl§ Engine · Maker v6.2'":"engine:'§wyrl§ Engine · Maker v6.3'",
      "version:6.2":"version:6.3",
      "editorLog('§wyrl§ Engine v6.2 initialized · Glitch Den exact-layout parity','ok')":"editorLog('§wyrl§ Engine v6.3 initialized · Glitch Den II Apex Nexus','ok')"
    }
    for a,b in repl.items(): s=_once(s,a,b)
    card='''<button class="project-card den" data-project-template="glitch-dragons-den"><span class="project-icon">🐲</span><strong>Glitch Dragon Den — Fracture Forge</strong><span class="template-tag">v6.2 VARIANT</span><p>The regular Dragon Den exactly — same architecture, layout, rooms, placements, exits and framing — with the Glitch visual identity layered over it.</p><span class="hint den-glow">Enter the Glitch Den</span></button>'''
    card2=card+'''\n            <button class="project-card den" data-project-template="glitch-dragons-den-apex"><span class="project-icon">🐉</span><strong>Glitch Dragon Den II — Apex Nexus</strong><span class="template-tag">v6.3 RESEARCHED</span><p>Dragon-scale crystal sanctuary with layered cavern masses, forge nexus, throne vault, suspended glitch shards and upgraded apex dragons.</p><span class="hint den-glow">Enter the Apex Nexus</span></button>'''
    s=_once(s,card,card2)
    s=_once(s,"if(template==='moba')buildMobaProject();else if(template==='glitch-dragons-den')buildGlitchDragonsDenProject();","if(template==='moba')buildMobaProject();else if(template==='glitch-dragons-den-apex')buildGlitchDragonsDenApexProject();else if(template==='glitch-dragons-den')buildGlitchDragonsDenProject();")
    # Project-card creation is routed above; saved-project inference retains dragons-den kind compatibility.
    marker="function inferProjectMeta(p){"
    block=r"""
function buildGlitchDragonsDenApexProject(){
  clearAll();applyProjectMeta({name:"Glitch Dragon Den II — Apex Nexus",template:'glitch-dragons-den-apex',kind:'dragons-den',environment:'glitch-dragon-den'});
  setProjectBackground('#00020a');scene.fog.near=13;scene.fog.far=88;renderer.toneMappingExposure=1.24;rebuildTerrain();makeGroundActor();clearGroup(waterGroup);
  const shell=[];
  for(let i=0;i<36;i++){const a=i/36*Math.PI*2,r=27+(i%5)*.8,x=Math.cos(a)*r,z=Math.sin(a)*r;const rock=makeRock([x,0,z],[4.4+(i%4)*.7,8.5+(i%6),4+(i%3)*.6],true,'Apex Cavern Mass '+(i+1));rock.rotation.y=-a+(i%2?.18:-.12);rock.userData.folder='Apex Nexus/Cavern';shell.push(rock);}
  groupActors(shell,'Apex Cavern Shell',{record:false,select:false,folder:'Apex Nexus/Cavern',role:'cavern-shell',tags:['glitch-apex','cavern-shell']});
  const floors=[];[[0,0,0,20,16],[-15,.08,8,8,7],[15,.08,8,8,7],[-14,.1,-11,8,7],[14,.1,-11,8,7],[0,.12,-17,11,6]].forEach((q,i)=>{const p=makeDenStructure('floorPlate',[q[0],0,q[2]],true,'Nexus Floor '+(i+1),i?'#392653':'#4d3270');p.position.y=q[1];p.scale.set(q[3],.8,q[4]);p.userData.colliderRadius=0;floors.push(p);});groupActors(floors,'Apex Nexus Floors',{record:false,select:false,folder:'Apex Nexus/Architecture',role:'den-floor'});
  const forge=makePedestal([0,0,0],'#a966ff',true,'Apex Nexus Forge',7.2);forge.userData.folder='Apex Nexus/Forge';
  const heart=makeCrystal([0,0,0],'#5cecff',true,'Nexus Heart Crystal',2.8);heart.userData.role='nexus-heart';
  for(let i=0;i<12;i++){const a=i/12*Math.PI*2,p=makeDenStructure('pillar',[Math.cos(a)*8.5,0,Math.sin(a)*8.5],true,'Nexus Rune Pylon '+(i+1),i%3===0?'#ff56ca':i%2?'#5cecff':'#9064ff');p.scale.set(.65,3.4,.65);p.userData.folder='Apex Nexus/Forge';}
  const veins=[];[[-21,5,'#54eaff',2],[-19,-13,'#9b65ff',2.3],[20,-13,'#ff52ca',2.1],[22,6,'#56ffd2',1.9],[-11,20,'#687cff',1.8],[12,21,'#d75cff',2.2]].forEach(q=>{const c=makeCrystal([q[0],0,q[1]],q[2],true,'Apex Crystal Vein',q[3]);c.userData.folder='Apex Nexus/Crystal Veins';veins.push(c);});groupActors(veins,'Apex Crystal Veins',{record:false,select:false,folder:'Apex Nexus/Crystal Veins'});
  const throne=makeThrone([0,0,-18],'#d36cff',true,'Apex Glitch Throne');throne.position.y+=1.8;throne.rotation.y=Math.PI;throne.userData.folder='Apex Nexus/Throne Vault';
  [[-13,13,.55,'Crystal Gallery'],[13,13,-.55,'Dragon Gallery'],[-18,-10,.8,'Frost Vault'],[18,-10,-.8,'Ember Vault'],[0,-24,0,'Deep Nexus Gate']].forEach(q=>{const a=makeDenStructure('arch',[q[0],0,q[1]],true,q[3],'#8158b0');a.rotation.y=q[2];a.userData.folder='Apex Nexus/Routes';});
  addPath('Apex Circuit',[[0,13],[-12,11],[-18,2],[-14,-12],[0,-18],[14,-12],[18,2],[12,11],[0,13]]);
  const sw=makeDragon([17,0,8],'#7c55ff',true,'§wyrl§ Apex Glitch Dragon',3.0);sw.position.y+=3.5;sw.rotation.y=-2.2;sw.userData.role='apex-lalm-avatar';
  const frost=makeDragon([-18,0,-5],'#4fcfff',true,'Frost Nexus Dragon',2.3);frost.position.y+=2.2;frost.rotation.y=1.3;
  const ember=makeDragon([14,0,-15],'#ff4f88',true,'Ember Fracture Dragon',2.15);ember.position.y+=2;ember.rotation.y=-.4;
  for(const q of [[0,7,0,'#7d5cff',3.2,26],[-18,6,-5,'#55ddff',2.4,20],[14,6,-15,'#ff5d8d',2.2,19],[0,9,-18,'#ff9b55',1.6,17]]){const l=new THREE.PointLight(q[3],q[4],q[5],2);l.position.set(q[0],q[1],q[2]);scene.add(l);}
  finishTemplate('hero');setRuntimeShellVisibility(false);orbit.target.set(0,3,0);perspectiveCamera.position.set(31,20,36);orbit.update();toast("Glitch Dragon Den II · Apex Nexus loaded");
}
"""
    if marker not in s: raise RuntimeError("v6.3 insertion marker missing")
    return s.replace(marker,block+"\n"+marker,1)
