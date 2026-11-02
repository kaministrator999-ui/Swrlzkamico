// §E v11.209 · Sheep Tag Quest Play quick wheels: original icon art,
// refined selection arcs, native costs/rules and very small cached glints.
// A/X hold/release timing, default input, build/skill authority unchanged.
const se209={
 icons:new Map(),decorated:0,reused:0,iconTextures:0,iconDisposals:0,
 segments:0,highlights:0,costReads:0,disabledReads:0,
 effectFrames:0,liveTextures:0,pages:0,lastSelected:''
};
function se209IconTexture(id,color){
 const key=id||'none',existing=se209.icons.get(key);
 if(existing)return existing;
 const canvas=document.createElement('canvas');canvas.width=canvas.height=128;
 const c=canvas.getContext('2d');if(!c)return null;
 const accent='#'+Number(color).toString(16).padStart(6,'0');
 const glow=c.createRadialGradient(64,58,8,64,64,59);
 glow.addColorStop(0,accent+'9a');glow.addColorStop(.63,'#152f43c0');
 glow.addColorStop(1,'#10233600');
 c.clearRect(0,0,128,128);c.fillStyle=glow;
 c.beginPath();c.arc(64,64,59,0,Math.PI*2);c.fill();
 c.strokeStyle=accent;c.lineWidth=4;
 c.globalAlpha=.88;c.beginPath();c.arc(64,64,50,0,Math.PI*2);c.stroke();
 c.globalAlpha=1;
 const house=id==='st-farm'||id==='st-income'||id==='st-fort';
 if(house){
  // Original minimal cottage silhouette, no runtime building clone.
  c.fillStyle='#e5e7cf';c.fillRect(37,57,54,40);
  c.fillStyle=accent;c.beginPath();
  c.moveTo(27,59);c.lineTo(64,30);c.lineTo(101,59);c.closePath();c.fill();
  c.fillStyle='#425b61';c.fillRect(58,69,15,28);
  c.fillStyle='#f3d58c';c.fillRect(43,67,10,10);c.fillRect(78,67,10,10);
  if(id==='st-income'){
   c.fillStyle='#ffdc74';c.beginPath();c.arc(93,35,13,0,Math.PI*2);c.fill();
   c.strokeStyle='#aa7838';c.lineWidth=3;c.beginPath();
   c.arc(93,35,8,0,Math.PI*2);c.stroke();
  }
  if(id==='st-fort'){
   c.fillStyle='#a0b9c6';
   for(let i=0;i<5;i++)c.fillRect(31+i*14,46,10,13);
   c.fillRect(31,57,66,5);
  }
 }else if(id==='split'){
  c.fillStyle='#b4f2ff';
  for(const [x,y] of [[49,61],[79,61]]){
   c.beginPath();c.moveTo(x,y-18);c.lineTo(x+14,y);
   c.lineTo(x,y+18);c.lineTo(x-14,y);c.closePath();c.fill();
  }
  c.strokeStyle='#5cd6f1';c.lineWidth=3;c.beginPath();
  c.moveTo(64,29);c.lineTo(64,94);c.stroke();
 }else if(id==='totem'){
  c.fillStyle='#75ded1';c.beginPath();
  c.moveTo(64,27);c.lineTo(86,55);c.lineTo(64,83);
  c.lineTo(42,55);c.closePath();c.fill();
  c.strokeStyle='#ead39d';c.lineWidth=7;
  c.beginPath();c.moveTo(64,81);c.lineTo(64,101);c.stroke();
  c.fillStyle='#f0dc8f';c.fillRect(45,96,38,5);
 }else{
  c.strokeStyle='#c2cad1';c.lineWidth=9;c.lineCap='round';
  c.beginPath();c.moveTo(44,44);c.lineTo(84,84);
  c.moveTo(84,44);c.lineTo(44,84);c.stroke();
 }
 const texture=new THREE.CanvasTexture(canvas);
 texture.colorSpace=THREE.SRGBColorSpace;
 texture.minFilter=THREE.LinearMipmapLinearFilter;
 texture.magFilter=THREE.LinearFilter;
 texture.generateMipmaps=true;texture.anisotropy=2;
 texture.userData.se209Icon=true;
 se209.icons.set(key,texture);se209.iconTextures++;
 se209.liveTextures=se209.icons.size;
 return texture;
}
function se209TextPlane(text,w,h){
 const map=se195Text(text);
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(w,h),
  new THREE.MeshBasicMaterial({map,transparent:true,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 mesh.renderOrder=10416;return mesh;
}
function se209DecorateWheel(panel){
 if(!panel||panel.root.userData.se209Decor){
  se209.reused++;return;
 }
 const {root,items,type}=panel,arc=2*Math.PI/items.length;
 const extra={wedges:[],icons:[],centers:[],statuses:[],glints:null};
 root.userData.se209Decor=extra;
 // Preserve existing small quick radial, but turn its plain buttons into
 // segmented holographic sectors with clear active selection.
 const header=root.children[2];
 if(header){header.position.y=.083;header.scale.setScalar(.72);}
 for(let i=0;i<items.length;i++){
  const item=items[i],a=-Math.PI/2+i*arc,entry=item.entry;
  const sector=new THREE.Mesh(
   new THREE.RingGeometry(.139,.345,18,1,a-arc/2+.055,arc-.11),
   new THREE.MeshBasicMaterial({color:entry.color,transparent:true,opacity:.13,
    depthTest:false,depthWrite:false,side:THREE.DoubleSide,
    toneMapped:false}));
  sector.renderOrder=10402;sector.position.z=.007;
  root.add(sector);extra.wedges.push(sector);se209.segments++;
  const map=se209IconTexture(entry.id,entry.color);
  const image=new THREE.Mesh(new THREE.PlaneGeometry(.108,.108),
   new THREE.MeshBasicMaterial({map,transparent:true,opacity:.9,
    depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
  image.position.set(Math.cos(a)*.205,Math.sin(a)*.205,.047);
  image.renderOrder=10409;root.add(image);extra.icons.push(image);
  // Text is outside its icon rather than laid over the collision cursor.
  item.mesh.position.set(Math.cos(a)*.316,Math.sin(a)*.316,.055);
  item.mesh.scale.setScalar(.68);item.mesh.renderOrder=10410;
  const center=new THREE.Mesh(new THREE.PlaneGeometry(.113,.113),
   new THREE.MeshBasicMaterial({map,transparent:true,opacity:1,
    depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
  center.position.set(0,-.014,.068);
  center.renderOrder=10415;center.visible=false;
  root.add(center);extra.centers.push(center);
 }
 // Compact background for the currently highlighted icon.
 const back=new THREE.Mesh(new THREE.CircleGeometry(.072,24),
  new THREE.MeshBasicMaterial({color:0x0b2530,transparent:true,opacity:.94,
   depthTest:false,depthWrite:false,side:THREE.DoubleSide,toneMapped:false}));
 back.position.z=.056;back.renderOrder=10413;root.add(back);
 const status=se209TextPlane('HOLD TO SELECT',.154,.037);
 status.position.set(0,-.112,.074);root.add(status);
 extra.status=status;extra.statusKey='HOLD TO SELECT';
 // Fixed eight glints are cheap and update rotation only while hold is active.
 const positions=new Float32Array(8*3);
 for(let k=0;k<8;k++){
  const a=k*2*Math.PI/8;
  positions[k*3]=Math.cos(a)*.357;
  positions[k*3+1]=Math.sin(a)*.357;
  positions[k*3+2]=.037;
 }
 const geo=new THREE.BufferGeometry();
 geo.setAttribute('position',new THREE.BufferAttribute(positions,3));
 const glints=new THREE.Points(geo,new THREE.PointsMaterial({
  color:0xa5fff0,size:.011,sizeAttenuation:true,transparent:true,
  opacity:.63,depthTest:false,depthWrite:false}));
 glints.renderOrder=10412;root.add(glints);extra.glints=glints;
 se209.decorated++;
}
function se209OptionStatus(panel,entry){
 if(!entry.id)return 'CANCEL';
 if(panel.type==='build'){
  const config=stBuildingConfig(entry.id,stSession?.rules);
  const price=Number(config?.cost)||0;
  const amount=Number(stSession?.resources?.[stSession?.controlledId])||0;
  se209.costReads++;
  return amount<price?'NEED '+price+' GOLD':price+' GOLD';
 }
 const enabled=se204SkillReady(entry.id);
 se209.disabledReads++;
 if(!enabled)return 'RULE LOCKED';
 if(entry.id==='totem'&&!stUi.buildingId)return 'SELECT HOUSE';
 return 'EQUIPPED';
}
function se209RefreshWheel(panel){
 const art=panel?.root?.userData?.se209Decor;
 if(!art||!panel.root.visible)return;
 const selected=panel.selected,item=panel.items[selected];
 if(!item)return;
 const text=se209OptionStatus(panel,item.entry);
 // Textures are cached by the existing Quest menu; no per-frame canvases.
 if(art.statusKey!==text){
  art.status.material.map=se195Text(text);
  art.statusKey=text;
  art.status.material.needsUpdate=true;
 }
 for(let i=0;i<panel.items.length;i++){
  const focused=i===selected,entry=panel.items[i].entry;
  const available=panel.type==='build'
   ?!entry.id||((stSession?.resources?.[stSession?.controlledId]||0)>=
    (stBuildingConfig(entry.id,stSession?.rules)?.cost||0))
   :!entry.id||se204SkillReady(entry.id);
  art.wedges[i].material.opacity=focused?.45:.09;
  art.wedges[i].scale.setScalar(focused?1.045:1);
  art.icons[i].material.opacity=available?(focused?1:.73):.28;
  art.icons[i].scale.setScalar(focused?1.10:1);
  art.centers[i].visible=focused;
 }
 se209.highlights++;se209.lastSelected=item.entry.id||'none';
}
const se209OldRoot=se204WheelRoot;
se204WheelRoot=function(type){
 const panel=se209OldRoot(type);
 se209DecorateWheel(panel);
 return panel;
};
const se209OldShow=se204WheelShow;
se204WheelShow=function(type){
 const result=se209OldShow(type);
 if(se204.wheel){se209.pages++;se209RefreshWheel(se204.wheel);}
 return result;
};
const se209OldHighlight=se204WheelHighlight;
se204WheelHighlight=function(force=false){
 const result=se209OldHighlight(force);
 se209RefreshWheel(se204.wheel);
 return result;
};
const se209OldStep=se204WheelStep;
se204WheelStep=function(record){
 const result=se209OldStep(record);
 const art=se204.wheel?.root?.userData?.se209Decor;
 if(art?.glints){
  art.glints.rotation.z=performance.now()*.00009;
  se209.effectFrames++;
 }
 return result;
};
const se209OldDispose=se204WheelDispose;
se204WheelDispose=function(){
 const out=se209OldDispose();
 for(const texture of se209.icons.values()){
  texture.dispose();se209.iconDisposals++;
 }
 se209.icons.clear();se209.liveTextures=0;
 return out;
};
window.SWYRL_ENGINE_SHEEP_RADIAL_ICONS_209=Object.freeze({
 diagnose:()=>({
  active:!!se204.wheel,cachedIconTextures:se209.liveTextures,
  newIconTextures:se209.iconTextures,disposedIcons:se209.iconDisposals,
  decoratedWheels:se209.decorated,reusedWheels:se209.reused,
  wheelSegments:se209.segments,selectionUpdates:se209.highlights,
  costReads:se209.costReads,skillAvailabilityChecks:se209.disabledReads,
  cheapEffectFrames:se209.effectFrames,currentOption:se209.lastSelected,
  gameplayBuildButton:'A hold select / tap build',
  gameplaySkillButton:'X hold select / tap skill'
 })
});
