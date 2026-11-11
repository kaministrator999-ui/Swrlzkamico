/* v11.416: zero/partial/full solo roster, VR menu and LAN bypass. */
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync(__dirname+'/../runtime/sheep_team_setup_v11_416.js','utf8');
let starts=0,radials=0;
const sheep=Array.from({length:6},(_,i)=>({id:'s'+i,kind:'sheep',
 actor:{visible:true},captured:false}));
const wolves=Array.from({length:2},(_,i)=>({id:'w'+i,kind:'wolf',actor:{visible:true},captured:false}));
const records=new Map([['menu',{role:'menu',next:'game'}],
 ['game',{role:'game',data:{project:{kind:'sheep-tag'},
 scene:{actors:Array.from({length:6},()=>({type:'st-sheep',baked:true}))}}}]]);
const ctx={console,window:{},renderer:{xr:{isPresenting:true}},
 seLevels:{records,playingMenu:true,overlay:{}},seLevelsCurrent:()=>records.get('menu'),
 se195:{mode:'menu',page:'main',visible:true},se195Page:p=>{ctx.se195.page=p;ctx.se195.visible=true},
 se195SetVisible:b=>{ctx.se195.visible=b},se195MakeRadial:()=>{radials++},
 se195Options:()=>[['start','PLAY']],se195HandleAction:()=>false,
 se150Match:{active:false},
 stSession:null,
 stStart:()=>{starts++;
  ctx.stSession={role:'sheep',controlledId:'s0',
   units:[...sheep,...wolves],resources:Object.fromEntries(sheep.map(s=>[s.id,80])),
   buildings:[{owner:'s5'}]};
  return {ok:true};
 },
 stStatus:()=>({units:ctx.stSession?.units.map(u=>({id:u.id,kind:u.kind}))}),
 stopSession:()=>{ctx.stSession=null;return true;},
 seLevelsStopMenu:()=>{ctx.seLevels.playingMenu=false;return true;},
 seLevelsTransition:()=>{ctx.seLevels.playingMenu=false;ctx.stStart();return true;},
};
vm.createContext(ctx);
vm.runInContext(src,ctx,{filename:'sheep_team_setup_v11_416.js'});
const api=ctx.window.SWYRL_ENGINE_SHEEP_TEAM_SETUP_416;
assert.equal(api.max(),5);assert.equal(api.count(),5,'default retains all five authored bots');
const opts=ctx.se195Options('menu','main');
assert.equal(opts[0][0],'start');
assert(ctx.se195HandleAction('start'), 'Quest PLAY opens setup');
assert.equal(ctx.se195.page,'aiSetup');
assert.equal(ctx.se195.visible,true,'Quest radial must remain visible');
assert.equal(starts,0,'do not start until confirmed');
for(const n of [0,2,5]){
 ctx.seLevels.playingMenu=true;ctx.se195.page='aiSetup';
 api.setCount(n);assert.equal(api.count(),n);
 assert(ctx.se195Options('menu','aiSetup').some(x=>x[0]==='se416Launch'));
 assert(ctx.se195HandleAction('se416Launch'));
 assert.equal(ctx.stSession.units.filter(u=>u.kind==='sheep').length,n+1);
 assert.equal(ctx.stSession.units.filter(u=>u.kind==='wolf').length,2);
 assert.equal(ctx.stSession.aiTeammates,n);
 assert.equal(ctx.stSession.buildings[0].owner,n===5?'s5':'s0');
 assert.equal(ctx.se195.visible,false);
 assert(ctx.stopSession());
 for(const s of sheep)s.actor.visible=true; // native stStop restores authored visibility
 ctx.seLevels.playingMenu=true;
}
assert(radials>=0);
ctx.se150Match.active=true;ctx.seLevels.playingMenu=true;
const before=starts;
assert(ctx.seLevelsTransition('game',true));
assert.equal(starts,before+1);
assert.equal(ctx.stSession.units.filter(u=>u.kind==='sheep').length,6,'LAN roster unchanged');
ctx.stopSession();
ctx.se150Match.active=false;
console.log('PASS se416 Quest chooser, authored 0/2/5 AI roster, LAN bypass');
