// v11.420: Test the actual last-layer Quest action wrappers, stable menu mesh
// identity after changing counts, native trigger delegation, boundaries and LAN.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const setup=fs.readFileSync(path.join(root,'runtime/sheep_team_setup_v11_416.js'),'utf8');
const menu=fs.readFileSync(path.join(root,'runtime/sheep_setup_menu_controls_v11_420.js'),'utf8');
let rebuilds=0,nextTexture=0,disposed=0,startCalls=0;
const tex=()=>({id:++nextTexture,dispose(){disposed++;}});
const records=new Map([
 ['menu',{role:'menu',next:'game'}],
 ['game',{role:'game',data:{project:{kind:'sheep-tag'},
  scene:{actors:Array.from({length:6},()=>({type:'st-sheep',visible:true,baked:true}))}}}]
]);
const ctx={
 window:{},renderer:{xr:{isPresenting:true}},se150Match:{active:false},
 seLevels:{records,playingMenu:true,overlay:{}},
 seLevelsCurrent:()=>records.get('menu'),
 se195:{mode:'menu',page:'main',visible:true,radial:null,buttons:[],textures:[],lastAction:''},
 se195Text(text){const t=tex();ctx.se195.textures.push(t);return t;},
 se195MakeRadial(){rebuilds++;},
 se195Page(page){
  ctx.se195.page=page;ctx.se195.visible=true;
  ctx.se195.radial={children:[]};ctx.se195.buttons=[];
  const mk=(name,action,header=false)=>({
   name,userData:action?{se195Action:action}:{},
   material:{map:ctx.se195Text(name),color:{setHex(){}},needsUpdate:false}
  });
  const heading=mk(page.toUpperCase(),null,true);
  ctx.se195.radial.children.push(heading);
  for(const [act,text] of ctx.se195Options('menu',page)){
   const button=mk(text,act);ctx.se195.buttons.push(button);
   ctx.se195.radial.children.push(button);
  }
  rebuilds++;
 },
 se195SetVisible(v){ctx.se195.visible=v;},
 se195Options:()=>[['start','PLAY'],['cinema','CINEMA'],['help','HELP'],['editor','EDIT']],
 se195HandleAction:()=>false,
 stSession:null,
 stStart:()=>{startCalls++;const sheep=Array.from({length:6},(_,i)=>({
   id:'s'+i,kind:'sheep',actor:{visible:true},captured:false
  }));ctx.stSession={controlledId:'s0',units:sheep,
    resources:Object.fromEntries(sheep.map(s=>[s.id,5])),buildings:[]};return {ok:true}},
 stStatus:()=>({active:true}),
 seLevelsTransition:()=>{ctx.seLevels.playingMenu=false;ctx.stStart();return true;},
 stopSession:()=>{ctx.stSession=null;return true;},
 seLevelsStopMenu:()=>{ctx.seLevels.playingMenu=false;return true;}
};
vm.createContext(ctx);vm.runInContext(setup,ctx);vm.runInContext(menu,ctx);
const act=x=>ctx.se195HandleAction(x,{controller:true,trigger:true});
assert(act('start'),'main menu starts setup');
assert.equal(ctx.se195.page,'aiSetup');
assert.equal(ctx.se195.visible,true);
assert.equal(ctx.se195Options('menu','aiSetup').length,5,'five actionable wedges');
assert(!ctx.se195Options('menu','aiSetup').some(([x])=>x==='se416Count'),'no inert count wedge');
const first=ctx.se195.radial,meshes=[...ctx.se195.buttons],heading=first.children[0],count=()=>ctx.window.SWYRL_ENGINE_SHEEP_TEAM_SETUP_416.count();
const initialRebuilds=rebuilds;
assert.equal(count(),5);
assert(act('se416Minus'));
assert.equal(count(),4);
assert.equal(first,ctx.se195.radial,'radial root stays mounted');
assert.deepEqual(meshes,ctx.se195.buttons,'all ray hit meshes remain same objects');
assert.equal(rebuilds,initialRebuilds,'no radial teardown/rebuild during count change');
assert.equal(heading.userData.se420Label,'AI SHEEP 4/5','count is clearly displayed');
assert(act('se416Plus'));
assert.equal(count(),5);
assert(act('se416Plus'));
assert.equal(count(),5);
assert(ctx.se195.lastAction.includes('Maximum'),'max press produces clear feedback');
assert(act('se420None'));
assert.equal(count(),0);
assert(act('se416Minus'));
assert.equal(count(),0);
assert(ctx.se195.lastAction.includes('Minimum'),'min press produces clear feedback');
assert.equal(ctx.se195Options('menu','aiSetup')[0][1],'MIN 0');
assert.equal(ctx.se195Options('menu','aiSetup')[1][1],'+ 1 SHEEP');
assert.equal(first,ctx.se195.radial);
assert.equal(ctx.se195.textures.length,6,'old label textures disposed, not leaked');
assert(disposed>0);
assert(act('se416Launch'));
assert.equal(startCalls,1);
assert.equal(ctx.stSession.units.filter(u=>u.kind==='sheep').length,1);
assert.equal(ctx.se195.visible,false);
ctx.seLevels.playingMenu=true;ctx.se195.page='main';ctx.se150Match.active=true;
assert(ctx.seLevelsTransition('game',true),'LAN host start unaffected');
assert.equal(ctx.stSession.units.length,6);
console.log('SHEEP_SETUP_MENU_420_PASS: main menu trigger, stable 3D ray/hover targets, +/-/none/min/max, texture disposal, launch and LAN');
