#!/usr/bin/env node
/* Actual assembled §E DOM-disabled-state contract, not only a string check. */
'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2]||'dist/swrlz-forge-moba/index.html','utf8');
assert.match(html,/SWYRL_ENGINE_DEPLOY_MARKER: V11_506_UV_BUTTON_OWNERSHIP/);
function extract(start,end){
 const i=html.indexOf(start),j=html.indexOf(end,i+start.length);
 assert.ok(i>=0&&j>i,'missing assembled function '+start);
 return html.slice(i,j);
}
const native=['se336UVExport','se336UVImport','se336UVRemove','se336UVSurface','se336UVSurfaceInfo']
 .map(id=>({id,disabled:false}));
const foreign=['se356UVRefresh','se503AtlasPrepare','se503AtlasApply','se503AtlasDiscard','se503AtlasExport']
 .map(id=>({id,disabled:id!=='se503AtlasPrepare'&&id!=='se356UVRefresh'}));
const names={'#se336UVName':{textContent:''},'#se336UVHasPaint':{textContent:''}};
const uvRoot={
 querySelector:s=>names[s],
 querySelectorAll:s=>{
  if(s==='.se336-uv-actions > button')return native;
  if(s==='button')return native.concat(foreign);
  throw Error('Unexpected legacy selector: '+s);
 }
};
let hasRender=false,paint=false;
const se336=Function('document','se336SelectedMesh',extract('function se336UpdateUI() {','function se336InstallUI()')+
 '\nreturn se336UpdateUI;')(
  {getElementById:()=>uvRoot},
  ()=>hasRender?{part:{name:'Hat',uvPaintPNG:paint?'png':undefined}}:null
 );
const snapshot=()=>foreign.map(x=>x.disabled);
const baseline=snapshot();
se336();
assert.ok(native.every(x=>x.disabled),'native tools require rendered UV mesh');
assert.deepEqual(snapshot(),baseline,'nested controls must retain own disabled flags when no mesh is rendered');
hasRender=true;se336();
assert.ok(native.every(x=>x.id==='se336UVRemove'?x.disabled:!x.disabled));
assert.deepEqual(snapshot(),baseline,'nested buttons still untouched when native UI updates');
paint=true;se336();
assert.ok(native.every(x=>!x.disabled),'native remove enabled with painted texture');
assert.deepEqual(snapshot(),baseline);

const atlasTarget=Function('se336SelectedMesh','partById','selection',
 extract('const se503Target=','function se503Rigged')+'return se503Target;')(
  ()=>null,id=>id==='hat'?{id:'hat',kind:'topologyMesh'}:null,'hat'
 );
assert.equal(atlasTarget().part.kind,'topologyMesh');
assert.equal(atlasTarget().mesh,null);
const rendered={part:{id:'hat',kind:'topologyMesh'},mesh:{geometry:{}}};
const atlasTargetRendered=Function('se336SelectedMesh','partById','selection',
 extract('const se503Target=','function se503Rigged')+'return se503Target;')(
 ()=>rendered,()=>{throw Error('should not need fallback');},'hat'
 );
assert.strictEqual(atlasTargetRendered(),rendered);

const wrapper=extract('se503Refresh=function(...args){','const topologyTypes=');
for(const kind of ['ready','native','textured-copy','reuse','auto-select','blocked']){
 const prepare={disabled:true,textContent:'',title:''};
 const status={textContent:''};
 const root={querySelector:s=>s==='#se503AtlasPrepare'?prepare:
   s==='#se503AtlasStatus'?status:null};
 const refresh=Function('priorUVRefresh','inspect','document','se503Preview',
  'let se503Refresh;'+wrapper+'return se503Refresh;')(
   ()=>{prepare.disabled=true;return 'updated';},
   ()=>({kind,reason:'Choose which mesh to edit'}),
   {getElementById:()=>root},
   null
  );
 assert.equal(refresh(),'updated');
 assert.equal(prepare.disabled,false,'Preview must remain actionable: '+kind);
 if(kind==='blocked')assert.match(status.textContent,/Choose which mesh to edit/);
 if(kind==='native')assert.match(prepare.textContent,/Make editable/);
}
console.log('SE506_UV_BUTTON_OWNERSHIP_PASS',JSON.stringify({
 nativeButtons:native.length,nestedButtons:foreign.length,
 planStatesTested:6,renderedMeshNotRequiredForTopologyPreview:true
}));
