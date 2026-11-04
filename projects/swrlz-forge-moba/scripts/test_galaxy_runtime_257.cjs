// Focused first native galaxy particle step, actual Three.js without browser UI.
const fs=require('node:fs'),vm=require('node:vm');
const THREE=require(process.env.THREE_PATH);
const runtime=process.env.RUNTIME_ROOT;
const canvas=()=>({width:64,height:64,getContext:()=>({
 createRadialGradient:()=>({addColorStop(){}}),
 fillStyle:'',fillRect(){}
})});
const doc={readyState:'loading',visibilityState:'visible',addEventListener(){},
 createElement(tag){return tag==='canvas'?canvas():{style:{},append(){},querySelector(){return null}}},
 getElementById(){return null},querySelector(){return null},body:{}};
const ctx={THREE,console,document:doc,devicePixelRatio:1,window:{addEventListener(){}},
 scene:new THREE.Scene(),camera:new THREE.PerspectiveCamera(),renderer:{},
 playing:false,simulating:false,paused:false,actors:[],structuredClone,
 uid:(()=>{let i=0;return ()=>'emitter_'+(++i)})(),
 toast(){},beginTransaction(){},commitTransaction(){},performance:{now:()=>0}};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[2],'utf8'),ctx,{filename:'effective-core'});
vm.runInContext('function se223UIRefresh(){}',ctx);
for(const filename of ['astral_vortex_starter_v11_248.js',
 'astral_vortex_ribbons_v11_249.js',
 'particle_curve_runtime_v11_251.js',
 'astral_nebula_filaments_v11_251.js']){
 vm.runInContext(fs.readFileSync(runtime+'/'+filename,'utf8'),ctx,{filename});
}
vm.runInContext("var galaxyConfigs=['vortex','vortexCyan','vortexCore','vortexSpark'].map(k=>se223Default(k))",ctx);
ctx.currentProject={particleStudio:{schema:'swyrl-particle-studio-v1',emitters:ctx.galaxyConfigs}};
vm.runInContext('se223State.preview=true;se223Reset()',ctx);
for(const cfg of ctx.galaxyConfigs){
 try{
  vm.runInContext('se223Runtime(currentProject.particleStudio.emitters.find(x=>x.id==='+JSON.stringify(cfg.id)+'))',ctx);
  vm.runInContext('se223Spawn(currentProject.particleStudio.emitters.find(x=>x.id==='+JSON.stringify(cfg.id)+'),3)',ctx);
  vm.runInContext('se223Step(currentProject.particleStudio.emitters.find(x=>x.id==='+JSON.stringify(cfg.id)+'),.016)',ctx);
  console.log('PASS emitter first step:',cfg.preset);
 }catch(error){
  console.error('FAIL emitter first step:',cfg.preset,error.stack||error);
  process.exitCode=1;
 }
}
for(let i=0;i<8;i++){
 try{vm.runInContext('se223Frame(.016,0)',ctx);}
 catch(error){console.error('FAIL whole galaxy frame:',i,error.stack||error);process.exitCode=1;break}
}
console.log('Native runtime records:',vm.runInContext('se223State.live.size',ctx));
if(process.exitCode)process.exit(process.exitCode);
