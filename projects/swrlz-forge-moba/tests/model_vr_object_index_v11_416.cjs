const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const code=fs.readFileSync(path.join(__dirname,'../runtime/model_vr_object_index_v11_416.js'),'utf8');
const entries=Array.from({length:23},(_,i)=>({id:'part-'+i,name:i<2?'Same name':'Object '+i})),ids=[];
const state={scene:{},session:{},page:'tools',se416IndexPage:0,se416IndexMulti:false},calls=[];
class Vec{constructor(x=0,y=0,z=0){Object.assign(this,{x,y,z});}copy(v){Object.assign(this,{x:v.x,y:v.y,z:v.z});return this;}clone(){return new Vec(this.x,this.y,this.z);}multiply(v){this.x*=v.x;this.y*=v.y;this.z*=v.z;return this;}multiplyScalar(v){this.x*=v;this.y*=v;this.z*=v;return this;}applyQuaternion(){return this;}addScaledVector(v,n){this.x+=v.x*n;this.y+=v.y*n;this.z+=v.z*n;return this;}}
class Mesh{constructor(g,m){this.isMesh=true;this.geometry=g;this.material=m;this.position=new Vec();this.scale=new Vec(1,1,1);this.quaternion={copy(){return this;}};this.userData={};this.visible=true;this.renderOrder=0;}
 removeFromParent(){if(this.parent){this.parent.children=this.parent.children.filter(n=>n!==this);this.parent=null;}}}
class Skin extends Mesh{constructor(g,m){super(g,m);this.isSkinnedMesh=true;this.bindMatrixInverse={copy(){return this;}};}bind(s,b){this.skeleton=s;this.bindMatrix=b;}}
class Mat{constructor(opts){this.opts=opts;}dispose(){this.disposed=true;}}
const THREE={MathUtils:{clamp:(n,a,b)=>Math.max(a,Math.min(b,n))},BackSide:1,Mesh,SkinnedMesh:Skin,MeshBasicMaterial:Mat};
const tools=()=>({selection:()=>({ids:[...ids]}),select:(id,options={})=>{const i=ids.indexOf(id);if(options.additive){if(i>=0)ids.splice(i,1);else if(ids.length<32)ids.push(id);else return{ok:false,error:'MODEL_SELECTION_LIMIT_32'};}else{ids.splice(0,ids.length);if(id)ids.push(id);}return{ok:true};}});
const factory=new Function('THREE','se340XR','se340VisibleSession','se340CancelGesture','se340PartEntries','se340Notice','se350Tools','se350Invalidate','se340SyncUI','se340Publish','se350Result','se340Pulse',code+'\nreturn {se416IndexAction,se416IndexState,se416IndexPageCount,se416UpdateHighlights,se416DisposeHighlights};');
const t=factory(THREE,state,()=>true,()=>{state.gesture=null;},()=>entries,v=>calls.push(v),tools,()=>{},()=>{},()=>{},()=>{},()=>{});
assert.equal(t.se416IndexPageCount(0),1);assert.equal(t.se416IndexPageCount(23),3);
assert.equal(t.se416IndexAction('objects'),true);assert.equal(state.page,'objects');
t.se416IndexAction('index-part-0');t.se416IndexAction('index-part-1');assert.deepEqual(ids,['part-1'],'single replaces by ID, not name');
t.se416IndexAction('index-add');t.se416IndexAction('index-part-0');assert.deepEqual(ids,['part-1','part-0']);
t.se416IndexAction('index-part-1');assert.deepEqual(ids,['part-0'],'multi toggles selected part off');
t.se416IndexAction('index-next');assert.equal(state.se416IndexPage,1);assert.equal(t.se416IndexAction('index-part-8'),false);
t.se416IndexAction('index-part-9');assert.deepEqual(ids,['part-0','part-9']);
t.se416IndexAction('index-next');t.se416IndexAction('index-next');assert.equal(state.se416IndexPage,2);
assert.equal(t.se416IndexAction('index-part-23'),false);
assert.equal(t.se416IndexAction('index-part-NaN'),false);
assert.equal(t.se416IndexState(state,entries,new Set(ids)).indexEntries.length,5);
t.se416IndexAction('index-add');t.se416IndexAction('index-part-22');assert.deepEqual(ids,['part-22']);
const parent={children:[],add(m){this.children.push(m);m.parent=this;}};
const geometry={boundingSphere:{radius:.5,center:new Vec(.2,0,0)}};
const a=new Mesh(geometry,{}),b=new Skin(geometry,{});b.bind({bones:[]},{});
parent.add(a);parent.add(b);
const s={scene:{}};const list=[{id:'a',name:'Bag',mesh:a},{id:'b',name:'Sleeve',mesh:b}];
t.se416UpdateHighlights(s,list,new Set(['a','b']));
assert.equal(s.se416Shells.size,2);assert.equal(parent.children.length,4);
assert.equal(s.se416Shells.get('a').shell.geometry,geometry);
assert.equal(s.se416Shells.get('b').shell.skeleton,b.skeleton);
assert.equal(s.se416Shells.get('a').shell.userData.se416SelectedSilhouette,true);
assert.equal(s.se416ShellMaterial.opts.side,THREE.BackSide);
t.se416UpdateHighlights(s,list,new Set(['b']));assert.equal(s.se416Shells.size,1);
const material=s.se416ShellMaterial;t.se416DisposeHighlights(s);
assert.equal(parent.children.length,2);assert.equal(material.disposed,true);
console.log('MODEL_VR_OBJECT_INDEX_ACTIONS_AND_SILHOUETTES_PASS');
