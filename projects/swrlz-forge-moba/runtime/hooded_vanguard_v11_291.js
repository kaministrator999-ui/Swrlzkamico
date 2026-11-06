// §E v11.291 — Hooded Vanguard, original native model after the supplied
// hooded knight visual reference. No bird, weapon, billboard, or confetti meshes.
// Cohesive anatomy, selective independently controllable garments, UV-mapped
// material detail. Starter is a static model study, NOT a verified character rig.
const se291Id='hooded-vanguard';
const se291Tiles={
 skin:['#dab69d',.92,0], hair:['#352923',.84,0],
 uniform:['#303e4d',.81,.10], cuirass:['#405466',.42,.35],
 ivory:['#e9e5da',.86,0], teal:['#166878',.7,.07],
 leather:['#4b332b',.74,0], gold:['#ba8944',.28,.77],
 steel:['#778390',.37,.62]
};
const se291Textures=new Map();
const se291Stats={attempts:0,successes:0,lastError:null,lastParts:0,lastTriangles:0};
function se291MaterialCanvas(tile,mode){
 const c=document.createElement('canvas');c.width=c.height=256;
 const ctx=c.getContext('2d',{willReadFrequently:true});
 const def=se291Tiles[tile]||se291Tiles.uniform;
 const hex=def[0].replace('#','');const base=[0,2,4].map(i=>parseInt(hex.slice(i,i+2),16));
 const pix=ctx.createImageData(256,256),a=pix.data;
 const hash=(x,y)=>{let q=(x*374761393+y*668265263+tile.length*2654435761)|0;q=Math.imul(q^(q>>>13),1274126177);return ((q^(q>>>16))>>>0)/4294967295;};
 const height=(x,y)=>{
  const coarse=Math.sin(x*.084+y*.037)*.37+Math.sin(y*.11-x*.043)*.18;
  const thread=(tile==='ivory'||tile==='teal'||tile==='uniform')?Math.cos(x*.34)*.22+Math.sin(y*.39)*.18:0;
  const grain=(hash(x>>1,y>>1)-.5)*.18;
  return coarse+thread+grain;
 };
 for(let y=0;y<256;y++)for(let x=0;x<256;x++){
  const k=(y*256+x)*4,h=height(x,y),n=hash(x,y);
  if(mode==='color'){
   const grain=(h*.045+(n-.5)*.024),shade=1+grain;
   for(let j=0;j<3;j++)a[k+j]=Math.max(0,Math.min(255,base[j]*shade));
  }else if(mode==='normal'){
   const dx=(height(x+1,y)-height(x-1,y))*.24;
   const dy=(height(x,y+1)-height(x,y-1))*.24;
   const l=Math.hypot(dx,dy,1);
   a[k]=Math.round(127.5*(1-dx/l));a[k+1]=Math.round(127.5*(1-dy/l));a[k+2]=Math.round(127.5*(1+1/l));
  }else{
   const v=Math.round(210+28*h+18*n);a[k]=a[k+1]=a[k+2]=Math.max(10,Math.min(255,v));
  }
  a[k+3]=255;
 }
 ctx.putImageData(pix,0,0);
 if(mode==='color'){
  const line=(color,width,points)=>{ctx.strokeStyle=color;ctx.lineWidth=width;ctx.lineJoin='round';ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();};
  if(tile==='cuirass'){
   // Painted inset metalwork, not independent strips of geometry.
   for(const s of [-1,1]){
    line('#c8a369',4,[[128,18],[128+s*72,62],[128+s*44,148],[128+s*9,221]]);
    line('#142c3c',5,[[128+s*19,36],[128+s*48,93],[128+s*25,180]]);
   }
   line('#d1b783',3,[[33,238],[128,210],[224,238]]);
  }
  if(tile==='teal'){
   line('#c9ad75',5,[[10,0],[10,256]]);line('#bc985e',3,[[244,0],[244,256]]);
   for(let y=17;y<256;y+=39)line('#2d8894',1,[[24,y],[128,y+7],[230,y]]);
  }
  if(tile==='ivory'){
   for(let i=15;i<256;i+=30)line('rgba(106,129,146,.26)',2,[[0,i],[120,i+22],[256,i-3]]);
   line('#bdaa88',4,[[12,245],[244,245]]);
  }
  if(tile==='gold'){
   for(let y=12;y<256;y+=27)line('rgba(255,233,181,.22)',2,[[10,y],[245,y-6]]);
   line('#ffe0a0',5,[[12,14],[243,14]]);
  }
  if(tile==='leather'){
   line('#b9976a',3,[[18,16],[18,240]]);
   for(let y=19;y<250;y+=21)line('#a47f60',2,[[14,y],[22,y+6]]);
  }
  if(tile==='uniform'){
   for(let y=0;y<256;y+=28)line('rgba(158,181,196,.17)',2,[[0,y],[256,y+11]]);
  }
  if(tile==='skin'){
   // A deliberately flat atlas: features are painted in UV space.
   for(const u of [.32,.68]){
    ctx.fillStyle='#eee3d1';ctx.beginPath();ctx.ellipse(u*256,123,19,9,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#607586';ctx.beginPath();ctx.ellipse(u*256,123,7,8,0,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#1c222c';ctx.beginPath();ctx.ellipse(u*256,123,3.3,6,0,0,Math.PI*2);ctx.fill();
    line('#3c302c',4,[[u*256-18,107],[u*256+17,105]]);
   }
   line('#985b56',3,[[105,185],[128,190],[150,185]]);
  }
  if(tile==='hair')for(let x=10;x<256;x+=18)line('rgba(211,172,123,.23)',2,[[x+4,0],[x-6,256]]);
 }
 return c;
}
function se291Map(tile,mode){
 const key=tile+'|'+mode;if(se291Textures.has(key))return se291Textures.get(key);
 const tex=new THREE.CanvasTexture(se291MaterialCanvas(tile,mode));
 tex.colorSpace=mode==='color'?THREE.SRGBColorSpace:THREE.NoColorSpace;
 tex.wrapS=THREE.RepeatWrapping;tex.wrapT=THREE.RepeatWrapping;
 tex.anisotropy=2;
 tex.minFilter=THREE.LinearMipmapLinearFilter;tex.magFilter=THREE.LinearFilter;
 tex.needsUpdate=true;se291Textures.set(key,tex);return tex;
}
function se291HeroMaterial(part){
 const tile=part.heroPBR?.tile||'uniform',def=se291Tiles[tile]||se291Tiles.uniform;
 const mat=new THREE.MeshStandardMaterial({
  color:'#ffffff',map:se291Map(tile,'color'),
  normalMap:se291Map(tile,'normal'),normalScale:new THREE.Vector2(.28,.28),
  roughnessMap:se291Map(tile,'roughness'),roughness:def[1],
  metalness:def[2],side:THREE.DoubleSide
 });
 mat.name='Vanguard PBR · '+tile+' / aligned UV color, normal and roughness';
 return mat;
}
function se291HeroScene(){
 se291Stats.attempts++;
 try{
  const ops=window.SWYRL_ENGINE_HAND_SURFACE;
  if(!ops?.surface||!ops?.weld)throw Error('Native mesh surface tools unavailable.');
  const scene=structuredClone(MODEL_ATELIER_CANONICAL_PROJECT),model=scene.project.modelAtelier;
  const parts=[],round=n=>+n.toFixed(5);
  function add(name,tile,data,group='Vanguard / anatomy'){
   if(!data?.positions?.length||!data?.indices?.length||data.uvs?.length!==data.positions.length/3*2)
    throw Error('Invalid UV or mesh geometry for '+name);
   const p={id:'vanguard-'+String(parts.length).padStart(2,'0'),
    name,kind:'topologyMesh',topologyMesh:data,color:'#ffffff',
    material:'matte',heroPBR:{tile,uv:'explicit',maps:['albedo','normal','roughness']},
    group,position:[0,0,0],rotation:[0,0,0],scale:[1,1,1]};
   parts.push(p);return p;
  }
  const ell=(p,c,r)=>(Math.hypot(...p.map((v,i)=>(v-c[i])/r[i]))-1)*Math.min(...r);
  const cap=(p,a,b,r1,r2)=>{
   const v=b.map((n,i)=>n-a[i]),q=p.map((n,i)=>n-a[i]),
    t=Math.max(0,Math.min(1,q.reduce((s,n,i)=>s+n*v[i],0)/v.reduce((s,n)=>s+n*n,0)));
   return Math.hypot(...p.map((n,i)=>n-a[i]-v[i]*t))-(r1+(r2-r1)*t);
  };
  const smooth=(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;};
  function fieldMesh(field,bounds,step,projection){
   const d=ops.weld(ops.surface((x,y,z)=>field([x,y,z]),bounds,step));
   if(!d?.positions?.length||!d.indices?.length)throw Error('Native SDF mesher returned an empty surface');
   d.uvs=[];
   for(let i=0;i<d.positions.length;i+=3){
    const x=d.positions[i],y=d.positions[i+1],z=d.positions[i+2];
    const uv=projection(x,y,z);
    d.uvs.push(round(uv[0]),round(uv[1]));
   }
   return d;
  }
  const body=p=>{
   let d=ell(p,[0,3.04,-.005],[.43,.63,.245]);
   d=smooth(d,ell(p,[0,2.45,0],[.335,.32,.222]),.17);
   d=smooth(d,cap(p,[0,3.5,-.01],[0,3.79,-.01],.12,.12),.10);
   for(const s of [-1,1]){
    d=smooth(d,cap(p,[s*.33,3.43,0],[s*.69,3.16,-.01],.145,.12),.09);
    d=smooth(d,cap(p,[s*.69,3.16,-.01],[s*.88,2.67,.05],.12,.083),.07);
    d=smooth(d,ell(p,[s*.89,2.59,.065],[.085,.125,.074]),.045);
    d=smooth(d,cap(p,[s*.195,2.38,0],[s*.29,1.37,0],.19,.115),.12);
    d=smooth(d,cap(p,[s*.29,1.37,0],[s*.295,.25,.065],.112,.085),.07);
   }
   return d;
  };
  const bodyMesh=fieldMesh(body,[[-1.15,.14,-.38],[1.15,3.85,.40]],.057,
   (x,y,z)=>[(x+1.15)/2.30,(y-.14)/3.71]);
  add('01 · continuous male silhouette / torso, arms, hands and legs','uniform',bodyMesh);
  const face=p=>{
   let d=ell(p,[0,4.055,.065],[.259,.335,.205]);
   d=smooth(d,ell(p,[0,3.83,.24],[.10,.09,.09]),.035);
   d=smooth(d,ell(p,[0,4.012,.275],[.048,.093,.072]),.02);
   d=smooth(d,ell(p,[0,3.902,.268],[.077,.025,.035]),.015);
   for(const s of [-1,1])d=smooth(d,ell(p,[s*.254,4.02,.05],[.042,.075,.048]),.019);
   return d;
  };
  add('02 · sculpted face, nose, jaw and ears','skin',
   fieldMesh(face,[[-.36,3.69,-.20],[.36,4.44,.38]],.023,
    (x,y,z)=>[(x+.32)/.64,(y-3.69)/.75]),'Vanguard / face');
  // Native parametric surface: every ribbon is ONE editable mesh, not tiny trim objects.
  function ribbon(rows,cols,fn,capEnds=false){
   const data={positions:[],uvs:[],indices:[]};
   for(let i=0;i<=rows;i++)for(let j=0;j<=cols;j++){
    const u=i/rows,v=j/cols,p=fn(u,v);
    data.positions.push(...p.map(round));data.uvs.push(round(v),round(u));
    if(i<rows&&j<cols){
     const a=i*(cols+1)+j,b=a+cols+1;
     data.indices.push(a,a+1,b,a+1,b+1,b);
    }
   }
   return data;
  }
  // Arched hood, visible open face, no internal confetti ribbons.
  add('03 · hood arch and projecting cloth silhouette','ivory',
   ribbon(30,38,(u,v)=>{
    const a=(.36+1.28*v)*Math.PI;
    const y=3.65+u*.79;
    const r=.284+Math.sin(u*Math.PI)*.075;
    return [Math.sin(a)*r,y,Math.cos(a)*(.22+Math.sin(u*Math.PI)*.045)-.07-u*.04];
   }),'Vanguard / hood');
  // One coherent dark hair cap under the hood, with painted hair strands.
  add('04 · hair silhouette','hair',
   ribbon(16,32,(u,v)=>{
    const theta=.24*Math.PI+1.52*Math.PI*v;
    const y=4.11+u*.28;
    const r=.252*Math.sqrt(Math.max(.06,1-u*u));
    return [r*Math.sin(theta),y,.065+.20*Math.cos(theta)*Math.sqrt(Math.max(.06,1-u*u))];
   }),'Vanguard / hair');
  // Raised scarf collar. White fold texture/normal detail handled in material.
  add('05 · scarf collar and folded drape','ivory',
   ribbon(12,40,(u,v)=>{
    const a=v*Math.PI*2,y=3.56+u*.27;
    const r=.23+.07*Math.sin(u*Math.PI)+.012*Math.sin(a*3);
    return [Math.sin(a)*r,y,Math.cos(a)*r*.75+.065];
   }),'Vanguard / garments');
  // Anatomically following breastplate, one shell; ornate metal lines live in maps.
  add('06 · engraved chest armor (mapped gold filigree)','cuirass',
   ribbon(22,30,(u,v)=>{
    const y=2.79+u*.71,x=(v-.5)*(.71+.13*u);
    const arch=Math.max(0,1-Math.pow(x/(.4+.10*u),2));
    return [x,y,.207+.065*Math.sqrt(arch)+.008*Math.sin(u*Math.PI)];
   }),'Vanguard / armor');
  // Two shoulders remain separate so their pivots can follow an eventual arm rig.
  for(const s of [-1,1]){
   const g=new THREE.SphereGeometry(1,23,15),p=g.attributes.position;
   for(let i=0;i<p.count;i++){
    const x=p.getX(i),y=p.getY(i),z=p.getZ(i);
    p.setXYZ(i,s*.47+s*.29*x,3.38+.205*y+Math.max(0,s*x)*.075,z*.22+.005);
   }
   p.needsUpdate=true;g.computeVertexNormals();
   const data={positions:Array.from(p.array),uvs:Array.from(g.attributes.uv.array),indices:Array.from(g.index.array)};
   g.dispose();add((s<0?'07':'08')+' · shaped shoulder pauldron','gold',data,'Vanguard / moving shoulder armor');
  }
  // Soft coat tails are separate because they should eventually sway independently.
  for(const s of [-1,1])add((s<0?'09':'10')+' · independently swinging teal coat tail','teal',
   ribbon(30,10,(u,v)=>{
    const lean=u*u*.35,center=s*(.26+lean),width=(.22+u*.12)*(1-.6*Math.pow(u,7));
    const y=2.47-u*1.91+Math.sin(v*Math.PI)*u*.06;
    return [center+(v-.5)*width,y,-.18-.055*u+.045*Math.sin(u*Math.PI*2)*v];
   }),'Vanguard / animated coat tails');
  // One belt volume; its stitching/buckle embellishment is mapped, not 25 objects.
  add('11 · waist belt and buckle material','leather',
   ribbon(6,34,(u,v)=>{
    const a=v*Math.PI*2,r=.349,y=2.46+u*.15;
    return [Math.sin(a)*r,y,Math.cos(a)*r*.69+.008];
   }),'Vanguard / belt');
  // Integrated boot volumes (two parts as equipment, not dozens of pieces).
  for(const s of [-1,1])add((s<0?'12':'13')+' · shaped leather boot','leather',
   fieldMesh(p=>smooth(ell(p,[s*.30,.19,.115],[.137,.18,.245]),
    cap(p,[s*.30,.20,.02],[s*.30,.76,.016],.129,.145),.065),
   [[s*.30-.23,.015,-.21],[s*.30+.23,.82,.42]],.038,
   (x,y,z)=>[(x-s*.30+.23)/.46,y/.82]),'Vanguard / boots');
  // One pair of gloves, no separately modelled stitches/knuckles.
  const glove=p=>{
   let d=20;for(const s of [-1,1]){
    d=Math.min(d,ell(p,[s*.89,2.595,.067],[.09,.135,.073]));
   }return d;
  };
  add('14 · white gloves / single accessory material','ivory',
   fieldMesh(glove,[[-1.08,2.42,-.07],[1.08,2.79,.21]],.025,
    (x,y,z)=>[(x+1.08)/2.16,(y-2.42)/.37]),'Vanguard / gloves');
  // Material-first: intentional, constrained groups instead of hundreds of parts.
  model.name='Hooded Vanguard · Material Study';
  model.parts=parts;model.meshGroups=[];
  model.rigging=null;model.poseFrames=[];model.poseNeutral=null;
  model.editedAt='local';
  model.reference='Original material-driven hooded armored male inspired by owner reference. No weapon or bird. Connected anatomical silhouette; mapped 2D armor engraving, scarf folds, cloth stitching and leather; separately controllable cloak tails/shoulder armor. Static starter; full body rig not yet authored.';
  scene.project.name=model.name;
  scene.project.kind='model-atelier';
  scene.project.template=se291Id;scene.project.canonicalId=se291Id;
  scene.project.environmentSettings={...scene.project.environmentSettings,
   showTerrain:false,showScenery:false,background:'#182331'};
  scene.engine='§wyrl§ Engine · Maker v11.291';scene.version=11.291;
  se291Stats.lastParts=parts.length;
  se291Stats.lastTriangles=parts.reduce((n,p)=>n+p.topologyMesh.indices.length/3,0);
  se291Stats.successes++;
  return scene;
 }catch(error){se291Stats.lastError=String(error?.message||error);console.error('Hooded Vanguard model generation',error);throw error;}
}
function se291OpenHero(force=false){
 if(dirty&&!force&&!confirm('Open Hooded Vanguard and discard unsaved scene changes?'))return false;
 try{
  const source=se291HeroScene();
  ModelAtelier.close();loadProject(source,{workspaceLocal:true});
  initializeHistory('Opened Hooded Vanguard material study');markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  se232ActivateSelectedModelWorkspace();ModelAtelier.syncProject();
  requestAnimationFrame(()=>requestAnimationFrame(()=>
   window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast('Hooded Vanguard · '+se291Stats.lastParts+' native meshes with mapped materials');
  return true;
 }catch(error){
  console.error('Hooded Vanguard starter',error);
  toast('Hooded Vanguard unavailable: '+String(error.message||error).slice(0,140));
  return false;
 }
}
const se291PreviousTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template===se291Id)return se291OpenHero(force);
 return se291PreviousTemplate(template,force);
};
if(new URLSearchParams(location.search).get('project')===se291Id)
 queueMicrotask(()=>se291OpenHero(true));
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:se291Id,createScene:se291HeroScene,open:se291OpenHero,
 status:()=>({...se291Stats,textureTiles:Object.keys(se291Tiles),loadedTextures:se291Textures.size,
  rigged:false,weapon:false,bird:false})
});