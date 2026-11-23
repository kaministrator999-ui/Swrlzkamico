/* v11.552: independent mobile UV alignment workspace and readable island overlays. */
let se552Portal=null,se552ShowWires=false,se552Pan=false,se552Touch=new Map();
function se552Edges(t,ids){
 const topo=se551Topology(t),chosen=new Set(ids),counts=new Map();
 for(const face of topo.faces){
  if(!face.every(i=>chosen.has(i)))continue;
  for(let k=0;k<3;k++){
   const a=face[k],b=face[(k+1)%3],uv=topo.uv;
   const pa=[uv.getX(a),uv.getY(a)],pb=[uv.getX(b),uv.getY(b)];
   const ka=pa.map(x=>x.toFixed(5)).join(','),kb=pb.map(x=>x.toFixed(5)).join(',');
   const key=ka<kb?ka+'|'+kb:kb+'|'+ka;
   const old=counts.get(key);counts.set(key,{n:(old?.n||0)+1,a:pa,b:pb});
  }
 }
 return [...counts.values()].filter(x=>x.n===1);
}
function se552Paint(){
 if(!se552Portal)return;
 const root=se356UVPreviewRoot(),cv=root?.querySelector('#se356UVCanvas');
 const t=se551Target();if(!cv||!t)return;
 const ctx=cv.getContext('2d'),size=cv.width;
 // Texture first: no dense cyan triangulation obscuring artwork.
 if(se356UVMode==='paint'){
  ctx.clearRect(0,0,size,size);
  se356UVCheckboard(ctx,size);
  const img=se356UVLoadImage(t.part);
  if(img)se356UVPaintImage(ctx,img,t.part,size);
  else {ctx.fillStyle='#e8edf5';ctx.font='16px system-ui';ctx.fillText('Import a texture to align UVs',16,30);}
  if(se552ShowWires){const guide=document.createElement('canvas');guide.width=guide.height=size;
   se336UVLayout(t.mesh,guide);ctx.globalAlpha=.28;ctx.drawImage(guide,0,0);ctx.globalAlpha=1;}
 }
 const s=se551Selection;
 if(!s||s.part!==t.part)return;
 const edges=se552Edges(t,s.ids);
 ctx.save();ctx.lineWidth=3;ctx.strokeStyle='#080e20';ctx.setLineDash([]);
 for(const edge of edges){ctx.beginPath();ctx.moveTo(edge.a[0]*size,(1-edge.a[1])*size);
  ctx.lineTo(edge.b[0]*size,(1-edge.b[1])*size);ctx.stroke();}
 ctx.lineWidth=2;ctx.strokeStyle='#fff36d';
 for(const edge of edges){ctx.beginPath();ctx.moveTo(edge.a[0]*size,(1-edge.a[1])*size);
  ctx.lineTo(edge.b[0]*size,(1-edge.b[1])*size);ctx.stroke();}
 ctx.restore();
}
function se552Open(){
 const root=se356UVPreviewRoot();if(!root||se552Portal)return;
 const cv=root.querySelector('#se356UVCanvas'),bar=root.querySelector('[data-se551="expand"]')?.parentElement;
 if(!cv||!bar)return;
 const host=document.createElement('div');host.id='se552UVHost';
 host.style.cssText='position:fixed;inset:0;z-index:2147483646;background:#0b1420;display:flex;flex-direction:column;overflow:hidden;color:#e8f4ff;font:14px system-ui;padding:env(safe-area-inset-top) 8px env(safe-area-inset-bottom);box-sizing:border-box';
 const header=document.createElement('div');header.style.cssText='display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 4px';
 header.innerHTML='<strong>UV Texture Alignment</strong><button type="button" data-se552-close style="padding:10px 16px;background:#29495b;color:white;border:1px solid #6a98aa;border-radius:8px">Close ✕</button>';
 const controls=document.createElement('div');controls.style.cssText='display:flex;flex-wrap:wrap;gap:6px;padding:6px 0';
 controls.innerHTML='<label style="display:flex;align-items:center;gap:5px">Tool <select data-se552-tool style="padding:9px;background:#1c3446;color:white;border:1px solid #658797;border-radius:6px"><option value="island">Move island</option><option value="vertex">Vertex</option><option value="edge">Edge</option><option value="off">Inspect</option></select></label>'+
 '<label style="display:flex;align-items:center;gap:5px"><input type="checkbox" data-se552-wires> Wireframe</label>'+
 '<label style="display:flex;align-items:center;gap:5px"><input type="checkbox" data-se552-pan> Pan</label>'+
 '<button type="button" data-se552-texture style="padding:8px;background:#254658;color:white;border:1px solid #537e91;border-radius:6px">Show texture</button>';
 const originalMode=root.querySelector('#se356EditMode');
 const viewport=cv.parentElement;
 const originalParent=root.parentNode,originalNext=root.nextSibling;
 const originalRootStyle=root.getAttribute('style'),oldText=bar.querySelector('[data-se551="expand"]')?.textContent;
 const oldMode=originalMode?.value||'off';
 const holder=document.createElement('div');originalParent.insertBefore(holder,root);
 host.append(header,controls,root);document.body.append(host);
 root.style.cssText='flex:1;min-height:0;overflow:auto;background:#111f2d;border:0;padding:0;margin:0;max-width:none;width:100%;';
 // Hide all content except mode controls, UV canvas, history and transforms.
 for(const child of [...root.children]){
  child.dataset.se552Hidden=child.style.display||'';
  if(!child.contains(cv)&&!child.contains(bar)&&!child.contains(originalMode))child.style.display='none';
 }
 viewport.style.cssText='overflow:auto;max-height:calc(100dvh - 205px);width:100%;touch-action:pan-x pan-y;background:#192a38;border:1px solid #537080;border-radius:8px';
 bar.style.cssText='display:flex;flex-wrap:wrap;gap:5px;align-items:center;position:sticky;top:0;background:#112332;padding:6px 0;z-index:2';
 const expand=bar.querySelector('[data-se551="expand"]');if(expand)expand.style.display='none';
 originalMode.value='island';originalMode.dispatchEvent(new Event('change',{bubbles:true}));
 se356UVMode='paint';
 const buttons=root.querySelectorAll('[data-se356-mode]');
 buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.se356Mode==='paint')));
 const setZoom=()=>{const fit=Math.max(.65,Math.min(2,(viewport.clientWidth-18)/512));se551Zoom=fit;
  cv.style.width=(512*fit)+'px';cv.style.height=(512*fit)+'px';cv.style.maxWidth='none';
  const z=bar.querySelector('[data-se551-zoom]');if(z)z.textContent=Math.round(fit*100)+'%';};
 setZoom();se356UVPreviewSchedule();
 const close=()=>{
  se552Portal=null;host.remove();
  holder.replaceWith(root);
  if(originalRootStyle===null)root.removeAttribute('style');else root.setAttribute('style',originalRootStyle);
  for(const child of [...root.children])if(child.dataset.se552Hidden!==undefined){child.style.display=child.dataset.se552Hidden;delete child.dataset.se552Hidden;}
  viewport.style.cssText='overflow:auto;max-height:65vh;max-width:100%;touch-action:pan-x pan-y;overscroll-behavior:contain';
  bar.style.cssText='display:flex;flex-wrap:wrap;gap:6px;align-items:center';
  if(expand){expand.style.display='';expand.textContent=oldText||'⛶ Expand';}
  originalMode.value=oldMode;originalMode.dispatchEvent(new Event('change',{bubbles:true}));
  se356UVPreviewSchedule();
 };
 header.querySelector('[data-se552-close]').addEventListener('click',close);
 controls.querySelector('[data-se552-tool]').addEventListener('change',e=>{
  originalMode.value=e.target.value;originalMode.dispatchEvent(new Event('change',{bubbles:true}));
 });
 controls.querySelector('[data-se552-wires]').addEventListener('change',e=>{se552ShowWires=e.target.checked;se356UVPreviewSchedule();});
 controls.querySelector('[data-se552-pan]').addEventListener('change',e=>{se552Pan=e.target.checked;cv.style.touchAction=se552Pan?'pan-x pan-y':'none';});
 controls.querySelector('[data-se552-texture]').addEventListener('click',()=>{se356UVMode='paint';se356UVPreviewSchedule();});
 // Pan mode bypasses UV editing and scrolls the enlarged canvas.
 cv.addEventListener('pointerdown',e=>{if(se552Pan){e.stopImmediatePropagation();}},true);
 se552Portal={host,close};se356UVPreviewSchedule();
}
function se552Install(){
 const root=se356UVPreviewRoot(),expand=root?.querySelector('[data-se551="expand"]');
 if(!expand||expand.dataset.se552)return;expand.dataset.se552='1';
 expand.addEventListener('click',e=>{
  e.preventDefault();e.stopImmediatePropagation();
  // v11.551 handler is on the parent bar; capture blocks the old inline expansion.
  se552Open();
 },true);
}
const se552PrevInstall=se356EditInstall;
se356EditInstall=function(){se552PrevInstall();se552Install();};
const se552PrevRender=se356UVRender;
se356UVRender=function(){se552PrevRender();se552Paint();};
