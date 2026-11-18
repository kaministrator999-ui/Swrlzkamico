/* SE503_UV_ISLAND_UI_START
   Opt-in UV panel atlas: preview -> inspect -> apply. Never change model
   geometry or texture before an explicit Apply. */
let se503Preview=null,se503Tweaks={},se503Preset='panels-rim',se503Brim=.18;
const se503Target=()=>se336SelectedMesh();
function se503Rigged(p){
 return Object.keys(p).some(k=>/^(skin|bone|rig|vertexweight|morph|clothweights)/i.test(k));
}
function se503Candidate() {
 const target=se503Target();
 if(!target?.part||target.part.kind!=='topologyMesh')
  throw Error('Select an editable indexed topology mesh (use Make editable copy if necessary).');
 const part=target.part;
 if(se503Rigged(part))throw Error('This mesh has rig/weight data; unwrap the unrigged source before binding bones.');
 if(part.runtimeLOD?.enabled)
  throw Error('Disable the active runtime LOD before re-unwrapping its UV seams.');
 const before=JSON.stringify(part.topologyMesh);
 const plan=se503AtlasMath.unwrap(part.topologyMesh,{
  preset:se503Preset,brimFraction:se503Brim,transforms:se503Tweaks
 });
 const proposed={...part,topologyMesh:plan.data};
 delete proposed.runtimeLOD;
 // Old texture maps another atlas; the new UVs cannot safely reuse it.
 delete proposed.uvPaintPNG;
 delete proposed.uvPaintRepeat;
 delete proposed.uvPaintOffset;
 delete proposed.uvArtMarker;
 if(!checkPart(proposed))throw Error('New UV layout does not pass saved-project mesh validation.');
 let anchor=null;
 const oldPin=se356UVPin?.id===part.id?se356UVPin:null;
 const m=se366Marker(part);
 const oldCenter=oldPin?[oldPin.u,oldPin.v]:m?.centerUV;
 if(oldCenter)anchor=se503AtlasMath.remapCenter(part.topologyMesh,plan,...oldCenter);
 if(anchor&&m)proposed.uvArtMarker={version:1,centerUV:anchor.slice(),angleDeg:0,scale:1};
 return {id:part.id,part,modelRef:model(),before,plan,proposed,anchor,
  oldTexture:!!part.uvPaintPNG,oldMarker:!!oldCenter};
}
function se503ShowPreview(info){
 const root=document.getElementById('se503AtlasTool');
 if(!root)return;
 const cv=root.querySelector('#se503AtlasCanvas'),ctx=cv.getContext('2d');
 const s=cv.width;
 ctx.clearRect(0,0,s,s);
 ctx.fillStyle='#152337';ctx.fillRect(0,0,s,s);
 ctx.lineWidth=1;
 for(const face of info.plan.faces){
  const pts=face.uv;
  ctx.beginPath();
  ctx.moveTo(pts[0][0]*s,(1-pts[0][1])*s);
  ctx.lineTo(pts[1][0]*s,(1-pts[1][1])*s);
  ctx.lineTo(pts[2][0]*s,(1-pts[2][1])*s);
  ctx.closePath();
  ctx.strokeStyle=info.plan.stats.find(x=>x.id===face.group)?.color||'#d8e7f0';
  ctx.globalAlpha=.33;ctx.stroke();
 }
 ctx.globalAlpha=1;
 ctx.font='600 15px system-ui';
 for(const x of info.plan.stats){
  const [u0,v0,u1,v1]=x.rect;
  ctx.strokeStyle=x.color;ctx.lineWidth=2;ctx.strokeRect(u0*s,(1-v1)*s,(u1-u0)*s,(v1-v0)*s);
  ctx.fillStyle='#fff';ctx.fillText(x.name,u0*s+8,(1-v1)*s+20);
 }
 if(info.anchor) {
  ctx.strokeStyle='#faf1bb';ctx.lineWidth=3;
  const x=info.anchor[0]*s,y=(1-info.anchor[1])*s;
  ctx.beginPath();ctx.arc(x,y,8,0,Math.PI*2);ctx.moveTo(x-12,y);ctx.lineTo(x+12,y);
  ctx.moveTo(x,y-12);ctx.lineTo(x,y+12);ctx.stroke();
 }
 cv.hidden=false;
 const m=info.plan,summary=root.querySelector('#se503AtlasStatus');
 const risk=m.collapsed?' WARNING: '+m.collapsed+' near-flat UV triangles. Inspect before applying.':'';
 summary.textContent=m.vertices+' vertices ('+m.duplicatedVertices+' seam duplicates) · '+
  m.triangles+' triangles · '+m.stats.length+' islands. '+m.stats.map(x=>x.name+': '+
  x.triangles).join(' | ')+'.'+risk+
  (info.oldTexture?' Existing painted texture will be detached on Apply; Undo restores it.':'')+
  (info.oldMarker&&!info.anchor?' Re-pick the center marker after Apply.':'');
}
function se503Refresh(){
 const root=document.getElementById('se503AtlasTool');if(!root)return;
 const target=se503Target(),available=target?.part?.kind==='topologyMesh'&&!se503Rigged(target.part);
 const preserved=!!se503Preview&&target?.part===se503Preview.part&&model()===se503Preview.modelRef;
 if(se503Preview&&!preserved)se503Preview=null;
 root.querySelector('#se503AtlasPrepare').disabled=!available;
 root.querySelector('#se503AtlasApply').disabled=!preserved;
 root.querySelector('#se503AtlasExport').disabled=!preserved;
 root.querySelector('#se503AtlasDiscard').disabled=!preserved;
 if(!preserved&&!available)
  root.querySelector('#se503AtlasStatus').textContent=
   'Select an unrigged editable topology mesh; procedural meshes can use Make editable copy first.';
}
function se503Prepare(){
 const root=document.getElementById('se503AtlasTool');
 try{
  const p=se503Candidate();se503Preview=p;se503ShowPreview(p);se503Refresh();
  status('Previewed '+p.plan.stats.length+' UV islands; model and texture unchanged. Apply when ready.');
 }catch(e){se503Preview=null;se503Refresh();root.querySelector('#se503AtlasStatus').textContent=e.message;
  status('UV island preview: '+e.message,true);}
}
function se503Apply(){
 const result=se503Preview,target=se503Target();
 if(!result||!target||target.part!==result.part||
    target.part.id!==result.id||model()!==result.modelRef||
    JSON.stringify(target.part.topologyMesh)!==result.before){
  se503Preview=null;se503Refresh();status('Mesh changed since UV preview; preview it again.',true);return;
 }
 if(!checkPart(result.proposed)){status('Saved-model validation rejected the UV atlas.',true);return;}
 checkpoint();
 const p=target.part;
 p.topologyMesh=result.plan.data;
 delete p.runtimeLOD;
 // The old pixels cannot be mapped to this different atlas without repainting.
 delete p.uvPaintPNG;delete p.uvPaintOffset;delete p.uvPaintRepeat;
 delete p.uvArtMarker;
 if(result.proposed.uvArtMarker)p.uvArtMarker=result.proposed.uvArtMarker;
 if(se356UVPin?.id===p.id){
  se356UVPin=result.anchor?{id:p.id,u:result.anchor[0],v:result.anchor[1]}:null;
 }
 se503Preview=null;
 signalEdited();select(p.id);se356UVPreviewSchedule();
 se503Refresh();
 status('Saved front/back UV islands with '+result.plan.duplicatedVertices+
  ' seam vertices. Export the new UV guide and paint it as one atlas; Undo restores the old texture and UVs.');
}
function se503ExportGuide(){
 const result=se503Preview;if(!result)return;
 const cv=document.createElement('canvas');
 cv.width=cv.height=2048;
 const ctx=cv.getContext('2d');
 ctx.clearRect(0,0,cv.width,cv.height);
 ctx.strokeStyle='#21e6ec';ctx.lineWidth=2;
 for(const face of result.plan.faces){
  ctx.beginPath();const a=face.uv;
  ctx.moveTo(a[0][0]*2048,(1-a[0][1])*2048);
  ctx.lineTo(a[1][0]*2048,(1-a[1][1])*2048);
  ctx.lineTo(a[2][0]*2048,(1-a[2][1])*2048);
  ctx.closePath();ctx.stroke();
 }
 se336SaveCanvas(cv,result.part.name+'-NEW-ATLAS-GUIDE-2048.png');
 status('Exported 2048px candidate UV guide. The model still uses the old UVs until Apply.');
}
function se503AdjustFromUI(){
 const root=document.getElementById('se503AtlasTool');
 const group=Number(root.querySelector('#se503Island').value);
 const get=id=>Number(root.querySelector('#'+id).value);
 se503Tweaks[group]={angle:get('se503Angle'),scale:get('se503Scale'),
  shiftU:get('se503ShiftU'),shiftV:get('se503ShiftV')};
 for(const [id,suffix] of [['se503Angle','°'],['se503Scale','×'],
  ['se503ShiftU',''],['se503ShiftV','']])
  root.querySelector('#'+id+'Value').textContent=get(id).toFixed(id==='se503Angle'?0:2)+suffix;
 se503Prepare();
}
function se503Install(){
 const host=se356UVPreviewRoot();
 if(!host||host.querySelector('#se503AtlasTool'))return;
 const root=document.createElement('section');root.id='se503AtlasTool';
 root.className='se503-atlas';
 root.innerHTML='<details><summary>New UV islands · front/back atlas (experimental)</summary>'+
 '<p>Preview true per-vertex UV changes on one mesh. Front and back occupy separate large areas; brim and underside use smaller islands. Existing artwork cannot automatically follow the new UVs. Folded surfaces may still overlap within an island.</p>'+
 '<label>Projection <select id="se503Preset"><option value="panels-rim">Front / back / brim / underside</option><option value="panels">Front and back only</option></select></label>'+
 '<label>Rim height <input id="se503Brim" type="range" min="8" max="34" value="18" step="1"><output id="se503BrimValue">18%</output></label>'+
 '<label>Edit island <select id="se503Island"><option value="0">Front</option><option value="1">Back</option><option value="2">Brim</option><option value="3">Underside</option></select></label>'+
 '<div class="se503-grid">'+
 '<label>Rotation <input type="range" id="se503Angle" min="-40" max="40" value="0"><output id="se503AngleValue">0°</output></label>'+
 '<label>Scale <input type="range" id="se503Scale" min="0.55" max="1.3" step="0.01" value="1"><output id="se503ScaleValue">1×</output></label>'+
 '<label>Move U <input type="range" id="se503ShiftU" min="-0.1" max="0.1" step="0.005" value="0"><output id="se503ShiftUValue">0</output></label>'+
 '<label>Move V <input type="range" id="se503ShiftV" min="-0.1" max="0.1" step="0.005" value="0"><output id="se503ShiftVValue">0</output></label></div>'+
 '<div class="se503-actions"><button id="se503AtlasPrepare" type="button">Preview UV atlas</button>'+
 '<button id="se503AtlasApply" type="button" disabled>Apply UVs</button>'+
 '<button id="se503AtlasDiscard" type="button" disabled>Cancel</button>'+
 '<button id="se503AtlasExport" type="button" disabled>Export candidate guide</button></div>'+
 '<canvas id="se503AtlasCanvas" width="768" height="768" hidden></canvas>'+
 '<p id="se503AtlasStatus" role="status">Select an editable indexed mesh to begin.</p>'+
 '<p>Applying updates indexed UV seam data only, invalidates any LOD, and detaches the old painted PNG. Use Undo or a prior project revision to restore it. Repaint using the new guide. No 3D sculpt positions are changed.</p>'+
 '</details>';
 host.append(root);
 root.querySelector('#se503AtlasPrepare').addEventListener('click',se503Prepare);
 root.querySelector('#se503AtlasApply').addEventListener('click',se503Apply);
 root.querySelector('#se503AtlasDiscard').addEventListener('click',()=>{
  se503Preview=null;root.querySelector('#se503AtlasCanvas').hidden=true;
  root.querySelector('#se503AtlasStatus').textContent='Preview cancelled. Model unchanged.';
  se503Refresh();
 });
 root.querySelector('#se503AtlasExport').addEventListener('click',se503ExportGuide);
 root.querySelector('#se503Preset').addEventListener('change',e=>{
  se503Preset=e.target.value;se503Prepare();
 });
 root.querySelector('#se503Brim').addEventListener('input',e=>{
  se503Brim=Number(e.target.value)/100;
  root.querySelector('#se503BrimValue').textContent=e.target.value+'%';se503Prepare();
 });
 const showGroup=()=>{
  const g=Number(root.querySelector('#se503Island').value),v=se503Tweaks[g]||{};
  for(const [id,key,def] of [['se503Angle','angle',0],['se503Scale','scale',1],
   ['se503ShiftU','shiftU',0],['se503ShiftV','shiftV',0]]){
   root.querySelector('#'+id).value=v[key]??def;
   root.querySelector('#'+id+'Value').textContent=String(v[key]??def);
  }
 };
 root.querySelector('#se503Island').addEventListener('change',showGroup);
 for(const key of ['se503Angle','se503Scale','se503ShiftU','se503ShiftV'])
  root.querySelector('#'+key).addEventListener('change',se503AdjustFromUI);
 se503Refresh();
}
const se503PriorUVInstall=se356UVInstallPreview;
se356UVInstallPreview=function(){
 const result=se503PriorUVInstall.apply(this,arguments);se503Install();return result;
};
const se503PriorInspectorRefresh=refreshInspector;
refreshInspector=function(){
 const result=se503PriorInspectorRefresh.apply(this,arguments);se503Refresh();return result;
};
window.SWYRLZ_E_UV_ISLANDS_503=Object.freeze({
 preview:se503Prepare,apply:se503Apply,cancel:()=>{se503Preview=null;se503Refresh();},
 state:()=>({candidate:!!se503Preview,triangles:se503Preview?.plan.triangles||0,
  vertices:se503Preview?.plan.vertices||0,collapsed:se503Preview?.plan.collapsed||0})
});
/* SE503_UV_ISLAND_UI_END */
