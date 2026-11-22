/* §E v11.537 — original untextured articulated humanoid mannequin starter.
   Native topology, no texture maps, image planes or second renderer. */
const se537Id='robotic-humanoid-mannequin';
let se537Opening=false;
function se537MakeMannequin(){
 const parts=[], groups=new Map(), bone='#cdd2d5', edge='#a9b2b7', joint='#626b72';
 const light='#dde1e3', recess='#485159';
 const rnd=v=>Math.round(v*100000)/100000;
 function add(name,group,color,positions,uvs,indices){
   if(positions.some(v=>!Number.isFinite(v)||Math.abs(v)>100)||indices.some(v=>!Number.isInteger(v)||v<0||v>=positions.length/3))throw Error('Mannequin topology invalid: '+name);
   const id='mannequin-'+String(parts.length+1).padStart(3,'0');
   parts.push({id,name,group,kind:'topologyMesh',color,material:'matte',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],
    topologyMesh:{positions:positions.map(rnd),uvs:uvs.map(rnd),indices}});
   if(!groups.has(group))groups.set(group,[]);
   groups.get(group).push(id);
 }
 function sphere(name,group,center,r,color=bone,detail=18,rows=12,warp=null){
   const p=[],uv=[],ix=[];
   for(let j=0;j<=rows;j++){
     const theta=Math.PI*j/rows,y=Math.cos(theta),w=Math.sin(theta);
     for(let i=0;i<=detail;i++){
       const a=i*2*Math.PI/detail;let x=Math.cos(a)*w,z=Math.sin(a)*w;
       const v=warp?warp(x,y,z):[x,y,z];
       p.push(center[0]+r[0]*v[0],center[1]+r[1]*v[1],center[2]+r[2]*v[2]);
       uv.push(i/detail,1-j/rows);
     }
   }
   for(let j=0;j<rows;j++)for(let i=0;i<detail;i++){
     const a=j*(detail+1)+i,b=a+detail+1;
     ix.push(a,a+1,b,b,a+1,b+1);
   }
   add(name,group,color,p,uv,ix);
 }
 function tube(name,group,control,color=bone,sides=18,divisions=2){
   const p=[],uv=[],ix=[],length=control.length;
   const interpolate=(a,b,t)=>a+(b-a)*t;
   const rows=(length-1)*divisions;
   for(let k=0;k<=rows;k++){
     const segment=Math.min(length-2,Math.floor(k/divisions)),t=k===rows?1:(k/divisions-segment);
     const h=t*t*(3-2*t);
     const a=control[segment],b=control[segment+1];
     const c=[0,1,2].map(n=>interpolate(a[n],b[n],h));
     const ra=interpolate(a[3],b[3],h),rb=interpolate(a[4],b[4],h);
     const before=control[Math.max(0,segment-1)],after=control[Math.min(length-1,segment+2)];
     let tangent=[after[0]-before[0],after[1]-before[1],after[2]-before[2]];
     const l=Math.hypot(...tangent)||1;tangent=tangent.map(v=>v/l);
     const ref=Math.abs(tangent[1])>.88?[0,0,1]:[0,1,0];
     let u=[tangent[1]*ref[2]-tangent[2]*ref[1],tangent[2]*ref[0]-tangent[0]*ref[2],tangent[0]*ref[1]-tangent[1]*ref[0]];
     const ul=Math.hypot(...u)||1;u=u.map(v=>v/ul);
     const v=[tangent[1]*u[2]-tangent[2]*u[1],tangent[2]*u[0]-tangent[0]*u[2],tangent[0]*u[1]-tangent[1]*u[0]];
     for(let s=0;s<=sides;s++){
       const ang=s*2*Math.PI/sides,ca=Math.cos(ang),sa=Math.sin(ang);
       p.push(c[0]+ra*ca*u[0]+rb*sa*v[0],c[1]+ra*ca*u[1]+rb*sa*v[1],c[2]+ra*ca*u[2]+rb*sa*v[2]);
       uv.push(s/sides,k/rows);
     }
   }
   for(let k=0;k<rows;k++)for(let i=0;i<sides;i++){
     const a=k*(sides+1)+i,b=a+sides+1;ix.push(a,a+1,b,a+1,b+1,b);
   }
   const n=p.length/3;
   for(const k of [0,rows]){
     const a=control[k===0?0:length-1];p.push(a[0],a[1],a[2]);uv.push(.5,k===0?0:1);
     const base=k*(sides+1),center=n+(k===0?0:1);
     for(let i=0;i<sides;i++)if(k===0)ix.push(center,base+i,base+i+1);
     else ix.push(center,base+i+1,base+i);
   }
   add(name,group,color,p,uv,ix);
 }
 function seam(name,group,pts,r=.009,color=recess){
   tube(name,group,pts.map(p=>[...p,r,r]),color,9,1);
 }
 // Skull, facial relief and mechanical jaw: exposed original geometry, no decals.
 sphere('Cranial shell · natural oval','Head',[0,4.43,0],[.267,.351,.244],bone,28,20,
  (x,y,z)=>[x*(y<-.15?1-.19*(-y):1),y,z*(y<-.35?1-.1*(-y):1)]);
 sphere('Facial mask · refined cheek and chin','Head',[0,4.365,.126],[.233,.277,.144],light,26,18,
  (x,y,z)=>[x*(y<-.12?.92+.16*y:1),y,z*(y<-.25?.92:1)]);
 sphere('Lower jaw volume','Head',[0,4.195,.085],[.19,.102,.183],bone);
 sphere('Neck core','Neck',[0,3.986,0],[.116,.161,.115],joint);
 for(let k=0;k<3;k++)sphere('Neck vertebra collar '+(k+1),'Neck',[0,3.957+k*.067,0],[.145-k*.009,.026,.14-k*.008],edge,20,10);
 sphere('Nasal bridge','Head',[0,4.442,.263],[.042,.116,.048],light,18,14);
 sphere('Nasal tip','Head',[0,4.378,.294],[.067,.039,.047],bone,18,12);
 sphere('Chin plate','Head',[0,4.226,.245],[.108,.046,.033],edge);
 seam('Mouth line · articulated lip','Head',[[-.093,4.288,.266],[-.046,4.280,.282],[0,4.279,.29],[.046,4.28,.282],[.093,4.288,.266]],.009,recess);
 for(const side of [-1,1]){
  const dir=side,lab=dir<0?'Left':'Right',h='Head';
  sphere(lab+' eye socket housing',h,[dir*.108,4.492,.248],[.096,.065,.04],edge,22,14);
  sphere(lab+' recessed optical lens',h,[dir*.11,4.492,.284],[.066,.039,.016],recess,22,12);
  sphere(lab+' optical aperture',h,[dir*.11,4.492,.296],[.027,.028,.011],light,16,10);
  sphere(lab+' brow ridge',h,[dir*.112,4.567,.261],[.104,.025,.036],bone,18,10);
  sphere(lab+' cheek muscle plate',h,[dir*.164,4.359,.223],[.073,.093,.041],bone,18,12);
  sphere(lab+' mandibular hinge',h,[dir*.237,4.285,.046],[.041,.066,.061],joint);
  sphere(lab+' ear chassis',h,[dir*.277,4.438,0],[.048,.092,.091],edge,20,12);
  sphere(lab+' ear inner actuator',h,[dir*.310,4.436,0],[.024,.048,.052],recess);
  seam(lab+' temple seam',h,[[dir*.17,4.655,.10],[dir*.235,4.558,.13],[dir*.255,4.445,.16]],.008);
 }
 // Tapered anatomical torso with chest, segmented abdomen, spine and hips.
 tube('Organic thoracic core','Torso',[[0,2.895,0,.282,.210],[0,3.12,0,.315,.218],[0,3.30,0,.39,.255],[0,3.55,0,.47,.267],[0,3.765,0,.452,.245],[0,3.84,0,.255,.178]],bone,32,3);
 sphere('Sternum centerline','Torso',[0,3.525,.254],[.072,.29,.039],edge,18,18);
 sphere('Upper dorsal scapula field','Torso',[0,3.575,-.21],[.295,.239,.072],edge,22,14);
 for(const side of [-1,1]){
  const s=side,lab=s<0?'Left':'Right';
  sphere(lab+' pectoral contour','Torso',[s*.229,3.611,.221],[.252,.177,.088],light,22,14,
   (x,y,z)=>[x,y*(z>0?1-.06*Math.abs(x):1),z]);
  sphere(lab+' serratus rib transition','Torso',[s*.341,3.27,.16],[.115,.246,.099],bone,18,16);
  sphere(lab+' oblique muscle shell','Torso',[s*.255,2.993,.155],[.152,.165,.096],light);
  sphere(lab+' clavicle','Torso',[s*.325,3.803,.151],[.26,.043,.072],bone,22,10);
  sphere(lab+' scapula','Torso',[s*.289,3.592,-.235],[.208,.211,.071],bone,20,16);
 }
 for(let j=0;j<4;j++){
  const y=3.33-j*.127;
  for(const s of [-1,1])sphere((s<0?'Left':'Right')+' abdominal plate '+(j+1),'Torso',[s*.104,y,.209-j*.006],[.104,.062,.06],j%2?bone:light,18,10);
  seam('Abdominal segmentation '+(j+1),'Torso',[[-.19,y-.060,.258],[0,y-.065,.273],[.19,y-.060,.258]],.005,recess);
 }
 tube('Pelvic architecture','Pelvis',[[0,2.23,0,.267,.212],[0,2.38,0,.369,.230],[0,2.55,0,.365,.225],[0,2.72,0,.278,.194],[0,2.84,0,.256,.18]],bone,26,3);
 sphere('Sacral support','Pelvis',[0,2.42,-.206],[.21,.176,.069],edge);
 sphere('Anterior pelvis guard','Pelvis',[0,2.39,.205],[.235,.132,.055],light);
 seam('Pelvic center hinge','Pelvis',[[0,2.57,.242],[0,2.42,.253],[0,2.293,.218]],.008);
 // Fully symmetrical horizontal T-pose: arms straight out, open hands, separate phalanges.
 for(const side of [-1,1]){
  const s=side,lab=s<0?'Left':'Right',arm=lab+' Arm',hand=lab+' Hand',leg=lab+' Leg';
  sphere(lab+' shoulder bearing',arm,[s*.516,3.665,0],[.141,.165,.163],joint,24,16);
  sphere(lab+' deltoid layered cap',arm,[s*.681,3.657,0],[.238,.210,.207],bone,22,16);
  sphere(lab+' rear deltoid blade',arm,[s*.693,3.643,-.156],[.188,.103,.06],edge);
  tube(lab+' upper arm · biceps/triceps',arm,[
   [s*.785,3.665,0,.175,.173],[s*.895,3.656,0,.181,.173],
   [s*1.08,3.65,0,.149,.156],[s*1.28,3.65,0,.115,.122],
   [s*1.345,3.65,0,.093,.096]],bone,22,3);
  sphere(lab+' biceps raised plane',arm,[s*1.039,3.704,.10],[.178,.105,.078],light);
  sphere(lab+' elbow swivel',arm,[s*1.405,3.65,0],[.103,.105,.105],joint,22,14);
  sphere(lab+' elbow exterior ring',arm,[s*1.4,3.649,.05],[.118,.112,.077],edge);
  tube(lab+' forearm radial-ulnar shell',arm,[
   [s*1.456,3.65,0,.115,.113],[s*1.59,3.65,0,.141,.136],
   [s*1.74,3.65,0,.125,.114],[s*1.95,3.65,0,.083,.080],
   [s*2.035,3.65,0,.076,.075]],bone,22,3);
  sphere(lab+' forearm flexor crest',arm,[s*1.675,3.686,.07],[.202,.065,.081],light,20,12);
  sphere(lab+' wrist rotary hub',hand,[s*2.056,3.65,0],[.075,.076,.076],joint);
  sphere(lab+' wrist cuff',hand,[s*2.084,3.65,0],[.068,.095,.094],edge);
  tube(lab+' metacarpal palm',hand,[
   [s*2.12,3.65,0,.080,.104],[s*2.19,3.65,0,.085,.151],
   [s*2.29,3.65,0,.057,.149],[s*2.35,3.65,0,.045,.126]],bone,18,2);
  sphere(lab+' dorsal knuckle rise',hand,[s*2.289,3.691,0],[.078,.032,.145],light);
  for(let finger=0;finger<4;finger++){
   const zz=-.107+finger*.071,extent=[.176,.219,.207,.171][finger];
   const origin=2.335+(finger===1||finger===2?.013:0);
   sphere(lab+' knuckle '+(finger+1),hand,[s*origin,3.65,zz],[.043,.047,.039],edge,14,10);
   for(let n=0;n<3;n++){
    const x0=origin+extent*n/3,x1=origin+extent*(n+1)/3;
    tube(lab+' finger '+(finger+1)+' phalanx '+(n+1),hand,[
     [s*x0,3.65,zz,.034-n*.005,.031-n*.004],
     [s*((x0+x1)/2),3.65,zz,.032-n*.005,.030-n*.004],
     [s*x1,3.65,zz,.028-n*.005,.027-n*.004]],n===2?light:bone,10,2);
    if(n<2)sphere(lab+' finger '+(finger+1)+' hinge '+(n+1),hand,[s*x1,3.65,zz],[.027,.031,.029],joint,12,8);
   }
  }
  tube(lab+' thumb opposable rail',hand,[
   [s*2.167,3.632,.125,.064,.053],[s*2.222,3.622,.19,.051,.044],
   [s*2.267,3.635,.256,.040,.035],[s*2.302,3.646,.288,.022,.025]],bone,12,3);
  sphere(lab+' thumb articulation',hand,[s*2.22,3.623,.187],[.039,.046,.045],edge,12,10);
  // Leg geometry. Naturally sculpted quadriceps/hamstrings, knee patella and ankle.
  sphere(lab+' ball hip',leg,[s*.278,2.30,0],[.177,.17,.174],joint,24,14);
  sphere(lab+' iliac crest',leg,[s*.317,2.52,0],[.182,.130,.204],light,22,12);
  tube(lab+' thigh · organic anterior and posterior contours',leg,[
   [s*.287,2.28,0,.174,.176],[s*.305,2.19,0,.228,.225],
   [s*.327,1.93,0,.229,.229],[s*.333,1.71,0,.201,.204],
   [s*.33,1.49,0,.15,.156],[s*.326,1.405,0,.130,.137]],bone,26,3);
  sphere(lab+' vastus lateralis',leg,[s*.421,1.92,.105],[.113,.26,.102],light,18,16);
  sphere(lab+' quadriceps anterior crest',leg,[s*.288,1.903,.187],[.131,.33,.068],bone,18,18);
  sphere(lab+' hamstring volume',leg,[s*.301,1.935,-.184],[.156,.302,.072],edge,18,18);
  sphere(lab+' knee bearing',leg,[s*.327,1.344,0],[.133,.132,.135],joint,20,14);
  sphere(lab+' patella plate',leg,[s*.327,1.344,.117],[.123,.116,.056],light,20,14);
  tube(lab+' shin · tapered gastrocnemius shell',leg,[
   [s*.326,1.294,0,.119,.126],[s*.332,1.16,-.015,.154,.159],
   [s*.336,.93,-.035,.161,.175],[s*.334,.73,-.005,.113,.124],
   [s*.333,.47,0,.089,.096],[s*.329,.35,0,.080,.084]],bone,24,3);
  sphere(lab+' calf medial contour',leg,[s*.28,.96,-.101],[.106,.245,.104],light,18,18);
  sphere(lab+' anterior tibial ridge',leg,[s*.334,.83,.123],[.079,.265,.041],edge,18,18);
  sphere(lab+' ankle rotary coupling',leg,[s*.327,.322,0],[.103,.107,.099],joint,18,12);
  sphere(lab+' malleolus housing',leg,[s*.424,.326,0],[.053,.085,.067],edge,16,10);
  tube(lab+' instep / metatarsal body',leg,[
   [s*.326,.245,-.01,.103,.125],[s*.33,.199,.088,.12,.157],
   [s*.331,.157,.215,.125,.159],[s*.329,.133,.36,.112,.131],
   [s*.329,.115,.405,.088,.091]],bone,24,3);
  sphere(lab+' heel',leg,[s*.329,.125,-.12],[.125,.116,.13],bone,18,12);
  sphere(lab+' sole · broad toe platform',leg,[s*.329,.085,.292],[.16,.059,.202],edge,22,12);
  for(let toe=0;toe<5;toe++){
   const spread=(toe-2)*.053;
   sphere(lab+' articulated toe '+(toe+1),leg,[s*(.329+spread),.113,.454-(Math.abs(toe-1)*.019)],[.031,.035,.087-Math.abs(toe-2)*.007],light,14,10);
  }
 }
 if(parts.length>400)throw Error('Native part capacity exceeded');
 const meshGroups=[...groups.entries()].flatMap(([name,ids])=>{
   const out=[];for(let i=0;i<ids.length;i+=32)if(ids.slice(i,i+32).length>=2)out.push({id:'mannequin-group-'+out.length+'-'+name.toLowerCase().replace(/[^a-z]+/g,'-'),name:name+(ids.length>32?' '+(i/32+1):''),members:ids.slice(i,i+32)});
   return out;
 });
 return {engine:'§wyrl§ Engine · Maker v11.537',version:11.537,
  project:{name:'Robotic Humanoid · Anatomy Mannequin',canonicalId:se537Id,template:se537Id,kind:'model-atelier',
   environment:'spatial-workspace',environmentSettings:{background:'#252b30',fogNear:80,fogFar:140,exposure:1.16,showTerrain:false,showScenery:false},
   modelAtelier:{schema:'swyrl-model-atelier-v1',name:'Robotic Humanoid · T-Pose',
    reference:'Original professional-scale grayscale humanoid: anatomically proportioned T-pose, sculpted-looking cranial and body surfaces, robotic articulations, separately editable native topology meshes, articulated fingers and toes. No image textures or external assets. This is a starter, not a skinned animation rig.',
    parts,meshGroups,poseFrames:[],poseNeutral:null,editedAt:null}},
  editor:{transformSpace:'world',snapEnabled:false,terrainSnapEnabled:false,viewMode:'edit',cameraView:'perspective',revision:0,layers:[{id:'atelier-scene',name:'Model Atelier Base',visible:true}],activeLayerId:'atelier-scene'},
  scene:{actors:[]}};
}
function se537ValidateScene(data){
 const m=data?.project?.modelAtelier,p=m?.parts;
 if(data?.project?.canonicalId!==se537Id||m?.schema!=='swyrl-model-atelier-v1'||!Array.isArray(p)||p.length<100||p.length>400)throw Error('Mannequin parts invalid');
 const seen=new Set();
 for(const part of p){
  const g=part.topologyMesh,n=g?.positions?.length/3;
  if(seen.has(part.id)||!Number.isInteger(n)||n<10||n>9000||g.positions.length%3||
    g.uvs.length!==2*n||g.indices.length%3||g.indices.length/3>16000||
    !g.indices.every(i=>Number.isInteger(i)&&i>=0&&i<n)||!g.uvs.every(Number.isFinite))throw Error('Mannequin mesh invalid: '+part.name);
  seen.add(part.id);
 }
 return p.length;
}
async function se537OpenMannequin(force=false){
 if(se537Opening)return false;
 if(dirty&&!force&&!confirm('Open the robotic humanoid and discard unsaved changes?'))return false;
 se537Opening=true;
 try{
  const data=se537MakeMannequin(),count=se537ValidateScene(data);
  if(typeof ModelAtelier?.close!=='function'||typeof loadProject!=='function')throw Error('Model Studio unavailable');
  ModelAtelier.close();loadProject(data,{workspaceLocal:true});
  if(currentProject?.canonicalId!==se537Id||currentProject.modelAtelier.parts.length!==count)throw Error('Model project did not load');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  initializeHistory('Opened untextured robotic humanoid mannequin');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('front')));
  toast('Robotic Humanoid · '+count+' editable untextured geometry pieces');
  return true;
 }catch(error){console.error('§E mannequin starter',error);toast('Mannequin could not open: '+String(error.message||error).slice(0,160));return false;}
 finally{se537Opening=false;}
}
const se537PreviousTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template===se537Id)return se537OpenMannequin(force);
 return se537PreviousTemplate(template,force);
};
function se537BindCard(){
 const hub=document.getElementById('projectHub');
 if(!hub||hub.dataset.se537Mannequin)return;
 hub.dataset.se537Mannequin='1';
 hub.addEventListener('click',event=>{
  const button=event.target?.closest?.('button[data-project-template="robotic-humanoid-mannequin"]');
  if(!button)return;
  event.preventDefault();event.stopImmediatePropagation();
  void se537OpenMannequin();
 },true);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',se537BindCard,{once:true});
else se537BindCard();
window.SWYRL_ENGINE_HUMANOID_537=Object.freeze({open:se537OpenMannequin,create:se537MakeMannequin,validate:se537ValidateScene,
 status:()=>({busy:se537Opening,cardExists:!!document.querySelector('button[data-project-template="robotic-humanoid-mannequin"]'),active:currentProject?.canonicalId===se537Id})});
/* SE537_HUMANOID_END */
