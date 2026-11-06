// §E v11.290 · Fix the rejected v11.289 forearm and improve material relief.
// The old post-process assumed an original mesh bottom near y=.57; the actual
// v11.217 anatomically tapered shell closes near y=.85, so that assertion could
// reject a real starter. Build the gauntlet directly into the existing SDF
// before native meshing; no extra rock or crack objects are created.
const se290GauntletDebug={attempts:0,successes:0,failures:0,lastError:null,lastMesh:null};
function se290Math(){
 const ell=(p,c,r)=>(Math.hypot(...p.map((x,i)=>(x-c[i])/r[i]))-1)*Math.min(...r);
 const cap=(p,a,b,ra,rb)=>{
  const d=b.map((x,i)=>x-a[i]),q=p.map((x,i)=>x-a[i]);
  const k=Math.max(0,Math.min(1,q.reduce((s,x,i)=>s+x*d[i],0)/d.reduce((s,x)=>s+x*x,0)));
  return Math.hypot(...p.map((x,i)=>x-a[i]-k*d[i]))-(ra+(rb-ra)*k);
 };
 const blend=(a,b,k)=>{
  const h=Math.max(0,k-Math.abs(a-b))/k;
  return Math.min(a,b)-h*h*k*.25;
 };
 return {ell,cap,blend};
}
function se290GauntletField(){
 const math=se290Math();
 if(typeof se217OrganicHandSkin!=='function'||!Array.isArray(se217FingerSpec))
  throw Error('Hand anatomy source is unavailable');
 const hand=se217OrganicHandSkin(se217FingerSpec,math);
 const {cap,blend}=math;
 return (x,y,z)=>{
  const p=[x,y,z];
  // Rounded forearm transitions smoothly into the original wrist/thenar.
  // A slightly broader distal end gives a GAUNTLET, not a long straight arm.
  // Flat lower plane closes the SINGLE contiguous surface near y=.20.
  const forearm=cap(p,[.004,.20,-.004],[.004,1.29,-.009],.322,.232);
  const continuous=blend(hand(x,y,z),forearm,.19);
  return Math.max(continuous,.20-y);
 };
}
function se290BuildGauntletSurface(part){
 se290GauntletDebug.attempts++;
 try{
  const ops=window.SWYRL_ENGINE_HAND_SURFACE;
  if(typeof ops?.surface!=='function'||typeof ops?.weld!=='function')
   throw Error('Native connected model surface engine is unavailable');
  const field=se290GauntletField();
  const bounds=[[-1.58,.12,-.56],[.88,3.51,.55]];
  const mesh=ops.weld(ops.surface(field,bounds,.047));
  const pos=mesh?.positions,ids=mesh?.indices;
  if(!pos||pos.length<300||pos.length%3||!ids||ids.length<300||ids.length%3)
   throw Error('Connected gauntlet topology failed validation');
  let bottom=Infinity,top=-Infinity,nonfinite=0;
  for(let i=0;i<pos.length;i+=3){
   if(!Number.isFinite(pos[i])||!Number.isFinite(pos[i+1])||!Number.isFinite(pos[i+2]))nonfinite++;
   bottom=Math.min(bottom,pos[i+1]);top=Math.max(top,pos[i+1]);
  }
  if(nonfinite||bottom<.15||bottom>.26||top<3.1)
   throw Error('Generated gauntlet bounds invalid: '+JSON.stringify({bottom,top,nonfinite}));
  // Native topology + bone envelope remain one part and the same 17-bone rig.
  part.topologyMesh=mesh;
  const state={minY:bottom,maxY:top,vertices:pos.length/3,triangles:ids.length/3,meshes:1};
  se290GauntletDebug.lastMesh=state;se290GauntletDebug.successes++;
  return state;
 }catch(error){
  se290GauntletDebug.failures++;se290GauntletDebug.lastError=String(error?.message||error);
  console.error('Cliff Hand gauntlet construction',error);
  throw error;
 }
}
function se290GauntletUV(part){
 const mesh=part.topologyMesh,p=mesh?.positions;
 if(!p?.length||p.length%3)throw Error('Cliff Hand forearm UV input is missing');
 let lowX=Infinity,highX=-Infinity,lowY=Infinity,highY=-Infinity;
 for(let i=0;i<p.length;i+=3){
  lowX=Math.min(lowX,p[i]);highX=Math.max(highX,p[i]);
  lowY=Math.min(lowY,p[i+1]);highY=Math.max(highY,p[i+1]);
 }
 const rx=Math.max(.2,highX-lowX),ry=Math.max(.2,highY-lowY),uv=[];
 for(let i=0;i<p.length;i+=3){
  const x=p[i],y=p[i+1],z=p[i+2];
  // Softly wrap front/back/side instead of clamping stone at the forearm tip.
  const u=(x-lowX+.22*z)/rx, v=(y-lowY+.065*z)/ry;
  uv.push(Math.max(.003,Math.min(.997,u)),Math.max(.003,Math.min(.997,v)));
 }
 mesh.uvs=uv;
 return uv.length/2;
}
function se290CliffMaterial(part){
 // PBR from the existing owner-provided high-resolution atlas, but favor
 // visible rock depth rather than the flat, diffuse-only stone appearance.
 // Stronger tangent-space normals shade fractures; AO darkens mapped seams.
 // Nothing changes geometry at the material stage.
 const mat=new THREE.MeshStandardMaterial({
  color:'#fff0df',
  map:se288AtlasTile(0,true),
  normalMap:se288AtlasTile(1),
  normalMapType:THREE.TangentSpaceNormalMap,
  normalScale:new THREE.Vector2(1.12,1.12),
  aoMap:se288AtlasTile(3),
  aoMapIntensity:1.28,
  roughnessMap:se288AtlasTile(2),
  roughness:.88,metalness:0,side:THREE.DoubleSide,
 });
 mat.name='Cliff Hand · dimensional sandstone, deep mapped cracks and subtle moss';
 return mat;
}
window.SWYRL_ENGINE_CLIFF_GAUNTLET_290=Object.freeze({
 id:'plain-hand-base',build:se290BuildGauntletSurface,remapUV:se290GauntletUV,
 status:()=>({...se290GauntletDebug,renderedRockObjects:0,renderedCrackObjects:0,
  atlas:'assets/cliff-hand/cliff_pbr_atlas_384.jpg',material:'enhanced PBR'})
});