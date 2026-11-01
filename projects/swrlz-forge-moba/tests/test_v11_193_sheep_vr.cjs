// Native-controller unit tests. No headset, second renderer or hosted deployment.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/engine_xr_sheep_capture_v11_193.js'),'utf8');
new vm.Script(source,{filename:'engine_xr_sheep_capture_v11_193.js'});
const calls=[];
class Vector3 {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
 clone(){return new Vector3(this.x,this.y,this.z);}
 addScaledVector(v,s){this.x+=v.x*s;this.y+=v.y*s;this.z+=v.z*s;return this;}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z;}
 normalize(){const n=Math.sqrt(this.lengthSq())||1;this.x/=n;this.y/=n;this.z/=n;return this;}
}
const context=vm.createContext({
 window:{},THREE:{Vector3},
 currentProject:{kind:'sheep-tag',name:'Sheep Tag'},
 st140Menu:{open:false},stSession:null,seLevels:{playingMenu:false},
 seLevelsCurrent:()=>({role:'menu'}),seLevelsOwns:()=>true,
 seLevelsTransition:()=>{calls.push('level-start');return true;},
 seLevelsStopMenu:()=>calls.push('menu-stop'),st140MenuStart:()=>calls.push('legacy-start'),
 st140MenuClose:()=>calls.push('legacy-close'),
 renderer:{xr:{isPresenting:true}},se181XR:{session:{},controllers:[]},
 stUi:{build:null,placement:null,follow:true},
 stUiChooseBuild:kind=>{context.stUi.build=kind;calls.push('choose:'+kind);},
 stUiPlacePreview:point=>{context.stUi.placement={ok:true,x:point.x,z:point.z};},
 stUiClearPreview:()=>calls.push('clear-preview'),
 stRefreshHUD:()=>{},stUiFeedback:()=>{},
 se192PanelsVisible:v=>calls.push('palette:'+v),
 stStatus:()=>({controlledId:'sheep-1',selectedId:'sheep-1',winner:null,units:[{id:'sheep-1',kind:'sheep',pos:[0,0,0]}],buildings:[]}),
 stUiCommand:(action,data)=>{calls.push(action+':'+JSON.stringify(data));return {ok:true};},
 se192Raycast:()=>({empty:true}),
 se192Ray:()=>null,
 document:{getElementById:()=>null},
 performance:{now:()=>1},Date,Math,Number,JSON,Map
});
vm.runInContext(source,context);
function evalExpr(expression){return vm.runInContext(expression,context);}
assert.equal(evalExpr('se193XRMenuActive()'),true,'authored menu level should activate native menu');
assert.equal(evalExpr('se193XRKind()'),'menu');
evalExpr("se193XRAction('start')");
assert(calls.includes('level-start'),'Start must use authored level transition, not the retired menu');
// No editor mutation while title is open.
assert.equal(evalExpr('se193XRGameActive()'),false);
context.stSession={simulate:false};
assert.equal(evalExpr('se193XRKind()'),'game');
assert.equal(evalExpr("se193XRGameButton({input:{handedness:'right'}},'a')"),true);
assert.equal(context.stUi.build,'st-farm');
assert.equal(evalExpr("se193XRGameButton({input:{handedness:'right'}},'a')"),true);
assert.equal(context.stUi.build,'st-income');
context.se193XRGameGround=()=>({x:3,z:4});
assert.equal(evalExpr('se193XRGameSelect({index:1})'),true);
assert(calls.some(s=>s.includes('build:{"kind":"st-income","x":3,"z":4}')),
 'trigger must use the existing authoritative Sheep Tag build command');
assert.equal(context.stUi.build,null);
assert.equal(evalExpr('se193XRGameSelect({index:1})'),true);
assert(calls.some(s=>s.includes('move:{"x":3,"z":4}')),
 'ground trigger must issue the original Sheep Tag move command');
evalExpr('se193XRSnapFollow()');
assert.equal(evalExpr('se193.follow'),true);
assert.equal(context.stUi.follow,true);
context.stSession=null;context.currentProject.kind='other';
evalExpr("se193XRAction('editorCapture')");
assert.equal(evalExpr('se193XRKind()'),'editor-capture',
 'spatial editor must have direct access to the capture studio');
assert.equal(evalExpr('se193.editorCaptureOpen'),true);
evalExpr("se193XRAction('back')");
assert.equal(evalExpr('se193.editorCaptureOpen'),false);
assert(calls.includes('palette:true'),'leaving capture must restore native editor tools');
assert(!source.includes('renderer.setAnimationLoop('),'adapter must not add a render loop');
assert(!source.includes('createPrefab('),'VR Sheep Tag must not mutate authored editor objects');
console.log('PASS v11.193: authored menu, native game orders, builds, follow reset, single-loop boundary');
