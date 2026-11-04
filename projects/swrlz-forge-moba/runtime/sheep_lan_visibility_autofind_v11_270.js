// §E v11.270 — Sheep Tag LAN entry/discovery visibility repair.
// Preserve the v11.268 peer protocol and the v11.269 galaxy renderer.
// The editable preview gains one explicit "LOCAL LAN" launch control; the
// runtime menu keeps one button; XR gets a visible world-pinned controller
// target as well as its existing wrist radial item.
const se270LanUI={tile:null,tileTexture:null,previewOpens:0,runtimeOpens:0,
 xrOpens:0,discoveryRequests:0,failedStarts:0,status:'ready'};

function se270ShowBrowserButton(overlay){
 const panel=overlay?.querySelector?.('.st141-menu-panel');
 if(!panel)return false;
 let entry=panel.querySelector('#se146LanOpen');
 if(!entry){
   entry=document.createElement('button');
   entry.id='se146LanOpen';entry.type='button';
   entry.onclick=()=>se146Open();
   panel.appendChild(entry);
 }
 entry.textContent='LOCAL LAN · FIND GAMES';
 entry.classList.add('se270-lan-primary');
 entry.setAttribute('aria-label','Local LAN multiplayer. Automatically find available games or host.');
 const start=panel.querySelector('#st141StartGame');
 if(start&&entry.previousElementSibling!==start)start.after(entry);
 return true;
}
function se270EnsurePreview(){
 const root=seLevels.preview;
 if(!root||!root.classList?.contains('st141-preview'))return false;
 const panel=root.querySelector('.st141-menu-panel');if(!panel)return false;
 let button=panel.querySelector('#se270PreviewLan');
 if(button)return true;
 button=document.createElement('button');button.type='button';
 button.id='se270PreviewLan';button.className='se270-lan-primary';
 button.textContent='LOCAL LAN · FIND GAMES';
 button.setAttribute('aria-label','Open Local LAN multiplayer from Sheep Tag menu preview');
 button.addEventListener('click',event=>{
   event.stopPropagation();event.preventDefault();
   if(!seLevelsOwns()||seLevelsCurrent()?.role!=='menu'||playing||simulating||stSession)return;
   const launched=seLevels.playingMenu||seLevelsPlayMenu();
   if(launched&&se146Open()){se270LanUI.previewOpens++;se270LanUI.status='preview opened LAN';}
   else {se270LanUI.failedStarts++;se270LanUI.status='Cannot open LAN until Sheep Tag Main Menu is ready';}
 });
 panel.appendChild(button);
 return true;
}
function se270Styles(){
 if(document.getElementById('se270LanStyles'))return;
 const style=document.createElement('style');style.id='se270LanStyles';
 style.textContent=[
  '#st141RuntimeMenu .st141-menu-panel .se270-lan-primary,',
  '#st141MenuPreview .st141-menu-panel .se270-lan-primary{',
  'display:block!important;width:min(100%,390px)!important;min-height:52px!important;',
  'margin:14px auto 0!important;padding:12px 16px!important;',
  'font:bold 16px system-ui,sans-serif!important;',
  'letter-spacing:.055em!important;text-transform:none!important;',
  'background:#184d52!important;color:#eefff7!important;',
  'border:2px solid #6ce6d4!important;border-radius:13px!important;',
  'box-shadow:0 4px 0 #08272a!important;cursor:pointer!important;',
  'pointer-events:auto!important;visibility:visible!important;opacity:1!important;',
  '}',
  '#st141MenuPreview .st141-menu-panel #se270PreviewLan{',
  'position:relative;z-index:5;pointer-events:auto!important;touch-action:manipulation;',
  '}',
  '#st141RuntimeMenu .se146-screen .se270-discovery-heading{',
  'font-weight:800;color:#a7ffee;letter-spacing:.06em;',
  '}'
 ].join('');
 document.head.appendChild(style);
}
function se270LabelDiscovery(){
 const root=se146Lan.root;if(!root)return;
 const head=root.querySelector('.se146-list-head b');
 if(head)head.textContent=location.protocol==='https:'?
   'AUTO-FIND OPEN GAMES':'AUTO-FIND LOCAL LAN GAMES';
 const scan=root.querySelector('#se146LanRefresh');
 if(scan)scan.textContent='↻ Scan Again';
 const hint=root.querySelector('#se270LanHint')||document.createElement('p');
 if(!hint.id){
   hint.id='se270LanHint';hint.className='se146-status';
   root.querySelector('.se146-list-head')?.after(hint);
 }
 hint.textContent=location.protocol==='https:'?
   'Auto-discovery uses the shared public network exit. It is not a private Wi-Fi scan. If no room appears, use the host invite code.':
   'Auto-scanning the local Wi-Fi Bridge for open rooms. Both devices must use the Bridge network.';
}
function se270Discover(){
 if(!se146Lan.active)return false;
 se270LanUI.discoveryRequests++;
 se270LabelDiscovery();
 // Existing code already automatically refreshes and owns the peer roster.
 // Make a real directory probe on open; no fabricated local hosts.
 if(location.protocol==='https:'){
   Promise.resolve(se159Start()).then(()=>{
     if(!se146Lan.active)return;
     if(se159.connected)se159Probe();
     se159Draw();
     se270LabelDiscovery();
   }).catch(error=>{se270LanUI.status='directory unavailable: '+String(error);});
 }else{
   void se146Scan(true);
 }
 return true;
}
const se270InstallBase=se146Install;
se146Install=function(...args){
 const result=se270InstallBase(...args);
 se270Styles();se270ShowBrowserButton(args[0]||seLevels.overlay);
 se270LabelDiscovery();
 return result;
};
const se270PlayBase=seLevelsPlayMenu;
seLevelsPlayMenu=function(...args){
 const result=se270PlayBase(...args);
 if(result){se270Styles();se270ShowBrowserButton(seLevels.overlay);}
 return result;
};
const se270EnsureUIBase=seLevelsEnsureUI;
seLevelsEnsureUI=function(...args){
 const result=se270EnsureUIBase(...args);
 se270Styles();se270EnsurePreview();
 return result;
};
const se270LanOpenBase=se146Open;
se146Open=function(...args){
 const opened=se270LanOpenBase(...args);
 if(opened){se270LanUI.runtimeOpens++;se270Discover();}
 return opened;
};
// Keep visible header coherent as asynchronous directory scans finish.
const se270ScanBase=se146Scan;
se146Scan=async function(...args){
 const result=await se270ScanBase(...args);
 if(se146Lan.active)se270LabelDiscovery();
 return result;
};

function se270XRMenu(){
 return renderer.xr.isPresenting&&se193XRMenuActive()&&
   se195.mode==='menu'&&se195.page==='main'&&se195.visible;
}
function se270TileDispose(){
 const tile=se270LanUI.tile;if(!tile)return;
 scene.remove(tile.root);tile.mesh.geometry.dispose();tile.mesh.material.dispose();
 tile.texture.dispose();se270LanUI.tile=null;
}
function se270TileCreate(){
 if(se270LanUI.tile)return se270LanUI.tile;
 if(!se270XRMenu())return null;
 const pose=se191XRHeadPose();if(!pose)return null;
 const canvas=document.createElement('canvas');canvas.width=768;canvas.height=260;
 const ctx=canvas.getContext('2d');if(!ctx)return null;
 ctx.fillStyle='#0a2735';ctx.fillRect(0,0,768,260);
 ctx.strokeStyle='#66ffcf';ctx.lineWidth=14;ctx.strokeRect(8,8,752,244);
 ctx.font='bold 69px sans-serif';ctx.fillStyle='#f1fff4';
 ctx.textAlign='center';ctx.textBaseline='middle';
 ctx.fillText('LOCAL LAN',384,95,710);
 ctx.font='bold 44px sans-serif';ctx.fillStyle='#a5f6e5';
 ctx.fillText('FIND GAMES / HOST',384,189,715);
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
 texture.generateMipmaps=false;texture.minFilter=THREE.LinearFilter;
 const root=new THREE.Group();
 root.name='Sheep Tag VR Main Menu - Local LAN';
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.82,.285),
   new THREE.MeshBasicMaterial({map:texture,transparent:true,side:THREE.DoubleSide,
     depthTest:false,depthWrite:false,toneMapped:false}));
 mesh.name='LOCAL LAN · controller-selectable menu tile';
 mesh.renderOrder=10740;mesh.frustumCulled=false;root.add(mesh);
 const f=pose.forward.clone();f.y=0;
 if(f.lengthSq()<.01)f.set(0,0,-1);f.normalize();
 const right=new THREE.Vector3().crossVectors(f,new THREE.Vector3(0,1,0)).normalize();
 root.position.copy(pose.eye).addScaledVector(f,1.45)
   .addScaledVector(right,-.45).add(new THREE.Vector3(0,-.12,0));
 root.lookAt(pose.eye); // One-time anchor, not continuous eye-facing.
 scene.add(root);
 se270LanUI.tile={root,mesh,texture};
 return se270LanUI.tile;
}
function se270TileHit(cast){
 const t=se270LanUI.tile;if(!t||!se270XRMenu()||!cast?.ray)return null;
 t.root.updateMatrixWorld(true);
 const hits=cast.ray.intersectObject(t.mesh,false);
 if(!hits.length)return null;
 return {ui:'se195:lanPage',distance:hits[0].distance,
   point:hits[0].point,button:t.mesh};
}
const se270PreviousRadialHit=se195RadialHit;
se195RadialHit=function(record,cast=se192Ray(record)){
 const primary=se270PreviousRadialHit(record,cast);
 const tile=se270TileHit(cast);
 // Preserve nearer radial controls and its modal backdrop.
 if(tile&&(!primary||tile.distance<primary.distance-.02))return tile;
 return primary;
};
const se270OldAction=se195HandleAction;
se195HandleAction=function(action,record){
 if(action==='lanPage'&&se270XRMenu()){
   se270LanUI.xrOpens++;
   se270TileDispose();
 }
 return se270OldAction(action,record);
};
const se270FrameBase=se193XRFrame;
se193XRFrame=function(...args){
 const result=se270FrameBase(...args);
 if(se270XRMenu())se270TileCreate();
 else se270TileDispose();
 return result;
};
const se270CleanupBase=se193XRCleanup;
se193XRCleanup=function(...args){
 se270TileDispose();
 return se270CleanupBase(...args);
};
se270Styles();
se270EnsurePreview();
window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_270=Object.freeze({
 diagnose:()=>({
   browserPreviewButton:!!document.querySelector('#se270PreviewLan'),
   runtimeButton:!!seLevels.overlay?.querySelector('#se146LanOpen'),
   runtimeOpen:!!se146Lan.active,vrTile:!!se270LanUI.tile,
   xrPage:se195.page,roomDirectoryConnected:!!se159.connected,
   discoveredRooms:se159.rooms?.size||0,
   autoDiscovery:se270LanUI.discoveryRequests,
   previewOpens:se270LanUI.previewOpens,
   runtimeOpens:se270LanUI.runtimeOpens,
   vrOpens:se270LanUI.xrOpens,
   lastStatus:se270LanUI.status,
   scanType:location.protocol==='https:'?'shared public network (not subnet)':'local HTTP bridge'
 })
});
