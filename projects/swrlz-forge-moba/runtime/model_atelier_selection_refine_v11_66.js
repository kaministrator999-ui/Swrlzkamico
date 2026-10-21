// v11.66 refinements: saved, viewport-relative dialog placement and easy recovery.
const atelierMeshDialogKey='swyrlz-atelier-mesh-dialog-v2';
let atelierMeshDialogDrag=null;
let atelierMeshDialogPlacement=(()=>{
 try{
  const saved=JSON.parse(localStorage.getItem(atelierMeshDialogKey)||'null');
  if(saved&&Number.isFinite(saved.x)&&Number.isFinite(saved.y)&&saved.x>=0&&saved.x<=1&&saved.y>=0&&saved.y<=1)return saved;
 }catch(_){}
 return {x:.02,y:.57};
})();
function atelierMeshToolbarPosition(){
 if(!atelierMeshStrip||atelierMeshStrip.hidden||!stage)return;
 if(atelierMeshDialogDrag)return;
 const width=stage.clientWidth,height=stage.clientHeight;
 if(width<1||height<1)return;
 const w=atelierMeshStrip.offsetWidth||275,h=atelierMeshStrip.offsetHeight||230;
 const usableX=Math.max(0,width-w-6),usableY=Math.max(0,height-h-6);
 const x=Math.round(5+usableX*atelierMeshDialogPlacement.x);
 const y=Math.round(5+usableY*atelierMeshDialogPlacement.y);
 if(atelierMeshStrip.style.left!==x+'px')atelierMeshStrip.style.left=x+'px';
 if(atelierMeshStrip.style.top!==y+'px')atelierMeshStrip.style.top=y+'px';
 atelierMeshStrip.style.visibility='visible';
}
function atelierMeshDialogInstall(){
 const header=atelierMeshStrip?.querySelector('.amq-head');
 if(!header||header.dataset.dialogDragInstalled)return;
 header.dataset.dialogDragInstalled='1';
 header.setAttribute('tabindex','0');
 header.setAttribute('role','button');
 header.setAttribute('aria-label','Drag the Mesh tools window to reposition it');
 header.title='Drag to move · position saved on this device';
 header.addEventListener('pointerdown',event=>{
  if(event.button!==0||event.target.closest('button,input,select'))return;
  const strip=atelierMeshStrip;
  const before=strip.getBoundingClientRect();
  atelierMeshDialogDrag={id:event.pointerId,x:event.clientX,y:event.clientY,
    left:parseFloat(strip.style.left)||0,top:parseFloat(strip.style.top)||0,
    width:before.width,height:before.height};
  try{header.setPointerCapture(event.pointerId)}catch(_){}
  event.preventDefault();event.stopPropagation();
 });
 header.addEventListener('pointermove',event=>{
  const drag=atelierMeshDialogDrag;
  if(!drag||drag.id!==event.pointerId)return;
  const maxX=Math.max(5,stage.clientWidth-drag.width-5);
  const maxY=Math.max(5,stage.clientHeight-drag.height-5);
  atelierMeshStrip.style.left=atelierMeshClamp(drag.left+event.clientX-drag.x,5,maxX)+'px';
  atelierMeshStrip.style.top=atelierMeshClamp(drag.top+event.clientY-drag.y,5,maxY)+'px';
  event.preventDefault();event.stopPropagation();
 });
 const finish=(event,save)=>{
  const drag=atelierMeshDialogDrag;if(!drag||drag.id!==event.pointerId)return;
  atelierMeshDialogDrag=null;
  if(save){
   const usableX=Math.max(1,stage.clientWidth-drag.width-6);
   const usableY=Math.max(1,stage.clientHeight-drag.height-6);
   atelierMeshDialogPlacement={
    x:atelierMeshClamp(((parseFloat(atelierMeshStrip.style.left)||5)-5)/usableX,0,1),
    y:atelierMeshClamp(((parseFloat(atelierMeshStrip.style.top)||5)-5)/usableY,0,1)
   };
   try{localStorage.setItem(atelierMeshDialogKey,JSON.stringify(atelierMeshDialogPlacement))}catch(_){}
  }
  atelierMeshToolbarPosition();
  event.preventDefault();event.stopPropagation();
 };
 header.addEventListener('pointerup',event=>finish(event,true));
 header.addEventListener('pointercancel',event=>finish(event,false));
 header.addEventListener('keydown',event=>{
  if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(event.key))return;
  const delta=event.shiftKey?.05:.015;
  if(event.key==='ArrowUp')atelierMeshDialogPlacement.y=atelierMeshClamp(atelierMeshDialogPlacement.y-delta,0,1);
  if(event.key==='ArrowDown')atelierMeshDialogPlacement.y=atelierMeshClamp(atelierMeshDialogPlacement.y+delta,0,1);
  if(event.key==='ArrowLeft')atelierMeshDialogPlacement.x=atelierMeshClamp(atelierMeshDialogPlacement.x-delta,0,1);
  if(event.key==='ArrowRight')atelierMeshDialogPlacement.x=atelierMeshClamp(atelierMeshDialogPlacement.x+delta,0,1);
  try{localStorage.setItem(atelierMeshDialogKey,JSON.stringify(atelierMeshDialogPlacement))}catch(_){}
  atelierMeshToolbarPosition();event.preventDefault();
 });
}
function atelierMeshHistoryShortcut(backward){
 const stack=backward?undo:redo;
 if(!stack.length){status('No '+(backward?'Undo':'Redo')+' history available.');return;}
 const prior=selection,group=[...atelierMeshIds];
 historyStep(backward);
 const restored=group.find(id=>partById(id))||(partById(prior)?prior:null);
 if(restored){atelierMeshAdding=false;select(restored);}
 atelierMeshToolbarRefresh();
}
function atelierMeshFrameSelected(){
 const btn=[...panel.querySelectorAll('button')].find(b=>/frame selected/i.test(b.textContent||''));
 if(btn){btn.click();return;}
 const meshes=atelierMeshSelectedMeshes(),bounds=new THREE.Box3();
 for(const mesh of meshes)bounds.expandByObject(mesh);
 if(!bounds.isEmpty()&&typeof atelierDetailTarget!=='undefined'){
  atelierDetailTarget=bounds.getCenter(new THREE.Vector3());
  orbit.distance=atelierMeshClamp(bounds.getSize(new THREE.Vector3()).length()*1.65,1.2,20);
  cameraUpdate();
  status('Selected mesh framed in camera.');
 }
}
