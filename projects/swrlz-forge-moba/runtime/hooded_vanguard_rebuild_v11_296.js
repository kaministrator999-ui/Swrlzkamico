// §E v11.296: rebuilt Hooded Vanguard from owner reference.
// Original v11.291 factory is retained; only fresh starter construction is replaced.
// UV-aligned 384px color / tangent-normal / roughness texture maps are generated
// once per named surface, then shared by all pieces using that surface.
const se296Maps=new Map();
const se296Palette={
 'v296:skin':{color:[210,174,154],rough:.84,metal:0},
 'v296:hair':{color:[52,39,34],rough:.79,metal:0},
 'v296:hood':{color:[83,67,58],rough:.91,metal:0},
 'v296:scarf':{color:[216,220,217],rough:.9,metal:0},
 'v296:uniform':{color:[58,70,78],rough:.81,metal:.06},
 'v296:armor':{color:[79,94,108],rough:.43,metal:.48},
 'v296:pauldron':{color:[70,83,95],rough:.4,metal:.52},
 'v296:teal':{color:[25,105,116],rough:.77,metal:.02},
 'v296:leather':{color:[79,53,43],rough:.87,metal:0},
 'v296:gloves':{color:[196,202,201],rough:.79,metal:0},
 'v296:boots':{color:[48,48,52],rough:.77,metal:.06}
};
function se296TextureSet(tile){
 if(se296Maps.has(tile))return se296Maps.get(tile);
 const spec=se296Palette[tile]||se296Palette['v296:uniform'],size=384;
 function canvas(){const c=document.createElement('canvas');c.width=c.height=size;return c;}
 const color=canvas(),height=canvas(),roughness=canvas();
 const cc=color.getContext('2d',{willReadFrequently:true});
 const hc=height.getContext('2d',{willReadFrequently:true});
 const rc=roughness.getContext('2d',{willReadFrequently:true});
 const ci=cc.createImageData(size,size),hi=hc.createImageData(size,size),ri=rc.createImageData(size,size);
 const material=tile.slice(5),cloth=['hood','scarf','uniform','teal','gloves'].includes(material);
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){
  const i=(y*size+x)*4;
  const noise=((Math.imul(x+17,73856093)^Math.imul(y+29,19349663)^Math.imul(material.length,83492791))>>>0)%127/127-.5;
  const stripe=cloth?(Math.sin(x*.32)*1.7+Math.sin(y*.27)*1.1):Math.sin((x+y)*.06)*.9;
  const mix=noise*9+stripe;
  for(let c=0;c<3;c++)ci.data[i+c]=Math.max(0,Math.min(255,spec.color[c]+mix));
  const v=128+noise*11+stripe*1.6;
  hi.data[i]=hi.data[i+1]=hi.data[i+2]=v;
  const rough=255*(spec.rough+(noise*.045));
  ri.data[i]=ri.data[i+1]=ri.data[i+2]=Math.min(255,Math.max(0,rough));
  ci.data[i+3]=hi.data[i+3]=ri.data[i+3]=255;
 }
 cc.putImageData(ci,0,0);hc.putImageData(hi,0,0);rc.putImageData(ri,0,0);
 const S=size/384;
 const line=(ctx,pts,c,w=2)=>{
  ctx.beginPath();ctx.moveTo(pts[0][0]*S,pts[0][1]*S);
  for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0]*S,pts[i][1]*S);
  ctx.strokeStyle=c;ctx.lineWidth=w*S;ctx.lineCap='round';ctx.lineJoin='round';ctx.stroke();
 };
 const draw=(pts,col,width=2,ridge=30)=>{
  line(cc,pts,col,width);line(hc,pts,'rgb('+ridge+','+ridge+','+ridge+')',width);
 };
 const ellipse=(ctx,x,y,rx,ry,col)=>{
  ctx.beginPath();ctx.ellipse(x*S,y*S,rx*S,ry*S,0,0,Math.PI*2);
  ctx.fillStyle=col;ctx.fill();
 };
 if(material==='skin'){
  // Front of head is centered at u=.5. Vertex latitude raises toward canvas top.
  for(const x of [165,219]){
   ellipse(cc,x,191,17,9,'#8a6860');ellipse(cc,x,192,15,8,'#eee9df');
   ellipse(cc,x,192,6.9,8.5,'#637985');ellipse(cc,x,193,3.2,6.6,'#242e37');
   ellipse(cc,x-2,189,2.2,2.5,'#f8f7f0');
   line(cc,[[x-19,177],[x-11,172],[x+7,171],[x+17,175]],'#46332e',3);
   line(cc,[[x-16,202],[x,205],[x+13,201]],'rgba(145,102,95,.65)',1.4);
  }
  ellipse(cc,151,247,13,6,'rgba(208,133,124,.22)');
  ellipse(cc,233,247,13,6,'rgba(208,133,124,.22)');
  line(cc,[[191,237],[190,258],[194,262]],'rgba(139,94,86,.55)',1.6);
  line(cc,[[180,286],[189,289],[196,289],[204,286]],'#975e5b',2.3);
  line(cc,[[181,287],[190,292],[197,291],[202,288]],'#c88780',1);
 }
 if(material==='hair'){
  for(let x=8;x<384;x+=13){
   line(cc,[[x+3,3],[x-9,124],[x+6,253],[x-4,383]],'rgba(183,142,105,.35)',1.7);
   line(hc,[[x+3,3],[x-9,124],[x+6,253],[x-4,383]],'#a2a2a2',2);
  }
 }
 if(material==='hood'){
  for(const x of [9,375]){
   draw([[x,3],[x+2,100],[x-2,252],[x,381]],'#b29d85',4,156);
   draw([[x+9,4],[x+11,130],[x+8,276],[x+9,380]],'#342924',2,110);
  }
  for(let y=18;y<382;y+=32)draw([[15,y],[28,y+5],[33,y]],'rgba(204,175,128,.32)',1.5,143);
 }
 if(material==='scarf'){
  for(let y=24;y<384;y+=68){
   draw([[3,y+13],[88,y+8],[195,y+26],[285,y-4],[382,y+16]],'rgba(99,119,133,.28)',3,148);
   draw([[2,y+25],[125,y+22],[264,y+31],[383,y+17]],'rgba(250,249,239,.6)',3,147);
  }
  draw([[4,378],[192,371],[380,378]],'#bd9b65',3,167);
 }
 if(material==='armor'){
  for(const x of [17,367])draw([[x,8],[x+7,100],[x+12,230],[x,380]],'#c9ab73',5,180);
  draw([[40,82],[188,27],[343,82]],'#c3a273',4,173);
  draw([[56,104],[192,170],[328,104]],'#344755',5,110);
  draw([[80,204],[192,244],[303,204]],'#b69a67',3,172);
  draw([[135,298],[192,339],[249,298]],'#c1a56f',3,177);
  for(const x of [99,284])draw([[x,116],[x+(x<192?24:-24),184],[x,258]],'#b3a17f',2,162);
 }
 if(material==='pauldron'){
  draw([[13,19],[85,9],[194,17],[295,8],[371,22]],'#d5b882',7,176);
  draw([[14,363],[91,354],[191,373],[287,353],[370,362]],'#b99762',5,176);
  draw([[28,50],[129,123],[195,187],[265,119],[361,48]],'rgba(40,101,114,.8)',9,167);
  draw([[45,233],[190,294],[342,232]],'#b69865',4,158);
 }
 if(material==='teal'){
  draw([[10,0],[12,383]],'#c5a46c',6,179);
  draw([[373,0],[372,383]],'#c5a46c',6,179);
  for(let y=28;y<384;y+=64){
   draw([[26,y],[94,y+12],[178,y+6],[269,y+15],[356,y]],'rgba(66,167,165,.35)',2,146);
  }
  for(let y=30;y<384;y+=96)draw([[166,y],[184,y+14],[202,y],[184,y-14],[166,y]],'rgba(203,180,114,.37)',2,167);
 }
 if(material==='uniform'){
  for(let y=12;y<384;y+=42)draw([[2,y],[108,y+8],[274,y+4],[383,y+14]],'rgba(169,183,189,.22)',1.4,142);
 }
 if(material==='leather'||material==='boots'){
  for(let x=21;x<384;x+=62){
   draw([[x,1],[x-5,133],[x+5,266],[x,383]],'rgba(155,121,85,.25)',2,154);
  }
  draw([[18,28],[366,28]],'#ba976b',3,163);
  draw([[19,354],[366,354]],'#45322b',3,110);
  if(material==='leather'){
   draw([[137,111],[245,111],[245,214],[137,214],[137,111]],'#bca16b',5,168);
   draw([[163,130],[218,130],[218,199],[163,199]],'#302820',3,108);
  }
 }
 if(material==='gloves'){
  for(const x of [75,135,196,254,315]){
   draw([[x-16,191],[x+4,195],[x+20,191]],'rgba(119,130,133,.48)',2,142);
   draw([[x-14,244],[x+3,251],[x+19,243]],'rgba(131,145,148,.32)',1.3,144);
  }
 }
 // Derive tangent-space normal from drawn grayscale height, including
 // matching stitched/engraved lines; surface shading comes from the mesh.
 const raw=hc.getImageData(0,0,size,size).data,norm=canvas(),nc=norm.getContext('2d');
 const ni=nc.createImageData(size,size),q=ni.data;
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){
  const i=(y*size+x)*4;
  const xl=(y*size+Math.max(0,x-1))*4,xr=(y*size+Math.min(size-1,x+1))*4;
  const yu=(Math.max(0,y-1)*size+x)*4,yd=(Math.min(size-1,y+1)*size+x)*4;
  const dx=(raw[xr]-raw[xl])*.018,dy=(raw[yd]-raw[yu])*.018;
  const len=Math.hypot(dx,dy,1);
  q[i]=127.5*(1-dx/len);q[i+1]=127.5*(1-dy/len);q[i+2]=127.5*(1+1/len);q[i+3]=255;
 }
 nc.putImageData(ni,0,0);
 const set={color,normal:norm,roughness};
 se296Maps.set(tile,set);
 return set;
}
const se296OriginalHeroMaterial=se291HeroMaterial;
se291HeroMaterial=function(part){
 const tile=part.heroPBR?.tile;
 if(!se296Palette[tile])return se296OriginalHeroMaterial(part);
 const canvases=se296TextureSet(tile),spec=se296Palette[tile],maps={};
 for(const mode of ['color','normal','roughness']){
  const tex=new THREE.CanvasTexture(canvases[mode]);
  tex.colorSpace=mode==='color'?THREE.SRGBColorSpace:THREE.NoColorSpace;
  tex.wrapS=tex.wrapT=THREE.ClampToEdgeWrapping;
  tex.anisotropy=2;tex.minFilter=THREE.LinearMipmapLinearFilter;
  tex.needsUpdate=true;maps[mode]=tex;
 }
 // Dispose only the redundant CanvasTexture wrappers, not source canvases:
 // subsequent parts reuse one preconstructed material texture set.
 const previous=se296Maps.get(tile);
 if(previous.textures)for(const mode of Object.keys(maps))maps[mode].dispose();
 else previous.textures=maps;
 const tex=previous.textures;
 return new THREE.MeshStandardMaterial({color:'#ffffff',map:tex.color,
  normalMap:tex.normal,normalScale:new THREE.Vector2(.44,.44),
  roughnessMap:tex.roughness,roughness:1,metalness:spec.metal,
  side:THREE.DoubleSide});
};
function se296HeroScene(){
 se291Stats.attempts++;
 try{
  const ops=window.SWYRL_ENGINE_HAND_SURFACE;
  if(!ops?.surface||!ops?.weld)throw Error('Native mesh surface tools unavailable');
  const scene=structuredClone(MODEL_ATELIER_CANONICAL_PROJECT),model=scene.project.modelAtelier;
  const parts=[];
  const R=n=>+n.toFixed(5);
  function add(name,tile,geometry,group){
   if(!geometry?.positions?.length||!geometry?.indices?.length||
      geometry.uvs?.length!==geometry.positions.length/3*2)
    throw Error('Missing geometry or UV for '+name);
   const p={id:'vanguard-rebuilt-'+String(parts.length).padStart(2,'0'),name,
    kind:'topologyMesh',topologyMesh:geometry,color:'#ffffff',material:'matte',
    heroPBR:{tile:'v296:'+tile,uv:'explicit',maps:['albedo','normal','roughness']},
    group:group||'Vanguard / rebuilt anatomy',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1]};
   parts.push(p);return p;
  }
  function ribbon(rows,cols,fn){
   const g={positions:[],uvs:[],indices:[]};
   for(let i=0;i<=rows;i++)for(let j=0;j<=cols;j++){
    const u=i/rows,v=j/cols,p=fn(u,v);
    g.positions.push(...p.map(R));g.uvs.push(R(v),R(u));
    if(i<rows&&j<cols){
     const a=i*(cols+1)+j,b=a+cols+1;
     g.indices.push(a,a+1,b,a+1,b+1,b);
    }
   }
   return g;
  }
  function join(geometries){
   const g={positions:[],uvs:[],indices:[]};
   for(const v of geometries){
    const offset=g.positions.length/3;
    g.positions.push(...v.positions);g.uvs.push(...v.uvs);
    for(const i of v.indices)g.indices.push(i+offset);
   }
   return g;
  }
  const ell=(p,c,r)=>(Math.hypot(...p.map((v,i)=>(v-c[i])/r[i]))-1)*Math.min(...r);
  const cap=(p,a,b,r0,r1)=>{
   const q=b.map((v,i)=>v-a[i]),l=q.reduce((n,v)=>n+v*v,0);
   const t=Math.max(0,Math.min(1,p.reduce((n,v,i)=>n+(v-a[i])*q[i],0)/l));
   return Math.hypot(...p.map((v,i)=>v-a[i]-q[i]*t))-(r0+(r1-r0)*t);
  };
  const smooth=(a,b,k)=>{const h=Math.max(0,k-Math.abs(a-b))/k;return Math.min(a,b)-h*h*k*.25;};
  function field(fieldFn,bounds,step,project){
   const g=ops.weld(ops.surface((x,y,z)=>fieldFn([x,y,z]),bounds,step));
   if(!g?.positions?.length||!g.indices?.length)throw Error('Empty anatomy mesh');
   g.uvs=[];
   for(let i=0;i<g.positions.length;i+=3){
    const p=[g.positions[i],g.positions[i+1],g.positions[i+2]];
    const uv=project(...p);g.uvs.push(R(uv[0]),R(uv[1]));
   }
   return g;
  }
  // One anatomically proportioned silhouette, with tapered limbs and no mitten
  // appendages: each glove below has its own modeled palm and five digits.
  function figure(p){
   let d=ell(p,[0,3.03,-.018],[.385,.62,.232]);
   d=smooth(d,ell(p,[0,2.47,-.007],[.318,.28,.225]),.12);
   d=smooth(d,cap(p,[0,3.45,0],[0,3.81,0],.11,.105),.095);
   for(const s of [-1,1]){
    d=smooth(d,cap(p,[s*.32,3.40,-.02],[s*.65,3.16,.002],.137,.117),.085);
    d=smooth(d,cap(p,[s*.65,3.16,0],[s*.86,2.73,.05],.116,.083),.08);
    d=smooth(d,cap(p,[s*.17,2.36,-.018],[s*.235,1.32,0],.178,.116),.115);
    d=smooth(d,cap(p,[s*.235,1.32,0],[s*.26,.37,.035],.115,.09),.07);
   }
   return d;
  }
  add('01 · anatomically tapered torso, sleeves and trousers','uniform',
   field(figure,[[-1.10,.25,-.35],[1.10,3.89,.38]],.051,
    (x,y)=>[(x+1.10)/2.20,(y-.25)/3.64]));
  // A single head surface: no extruded sphere for the chin, lips or ears.
  // Facial relief is controlled continuously by the actual face coordinates.
  add('02 · unified face, shaped jaw and restrained nose','skin',
   ribbon(45,96,(u,v)=>{
    const a=(v-.5)*Math.PI*2,r=Math.pow(Math.max(0,Math.sin(Math.PI*u)),.79);
    const y=3.76+.76*u,cheek=1+.047*Math.exp(-Math.pow((u-.51)/.13,2));
    const jaw=1-.17*Math.max(0,.38-u)/.38;
    const x=.257*r*Math.sin(a)*cheek*jaw;
    const front=Math.max(0,Math.cos(a));
    const n=Math.exp(-Math.pow((u-.33)/.09,2))*Math.exp(-Math.pow(a/.17,2));
    const lips=Math.exp(-Math.pow((u-.21)/.034,2))*Math.exp(-Math.pow(a/.17,2));
    const z=.043+.211*r*Math.cos(a)+.035*n+.006*lips;
    return [x,y,z];
   }),'Vanguard / face');
  // A fitted undercut hair mass and long locks, NOT a hemisphere haircut.
  add('03 · tapered dark hair with natural hairline','hair',
   ribbon(20,72,(u,v)=>{
    const a=(v-.5)*Math.PI*2;
    const base=4.24+.038*Math.cos(a*2)+.025*Math.sin(a*3);
    const y=base+(.275-.026*Math.cos(a))*u;
    const r=Math.sqrt(Math.max(.006,1-u*u));
    return [.267*r*Math.sin(a),y,.034+.241*r*Math.cos(a)];
   }),'Vanguard / hair');
  const locks=[];
  for(const s of [-1,1])for(let side=0;side<2;side++){
   locks.push(ribbon(20,4,(u,v)=>{
    const taper=Math.pow(1-u,.62),w=(.067-side*.018)*taper;
    const cx=s*(.208+side*.04+.037*Math.sin(u*Math.PI));
    return [cx+(v-.5)*w,4.28-u*(.58+side*.12),
      .177+.026*Math.sin(u*3.7+side)+.012*Math.sin(v*Math.PI)];
   }));
  }
  add('04 · layered face-framing hair locks','hair',join(locks),'Vanguard / hair');
  // A real wrapping hood shell with a broad open face aperture and overhanging
  // curved front brim. Both pieces belong to one editable garment mesh.
  const hood=ribbon(28,72,(u,v)=>{
    const a=.67+(Math.PI*2-1.34)*v;
    const y=3.57+.97*u;
    const r=.418-.145*u+.02*Math.sin(Math.PI*u);
    return [r*Math.sin(a),y,-.082+(.337-.128*u)*Math.cos(a)-.025*u];
  });
  const hoodBrim=ribbon(6,36,(u,v)=>{
    const x=(v-.5)*.61;
    return [x,4.44+.095*Math.sin(Math.PI*v)+.024*u,
      .142+.042*Math.sin(Math.PI*v)-.035*u];
  });
  add('05 · curved fitted hood shell and forward face brim','hood',
   join([hood,hoodBrim]),'Vanguard / hood');
  add('06 · gathered neck scarf with shallow cloth folds','scarf',
   ribbon(15,48,(u,v)=>{
    const a=v*Math.PI*2;
    return [Math.sin(a)*(.213+.045*Math.sin(u*Math.PI)),
      3.57+.255*u+.015*Math.sin(3*a+u*5),
      .04+Math.cos(a)*(.163+.025*Math.sin(u*Math.PI))];
   }),'Vanguard / garments');
  add('07 · draped triangular scarf and layered hem','scarf',
   ribbon(20,38,(u,v)=>{
    const x=(v-.5)*(.70-.21*u);
    const y=3.54-u*(.36+.15*(1-Math.pow(Math.abs(v-.5)*2,.75)));
    const z=.27+.055*Math.sin(Math.PI*v)+.014*Math.sin(u*9);
    return [x,y,z];
   }),'Vanguard / garments');
  // Contoured plate tapers to the waist; actual decorative lines live in
  // a matching UV atlas, not independent metallic strips.
  add('08 · fitted breastplate with UV-engraved metalwork','armor',
   ribbon(29,42,(u,v)=>{
    const x=(v-.5)*(.68+.12*Math.sin(Math.PI*u))*(1-.10*u);
    const y=2.58+.86*u-.06*Math.abs(v-.5);
    const z=.224+.074*Math.sin(Math.PI*v)+.018*Math.sin(Math.PI*u);
    return [x,y,z];
   }),'Vanguard / armor');
  for(const s of [-1,1])add((s<0?'09':'10')+' · formed layered shoulder pauldron',
   'pauldron',ribbon(18,30,(u,v)=>{
    const x=s*(.29+.45*u);
    const width=Math.sin(Math.PI*u)*.11;
    const y=3.52-.23*u+.045*Math.sin(Math.PI*v)-.045*Math.pow(v-.5,2);
    const z=-.05+.23*Math.sin(Math.PI*v)+width*(v-.5);
    return [x,y,z];
   }),'Vanguard / articulated shoulders');
  for(const s of [-1,1])add((s<0?'11':'12')+' · flowing lined teal coat panel',
   'teal',ribbon(44,18,(u,v)=>{
    const taper=Math.pow(Math.max(.02,1-Math.pow(u,5)),.48);
    const cx=s*(.30+.17*u+.075*Math.sin(u*Math.PI));
    const width=(.26+.11*Math.sin(Math.PI*u))*taper;
    return [cx+(v-.5)*width,2.49-2.18*u+.06*u*v,
     -.125-.22*u+.075*Math.sin(Math.PI*u*2+v*Math.PI)];
   }),'Vanguard / moving cloth panels');
  add('13 · narrow buckled leather waist belt','leather',
   ribbon(8,46,(u,v)=>{
    const a=v*Math.PI*2;
    return [Math.sin(a)*.327,2.48+.118*u,.008+Math.cos(a)*.236];
   }),'Vanguard / accessories');
  // A real hand shape: palm, four individually formed fingers and a thumb.
  // One welded SDF topology per glove; detailed knuckle shading is mapped.
  for(const s of [-1,1]){
   const hx=s*.888;
   const hand=p=>{
    let d=ell(p,[hx,2.57,.074],[.099,.13,.061]);
    d=smooth(d,cap(p,[hx,2.70,.069],[hx,2.59,.076],.085,.095),.035);
    for(let i=0;i<4;i++){
     const x=hx+(i-1.5)*.043;
     const lengths=[.115,.145,.137,.108],bottom=2.36-lengths[i];
     d=smooth(d,cap(p,[x,2.49,.085],[x+(i-1.5)*.006,bottom,.099],
      .022,.014),.013);
    }
    const thumbX=hx-s*.097;
    d=smooth(d,cap(p,[hx-s*.071,2.59,.104],[thumbX-s*.018,2.40,.145],
      .036,.021),.024);
    return d;
   };
   add((s<0?'14':'15')+' · sculpted glove, four fingers and thumb','gloves',
    field(hand,[[hx-.20,2.15,-.005],[hx+.20,2.75,.22]],.014,
      (x,y)=>[(x-hx+.20)/.40,(y-2.15)/.60]),'Vanguard / hands');
  }
  for(const s of [-1,1]){
   const x=s*.263;
   add((s<0?'16':'17')+' · shaped leather boot with toe','boots',
    field(p=>smooth(ell(p,[x,.182,.135],[.132,.16,.24]),
     cap(p,[x,.21,.018],[x,.67,.018],.131,.115),.065),
    [[x-.21,.018,-.23],[x+.21,.76,.41]],.035,
    (px,y)=>[(px-x+.21)/.42,y/.76]),'Vanguard / boots');
  }
  model.name='Hooded Vanguard · Rebuilt Character';
  model.parts=parts;model.meshGroups=[];model.assemblies=null;
  model.rigging=null;model.poseFrames=[];model.poseNeutral=null;model.editedAt='local';
  model.reference='v11.296 rebuilt static male character. Smooth fitted face, five-digit gloves, hood shell and hair, sculpted fabric drapes, shaped armor, tapered teal coat, UV-mapped cloth/metal/leather/skin color, normal and roughness. No weapon, bird or full-body skeletal rig.';
  scene.project.name=model.name;scene.project.kind='model-atelier';
  scene.project.template='hooded-vanguard';scene.project.canonicalId='hooded-vanguard';
  scene.project.environmentSettings={...scene.project.environmentSettings,
   showTerrain:false,showScenery:false,background:'#182331'};
  scene.engine='§wyrl§ Engine · Maker v11.296';scene.version=11.296;
  se291Stats.lastParts=parts.length;
  se291Stats.lastTriangles=parts.reduce((n,p)=>n+p.topologyMesh.indices.length/3,0);
  se291Stats.lastError=null;se291Stats.successes++;
  return scene;
 }catch(e){se291Stats.lastError=String(e?.message||e);
  console.error('Vanguard reconstructed model failed',e);throw e;}
}
se291HeroScene=se296HeroScene;
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',createScene:se296HeroScene,open:se291OpenHero,
 status:()=>({...se291Stats,textureTiles:Object.keys(se296Palette),
  generatedAtlases:se296Maps.size,rigged:false,weapon:false,bird:false,
  version:'v11.296',anatomicalHands:true})
});
