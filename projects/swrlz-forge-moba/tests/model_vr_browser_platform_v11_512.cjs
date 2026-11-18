'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const ROOT=path.resolve(__dirname,'../runtime');
const browser=fs.readFileSync(path.join(ROOT,'model_vr_browser_pick_v11_512.js'),'utf8');
const platform=fs.readFileSync(path.join(ROOT,'model_display_platform_v11_512.js'),'utf8');
function fixture(ua='OculusBrowser/42',immersive=false){
 const mesh={isMesh:true,visible:true,userData:{atelierId:'sphere'}};
 const helper={isMesh:true,visible:true,userData:{atelierHelper:true}};
 const stage={style:{position:''},children:[],append(o){this.children.push(o);}};
 const rect={left:0,top:0,right:500,bottom:500,width:500,height:500};
 const mouse={x:0,y:0,set(x,y){this.x=x;this.y=y;}};
 const ctx={console,navigator:{userAgent:ua},renderer:{xr:{isPresenting:immersive},
  domElement:{getBoundingClientRect:()=>rect}},
  modelRoot:{children:[helper,mesh],updateWorldMatrix(){}},
  mouse,camera:{updateMatrixWorld(){}},
  raycaster:{setFromCamera(){},intersectObjects:meshes=>meshes.includes(mesh)&&Math.abs(mouse.x)<.02&&Math.abs(mouse.y)<.02?[{object:mesh}]:[]},
  partById:id=>id==='sphere'?{id}:null,
  select(id){this.selection=id;},selection:null,
  pressed:null,
  pointerUp(e){this.pressed=null;this.selection=null;},
  getComputedStyle:()=>({position:'static'}),
  document:{createElement:()=>({style:{},attrs:{},listeners:{},setAttribute(key,value){this.attrs[key]=value;},
   addEventListener(type,callback){this.listeners[type]=callback;},remove(){this.removed=true;}})}
 };
 ctx.window=ctx;
 const context=vm.createContext(ctx);
 vm.runInContext(browser,context);vm.runInContext(platform,context);
 return {ctx,mesh,stage};
}
let tests=0;
{
 const {ctx}=fixture();ctx.pressed={x:250,y:250,moved:false};
 ctx.pointerUp({clientX:257,clientY:250,pointerType:'mouse'});
 assert.equal(ctx.selection,'sphere','Quest release-jitter should select the intended mesh');tests++;
}
{
 const {ctx}=fixture('Mozilla/5.0 Chrome');ctx.pressed={x:250,y:250,moved:false};
 ctx.pointerUp({clientX:257,clientY:250,pointerType:'mouse'});
 assert.equal(ctx.selection,null,'desktop must retain native click behavior');tests++;
}
{
 const {ctx}=fixture('OculusBrowser/42',true);ctx.pressed={x:250,y:250,moved:false};
 ctx.pointerUp({clientX:257,clientY:250,pointerType:'mouse'});
 assert.equal(ctx.selection,null,'immersive VR must not take 2D ray fallback');tests++;
}
{
 const {ctx}=fixture();ctx.pressed={x:250,y:250,moved:true};
 ctx.pointerUp({clientX:257,clientY:250,pointerType:'mouse'});
 assert.equal(ctx.selection,null,'real orbit drags must not trigger selection');tests++;
}
{
 const {ctx}=fixture();ctx.atelierMeshDrag={axis:'x'};ctx.pressed={x:250,y:250,moved:false};
 ctx.pointerUp({clientX:257,clientY:250,pointerType:'mouse'});
 assert.equal(ctx.selection,null,'gizmo drags retain ownership');tests++;
}
{
 const {ctx,stage}=fixture(),floor={visible:true};
 ctx.se512PlatformBrowserAttach(floor,stage);
 assert.equal(stage.children.length,1);
 const button=stage.children[0];assert.equal(button.textContent,'Hide platform');
 button.listeners.click();assert.equal(floor.visible,false);
 assert.equal(button.textContent,'Show platform');
 assert.equal(ctx.se512BrowserFloorVisible,false);
 ctx.se512PlatformBrowserDetach();assert.equal(button.removed,true);
 assert.equal(stage.style.position,'');tests++;
}
console.log('SE512 Browser 2D + platform: '+tests+' scenario groups passed');
