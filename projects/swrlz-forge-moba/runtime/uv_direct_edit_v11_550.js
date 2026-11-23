/* SE UV direct edit: modifies actual native topologyMesh UVs, not guide pixels.
   One history checkpoint per gesture. Restrict editing to native editable meshes. */
let se356EditMode='off',se356EditDrag=null;
function se356EditTarget(){
 const t=se336SelectedMesh(),p=t?.part,g=t?.mesh?.geometry;
 if(!p||p.kind!=='topologyMesh'||!Array.isArray(p.topologyMesh?.uvs)||
    !g?.getAttribute('uv')||p.topologyMesh.uvs.length!==g.getAttribute('uv').count*2)return null;
 return t;
}
function se356EditNearest(canvas,e){
 const t=se356EditTarget();if(!t)return null;
 const uv=t.mesh.geometry.getAttribute('uv'),r=canvas.getBoundingClientRect();
 const x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;
 let best=-1,d2=Infinity;
 for(let i=0;i<uv.count;i++){
  const dx=uv.getX(i)-x,dy=1-uv.getY(i)-y;
  const d=dx*dx+dy*dy;
  if(d<d2){d2=d;best=i;}
 }
 return d2<Math.pow(15/Math.min(r.width,r.height),2)?best:null;
}
function se356EditApply(t,ids,base,du,dv){
 const uv=t.mesh.geometry.getAttribute('uv'),arr=t.part.topologyMesh.uvs;
 for(let k=0;k<ids.length;k++){
  const i=ids[k],u=Math.max(0,Math.min(1,base[k][0]+du));
  const v=Math.max(0,Math.min(1,base[k][1]+dv));
  arr[i*2]=u;arr[i*2+1]=v;uv.setXY(i,u,v);
 }
 uv.needsUpdate=true;
 se356UVPreviewSchedule();
}
function se356EditInstall(){
 const root=se356UVPreviewRoot(),cv=root?.querySelector('#se356UVCanvas');
 if(!cv||cv.dataset.se356Editable)return;
 cv.dataset.se356Editable='1';
 const bar=document.createElement('div');bar.className='se356-uv-preview-actions';
 bar.innerHTML='<label>UV editing <select id="se356EditMode">'+
 '<option value="off">Inspect only</option><option value="vertex">Drag vertex</option>'+
 '<option value="edge">Drag edge</option></select></label>'+
 '<span id="se356EditHint">Select an editable topology mesh; drag UV points to reshape the real texture mapping.</span>';
 cv.before(bar);
 bar.querySelector('#se356EditMode').addEventListener('change',e=>{
  se356EditMode=e.target.value;cv.style.touchAction=se356EditMode==='off'?'':'none';
 });
 cv.addEventListener('pointerdown',e=>{
  if(se356EditMode==='off'||e.button!==0)return;
  const t=se356EditTarget(),index=se356EditNearest(cv,e);
  if(!t||index===null)return;
  const uv=t.mesh.geometry.getAttribute('uv'),ids=[index];
  if(se356EditMode==='edge'){
   const ix=t.mesh.geometry.getIndex(),count=ix?.count||uv.count;
   let partner=-1,best=Infinity;
   for(let k=0;k<count;k+=3){
    const tri=[0,1,2].map(n=>ix?ix.getX(k+n):k+n);
    if(!tri.includes(index))continue;
    for(const other of tri)if(other!==index){
     const d=(uv.getX(index)-uv.getX(other))**2+
      (uv.getY(index)-uv.getY(other))**2;
     if(d<best){best=d;partner=other;}
    }
   }
   if(partner>=0)ids.push(partner);
  }
  se356EditDrag={pointer:e.pointerId,id:t.part.id,part:t.part,
   x:e.clientX,y:e.clientY,width:cv.getBoundingClientRect().width,
   height:cv.getBoundingClientRect().height,ids,
   base:ids.map(i=>[uv.getX(i),uv.getY(i)]),changed:false};
  cv.setPointerCapture(e.pointerId);e.preventDefault();e.stopImmediatePropagation();
 },true);
 cv.addEventListener('pointermove',e=>{
  const d=se356EditDrag;if(!d||d.pointer!==e.pointerId)return;
  e.preventDefault();e.stopImmediatePropagation();
  const t=se356EditTarget();
  if(!t||t.part!==d.part||t.part.id!==d.id){se356EditDrag=null;return;}
  const dx=(e.clientX-d.x)/d.width,dy=-(e.clientY-d.y)/d.height;
  if(!d.changed&&Math.hypot(e.clientX-d.x,e.clientY-d.y)>2){
   checkpoint();d.changed=true;
  }
  if(d.changed)se356EditApply(t,d.ids,d.base,dx,dy);
 },true);
 const end=e=>{
  const d=se356EditDrag;if(!d||d.pointer!==e.pointerId)return;
  e.preventDefault();e.stopImmediatePropagation();se356EditDrag=null;
  if(cv.hasPointerCapture(e.pointerId))cv.releasePointerCapture(e.pointerId);
  if(d.changed){
   const t=se356EditTarget();
   if(t?.part===d.part){
    signalEdited();se356UVPreviewSchedule();
    status('UV vertex mapping changed. Undo restores the gesture; Save Project persists it.');
   }
  }
 };
 cv.addEventListener('pointerup',end,true);
 cv.addEventListener('pointercancel',end,true);
 cv.addEventListener('click',e=>{
  if(se356EditMode!=='off'){e.preventDefault();e.stopImmediatePropagation();}
 },true);
}

