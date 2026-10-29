"""§wyrl§ Engine v6.4: one researched Glitch Den + dragon anatomy v3."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v6.4 token missing: "+old[:180])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V6_3_GLITCH_DEN_APEX":"V6_4_GLITCH_DEN_DRAGON_V3",
      "Maker v6.3":"Maker v6.4","MAKER v6.3":"MAKER v6.4",
      "v6.3 · GLITCH DEN APEX":"v6.4 · GLITCH DEN DRAGON V3",
      "version:'v6.3'":"version:'v6.4'",
      "version:'swyrl-engine-agent-v4.3'":"version:'swyrl-engine-agent-v4.4'",
      "engine:'§wyrl§ Engine · Maker v6.3'":"engine:'§wyrl§ Engine · Maker v6.4'",
      "version:6.3":"version:6.4",
      "editorLog('§wyrl§ Engine v6.3 initialized · Glitch Den II Apex Nexus','ok')":"editorLog('§wyrl§ Engine v6.4 initialized · single Glitch Den · dragon anatomy v3','ok')"
    }.items(): s=_once(s,a,b)

    # Remove the accidental second project/card/router.
    apex_card='''\n            <button class="project-card den" data-project-template="glitch-dragons-den-apex"><span class="project-icon">🐉</span><strong>Glitch Dragon Den II — Apex Nexus</strong><span class="template-tag">v6.3 RESEARCHED</span><p>Dragon-scale crystal sanctuary with layered cavern masses, forge nexus, throne vault, suspended glitch shards and upgraded apex dragons.</p><span class="hint den-glow">Enter the Apex Nexus</span></button>'''
    s=_once(s,apex_card,"")
    s=_once(s,"if(template==='moba')buildMobaProject();else if(template==='glitch-dragons-den-apex')buildGlitchDragonsDenApexProject();else if(template==='glitch-dragons-den')buildGlitchDragonsDenProject();","if(template==='moba')buildMobaProject();else if(template==='glitch-dragons-den')buildGlitchDragonsDenProject();")

    # Remove accidental Apex builder entirely.
    a=s.find("function buildGlitchDragonsDenApexProject(){")
    b=s.find("\nfunction inferProjectMeta(p){",a)
    if a<0 or b<0: raise RuntimeError("v6.4 Apex builder boundary missing")
    s=s[:a]+s[b+1:]

    # Replace parity-only Glitch Den with the researched single project.
    a=s.find("function buildGlitchDragonsDenProject(){")
    b=s.find("\nfunction inferProjectMeta(p){",a)
    if a<0 or b<0: raise RuntimeError("v6.4 Glitch builder boundary missing")
    block=r'''function buildGlitchDragonsDenProject(){
  clearAll();applyProjectMeta({name:"Glitch Dragon Den — Fracture Forge",template:'glitch-dragons-den',kind:'dragons-den',environment:'glitch-dragon-den'});
  setProjectBackground('#00020a');scene.fog.near=13;scene.fog.far=88;renderer.toneMappingExposure=1.22;rebuildTerrain();makeGroundActor();clearGroup(waterGroup);
  const shell=[];
  for(let i=0;i<36;i++){const ang=i/36*Math.PI*2,r=27+(i%5)*.8,x=Math.cos(ang)*r,z=Math.sin(ang)*r;const rock=makeRock([x,0,z],[4.4+(i%4)*.7,8.5+(i%6),4+(i%3)*.6],true,'Fracture Cavern Mass '+(i+1));rock.rotation.y=-ang+(i%2?.18:-.12);rock.userData.folder='Glitch Den/Cavern';shell.push(rock);}
  groupActors(shell,'Fracture Forge Cavern Shell',{record:false,select:false,folder:'Glitch Den/Cavern',role:'cavern-shell',tags:['glitch-den','cavern-shell']});
  const floors=[];[[0,0,0,20,16],[-15,.08,8,8,7],[15,.08,8,8,7],[-14,.1,-11,8,7],[14,.1,-11,8,7],[0,.12,-17,11,6]].forEach((q,i)=>{const p=makeDenStructure('floorPlate',[q[0],0,q[2]],true,'Fracture Floor '+(i+1),i?'#392653':'#4d3270');p.position.y=q[1];p.scale.set(q[3],.8,q[4]);p.userData.colliderRadius=0;floors.push(p);});groupActors(floors,'Fracture Forge Floors',{record:false,select:false,folder:'Glitch Den/Architecture',role:'den-floor'});
  const forge=makePedestal([0,0,0],'#a966ff',true,'Fracture Forge Nexus',7.2);forge.userData.folder='Glitch Den/Forge';
  const heart=makeCrystal([0,0,0],'#5cecff',true,'Fracture Heart Crystal',2.8);heart.userData.role='forge-heart';
  for(let i=0;i<12;i++){const ang=i/12*Math.PI*2,p=makeDenStructure('pillar',[Math.cos(ang)*8.5,0,Math.sin(ang)*8.5],true,'Fracture Rune Pylon '+(i+1),i%3===0?'#ff56ca':i%2?'#5cecff':'#9064ff');p.scale.set(.65,3.4,.65);p.userData.folder='Glitch Den/Forge';}
  const veins=[];[[-21,5,'#54eaff',2],[-19,-13,'#9b65ff',2.3],[20,-13,'#ff52ca',2.1],[22,6,'#56ffd2',1.9],[-11,20,'#687cff',1.8],[12,21,'#d75cff',2.2]].forEach(q=>{const c=makeCrystal([q[0],0,q[1]],q[2],true,'Fracture Crystal Vein',q[3]);c.userData.folder='Glitch Den/Crystal Veins';veins.push(c);});groupActors(veins,'Chromatic Fracture Veins',{record:false,select:false,folder:'Glitch Den/Crystal Veins'});
  const throne=makeThrone([0,0,-18],'#d36cff',true,'Glitch Throne');throne.position.y+=1.8;throne.rotation.y=Math.PI;throne.userData.folder='Glitch Den/Throne Vault';
  [[-13,13,.55,'Crystal Gallery'],[13,13,-.55,'Dragon Gallery'],[-18,-10,.8,'Frost Vault'],[18,-10,-.8,'Ember Vault'],[0,-24,0,'Deep Forge Gate']].forEach(q=>{const arch=makeDenStructure('arch',[q[0],0,q[1]],true,q[3],'#8158b0');arch.rotation.y=q[2];arch.userData.folder='Glitch Den/Routes';});
  addPath('Fracture Circuit',[[0,13],[-12,11],[-18,2],[-14,-12],[0,-18],[14,-12],[18,2],[12,11],[0,13]]);
  const sw=makeGlitchDragonV3([17,0,8],'#7c55ff',true,'§wyrl§ Glitch Dragon',2.8,'#5cecff');sw.position.y+=3.3;sw.rotation.y=-2.2;sw.userData.role='primary-lalm-avatar';
  const frost=makeGlitchDragonV3([-18,0,-5],'#4fcfff',true,'Frost Forge Dragon',2.15,'#d7fbff');frost.position.y+=2.05;frost.rotation.y=1.3;
  const ember=makeGlitchDragonV3([14,0,-15],'#ff4f88',true,'Ember Glitch Dragon',2.0,'#ffb15c');ember.position.y+=1.9;ember.rotation.y=-.4;
  for(const q of [[0,7,0,'#7d5cff',3.2,26],[-18,6,-5,'#55ddff',2.4,20],[14,6,-15,'#ff5d8d',2.2,19],[0,9,-18,'#ff9b55',1.6,17]]){const l=new THREE.PointLight(q[3],q[4],q[5],2);l.position.set(q[0],q[1],q[2]);scene.add(l);}
  finishTemplate('hero');setRuntimeShellVisibility(false);orbit.target.set(0,3,0);perspectiveCamera.position.set(31,20,36);orbit.update();toast("Glitch Dragon Den · Fracture Forge loaded");
}
'''
    s=s[:a]+block+s[b:]

    # Dragon v3 decorates proven anatomy-v2 with coherent armor, crown, wing fingers and fracture energy.
    marker="function addPath(name, points){"
    if marker not in s: raise RuntimeError("v6.4 dragon insertion marker missing")
    dragon=r'''function makeGlitchDragonV3(pos,color='#8b5cff',baked=true,name='Glitch Dragon',scale=1,accent='#5cecff'){
  const d=makeDragon(pos,color,baked,name,scale);
  const armor=new THREE.MeshStandardMaterial({color:new THREE.Color(color).multiplyScalar(.52),metalness:.52,roughness:.3,emissive:new THREE.Color(accent),emissiveIntensity:.11,flatShading:true});
  const crystal=new THREE.MeshStandardMaterial({color:accent,metalness:.16,roughness:.16,emissive:accent,emissiveIntensity:.78,transparent:true,opacity:.9,flatShading:true});
  for(const side of [-1,1]){
    for(const q of [[.70,3.05,.20,.28],[.78,2.55,.68,.24],[.64,2.03,1.16,.20]]){const spike=new THREE.Mesh(new THREE.ConeGeometry(q[3],q[3]*3,6),crystal.clone());spike.position.set(side*q[0],q[1],q[2]);spike.rotation.z=side*.45;spike.castShadow=true;d.add(spike);}
    const cheek=new THREE.Mesh(new THREE.IcosahedronGeometry(.23,0),crystal.clone());cheek.position.set(side*.55,4.48,-1.62);cheek.scale.set(1,.65,1.65);d.add(cheek);
    const crown=new THREE.Mesh(new THREE.ConeGeometry(.15,.8,6),armor.clone());crown.position.set(side*.34,5.05,-1.18);crown.rotation.z=side*.24;d.add(crown);
  }
  for(const q of [[0,2.78,-.18,.42],[0,2.55,.40,.38],[0,2.27,.96,.34],[0,1.98,1.48,.29]]){const plate=new THREE.Mesh(new THREE.IcosahedronGeometry(q[3],0),armor.clone());plate.position.set(q[0],q[1],q[2]);plate.scale.set(1.45,.35,1.25);plate.castShadow=true;d.add(plate);}
  const halo=new THREE.Mesh(new THREE.TorusGeometry(.95,.045,8,32),crystal.clone());halo.position.set(0,4.46,-1.42);halo.rotation.x=Math.PI/2;d.add(halo);
  d.userData.blueprintClass='BP_GlitchDragonV3';d.userData.tags.push('dragon-anatomy-v3','crystal-armor','fracture-energy');return d;
}
'''
    s=s.replace(marker,dragon+"\n"+marker,1)

    # Update the single project card; no second Glitch Den.
    s=s.replace('<span class="template-tag">v6.2 VARIANT</span><p>The regular Dragon Den exactly — same architecture, layout, rooms, placements, exits and framing — with the Glitch visual identity layered over it.</p>','<span class="template-tag">v6.4 RESEARCHED</span><p>Dragon-scale Fracture Forge with layered cavern masses, chromatic crystal veins, throne vault, forge nexus, atmospheric lighting and redesigned crystal-armored dragons.</p>',1)
    return s
