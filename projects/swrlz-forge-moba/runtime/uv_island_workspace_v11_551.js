/* v11.551: native UV island selection, transform, zoom and visible history. */
let se551Mode='off',se551Selection=null,se551Gesture=null,se551Zoom=1;
function se551Target(){return se356EditTarget();}
function se551Topology(t){
 const uv=t.mesh.geometry.getAttribute('uv'),ix=t.mesh.geometry.getIndex(),n=ix?ix.count:uv.count;
 const faces=[];for(let i=0;i+2<n;i+=3)faces.push([0,1,2].map(j=>ix?ix.getX(i+j):i+j));
 const key=i=>uv.getX(i).toFixed(6)+','+uv.getY(i).toFixed(6);
 const edges=new Map(),parent=faces.map((_,i)=>i);
 const root=i=>{while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;};
 const join=(a,b)=>{a=root(a);b=root(b);if(a!==b)parent[b]=a;};
 faces.forEach((f,fi)=>{for(let j=0;j<3;j++){
  const a=key(f[j]),b=key(f[(j+1)%3]),k=a<b?a+'|'+b:b+'|'+a;
  if(edges.has(k))join(fi,edges.get(k));else edges.set(k,fi);
 }});
 return {uv,faces,root};
}
function se551Pick(t,cv,e){
 const rect=cv.getBoundingClientRect(),u=(e.clientX-rect.left)/rect.width,v=1-(e.clientY-rect.top)/rect.height;
 const topo=se551Topology(t);let picked=-1;
 for(let fi=0;fi<topo.faces.length;fi++){
  const f=topo.faces[fi],p=f.map(i=>[topo.uv.getX(i),topo.uv.getY(i)]);
  const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const q=[u,v],area=cross(p[0],p[1],p[2]);
  if(Math.abs(area)<1e-12)continue;
  const a=cross(p[0],p[1],q)/area,b=cross(p[1],p[2],q)/area,c=cross(p[2],p[0],q)/area;
  if(a>=-1e-5&&b>=-1e-5&&c>=-1e-5){picked=fi;break;}
 }
 if(picked<0)return null;
 const r=topo.root(picked),ids=new Set();
 topo.faces.forEach((f,i)=>{if(topo.root(i)===r)f.forEach(v=>ids.add(v));});
 return [...ids];
}
function se551Draw(){
 const t=se551Target(),cv=se356UVPreviewRoot()?.querySelector('#se356UVCanvas');
 if(!t||!cv||!se551Selection||se551Selection.part!==t.part)return;
 const ctx=cv.getContext('2d'),uv=t.mesh.geometry.getAttribute('uv');
 ctx.save();ctx.fillStyle='#ffe58a';ctx.strokeStyle='#131b35';ctx.lineWidth=2;
 for(const i of se551Selection.ids){const x=uv.getX(i)*cv.width,y=(1-uv.getY(i))*cv.height;
  ctx.beginPath();ctx.arc(x,y,4,0,Math.PI*2);ctx.fill();ctx.stroke();}
 ctx.restore();
}
function se551Transform(kind,amount){
 const t=se551Target(),s=se551Selection;if(!t||!s||s.part!==t.part)return;
 const uv=t.mesh.geometry.getAttribute('uv'),base=s.ids.map(i=>[uv.getX(i),uv.getY(i)]);
 const cx=base.reduce((a,p)=>a+p[0],0)/base.length,cy=base.reduce((a,p)=>a+p[1],0)/base.length;
 const angle=amount*Math.PI/180,cos=Math.cos(angle),sin=Math.sin(angle);
 const values=base.map(([u,v])=>{
  let x=u-cx,y=v-cy;
  if(kind==='rotate'){const xx=x*cos-y*sin;y=x*sin+y*cos;x=xx;}
  if(kind==='scale'){x*=amount;y*=amount;}
  if(kind==='flipU')x=-x;
  if(kind==='flipV')y=-y;
  return [cx+x,cy+y];
 });
 if(values.some(p=>p.some(v=>v<0||v>1))){status('UV transform exceeds the 0–1 atlas; move island inward first.');return;}
 checkpoint();const arr=t.part.topologyMesh.uvs;
 s.ids.forEach((i,k)=>{arr[i*2]=values[k][0];arr[i*2+1]=values[k][1];uv.setXY(i,...values[k]);});
 uv.needsUpdate=true;signalEdited();se356UVPreviewSchedule();
}
function se551Install(){
 const root=se356UVPreviewRoot(),cv=root?.querySelector('#se356UVCanvas');
 if(!cv||cv.dataset.se551)return;cv.dataset.se551='1';
 const dropdown=root.querySelector('#se356EditMode');
 dropdown.insertAdjacentHTML('beforeend','<option value="island">Select / move island</option>');
 dropdown.addEventListener('change',()=>{se551Mode=dropdown.value;
  if(se551Mode==='island')se356EditMode='off';
  se551Gesture=null;cv.style.touchAction=se551Mode==='off'?'':'none';
 });
 const bar=document.createElement('div');bar.className='se356-uv-preview-actions';
 bar.style.cssText='display:flex;flex-wrap:wrap;gap:6px;align-items:center';
 bar.innerHTML='<button type="button" data-se551="undo">↶ Undo</button><button type="button" data-se551="redo">↷ Redo</button>'+
 '<button type="button" data-se551="expand">⛶ Expand</button><button type="button" data-se551="minus">−</button>'+
 '<span data-se551-zoom>100%</span><button type="button" data-se551="plus">+</button>'+
 '<button type="button" data-se551="fit">Fit</button>'+
 '<button type="button" data-se551="rotateLeft">↶ Rotate 15°</button><button type="button" data-se551="rotateRight">↷ Rotate 15°</button>'+
 '<button type="button" data-se551="smaller">Scale −10%</button><button type="button" data-se551="larger">Scale +10%</button>'+
 '<button type="button" data-se551="flipU">Flip U</button><button type="button" data-se551="flipV">Flip V</button>'+
 '<span data-se551-info>Select / move island, then tap a UV face.</span>';
 cv.before(bar);
 const viewport=document.createElement('div');viewport.style.cssText='overflow:auto;max-height:65vh;max-width:100%;touch-action:pan-x pan-y;overscroll-behavior:contain';
 cv.parentNode.insertBefore(viewport,cv);viewport.append(cv);
 const setZoom=z=>{se551Zoom=Math.max(1,Math.min(6,z));cv.style.width=(512*se551Zoom)+'px';
  cv.style.height=(512*se551Zoom)+'px';cv.style.maxWidth='none';bar.querySelector('[data-se551-zoom]').textContent=Math.round(se551Zoom*100)+'%';};
 setZoom(1);
 bar.addEventListener('click',e=>{
  const b=e.target.closest('[data-se551]');if(!b)return;const op=b.dataset.se551;
  if(op==='undo'||op==='redo'){historyStep(op==='undo');se551Selection=null;se356UVPreviewSchedule();return;}
  if(op==='expand'){const expanded=root.classList.toggle('se551-expanded');
   root.style.cssText=expanded?'position:fixed!important;inset:3vh 3vw!important;z-index:2147483000!important;background:#101927!important;overflow:auto!important;padding:12px!important;border:1px solid #678!important;max-height:94vh!important;':'';
   viewport.style.maxHeight=expanded?'72vh':'65vh';b.textContent=expanded?'Close expanded':'⛶ Expand';return;}
  if(op==='plus')setZoom(se551Zoom*1.4);
  if(op==='minus')setZoom(se551Zoom/1.4);
  if(op==='fit')setZoom(1);
  if(op==='rotateLeft')se551Transform('rotate',-15);
  if(op==='rotateRight')se551Transform('rotate',15);
  if(op==='smaller')se551Transform('scale',.9);
  if(op==='larger')se551Transform('scale',1.1);
  if(op==='flipU'||op==='flipV')se551Transform(op,0);
 });
 cv.addEventListener('pointerdown',e=>{
  if(se551Mode!=='island'||e.button!==0)return;
  const t=se551Target();if(!t)return;
  let ids=se551Pick(t,cv,e);
  if(!ids&&se551Selection?.part===t.part)ids=se551Selection.ids;
  if(!ids)return;
  se551Selection={part:t.part,ids};
  const uv=t.mesh.geometry.getAttribute('uv'),rect=cv.getBoundingClientRect();
  se551Gesture={pointer:e.pointerId,part:t.part,x:e.clientX,y:e.clientY,w:rect.width,h:rect.height,
   base:ids.map(i=>[uv.getX(i),uv.getY(i)]),changed:false};
  cv.setPointerCapture(e.pointerId);e.preventDefault();e.stopImmediatePropagation();
  bar.querySelector('[data-se551-info]').textContent=ids.length+' UV vertices selected';
  se356UVPreviewSchedule();
 },true);
 cv.addEventListener('pointermove',e=>{
  const d=se551Gesture;if(!d||e.pointerId!==d.pointer)return;
  e.preventDefault();e.stopImmediatePropagation();
  const t=se551Target();if(!t||t.part!==d.part){se551Gesture=null;return;}
  const du=(e.clientX-d.x)/d.w,dv=-(e.clientY-d.y)/d.h;
  if(!d.changed&&Math.hypot(e.clientX-d.x,e.clientY-d.y)>3){checkpoint();d.changed=true;}
  if(!d.changed)return;
  const uv=t.mesh.geometry.getAttribute('uv'),arr=t.part.topologyMesh.uvs;
  se551Selection.ids.forEach((i,k)=>{const u=Math.max(0,Math.min(1,d.base[k][0]+du)),
   v=Math.max(0,Math.min(1,d.base[k][1]+dv));arr[i*2]=u;arr[i*2+1]=v;uv.setXY(i,u,v);});
  uv.needsUpdate=true;se356UVPreviewSchedule();
 },true);
 const end=e=>{const d=se551Gesture;if(!d||d.pointer!==e.pointerId)return;
  e.preventDefault();e.stopImmediatePropagation();se551Gesture=null;
  if(cv.hasPointerCapture(e.pointerId))cv.releasePointerCapture(e.pointerId);
  if(d.changed){signalEdited();se356UVPreviewSchedule();}
 };
 cv.addEventListener('pointerup',end,true);cv.addEventListener('pointercancel',end,true);
}
const se551PreviousInstall=se356EditInstall;
se356EditInstall=function(){se551PreviousInstall();se551Install();};
const se551PreviousRender=se356UVRender;
se356UVRender=function(){se551PreviousRender();se551Draw();};
