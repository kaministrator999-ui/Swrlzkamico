/* Original Sheep Tag meadow assets. Authored transforms remain native scene data. */
function stMakeVisual(type){
  const g=new THREE.Group();g.name=type;
  const palette={cream:'#fff2d5',wool:'#fbf4e6',face:'#796147',hoof:'#534235',wood:'#a87943',woodDark:'#6c4e35',gold:'#f0c862',straw:'#d9af50',green:'#75a457',darkGreen:'#357558',teal:'#50c9bd',stone:'#a3b4ad',darkStone:'#677e7d',wolf:'#718393',wolfLight:'#bdcbd1',ink:'#26363c'};
  const materials={};
  function material(color,emissive=false){
    const key=color+(emissive?'!':'');
    return materials[key]||(materials[key]=new THREE.MeshStandardMaterial({color,roughness:.91,metalness:0,flatShading:true,...(emissive?{emissive:color,emissiveIntensity:.28}:{} )}));
  }
  function mesh(geo,color,pos=[0,0,0],parent=g,rotation=null){
    const o=new THREE.Mesh(geo,material(color));o.position.fromArray(pos);if(rotation)o.rotation.set(...rotation);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;
  }
  function box(size,color,pos,parent=g,rotation=null){return mesh(new THREE.BoxGeometry(...size),color,pos,parent,rotation);}
  function ball(radius,color,pos,scale=[1,1,1],parent=g,detail=1){const o=mesh(new THREE.IcosahedronGeometry(radius,detail),color,pos,parent);o.scale.fromArray(scale);return o;}
  function cylinder(top,bottom,height,color,pos,parent=g,sides=8){return mesh(new THREE.CylinderGeometry(top,bottom,height,sides),color,pos,parent);}
  function cone(radius,height,color,pos,parent=g,sides=6){return mesh(new THREE.ConeGeometry(radius,height,sides),color,pos,parent);}
  function roof(width,depth,height,color,pos){
    const shape=new THREE.Shape();shape.moveTo(-width/2,0);shape.lineTo(width/2,0);shape.lineTo(0,height);shape.closePath();
    const geo=new THREE.ExtrudeGeometry(shape,{depth,steps:1,bevelEnabled:false});geo.translate(0,0,-depth/2);return mesh(geo,color,pos);
  }
  function ring(radius,tube,color,pos,parent=g){return mesh(new THREE.TorusGeometry(radius,tube,5,32),color,pos,parent,[-Math.PI/2,0,0]);}
  function pivot(name,pos,parent=g){const p=new THREE.Group();p.name=name;p.position.fromArray(pos);parent.add(p);return p;}
  function eye(pos,parent=g,size=.04){ball(size,palette.ink,pos,[1,1,.55],parent,1);}
  function flowers(points){
    const geo=new THREE.CircleGeometry(.065,5),m=new THREE.MeshStandardMaterial({color:'#ffe18d',roughness:1,side:THREE.DoubleSide});
    const f=new THREE.InstancedMesh(geo,m,points.length),matrix=new THREE.Matrix4(),q=new THREE.Quaternion().setFromEuler(new THREE.Euler(-Math.PI/2,0,0));
    points.forEach((p,i)=>{matrix.compose(new THREE.Vector3(...p),q,new THREE.Vector3(1,1,1));f.setMatrixAt(i,matrix);});f.instanceMatrix.needsUpdate=true;f.receiveShadow=true;g.add(f);
  }
  function sheep(){
    // Four shoulder/hip pivots; the hoof sits below each pivot for clean gait arcs.
    [[-.23,.40,-.28],[.23,.40,-.28],[-.23,.40,.29],[.23,.40,.29]].forEach((p,i)=>{
      const leg=pivot('stLeg'+i,p);cylinder(.062,.065,.24,palette.face,[0,-.12,0],leg,6);box([.13,.095,.16],palette.hoof,[0,-.29,.01],leg);
    });
    ball(.41,palette.wool,[0,.68,-.025],[.82,.86,1.13]);
    for(const p of [[-.25,.63,-.15],[.25,.65,-.15],[-.21,.83,.08],[.21,.84,.09],[0,.93,-.12],[-.17,.78,-.37],[.17,.77,-.37],[0,.58,.34]])ball(.19,palette.cream,p,[1,1,1],g,0);
    const neck=pivot('stHead',[0,.73,.39]);
    ball(.21,palette.face,[0,.02,.12],[.83,1.13,.90],neck);
    ball(.15,palette.wool,[0,.17,.06],[1.16,.66,.86],neck);
    ball(.105,palette.face,[-.21,.10,.045],[1.3,.42,.58],neck);ball(.105,palette.face,[.21,.10,.045],[1.3,.42,.58],neck);
    ball(.048,'#e7bfa4',[-.255,.108,.065],[1,.5,.42],neck);ball(.048,'#e7bfa4',[.255,.108,.065],[1,.5,.42],neck);
    eye([-.083,.063,.283],neck,.031);eye([.083,.063,.283],neck,.031);
    ball(.026,'#e8d3b5',[-.043,-.036,.286],[1,.55,.44],neck);ball(.026,'#e8d3b5',[.043,-.036,.286],[1,.55,.44],neck);
    const tail=pivot('stTail',[0,.65,-.47]);ball(.095,palette.cream,[0,0,-.04],[.8,.9,1.3],tail,0);
    const collar=cylinder(.157,.157,.055,palette.teal,[0,-.145,.03],neck);collar.rotation.x=.25;
    ball(.048,palette.gold,[0,-.155,.19],[.7,1,.7],neck,0);
  }
  function wolf(){
    [[-.29,.65,-.45],[.29,.65,-.45],[-.28,.65,.41],[.28,.65,.41]].forEach((p,i)=>{
      const leg=pivot('stLeg'+i,p);cylinder(.085,.062,.46,palette.wolf,[0,-.23,0],leg,6);box([.20,.13,.28],palette.darkStone,[0,-.54,.055],leg);
    });
    ball(.57,palette.wolf,[0,.89,-.075],[.68,.78,1.31]);
    ball(.38,palette.wolfLight,[0,1.00,.39],[.90,1.12,.84],g,0);
    const head=pivot('stHead',[0,1.27,.61]);
    ball(.32,palette.wolf,[0,.08,.10],[.95,1,.99],head,0);
    cone(.137,.32,palette.wolf,[-.20,.38,.015],head,4);cone(.137,.32,palette.wolf,[.20,.38,.015],head,4);
    const innerLeft=cone(.070,.19,'#d5a79b',[-.20,.40,.065],head,3);innerLeft.scale.z=.32;
    const innerRight=cone(.070,.19,'#d5a79b',[.20,.40,.065],head,3);innerRight.scale.z=.32;
    ball(.21,palette.wolfLight,[0,-.035,.34],[.88,.58,1.45],head,0);
    ball(.097,palette.ink,[0,.006,.581],[.95,.70,.72],head,0);
    eye([-.145,.125,.35],head,.045);eye([.145,.125,.35],head,.045);
    ball(.019,palette.gold,[-.145,.13,.374],[1,1,.5],head);ball(.019,palette.gold,[.145,.13,.374],[1,1,.5],head);
    const collar=cylinder(.28,.28,.09,'#c96359',[0,1.115,.56]);collar.rotation.x=.32;
    box([.1,.15,.06],palette.gold,[0,1.035,.845]);
    const tail=pivot('stTail',[0,.94,-.80]);tail.rotation.x=-.43;
    const tailBase=cone(.17,.65,palette.wolf,[0,.13,-.12],tail);tailBase.rotation.x=-Math.PI/2-.4;
    ball(.115,palette.wolfLight,[0,.20,-.44],[1,1,1.4],tail,0);
  }
  function hut(kind){
    box([2.34,.13,2.34],kind==='st-fort'?palette.darkStone:palette.woodDark,[0,.065,0]);
    if(kind==='st-fort'){
      box([1.98,1.38,1.98],palette.stone,[0,.82,0]);
      box([1.78,.14,1.78],palette.darkStone,[0,1.59,0]);
      for(const x of [-.83,0,.83])for(const z of [-.83,.83])box([.38,.35,.35],palette.stone,[x,1.8,z]);
      for(const z of [0])for(const x of [-.83,.83])box([.35,.35,.38],palette.stone,[x,1.8,z]);
      box([.48,.87,.055],palette.woodDark,[0,.6,1.02]);
      for(const x of [-.73,.73])box([.16,.40,.045],palette.darkStone,[x,.91,1.026]);
      box([.14,.14,.08],palette.gold,[.15,.58,1.06]);
      for(const x of [-1.08,1.08])for(const z of [-.95,-.32,.32,.95]){
        cylinder(.065,.065,1.30,palette.wood,[x,.71,z]);cone(.073,.19,palette.woodDark,[x,1.46,z]);
      }
      const flag=pivot('stFlag',[.72,2.04,-.72]);cylinder(.024,.024,.87,palette.woodDark,[0,.34,0],flag,5);box([.42,.23,.024],palette.teal,[.20,.60,0],flag);
      return;
    }
    box([1.74,1.12,1.68],palette.cream,[0,.69,0]);
    for(const x of [-.89,.89])for(const z of [-.85,.85])box([.11,1.22,.11],palette.wood,[x,.74,z]);
    box([1.91,.11,1.82],palette.wood,[0,1.27,0]);
    for(const x of [-.91,.91])box([.07,.10,1.7],palette.wood,[x,.69,0]);
    roof(2.19,2.12,.78,palette.straw,[0,1.27,0]);
    // The triangular prism peaks at 2.05 m; its ridge follows local Z.
    box([.48,.76,.055],palette.woodDark,[0,.53,.858]);
    for(const x of [-.59,.59]){
      box([.31,.32,.065],palette.teal,[x,.88,.862]);box([.035,.36,.073],palette.wood,[x,.88,.904]);box([.35,.035,.073],palette.wood,[x,.88,.904]);
    }
    box([.07,.08,.07],palette.gold,[.12,.51,.90]);
    box([.92,.09,.27],palette.wood,[0,.21,1.005]);
    for(const x of [-1.03,1.03])for(const z of [-1.03,1.03])box([.10,.55,.10],palette.wood,[x,.36,z]);
    for(const x of [-1.03,1.03])box([.055,.055,2.02],palette.wood,[x,.52,0]);
    if(kind==='st-income'){
      box([.56,.87,.48],palette.wood,[.30,1.64,-.39]);
      const rotor=pivot('stWindmillRotor',[.30,2.26,-.68]);
      for(let i=0;i<4;i++){
        const blade=pivot('stBlade'+i,[0,0,0],rotor);blade.rotation.z=i*Math.PI/2;
        box([.075,.78,.065],palette.woodDark,[0,.40,0],blade);box([.25,.50,.065],palette.cream,[.087,.53,-.009],blade);
      }
      ball(.105,palette.gold,[0,0,-.065],[1,1,.64],rotor,0);
      box([.71,.14,.47],palette.woodDark,[-.57,.21,-.60]);
      for(let i=0;i<5;i++){const x=-.82+i*.13;cylinder(.017,.017,.39,palette.green,[x,.43,-.6],g,4);ball(.047,palette.gold,[x,.65,-.60],[.8,1.6,.8],g,0);}
      box([.38,.36,.04],palette.green,[-.57,.40,1.07]);
      ball(.08,palette.gold,[-.57,.41,1.10],[1,1,.2],g,0);
    }else{
      box([.31,.33,.38],palette.wood,[.58,2.04,-.36]);box([.36,.06,.42],palette.woodDark,[.58,2.23,-.36]);
      ball(.11,palette.cream,[.62,2.4,-.35],[1.1,.7,1],g,0);
      box([.45,.22,.30],palette.green,[-.61,.30,1.03]);
      flowers([[-.76,.43,1.01],[-.60,.44,1.06],[-.45,.43,1.0]]);
    }
  }
  function sanctuary(){
    cylinder(4.55,4.85,.15,'#abc9b5',[0,.08,0],g,32);
    cylinder(3.40,3.55,.07,'#dbe4cb',[0,.185,0],g,32);
    ring(3.30,.038,palette.gold,[0,.232,0]);ring(1.20,.048,palette.teal,[0,.239,0]);
    // Corner piers leave a wide approach through each cardinal direction.
    for(const x of [-3.05,3.05])for(const z of [-3.05,3.05]){
      box([1.07,.27,1.07],palette.darkStone,[x,.22,z]);box([.79,1.30,.79],palette.stone,[x,.95,z]);
      box([.94,.15,.94],palette.cream,[x,1.62,z]);
      const crystal=mesh(new THREE.OctahedronGeometry(.25),palette.teal,[x,1.94,z]);crystal.scale.y=1.4;crystal.material=material(palette.teal,true);
    }
    for(let i=0;i<4;i++){
      const a=Math.PI/4+i*Math.PI/2;
      for(const offset of [-.24,.24]){const t=a+offset,x=Math.sin(t)*4.37,z=Math.cos(t)*4.37;box([.64,.38,.28],palette.stone,[x,.36,z],g,[0,t,0]);}
    }
    cylinder(.62,.79,.26,palette.darkStone,[0,.3,0],g,12);
    cylinder(.48,.60,.07,palette.gold,[0,.465,0],g,12);
    const spirit=mesh(new THREE.OctahedronGeometry(.39),palette.teal,[0,1.05,0]);spirit.scale.y=1.48;spirit.material=material(palette.teal,true);spirit.name='stSpiritCrystal';
    const halo=ring(.75,.032,palette.gold,[0,1.10,0]);halo.rotation.x=-Math.PI/3;
    flowers([[-2.4,.239,.8],[2.5,.239,-1.0],[.8,.239,2.7],[-.9,.239,-2.6]]);
  }
  function tree(){
    cylinder(.19,.32,1.44,palette.wood,[0,.72,0],g,7);
    cone(1.65,2.25,palette.darkGreen,[0,2.28,0],g,7);
    cone(1.25,1.94,'#498b57',[0,3.23,0],g,7);
    cone(.82,1.63,'#79a95e',[0,4.13,0],g,7);
    ball(.22,'#bfcc82',[-.23,.19,.32],[1.4,.55,1.0],g,0);
  }
  function rock(){
    ball(.99,palette.darkStone,[-.47,.49,-.17],[1.0,.76,.88],g,0);
    ball(.77,palette.stone,[.66,.41,.33],[1.08,.85,1.03],g,0);
    ball(.44,'#bfd0bd',[-.04,.18,.93],[1.26,.74,1],g,0);
    ball(.30,palette.green,[-.68,.70,-.15],[1.1,.3,1.2],g,0);
  }
  function pond(){
    const water=mesh(new THREE.CircleGeometry(2.4,24),palette.teal,[0,.075,0],g,[-Math.PI/2,0,0]);water.scale.set(1.1,.88,1);water.material=new THREE.MeshStandardMaterial({color:'#58b9c1',roughness:.35,metalness:.05});
    for(let i=0;i<17;i++){
      const a=i*Math.PI*2/17,r=2.4;ball(.27,i%3===0?palette.cream:palette.stone,[Math.cos(a)*r*1.1,.16,Math.sin(a)*r*.88],[1.25,.49,1],g,0);
    }
    for(const p of [[1.60,.13,.62],[-1.28,.13,-.51],[-.50,.13,1.26]]){
      const lily=mesh(new THREE.CircleGeometry(.23,7),palette.darkGreen,p,g,[-Math.PI/2,0,0]);lily.rotation.z=.2;
      ball(.05,'#ffe8b6',[p[0],p[1]+.05,p[2]],[1,1.4,1],g,0);
    }
    for(const [x,z] of [[-2.07,1.16],[1.93,-1.11]])for(let i=0;i<3;i++){
      cylinder(.022,.022,.70,palette.darkGreen,[x+i*.12,.38,z],g,4);cylinder(.05,.05,.18,palette.gold,[x+i*.12,.81,z],g,5);
    }
    const ripple=ring(.46,.014,'#a5e5dd',[.66,.101,-.84]);ripple.scale.z=.7;
  }
  function shop(){
    box([2.8,.14,2.7],palette.woodDark,[0,.07,0]);
    for(const x of [-1.15,1.15])for(const z of [-1.09,1.09])cylinder(.046,.046,1.87,palette.wood,[x,1.01,z],g,6);
    box([2.55,.88,.16],palette.cream,[0,.68,-1.12]);
    roof(2.75,2.58,.65,palette.teal,[0,1.56,0]);
    for(const x of [-.89,-.45,0,.45,.89])box([.22,.24,.04],palette.gold,[x,1.53,1.21]);
    box([2.1,.63,.65],palette.wood,[0,.41,.76]);box([2.24,.08,.74],palette.gold,[0,.765,.76]);
    for(const p of [[-.7,.91,.77],[.0,.91,.70],[.61,.90,.8]]){
      cylinder(.14,.18,.24,palette.woodDark,p,g,8);ball(.115,palette.gold,[p[0],p[1]+.145,p[2]],[1.1,.48,1.1],g,0);
    }
    box([.70,.61,.055],palette.woodDark,[0,1.25,-1.18]);
    ball(.15,palette.gold,[0,1.26,-1.222],[1,1,.2],g,1);
    box([.22,.34,.055],palette.teal,[0,1.26,-1.25],g,[0,0,Math.PI/4]);
    cylinder(.06,.065,.42,palette.wood,[-1.22,.26,1.14],g,6);ball(.15,palette.green,[-1.22,.50,1.14],[1,.65,1],g,0);
  }
  function meadow(){
    // A single original canvas surface supplies paths, grass variation and flowers.
    const canvas=document.createElement('canvas');canvas.width=canvas.height=1024;const c=canvas.getContext('2d');
    c.fillStyle='#80a85e';c.fillRect(0,0,1024,1024);
    let seed=104729;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
    for(let i=0;i<3400;i++){
      const x=rand()*1024,y=rand()*1024,r=6+rand()*30;c.fillStyle=i%2?'#82aa6255':'#72995355';c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();
    }
    c.strokeStyle='#d4c598';c.lineWidth=29;c.lineCap='round';
    for(const line of [[[512,64],[512,960]],[[64,512],[960,512]]]){c.beginPath();c.moveTo(...line[0]);c.lineTo(...line[1]);c.stroke();}
    c.strokeStyle='#dfd1a988';c.lineWidth=17;
    for(const path of [[[85,140],[225,200],[350,370],[512,512]],[[938,140],[800,200],[665,370],[512,512]],[[85,887],[230,816],[350,655],[512,512]],[[938,887],[800,816],[665,655],[512,512]]]){
      c.beginPath();c.moveTo(...path[0]);for(const p of path.slice(1))c.lineTo(...p);c.stroke();
    }
    c.fillStyle='#c4d39c';c.beginPath();c.arc(512,512,64,0,Math.PI*2);c.fill();
    c.strokeStyle='#d6ddb817';c.lineWidth=1;
    for(let p=512%30.72;p<1024;p+=30.72){c.beginPath();c.moveTo(p,0);c.lineTo(p,1024);c.stroke();c.beginPath();c.moveTo(0,p);c.lineTo(1024,p);c.stroke();}
    for(let i=0;i<2900;i++){
      const x=rand()*1024,y=rand()*1024;if(Math.abs(x-512)<25||Math.abs(y-512)<25||Math.hypot(x-512,y-512)<70)continue;
      c.fillStyle=i%11===0?'#f5dda6':i%7===0?'#e4e9bb':'#547b434f';c.fillRect(x,y,i%11===0?2:1,2);
    }
    const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;
    const ground=new THREE.Mesh(new THREE.PlaneGeometry(80,80),new THREE.MeshStandardMaterial({map:texture,color:'#ffffff',roughness:1,metalness:0}));ground.rotation.x=-Math.PI/2;ground.position.y=.04;ground.receiveShadow=true;ground.name='stMeadowGround';g.add(ground);
    const base=box([80,.20,80],'#5a7948',[0,-.075,0]);base.castShadow=false;base.receiveShadow=false;
  }
  if(type==='st-sheep')sheep();else if(type==='st-wolf')wolf();else if(['st-farm','st-income','st-fort'].includes(type))hut(type);
  else if(type==='st-pen')sanctuary();else if(type==='st-tree')tree();else if(type==='st-rock')rock();else if(type==='st-pond')pond();else if(type==='st-shop')shop();else if(type==='st-meadow')meadow();
  else throw new Error('Unknown Sheep Tag visual '+type);
  return g;
}

function stPrefab(type,pos=[0,0,0],baked=true,name=''){
  const labels={'st-sheep':'Sheep builder','st-wolf':'Wolf hunter','st-farm':'Shelter farm','st-income':'Golden windmill','st-fort':'Fortified farm','st-pen':'Spirit sanctuary','st-tree':'Meadow pine','st-rock':'Mossy boulders','st-pond':'Lily pond','st-shop':'Meadow merchant','st-meadow':'Sheep Tag meadow'};
  const unit=type==='st-sheep'||type==='st-wolf',building=['st-farm','st-income','st-fort','st-shop'].includes(type);
  const radius={'st-sheep':.27,'st-wolf':.68,'st-farm':1.2,'st-income':1.2,'st-fort':1.2,'st-tree':1.7,'st-rock':1.8,'st-pond':3,'st-shop':1.5}[type]||0;
  const actor=markActor(stMakeVisual(type),type,{name:name||labels[type]||type,baked,team:type==='st-sheep'?'blue':type==='st-wolf'?'red':'neutral',folder:'Sheep Tag/'+(unit?'Units':building?'Buildings':'Meadow'),blueprintClass:'SheepTag/'+type.slice(3),components:['Transform','Scene','StaticMesh',...(radius?['Collider']:[])],colliderRadius:radius,role:type==='st-sheep'?'sheep':type==='st-wolf'?'wolf':'',tags:['sheep-tag']});
  actor.position.fromArray(pos);actor.userData.spawnPos=actor.position.toArray();return actor;
}
