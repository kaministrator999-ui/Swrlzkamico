const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const file=path.resolve(__dirname,'../runtime/model_uv_heatmap_export_v11_501.js');
const source=fs.readFileSync(file,'utf8');
class Canvas {
 constructor(){this.width=0;this.height=0;this.ops=[];}
 getContext(){
  const ops=this.ops;
  return new Proxy({}, {get:(_,k)=>{
   if(k==='canvas')return this;
   return (...args)=>ops.push([k,...args]);
  },set:(_,k,v)=>{ops.push(['set:'+k,v]);return true;}});
 }
}
const part={id:'hat',name:'Sorting Hat',uvArtMarker:{version:1,centerUV:[.25,.75],angleDeg:30,scale:1.5},uvPaintPNG:'data:image/png;base64,AAAA',uvPaintOffset:[.11,-.22],uvPaintRepeat:[.87,1]};
const mesh={geometry:{id:'one-mesh'},matrixWorld:{elements:Array(16).fill(1)},updateWorldMatrix(){}};
const target={part,mesh};
const context={
 document:{getElementById:()=>null,createElement:tag=>{assert.equal(tag,'canvas');return new Canvas();}},
 se336SelectedMesh:()=>target,se366Marker:p=>p.uvArtMarker,
 se356UVPin:null,se356UVRender:()=>{},se356UVInstallPreview:()=>{},refreshInspector:()=>{},
 se356UVResolve:()=>{},se366SaveMarker:()=>{},
 se356UVPaintImage:(_ctx,_img,p,size)=>{assert.equal(p,part);assert.ok(size>=256);context.paintCalls++;},
 se336UVLayout:()=>({triangles:1,vertices:3}),
 se469Math:{measure:(geo,matrix,maxFaces)=>({triangles:1,sampled:1,faces:[{uv:[0,0,1,0,0,1],ratio:1.8}],maxFaces})},
 se356UVPopupVisible:()=>false,se356UVPreviewRoot:()=>null,
 status:()=>{},window:{},Image:class{},Math,JSON,Number,
 paintCalls:0,
};
vm.createContext(context);
vm.runInContext(source+'\nglobalThis.se501TestAPI=se501UV;',context,{filename:file});
const api=context.se501TestAPI;
assert.equal(api.anchor(target).u,.25);
assert.equal(api.anchor(target).v,.75);
assert.equal(api.anchor(target).angleDeg,30);
assert.equal(api.anchor(target).scale,1.5);
context.se356UVPin={id:'hat',u:.7,v:.8};
assert.equal(api.anchor(target).u,.7);
assert.equal(api.anchor(target).angleDeg,0);
const before=JSON.stringify(part);
const report=api.measure(target,false);
assert.equal(report.maxFaces,6000);
const heat=api.compose(target,512,report,'heat',null,api.anchor(target),true);
assert.ok(heat.ops.some(x=>x[0]==='rotate'));
assert.equal(context.paintCalls,0);
const both=api.compose(target,512,report,'overlay',{width:512},api.anchor(target),true);
assert.ok(both.ops.some(x=>x[0]==='drawImage'));
assert.equal(context.paintCalls,1);
assert.equal(JSON.stringify(part),before,'Diagnostics must never alter the source mesh payload');
console.log('SE501_CENTER_AND_TEXTURE_OVERLAY_OK');
