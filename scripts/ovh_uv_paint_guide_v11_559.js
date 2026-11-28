/* SE559: separate the actual paint atlas from island-identification badges. */
let se559Legend=null,se559LegendKey='';
function se559RegionInfo(t,r){
 const pos=t.mesh.geometry.getAttribute('position');
 const descriptions=['Torso front','Torso back','Pelvis underside','Head front','Head back','Crown cap','Arm -X end cap','Arm -X shell','Hand -X digit A','Hand -X digit B','Hand -X digit C','Hand -X digit D','Hand -X thumb','Arm +X end cap','Arm +X shell','Hand +X digit A','Hand +X digit B','Hand +X digit C','Hand +X digit D','Hand +X thumb','Leg -X / foot','Leg +X / foot'];
 const counts=[715,715,135,475,475,193,99,777,64,64,64,64,50,99,777,64,64,64,64,50,673,673];
 const named=t.part.id==='clean-topology-humanoid-base'&&r.groups.length===22&&r.groups.every((g,i)=>g.ids.size===counts[i]);
 return r.groups.map((g,i)=>{
  const centerZ=[...g.ids].reduce((s,v)=>s+pos.getZ(v),0)/g.ids.size;
  let name=named?descriptions[i]:r.anatomical?se552Names[g.id]:'Island '+(i+1);
  if(named&&(i===0||i===1))name='Torso '+(centerZ>0?'front (+Z)':'back (-Z)');
  if(named&&(i===3||i===4))name='Head '+(centerZ>0?'front (+Z)':'back (-Z)');
  return {group:g,id:r.anatomical?g.id+1:i+1,name,color:se552Color(g,i,r.anatomical)};
 });
}
function se559Boundary(ctx,uv,faces,size){
 const edges=new Map(),point=v=>[uv.getX(v),uv.getY(v)],key=p=>p.map(x=>x.toFixed(6)).join(',');
 for(const f of faces)for(let i=0;i<3;i++){
  const a=point(f[i]),b=point(f[(i+1)%3]),ka=key(a),kb=key(b),k=ka<kb?ka+'|'+kb:kb+'|'+ka;
  if(edges.has(k))edges.get(k).n++;else edges.set(k,{a,b,n:1});
 }
 ctx.beginPath();
 for(const {a,b,n} of edges.values())if(n===1){ctx.moveTo(a[0]*size,(1-a[1])*size);ctx.lineTo(b[0]*size,(1-b[1])*size);}
 ctx.stroke();
}
function se559UpdateLegend(t,rows){
 if(!se559Legend?.isConnected)return;
 const key=t.part.id+'|'+rows.map(x=>[x.id,x.name,x.color].join(':')).join('|');
 if(key===se559LegendKey)return;
 se559LegendKey=key;
 const list=se559Legend.querySelector('[data-se559-list]');list.replaceChildren();
 for(const row of rows){
  const b=document.createElement('button');b.type='button';b.dataset.se559Island=String(row.id);
  const sw=document.createElement('span');sw.style.cssText='width:12px;height:12px;flex:none;border-radius:3px;background:'+row.color;
  const txt=document.createElement('span');txt.textContent=row.id+' · '+row.name;b.append(sw,txt);
  b.onclick=()=>{
   const target=se551Target();if(!target)return;
   const item=se559RegionInfo(target,se552Regions(target)).find(x=>x.id===row.id);
   if(!item)return;
   se551Selection={part:target.part,ids:[...item.group.ids]};se356UVPreviewSchedule();
   se559Legend.open=false;status('Selected UV island '+row.id+' · '+item.name);
  };list.append(b);
 }
 se559Legend.querySelector('summary').textContent='Island legend · '+rows.length;
}
se552DrawRegions=function(t,cv,exporting=false){
 const r=se552Regions(t),rows=se559RegionInfo(t,r),ctx=cv.getContext('2d'),size=cv.width;
 const selected=new Set(se551Selection?.part===t.part?se551Selection.ids:[]);
 ctx.save();
 for(const {group:g,color} of rows){
  ctx.fillStyle=color;ctx.globalAlpha=exporting?.45:selected.size&&[...g.ids].every(v=>selected.has(v))?.7:.32;
  for(const f of g.faces){ctx.beginPath();f.forEach((v,k)=>{const x=r.topo.uv.getX(v)*size,y=(1-r.topo.uv.getY(v))*size;k?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.closePath();ctx.fill();}
  ctx.globalAlpha=.9;ctx.strokeStyle=color;ctx.lineWidth=Math.max(1,size/900);se559Boundary(ctx,r.topo.uv,g.faces,size);
 }
 ctx.restore();if(!exporting)se559UpdateLegend(t,rows);return r.groups;
};
function se559ExportPaintGuide(){
 const t=se551Target();if(!t){status('Select a mesh to export its clean paint guide.');return;}
 const r=se552Regions(t),size=4096,cv=document.createElement('canvas');cv.width=cv.height=size;
 const ctx=cv.getContext('2d');ctx.strokeStyle='#181e29';ctx.lineWidth=3;ctx.lineJoin='round';
 for(const g of r.groups)se559Boundary(ctx,r.topo.uv,g.faces,size);
 cv.toBlob(blob=>{
  if(!blob){status('Unable to export paint guide.');return;}
  const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download='se-ai-paint-guide-4096.png';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
  status('4096² exact boundary guide exported · transparent, no labels, no triangulation. Keep all UV positions fixed.');
 },'image/png');
}
const se559OpenBase=se552Open;
se552Open=function(){
 se559OpenBase();
 const host=se552Portal?.host,controls=host?.children?.[1];if(!controls||controls.querySelector('[data-se559-legend]'))return;
 const regions=controls.querySelector('[data-se552-regions]');
 if(regions?.parentNode?.lastChild?.nodeType===3)regions.parentNode.lastChild.textContent=' UV island colors';
 const details=document.createElement('details');details.dataset.se559Legend='1';details.style.cssText='position:relative;flex:none';
 details.innerHTML='<summary style="cursor:pointer;padding:7px 9px;border:1px solid #658797;border-radius:6px">Island legend</summary><div data-se559-list style="position:absolute;z-index:100;top:100%;left:0;background:#102334;border:1px solid #658797;border-radius:8px;min-width:190px;max-width:80vw;max-height:45dvh;overflow:auto;padding:6px;display:flex;flex-direction:column;gap:3px"></div>';
 controls.append(details);se559Legend=details;se559LegendKey='';
 const style=document.createElement('style');style.textContent='[data-se559-list] button{display:flex;gap:7px;align-items:center;text-align:left;white-space:normal!important;padding:6px;background:#20394c;color:white;border:0;border-radius:4px}';
 details.append(style);
 function button(name,fn){const b=document.createElement('button');b.type='button';b.textContent=name;b.style.cssText='padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px';controls.append(b);b.onclick=fn;}
 button('Export clean 4K paint guide',se559ExportPaintGuide);
 button('AI anatomical layout',()=>void se557Optimize(false,'anatomical'));
 const t=se551Target();if(t)se559UpdateLegend(t,se559RegionInfo(t,se552Regions(t)));se356UVPreviewSchedule();
};
/* SE559_PAINT_GUIDE_END */
