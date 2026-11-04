// §E v11.271 — Sheep Tag LAN entry/discovery visibility repair.
// Preserve the v11.268 peer protocol and the v11.269 galaxy renderer.
// The editable preview gains one explicit "LOCAL LAN" launch control; the
// runtime menu keeps one button; XR gets a visible world-pinned controller
// target as well as its existing wrist radial item.
const se271LanUI={tile:null,tileTexture:null,previewOpens:0,runtimeOpens:0,
 xrOpens:0,discoveryRequests:0,failedStarts:0,status:'ready'};

function se271ShowBrowserButton(overlay){
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
 entry.classList.add('se271-lan-primary');
 entry.setAttribute('aria-label','Local LAN multiplayer. Automatically find available games or host.');
 const start=panel.querySelector('#st141StartGame');
 if(start&&entry.previousElementSibling!==start)start.after(entry);
 return true;
}
function se271EnsurePreview(){
 const root=seLevels.preview;
 if(!root||!root.classList?.contains('st141-preview'))return false;
 const panel=root.querySelector('.st141-menu-panel');if(!panel)return false;
 let button=panel.querySelector('#se271PreviewLan');
 if(button)return true;
 button=document.createElement('button');button.type='button';
 button.id='se271PreviewLan';button.className='se271-lan-primary';
 button.textContent='LOCAL LAN · FIND GAMES';
 button.setAttribute('aria-label','Open Local LAN multiplayer from Sheep Tag menu preview');
 button.addEventListener('click',event=>{
   event.stopPropagation();event.preventDefault();
   if(!seLevelsOwns()||seLevelsCurrent()?.role!=='menu'||playing||simulating||stSession)return;
   const launched=seLevels.playingMenu||seLevelsPlayMenu();
   if(launched&&se146Open()){se271LanUI.previewOpens++;se271LanUI.status='preview opened LAN';}
   else {se271LanUI.failedStarts++;se271LanUI.status='Cannot open LAN until Sheep Tag Main Menu is ready';}
 });
 panel.appendChild(button);
 return true;
}
function se271Styles(){
 if(document.getElementById('se271LanStyles'))return;
 const style=document.createElement('style');style.id='se271LanStyles';
 style.textContent=[
  '#st141RuntimeMenu .st141-menu-panel .se271-lan-primary,',
  '#st141MenuPreview .st141-menu-panel .se271-lan-primary{',
  'display:block!important;width:min(100%,390px)!important;min-height:52px!important;',
  'margin:14px auto 0!important;padding:12px 16px!important;',
  'font:bold 16px system-ui,sans-serif!important;',
  'letter-spacing:.055em!important;text-transform:none!important;',
  'background:#184d52!important;color:#eefff7!important;',
  'border:2px solid #6ce6d4!important;border-radius:13px!important;',
  'box-shadow:0 4px 0 #08272a!important;cursor:pointer!important;',
  'pointer-events:auto!important;visibility:visible!important;opacity:1!important;',
  '}',
  '#st141MenuPreview .st141-menu-panel #se271PreviewLan{',
  'position:relative;z-index:5;pointer-events:auto!important;touch-action:manipulation;',
  '}',
  '#st141RuntimeMenu .se146-screen .se271-discovery-heading{',
  'font-weight:800;color:#a7ffee;letter-spacing:.06em;',
  '}'
 ].join('');
 document.head.appendChild(style);
}
function se271LabelDiscovery(){
 const root=se146Lan.root;if(!root)return;
 const head=root.querySelector('.se146-list-head b');
 if(head)head.textContent=location.protocol==='https:'?
   'AUTO-FIND OPEN GAMES':'AUTO-FIND LOCAL LAN GAMES';
 const scan=root.querySelector('#se146LanRefresh');
 if(scan)scan.textContent='↻ Scan Again';
 const hint=root.querySelector('#se271LanHint')||document.createElement('p');
 if(!hint.id){
   hint.id='se271LanHint';hint.className='se146-status';
   root.querySelector('.se146-list-head')?.after(hint);
 }
 hint.textContent=location.protocol==='https:'?
   'Auto-discovery uses the shared public network exit. It is not a private Wi-Fi scan. If no room appears, use the host invite code.':
   'Auto-scanning the local Wi-Fi Bridge for open rooms. Both devices must use the Bridge network.';
}
function se271Discover(){
 if(!se146Lan.active)return false;
 se271LanUI.discoveryRequests++;
 se271LabelDiscovery();
 // Existing code already automatically refreshes and owns the peer roster.
 // Make a real directory probe on open; no fabricated local hosts.
 if(location.protocol==='https:'){
   Promise.resolve(se159Start()).then(()=>{
     if(!se146Lan.active)return;
     if(se159.connected)se159Probe();
     se159Draw();
     se271LabelDiscovery();
   }).catch(error=>{se271LanUI.status='directory unavailable: '+String(error);});
 }else{
   void se146Scan(true);
 }
 return true;
}
const se271InstallBase=se146Install;
se146Install=function(...args){
 const result=se271InstallBase(...args);
 se271Styles();se271ShowBrowserButton(args[0]||seLevels.overlay);
 se271LabelDiscovery();
 return result;
};
const se271PlayBase=seLevelsPlayMenu;
seLevelsPlayMenu=function(...args){
 const result=se271PlayBase(...args);
 if(result){se271Styles();se271ShowBrowserButton(seLevels.overlay);}
 return result;
};
const se271EnsureUIBase=seLevelsEnsureUI;
seLevelsEnsureUI=function(...args){
 const result=se271EnsureUIBase(...args);
 se271Styles();se271EnsurePreview();
 return result;
};
const se271LanOpenBase=se146Open;
se146Open=function(...args){
 const opened=se271LanOpenBase(...args);
 if(opened){se271LanUI.runtimeOpens++;se271Discover();}
 return opened;
};
// Keep visible header coherent as asynchronous directory scans finish.
const se271ScanBase=se146Scan;
se146Scan=async function(...args){
 const result=await se271ScanBase(...args);
 if(se146Lan.active)se271LabelDiscovery();
 return result;
};

function se271XRMenu(){
 return renderer.xr.isPresenting&&se193XRMenuActive()&&
   se195.mode==='menu'&&se195.page==='main'&&se195.visible;
}
function se271TileDispose(){
 const tile=se271LanUI.tile;if(!tile)return;
 scene.remove(tile.root);tile.mesh.geometry.dispose();tile.mesh.material.dispose();
 tile.texture.dispose();se271LanUI.tile=null;
}
function se271TileCreate(){
 if(se271LanUI.tile)return se271LanUI.tile;
 if(!se271XRMenu())return null;
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
 se271LanUI.tile={root,mesh,texture};
 return se271LanUI.tile;
}
function se271TileHit(cast){
 const t=se271LanUI.tile;if(!t||!se271XRMenu()||!cast?.ray)return null;
 t.root.updateMatrixWorld(true);
 const hits=cast.ray.intersectObject(t.mesh,false);
 if(!hits.length)return null;
 return {ui:'se195:lanPage',distance:hits[0].distance,
   point:hits[0].point,button:t.mesh};
}
const se271PreviousRadialHit=se195RadialHit;
se195RadialHit=function(record,cast=se192Ray(record)){
 const primary=se271PreviousRadialHit(record,cast);
 const tile=se271TileHit(cast);
 // Preserve nearer radial controls and its modal backdrop.
 if(tile&&(!primary||tile.distance<primary.distance-.02))return tile;
 return primary;
};
const se271OldAction=se195HandleAction;
se195HandleAction=function(action,record){
 if(action==='lanPage'&&se271XRMenu()){
   se271LanUI.xrOpens++;
   se271TileDispose();
 }
 return se271OldAction(action,record);
};
const se271FrameBase=se193XRFrame;
se193XRFrame=function(...args){
 const result=se271FrameBase(...args);
 if(se271XRMenu())se271TileCreate();
 else se271TileDispose();
 return result;
};
const se271CleanupBase=se193XRCleanup;
se193XRCleanup=function(...args){
 se271TileDispose();
 return se271CleanupBase(...args);
};
se271Styles();
se271EnsurePreview();
window.SWYRL_ENGINE_SHEEP_LAN_VISIBILITY_271=Object.freeze({
 diagnose:()=>({
   browserPreviewButton:!!document.querySelector('#se271PreviewLan'),
   runtimeButton:!!seLevels.overlay?.querySelector('#se146LanOpen'),
   runtimeOpen:!!se146Lan.active,vrTile:!!se271LanUI.tile,
   xrPage:se195.page,roomDirectoryConnected:!!se159.connected,
   discoveredRooms:se159.rooms?.size||0,
   autoDiscovery:se271LanUI.discoveryRequests,
   previewOpens:se271LanUI.previewOpens,
   runtimeOpens:se271LanUI.runtimeOpens,
   vrOpens:se271LanUI.xrOpens,
   lastStatus:se271LanUI.status,
   scanType:location.protocol==='https:'?'shared public network (not subnet)':'local HTTP bridge'
 })
});
