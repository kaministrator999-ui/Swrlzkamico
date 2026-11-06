// §E v11.301: authored mapped game textures, softer face and neutral wrists.
// Native 17-part starter only. No cut-and-paste of photographed concept objects.
// Historic v11.300 stays intact; saved scenes remain unchanged.
const se301Result={version:'v11.301',retouchedFamilies:0,correctedHands:0,
 faceGeometryAdjusted:false,source:'hand-designed native UV artwork; reference color guide',
 visualAcceptance:false};
function se301Path(ctx,pts,color,width=2){
 ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);
 for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);
 ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineCap='round';ctx.lineJoin='round';ctx.stroke();
}
function se301Bezier(ctx,p,color,width=2){
 ctx.beginPath();ctx.moveTo(p[0],p[1]);
 ctx.bezierCurveTo(p[2],p[3],p[4],p[5],p[6],p[7]);
 ctx.lineCap='round';ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();
}
function se301Oval(ctx,x,y,rx,ry,color,outline){
 ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);
 ctx.fillStyle=color;ctx.fill();
 if(outline){ctx.strokeStyle=outline;ctx.lineWidth=1;ctx.stroke();}
}
function se301Fill(ctx,stops){
 const gradient=ctx.createLinearGradient(0,0,110,384);
 for(const [at,color] of stops)gradient.addColorStop(at,color);
 ctx.fillStyle=gradient;ctx.fillRect(0,0,384,384);
}
function se301Border(ctx,gold='#be9e6c'){
 se301Path(ctx,[[13,372],[13,13],[371,13],[371,372],[13,372]],'rgba(34,39,43,.48)',11);
 se301Path(ctx,[[16,370],[16,16],[368,16],[368,370],[16,370]],gold,4);
}
// Paint by the actual current mesh's local UVs. There are no photographic
// cutout faces, page edges, entire image rectangles, or projected body parts.
se300DrawArtwork=function(_reference,family,canvas){
 const ctx=canvas.getContext('2d');
 if(!ctx)throw Error('No UV painting context for '+family);
 switch(family){
 case 'skin': {
  se301Fill(ctx,[[0,'#e6c1ad'],[.35,'#dcb7a3'],[.68,'#d2a994'],[1,'#bf9381']]);
  // Head UV longitude front = x 192; back seam = x 0/384.
  // Both eyes, brow, nose, lips intentionally restricted to x 152..232.
  for(const x of [170,214]){
   se301Bezier(ctx,[x-17,146,x-7,139,x+7,139,x+17,146],'#67483b',2.8);
   se301Bezier(ctx,[x-14,161,x-6,154,x+6,155,x+14,161],'#795447',2.0);
   se301Oval(ctx,x,166,10.8,5.8,'#f5efea','#c7a596');
   se301Oval(ctx,x,166,4.8,5.4,'#6e8791');
   se301Oval(ctx,x,166,2.4,4.4,'#314b58');
   se301Oval(ctx,x-1.7,163.9,1.6,1.5,'rgba(255,255,255,.86)');
   se301Bezier(ctx,[x-12,175,x-3,177,x+7,176,x+12,173],'rgba(154,106,94,.23)',.9);
  }
  se301Oval(ctx,149,205,17,9,'rgba(177,93,92,.09)');
  se301Oval(ctx,236,205,17,9,'rgba(177,93,92,.09)');
  se301Bezier(ctx,[190,189,187,197,187,209,193,212],'rgba(130,80,73,.35)',1.4);
  se301Bezier(ctx,[193,212,195,213,198,213,200,211],'rgba(137,82,79,.34)',1);
  se301Bezier(ctx,[177,256,185,260,201,259,208,255],'#9b6a67',1.9);
  se301Bezier(ctx,[179,259,192,262,201,263,205,258],'rgba(210,142,132,.44)',1);
  break;
 }
 case 'hair':{
  se301Fill(ctx,[[0,'#261f1c'],[.4,'#4d3930'],[.72,'#352820'],[1,'#241e1b']]);
  for(let x=0;x<405;x+=18){
   se301Bezier(ctx,[x,4,x-21,99,x+18,211,x-12,385],
    x%3?'rgba(173,125,91,.23)':'rgba(211,153,106,.27)',1.5);
  }
  break;
 }
 case 'hood':{
  se301Fill(ctx,[[0,'#f1eee7'],[.32,'#dedbd4'],[.65,'#e9e5db'],[1,'#c9c5c0']]);
  for(let x=33;x<390;x+=49)
   se301Bezier(ctx,[x,7,x-13,116,x+9,214,x-5,383],'rgba(114,113,107,.13)',3.4);
  se301Border(ctx,'#cab08a');
  se301Path(ctx,[[30,26],[355,26]],'rgba(255,255,255,.7)',2);
  break;
 }
 case 'scarf':{
  se301Fill(ctx,[[0,'#f0f1eb'],[.31,'#dfe0de'],[.69,'#c5cdd0'],[1,'#e8e6e1']]);
  for(let y=17;y<400;y+=55){
   se301Bezier(ctx,[-9,y,92,y+18,256,y-12,397,y+16],'rgba(102,116,129,.24)',5);
   se301Bezier(ctx,[-9,y+9,92,y+26,256,y-5,397,y+23],'rgba(255,255,251,.6)',3);
  }
  se301Path(ctx,[[16,368],[192,376],[368,368]],'#b8a27a',2);
  break;
 }
 case 'uniform':{
  se301Fill(ctx,[[0,'#48525a'],[.26,'#333f46'],[.65,'#343d44'],[1,'#292d33']]);
  for(let x=25;x<391;x+=50)
   se301Bezier(ctx,[x,4,x-8,125,x+7,255,x,382],'rgba(167,178,177,.05)',1.5);
  se301Bezier(ctx,[48,0,62,126,45,274,55,383],'rgba(157,170,173,.15)',2.2);
  se301Bezier(ctx,[333,0,318,126,338,274,329,383],'rgba(157,170,173,.15)',2.2);
  break;
 }
 case 'armor':{
  se301Fill(ctx,[[0,'#64727a'],[.19,'#384651'],[.56,'#2b3943'],[1,'#293744']]);
  se301Border(ctx,'#c1a16d');
  se301Bezier(ctx,[35,75,116,113,264,113,350,75],'#b7a06c',3.2);
  se301Bezier(ctx,[40,91,129,135,254,136,347,91],'rgba(84,152,153,.52)',3);
  for(let j=0;j<3;j++){
   const y=148+j*62;
   se301Bezier(ctx,[44,y,126,y+6,168,y+18,192,y+28],'#121f2a',7);
   se301Bezier(ctx,[340,y,258,y+6,216,y+18,192,y+28],'#121f2a',7);
   se301Bezier(ctx,[49,y-5,126,y,169,y+11,192,y+20],'#ab996f',2.3);
   se301Bezier(ctx,[335,y-5,258,y,215,y+11,192,y+20],'#ab996f',2.3);
  }
  se301Path(ctx,[[192,119],[224,165],[192,205],[160,165],[192,119]],'#cbb07d',2.5);
  se301Path(ctx,[[192,135],[209,165],[192,186],[175,165],[192,135]],'rgba(54,131,133,.72)',4);
  se301Path(ctx,[[58,320],[192,344],[326,320]],'#b7a16f',3);
  break;
 }
 case 'pauldron':{
  se301Fill(ctx,[[0,'#66747c'],[.42,'#465660'],[.77,'#30404d'],[1,'#26313a']]);
  se301Border(ctx,'#c3a573');
  se301Bezier(ctx,[28,90,119,58,268,58,355,90],'#d3b681',4);
  se301Bezier(ctx,[34,113,123,91,261,93,348,113],'rgba(24,117,125,.74)',9);
  se301Bezier(ctx,[44,273,130,291,258,291,340,273],'#a78d68',3);
  break;
 }
 case 'teal':{
  se301Fill(ctx,[[0,'#26868d'],[.23,'#1d737c'],[.59,'#175d65'],[1,'#164950']]);
  for(let x=34;x<390;x+=64)
   se301Bezier(ctx,[x,2,x+10,118,x-12,266,x+5,382],'rgba(115,200,194,.12)',2);
  se301Border(ctx,'#cead6d');
  for(let x=60;x<351;x+=56)
   se301Path(ctx,[[x,321],[x+12,335],[x,348],[x-12,335],[x,321]],
    'rgba(198,177,121,.46)',1.25);
  break;
 }
 case 'leather':{
  se301Fill(ctx,[[0,'#624a3c'],[.45,'#4c352c'],[1,'#302723']]);
  ctx.fillStyle='#c2a774';ctx.fillRect(166,143,51,91);
  ctx.fillStyle='#49382a';ctx.fillRect(173,150,37,77);
  ctx.fillStyle='#d1b77d';ctx.fillRect(185,165,8,43);
  break;
 }
 case 'gloves':{
  se301Fill(ctx,[[0,'#f0efe9'],[.4,'#ddddda'],[.76,'#cbd0d2'],[1,'#b0b6b8']]);
  for(const y of [58,114,170,246,310])
   se301Bezier(ctx,[18,y,106,y+10,252,y+8,369,y-6],'rgba(114,123,129,.18)',2);
  break;
 }
 case 'boots':{
  se301Fill(ctx,[[0,'#514239'],[.41,'#342d2b'],[.77,'#40352d'],[1,'#232126']]);
  se301Border(ctx,'#b8a178');
  se301Path(ctx,[[192,30],[200,123],[187,250],[194,360]],'rgba(175,153,120,.34)',2);
  se301Bezier(ctx,[35,240,130,254,252,252,346,240],'#bba177',3);
  break;
 }
 default:throw Error('Unknown custom UV art material '+family);
 }
};
// Rebuild paint synchronously instead of depending on a 512px JPEG that
// contained preview photographs. The concept art remains the palette guide.
se300InitArt=function(){
 if(!se301Result.retouchedFamilies){
  for(const family of Object.keys(se300Families)){
   const atlas=se300Canvas();
   se300DrawArtwork(null,family,atlas);
   se300Atlases.set(family,atlas);
  }
  se301Result.retouchedFamilies=se300Atlases.size;
  se300Status.materialSource='purpose-painted game surfaces matching native UVs';
  se300Status.paintedFamilies=se300Atlases.size;
  se300Status.created=se300Atlases.size;
  se300Status.imageReady=true;
  se300Status.imageError=null;
 }
 // Materials are instantiated lazily: synchronize EVERY late-loaded material
 // with its authored atlas, not only the first one created on this page.
 for(const [family,texture] of se300MaterialTex){
  const atlas=se300Atlases.get(family);
  if(!atlas)throw Error('Missing UV painting for '+family);
  if(texture.image!==atlas){texture.image=atlas;texture.needsUpdate=true;}
 }
};
const se301SceneBefore=se291HeroScene;
se291HeroScene=function(){
 const scene=se301SceneBefore(),parts=scene?.project?.modelAtelier?.parts;
 if(!Array.isArray(parts)||parts.length!==17||
    !parts.every(p=>p.id.startsWith('vanguard-rebuilt-')))
  throw Error('v11.301 expected 17-part native Hooded Vanguard');
 // Retouch the real head silhouette: broader jaw/cheeks and a smaller
 // sculpted nose, keeping local cylindrical UV longitude front at 0.5.
 const face=se300Ribbon(54,96,(latitude,longitude)=>{
  const angle=(longitude-.5)*Math.PI*2,
   lat=(latitude-.5)*Math.PI,
   ring=Math.pow(Math.max(.006,Math.cos(lat)),.65);
  const jaw=1-.075*Math.pow(Math.max(0,.33-latitude)/.33,1.3);
  const cheek=1+.055*Math.exp(-Math.pow((latitude-.56)/.16,2));
  const forehead=1+.012*Math.exp(-Math.pow((latitude-.72)/.17,2));
  const nose=.019*Math.exp(-Math.pow((latitude-.46)/.075,2)-Math.pow(angle/.14,2));
  return [.258*ring*jaw*cheek*Math.sin(angle),
   3.82+.695*latitude,
   .054+.219*ring*forehead*Math.cos(angle)+nose];
 });
 parts[1].topologyMesh=face;
 parts[1].name='Vanguard / face · refined jaw and custom front-only UV portrait';
 parts[1].heroPBR={...parts[1].heroPBR,
  art:'stylized face painting positioned against native latitude and longitude'};
 se301Result.faceGeometryAdjusted=true;
 // The neutral wrist points where the forearm points. The earlier mesh had
 // globally down-facing fingers, even with diagonally outstretched arms.
 // Rotate both five-digit palm meshes about the existing cuff/wrist point.
 for(const [index,side] of [[13,-1],[14,1]]){
  const p=parts[index],g=p.topologyMesh,points=g?.positions;
  if(!Array.isArray(points)||points.length<60)
   throw Error('Missing actual hand topology for '+p?.name);
  const wristX=side*.86,wristY=2.73;
  const angle=side*.64,cs=Math.cos(angle),sn=Math.sin(angle);
  // Light scale also reduces previously oversized finger lengths.
  for(let i=0;i<points.length;i+=3){
   const dx=(points[i]-wristX)*.95,dy=(points[i+1]-wristY)*.95;
   points[i]=+(wristX+dx*cs-dy*sn).toFixed(6);
   points[i+1]=+(wristY+dx*sn+dy*cs).toFixed(6);
   points[i+2]=+(points[i+2]*.97).toFixed(6);
  }
  p.name=side<0?'Vanguard / hands · left aligned neutral wrist':
    'Vanguard / hands · right aligned neutral wrist';
  p.heroPBR={...p.heroPBR,wristPose:'forearm-aligned-A-pose',
   wristAngleRadians:angle,handScale:.95};
  se301Result.correctedHands++;
 }
 // Smaller shaped armor plate: bottom V tapers under the chest instead of
 // presenting a rigid photo rectangle across the torso.
 const breast=se300Ribbon(40,60,(u,v)=>{
  const edge=Math.abs(2*v-1),width=.237+.135*Math.sin(.82*Math.PI*u)+.055*u;
  const y=2.54+.93*u-.14*(1-u)*(1-edge);
  const fullness=Math.max(0,1-edge*edge);
  return [(2*v-1)*width,y,
   .211+.079*fullness+.028*Math.sin(Math.PI*u)*fullness-.018*u];
 });
 parts[7].topologyMesh=breast;
 parts[7].name='Vanguard / armor · tapered painted-contour breastplate';
 const model=scene.project.modelAtelier;
 model.name='Hooded Vanguard · Styled Face & Neutral Hands';
 model.reference='v11.301: softer anatomically integrated jaw, frontal UV-painted blue-gray eyes and subtle lips; 11 bespoke painted texture designs aligned to actual surfaces, no photographs or pasted magazine pieces; both five-digit hands rotated ~0.64 rad around cuffs to follow angled forearms. Refit tapered shield breastplate. Preserves 17 native editable parts, static no bird/weapon/full rig.';
 scene.project.name=model.name;scene.engine='§wyrl§ Engine · Maker v11.301';
 scene.version=11.301;
 for(const p of parts){
  const g=p.topologyMesh;
  if(g.uvs.length!==g.positions.length/3*2||
    g.indices.some(i=>i<0||i>=g.positions.length/3)||
    g.positions.some(v=>!Number.isFinite(v))||
    g.uvs.some(v=>!Number.isFinite(v)||v<0||v>1))
   throw Error('Invalid styled Vanguard native part '+p.name);
 }
 return scene;
};
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',open:se291OpenHero,createScene:se291HeroScene,
 status:()=>({...se291Stats,...se300Status,...se301Result,
  correctedHandAlignment:true,photographicCutoutTextures:false,
  editableParts:17,weapon:false,bird:false,rigged:false})
});
