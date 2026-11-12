// Regression against the function shipped in the assembled editor, rather
// than a second implementation of the component-to-vertex resolver.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const htmlPath=process.argv[2];
assert.ok(htmlPath,'Pass the assembled Model Studio HTML as the first argument');
const html=fs.readFileSync(htmlPath,'utf8');
const signature='function atelierComponentIndices(';
const start=html.indexOf(signature);
assert.ok(start>=0,'The assembled editor must contain its native component resolver');
assert.equal(html.indexOf(signature,start+signature.length),-1,'The native resolver must have one definition');

// Stop at the matching function brace. Comments and string contents cannot
// accidentally end the extracted function when the source is reorganized.
const opening=html.indexOf('{',start);
let depth=0,quote='',comment='',escaped=false,end=-1;
for(let i=opening;i<html.length;i++){
 const c=html[i],next=html[i+1];
 if(comment==='line'){if(c==='\n')comment='';continue;}
 if(comment==='block'){if(c==='*'&&next==='/'){comment='';i++;}continue;}
 if(quote){if(escaped){escaped=false;continue;}if(c==='\\'){escaped=true;continue;}if(c===quote)quote='';continue;}
 if(c==='/'&&next==='/'){comment='line';i++;continue;}
 if(c==='/'&&next==='*'){comment='block';i++;continue;}
 if(c==='"'||c==="'"||c==='`'){quote=c;continue;}
 if(c==='{')depth++;
 if(c==='}'&&--depth===0){end=i+1;break;}
}
assert.ok(end>opening,'The native resolver function must have balanced braces');
const source=html.slice(start,end);
const context=vm.createContext({});
vm.runInContext('let atelierComponentMode="vertex",atelierComponentIds=[2];\n'+source+
 '\nglobalThis.resolve=atelierComponentIndices;',context,{filename:'assembled-component-resolver.js'});

// Geometry seams make storage slots differ from the visible vertex ordinals.
// The UI highlights top.vertices[ordinal], so ordinal 2 means physical C,
// whose two coincident UV slots are 4 and 5; storage slot 2 instead means B.
const topology={
 vertices:[0,2,4,6],
 keys:['A','A','B','B','C','C','D','D'],
 groups:new Map([['A',[0,1]],['B',[2,3]],['C',[4,5]],['D',[6,7]]]),
 edges:[[0,2],[2,4],[4,6],[6,0]],
 tri:[[0,2,4],[0,4,6]]
};
const snapshot=()=>JSON.stringify({...topology,groups:[...topology.groups]});
const baseline=snapshot();
const resolve=(mode,ids)=>Array.from(context.resolve(topology,mode,ids));
const groups=[];
function test(name,fn){fn();groups.push(name);}

test('Vertex ordinal resolves to the same physical vertex as its highlight',()=>{
 assert.equal(topology.vertices[2],4);
 assert.deepEqual(resolve('vertex',[2]),[4,5]);
 assert.notDeepEqual(resolve('vertex',[2]),[2,3]);
});
test('First and last visible vertex ordinals expand their complete UV seam groups',()=>{
 assert.deepEqual(resolve('vertex',[0]),[0,1]);
 assert.deepEqual(resolve('vertex',[3]),[6,7]);
 assert.deepEqual(resolve('vertex',[0,3]),[0,1,6,7]);
});
test('Edge selection expands physical endpoints rather than treating them as ordinals',()=>{
 assert.deepEqual(resolve('edge',[1]),[2,3,4,5]);
 assert.deepEqual(resolve('edge',[3]),[0,1,6,7]);
});
test('Face selection expands all coincident slots for every physical corner',()=>{
 assert.deepEqual(resolve('face',[0]),[0,1,2,3,4,5]);
 assert.deepEqual(resolve('face',[1]),[0,1,4,5,6,7]);
});
test('Overlapping multi-selections are unique and consistently ordered',()=>{
 assert.deepEqual(resolve('vertex',[3,2,2,0]),[0,1,4,5,6,7]);
 assert.deepEqual(resolve('edge',[2,1,2]),[2,3,4,5,6,7]);
 assert.deepEqual(resolve('face',[1,0,1]),[0,1,2,3,4,5,6,7]);
});
test('Missing, fractional and out-of-range component IDs never select another point',()=>{
 for(const mode of ['vertex','edge','face']){
  assert.deepEqual(resolve(mode,[-1,999,NaN,Infinity,1.25]),[]);
  assert.deepEqual(resolve(mode,[]),[]);
 }
 assert.deepEqual(resolve('vertex',[4]),[]);
 assert.deepEqual(resolve('edge',[4]),[]);
 assert.deepEqual(resolve('face',[2]),[]);
 assert.deepEqual(resolve('mesh',[2]),[]);
});
test('Current native mode/selection defaults remain supported without source mutation',()=>{
 assert.deepEqual(Array.from(context.resolve(topology)),[4,5]);
 assert.equal(snapshot(),baseline);
});

console.log('MODEL_COMPONENT_SELECTION_V11_430_PASS',JSON.stringify({
 groups:groups.length,source:'assembled native atelierComponentIndices',
 uvSeamOrdinalRegression:true,edgeAndFaceAliases:true,invalidSelectionSafe:true
}));
