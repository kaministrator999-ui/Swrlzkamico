// §E v11.57 — independently draggable/saved local-image reference windows.
// Maximum four, one per existing data:image reference. Never fetch remote URLs.
// Each layout is native model data; dragging only previews until pointerup.
let atelierFloatingHost=null;
function atelierFloatingLayoutValid(v){
 if(v===undefined)return true;
 return !!v&&typeof v==='object'&&!Array.isArray(v)&&
  Object.keys(v).sort().join('|')==='height|open|pinned|width|x|y'&&
  typeof v.open==='boolean'&&typeof v.pinned==='boolean'&&
  Number.isInteger(v.x)&&v.x>=0&&v.x<=6000&&
  Number.isInteger(v.y)&&v.y>=0&&v.y<=6000&&
  Number.isInteger(v.width)&&v.width>=180&&v.width<=560&&
  Number.isInteger(v.height)&&v.height>=180&&v.height<=600;
}
function atelierFloatingDefault(index=0){
 const w=typeof stage!=='undefined'&&stage?.clientWidth||800;
 const h=typeof stage!=='undefined'&&stage?.clientHeight||620;
 // Leave the upper-left reference tab controls reachable even on phones.
 return {open:true,pinned:false,x:Math.max(0,Math.round(w-300-index*25)),
  y:Math.max(140,Math.round(h-300-index*32)),width:280,height:280};
}
function atelierFloatingPlace(el,layout){
 const w=stage?.clientWidth||320,h=stage?.clientHeight||400;
 const left=Math.min(Math.max(0,layout.x),Math.max(0,w-Math.min(layout.width,w)));
 const top=Math.min(Math.max(0,layout.y),Math.max(0,h-Math.min(layout.height,h)));
 el.style.left=left+'px';el.style.top=top+'px';
 el.style.width=layout.width+'px';el.style.height=layout.height+'px';
 el.style.maxWidth='calc(100% - 8px)';el.style.maxHeight='calc(100% - 8px)';
 return {left,top};
}
function atelierFloatingCommit(id,layout){
 const m=atelierRefEnsure(),ref=m?.references?.find(r=>r.id===id);
 if(!ref||!atelierFloatingLayoutValid(layout))return false;
 if(JSON.stringify(ref.floatWindow||null)===JSON.stringify(layout))return true;
 const next={...ref,floatWindow:{...layout}};
 if(!atelierRefValid([next]))return false;
 atelierRefSnapshotBefore(()=>{ref.floatWindow={...layout};});
 return true;
}
function atelierFloatingEnsureHost(){
 if(atelierFloatingHost)return atelierFloatingHost;
 // RefInstall occurs before the 3D stage finishes initializing in v11.20.
 // Mount lazily on first paint/interaction instead of abandoning UI listeners.
 if(!stage)return null;
 atelierFloatingHost=document.createElement('div');
 atelierFloatingHost.id='modelAtelierFloatingReferences';
 Object.assign(atelierFloatingHost.style,{position:'absolute',inset:'0',
  pointerEvents:'none',overflow:'hidden',zIndex:'220'});
 // Existing viewport controls have z-index 180; floating reference handles
 // must remain hit-testable above them on narrow phones. Empty host is click-through.
 stage.appendChild(atelierFloatingHost);
 return atelierFloatingHost;
}
function atelierFloatingRefresh(){
 if(!atelierFloatingEnsureHost())return;
 const m=atelierRefEnsure();
 atelierFloatingHost.replaceChildren();
 if(!m)return;
 for(const [index,ref] of m.references.entries()){
  const v=ref.floatWindow;
  if(!v?.open)continue;
  const panel=document.createElement('section');
  panel.className='atelier-float-reference';
  panel.setAttribute('aria-label',ref.name+' independently floating reference');
  panel.dataset.referenceId=ref.id;
  Object.assign(panel.style,{position:'absolute',display:'flex',flexDirection:'column',
   background:'#151b28',border:'1px solid #779bb4',borderRadius:'8px',
   overflow:'hidden',boxShadow:'0 10px 28px #0008',pointerEvents:'none',
   // Earlier panels stay above later overlapping photo content so their
   // headers remain touchable in a cascade on desktop and mobile.
   zIndex:String(110+m.references.length-index),touchAction:'none'});
  const fitted=atelierFloatingPlace(panel,v);
  const header=document.createElement('div');header.className='atelier-float-reference-handle';
  Object.assign(header.style,{height:'34px',display:'flex',alignItems:'center',justifyContent:'space-between',
   cursor:v.pinned?'default':'move',background:'#26394e',color:'#fff',
   padding:'3px 8px',touchAction:'none',userSelect:'none',flexShrink:'0',pointerEvents:'auto'});
  const label=document.createElement('strong');label.textContent=ref.angle+' · '+ref.name.slice(0,30);
  label.style.fontSize='12px';
  const actions=document.createElement('span');actions.style.display='flex';actions.style.gap='8px';
  const pin=document.createElement('button');pin.type='button';pin.textContent=v.pinned?'Unpin':'Pin';
  pin.setAttribute('aria-label','Toggle pin '+ref.name);pin.addEventListener('click',e=>{
   e.stopPropagation();atelierFloatingCommit(ref.id,{...v,pinned:!v.pinned});
  });
  const close=document.createElement('button');close.type='button';close.textContent='×';
  close.setAttribute('aria-label','Close floating '+ref.name);
  close.addEventListener('click',e=>{e.stopPropagation();atelierFloatingCommit(ref.id,{...v,open:false});});
  actions.append(pin,close);header.append(label,actions);
  const img=document.createElement('img');img.src=ref.data;img.alt=ref.name;
  img.draggable=false;
  Object.assign(img.style,{width:'100%',flex:'1',minHeight:'0',objectFit:'contain',
   background:'#10151e',pointerEvents:'none'});
  const caption=document.createElement('small');caption.textContent='Local '+ref.angle+' reference · read-only';
  caption.style.padding='3px 8px';caption.style.color='#bacbdb';
  panel.append(header,img,caption);
  let drag=null;
  header.addEventListener('pointerdown',e=>{
   if(e.button!==0||e.target!==header&&e.target!==label||v.pinned)return;
   e.preventDefault();e.stopPropagation();
   const r=panel.getBoundingClientRect();
   drag={id:e.pointerId,x:e.clientX,y:e.clientY,left:fitted.left,top:fitted.top};
   header.setPointerCapture?.(e.pointerId);
  });
  header.addEventListener('pointermove',e=>{
   if(!drag||drag.id!==e.pointerId)return;
   const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
   atelierFloatingPlace(panel,{...v,x:Math.round(drag.left+dx),y:Math.round(drag.top+dy)});
  });
  function end(e,cancel=false){
   if(!drag||drag.id!==e.pointerId)return;
   const d=drag;drag=null;
   if(cancel){atelierFloatingPlace(panel,v);return;}
   const state={...v,x:Math.min(6000,Math.max(0,Math.round(d.left+e.clientX-d.x))),
     y:Math.min(6000,Math.max(0,Math.round(d.top+e.clientY-d.y)))};
   if(!atelierFloatingCommit(ref.id,state))atelierFloatingPlace(panel,v);
  }
  header.addEventListener('pointerup',e=>end(e));
  header.addEventListener('pointercancel',e=>end(e,true));
  atelierFloatingHost.append(panel);
 }
 const info=$m('ReferenceFloatInfo');
 if(info)info.textContent=m.references.filter(r=>r.floatWindow?.open).length+
  ' independent image windows · saved individually with project JSON.';
}
function atelierFloatingInstall(){
 atelierFloatingEnsureHost();
 $m('ReferenceFloatOpen')?.addEventListener('click',()=>{
  const m=atelierRefEnsure(),ref=atelierRefCurrent();if(!m||!ref)return;
  const i=m.references.indexOf(ref);
  if(atelierFloatingCommit(ref.id,{...(ref.floatWindow||atelierFloatingDefault(i)),open:true}))
   status('Opened independent '+ref.angle+' reference. Drag the header to move; save/Undo persists placement.');
 });
 $m('ReferenceFloatCloseAll')?.addEventListener('click',()=>{
  const m=atelierRefEnsure();if(!m||!m.references.some(r=>r.floatWindow?.open))return;
  checkpoint();
  for(const r of m.references)if(r.floatWindow)r.floatWindow.open=false;
  atelierRefMark();atelierRefPaint();
  status('Closed floating reference windows with a single Undo checkpoint.');
 });
 atelierFloatingRefresh();
}
