#!/usr/bin/env node
// Exercise the shipped spatial UI with real Three.js intersections. Canvas is
// only a label surface here; button geometry, animation and disposal are real.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!process.argv[2])throw Error('Usage: node tests/model_vr_ui_v11_360.mjs /path/to/three-0.169.0.mjs');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));assert.equal(THREE.REVISION,'169');
const source=fs.readFileSync(path.join(ROOT,'runtime/model_studio_vr_ui_v11_360.js'),'utf8');

function fixture(){
 let time=0,timerId=0;const timers=new Map(),resources=new Set(),disposals=new Map(),constructors=new Map(),canvases=[];
 const runtimeThree=new Proxy(THREE,{get(target,key){
  const value=target[key];if(typeof value!=='function'||!/(?:Geometry|Material|Texture)$/.test(String(key)))return value;
  if(!constructors.has(key))constructors.set(key,new Proxy(value,{construct(ctor,args,newTarget){
   const object=Reflect.construct(ctor,args,newTarget);resources.add(object);disposals.set(object,0);
   object.addEventListener('dispose',()=>disposals.set(object,disposals.get(object)+1));return object;
  }}));return constructors.get(key);
 }});
 const document={createElement(tag){
  assert.equal(tag,'canvas');const canvas={width:0,height:0};
  const raw={font:'10px sans-serif',globalAlpha:1,measureText(text){const px=Number(/([\d.]+)px/.exec(this.font)?.[1]||10);return {width:String(text).length*px*.54};},
   createLinearGradient(){return {addColorStop(){}};},createRadialGradient(){return {addColorStop(){}};},
   getImageData(){return {data:new Uint8ClampedArray(4)};}};
  const context=new Proxy(raw,{get(object,key){if(key in object)return object[key];if(/^create.*Gradient$/.test(String(key)))return ()=>({addColorStop(){}});return ()=>{};},set(object,key,value){object[key]=value;return true;}});
  canvas.getContext=type=>{assert.equal(type,'2d');return context;};canvases.push(canvas);return canvas;
 }};
 const sandbox=vm.createContext({document,window:{devicePixelRatio:1},performance:{now:()=>time},console,
  setTimeout(callback,delay=0){const id=++timerId;timers.set(id,{callback,at:time+delay});return id;},
  clearTimeout(id){timers.delete(id);}});
 vm.runInContext(source+'\nthis.createUI=se340CreateModelVRUI;',sandbox);
 const actions=new Proxy({},{get:()=>true});const ui=sandbox.createUI({THREE:runtimeThree,actions});
 function frame(dt=1/90,options={}){
  time+=dt*1000;for(const [id,timer] of [...timers])if(timer.at<=time){timers.delete(id);timer.callback();}
  ui.tick(dt,{visible:ui.root.visible,reducedMotion:false,...options});ui.root.updateWorldMatrix(true,true);
 }
 function settle(){for(let i=0;i<180;i++)frame();}
 const targets=()=>ui.targets.filter(t=>t.visible!==false&&t.userData.se340Action);
 const byAction=id=>targets().find(t=>t.userData.se340Action===id);
 function rayAt(mesh){
  ui.root.updateWorldMatrix(true,true);const point=mesh.getWorldPosition(new THREE.Vector3());
  const normal=new THREE.Vector3(0,0,1).applyQuaternion(mesh.getWorldQuaternion(new THREE.Quaternion())).normalize();
  return new THREE.Raycaster(point.clone().addScaledVector(normal,.4),normal.negate());
 }
 function hit(id){const mesh=typeof id==='string'?byAction(id):id;assert.ok(mesh,'missing target '+id);return ui.hitTest(rayAt(mesh));}
 function snapshot(){ui.root.updateWorldMatrix(true,true);const values=[];ui.root.traverse(object=>{
  values.push([object.uuid,object.position.toArray(),object.quaternion.toArray(),object.scale.toArray(),object.visible,
   ...(Array.isArray(object.material)?object.material:object.material?[object.material]:[]).map(m=>m.opacity)]);
 });return values;}
 return {ui,frame,settle,targets,byAction,hit,rayAt,snapshot,resources,disposals,timers,canvases};
}
let groups=0;
{
 const f=fixture(),{ui}=f;assert.equal(typeof ui.tick,'function');f.settle();
 assert.equal(ui.inspect().page,'tools');assert.ok(f.byAction('sculpt'));assert.ok(f.byAction('two-hand'));
 ui.update({canUndo:false,canRedo:false});f.settle();
 const undo=f.hit('undo');assert.equal(undo?.object.userData.se340Action,'undo','Disabled UI must block the model behind it');
 assert.equal(ui.press(undo),false);assert.equal(ui.press('redo'),false);
 ui.update({canUndo:true,canRedo:true});f.settle();assert.equal(ui.press(f.hit('undo')),true);
 const background=ui.targets.find(t=>t.userData.se340Block);assert.ok(background);
 const ray=f.rayAt(background);const hit=ui.hitTest(ray);assert.ok(hit,'Panel gaps must hit an opaque input surface');
 assert.ok(hit.object.userData.se340Block||hit.object.userData.se340Action);
 ui.dispose();groups++;
}
{
 const f=fixture(),{ui}=f;
 const required={tools:['inspect','move','two-hand','sculpt','draw'],mesh:['selection-clear','precision','snap'],
  studio:['mesh','sculpt','draw','views','aim','help'],sculpt:['sculpt-push','sculpt-smooth','sculpt-flatten','sculpt-inflate','sculpt-pinch','sculpt-translate'],
  draw:['draw','extrude','lasso','lasso-clear'],views:['display-textured','display-solid','display-wireframe','display-xray','display-normals','cameras'],
  cameras:['view-front','view-back','view-left','view-right','view-top','view-bottom','view-iso'],aim:['aim-hand','aim-reset-all']};
 for(const [page,ids] of Object.entries(required)){
  ui.update({page,helpVisible:false});f.settle();assert.equal(ui.inspect().page,page);
  for(const id of [...ids,'exit']){const hit=f.hit(id);assert.equal(hit?.object.userData.se340Action,id,`${page}: ${id} must be ray reachable`);}
  for(const target of f.targets().filter(t=>t.userData.se360Role==='tool')){
   assert.equal(f.hit(target)?.object,target,`${page}: tool card ${target.userData.se340Action} is covered by another control`);
  }
 }
 ui.update({page:'draw',drawPointCount:0});f.settle();assert.equal(ui.press('draw-finish'),false);
 ui.update({drawPointCount:5});f.settle();assert.equal(ui.press('draw-finish'),true);
 ui.update({page:'sculpt',mode:'sculpt',sculptTool:'flatten',selectedRegionId:'mask-1'});f.settle();
 assert.equal(f.byAction('sculpt-flatten').userData.se340Selected,true,'The active brush needs a visible selected state');
 assert.equal(f.byAction('sculpt-push').userData.se340Selected,false);
 ui.update({page:'views',displayMode:'wireframe'});f.settle();
 assert.equal(f.byAction('display-wireframe').userData.se340Selected,true);assert.equal(f.byAction('display-textured').userData.se340Selected,false);
 for(const page of Object.keys(required)){
  ui.update({page,helpVisible:true});f.settle();assert.ok(ui.inspect().helpVisible);
  assert.equal(ui.press(f.hit('help')),true,`${page}: Guide must have a Back action`);assert.equal(ui.press(f.hit('exit')),true);
 }
 ui.dispose();groups++;
}
{
 const f=fixture(),{ui}=f;ui.root.position.set(.2,1.4,-1);ui.root.rotation.set(.08,.28,-.03);
 for(const [kind,ids] of Object.entries({tools:['inspect','move','rotate','scale','sculpt','draw','two-hand'],studio:['mesh','sculpt','draw','views','aim','help'],brush:['sculpt-push','sculpt-smooth','sculpt-flatten','sculpt-inflate','sculpt-pinch','sculpt-translate']})){
  assert.equal(ui.openWheel(kind),true);f.settle();assert.equal(ui.inspect().wheel,kind);
  for(const id of ids){const hit=f.hit(id);assert.equal(hit?.object.userData.se340Action,id,`${kind}: ${id} is occluded by another wheel sector`);}
  const item=f.hit(ids[2]);ui.hover(item);assert.equal(ui.releaseWheel(item),ids[2]);assert.equal(ui.inspect().wheel,null);
  ui.openWheel(kind);f.settle();assert.equal(ui.releaseWheel(null),null,'Releasing off a sector must not choose the previous hover');
 }
 ui.openWheel('tools');f.settle();ui.closeWheel();f.settle();assert.equal(ui.inspect().wheel,null);
 ui.dispose();groups++;
}
{
 const f=fixture(),{ui}=f;f.settle();const paint=ui.inspect().paintCount,before=f.snapshot();
 for(let i=0;i<360;i++){ui.update();f.frame();}
 assert.equal(ui.inspect().paintCount,paint,'Idle frames must reuse canvas textures');assert.deepEqual(f.snapshot(),before,'A settled menu must stop moving');
 const move=f.byAction('move'),start=move.getWorldPosition(new THREE.Vector3());ui.hover(f.hit(move));
 for(let i=0;i<8;i++)f.frame();assert.notDeepEqual(f.snapshot(),before,'Hover must produce spatial feedback');
 assert.equal(f.hit('move')?.object.userData.se340Action,'move','Animated hover retains a ray target');
 ui.press('move');for(let i=0;i<10;i++)f.frame();ui.hover(null);f.settle();
 assert.ok(move.getWorldPosition(new THREE.Vector3()).distanceTo(start)<1e-6,'Hover and press must return to their resting layout');
 const settledPaint=ui.inspect().paintCount;for(let i=0;i<180;i++)f.frame();assert.equal(ui.inspect().paintCount,settledPaint,'Effects must animate transforms/materials without continuously repainting text');
 ui.dispose();groups++;
}
{
 const a=fixture(),b=fixture();a.settle();b.settle();a.ui.hover(a.hit('move'));b.ui.hover(b.hit('move'));
 for(let i=0;i<45;i++)a.frame(1/90);for(let i=0;i<30;i++)b.frame(1/60);
 const targetA=a.byAction('move'),targetB=b.byAction('move');
 assert.ok(targetA.getWorldPosition(new THREE.Vector3()).distanceTo(targetB.getWorldPosition(new THREE.Vector3()))<.00015,'Hover motion must converge consistently at 60 and 90 Hz');
 assert.ok(targetA.scale.distanceTo(targetB.scale)<.001,'Hover scale must be frame-rate independent');
 a.ui.dispose();b.ui.dispose();groups++;
}
{
 const f=fixture(),{ui}=f;f.settle();const sculpt=f.targets().filter(t=>t.userData.se340Action==='sculpt');
 assert.equal(sculpt.length,2,'The persistent Sculpt tab and Sculpt tool should both be available');
 const nav=sculpt.find(t=>t.userData.se360Role==='nav'),tool=sculpt.find(t=>t.userData.se360Role==='tool');assert.ok(nav&&tool);
 const navBefore=nav.getWorldPosition(new THREE.Vector3()),toolBefore=tool.getWorldPosition(new THREE.Vector3());ui.hover(f.hit(tool));for(let i=0;i<12;i++)f.frame();
 assert.ok(tool.getWorldPosition(new THREE.Vector3()).distanceTo(toolBefore)>.00001,'The actual hovered card should lift');
 assert.ok(nav.getWorldPosition(new THREE.Vector3()).distanceTo(navBefore)<1e-8,'A duplicate navigation action must not animate as if hovered');
 ui.hover(f.hit(nav));f.settle();assert.ok(tool.getWorldPosition(new THREE.Vector3()).distanceTo(toolBefore)<1e-6);assert.ok(nav.getWorldPosition(new THREE.Vector3()).distanceTo(navBefore)>.00001);
 ui.dispose();groups++;
}
{
 const f=fixture(),{ui}=f;f.settle();ui.hover(f.hit('move'));f.frame(1/90,{reducedMotion:true});
 const reduced=f.snapshot();for(let i=0;i<90;i++)f.frame(1/90,{reducedMotion:true});assert.deepEqual(f.snapshot(),reduced,'Reduced motion must settle immediately');
 ui.root.visible=false;f.frame(1/90,{visible:false});const hidden=f.snapshot();assert.equal(ui.hitTest(f.rayAt(f.byAction('move'))),null,'Hidden menus must not accept rays');
 for(let i=0;i<180;i++)f.frame(1/90,{visible:false});assert.deepEqual(f.snapshot(),hidden,'Hidden menus must not keep animating');
 ui.root.visible=true;f.settle();assert.equal(f.hit('move')?.object.userData.se340Action,'move');
 ui.dispose();groups++;
}
{
 const f=fixture(),{ui}=f;f.settle();const count=f.resources.size;
 for(let i=0;i<80;i++){
  ui.update({page:['tools','mesh','studio','sculpt','draw','views','cameras','aim'][i%8],brushRadius:.04+i*.001,selectedCount:i%4});
  ui.openWheel(['tools','studio','brush'][i%3]);f.frame();ui.closeWheel();f.frame();
 }
 f.settle();assert.equal(f.resources.size,count,'Page/wheel changes must reuse bounded GPU resources');
 ui.hover(f.hit('exit'));ui.press('exit');ui.dispose();ui.dispose();
 assert.equal(ui.inspect().disposed,true);assert.equal(ui.targets.length,0);assert.equal(f.timers.size,0,'Disposed menus cannot leave press timers behind');
 for(const [resource,n] of f.disposals)assert.equal(n,1,`${resource.type} must dispose exactly once`);
 assert.equal(ui.hitTest(new THREE.Raycaster()),null);assert.equal(ui.press('move'),false);
 const disposedPaint=ui.inspect().paintCount;ui.update({page:'tools'});ui.tick(1/60);assert.equal(ui.inspect().paintCount,disposedPaint);
 groups++;
}
console.log('MODEL_VR_UI_V11_360_PASS',JSON.stringify({groups,three:THREE.REVISION,actualRaycasts:true,animation:'settled and frame-rate independent',resources:'bounded and disposed exactly once'}));
