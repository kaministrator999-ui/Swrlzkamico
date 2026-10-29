// §E v11.28: bounded parametric density planning; no arbitrary vertex-count
// promises and no conflation between editable source density and runtime LOD.
// The generated result is measured through the native geometry generator.
const atelierDensityPresets=Object.freeze({
 blockout:.25,preview:.5,working:1,high:1.5
});
function atelierDensityEligible(p){
 return !!p&&['sphere','loft'].includes(p.kind);
}
function atelierDensityPlan(part,u,v){
 if(!atelierDensityEligible(part)||!Number.isInteger(u)||!Number.isInteger(v)||
    u<16||u>256||v<12||v>192||u*v>42000)
   return {ok:false,reason:'U must be 16–256, V 12–192 and U×V ≤42,000'};
 const candidate={...part,meshDensity:{u,v},sculptVertexEdits:undefined};
 if(!checkPart(candidate))return {ok:false,reason:'Native part validation rejected the proposed source density'};
 const original=geometry(part),test=geometry(candidate);
 try{
   if(!original?.attributes?.position||!test?.attributes?.position)
     return {ok:false,reason:'No generated source mesh'};
   const measure=g=>({vertices:g.attributes.position.count,
     triangles:Math.floor((g.index?.count||g.attributes.position.count)/3)});
   const before=measure(original),after=measure(test);
   return {ok:true,before,after,u,v,clearsIndexedEdits:!!part.sculptVertexEdits?.length,
     preservesBrushes:!!part.sculptBrushes?.length,kind:part.kind};
 }finally{
   original?.dispose();test?.dispose();
 }
}
function atelierSculptDensityRefresh(){
 const p=partById(selection),pane=$m('SculptDensityTools');
 if(!pane)return;
 pane.hidden=!atelierDensityEligible(p);
 if(!atelierDensityEligible(p))return;
 $m('SculptDensityPreset').value='custom';
 $m('SculptDensityBudget').textContent='Preview selected-object U/V sampling before pressing Re-sample vertex grid. This is editable density, not runtime LOD.';
}
function atelierSculptDensityInstall(){
 const id=s=>$m('SculptDensity'+s);
 const preset=id('Preset');
 preset.addEventListener('change',()=>{
   const p=partById(selection),factor=atelierDensityPresets[preset.value];
   if(!atelierDensityEligible(p)||!factor)return;
   const base=atelierSculptResolution(p);
   const u=Math.min(256,Math.max(16,Math.round((base[0]||64)*factor)));
   const v=Math.min(192,Math.max(12,Math.round((base[1]||48)*factor)));
   $m('SculptBrushGridU').value=String(u);
   $m('SculptBrushGridV').value=String(v);
   id('Budget').textContent='Preset '+preset.value+' populated exact grid dimensions '+u+' × '+v+
     '. Check measured geometry before applying. No native changes made.';
 });
 id('Preview').addEventListener('click',()=>{
   const p=partById(selection);
   const u=Number($m('SculptBrushGridU').value),v=Number($m('SculptBrushGridV').value);
   const result=atelierDensityPlan(p,u,v);
   if(!result.ok){
     id('Budget').textContent='Density preview rejected: '+result.reason+'. Source unchanged.';
     return;
   }
   const count=v=>v.toLocaleString();
   id('Budget').textContent='Measured native base · '+count(result.before.vertices)+' → '+
     count(result.after.vertices)+' vertex slots; '+
     count(result.before.triangles)+' → '+count(result.after.triangles)+
     ' triangles at U '+u+' × V '+v+'.'+
     (result.clearsIndexedEdits?' WARNING: Apply clears source-indexed vertex edits; export backup first.':'')+
     ' Existing brush strokes remain. Preview makes no edit.';
 });
}
