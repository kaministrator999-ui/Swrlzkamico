// §E v11.283 · Weathered Rocky Hand. Owner: "more smoothish."
// Only the Rocky Anime Hand starter is affected. Keep the solid rock body,
// no exposed glove core, all 17 bone joints and existing amber rock fractures.
// Smooth the rock SURFACE, not the silhouette into human skin.
const se283RockOriginalMesh=se282Mesh;
const se283RockOriginalScene=se282FullRockScene;
const se283RockStats={meshes:0,vertices:0,triangles:0,subdivision:1,relaxation:.24};
function se283WeatherRockTopology(topology){
 const positions=topology?.positions||[],original=topology?.indices||[];
 if(!positions.length||!original.length)throw Error('Weathering requires a rock topology.');
 // Existing v11.282 triangular geometry intentionally repeats every vertex to
 // produce hard flat shading. Weld only coincident points WITHIN THE SAME ROCK
 // part; joints between distinct stones remain discrete and articulatable.
 const vertices=[],indices=[],byPosition=new Map();
 function add(p){
  if(!p.every(Number.isFinite))throw Error('Nonfinite weathered rock coordinate');
  const key=p.map(v=>Math.round(v*100000)).join(':');
  let id=byPosition.get(key);
  if(id===undefined){id=vertices.length;vertices.push(p.slice());byPosition.set(key,id);}
  return id;
 }
 for(let i=0;i<original.length;i++){
  const k=original[i],at=k*3;
  if(!Number.isInteger(k)||at+2>=positions.length)throw Error('Invalid cliff triangle index');
  indices.push(add([positions[at],positions[at+1],positions[at+2]]));
 }
 // One real triangle subdivision: midpoint vertices are shared by adjoining
 // faces. This gives the stone slabs rounded edges WITHOUT replacing them by
 // an interpolated smooth glove surface or adding any skin mesh.
 const midpoint=new Map(),split=[];
 function mid(a,b){
  const key=a<b?a+':'+b:b+':'+a;
  let id=midpoint.get(key);
  if(id===undefined){
   const p=vertices[a],q=vertices[b];
   id=vertices.length;vertices.push([(p[0]+q[0])*.5,(p[1]+q[1])*.5,(p[2]+q[2])*.5]);
   midpoint.set(key,id);
  }
  return id;
 }
 for(let i=0;i<indices.length;i+=3){
  const a=indices[i],b=indices[i+1],c=indices[i+2];
  if(a===b||b===c||a===c)continue;
  const ab=mid(a,b),bc=mid(b,c),ca=mid(c,a);
  split.push(a,ab,ca,ab,b,bc,ca,bc,c,ab,bc,ca);
 }
 const neighbours=vertices.map(()=>new Set());
 for(let i=0;i<split.length;i+=3){
  const a=split[i],b=split[i+1],c=split[i+2];
  neighbours[a].add(b);neighbours[a].add(c);
  neighbours[b].add(a);neighbours[b].add(c);
  neighbours[c].add(a);neighbours[c].add(b);
 }
 // Two gentle Laplacian rounds soften sharp artificial corner spikes. Each
 // stone remains fully closed and separate. The low relaxation strength keeps
 // a naturally worn, irregular cliff silhouette and avoids a rubbery hand.
 const factor=se283RockStats.relaxation;
 for(let step=0;step<2;step++){
  const next=vertices.map((p,i)=>{
   const around=neighbours[i];if(around.size<3)return p.slice();
   const q=[0,0,0];for(const j of around){for(let k=0;k<3;k++)q[k]+=vertices[j][k];}
   return p.map((value,k)=>value+(q[k]/around.size-value)*factor);
  });
  for(let i=0;i<vertices.length;i++)vertices[i]=next[i];
 }
 const result={
  positions:vertices.flatMap(v=>v.map(n=>+n.toFixed(5))),
  uvs:vertices.flatMap(v=>[+(v[0]*.32).toFixed(5),+(v[1]*.32).toFixed(5)]),
  indices:split
 };
 if(result.positions.length/3>16000||result.indices.length>96000)
  throw Error('Rock smoothing exceeded native model bounds.');
 se283RockStats.meshes++;
 se283RockStats.vertices+=vertices.length;
 se283RockStats.triangles+=split.length/3;
 return result;
}
// Hooks the exact v11.282 native rock mesh factory. Emissive fissures still
// use se281CrackTopology, so their thin highlighted lines remain crisp.
se282Mesh=function(){
 const mesh=se283RockOriginalMesh();
 return {
  addTri:mesh.addTri,
  quad:mesh.quad,
  result:()=>se283WeatherRockTopology(mesh.result())
 };
};
// Existing starter loader calls se281RockScene dynamically. Reuse it, stamp
// current scene provenance, and keep its rig/keyframes and project identity.
se281RockScene=function(){
 se283RockStats.meshes=0;se283RockStats.vertices=0;se283RockStats.triangles=0;
 const scene=se283RockOriginalScene();
 const m=scene.project?.modelAtelier;
 if(!m||!se220RigValidate(m.rigging))
  throw Error('Weathered rock hand must retain 17 bone rig.');
 if(m.parts.some(p=>p.organicSurface||/Underlying.*glove/i.test(p.name)))
  throw Error('Smooth glove must not reappear beneath rock.');
 m.reference='Weathered cliff hand: softly rounded natural rock facets over a completely stone palm, sides, fingers, thumb and wrist. Continuous rock coverage with separate bones, rocks and glowing fault seams.';
 scene.engine='§wyrl§ Engine · Maker v11.283';
 scene.version=11.283;
 return scene;
};
window.SWYRL_ENGINE_WEATHERED_ROCK_HAND=Object.freeze({
 createScene:()=>se281RockScene(),
 status:()=>({...se283RockStats,sourceVersion:'v11.283',
  noOrganicGlove:true,originalRockMeshIntact:true})
});
