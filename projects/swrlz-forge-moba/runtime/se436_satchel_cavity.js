/* SE436_SATCHEL_CAVITY_START */
// Read-only recognition for a single connected inset + inward-extruded body.
// The native topology kernel continues to own conversion and all edits.
const se436SatchelCavity=(()=>{
 const close=(a,b,t)=>Math.abs(a-b)<=t;
 function inspectOne(part){
  const d=part?.topologyMesh;
  if(part?.kind!=='topologyMesh'||!Array.isArray(d?.positions)||!Array.isArray(d?.indices)||d.positions.length<24||d.positions.length>27000||d.indices.length>48000||
   d.positions.length%3||d.indices.length%3||!d.positions.every(Number.isFinite))return null;
  const count=d.positions.length/3;
  if(d.indices.some(i=>!Number.isInteger(i)||i<0||i>=count))return null;
  const coords=Array.from({length:count},(_,i)=>d.positions.slice(i*3,i*3+3));
  const min=coords.reduce((v,p)=>Math.min(v,p[1]),Infinity),max=coords.reduce((v,p)=>Math.max(v,p[1]),-Infinity);
  const minX=Math.min(...coords.map(p=>p[0])),maxX=Math.max(...coords.map(p=>p[0]));
  const minZ=Math.min(...coords.map(p=>p[2])),maxZ=Math.max(...coords.map(p=>p[2]));
  const height=max-min,width=maxX-minX,depth=maxZ-minZ,eps=Math.max(height*1e-5,1e-6);
  if(height<.1||width<.1||depth<.1)return null;
  const caps=new Map(),triangles=[];
  for(let i=0;i<d.indices.length;i+=3){
   const vertices=d.indices.slice(i,i+3).map(id=>coords[id]),[a,b,c]=vertices;
   const ab=b.map((v,k)=>v-a[k]),ac=c.map((v,k)=>v-a[k]);
   const normal=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];
   const len=Math.hypot(...normal);
   if(len<1e-9)continue;
   const lo=Math.min(...vertices.map(p=>p[1])),hi=Math.max(...vertices.map(p=>p[1]));
   triangles.push({lo,hi,vertices});
   // An actual upward-facing floor below the rim, but still above the
   // outer bottom. The top rim cannot qualify as an inset cavity floor.
   if(hi-lo>eps||normal[1]/len<.95||lo<=min+height*.06||hi>=max-height*.08)continue;
   const marginX=width*.035,marginZ=depth*.035;
   if(vertices.some(p=>p[0]<=minX+marginX||p[0]>=maxX-marginX||p[2]<=minZ+marginZ||p[2]>=maxZ-marginZ))continue;
   const key=Math.round(lo/eps),entry=caps.get(key)||{y:lo,count:0,area:0};
   entry.count++;entry.area+=Math.abs(normal[1])*.5;caps.set(key,entry);
  }
  for(const cap of caps.values()){
   if(cap.count<2||cap.area<width*depth*.03)continue;
   // Triangles must connect that lower floor to the actual top rim.
   const walls=triangles.filter(t=>t.lo<=cap.y+eps*2&&t.hi>=max-eps*2&&t.hi-t.lo>height*.08).length;
   if(walls>=4)return {ok:true,partId:part.id,body:part,depth:max-cap.y,walls,capTriangles:cap.count};
  }
  return null;
 }
 function inspect(parts){
  if(!Array.isArray(parts))return {ok:false,body:null};
  const preferred=parts.filter(p=>p?.id==='model-seed'||/body|pouch|satchel|practice/i.test(p?.name||''));
  for(const p of [...preferred,...parts.filter(p=>!preferred.includes(p))]){
   const result=inspectOne(p);if(result)return result;
  }
  return {ok:false,body:preferred.find(p=>p?.kind==='topologyMesh')||null};
 }
 function makeGhost(group){
  if(!group?.isObject3D||typeof THREE==='undefined'||typeof se430MeshOps==='undefined')return false;
  const original=new THREE.BoxGeometry(1.4,1,.65);
  let converted;
  try{converted=se430MeshOps.convert(original);}finally{original.dispose();}
  if(!converted?.ok)return false;
  const d=converted.data,top=Array.from({length:d.indices.length/3},(_,f)=>f).find(f=>{
   const ids=d.indices.slice(f*3,f*3+3),p=ids.map(id=>d.positions.slice(id*3,id*3+3));
   const a=p[0],b=p[1],c=p[2];
   const y=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]);
   return y>.0001;
  });
  if(top===undefined)return false;
  const region=se430MeshOps.region(d,[top],{expand:true});
  if(!region.ok)return false;
  const inset=se430MeshOps.inset(d,region.triangleIds,{fraction:.18});
  if(!inset.ok)return false;
  const cavity=se430MeshOps.extrude(inset.data,inset.selectedFaces,{depth:-.35});
  if(!cavity.ok)return false;
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(cavity.data.positions,3));
  geometry.setIndex(cavity.data.indices);geometry.computeVertexNormals();
  const material=new THREE.MeshBasicMaterial({color:'#75edce',transparent:true,opacity:.25,
   depthWrite:false,depthTest:true,wireframe:true,side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(geometry,material);
  mesh.position.set(0,1.5,0);mesh.userData.editorOnly=true;mesh.name='Satchel cavity goal · connected topology ghost';
  mesh.raycast=()=>{};group.add(mesh);return true;
 }
 return Object.freeze({inspect,inspectOne,makeGhost});
})();
window.SWYRL_E_SATCHEL_CAVITY_436=se436SatchelCavity;
/* SE436_SATCHEL_CAVITY_END */
