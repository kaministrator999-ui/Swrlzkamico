// §E v11.206 — visual-only meadow/fog Quest performance and state ownership.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
class V{
 constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z})}
 clone(){return new V(this.x,this.y,this.z)}
 set(x,y,z){Object.assign(this,{x,y,z});return this}
}
let now=1000,active=true,overlay=false,frames=0,stops=0,cleanups=0;
let canvasCount=0,ctxFills=0,ctxArcs=0,gpuCreates=0,gpuDisposals=0;
const ctx2d={
 clearRect(){},createRadialGradient:()=>({addColorStop(){}}),
 beginPath(){},arc(){ctxArcs++},fill(){ctxFills++},fillRect(){ctxFills++},
 save(){},restore(){},setLineDash(){},stroke(){}
};
class Canvas{
 constructor(){this.width=this.height=0}
 getContext(type){assert.equal(type,'2d');return ctx2d}
}
class Texture{
 constructor(c){this.image=c;this.disposed=false;gpuCreates++;
 this.minFilter='old-nearest';this.magFilter='old-nearest';this.generateMipmaps=false;
 this.anisotropy=1}
 dispose(){assert.equal(this.disposed,false,'no double texture disposal');
 this.disposed=true;gpuDisposals++}
}
class Geometry{
 constructor(w,h){this.w=w;this.h=h;this.disposed=false;gpuCreates++}
 dispose(){assert.equal(this.disposed,false);this.disposed=true;gpuDisposals++}
}
class Material{
 constructor(opts){Object.assign(this,opts);this.disposed=false;gpuCreates++}
 dispose(){assert.equal(this.disposed,false);this.disposed=true;gpuDisposals++}
}
class Mesh{
 constructor(g,m){this.geometry=g;this.material=m;this.rotation={x:0};
 this.position=new V();this.userData={};this.renderOrder=0;this.name='';this.visible=true}
}
const s={
 simulate:false,rules:{bounds:64,role:'sheep',fogMode:'team'},
 navVersion:9,units:[{id:'a',kind:'sheep'}],buildings:[{id:'b',kind:'st-farm'}],
 fog:{
  material:{opacity:.98,transparent:true,depthWrite:false,depthTest:true,
    polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-4},
  mesh:{position:{y:.17},renderOrder:3},
  texture:{minFilter:'old-nearest',magFilter:'old-nearest',generateMipmaps:true},
  visible:new Uint8Array([1,0,1,0]),explored:new Uint8Array([1,1,1,0]),feather:1.5
 }
};
const native={...s.fog.material,fogY:s.fog.mesh.position.y,order:s.fog.mesh.renderOrder,
 visible:s.fog.visible,explored:s.fog.explored};
const beforeActors=[{userData:{actorType:'st-meadow'},
 getWorldPosition:()=>new V(0,0,0),updateMatrixWorld(){}}];
const scene={
 children:[],add(o){this.children.push(o)},
 remove(o){this.children=this.children.filter(x=>x!==o)}
};
const sandbox={
 console,Math,THREE:{
  Vector3:V,CanvasTexture:Texture,PlaneGeometry:Geometry,MeshBasicMaterial:Material,Mesh,
  SRGBColorSpace:'srgb',LinearFilter:'linear',LinearMipmapLinearFilter:'mips',DoubleSide:2
 },
 document:{createElement(name){assert.equal(name,'canvas');canvasCount++;return new Canvas()}},
 scene,actors:beforeActors,stSession:s,
 se195:{visible:false,photo:false},se205OverlayActive:()=>overlay,
 se193XRGameActive:()=>active,
 performance:{now:()=>now},
 stStop:()=>{stops++;sandbox.stSession=null;return 'stopped'},
 se193XRCleanup:()=>{cleanups++;return 'exited'},
 se193XRFrame:()=>{frames++;return 'frame'},
 window:{}
};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','runtime',
 'sheep_quest_meadow_fog_polish_v11_206.js'),'utf8'),sandbox);
const diag=()=>sandbox.window.SWYRL_ENGINE_SHEEP_MEADOW_FOG_206.diagnose();
assert.equal(diag().ready,false);
assert.equal(diag().sourceDecorOnly,true);
assert.equal(scene.children.length,0);
assert.equal(sandbox.se193XRFrame(),'frame');
assert.equal(diag().fogVisualSetups,1);
assert.equal(diag().fogOpacity,.84);
assert.equal(s.fog.feather,2.15);
assert.equal(s.fog.mesh.position.y,.175);
assert.equal(s.fog.texture.minFilter,'linear');
assert.strictEqual(s.fog.visible,native.visible,'native fog-visible mask identity unchanged');
assert.strictEqual(s.fog.explored,native.explored,'native explored mask identity unchanged');
assert.deepEqual(Array.from(s.fog.visible),[1,0,1,0]);
assert.equal(s.navVersion,9,'no collisions or routing invalidated');
assert.equal(beforeActors.length,1,'no editor actor or scene authored');
assert.equal(canvasCount,1);
assert.ok(diag().biomeBlooms>0);
let previousStage=diag().paintStages;
sandbox.se195.visible=true;now+=16;sandbox.se193XRFrame();
assert.equal(diag().paintStages,previousStage,'wrist menu pauses cosmetic painter');
sandbox.se195.visible=false;overlay=true;now+=16;sandbox.se193XRFrame();
assert.equal(diag().paintStages,previousStage,'Quest native overlay pauses cosmetic painter');
overlay=false;sandbox.se195.photo=true;now+=16;sandbox.se193XRFrame();
assert.equal(diag().paintStages,previousStage,'capture/photo pauses cosmetic painter');
sandbox.se195.photo=false;
for(let i=0;i<15;i++){now+=16;sandbox.se193XRFrame()}
assert.equal(diag().ready,true);
assert.equal(diag().textureUploads,1,'one upload per match');
assert.equal(diag().decorCreated,1);
assert.equal(diag().geometryAdded,1,'one new ground mesh/draw call');
assert.ok(diag().biomeBlooms>850,'many tiny florets in single texture');
assert.ok(diag().roadSitesAvoided>250,'paths and central sanctuary avoid painted flowers');
assert.ok(ctxFills>1000&&ctxArcs>=29,'procedural biome and sanctuary flourish built');
assert.equal(scene.children.length,1);
const mesh=scene.children[0];
assert.equal(mesh.userData.se206DecorOnly,true);
assert.equal(mesh.userData.sheepTagPreview,true);
assert.equal(mesh.geometry.w,128);
assert.equal(mesh.geometry.h,128);
assert.equal(mesh.rotation.x,-Math.PI/2);
assert.equal(mesh.renderOrder,2);
assert.ok(mesh.position.y>0&&mesh.position.y<s.fog.mesh.position.y,
 'decoration is below original fog so it cannot reveal hidden world');
assert.equal(mesh.material.depthWrite,false,'ground decal never hides geometry depth');
assert.equal(mesh.material.opacity,.83);
assert.equal(mesh.material.map.generateMipmaps,true);
assert.equal(mesh.material.map.minFilter,'mips');
assert.equal(mesh.material.map.anisotropy,2);
assert.ok(typeof mesh.raycast==='function');
assert.equal(mesh.raycast(),undefined,'decor cannot receive pointer hit');
assert.equal(s.navVersion,9);
assert.equal(s.units.length,1);
assert.equal(s.buildings.length,1);
const prev=diag().textureUploads;
for(let i=0;i<24;i++){now+=16;sandbox.se193XRFrame();}
assert.equal(diag().textureUploads,prev,'no gameplay-frame canvas reupload');
assert.strictEqual(scene.children[0],mesh);
assert.ok(diag().modalFramesSkipped>=3);
assert.equal(diag().fogPaintAuthority,'unchanged');
// Restore original visual material when leaving immersive VR while a game lives.
const tex=mesh.material.map;
active=false;now+=16;sandbox.se193XRFrame();
assert.equal(scene.children.length,0,'dispose VR-only meadow on headset exit');
assert.equal(diag().ready,false);
assert.equal(tex.disposed,true,'texture GPU allocation released');
assert.equal(mesh.geometry.disposed,true);
assert.equal(mesh.material.disposed,true);
assert.equal(s.fog.material.opacity,native.opacity,'original 2D fog alpha restored');
assert.equal(s.fog.material.polygonOffsetFactor,native.polygonOffsetFactor);
assert.equal(s.fog.material.polygonOffsetUnits,native.polygonOffsetUnits);
assert.equal(s.fog.mesh.position.y,native.fogY);
assert.equal(s.fog.mesh.renderOrder,native.order);
assert.equal(s.fog.texture.minFilter,'old-nearest');
assert.equal(s.fog.texture.magFilter,'old-nearest');
assert.equal(s.fog.texture.generateMipmaps,true);
assert.equal(s.fog.feather,1.5);
assert.strictEqual(s.fog.visible,native.visible);
assert.ok(gpuDisposals>=3);
active=true;now+=16;sandbox.se193XRFrame();
assert.equal(diag().active,true,'new immersive session can rebuild overlay');
assert.equal(canvasCount,2);
assert.equal(sandbox.stStop(),'stopped');
assert.equal(stops,1);
assert.equal(diag().active,false);
assert.equal(diag().ready,false);
assert.equal(sandbox.se193XRCleanup(),'exited');
assert.equal(cleanups,1);
const patch=fs.readFileSync(path.join(__dirname,'..','patches',
 'v11_206_sheep_quest_meadow_fog_polish.py'),'utf8');
assert.ok(patch.includes("V11_206_SHEEP_QUEST_MEADOW_FOG_ART"));
assert.ok(patch.includes("runtime/sheep_quest_meadow_fog_polish_v11_206.js"));
console.log(JSON.stringify({pass:true,checks:51,flowers:diag().biomeBlooms,
 avoidedRoads:diag().roadSitesAvoided,textureUploads:diag().textureUploads,
 fogSetups:diag().fogVisualSetups,textureDisposals:gpuDisposals,
 allOldControlsUntouched:true}));
