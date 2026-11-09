#!/usr/bin/env node
// Focused tests for marker coordinate equivalence and native model persistence.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../runtime/model_uv_art_marker_v11_366.js'),'utf8');
let checkpoints=0,edited=0,previewed=0;
let part={id:'mage-face',name:'Mage face',kind:'sphere'};
const objects={};
const context={
  console,window:objects,Math,Number,JSON,
  ensurePanel(){},refreshInspector(){},checkPart(){return true},
  se336SelectedMesh(){return {part,mesh:{geometry:{}}}},
  se336SlideState(){return {enabled:false}},
  se336SlideOffset(){return [0,0]},
  se356UVPreviewSchedule(){previewed++},
  se336UVLayout(){return {triangles:1260,vertices:713}},
  checkpoint(){checkpoints++},signalEdited(){edited++},
  document:{getElementById(){return null},createElement(){return {width:1024,height:1024}}},
  status(){},selection:'mage-face',partById(){return part},
};
const sandbox=vm.createContext(context);
vm.runInContext(source,sandbox);
const api=objects.SWYRLZ_E_UV_ART_MARKER;
assert(api,'Exported §E marker API missing');
const markers=[
  {version:1,centerUV:[.255555565,.712121228],angleDeg:0,scale:1},
  {version:1,centerUV:[.255555565,.712121228],angleDeg:25,scale:1.3},
  {version:1,centerUV:[.5,.65],angleDeg:-78,scale:.75},
  {version:1,centerUV:[.99,.02],angleDeg:180,scale:2},
];
let evaluated=0;
for(const marker of markers){
  assert.equal(vm.runInContext('se366Valid('+JSON.stringify(marker)+')',sandbox),true);
  const center=api.nativeToArt(...marker.centerUV,marker);
  for(const val of center)assert(Math.abs(val-.5)<1e-10,'Selected UV not authored at image center');
  for(let u=0;u<=1;u+=.125)for(let v=0;v<=1;v+=.125){
    const a=api.nativeToArt(u,v,marker);
    const inverse=api.artToNative(...a,marker);
    assert(Math.abs(inverse[0]-u)<1e-10, 'U round trip');
    assert(Math.abs(inverse[1]-v)<1e-10, 'V round trip');
    evaluated++;
  }
}
assert.equal(vm.runInContext("se366Valid({version:1,centerUV:[1.1,0],angleDeg:0,scale:1})",sandbox),false);
assert.equal(vm.runInContext("se366Valid({version:1,centerUV:[.5,.5],angleDeg:0,scale:0})",sandbox),false);
const turn90={version:1,centerUV:[.5,.5],angleDeg:90,scale:1};
const turned=api.nativeToArt(.6,.5,turn90);
assert(Math.abs(turned[0]-.5)<1e-10&&Math.abs(turned[1]-.6)<1e-10,'Clockwise angle is in image-pixel coordinates');
// Project persistence and undo checkpoints are owned by the original model.
vm.runInContext("se366MarkAt(.25555,.71)",sandbox);
assert.deepEqual(Array.from(part.uvArtMarker.centerUV),[.25555,.71]);
assert.equal(checkpoints,1);
assert.equal(edited,1);
const stored=JSON.parse(JSON.stringify(part));
assert.deepEqual(stored.uvArtMarker,part.uvArtMarker);
vm.runInContext("se366MarkAt(.25555,.71)",sandbox);
assert.equal(checkpoints,1,'Idempotent marker placement should not create duplicate undo');
const calls=[];
const drawContext={clearRect(...v){calls.push(['clearRect',...v])},
 save(){calls.push(['save'])},restore(){calls.push(['restore'])},
 translate(...v){calls.push(['translate',...v])},
 rotate(v){calls.push(['rotate',v])},
 scale(...v){calls.push(['scale',...v])},
 drawImage(...v){calls.push(['drawImage',...v.slice(1)])}};
const drawCanvas={width:1024,height:1024,getContext(){return drawContext}};
sandbox.canvas=drawCanvas;
sandbox.exampleMarker=markers[1];
vm.runInContext("se366BakeArtwork(canvas,{width:1024,height:1024},exampleMarker)",sandbox);
assert.equal(calls.filter(x=>x[0]==='drawImage').length,25);
assert.equal(calls.filter(x=>x[0]==='translate').length,2);
assert.equal(calls.filter(x=>x[0]==='rotate')[0][1],-markers[1].angleDeg*Math.PI/180);
assert.equal(calls.filter(x=>x[0]==='scale')[0][1],1/markers[1].scale);
console.log('UV_MARKER_TESTS_OK',JSON.stringify({
  coordinateRoundTrips:evaluated,
  nativeUVUnchanged:true,
  persistedOnPart:true,
  undoCheckpoint:true,
  authoringFrameInverse:true,
  tiledImageDraws:25
}));
