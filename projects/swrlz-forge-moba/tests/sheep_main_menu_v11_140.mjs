import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const root='projects/swrlz-forge-moba/';
const source=fs.readFileSync(root+'runtime/sheep_main_menu_attract_v11_140.js','utf8');
const css=fs.readFileSync(root+'runtime/sheep_main_menu_attract_v11_140.css','utf8');
const assembled=process.env.SE_ASSEMBLED_HTML;
assert.ok(assembled,'Test assembled sealed HTML, not only standalone runtime fragment');
const html=fs.readFileSync(assembled,'utf8');
for(const term of ['V11_140_SHEEP_START_MENU_CINEMATIC',
 'animeUpdateCinematic(dt);st140MenuTick(dt);',
 'const st140LoadStarterBase=stLoadStarter',
 'st140MenuStart','se140-sheep-main-menu'])
 assert.ok(html.includes(term),'missing assembled integration '+term);
class V3 {
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 set(x,y,z){this.x=x;this.y=y;this.z=z;return this;}
 clone(){return new V3(this.x,this.y,this.z);}
 copy(v){return this.set(v.x,v.y,v.z);}
}
class Group{
 constructor(){this.children=[];this.position=new V3();this.rotation={x:0,y:0,z:0};this.visible=true;
 this.scale={x:1,y:1,z:1,set(x,y,z){this.x=x;this.y=y;this.z=z;},setScalar(n){this.x=this.y=this.z=n;}};
 }
 add(child){this.children.push(child);}
 remove(child){this.children=this.children.filter(x=>x!==child);}
}
class Mesh extends Group {constructor(geometry,material){super();this.geometry=geometry;this.material=material;}}
const CSSClasses=()=>({values:new Set(),add(x){this.values.add(x)},remove(x){this.values.delete(x)},contains(x){return this.values.has(x)}});
const viewport={children:[],classList:CSSClasses(),appendChild(x){this.children.push(x);x.parent=this;}};
const fakeMenu=()=>({
 id:'',className:'',attributes:{},remove(){if(this.parent){this.parent.children=this.parent.children.filter(x=>x!==this);this.parent=null;}},
 setAttribute(k,v){this.attributes[k]=v},addEventListener(){},
 querySelector(query){return query==='#st140StartGame'?this.start:null},
 start:{listeners:{},addEventListener(event,fn){this.listeners[event]=fn;},click(){this.listeners.click();}}
});
let nativePlay=0,savedLoads=0,disposals=0,menuInstalls=0;
const actors=[{name:'author-owned-unit'}];
const scene={children:[],add(x){this.children.push(x)},remove(x){this.children=this.children.filter(y=>y!==x)}};
const perspectiveCamera={position:new V3(45,70,42),quaternion:{clone(){return {copy(){}}},copy(){}},
 up:new V3(0,1,0),fov:50,updateProjectionMatrix(){},lookAt(){},updateMatrixWorld(){}};
const orbit={target:new V3(),enabled:true,update(){}};
const ctx={
 console,Math,Number,THREE:{Group,Mesh,Vector3:V3,CircleGeometry:class{},PlaneGeometry:class{},MeshStandardMaterial:class{}},
 scene,perspectiveCamera,orbit,actors,currentProject:{kind:'other'},
 playing:false,simulating:false,stSession:null,
 terrainHeight(){return 0;},
 stMakeVisual(type){const v=new Group();v.type=type;return v;},
 stDisposeVisual(){disposals++;},
 stLoadStarter(){savedLoads++;ctx.loadProject({kind:'sheep-tag'});},
 loadProject(data){ctx.currentProject=data;},
 st140__probe:0,
 toast(){},
 $:id=>id==='viewport'?viewport:id==='playBtn'?{
  disabled:false,click(){nativePlay++;ctx.stSession={active:true};}
 }:null,
 document:{createElement(){menuInstalls++;return fakeMenu();}}
};
vm.createContext(ctx);
vm.runInContext(source,ctx,{filename:'sheep-attract-140.js'});
const value=expr=>vm.runInContext(expr,ctx);
ctx.st140MenuOpen();
assert.equal(value('st140Menu.open'),false,'do not install menu into unrelated editor projects');
ctx.stLoadStarter();
assert.equal(savedLoads,1);
assert.equal(value('st140Menu.open'),true);
assert.equal(nativePlay,0,'opening the starter must never run gameplay');
assert.equal(viewport.children.length,1,'one menu overlay');
assert.equal(scene.children.length,1,'one transient 3D stage');
assert.equal(actors.length,1,'no saved actors created');
assert.equal(value('st140Menu.visuals.length'),4,'three sheep and one scripted wolf');
assert.equal(value('st140Menu.houses.length'),4,'four lightweight transient house visuals');
assert.equal(orbit.enabled,false);
assert.equal(viewport.classList.contains('st140-menu-root'),true);
const originalCamera=perspectiveCamera.position.clone();
ctx.st140MenuTick(.016);
ctx.st140MenuTick(4);
assert.notEqual(perspectiveCamera.position.x,originalCamera.x,'cinematic camera must move in 3D');
assert.equal(ctx.stSession,null,'demo never starts live match');
assert.equal(nativePlay,0);
assert.equal(css.includes('id="st140StartGame"'),false,'CSS should use selector, not embed markup');
assert.ok(css.includes('#st140StartGame'));
assert.ok(source.includes('▶ START GAME'));
// Start Game must close demo and go THROUGH the single original Play button.
viewport.children[0].start.click();
assert.equal(nativePlay,1,'Start Game invokes existing Play exactly once');
assert.equal(scene.children.length,0,'all transient 3D models cleaned');
assert.equal(viewport.children.length,0,'overlay removed');
assert.equal(disposals,1,'attract group disposed once');
assert.equal(orbit.enabled,true,'editor camera controls restored');
assert.equal(value('st140Menu.open'),false);
assert.equal(actors.length,1);
assert.equal(viewport.classList.contains('st140-menu-root'),false);
// Repeated click must not initiate duplicate games.
assert.equal(value('st140MenuStart()'),false);assert.equal(nativePlay,1);
// Re-enter starter, switch project before Play: dispose every transient object.
ctx.stSession=null;
ctx.stLoadStarter();
assert.equal(scene.children.length,1);
ctx.loadProject({kind:'anime-studio'});
assert.equal(scene.children.length,0);
assert.equal(viewport.children.length,0);
assert.equal(disposals,2);
assert.equal(ctx.currentProject.kind,'anime-studio');
assert.equal(nativePlay,1);
assert.equal(actors.length,1);
console.log('SE140_SHEEP_STARTER_CINEMATIC_TITLE_NATIVE_PLAY_CLEANUP_PASS');
