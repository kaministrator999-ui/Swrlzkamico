// §E v11.49 — real source-UV diagnostics and bounded planar UV reprojection.
// This is an opt-in destructive edit to the baked COPY's UV coordinates,
// never a repair of arbitrary curved/overlapping UV atlases.
function atelierUVInspect(part){
 if(part?.kind!=='topologyMesh'||!atelierTopologyValid(part))
  return {ok:false,reason:'Select a valid saved indexed mesh'};
 const t=part.topologyMesh,count=t.indices.length/3;
 let collapsed=0,flipped=0,good=0,totalWorld=0,totalUV=0;
 let firstSign=0,minScale=Infinity,maxScale=0;
 for(let f=0;f<count;f++){
  const ids=t.indices.slice(f*3,f*3+3);
  const v=ids.map(i=>t.positions.slice(3*i,3*i+3)),
      u=ids.map(i=>t.uvs.slice(2*i,2*i+2));
  const ab=v[1].map((x,i)=>x-v[0][i]),
    ac=v[2].map((x,i)=>x-v[0][i]);
  const n=[
   ab[1]*ac[2]-ab[2]*ac[1],
   ab[2]*ac[0]-ab[0]*ac[2],
   ab[0]*ac[1]-ab[1]*ac[0]];
  const world=Math.hypot(...n)/2;
  const signed=((u[1][0]-u[0][0])*(u[2][1]-u[0][1])-
     (u[1][1]-u[0][1])*(u[2][0]-u[0][0]))/2;
  if(world<=1e-12)return {ok:false,reason:'Zero-area 3D source triangle'};
  totalWorld+=world;totalUV+=Math.abs(signed);
  if(Math.abs(signed)<1e-12){collapsed++;continue;}
  const sign=Math.sign(signed);
  if(firstSign===0)firstSign=sign;
  else if(sign!==firstSign)flipped++;
  const scale=Math.sqrt(Math.abs(signed)/world);
  minScale=Math.min(minScale,scale);maxScale=Math.max(maxScale,scale);
  good++;
 }
 return {ok:true,triangles:count,collapsedUVFaces:collapsed,
  oppositeUVFaces:flipped,noncollapsedFaces:good,
  worldArea:totalWorld,uvArea:totalUV,
  maxLocalScaleVariation:good?maxScale/Math.max(minScale,1e-12):null};
}
function atelierUVReprojectCandidate(part,plane,mirrorU=false){
 const existing=atelierUVInspect(part);
 if(!existing.ok)return existing;
 if(!['XY','XZ','YZ'].includes(plane)||typeof mirrorU!=='boolean')
  return {ok:false,reason:'Choose a supported planar UV direction'};
 const src=part.topologyMesh,axes={
  XY:[0,1],XZ:[0,2],YZ:[1,2]}[plane],vCount=src.positions.length/3;
 const xs=[],ys=[];
 for(let i=0;i<vCount;i++){
  xs.push(src.positions[i*3+axes[0]]);
  ys.push(src.positions[i*3+axes[1]]);
 }
 const loX=Math.min(...xs),hiX=Math.max(...xs),
   loY=Math.min(...ys),hiY=Math.max(...ys);
 if(hiX-loX<1e-7||hiY-loY<1e-7)
  return {ok:false,reason:'Mesh collapses in that planar view; choose another plane'};
 const uvs=[];
 for(let i=0;i<vCount;i++){
  const u=(xs[i]-loX)/(hiX-loX),v=(ys[i]-loY)/(hiY-loY);
  uvs.push(mirrorU?1-u:u,v);
 }
 const t={positions:src.positions.slice(),indices:src.indices.slice(),uvs};
 if(!atelierTopologyValid({kind:'topologyMesh',topologyMesh:t}))
  return {ok:false,reason:'Generated UV data violates native schema'};
 const after=atelierUVInspect({kind:'topologyMesh',topologyMesh:t});
 if(!after.ok||after.collapsedUVFaces||after.oppositeUVFaces)
  return {ok:false,reason:'Mesh folds, has near-edge-on triangles or projected UV overlaps; planar repair refused'};
 return {ok:true,data:t,before:existing,after,plane,mirrorU,
  dropsRuntimeLOD:!!part.runtimeLOD};
}
let atelierUVCandidate=null;
function atelierUVRefresh(){
 const p=partById(selection),panel=$m('UVTools');
 if(!panel)return;
 panel.hidden=p?.kind!=='topologyMesh';
 if(p?.kind!=='topologyMesh'){atelierUVCandidate=null;return;}
 const info=atelierUVInspect(p);
 $m('UVStatus').textContent=info.ok?(
  'Actual '+info.triangles+' indexed faces · '+info.collapsedUVFaces+
  ' zero-area UV triangles · '+info.oppositeUVFaces+
  ' reverse-oriented UV triangles · relative face scale range ×'+
  (info.maxLocalScaleVariation===null?'not measurable':info.maxLocalScaleVariation.toFixed(3))+
  '. This is a diagnostic; UV atlas overlap is not automatically checked.'
 ):info.reason;
}
function atelierUVInstall(){
 const el=k=>$m('UV'+k);
 el('Inspect').addEventListener('click',()=>{
  atelierUVRefresh();
  status('Current indexed mesh UV area and orientation analyzed without mutation.');
 });
 el('Preview').addEventListener('click',()=>{
  const p=partById(selection),
    x=atelierUVReprojectCandidate(p,el('Plane').value,el('Mirror').checked);
  atelierUVCandidate=x.ok?{...x,id:p.id,baseline:JSON.stringify(p.topologyMesh)}:null;
  if(!x.ok){status('Planar UV repair unavailable: '+x.reason,true);return;}
  el('Status').textContent='Preview '+x.plane+' normalized UV: collapsed faces '+
    x.before.collapsedUVFaces+' → '+x.after.collapsedUVFaces+
    ', reversed local UV orientation '+x.before.oppositeUVFaces+
    ' → '+x.after.oppositeUVFaces+'. UVs change ONLY upon Apply.';
  status('Previewed real planar UV coordinates. Existing texture placement may change.');
 });
 el('Apply').addEventListener('click',()=>{
  const p=partById(selection),result=atelierUVCandidate;
  if(!p||!result?.ok||p.id!==result.id||
   JSON.stringify(p.topologyMesh)!==result.baseline){
   status('Preview the current same indexed UV data first.',true);return;
  }
  const next={...p,topologyMesh:result.data};
  delete next.runtimeLOD;
  if(!checkPart(next)){status('UV reprojection rejected by native validation.',true);return;}
  checkpoint();p.topologyMesh=result.data;delete p.runtimeLOD;
  atelierUVCandidate=null;signalEdited();select(p.id);
  status('Reprojected native UV coordinates in '+result.plane+
    '; saved prior UV atlas in Undo. Other procedural assets untouched.');
 });
}
