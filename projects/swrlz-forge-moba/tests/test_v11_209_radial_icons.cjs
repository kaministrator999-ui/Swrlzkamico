// §E v11.209 - illustrated Sheep Tag Play wheels; cached icon GPU lifecycle.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
let now=1000,canvasCreated=0,textureDisposed=0,geometryDisposed=0,materialDisposed=0;
let nativeRootCalls=0,nativeShows=0,nativeHighlights=0,nativeSteps=0,nativeDisposes=0;
let nativeTextCreates=0,commandCalls=0;
class V{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z})}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this}
}
class Geo{constructor(...params){this.parameters=params;this.disposed=false}
 dispose(){assert.equal(this.disposed,false);this.disposed=true;geometryDisposed++}
 setAttribute(){}}
class Mat{constructor(params={}){Object.assign(this,params);this.opacity=params.opacity??1;
 this.color={setHex:n=>{this.colorValue=n}};this.disposed=false}
 dispose(){assert.equal(this.disposed,false);this.disposed=true;materialDisposed++}}
class O{
 constructor(){this.children=[];this.userData={};this.position=new V();this.rotation={z:0};
 this.scale={x:1,y:1,z:1,setScalar:n=>{this.scale.x=this.scale.y=this.scale.z=n}};
 this.visible=true;this.renderOrder=0;}
 add(obj){this.children.push(obj);obj.parent=this}
 traverse(fn){fn(this);this.children.forEach(c=>c.traverse?c.traverse(fn):fn(c))}
}
class Mesh extends O{constructor(geometry,material){super();this.geometry=geometry;this.material=material}}
class Points extends Mesh{}
class Tex{constructor(canvas){this.canvas=canvas;this.userData={};this.disposed=false}
 dispose(){assert.equal(this.disposed,false);this.disposed=true;textureDisposed++}}
const texCache=new Map();
const menuText=(label)=>{if(!texCache.has(label)){nativeTextCreates++;texCache.set(label,{text:label})}return texCache.get(label)};
const screen={
 createRadialGradient(){return {addColorStop(){}}},
 clearRect(){},beginPath(){},arc(){},fill(){},stroke(){},
 fillRect(){},moveTo(){},lineTo(){},closePath(){},
};
const build=[
{id:'st-farm',label:'FARM',color:0x5ddbbb},
{id:'st-income',label:'INCOME',color:0xf1cf80},
{id:'st-fort',label:'FORT',color:0x99b8e8},
{id:null,label:'CANCEL',color:0xadb5bf}
];
const skill=[
{id:'split',label:'MIRROR',color:0x71dafa},
{id:'totem',label:'TOTEM',color:0x78da9f},
{id:null,label:'NONE',color:0xa6b2c6}
];
const s={rules:{split:true,totems:false},resources:{u:50},controlledId:'u'};
const ctx={
 console,Math,performance:{now:()=>now},document:{
 createElement(type){assert.equal(type,'canvas');canvasCreated++;
 return {width:0,height:0,getContext:()=>screen}}
 },
 THREE:{Group:O,Mesh,Points,RingGeometry:Geo,PlaneGeometry:Geo,CircleGeometry:Geo,
 BufferGeometry:Geo,BufferAttribute:class{constructor(a,n){this.array=a;this.itemSize=n}},
 MeshBasicMaterial:Mat,PointsMaterial:Mat,CanvasTexture:Tex,DoubleSide:2,
 SRGBColorSpace:'srgb',LinearFilter:'linear',LinearMipmapLinearFilter:'mipmap'},
 se204:{wheel:null,wheels:new Map()},
 se204Buildings:build,se204Skills:skill,
 stSession:s,stUi:{buildingId:null,rotation:1},
 se195Text:menuText,stBuildingConfig:kind=>({
 'st-farm':{cost:0},'st-income':{cost:60},'st-fort':{cost:100}}[kind]),
 se204SkillReady:id=>!!s.rules[id==='split'?'split':'totems'],
 se204WheelRoot:type=>{
  nativeRootCalls++;
  const root=new O();root.name=type;root.visible=false;
  root.add(new Mesh(new Geo(),new Mat()));
  root.add(new Mesh(new Geo(),new Mat()));
  root.add(new Mesh(new Geo(),new Mat()));
  const entries=type==='build'?build:skill;
  const items=entries.map(entry=>{
   const mesh=new Mesh(new Geo(),new Mat());
   root.add(mesh);return {entry,mesh};
  });
  return {root,items,selected:0,type};
 },
 se204WheelShow:type=>{
  nativeShows++;const current=ctx.se204;
  let panel=current.wheels.get(type);
  if(!panel){panel=ctx.se204WheelRoot(type);current.wheels.set(type,panel)}
  current.wheel=panel;panel.root.visible=true;
  ctx.se204WheelHighlight(true);
 },
 se204WheelHighlight:()=>{nativeHighlights++},
 se204WheelStep:record=>{
  nativeSteps++;const panel=ctx.se204.wheel;
  if(panel&&Number.isInteger(record?.selected)&&record.selected<panel.items.length){
   if(panel.selected!==record.selected){
    panel.selected=record.selected;ctx.se204WheelHighlight();
   }
  }
 },
 se204WheelDispose:()=>{
  nativeDisposes++;
  for(const panel of ctx.se204.wheels.values()){
   panel.root.traverse(o=>{o.geometry?.dispose?.();o.material?.dispose?.()});
  }
  ctx.se204.wheels.clear();ctx.se204.wheel=null;
 },
 window:{}
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'engine_xr_sheep_radial_icons_feedback_v11_209.js'),'utf8'),ctx);
const art=vm.runInContext('se209',ctx);
const diag=()=>ctx.window.SWYRL_ENGINE_SHEEP_RADIAL_ICONS_209.diagnose();
assert.equal(diag().active,false);
ctx.se204WheelShow('build');
assert.equal(nativeRootCalls,1);assert.equal(nativeShows,1);
assert.equal(diag().active,true);
assert.equal(diag().decoratedWheels,1);
assert.equal(diag().wheelSegments,4);
assert.equal(diag().newIconTextures,4,'three houses and one Cancel icon');
assert.equal(canvasCreated,4,'icons rendered once only');
assert.equal(diag().cachedIconTextures,4);
const house=ctx.se204.wheel;
const ui=house.root.userData.se209Decor;
assert.ok(ui&&ui.wedges.length===4);
assert.equal(ui.icons.length,4);
assert.equal(ui.centers.length,4);
assert.equal(ui.glints.geometry.parameters.length,0);
assert.equal(ui.glints.geometry.attribute===undefined,true);
assert.ok(house.root.children.length>16);
assert.equal(house.root.children[2].position.y,.083);
assert.equal(house.root.children[2].scale.x,.72);
assert.equal(ui.statusKey,'0 GOLD');
assert.equal(ui.centers.filter(x=>x.visible).length,1);
assert.equal(ui.centers[0].visible,true);
assert.equal(ui.wedges[0].material.opacity,.45);
assert.equal(ui.icons[0].material.opacity,1);
const drawCalls=ui.icons.length+ui.wedges.length;
assert.equal(drawCalls,8);
ctx.se204WheelStep({selected:1});
assert.equal(house.selected,1);
assert.equal(ui.statusKey,'NEED 60 GOLD');
assert.equal(ui.icons[1].material.opacity,.28,'unaffordable house dimmed');
assert.equal(ui.centers[1].visible,true);
assert.equal(ui.centers[0].visible,false);
assert.equal(ui.wedges[1].material.opacity,.45);
assert.equal(ui.wedges[0].material.opacity,.09);
assert.equal(diag().currentOption,'st-income');
assert.ok(diag().costReads>=2);
s.resources.u=120;
ctx.se204WheelShow('build');
assert.equal(ui.statusKey,'60 GOLD','price from native config, resources now enough');
assert.equal(ui.icons[1].material.opacity,1);
assert.equal(nativeRootCalls,1,'reopening wheel reuses existing meshes');
assert.equal(canvasCreated,4,'no additional icon textures on reopening');
assert.equal(diag().decoratedWheels,1);
const previousMaterials=materialDisposed;
now+=110;ctx.se204WheelStep({selected:2});
assert.equal(ui.statusKey,'100 GOLD');
assert.equal(diag().currentOption,'st-fort');
assert.ok(diag().cheapEffectFrames>=2);
assert.equal(materialDisposed,previousMaterials,'no per-frame GPU object disposal');
const reusedPoints=ui.glints.geometry;
now+=110;ctx.se204WheelStep({selected:0});
assert.strictEqual(ui.glints.geometry,reusedPoints,'fixed glint geometry reused');
ctx.se204WheelShow('skill');
assert.equal(nativeRootCalls,2);
assert.equal(diag().decoratedWheels,2);
assert.equal(diag().wheelSegments,7,'three more radial wedges');
assert.equal(diag().newIconTextures,6,
 'Mirror and Totem new, Cancel and None share one icon');
assert.equal(canvasCreated,6);
const abilities=ctx.se204.wheel,skillUI=abilities.root.userData.se209Decor;
assert.equal(skillUI.statusKey,'AVAILABLE');
ctx.se204WheelStep({selected:1});
assert.equal(skillUI.statusKey,'RULE LOCKED');
assert.equal(skillUI.icons[1].material.opacity,.28);
s.rules.totems=true;ctx.se204WheelShow('skill');
assert.equal(skillUI.statusKey,'SELECT HOUSE');
ctx.stUi.buildingId='farm-23';
ctx.se204WheelShow('skill');
assert.equal(skillUI.statusKey,'AVAILABLE','ability selectable; no fake cooldown value');
assert.equal(skillUI.icons[1].material.opacity,1);
assert.equal(diag().skillAvailabilityChecks>0,true);
assert.equal(diag().currentOption,'totem');
assert.equal(ctx.stUi.rotation,1,'visual wheel never changes building orientation');
assert.equal(commandCalls,0,'visual only; native build and skills are untouched');
assert.equal(diag().gameplayBuildButton,'A hold select / tap build');
assert.equal(diag().gameplaySkillButton,'X hold select / tap skill');
const textures=[...art.icons.values()];
assert.equal(textures.length,6);
const countMeshes=geometryDisposed;
ctx.se204WheelDispose();
assert.equal(nativeDisposes,1);
assert.equal(diag().cachedIconTextures,0);
assert.equal(textureDisposed,6,'icon textures released when XR quick wheels disposed');
assert.ok(textures.every(t=>t.disposed));
assert.ok(geometryDisposed>countMeshes);
assert.ok(materialDisposed>previousMaterials);
assert.equal(ctx.se204.wheels.size,0);
ctx.se204WheelShow('build');
assert.equal(diag().cachedIconTextures,4,'new XR session lazily rebuilds icons');
assert.equal(canvasCreated,10);
ctx.se204WheelDispose();
assert.equal(diag().cachedIconTextures,0);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_209_quest_radial_icons_feedback.py'),'utf8');
assert.ok(patch.includes('V11_209_SHEEP_RADIAL_ICONS_FEEDBACK'));
assert.ok(!patch.includes('stUi.rotation='),'radial art may not rotate gameplay houses');
console.log(JSON.stringify({pass:true,checks:54,cachedIcons:diag().newIconTextures,
 disposedIcons:diag().disposedIcons,segmentedSlots:diag().wheelSegments,
 wheelBuilds:diag().decoratedWheels,selectionUpdates:diag().selectionUpdates,
 effectFrames:diag().cheapEffectFrames}));
