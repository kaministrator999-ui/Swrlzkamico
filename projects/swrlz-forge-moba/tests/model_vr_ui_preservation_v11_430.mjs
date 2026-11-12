// Actual Three.js surfaces/rays exercise the combined v425 + v430 console.
// Canvas is a controlled label adapter; native model geometry is not mocked
// or edited by this UI-only suite.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath,pathToFileURL} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
assert.ok(process.argv[2],'Pass an existing Three r169 ES module');
const THREE=await import(pathToFileURL(path.resolve(process.argv[2])));
assert.equal(THREE.REVISION,'169');
const source=fs.readFileSync(path.join(ROOT,'runtime/model_studio_vr_ui_v11_430.js'),'utf8');
const teaching=fs.readFileSync(path.join(ROOT,'runtime/model_studio_teaching_v11_430.js'),'utf8');
function fixture(){
 const resources=new Set(),disposals=new Map(),constructors=new Map(),canvases=[];
 const runtimeThree=new Proxy(THREE,{get(target,key){
  const value=target[key];if(typeof value!=='function'||!/(?:Geometry|Material|Texture)$/.test(String(key)))return value;
  if(!constructors.has(key))constructors.set(key,new Proxy(value,{construct(ctor,args,newTarget){
   const object=Reflect.construct(ctor,args,newTarget);resources.add(object);disposals.set(object,0);
   object.addEventListener('dispose',()=>disposals.set(object,disposals.get(object)+1));return object;
  }}));return constructors.get(key);
 }});
 const document={createElement(tag){
  assert.equal(tag,'canvas');const canvas={width:0,height:0,texts:[],strokes:[]};
  const raw={font:'10px sans-serif',globalAlpha:1,clearRect(){canvas.texts=[];},fillText(text){canvas.texts.push(String(text));},
   measureText(text){const px=Number(/([\d.]+)px/.exec(this.font)?.[1]||10);return {width:String(text).length*px*.54};},
   stroke(){canvas.strokes.push(this.strokeStyle);},createLinearGradient(){return {addColorStop(){}};},
   createRadialGradient(){return {addColorStop(){}};}};
  const context=new Proxy(raw,{get(object,key){return key in object?object[key]:()=>{};},set(object,key,value){object[key]=value;return true;}});
  canvas.getContext=type=>{assert.equal(type,'2d');return context;};canvases.push(canvas);return canvas;
 }};
 const sandbox=vm.createContext({document,window:{devicePixelRatio:1},console});
 vm.runInContext(teaching+'\n'+source+'\nthis.createUI=se340CreateModelVRUI;this.route=(state,id)=>{'+
  source.slice(source.indexOf('function iconType(id){'),source.indexOf('function icon(c,type'))+'return iconType(id);};',sandbox);
 const ui=sandbox.createUI({THREE:runtimeThree});
 function settle(options={}){for(let i=0;i<150;i++)ui.tick(1/90,{visible:true,reducedMotion:false,...options});ui.root.updateWorldMatrix(true,true);}
 const targets=()=>ui.targets.filter(t=>t.visible!==false&&t.userData.se340Action);
 const item=id=>targets().find(t=>t.userData.se340Action===id);
 function hit(id){
  const target=typeof id==='string'?item(id):id;assert.ok(target,'Missing target '+id);
  ui.root.updateWorldMatrix(true,true);const point=target.getWorldPosition(new THREE.Vector3());
  const normal=new THREE.Vector3(0,0,1).applyQuaternion(target.getWorldQuaternion(new THREE.Quaternion())).normalize();
  return ui.hitTest(new THREE.Raycaster(point.clone().addScaledVector(normal,.4),normal.negate()));
 }
 return {ui,settle,targets,item,hit,canvases,resources,disposals,sandbox};
}
let groups=0;
{
 const f=fixture();f.settle();assert.deepEqual(f.ui.root.scale.toArray(),[1.16,1.16,1.16]);
 for(const target of f.targets())if(target.material?.map)assert.equal(target.material.map.anisotropy,8,'Preserve v421 label filtering');
 const navigation=f.targets().filter(t=>t.userData.se360Role==='nav');assert.equal(navigation.length,7);
 assert.ok(navigation.some(t=>t.userData.se340Action==='objects'),'Preserve Object Index navigation');
 assert.equal(typeof f.ui.drawGuideIcon,'function');assert.equal(typeof f.ui.highlightTutorialAction,'function');f.ui.dispose();groups++;
}
{
 const f=fixture();const expected={objects:'layers','index-add':'multi','index-prev':'left-arrow','index-next':'right-arrow',
  'index-part-0':'cube',selector:'select','selector-sweep':'sweep','selector-lasso-front':'lasso-front',
  'selector-lasso-through':'lasso-through','save-local':'save','save-account':'cloud','clone-project':'clone',
  'aim-yaw-plus':'yaw','view-front':'view-front','view-top':'view-top','manual-inset':'inset',
  'manual-extrude':'extrude','manual-solidify':'solidify','manual-apply':'confirm'};
 for(const [id,want]of Object.entries(expected))assert.equal(f.sandbox.route({accessoryParams:{}},id),want,id);
 assert.ok(!source.includes("fillText('?',0,1)"));assert.ok(source.includes("if(/-(?:plus|minus)$/.test(item.id))"));
 f.ui.dispose();groups++;
}
{
 const f=fixture(),entries=Array.from({length:9},(_,i)=>({id:'part-'+i,name:i<2?'Same name':'Object '+i}));
 f.ui.update({page:'objects',indexEntries:entries,indexSelected:['part-1'],indexTotal:23,indexPage:0,indexMulti:true});f.settle();
 assert.equal(f.ui.inspect().indexTotal,23);assert.equal(f.ui.inspect().indexMulti,true);
 for(let i=0;i<9;i++)assert.equal(f.hit('index-part-'+i)?.object.userData.se340Action,'index-part-'+i);
 assert.equal(f.item('index-part-1').userData.se340Selected,true);assert.equal(f.item('index-part-0').userData.se340Selected,false);
 assert.equal(f.ui.press('index-prev'),false);assert.equal(f.ui.press('index-next'),true);
 f.ui.update({indexPage:2,indexEntries:[{id:'part-18',name:'Last name changed'}]});f.settle();
 assert.ok(f.item('index-part-18').material.map.image.texts.includes('Last name changed'));
 assert.equal(f.ui.press('index-next'),false);assert.equal(f.ui.press('index-prev'),true);f.ui.dispose();groups++;
}
{
 const f=fixture();f.ui.update({page:'create'});f.settle();
 const target=f.item('create-box'),canvas=target.material.map.image;canvas.strokes=[];
 f.ui.highlightTutorialAction('create-box');f.settle();assert.ok(canvas.strokes.includes('#e7ff74'),'Native Satchel Show Me highlight remains visible');
 const guideContext=f.canvases[0].getContext('2d');f.ui.drawGuideIcon(guideContext,'save-account',20,20,30,'#ffffff');
 f.ui.highlightTutorialAction(null);f.ui.dispose();groups++;
}
{
 const f=fixture();f.ui.update({page:'manual-mesh',manualActive:true,manualOperation:'inset',manualConvert:{available:true},
  manualAvailability:{inset:{available:false,reason:'Select faces first'}},manualSelection:{faceCount:0}});f.settle();
 for(const id of ['manual-convert','manual-pick','manual-learn','manual-inset','manual-extrude','manual-solidify','exit'])
  assert.equal(f.hit(id)?.object.userData.se340Action,id);
 f.ui.update({page:'manual-operation'});f.settle();assert.equal(f.ui.press('manual-preview'),false);
 f.ui.update({manualPreview:true,manualAvailability:{inset:{available:true}}});f.settle();
 assert.equal(f.ui.press('manual-preview'),true);assert.equal(f.ui.press('manual-apply'),true);assert.equal(f.ui.press('manual-cancel'),true);
 assert.equal(f.ui.press('manual-convert'),false);f.ui.dispose();groups++;
}
{
 const f=fixture();f.ui.update({page:'manual-operation',helpVisible:true,learningTool:'inset',manualActive:true});f.settle();
 assert.equal(f.ui.inspect().learningTool,'inset');assert.equal(f.hit('help')?.object.userData.se340Action,'help');
 const before=f.ui.inspect().paintCount;for(let i=0;i<20;i++)f.ui.tick(.05,{visible:true,reducedMotion:false});
 assert.ok(f.ui.inspect().paintCount>before,'Visible tool diagram animates through the existing tick');
 f.ui.tick(.05,{visible:true,reducedMotion:true});const reduced=f.ui.inspect().paintCount;
 for(let i=0;i<20;i++)f.ui.tick(.05,{visible:true,reducedMotion:true});assert.equal(f.ui.inspect().paintCount,reduced);
 f.ui.dispose();groups++;
}
{
 const f=fixture();f.settle();const allocated=f.resources.size;
 for(const page of ['objects','manual-mesh','manual-operation','accessory-body','sculpt','views','cameras','tools']){
  f.ui.update({page,helpVisible:false,indexEntries:[],indexTotal:0,manualActive:page.startsWith('manual')});f.settle();
  for(const target of f.targets().filter(t=>t.userData.se360Role==='tool'))assert.equal(f.hit(target)?.object,target,page+' actual ray reachability');
 }
 assert.equal(f.resources.size,allocated,'New and preserved pages reuse bounded surface resources');
 const paint=f.ui.inspect().paintCount;for(let i=0;i<90;i++){f.ui.update();f.ui.tick(1/90,{visible:true,reducedMotion:false});}
 assert.equal(f.ui.inspect().paintCount,paint,'Idle tool menu does not repaint labels');
 f.ui.dispose();f.ui.dispose();for(const n of f.disposals.values())assert.equal(n,1,'Owned resources dispose once');groups++;
}
console.log('MODEL_VR_UI_PRESERVATION_V11_430_PASS',JSON.stringify({groups,three:THREE.REVISION,
 preserved:['native icons','button references','tutorial highlight','Object Index','scaled filtered labels'],
 added:['manual face tools','shared teaching'],realRays:true,ownedResources:true}));
