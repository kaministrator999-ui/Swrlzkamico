/* SE377_IMAGE_PART_OUTLINES_START
 * Local, editable 2D trace-first reference workflow.
 * Color-connected regions are proposals, NOT semantic AI identification.
 * Original image pixels stay in browser memory; SVG export is user initiated.
 */
const se377={regions:[],selected:null,view:'Front',tool:'select',drag:null,lastMessage:''};
const se377Colors=['#62edcc','#f9c46b','#ef8dc8','#a4b4ff','#ff966c','#b3f18e','#ece1ad'];
const se377$=name=>document.getElementById('se377'+name);
function se377Closest(a,b){return Math.hypot(a[0]-b[0],a[1]-b[1]);}
function se377Area(poly){let a=0;for(let i=0;i<poly.length;i++){const p=poly[i],q=poly[(i+1)%poly.length];a+=p[0]*q[1]-q[0]*p[1];}return a/2;}
function se377Components(mask,nx,ny,minCount,maxCount){
 const seen=new Uint8Array(mask.length),found=[],queue=new Int32Array(mask.length);
 for(let i=0;i<mask.length;i++){
  if(!mask[i]||seen[i])continue;
  let head=0,tail=1;queue[0]=i;seen[i]=1;
  while(head<tail){
   const j=queue[head++],x=j%nx,y=Math.floor(j/nx);
   const neighbors=[x>0?j-1:-1,x+1<nx?j+1:-1,y>0?j-nx:-1,y+1<ny?j+nx:-1];
   for(const n of neighbors)if(n>=0&&mask[n]&&!seen[n]){seen[n]=1;queue[tail++]=n;}
  }
  if(tail>=minCount)found.push(Array.from(queue.subarray(0,tail)));
 }
 return found.sort((a,b)=>b.length-a.length).slice(0,maxCount);
}
function se377Outline(cells,nx,ny,box){
 const active=new Set(cells),edges=[],starts=new Map();
 function edge(a,b){
  const n=edges.length;edges.push([a,b]);
  const key=a.join(',');if(!starts.has(key))starts.set(key,[]);starts.get(key).push(n);
 }
 for(const p of cells){
  const x=p%nx,y=Math.floor(p/nx);
  if(y===0||!active.has(p-nx))edge([x,y],[x+1,y]);
  if(x===nx-1||!active.has(p+1))edge([x+1,y],[x+1,y+1]);
  if(y===ny-1||!active.has(p+nx))edge([x+1,y+1],[x,y+1]);
  if(x===0||!active.has(p-1))edge([x,y+1],[x,y]);
 }
 const used=new Set();let best=[];
 for(let start=0;start<edges.length;start++){
  if(used.has(start))continue;
  let at=start,poly=[],guard=0;
  while(!used.has(at)&&guard++<edges.length){
   used.add(at);
   const [from,to]=edges[at];poly.push(from);
   const options=starts.get(to.join(','))||[];
   const next=options.find(n=>!used.has(n));
   if(next===undefined)break;
   at=next;
  }
  if(poly.length>best.length)best=poly;
 }
 if(best.length<8)return [];
 // Simplify a closed pixel staircase to at most 96 interactive control points.
 let step=Math.max(1,Math.ceil(best.length/96)),out=[];
 for(let i=0;i<best.length;i+=step){
  const [x,y]=best[i];out.push([
   Number((box.x+box.w*x/nx).toFixed(5)),
   Number((box.y+box.h*y/ny).toFixed(5))
  ]);
 }
 if(out.length>3&&se377Closest(out[0],out[out.length-1])<.0003)out.pop();
 return out;
}
function se377Palette(samples,count){
 if(!samples.length)return [];
 const picks=[samples[Math.floor(samples.length/2)].slice()];
 while(picks.length<count){
  let far=null,score=-1;
  for(let k=0;k<samples.length;k+=Math.max(1,Math.floor(samples.length/1400))){
   const p=samples[k],nearest=Math.min(...picks.map(c=>(p[0]-c[0])**2+(p[1]-c[1])**2+(p[2]-c[2])**2));
   if(nearest>score){score=nearest;far=p;}
  }
  if(score<100)break;
  picks.push(far.slice());
 }
 for(let iter=0;iter<7;iter++){
  const sums=picks.map(()=>[0,0,0,0]);
  for(const p of samples){
   let best=0,dist=Infinity;
   for(let j=0;j<picks.length;j++){
    const c=picks[j],d=2*(p[0]-c[0])**2+2*(p[1]-c[1])**2+2*(p[2]-c[2])**2;
    if(d<dist){best=j;dist=d;}
   }
   const s=sums[best];s[0]+=p[0];s[1]+=p[1];s[2]+=p[2];s[3]++;
  }
  sums.forEach((s,j)=>{if(s[3])picks[j]=s.slice(0,3).map(v=>v/s[3]);});
 }
 return picks;
}
function se377TraceView(box,img,bg){
 const w=se375Canvas.width,h=se375Canvas.height;
 const nx=Math.max(20,Math.min(180,Math.round(box.w*w/2.5)));
 const ny=Math.max(20,Math.min(220,Math.round(box.h*h/2.5)));
 const mask=new Uint8Array(nx*ny),colors=new Array(mask.length),samples=[];
 for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
  const ix=Math.max(0,Math.min(w-1,Math.round((box.x+(x+.5)*box.w/nx)*w)));
  const iy=Math.max(0,Math.min(h-1,Math.round((box.y+(y+.5)*box.h/ny)*h)));
  const k=y*nx+x,p=(iy*w+ix)*4;
  if(!se375Foreground(img,ix,iy,w,h,bg))continue;
  const color=[img[p],img[p+1],img[p+2]];
  mask[k]=1;colors[k]=color;samples.push(color);
 }
 if(samples.length<100)return [];
 const minOverall=Math.max(18,Math.round(nx*ny*.002));
 const bodies=se377Components(mask,nx,ny,minOverall,3);
 if(!bodies.length)return [];
 const result=[];
 bodies.forEach((cells,index)=>{
  const pts=se377Outline(cells,nx,ny,box);if(pts.length<3)return;
  result.push({name:index?'Detached silhouette '+index:'Main silhouette',view:box.name,points:pts,
   color:se377Colors[index%se377Colors.length],visible:true,kind:'silhouette',size:cells.length});
 });
 const palette=se377Palette(samples,5);
 if(palette.length>1){
  const buckets=palette.map(()=>new Uint8Array(mask.length));
  for(let k=0;k<mask.length;k++){
   if(!mask[k])continue;
   const p=colors[k];let best=0,dist=Infinity;
   for(let j=0;j<palette.length;j++){
    const c=palette[j],d=2*(p[0]-c[0])**2+2*(p[1]-c[1])**2+2*(p[2]-c[2])**2;
    if(d<dist){best=j;dist=d;}
   }
   buckets[best][k]=1;
  }
  const pieces=[];
  for(let j=0;j<buckets.length;j++){
   const chunks=se377Components(buckets[j],nx,ny,Math.max(18,Math.round(nx*ny*.006)),5);
   for(const chunk of chunks){
    const pts=se377Outline(chunk,nx,ny,box);
    if(pts.length>=4)pieces.push({name:'Color region',view:box.name,points:pts,
      color:se377Colors[(j+2)%se377Colors.length],visible:true,kind:'detail',size:chunk.length});
   }
  }
  pieces.sort((a,b)=>b.size-a.size).slice(0,10).forEach((p,i)=>{
   p.name='Color region '+(i+1);result.push(p);
  });
 }
 return result;
}
function se377Analyze(){
 se377.regions=[];se377.selected=null;se377.drag=null;
 if(!se375Canvas)return;
 try{
  const canvas=se375Canvas,w=canvas.width,h=canvas.height;
  const img=canvas.getContext('2d',{willReadFrequently:true}).getImageData(0,0,w,h).data;
  const bg=se375Sample().bg;
  for(const box of se375PanelRects()){
   box.name=box.name;
   se377.regions.push(...se377TraceView(box,img,bg));
  }
  se377.regions.forEach((r,i)=>{r.id='trace-'+(i+1);});
  if(se377.regions.length)se377.selected=se377.regions.find(r=>r.view===se377.view)?.id||se377.regions[0].id;
  se377Note(se377.regions.length+' draft outlines found across the view guides. Color boundaries are proposals, not reliable recognition of hood, hair or robe parts. Tap a contour, rename it, then refine points.');
 }catch(error){
  se377Note('Could not trace reference: '+String(error?.message||error),true);
 }
 se377Refresh();
}
function se377Note(message,error=false){se377.lastMessage=message;se375Note(message,error);}
function se377Picked(){return se377.regions.find(r=>r.id===se377.selected)||null;}
function se377InPoly(p,poly){
 let inside=false;
 for(let i=0,j=poly.length-1;i<poly.length;j=i++){
  const a=poly[i],b=poly[j];
  if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside;
 }
 return inside;
}
function se377Paint(){
 const canvas=se375Id('Preview');if(!canvas||!se375Canvas)return;
 const ctx=canvas.getContext('2d'),wx=canvas.width,hy=canvas.height;
 for(const region of se377.regions){
  if(!region.visible||region.points.length<3)continue;
  const active=region.id===se377.selected,full=region.view===se377.view;
  ctx.save();ctx.globalAlpha=full?1:.35;ctx.lineWidth=active?3:1.6;
  ctx.strokeStyle=active?'#ffed78':region.color;ctx.fillStyle=active?'#ffe97024':'#78deec09';
  ctx.beginPath();region.points.forEach((p,i)=>i?ctx.lineTo(p[0]*wx,p[1]*hy):ctx.moveTo(p[0]*wx,p[1]*hy));
  ctx.closePath();ctx.fill();ctx.stroke();
  if(active){
   ctx.fillStyle='#ffed78';
   for(const p of region.points){ctx.beginPath();ctx.arc(p[0]*wx,p[1]*hy,3.2,0,Math.PI*2);ctx.fill();}
  }
  ctx.restore();
 }
}
function se377Refresh(){
 const select=se377$('Region'),name=se377$('Name'),show=se377$('Visible');
 if(select){
  select.replaceChildren();
  for(const r of se377.regions.filter(r=>r.view===se377.view)){
   const option=document.createElement('option');option.value=r.id;option.textContent=r.name+' · '+r.points.length+' pts';
   select.append(option);
  }
  if(!se377.regions.some(r=>r.id===se377.selected&&r.view===se377.view))
   se377.selected=se377.regions.find(r=>r.view===se377.view)?.id||null;
  select.value=se377.selected||'';
 }
 const picked=se377Picked();
 if(name){name.value=picked?.name||'';name.disabled=!picked;}
 if(show){show.checked=!!picked?.visible;show.disabled=!picked;}
 const total=se377$('Count');
 if(total)total.textContent=se377.regions.filter(r=>r.view===se377.view).length+' contours in '+se377.view;
 const original=se377DrawOriginal;
 if(se375Canvas&&typeof original==='function')se375Draw();
}
function se377Cursor(event){
 const canvas=se375Id('Preview'),rect=canvas.getBoundingClientRect();
 const scale=Math.min(rect.width/canvas.width,rect.height/canvas.height);
 const w=canvas.width*scale,h=canvas.height*scale;
 const x=rect.left+(rect.width-w)/2,y=rect.top+(rect.height-h)/2;
 return [(event.clientX-x)/Math.max(1,w),(event.clientY-y)/Math.max(1,h)];
}
function se377NearVertex(region,p){
 let best=-1,dist=Infinity;
 region.points.forEach((v,i)=>{const d=se377Closest([v[0]*460,v[1]*460],[p[0]*460,p[1]*460]);if(d<dist){dist=d;best=i;}});
 return dist<13?best:-1;
}
function se377NearEdge(region,p){
 let best=0,dist=Infinity,projection=null;
 for(let i=0;i<region.points.length;i++){
  const a=region.points[i],b=region.points[(i+1)%region.points.length],
   dx=b[0]-a[0],dy=b[1]-a[1],len=dx*dx+dy*dy||1,
   t=Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/len)),
   q=[a[0]+t*dx,a[1]+t*dy],d=se377Closest(p,q);
  if(d<dist){best=i;dist=d;projection=q;}
 }
 return {index:best,dist,point:projection};
}
function se377PointerDown(event){
 if(!se375Canvas||!se377.regions.length)return;
 const p=se377Cursor(event);
 const regions=se377.regions.filter(r=>r.view===se377.view&&r.visible);
 let chosen=null;
 // Interior selection favors detail pieces over the overall silhouette.
 for(const r of [...regions].reverse())if(se377InPoly(p,r.points)){chosen=r;break;}
 const picked=se377Picked();
 if((se377.tool==='move'||se377.tool==='remove'||se377.tool==='add')&&picked){
  if(se377.tool==='add'){
   const edge=se377NearEdge(picked,p);
   if(edge.dist<.032&&picked.points.length<128){
    picked.points.splice(edge.index+1,0,edge.point);se377Note('Added editable point to '+picked.name+'.');
   }
  }else{
   const i=se377NearVertex(picked,p);
   if(i>=0&&se377.tool==='remove'&&picked.points.length>3){
    picked.points.splice(i,1);se377Note('Removed contour point.');
   }else if(i>=0&&se377.tool==='move'){
    se377.drag={id:picked.id,index:i};event.currentTarget.setPointerCapture?.(event.pointerId);
   }
  }
 }else if(chosen){se377.selected=chosen.id;se377Note('Selected '+chosen.name+'. Rename or edit its outline.');}
 se377Refresh();event.preventDefault();
}
function se377PointerMove(event){
 if(!se377.drag)return;
 const r=se377Picked();if(!r||r.id!==se377.drag.id)return;
 const p=se377Cursor(event),box=se375PanelRects().find(b=>b.name===r.view);
 if(!box)return;
 r.points[se377.drag.index]=[Math.max(box.x,Math.min(box.x+box.w,p[0])),
   Math.max(box.y,Math.min(box.y+box.h,p[1]))];
 se375Draw();event.preventDefault();
}
function se377Export(){
 if(!se375Canvas||!se377.regions.length){se377Note('Import and trace an image first.',true);return;}
 const w=se375Canvas.width,h=se375Canvas.height;
 const escape=s=>String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
 const paths=se377.regions.filter(r=>r.visible&&r.points.length>=3).map(r=>{
  const d=r.points.map((p,i)=>(i?'L':'M')+(p[0]*w).toFixed(1)+' '+(p[1]*h).toFixed(1)).join(' ')+' Z';
  return '<path d="'+d+'" stroke="'+escape(r.color)+'" fill="none" stroke-width="2" data-view="'+escape(r.view)+'" data-name="'+escape(r.name)+'"/>';
 });
 const svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+w+' '+h+'"><title>§E editable 2D reference trace</title>'+paths.join('')+'</svg>';
 const url=URL.createObjectURL(new Blob([svg],{type:'image/svg+xml'})),a=document.createElement('a');
 a.href=url;a.download='swrlz-reference-contours.svg';a.click();
 setTimeout(()=>URL.revokeObjectURL(url),2000);
 se377Note('Exported '+paths.length+' visible outlines as vector SVG. No automatic 3D model was created.');
}
const se377DrawOriginal=se375Draw;
se375Draw=function(){se377DrawOriginal();se377Paint();};
const se377LoadOriginal=se375Load;
se375Load=async function(file){
 se377.regions=[];se377.selected=null;
 await se377LoadOriginal(file);
 if(se375Canvas)se377Analyze();
};
const se377InstallOriginal=se375Install;
se375Install=function(){
 se377InstallOriginal();
 const panel=se375Id('Panel');if(!panel||se377$('View'))return;
 const summary=panel.querySelector(':scope > summary');if(summary)summary.textContent='✦ Image → editable 2D outlines';
 const body=panel.querySelector('.se375-body'),preview=se375Id('Preview');
 preview.style.maxHeight='min(44vh,380px)';preview.style.touchAction='none';preview.style.cursor='crosshair';
 const tools=document.createElement('section');tools.id='se377Tools';
 tools.innerHTML='<div class="se377-row"><label>View<select id="se377View"><option>Front</option><option>Left</option><option>Right</option><option>Back</option><option>Top</option></select></label><label>Edit contour<select id="se377Tool"><option value="select">Select region</option><option value="move">Move point</option><option value="add">Add point</option><option value="remove">Remove point</option></select></label></div>'
 +'<small id="se377Count">Import an image to trace visible shapes</small>'
 +'<label>Outlined piece<select id="se377Region" aria-label="Outlined piece"></select></label>'
 +'<div class="se377-row"><label>Piece name<input id="se377Name" maxlength="90" placeholder="Rename selected contour"></label><label class="se377-visible"><input id="se377Visible" type="checkbox" checked> Visible</label></div>'
 +'<div class="se377-actions"><button id="se377Retry" type="button">Re-trace image</button><button id="se377Export" type="button">Export 2D SVG</button></div>'
 +'<small>Draft color-separated outlines, not semantic AI recognition. Select a region and refine its vertices before converting to 3D.</small>';
 const style=document.createElement('style');style.textContent='#se377Tools{display:grid;gap:7px;padding:7px;border:1px solid #766a93;border-radius:7px}#se377Tools .se377-row{display:grid;grid-template-columns:1fr 1fr;gap:6px;align-items:end}#se377Tools input,#se377Tools select{min-width:0;width:100%;background:#211b32;color:#f6efff;border:1px solid #7a708e;border-radius:4px;padding:5px}#se377Tools .se377-actions{display:flex;flex-wrap:wrap;gap:6px}#se377Tools .se377-visible{align-self:end;display:flex;align-items:center;gap:5px}#se377Tools .se377-visible input{width:auto}#se377Tools small{color:#d9ceef;line-height:1.35}@media(max-width:340px){#se377Tools .se377-row{grid-template-columns:1fr}}';
 document.head.append(style);
 preview.insertAdjacentElement('afterend',tools);
 const old3D=se375Id('Generate');const advanced=document.createElement('details');
 advanced.innerHTML='<summary>Experimental old rough 3D blockout</summary><p>This older loft generator may create overlapping shapes. Review 2D contours first.</p>';
 advanced.append(old3D);body.insertBefore(advanced,se375Id('Status'));
 se377$('View').onchange=e=>{se377.view=e.target.value;se377Refresh();};
 se377$('Tool').onchange=e=>{se377.tool=e.target.value;};
 se377$('Region').onchange=e=>{se377.selected=e.target.value;se377Refresh();};
 se377$('Name').onchange=e=>{const r=se377Picked();if(r){r.name=e.target.value.trim().slice(0,90)||r.name;se377Refresh();}};
 se377$('Visible').onchange=e=>{const r=se377Picked();if(r){r.visible=e.target.checked;se377Refresh();}};
 se377$('Retry').onclick=()=>se377Analyze();
 se377$('Export').onclick=se377Export;
 preview.addEventListener('pointerdown',se377PointerDown);
 preview.addEventListener('pointermove',se377PointerMove);
 preview.addEventListener('pointerup',()=>{se377.drag=null;});
 preview.addEventListener('pointercancel',()=>{se377.drag=null;});
 se375Id('Guides')?.querySelectorAll('input').forEach(input=>input.addEventListener('change',()=>se377Analyze()));
 se377Refresh();
};
queueMicrotask(se375Install);
/* SE377_IMAGE_PART_OUTLINES_END */