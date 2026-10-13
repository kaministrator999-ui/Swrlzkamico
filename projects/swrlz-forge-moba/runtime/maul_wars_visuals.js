// Original §E snowy arena pieces; no Warcraft game assets are embedded.
const WARS_TYPES=['sector','cliff','spawn','gate','exit','builder','shrine','air-nest','pine','banner',...Object.keys(MAUL_CORE.definitions)].map(k=>'maul-wars-'+k);
const WARS_PLAYER_COLORS=['#ed636b','#689fff','#5cdbd4','#b587eb','#ebd56c','#f5a265'];
function warsMakeVisual(kind,level=1,meta={}){
  const g=new THREE.Group();g.name='Frostveil Wars '+kind;
  const mat=color=>new THREE.MeshStandardMaterial({color,roughness:.8,metalness:.12,flatShading:true});
  const add=(geo,color,p=[0,0,0],parent=g)=>{const m=new THREE.Mesh(geo,mat(color));m.position.fromArray(p);m.receiveShadow=true;m.castShadow=true;parent.add(m);return m;};
  const box=(size,color,p,parent)=>add(new THREE.BoxGeometry(...size),color,p,parent);
  const cyl=(r,R,h,color,p)=>add(new THREE.CylinderGeometry(r,R,h,8),color,p);
  const color=WARS_PLAYER_COLORS[meta.sector??(meta.team?3:0)];
  if(kind==='cliff'){
    box([2,1.25,2],'#284858',[0,.52,0]);const top=box([1.94,.12,1.94],'#d5e9eb',[0,1.19,0]);top.name='WarsIceTop';return g;
  }
  if(kind==='sector'){
    box([94,.32,48],'#789cac',[0,-.20,0]);
    const tiles=new THREE.InstancedMesh(new THREE.BoxGeometry(1.96,.025,1.96),mat('#d4e9ec'),47*24),matrix=new THREE.Matrix4();
    let i=0;for(let x=0;x<47;x++)for(let z=0;z<24;z++){matrix.makeTranslation((x-23)*2,-.026,(z-11.5)*2);tiles.setMatrixAt(i,matrix);tiles.setColorAt(i,new THREE.Color((x+z)%3?'#c2e0e6':'#cce8ed'));i++;}
    tiles.receiveShadow=true;g.add(tiles);return g;
  }
  if(kind==='shrine'||kind==='air-nest'){
    box([3.4,.25,3.4],'#364f63',[0,.12,0]);box([3.2,.13,3.2],'#d1e2e6',[0,.31,0]);
    for(const x of [-1,1])for(const z of [-1,1])cyl(.16,.24,2,'#68889d',[x,1.35,z]);
    if(kind==='shrine'){const roof=add(new THREE.ConeGeometry(2.3,1.1,4),color,[0,2.75,0]);roof.name='WarsFlag';roof.rotation.y=Math.PI/4;const gem=add(new THREE.OctahedronGeometry(.55),'#83e6ff',[0,1.4,0]);gem.material.emissive.set('#4fcfff');gem.material.emissiveIntensity=.45;}
    else {const ring=add(new THREE.TorusGeometry(1.15,.16,6,24),color,[0,2.4,0]);ring.name='WarsFlag';ring.rotation.x=Math.PI/2;box([2.4,.17,2.4],'#8db2bf',[0,2.2,0]);for(const side of [-1,1]){const wing=box([1.4,.13,.65],color,[side*1.0,2.7,0]);wing.name='WarsFlag';wing.rotation.z=side*.3;}}
    return g;
  }
  if(kind==='exit'){
    // Each defending team has its own ship, matching the Wars exit landmark.
    const hull=add(new THREE.CylinderGeometry(.7,1.25,3.2,6),'#665742',[0,.68,0]);hull.rotation.x=Math.PI/2;hull.scale.z=.58;
    box([1.7,.16,3.05],'#b79c77',[0,1.05,0]);cyl(.065,.095,3.5,'#c3b18e',[0,2.15,0]);
    box([1.6,1.55,.05],'#edf1e8',[.52,2.55,0]);box([.6,.40,.06],color,[.4,3.64,0]).name='WarsFlag';
    const ring=add(new THREE.TorusGeometry(1.65,.055,6,32),color,[0,.055,0]);ring.rotation.x=-Math.PI/2;return g;
  }
  if(kind==='gate'){
    const beacon=maulMakeVisual('gate');g.add(beacon);const beam=new THREE.Mesh(new THREE.CylinderGeometry(.018,.045,4.5,5),new THREE.MeshBasicMaterial({color:'#a4eaff',transparent:true,opacity:.65,depthWrite:false}));beam.position.y=2.4;g.add(beam);return g;
  }
  const prior=maulMakeVisual(kind,level);g.add(prior);
  if(kind==='banner')prior.traverse(n=>{if(n.isMesh&&n.geometry?.type==='BoxGeometry'){n.name='WarsFlag';n.material.color.set(color);}});
  if(kind==='builder')prior.traverse(n=>{if(n.name==='BuilderRobe')n.material.color.set(color);});
  return g;
}
function warsPrefab(type,position=[0,0,0],baked=true,name=null){
  const kind=type.slice(10),object=warsMakeVisual(kind);object.position.fromArray(position);
  return markActor(object,type,{name:name||'Frostveil Wars '+kind,baked,folder:'Wintermaul Wars/'+(MAUL_CORE.definitions[kind]?'Towers':['builder','spawn','gate','exit'].includes(kind)?'Gameplay':'Map'),components:['Transform','Scene','StaticMesh'],blueprintClass:'MaulWars/'+kind,colliderRadius:0,role:kind,tags:['maul-wars','frostveil']});
}
for(const type of WARS_TYPES)ASSET_LIBRARY.push({id:type,name:'Wars '+type.slice(10),path:'/Engine/WintermaulWars',desc:'Native snowy Wars arena piece. Bake and test with Play.'});
