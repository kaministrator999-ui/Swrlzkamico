// Geometry-only contract for the short Cliff Hand forearm. No browser/Quest needed.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const file=require('node:path').join(__dirname,'../runtime/cliff_gauntlet_forearm_v11_289.js');
const api={window:{}};
vm.createContext(api);
vm.runInContext(fs.readFileSync(file,'utf8'),api);
const points=[];
for(let j=0;j<=140;j++){
 const y=.60+2.7*j/140,ang=j*.7;
 points.push(.18*Math.cos(ang),y,.14*Math.sin(ang));
}
const source={topologyMesh:{positions:points.slice(),uvs:[],indices:[0,1,2]}};
const old=source.topologyMesh.positions.slice();
const before={parts:1,vertices:old.length/3,indices:source.topologyMesh.indices.slice()};
const stats=api.window.SWYRL_ENGINE_CLIFF_GAUNTLET_289.extend(source);
assert.equal(stats.meshCount,1);
assert.equal(source.topologyMesh.positions.length,old.length);
assert.deepEqual(source.topologyMesh.indices,before.indices);
assert(stats.forearmExtension>.60&&stats.forearmExtension<.81);
for(let i=0;i<old.length;i+=3){
 const y=old[i+1],now=source.topologyMesh.positions[i+1];
 if(y>=1.28){
   assert.equal(now,y,'upper hand vertices must not move');
   assert.equal(source.topologyMesh.positions[i],old[i]);
   assert.equal(source.topologyMesh.positions[i+2],old[i+2]);
 }
 assert(now<=y,'forearm stretches downward, never upward');
 if(i>=3)assert(source.topologyMesh.positions[i+1]>source.topologyMesh.positions[i-2],
   'monotonic transform must not fold the vertical mesh');
}
const n=api.window.SWYRL_ENGINE_CLIFF_GAUNTLET_289.remapUV(source);
assert.equal(n,before.vertices);
assert.equal(source.topologyMesh.uvs.length,n*2);
assert(source.topologyMesh.uvs.every(v=>Number.isFinite(v)&&v>=0&&v<=1));
assert.equal(source.topologyMesh.positions.length,before.vertices*3);
console.log(JSON.stringify({verified:true,connectedMeshes:1,vertices:n,
 extension:stats.forearmExtension,rig:'retained in source scene',crackObjectsAdded:0}));
