#!/usr/bin/env node
// Focused §E v11.309 test: actual assembled handler + mocked two XR records.
// No headset, no app-wide browser suite; verify the reported visual failure path.
const fs=require('fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2],'utf8');
const begin=html.indexOf('// §E v11.309:');
const end=html.indexOf('window.SWYRLZ_FORGE_BUILD=',begin);
assert(begin>=0&&end>begin,'v11.309 source compiled once');
const source=html.slice(begin,end);
const records=[0,1].map(index=>({
 index,ray:{visible:true},
 se192:{pivot:{rotation:{y:index?.14:-.12}},
 beam:{visible:true},dot:{visible:true}}
}));
const eventLog=[];
const app={
 se181XR:{session:{},controllers:records},
 renderer:{xr:{isPresenting:true}},
 currentProject:{kind:'blank-vr-hands'},se279GameId:'blank-vr-hands',
 se192:{savedAim:[-.12,.14]},
 se192RenderRay:(record)=>{eventLog.push('original-ray-'+record.index);record.se192.beam.visible=true;record.se192.dot.visible=true;},
 se192VRFrame:()=>{for(const r of records){app.se192RenderRay(r,{});r.se192.beam.visible=true;}},
 window:{},Object
};
vm.createContext(app);
vm.runInContext(source,app);
app.se192VRFrame();
for(const r of records){
 assert.equal(r.ray.visible,false,'legacy line hidden in Arcane');
 assert.equal(r.se192.beam.visible,false,'tapered beam hidden in Arcane');
 assert.equal(r.se192.dot.visible,false,'target reticle hidden in Arcane');
 assert.equal(r.se192.pivot.rotation.y,0,'no saved yaw in Arcane hit test');
}
assert.deepEqual(eventLog,[],'no visible renderer called in Arcane');
assert.equal(app.window.SWYRL_ENGINE_ARCANE_RAY_309.status().visualBeams,0);
app.currentProject.kind='sheep-tag';
app.se192VRFrame();
assert.deepEqual(eventLog,['original-ray-0','original-ray-1'],'other project renderer preserved');
for(const r of records){
 assert.equal(r.se192.pivot.rotation.y,app.se192.savedAim[r.index],'saved yaw restored elsewhere');
 assert.equal(r.se192.beam.visible,true,'spatial beam restored outside Arcane');
 assert.equal(r.ray.visible,false,'legacy duplicate still suppressed by spatial editor');
}
app.currentProject.kind='blank-vr-hands';
app.se192VRFrame();
for(const r of records)assert.equal(r.se192.beam.visible,false,'re-enter Arcane hides beams again');
app.se181XR.session=null;
app.renderer.xr.isPresenting=false;
app.currentProject.kind='sheep-tag';
app.se192VRFrame();
assert.equal(app.window.SWYRL_ENGINE_ARCANE_RAY_309.status().active,false);
assert(html.includes('function se280Cast(side,record,key){'),'spell casting preserved');
assert(html.includes('const anchor=se308GloveAnchor(side,record);'),'grip-space glove mount preserved');
console.log('SE309_NATIVE_RAY_SMOKE_OK',JSON.stringify({controllers:2,scenarios:4}));
