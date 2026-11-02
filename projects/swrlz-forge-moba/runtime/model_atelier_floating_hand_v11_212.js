// §E v11.212 · Floating Hand / Arcane Glove. Native, editable Model Atelier geometry.
// Original interpretation of an owner-supplied multi-view concept, not an image billboard.
// The palm/fingers are one watertight-looking sculpted surface; armor/runes stay separate.
// Intentionally no XR input changes, animation claims, remote assets, or extra renderer.
const se212Id='floating-hand-glove';
let se212Cached=null;
function se212HandScene(){
 if(se212Cached)return structuredClone(se212Cached);
 if(typeof atelierAnimalSurface!=='function')throw Error('Native organic surface builder is unavailable.');
 const source=structuredClone(MODEL_ATELIER_CANONICAL_PROJECT);
 const m=source.project.modelAtelier,parts=[];
 const clean=(v)=>+v.toFixed(5);
 const push=(name,kind,color,material,group,extra={})=>{
  const part={id:'floating-hand-'+String(parts.length).padStart(3,'0'),name,kind,
   position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color,material,group,...extra};
  parts.push(part);return part;
 };
 const color={glove:'#181520',seam:'#383043',plate:'#4a425b',rim:'#b0a7bf',
  accent:'#a439ec',light:'#e091ff',core:'#56217e',void:'#0b0b17'};
 const ell=(p,c,r)=>{
  const v=p.map((n,i)=>(n-c[i])/r[i]);
  return (Math.hypot(...v)-1)*Math.min(...r);
 };
 const cap=(p,a,b,ra,rb)=>{
  const d=b.map((x,i)=>x-a[i]),q=p.map((x,i)=>x-a[i]);
  const k=Math.max(0,Math.min(1,q.reduce((s,x,i)=>s+x*d[i],0)/d.reduce((s,x)=>s+x*x,0)));
  return Math.hypot(...p.map((x,i)=>x-a[i]-k*d[i]))-(ra+(rb-ra)*k);
 };
 const blend=(a,b,k)=>{
  const h=Math.max(0,k-Math.abs(a-b))/k;
  return Math.min(a,b)-h*h*k*.25;
 };
 const digit=[
  {x:-.43,from:2.23,to:3.07,r:.112},
  {x:-.15,from:2.26,to:3.34,r:.118},
  {x:.15,from:2.25,to:3.23,r:.111},
  {x:.43,from:2.18,to:2.95,r:.099}
 ];
 const skin=(x,y,z)=>{
  const p=[x,y,z];
  let d=ell(p,[0,1.72,0],[.655,.605,.215]);
  d=blend(d,ell(p,[0,2.10,-.005],[.604,.26,.196]),.14);
  d=blend(d,ell(p,[.005,1.10,-.007],[.344,.51,.19]),.15);
  for(const f of digit){
   const skew=f.x*.095;
   d=blend(d,cap(p,[f.x,f.from,-.005],[f.x+skew,f.to-.1,-.006],f.r,f.r*.78),.075);
   d=blend(d,ell(p,[f.x+skew,f.to-.095,-.006],[f.r*.78,.115,f.r*.75]),.035);
  }
  d=blend(d,cap(p,[-.48,1.43,.015],[-.96,1.91,.065],.19,.135),.16);
  d=blend(d,cap(p,[-.96,1.91,.065],[-1.24,2.16,.055],.136,.103),.052);
  d=blend(d,ell(p,[-1.24,2.16,.055],[.105,.113,.109]),.035);
  return d;
 };
 // The native marching-tetrahedra helper provides indexed mesh geometry and UVs.
 const skinMesh=atelierAnimalWeld(atelierAnimalSurface(skin,[[-1.52,.53,-.40],[.83,3.49,.42]],.049));
 push('Glove · organic connected palm, wrist, thumb and four fingers','topologyMesh',
  color.glove,'silk','Glove / core',{topologyMesh:skinMesh,organicSurface:{species:'arcane-glove',region:'shell'}});
 const sphere=(name,center,scale,c,mat,group)=>{
  return push(name,'sphere',c,mat,group,{position:center,scale,meshDensity:{u:24,v:16}});
 };
 const cylinder=(name,center,scale,c,mat,group)=>{
  return push(name,'cylinder',c,mat,group,{position:center,scale,meshDensity:{u:32,v:1}});
 };
 // A small smooth tube mesh for open lines and continuous closed rings.
 function tube(points,radius,closed=false){
  const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)),closed,'centripetal');
  const rows=closed?Math.max(24,points.length*3):Math.max(12,points.length*5),cols=8;
  const positions=[],uvs=[],indices=[];
  for(let i=0;i<=rows;i++){
   const t=i/rows,v=curve.getPoint(t),tan=curve.getTangent(t).normalize();
   const reference=Math.abs(tan.y)>.88?new THREE.Vector3(0,0,1):new THREE.Vector3(0,1,0);
   const u=new THREE.Vector3().crossVectors(tan,reference).normalize();
   const w=new THREE.Vector3().crossVectors(tan,u).normalize();
   for(let j=0;j<cols;j++){
    const a=2*Math.PI*j/cols,p=v.clone().addScaledVector(u,radius*Math.cos(a)).addScaledVector(w,radius*Math.sin(a));
    positions.push(clean(p.x),clean(p.y),clean(p.z));uvs.push(j/cols,t);
    if(i<rows){const k=i*cols+j,n=i*cols+(j+1)%cols;indices.push(k,n,k+cols,k+cols,n,n+cols);}
   }
  }
  if(!closed){
   for(const end of [0,rows]){
    const v=curve.getPoint(end/rows),center=positions.length/3;
    positions.push(clean(v.x),clean(v.y),clean(v.z));uvs.push(.5,end/rows);
    for(let j=0;j<cols;j++){
     const a=end*cols+j,b=end*cols+(j+1)%cols;
     if(end===0)indices.push(center,b,a);else indices.push(center,a,b);
    }
   }
  }
  return {positions,uvs,indices};
 }
 const wire=(name,path,r,c,mat,group,closed=false)=>
  push(name,'topologyMesh',c,mat,group,{topologyMesh:tube(path,r,closed)});
 const loop=(center,rx,ry,plane='xy')=>Array.from({length:32},(_,i)=>{
  const a=i*Math.PI/16;
  return plane==='xy'?[center[0]+rx*Math.cos(a),center[1]+ry*Math.sin(a),center[2]]:
   [center[0]+rx*Math.cos(a),center[1],center[2]+ry*Math.sin(a)];
 });
 // Cuff, articulated overlays and glowing floating, deliberately separated effects.
 cylinder('Wrist · dark floating sleeve',[0,.77,-.006],[.405,.41,.255],color.glove,'silk','Wrist / cuff');
 for(const [i,y] of [.58,.82,1.025].entries()){
  wire('Wrist · silver trim '+(i+1),loop([0,y,0],.415,.263,'xz'),.025,color.rim,'metal','Wrist / cuff',true);
 }
 for(const [i,y,r] of [[0,.39,.53],[1,.30,.31],[2,.46,.39]]){
  wire('Hover · violet energy halo '+(i+1),loop([0,y,0],r,r*.66,'xz'),
   i===1?.020:.014,i===1?color.light:color.accent,'emissive','Hover / effects',true);
 }
 sphere('Palm · engraved medallion backing',[0,1.70,.226],[.345,.345,.055],color.void,'metal','Palm / sigil');
 wire('Palm · medallion rim',loop([0,1.70,.290],.326,.326),.029,color.rim,'metal','Palm / sigil',true);
 wire('Palm · inner purple halo',loop([0,1.70,.298],.267,.267),.012,color.accent,'emissive','Palm / sigil',true);
 // Open original serpentine crest. Editable 3D curves; no image or trademark texture.
 wire('Palm · arcane curled dragon crest',
  [[-.15,1.59,.310],[-.19,1.73,.312],[-.095,1.845,.312],[.065,1.858,.312],
   [.170,1.75,.312],[.13,1.625,.312],[.025,1.605,.314],[-.026,1.685,.317],
   [.038,1.728,.319],[.095,1.690,.319]],.024,color.light,'emissive','Palm / sigil');
 for(const [i,f] of digit.entries()){
  const y=f.to-.13,x=f.x+f.x*.09;
  sphere('Digit '+(i+1)+' · knuckle plating',[f.x,2.31,-.183],[f.r*1.19,.17,.055],color.plate,'metal','Fingers / armor');
  sphere('Digit '+(i+1)+' · long dorsal plate',[f.x+f.x*.045,(f.from+f.to)*.5,-.137],
   [f.r*.89,(f.to-f.from)*.29,.042],color.plate,'metal','Fingers / armor');
  sphere('Digit '+(i+1)+' · silver knuckle gem',[f.x,2.325,-.242],[.060,.080,.036],
   color.rim,'metal','Fingers / armor');
  wire('Digit '+(i+1)+' · glowing dorsal seam',
   [[f.x,2.41,-.205],[f.x+f.x*.045,(f.from+f.to)*.53,-.181],
    [x,y,-.133]],.014,color.accent,'emissive','Fingers / runes');
  sphere('Digit '+(i+1)+' · glowing tip',[x,f.to-.09,-.084],[.038,.053,.027],
   color.light,'emissive','Fingers / runes');
 }
 sphere('Thumb · armor joint',[-.77,1.71,-.123],[.19,.15,.051],color.plate,'metal','Thumb / armor');
 wire('Thumb · luminescent seam',
  [[-.72,1.64,-.154],[-.96,1.91,-.084],[-1.19,2.13,-.048]],.017,color.accent,'emissive','Thumb / armor');
 sphere('Backhand · armored shield',[0,1.71,-.205],[.54,.53,.083],color.plate,'metal','Backhand / armor');
 wire('Backhand · central rune',
  [[0,2.14,-.301],[-.19,1.95,-.308],[-.065,1.78,-.307],[0,1.59,-.307],
   [.065,1.78,-.307],[.19,1.95,-.308],[0,2.14,-.301]],.023,color.light,'emissive','Backhand / runes');
 wire('Backhand · lower vertical trace',[[0,1.63,-.305],[0,1.23,-.245]],.020,
  color.accent,'emissive','Backhand / runes');
 for(const s of [-1,1]){
  wire((s<0?'Left':'Right')+' backhand vein',
   [[s*.14,1.60,-.300],[s*.34,1.91,-.285],[s*.46,2.18,-.211]],.014,
   color.accent,'emissive','Backhand / runes');
 }
 m.name='Floating Hand · Arcane Glove';m.parts=parts;
 m.meshGroups=[...new Set(parts.map(p=>p.group))].map((g,i)=>({
  id:'floating-hand-assembly-'+i,name:g,members:parts.filter(p=>p.group===g).map(p=>p.id)
 })).filter(g=>g.members.length>=2);
 m.poseFrames=[];m.poseNeutral=null;m.editedAt='local';
 m.reference='Owner-supplied floating glove visual; native original polygonal construction, not an image plane.';
 source.project.name='Floating Hand · Arcane Glove';
 source.project.canonicalId=se212Id;source.project.template=se212Id;
 source.project.kind='model-atelier';
 source.project.environmentSettings={...source.project.environmentSettings,showTerrain:false,showScenery:false,background:'#11101b'};
 source.engine='§wyrl§ Engine · Maker v11.212';source.version=11.212;
 se212Cached=source;
 return structuredClone(source);
}
function se212OpenHand(force=false){
 if(dirty&&!force&&!confirm('Open Floating Hand and discard unsaved scene changes?'))return false;
 try{
  const payload=se212HandScene();
  ModelAtelier.close();loadProject(payload,{workspaceLocal:true});
  initializeHistory('Opened Floating Hand · Arcane Glove starter');
  markSaved();document.getElementById('projectHub')?.classList.remove('show');
  ModelAtelier.syncProject();ModelAtelier.open();
  const panel=document.getElementById('modelAtelierPanel');
  if(panel){
   panel.classList.add('courier-studio');
   const studio=document.getElementById('modelAtelierCourierStudio');
   if(studio){studio.hidden=false;studio.textContent='Edit model';studio.setAttribute('aria-pressed','true');}
  }
  requestAnimationFrame(()=>requestAnimationFrame(()=>window.SWYRL_ENGINE_MODEL_ATELIER.view?.('three')));
  toast('Floating Hand · native sculpt, armor, crest and hover rings ready to edit');
  return true;
 }catch(error){console.error('Floating Hand starter',error);toast('Unable to create hand: '+error.message);return false;}
}
const se212PreviousTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template===se212Id)return se212OpenHand(force);
 return se212PreviousTemplate(template,force);
};
window.SWYRL_ENGINE_FLOATING_HAND=Object.freeze({
 createScene:()=>se212HandScene(),open:(force=false)=>se212OpenHand(force),
 status:()=>({ready:typeof atelierAnimalSurface==='function',parts:se212Cached?.project?.modelAtelier?.parts?.length||0})
});
