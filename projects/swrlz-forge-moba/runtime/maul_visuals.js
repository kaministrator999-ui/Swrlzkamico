// Original Frostveil models: native editable assets, shared by authoring and Play.
const MAUL_TYPES=['maul-sector','maul-cliff','maul-spawn','maul-gate','maul-exit','maul-builder','maul-arrow','maul-cannon','maul-frost','maul-storm','maul-maze-wall','maul-pine','maul-banner'];
const MAUL_COLORS={arrow:'#f6bd65',cannon:'#ed7650',frost:'#73dcf4',storm:'#bca1ff','maze-wall':'#8cabb3'};
function maulMakeVisual(kind,level=1){
  const g=new THREE.Group();g.name='Frostveil '+kind;
  const material=color=>new THREE.MeshStandardMaterial({color,roughness:.75,metalness:.12,flatShading:true});
  const add=(geo,color,p=[0,0,0],parent=g)=>{const m=new THREE.Mesh(geo,material(color));m.position.fromArray(p);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;};
  const box=(s,c,p,parent)=>add(new THREE.BoxGeometry(...s),c,p,parent);
  const cyl=(r,R,h,c,p)=>add(new THREE.CylinderGeometry(r,R,h,8),c,p);
  const gem=(r,c,p)=>{const m=add(new THREE.OctahedronGeometry(r),c,p);m.material.emissive.set(c);m.material.emissiveIntensity=.45;return m;};
  if(kind==='sector'){
    box([18,.22,20],'#607d86',[0,-.14,0]);
    const geo=new THREE.BoxGeometry(1.94,.035,1.94),m=material('#91aeb5'),tiles=new THREE.InstancedMesh(geo,m,90),matrix=new THREE.Matrix4();
    let i=0;for(let x=0;x<9;x++)for(let z=0;z<10;z++){matrix.makeTranslation((x-4)*2,-.006,(z-4.5)*2);tiles.setMatrixAt(i++,matrix);}tiles.receiveShadow=true;g.add(tiles);
    return g;
  }
  if(kind==='cliff'){box([2,1.25,2],'#364e5b',[0,.52,0]);box([1.94,.12,1.94],'#ccdfe4',[0,1.19,0]);return g;}
  if(kind==='pine'){cyl(.15,.25,1.5,'#514b40',[0,.75,0]);for(let i=0;i<3;i++){add(new THREE.ConeGeometry(1.5-i*.32,2,7),'#314f54',[0,1.7+i*.7,0]);add(new THREE.ConeGeometry(1.43-i*.32,.5,7),'#c8dce2',[0,2.39+i*.7,0]);}return g;}
  if(kind==='banner'){cyl(.055,.07,3.7,'#aebfc6',[0,1.85,0]);box([1.25,1.55,.055],'#263954',[.55,2.68,0]);gem(.18,'#f6bd65',[.55,2.73,.05]);return g;}
  if(['spawn','gate','exit'].includes(kind)){
    const color=kind==='spawn'?'#c790fb':kind==='gate'?'#f6cc77':'#85f3ce';
    cyl(.83,.95,.10,'#314959',[0,.02,0]);const r=add(new THREE.TorusGeometry(.75,.065,6,24),color,[0,.09,0]);r.rotation.x=-Math.PI/2;
    if(kind==='spawn'){const portal=add(new THREE.TorusGeometry(.7,.10,6,24),color,[0,1.1,0]);portal.name='PortalRing';gem(.25,color,[0,1.08,0]);}
    if(kind==='gate'){for(const x of [-.7,.7]){cyl(.12,.16,.75,'#516e7b',[x,.4,0]);gem(.16,color,[x,.85,0]);}}
    if(kind==='exit'){cyl(.55,.75,.6,'#344d5b',[0,.3,0]);gem(.6,color,[0,1.3,0]);const halo=add(new THREE.TorusGeometry(1,.035,5,32),color,[0,1.1,0]);halo.rotation.x=Math.PI/2;}
    return g;
  }
  if(kind==='builder'){
    const body=cyl(.21,.35,.7,'#316179',[0,.64,0]);body.name='BuilderRobe';add(new THREE.SphereGeometry(.21,8,6),'#eed0a7',[0,1.2,0]);add(new THREE.ConeGeometry(.36,.58,7),'#4ca5ba',[0,1.62,0]);
    for(const x of [-.21,.21]){box([.17,.17,.28],'#263c4c',[x,.11,.08]);const arm=new THREE.Group();arm.name='BuilderArm'+x;arm.position.set(x,.88,0);g.add(arm);box([.15,.48,.16],'#4091a6',[0,-.13,0],arm);}
    cyl(.035,.035,.9,'#dfbc77',[.43,.6,.18]);gem(.12,'#73dcf4',[.43,1.12,.18]);return g;
  }
  if(['creep','air-creep','boss'].includes(kind)){
    const air=kind==='air-creep',boss=kind==='boss',color=boss?'#b05680':air?'#896cc0':'#b29a86';
    const body=add(new THREE.IcosahedronGeometry(.47,0),color,[0,.7,0]);body.scale.set(.8,1,1.12);
    add(new THREE.IcosahedronGeometry(.26,0),'#e5d6bd',[0,1.16,.23]);
    for(const x of [-.15,.15])add(new THREE.SphereGeometry(.035,6,4),'#151e2a',[x,1.21,.46]);
    for(let i=0;i<4;i++){const p=new THREE.Group();p.name='CreepLeg'+i;p.position.set(i%2? .27:-.27,.52,i<2?-.24:.24);g.add(p);box([.13,.48,.15],'#5a5160',[0,-.19,0],p);}
    if(air)for(const side of [-1,1]){const wing=new THREE.Group();wing.name='CreepWing'+side;wing.position.set(side*.27,.88,0);g.add(wing);const w=box([1.05,.07,.65],'#bba2ea',[side*.5,0,-.07],wing);w.rotation.y=side*.3;}
    if(boss){g.scale.setScalar(1.7);for(const x of [-.3,.3])add(new THREE.ConeGeometry(.13,.48,4),'#f8ce84',[x,1.55,.13]);}
    const bar=box([.85,.08,.07],'#7cebaf',[0,boss?1.5:1.73,0]);bar.name='HealthFill';return g;
  }
  const color=MAUL_COLORS[kind]||'#f6bd65';
  box([1.82,.18,1.82],'#304956',[0,.09,0]);box([1.65,.12,1.65],'#cbd9d5',[0,.22,0]);
  if(kind==='maze-wall'){box([1.65,1.18,1.65],'#678593',[0,.86,0]);for(const x of [-.55,0,.55])box([.38,.3,1.65],'#a2b8bf',[x,1.58,0]);return g;}
  cyl(.54,.72,1.25,'#4f6976',[0,.94,0]);cyl(.72,.63,.19,'#b7cbd0',[0,1.59,0]);
  for(let i=0;i<level;i++){const ring=add(new THREE.TorusGeometry(.61,.035,5,20),color,[0,.48+i*.3,0]);ring.rotation.x=Math.PI/2;}
  const head=new THREE.Group();head.name='TowerHead';head.position.y=1.75;g.add(head);
  if(kind==='arrow'){box([1.25,.11,.15],'#b79a67',[0,.17,.02],head);box([.14,.16,1.03],color,[0,.19,.13],head);box([.25,.23,.30],'#3c5260',[0,.11,-.26],head);}
  if(kind==='cannon'){const barrel=add(new THREE.CylinderGeometry(.25,.32,1.12,8),'#334955',[0,.15,.25],head);barrel.rotation.x=Math.PI/2;box([.8,.31,.65],color,[0,0,0],head);}
  if(kind==='frost'){const crystal=add(new THREE.OctahedronGeometry(.58),color,[0,.52,0],head);crystal.scale.y=1.4;crystal.material.emissive.set(color);crystal.material.emissiveIntensity=.55;}
  if(kind==='storm'){const crystal=add(new THREE.IcosahedronGeometry(.36,1),color,[0,.48,0],head);crystal.material.emissive.set(color);crystal.material.emissiveIntensity=.7;const halo=add(new THREE.TorusGeometry(.59,.035,5,24),color,[0,.48,0],head);halo.rotation.x=.4;}
  return g;
}
function maulPrefab(type,position=[0,0,0],baked=true,name=null){
  const kind=type.slice(5),object=maulMakeVisual(kind);object.position.fromArray(position);
  return markActor(object,type,{name:name||'Frostveil '+kind,baked,folder:'Maul/'+(MAUL_CORE.definitions[kind]?'Towers':['spawn','gate','exit','builder'].includes(kind)?'Gameplay':'Map'),components:['Transform','Scene','StaticMesh'],blueprintClass:'Maul/'+kind,colliderRadius:0,role:kind,tags:['maul','frostveil']});
}
for(const type of MAUL_TYPES)ASSET_LIBRARY.push({id:type,name:'Frostveil '+type.slice(5),path:'/Engine/Maul',desc:'Editable Maul map piece. Bake changes and test using native Play.'});
