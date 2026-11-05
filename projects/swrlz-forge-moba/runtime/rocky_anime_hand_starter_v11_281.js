// §E v11.281 · Rocky Anime Hand. Independently editable, native rigged
// Model Atelier starter derived from the generated multi-view concept sheet.
// Chiseled indexed stone facets and amber fissures are 3D geometry, not sprites.
// The source Arcane Glove starter and its VR controller rig are not modified.
const se281RockId='rocky-anime-hand';
const se281RockColors=Object.freeze({
 core:'#47414e',shadow:'#312d38',stone:'#716a78',
 stoneMid:'#807987',light:'#a39ba9',edge:'#c1b4bb',
 deep:'#544d5b',amber:'#ffb548',flame:'#ffde86'
});
const se281Rounding=n=>Math.round(n*100000)/100000;
// A low-poly bevelled block, with real outward-facing side facets and a
// raised offset front face. Independent indexed mesh for sculpt/material tools.
function se281RockTopology(center,rx,ry,depth,front,angle,seed){
 const count=9,vertices=[],uvs=[],indices=[];
 const nudge=i=>.86+.13*Math.sin(i*2.29+seed*1.7)+.065*Math.cos(seed*3.7+i*1.81);
 const rotate=([x,y])=>[x*Math.cos(angle)-y*Math.sin(angle),
   x*Math.sin(angle)+y*Math.cos(angle)];
 const vertex=(x,y,z)=>{
  const [dx,dy]=rotate([x,y]);
  vertices.push(se281Rounding(center[0]+dx),se281Rounding(center[1]+dy),
    se281Rounding(center[2]+z));
  uvs.push((x/rx+1)*.5,(y/ry+1)*.5);
  return vertices.length/3-1;
 };
 const outer=[],bevel=[],back=[];
 for(let i=0;i<count;i++){
  const a=i*Math.PI*2/count+.12*Math.sin(seed);
  const v=nudge(i);
  outer.push(vertex(rx*Math.cos(a)*v,ry*Math.sin(a)*v,front*depth*.11));
 }
 for(let i=0;i<count;i++){
  const a=i*Math.PI*2/count+.12*Math.sin(seed),v=nudge(i);
  bevel.push(vertex(rx*Math.cos(a)*v*.82,ry*Math.sin(a)*v*.82,
    front*depth*.48));
 }
 const centerId=vertex(.05*rx*Math.sin(seed),.04*ry*Math.cos(seed),front*depth*.57);
 for(let i=0;i<count;i++){
  const a=i*Math.PI*2/count+.12*Math.sin(seed),v=nudge(i);
  back.push(vertex(rx*Math.cos(a)*v*.95,ry*Math.sin(a)*v*.95,
    -front*depth*.52));
 }
 const tri=(a,b,c,side)=>{if(side>0)indices.push(a,b,c);else indices.push(a,c,b);};
 for(let i=0;i<count;i++){
  const j=(i+1)%count;
  tri(outer[i],outer[j],bevel[i],front);
  tri(bevel[i],outer[j],bevel[j],front);
  tri(bevel[i],bevel[j],centerId,front);
  tri(back[i],back[j],outer[i],-front);
  tri(outer[i],back[j],outer[j],-front);
 }
 for(let i=1;i<count-1;i++)tri(back[0],back[i],back[i+1],-front);
 return {positions:vertices,uvs,indices};
}
// Sculptable connected line along a fissure; it is an actual 3D tube with
// carefully bounded per-segment geometry, not a shader-only stroke.
function se281CrackTopology(path,radius){
 const xyz=[],uv=[],idx=[],sides=5,points=path.map(p=>new THREE.Vector3(...p));
 for(let i=0;i<points.length;i++){
  const prev=points[Math.max(i-1,0)],next=points[Math.min(i+1,points.length-1)];
  const tangent=next.clone().sub(prev).normalize();
  if(tangent.lengthSq()<1e-6)tangent.set(0,1,0);
  let axis=new THREE.Vector3(0,0,1);
  if(Math.abs(tangent.dot(axis))>.94)axis.set(1,0,0);
  const tangentU=new THREE.Vector3().crossVectors(tangent,axis).normalize();
  const tangentV=new THREE.Vector3().crossVectors(tangent,tangentU).normalize();
  for(let k=0;k<sides;k++){
   const theta=k*Math.PI*2/sides;
   const v=points[i].clone().addScaledVector(tangentU,radius*Math.cos(theta))
      .addScaledVector(tangentV,radius*Math.sin(theta));
   xyz.push(se281Rounding(v.x),se281Rounding(v.y),se281Rounding(v.z));
   uv.push(k/sides,i/(points.length-1));
   if(i>0){const a=(i-1)*sides+k,b=(i-1)*sides+(k+1)%sides;
    idx.push(a,b,a+sides,b,b+sides,a+sides);}
  }
 }
 // Explicit capped tips so every glowing seam remains solid mesh geometry.
 const end=(i,reverse)=>{
  const center=xyz.length/3,p=points[i];xyz.push(p.x,p.y,p.z);uv.push(.5,i/(points.length-1));
  for(let k=0;k<sides;k++){
   const a=i*sides+k,b=i*sides+(k+1)%sides;
   if(reverse)idx.push(center,b,a);else idx.push(center,a,b);
  }
 };
 end(0,true);end(points.length-1,false);
 return {positions:xyz,uvs:uv,indices:idx};
}
function se281RockScene(){
 const scene=se212HandScene();
 const m=scene.project.modelAtelier,original=m.parts;
 const core=original.find(p=>p.organicSurface&&p.kind==='topologyMesh');
 if(!core||!se220RigValidate(m.rigging))
  throw Error('The native organic hand or 17-joint rig is unavailable.');
 const C=se281RockColors;
 const parts=[],name='Rocky Anime Hand · Emberstone',num=()=>String(parts.length).padStart(3,'0');
 const add=(title,color,material,group,topologyMesh)=>{
  const part={id:'rock-hand-'+num(),name:title,kind:'topologyMesh',
   position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],
   color,material,group,topologyMesh};
  parts.push(part);return part;
 };
 const plate=(title,p,w,h,d,side,color,group,theta=0,seed=1)=>{
  return add(title,color,'silk',group,se281RockTopology(p,w,h,d,side,theta,seed));
 };
 const seam=(title,route,thickness,group,hot=false)=>{
  return add(title,hot?C.flame:C.amber,'emissive',group,
   se281CrackTopology(route,thickness));
 };
 const sub=(tag,face,coord,w,h,d,color,theta,seed)=>{
  const side=face==='dorsal'?-1:1,group=face==='dorsal'?'Back / faceted rocks':'Palm / faceted rocks';
  return plate(tag,[coord[0],coord[1],side*.306],w,h,d,side,color,group,theta,seed);
 };
 // Only preserve the connected organic silhouette (not the Arcane Glove's
 // armored sigils, decorations or floating wrist rings).
 add('Underlying shadow-stone · continuous anatomical thumb and fingers',
   C.core,'silk','Structure / connected rock',structuredClone(core.topologyMesh));
 // Large overlapping asymmetric polygonal plates cover BOTH the back and palm.
 // Individual stone shapes are separate editable mesh parts.
 const slabs=[
  ['heel',[-.03,1.23],.33,.28,.02,C.deep,1],
  ['heart',[0,1.75],.35,.42,-.04,C.stone,2],
  ['index knuckle',[-.36,2.09],.20,.19,-.16,C.stoneMid,3],
  ['middle knuckle',[-.11,2.17],.20,.20,.09,C.light,4],
  ['ring knuckle',[.16,2.14],.19,.19,-.07,C.stone,5],
  ['little knuckle',[.39,2.06],.15,.16,.17,C.deep,6],
  ['radial shield',[-.38,1.67],.23,.31,-.18,C.stoneMid,7],
  ['ulnar shield',[.39,1.66],.21,.31,.16,C.deep,8],
  ['lower diagonal slab',[-.14,1.48],.22,.26,-.31,C.light,9],
  ['upper diagonal slab',[.22,1.90],.19,.26,.30,C.stoneMid,10]
 ];
 for(const face of ['dorsal','palm']){
  for(const [label,p,w,h,theta,color,seed] of slabs){
   const dx=face==='palm'?-.014:0;
   sub((face==='palm'?'Palm':'Back')+' · '+label+' chiseled stone',
     face,[p[0]+dx,p[1]],w*(face==='palm'?.93:1),
     h*(face==='palm'?.93:1),.17,color,theta,seed+(face==='palm'?23:0));
  }
 }
 // Explicit shining V cracks cross the dorsal central palm plates.
 seam('Back · main branching magma split',
  [[-.25,2.03,-.411],[-.13,1.89,-.418],[.025,1.78,-.425],
   [.06,1.64,-.415],[.22,1.52,-.404]],.014,'Energy / back fissures');
 seam('Back · bright Y fork',
  [[-.13,1.89,-.422],[-.30,1.90,-.416],[-.40,2.06,-.393]],.009,'Energy / back fissures');
 seam('Back · lower slant',
  [[.05,1.63,-.417],[-.06,1.49,-.410],[-.09,1.31,-.393]],.011,'Energy / back fissures');
 seam('Palm · thumb-web glow',
  [[-.42,1.90,.417],[-.27,1.73,.429],[-.17,1.62,.428],[-.30,1.45,.411]],
  .010,'Energy / palm fissures');
 seam('Palm · radiant core crack',
  [[.17,2.03,.416],[.045,1.84,.435],[.21,1.70,.427],[.15,1.51,.415]],
  .013,'Energy / palm fissures',true);
 // Wrist cuff: interlocking dark gray rock chunks with seams, no armor rings.
 for(const [i,y] of [.68,.88,1.07].entries()){
  const u=.31-i*.016;
  for(const sign of [-1,1]){
   plate('Wrist tier '+(i+1)+' · '+(sign<0?'back':'front')+' slab',
     [0,y,sign*.272],u,.16,.18,sign,i===1?C.stone:C.deep,
     'Wrist / interlocking basalt',i===1?.11:-.08,12+i+sign);
   if(i<2)seam('Wrist · amber fault '+i+' '+sign,
     [[-.21,y+.08,sign*.38],[-.04,y+.105,sign*.40],
      [.14,y+.082,sign*.39],[.25,y+.07,sign*.35]],
     .010,'Energy / wrist joints');
  }
 }
 // Finger phalanges have individually segmented rigid rocky armor. Each
 // separate slab sits over the existing deformable index/middle/ring/pinky bones.
 const digit=m.rigging.digits;
 for(const [i,f] of digit.entries()){
  const h=f.to-f.from;
  const segments=[
   {a:.045,b:.48,key:'proximal',width:1.46},
   {a:.525,b:.765,key:'middle',width:1.22},
   {a:.805,b:.975,key:'distal',width:1.02}
  ];
  for(const [j,seg] of segments.entries()){
   const t=(seg.a+seg.b)*.5;
   const x=f.x+f.splay*t,y=f.from+h*t;
   const radius=f.r*seg.width;
   const depth=j===0?.14:j===1?.115:.095;
   for(const side of [-1,1]){
    const face=side<0?'back':'palm';
    plate('Finger '+f.name+' · '+seg.key+' '+face+' stone',
      [x,y,f.z+side*(f.r+depth*.53)],
      radius,Math.max(.066,h*(seg.b-seg.a)*.52),depth,side,
      [C.stone,C.light,C.stoneMid,C.deep][(i+j+(side>0?1:0))%4],
      'Fingers / '+f.name+' rock segments',
      f.splay*.17,30+i*10+j+(side>0?60:0));
   // Tip-to-root fracture lines mark each actual joint; gaps stay flexible
   // while the underlying connected organic shell is skinned to 17 bones.
   if(j<2){
    const yy=f.from+h*(j===0?.505:.786);
    seam('Finger '+f.name+' · '+seg.key+' amber joint · '+face,
      [[x-f.r*.82,yy,f.z+side*(f.r+.049)],
       [x,yy+.012,f.z+side*(f.r+.07)],
       [x+f.r*.76,yy-.016,f.z+side*(f.r+.048)]],
      .009,'Energy / articulated knuckles');
   }
  }
  }
 }
 // Angular thumb pads follow the angled CMC/MCP/IP skeleton, rather than
 // stacking vertical blocks. Four-view silhouette keeps the thumb readable.
 const thumbPoints=[
  [-.56,1.56,.13],[-.83,1.78,.18],[-1.015,1.95,.22],[-1.12,2.065,.235]
 ];
 for(let i=0;i<3;i++){
  const a=thumbPoints[i],b=thumbPoints[i+1],dx=b[0]-a[0],dy=b[1]-a[1];
  const length=Math.hypot(dx,dy);
  const angle=Math.atan2(-dx,dy);
  const center=[(a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2];
  for(const side of [-1,1]){
   plate('Thumb · '+['root','middle','tip'][i]+' rock '+(side<0?'back':'palm'),
    [center[0],center[1],center[2]+side*.116],
    .185-i*.027,length*.60,.13-i*.012,side,
    [C.stoneMid,C.stone,C.light][i],'Thumb / angular segments',
    angle,105+i*3+side);
  }
  if(i<2)seam('Thumb · glowing joint '+(i+1),
    [[b[0]-.073,b[1]-.037,b[2]+.216],
     [b[0],b[1]+.008,b[2]+.239],
     [b[0]+.06,b[1]+.028,b[2]+.216]],
     .012,'Energy / articulated thumb');
 }
 // Discrete stone shards at the palm edge reinforce the chunky fantasy
 // anime silhouette without relying on textures or postprocessing.
 for(const side of [-1,1]){
  for(let i=0;i<3;i++){
   const y=1.37+i*.23,x=side*(.47-(i===2?.045:0));
   plate('Lateral edge · chipped rock '+(side<0?'thumb':'little')+' '+(i+1),
    [x,y,-.02],.125,.158,.15,side,
    i===1?C.light:C.deep,'Side / broken stone edges',
    side*.36,135+i+side*5);
  }
 }
 if(parts.length>230)throw Error('Rocky Hand exceeds native part budget.');
 m.name=name;m.parts=parts;
 m.meshGroups=[...new Set(parts.map(p=>p.group))].map((group,i)=>({
  id:'rock-hand-group-'+i,name:group,
  members:parts.filter(p=>p.group===group).map(p=>p.id)
 })).filter(group=>group.members.length>=2);
 m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';
 m.reference='Native geometry adaptation of the user-requested rocky anime hand reference: faceted gray-violet stones, separate finger joints, molten amber fissures. This is a modeled interpretation, not a pixel-perfect reconstruction.';
 // Inherit the real 17-bone Rig Studio skeleton and editable open–fist–open
 // timeline; do not copy the glove's visual armor, runes, or hover rings.
 if(!se220RigValidate(m.rigging))throw Error('Rock hand rig failed native validation.');
 scene.project.name=name;
 scene.project.canonicalId=se281RockId;scene.project.template=se281RockId;
 scene.project.kind='model-atelier';
 scene.project.environmentSettings={...scene.project.environmentSettings,
  showTerrain:false,showScenery:false,background:'#171522'};
 scene.engine='§wyrl§ Engine · Maker v11.281';scene.version=11.281;
 return scene;
}
function se281OpenRockyHand(force=false){
 if(dirty&&!force&&!confirm('Open Rocky Anime Hand and discard unsaved scene changes?'))return false;
 try{
  const source=se281RockScene();
  ModelAtelier.close();loadProject(source,{workspaceLocal:true});
  initializeHistory('Opened Rocky Anime Hand · Emberstone starter');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  se232ActivateSelectedModelWorkspace();
  ModelAtelier.syncProject();
  requestAnimationFrame(()=>requestAnimationFrame(()=>
    window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast('Rocky Anime Hand · editable chiseled stones + amber seams + 17-bone animation rig');
  return true;
 }catch(error){
  console.error('Rocky hand starter',error);
  toast('Cannot open Rocky Anime Hand: '+String(error.message||error).slice(0,120));
  return false;
 }
}
const se281PreviousTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(id,force=false){
 if(id===se281RockId)return se281OpenRockyHand(force);
 return se281PreviousTemplate(id,force);
};
window.SWYRL_ENGINE_ROCK_HAND=Object.freeze({
 id:se281RockId,createScene:se281RockScene,open:se281OpenRockyHand,
 inspect:()=>({template:se281RockId,
  inProject:currentProject?.canonicalId===se281RockId||
    currentProject?.template===se281RockId,
  rigReady:typeof se220RigValidate==='function',
  templateCard:!!document.querySelector('[data-project-template="rocky-anime-hand"]')})
});
