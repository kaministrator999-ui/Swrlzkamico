const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const s=fs.readFileSync(process.argv[2], 'utf8');
const start=s.indexOf('loadProject=function(data,...args){',s.indexOf('const seLevelRawLoadProject=loadProject;'));
const end=s.indexOf('\n};\nfunction seLevelsSwitch(id)',start);
assert.ok(start>0&&end>start,'v11.183 native levels wrapper missing');
assert.ok(!s.slice(start,end).includes('seLevelRawLoadProject(structuredClone(chosen.data)'),'redundant second scene build returned');
const code=s.slice(start,end+3);
function harness(internal=false){
 const calls=[];
 const context={
  loadProject:null,seLevels:{loading:internal,playingMenu:false},
  seLevelsHydrate:()=>true,seLevelsInitSingle:()=>{throw Error('Unexpected single init')},
  seLevelsEnsureUI(){},seLevelsRefresh(){},
  seLevelRawLoadProject(data,...args){calls.push({data,args});return 'native-loaded';},
  structuredClone,Error,Array
 };
 vm.createContext(context);vm.runInContext(code,context,{timeout:1000});
 return {context,calls};
}
const full={project:{name:'Pack',levelPack:{schema:'se-levels-v1',active:'level-2',levels:[
 {id:'level-1',data:{project:{name:'Menu'},scene:{actors:[{type:'menu'}]}}},
 {id:'level-2',data:{project:{name:'Gameplay'},scene:{actors:[{type:'game'}]}}}
]}},scene:{actors:[{type:'outer'}]}};
const {context,calls}=harness();
assert.equal(context.loadProject(full,{fromOwner:true}),'native-loaded');
assert.equal(calls.length,1,'a bundled multi-level project must invoke native scene loader once');
assert.equal(calls[0].data.project.name,'Gameplay');
assert.equal(calls[0].args[0].workspaceLocal,true);
assert.equal(calls[0].args[0].fromOwner,true);
const plain={project:{name:'Plain'},scene:{actors:[]}};
const fallback=harness(true);
fallback.context.loadProject(plain,{workspaceLocal:false});
assert.equal(fallback.calls.length,1);
assert.equal(fallback.calls[0].data,plain);
console.log('SE183_SINGLE_SCENE_BUILD_PASS');
