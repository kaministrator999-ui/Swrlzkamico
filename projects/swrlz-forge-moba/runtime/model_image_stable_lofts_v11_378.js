/* SE378_STABLE_LOFT_START
 * Opt-in native loft blockout from user-edited v11.377 silhouettes.
 * No semantic part recognition, hidden geometry reconstruction or UV mapping.
 */
const se378Round=n=>Number(n.toFixed(4));
const se378Clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function se378Primary(view){
 return se377.regions.filter(r=>r.view===view&&r.kind==='silhouette'&&r.visible!==false&&r.points.length>=3)
   .sort((a,b)=>(b.size||0)-(a.size||0))[0]||null;
}
function se378Bounds(region){
 const x=region.points.map(p=>p[0]),y=region.points.map(p=>p[1]);
 return {left:Math.min(...x),right:Math.max(...x),top:Math.min(...y),bottom:Math.max(...y)};
}
function se378Span(region,t){
 if(!region)return null;
 const b=se378Bounds(region),y=b.top+(b.bottom-b.top)*se378Clamp(t,.005,.995);
 const hits=[],points=region.points;
 for(let i=0;i<points.length;i++){
  const a=points[i],c=points[(i+1)%points.length];
  if((a[1]<=y&&c[1]>y)||(c[1]<=y&&a[1]>y))
   hits.push(a[0]+(y-a[1])*(c[0]-a[0])/(c[1]-a[1]));
 }
 if(hits.length<2)return null;
 const lo=Math.min(...hits),hi=Math.max(...hits);
 return {center:(lo+hi)/2,width:hi-lo};
}
function se378Rows(front,side,right){
 const f=se378Bounds(front),fw=f.right-f.left,fh=f.bottom-f.top;
 if(fw<.025||fh<.12)throw Error('Front contour is too small; re-trace with the guides.');
 const raw=Array.from({length:37},(_,i)=>{
  const t=i/36,s=se378Span(front,t);
  if(!s)throw Error('Front contour has missing rows; adjust its editable outline.');
  const depths=[side,right].filter(Boolean).map(v=>{
   const b=se378Bounds(v),p=se378Span(v,t);
   return p&&b.right>b.left?p.width/(b.right-b.left):null;
  }).filter(v=>v!==null);
  return {t,x:se378Clamp((s.center-(f.left+f.right)/2)/fw*1.2,-.15,.15),
    radius:se378Clamp(s.width/fw*1.08,.045,1.12),
    depth:depths.length?depths.reduce((a,b)=>a+b)/depths.length:.58};
 });
 return raw.map((r,i)=>{
  const nearby=raw.slice(Math.max(0,i-2),Math.min(raw.length,i+3));
  const avg=k=>nearby.reduce((a,b)=>a+b[k],0)/nearby.length;
  return {...r,x:avg('x'),radius:avg('radius'),depth:avg('depth')};
 });
}
function se378Blockout(){
 if(!se375Canvas)throw Error('Upload the reference image first.');
 const front=se378Primary('Front');
 if(!front)throw Error('Trace a visible Front silhouette before building 3D.');
 const left=se378Primary('Left'),right=se378Primary('Right');
 const rows=se378Rows(front,left,right),sample=se375Sample(),bounds=se378Bounds(front);
 const bands=[[0,10,'Upper form · hood/head estimate'],[10,23,'Middle form · robe estimate'],
              [23,36,'Lower form · skirt estimate']];
 const parts=bands.map(([start,end,label],index)=>{
  const profile=rows.slice(start,end+1).map(r=>({...r}));
  if(index)profile[0].t+=.002;
  if(index<2)profile[profile.length-1].t-=.002;
  const z=se378Clamp(.50+profile.reduce((a,r)=>a+r.depth,0)/profile.length*.40,.57,.90);
  const top=bounds.top+(bounds.bottom-bounds.top)*start/36;
  const bottom=bounds.top+(bounds.bottom-bounds.top)*end/36;
  return {op:'mesh.add',kind:'loft',
   name:'Reference blockout '+(index+1)+' · '+label,
   position:[0,0,0],rotation:[0,0,0],scale:[1,1,se378Round(z)],
   path:profile.map(r=>[se378Round(r.x),se378Round(.15+4.15*(1-r.t)),0]),
   radii:profile.map(r=>se378Round(r.radius)),
   segments:24,color:sample.dominant(sample.rects[0],top,bottom),material:'matte'};
 });
 // The unmodified segmentation may include a detached staff. Only add one if
 // it is clearly tall, slender, and outside the main front silhouette.
 if(se375Id('Prop')?.checked){
  const props=se377.regions.filter(r=>r.view==='Front'&&r.kind==='silhouette'&&r.id!==front.id&&r.visible!==false);
  for(const region of props){
   const b=se378Bounds(region),width=b.right-b.left,height=b.bottom-b.top,fw=bounds.right-bounds.left;
   if(width<.004||height<.13||height/width<2||width>fw*.42||
      !(b.right<bounds.left+fw*.15||b.left>bounds.right-fw*.15))continue;
   const path=[],radii=[];
   for(let i=0;i<15;i++){
    const t=i/14,shape=se378Span(region,t);
    if(!shape)continue;
    path.push([se378Round(se378Clamp((shape.center-(bounds.left+bounds.right)/2)/fw*2.2,-3,3)),
      se378Round(.15+4.15*(1-(b.top+(b.bottom-b.top)*t-bounds.top)/(bounds.bottom-bounds.top))),0]);
    radii.push(se378Round(se378Clamp(shape.width/fw*.58,.025,.09)));
   }
   if(path.length>=10){parts.push({op:'mesh.add',kind:'loft',
    name:'Reference blockout · detached prop',position:[0,0,0],rotation:[0,0,0],
    scale:[1,1,1],path,radii,segments:12,color:'#957f9c',material:'matte'});break;}
  }
  // Left-side staff can fall just OUTSIDE the Front view guide. Preserve
  // the older independent narrow-prop scan instead of silently losing it.
  if(parts.length===3){
   const sample=se375Sample(),box={x:Math.max(0,se375Guides.front-.124),y:.20,w:.054,h:.42};
   const hits=Array.from({length:16},(_,i)=>{
    const y=.225+(.61-.225)*i/15;
    return {y,shape:sample.scan(box,y)};
   }).filter(p=>p.shape&&p.shape.width<se375Canvas.width*.025);
   if(hits.length>=11){
    const fw=(bounds.right-bounds.left)*se375Canvas.width;
    const cx=(bounds.left+bounds.right)*se375Canvas.width/2;
    const path=hits.map(p=>[se378Round(se378Clamp((p.shape.center-cx)/fw*2.2,-3,3)),
      se378Round(.15+4.15*(se375Guides.lower-p.y)/(se375Guides.lower-se375Guides.upper)),0]);
    const radii=hits.map(p=>se378Round(se378Clamp(p.shape.width/fw*.40,.025,.09)));
    parts.push({op:'mesh.add',kind:'loft',name:'Reference blockout · detached prop',
     position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],
     path,radii,segments:12,color:'#957f9c',material:'matte'});
   }
  }
 }
 return parts;
}
// Native ModelAtelier.chatAction still owns validation, history, saved data and
// the blank-project protection of se375Run.
se375Blockout=se378Blockout;
const se378InstallOriginal=se375Install;
se375Install=function(){
 se378InstallOriginal();
 const button=se375Id('Generate');
 if(!button||button.dataset.se378)return;
 button.dataset.se378='1';
 button.textContent='Build improved 3D from 2D outlines';
 const note=document.createElement('small');
 note.style.cssText='display:block;color:#d9ceef;margin:6px 0;line-height:1.4';
 note.textContent='Uses your current edited front silhouette; side views guide depth. Three aligned native lofts, optional detached prop. No automatic anatomical recognition. Use a separate blank Model project to compare both experiments.';
 button.insertAdjacentElement('afterend',note);
};
queueMicrotask(se375Install);
/* SE378_STABLE_LOFT_END */
