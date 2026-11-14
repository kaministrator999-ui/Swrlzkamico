import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
assert(process.argv[2],'Pass current sealed HTML');
const html=fs.readFileSync(process.argv[2],'utf8');
const expected=[["/* SE413_SATCHEL_VR_QUEST_START", "/* SE413_SATCHEL_VR_QUEST_END */", "ab90bb9ad03dbcec27736a745bb3b345e2f4206150520423427bd92ee51b2b49"], ["/* SE416_SATCHEL_VR_COACH_START", "/* SE416_SATCHEL_VR_COACH_END */", "ac537d01f517e80aed0488f5f5f3f47e27723b3d71d136f05cfdc32f68d37679"], ["/* SE436_SATCHEL_CAVITY_START */", "/* SE436_SATCHEL_CAVITY_END */", "d7b9ede61d343bea2bfeb48b32d685226afc02e932cb6d0faffc5b436062d1c5"], ["/* SE436_VR_CUBE_EXTRUDE_START */", "/* SE436_VR_CUBE_EXTRUDE_END */", "2147277537ba6dfdbf494d1ab95a8906e0b929c874e7429bd787452402819a22"], ["/* SE430_MODEL_VR_MANUAL_WORKSHOP_START */", "/* SE430_MODEL_VR_MANUAL_WORKSHOP_END */", "afacbac1cfe08eba7c90ac29003b763eeee4238dc2b3da85f506ac864d175427"], ["/* SE441_SATCHEL_WORKFLOW_START */", "/* SE441_SATCHEL_WORKFLOW_END */", "b112f5f0af9255fbe6e317e943fa980dc9b909510bc346aff59b83d588dfcbe8"], ["/* SE441_SATCHEL_LESSON_START */", "/* SE441_SATCHEL_LESSON_END */", "7b0363dcb346a2b8308d84680071476916bb3f9894c5a01d7656a4ac2ee84ab9"]];
function section(a,b){assert.equal(html.split(a).length,2,a);assert.equal(html.split(b).length,2,b);return html.slice(html.indexOf(a),html.indexOf(b)+b.length);}
for(const [a,b,hash]of expected)assert.equal(crypto.createHash('sha256').update(section(a,b)).digest('hex'),hash,a+' must preserve the hosted441 VR/geometry implementation');
let groups=1;
const calls=[];
const base={steps:Array.from({length:7},(_,i)=>Object.freeze({title:'Tool '+i,tool:'VR tool '+i,task:'old flat task',hint:'old flat hint',vrTask:'VR task '+i,vrHint:'VR hint '+i,...(i?{vrTool:'Explicit VR '+i}:{})})),workflow:'one-body-v1',showMe:(...args)=>{calls.push(args);return 'native VR';}};
for(const key of ['verify','amountFor','drawName','makeGhost'])base[key]=()=>key;
Object.freeze(base);
const sandbox=vm.createContext({window:{SWYRL_E_SATCHEL_LESSON_441:base,SWYRL_ENGINE_TUTORIAL_412:{status:()=>({active:false})}},document:{querySelector(){throw Error('VR delegation must not touch flat DOM');}}});
vm.runInContext(section('/* SE442_SATCHEL_FLAT_LESSON_START */','/* SE442_SATCHEL_FLAT_LESSON_END */'),sandbox);
const lesson=sandbox.window.SWYRL_E_SATCHEL_LESSON_441;
for(const key of ['verify','amountFor','drawName','makeGhost','workflow'])assert.equal(lesson[key],base[key],key);
for(let i=0;i<7;i++){
 assert.equal(lesson.steps[i].title,base.steps[i].title);assert.equal(lesson.steps[i].vrTask||lesson.steps[i].task,base.steps[i].vrTask||base.steps[i].task);
 assert.equal(lesson.steps[i].vrHint||lesson.steps[i].hint,base.steps[i].vrHint||base.steps[i].hint);
 assert.equal(lesson.steps[i].vrTool||lesson.steps[i].tool,base.steps[i].vrTool||base.steps[i].tool);
 assert.equal(lesson.showMe(i,true),'native VR');assert.equal(calls.at(-1)[0],i);assert.equal(calls.at(-1)[1],true);
}
assert.equal(lesson.showMe(1,false),null);groups++;
const a=html.indexOf(' const GROUPS={');assert(a>=0);const b=html.indexOf('\n };',a);assert(b>a);
const rule=html.match(/ if\(!GROUPS\.Meshes\.some[^\n]+SE442_TRANSFORM_DISCOVERY/)[0];
const catalog=vm.createContext({});vm.runInContext(html.slice(a,b+4)+'\n'+rule+'\nthis.result=GROUPS;',catalog);
const mesh=catalog.result.Meshes;assert.equal(mesh.filter(r=>r[0]==='Transform').length,1);assert.equal(mesh.filter(r=>r[0]==='Mesh identity').length,1);
assert.equal(mesh.find(r=>r[0]==='Transform')[1].length,9);assert(mesh.some(r=>r[0]==='Assemblies & selection'));groups++;
for(const kind of ['position','rotation','scale'])for(let i=0;i<3;i++){
 const tag=html.match(new RegExp('<input type="number"[^>]+id="modelAtelier'+kind+i+'"[^>]*>'))[0];
 assert.match(tag,/step=".001"/);assert.match(tag,/aria-label=/);
 if(kind==='scale')assert.match(tag,/min=".006"/);
}groups++;
const start=html.indexOf('function se430BeginnerAmount('),end=html.indexOf('\n}',start);assert(start>=0&&end>start);
const amount=vm.createContext({});vm.runInContext(html.slice(start,end+2)+'\nthis.get=se430BeginnerAmount;',amount);
for(const op of ['inset','extrude','solidify','subdivide']){
 const row=amount.get(op);assert(row.value>=row.min&&row.value<=row.max);assert(Math.abs((row.value-row.min)/row.step-Math.round((row.value-row.min)/row.step))<1e-8,op+' default is a valid numeric step');
}groups++;
assert(html.includes('window.SWYRL_E_SATCHEL_DIALOG_442.mount(panel)'));
console.log('MODEL_SATCHEL_BROWSER_PRESERVATION_442_PASS',JSON.stringify({groups,hosted441SegmentsPreserved:expected.length,vrLessonDelegated:true,transformDiscoverable:true,typedPrecision:0.001,physicalAndroid:false}));
