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
  se336SlideOffset(p){return Array.isArray(p?.uvPaintOffset)?p.uvPaintOffset.slice():[0,0]},
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
assert.equal(JSON.stringify(stored.uvArtMarker),JSON.stringify(part.uvArtMarker));
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

// Camera-relative front/top are inferred from actual triangle tangents AFTER
// mesh rotation, not from hardcoded +Z or a pre-assumed spherical UV quarter.
const base=[0,0,0],uv0=[0,0],uv1=[1,0],uv2=[0,1];
const angle=(p1,p2,right=[1,0,0],up=[0,1,0])=>
  api.angleFromView(base,p1,p2,uv0,uv1,uv2,right,up);
assert.equal(angle([1,0,0],[0,1,0]),0,'U/V aligned with camera');
assert.equal(angle([0,1,0],[-1,0,0]),-90,'Rotated mesh changes paint-up angle');
assert.equal(angle([-1,0,0],[0,-1,0]),-180,'Upside-down mesh should be rotated');
assert.equal(angle([1,0,0],[0,1,0],[0,-1,0],[1,0,0]),-90,'Rolled camera changes screen-up');
assert.equal(api.angleFromView(base,[1,0,0],[0,1,0],uv0,uv0,uv2,[1,0,0],[0,1,0]),null,
  'Degenerate triangle must be reported');
class Vec{
 constructor(x=0,y=0,z=0){this.x=x;this.y=y;this.z=z;}
 clone(){return new Vec(this.x,this.y,this.z);}
 addScaledVector(v,s){this.x+=v.x*s;this.y+=v.y*s;this.z+=v.z*s;return this;}
 sub(v){this.x-=v.x;this.y-=v.y;this.z-=v.z;return this;}
 lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z;}
 length(){return Math.sqrt(this.lengthSq());}
 normalize(){const d=this.length()||1;this.x/=d;this.y/=d;this.z/=d;return this;}
 setFromMatrixColumn(m,i){const v=m.columns[i];this.x=v[0];this.y=v[1];this.z=v[2];return this;}
 applyMatrix4(m){const {x,y,z}=this;this.x=m[0][0]*x+m[0][1]*y+m[0][2]*z;
   this.y=m[1][0]*x+m[1][1]*y+m[1][2]*z;
   this.z=m[2][0]*x+m[2][1]*y+m[2][2]*z;return this;}
 fromBufferAttribute(attr,i){const v=attr.vertices[i];this.x=v[0];this.y=v[1];this.z=v[2];return this;}
 toArray(){return [this.x,this.y,this.z];}
}
const rotationZ90=[[0,-1,0],[1,0,0],[0,0,1]];
const positions={count:3,vertices:[[0,0,0],[1,0,0],[0,1,0]]};
const tex={count:3,uvs:[[0,0],[1,0],[0,1]],getX(i){return this.uvs[i][0];},getY(i){return this.uvs[i][1];}};
const fakeMesh={
 geometry:{getAttribute(name){return name==='position'?positions:tex;},
   computeBoundingSphere(){this.boundingSphere={center:new Vec(0,0,0),radius:1};}},
 matrixWorld:rotationZ90,updateWorldMatrix(){},getWorldScale(v){v.x=1;v.y=1;v.z=1;return v;}
};
context.se336SelectedMesh=()=>({part,mesh:fakeMesh});
context.THREE={Vector3:Vec,Raycaster:class{
 intersectObject(mesh){assert.equal(mesh,fakeMesh);return [{uv:{x:.255555565,y:.71},face:{a:0,b:1,c:2}}];}
}};
context.camera={
 matrixWorld:{columns:[[1,0,0],[0,1,0],[0,0,1]]},
 updateWorldMatrix(){},getWorldPosition(v){v.x=0;v.y=0;v.z=4;return v;}
};
const beforeCheckpoints=checkpoints;
const initialOffset=part.uvPaintOffset=[.2494,-.0143];
api.autoAlignCamera();
assert.equal(checkpoints,beforeCheckpoints+1,'Auto-fit should commit one checkpoint');
assert(Math.abs(part.uvArtMarker.centerUV[0]-.255556)<1e-6,'Front centered from raycast');
assert.equal(part.uvArtMarker.angleDeg,-90,'Object roll handled in world tangent calculation');
assert.equal(JSON.stringify(part.uvPaintOffset),JSON.stringify(initialOffset),'Auto-fit must not silently alter original UV Slide');
const mapped=api.nativeToArt(...part.uvArtMarker.centerUV,part.uvArtMarker);
assert(Math.abs(mapped[0]-.5)<1e-9&&Math.abs(mapped[1]-.5)<1e-9,
 'The quarter-offset mage front should land at artwork image center');


const paintedOffset=[.2494,-.0143];
part.uvPaintPNG='data:image/png;base64,AAAA';
part.uvPaintOffset=paintedOffset.slice();
api.captureSlide();
assert(Math.abs(part.uvArtMarker.centerUV[0]-.2506)<1e-6,
  'A positive quarter-width texture offset makes source mesh front U≈0.25');
assert(Math.abs(part.uvArtMarker.centerUV[1]-.5143)<1e-6,
  'V correction should be captured consistently');
assert.equal(part.uvArtMarker.angleDeg,-90,
  'Capturing the prior slide should preserve previously oriented marker');
assert.equal(JSON.stringify(part.uvPaintOffset),JSON.stringify(paintedOffset),
  'Capture must not modify previous artwork or UV placement');

console.log('UV_MARKER_TESTS_OK',JSON.stringify({
  coordinateRoundTrips:evaluated,
  nativeUVUnchanged:true,
  persistedOnPart:true,
  undoCheckpoint:true,
  authoringFrameInverse:true,
  tiledImageDraws:25,
  cameraOrientationChecks:5,
  cameraAlignedRotatedMesh:true,
  sourceQuarterOffsetCentered:true,
  realSlideCapture:true
}));
