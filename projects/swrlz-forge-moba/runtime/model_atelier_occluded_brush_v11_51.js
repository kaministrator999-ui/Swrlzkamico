// §E v11.51: exact first-surface camera-ray brush visibility.
// Read-only selection against the original indexed/nonindexed geometry.
// A bounded triangle BVH avoids per-candidate full-mesh scans on mobile.
// The saved eye is part-local; replay never depends on a later camera pose.
const atelierOcclusionMaxTriangles=150000;
const atelierOcclusionMaxVertices=250000;
function atelierBrushOcclusionMask(geometry,eye,eligible,radius){
 const positions=geometry?.attributes?.position,indices=geometry?.index;
 const count=positions?.count||0,faces=Math.floor((indices?indices.count:count)/3);
 if(!Array.isArray(eye)||eye.length!==3||eye.some(v=>!Number.isFinite(v))
    ||faces>atelierOcclusionMaxTriangles||count>atelierOcclusionMaxVertices
    ||!count)return null;
 const ix=(f,c)=>indices?indices.getX(3*f+c):3*f+c;
 const px=i=>positions.getX(i),py=i=>positions.getY(i),pz=i=>positions.getZ(i);
 const triangles=[];
 for(let f=0;f<faces;f++){
  const i=ix(f,0),j=ix(f,1),k=ix(f,2);
  if(i>=count||j>=count||k>=count||Math.min(i,j,k)<0)return null;
  const ax=px(i),ay=py(i),az=pz(i),bx=px(j),by=py(j),bz=pz(j),
    cx=px(k),cy=py(k),cz=pz(k);
  if(![ax,ay,az,bx,by,bz,cx,cy,cz].every(Number.isFinite))return null;
  triangles.push({i,j,k,b:[
   Math.min(ax,bx,cx),Math.min(ay,by,cy),Math.min(az,bz,cz),
   Math.max(ax,bx,cx),Math.max(ay,by,cy),Math.max(az,bz,cz)],
   center:[(ax+bx+cx)/3,(ay+by+cy)/3,(az+bz+cz)/3]});
 }
 // AABB bounds/median subdivision; leaves contain at most 12 triangles.
 function build(list){
  const bounds=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity];
  for(const t of list)for(let a=0;a<3;a++){
   bounds[a]=Math.min(bounds[a],t.b[a]);bounds[a+3]=Math.max(bounds[a+3],t.b[a+3]);
  }
  if(list.length<=12)return {bounds,leaf:list};
  const spans=[0,1,2].map(a=>bounds[a+3]-bounds[a]);
  const axis=spans.indexOf(Math.max(...spans));
  list.sort((a,b)=>a.center[axis]-b.center[axis]);
  const mid=list.length>>1;
  return {bounds,left:build(list.slice(0,mid)),right:build(list.slice(mid))};
 }
 if(!triangles.length)return eligible.map(v=>!!v);
 const tree=build(triangles);
 function intersectsBox(b,origin,direction,maxT){
  let minT=0,max=maxT;
  for(let a=0;a<3;a++){
   const d=direction[a],o=origin[a];
   if(Math.abs(d)<1e-12){if(o<b[a]||o>b[a+3])return false;continue;}
   let t1=(b[a]-o)/d,t2=(b[a+3]-o)/d;
   if(t1>t2){const t=t1;t1=t2;t2=t;}
   minT=Math.max(minT,t1);max=Math.min(max,t2);
   if(minT>max)return false;
  }
  return true;
 }
 function hitsTriangle(t,origin,dir,maxDist){
  const [ax,ay,az]=[px(t.i),py(t.i),pz(t.i)];
  const e1=[px(t.j)-ax,py(t.j)-ay,pz(t.j)-az];
  const e2=[px(t.k)-ax,py(t.k)-ay,pz(t.k)-az];
  const pv=[dir[1]*e2[2]-dir[2]*e2[1],
    dir[2]*e2[0]-dir[0]*e2[2],dir[0]*e2[1]-dir[1]*e2[0]];
  const det=e1[0]*pv[0]+e1[1]*pv[1]+e1[2]*pv[2];
  if(Math.abs(det)<1e-12)return false;
  const inv=1/det,q=[origin[0]-ax,origin[1]-ay,origin[2]-az];
  const u=(q[0]*pv[0]+q[1]*pv[1]+q[2]*pv[2])*inv;
  if(u< -1e-8||u>1+1e-8)return false;
  const cross=[q[1]*e1[2]-q[2]*e1[1],
    q[2]*e1[0]-q[0]*e1[2],q[0]*e1[1]-q[1]*e1[0]];
  const v=(dir[0]*cross[0]+dir[1]*cross[1]+dir[2]*cross[2])*inv;
  if(v< -1e-8||u+v>1+1e-8)return false;
  const distance=(e2[0]*cross[0]+e2[1]*cross[1]+e2[2]*cross[2])*inv;
  return distance>1e-6&&distance<maxDist;
 }
 function occludes(node,origin,dir,maxDist){
  if(!intersectsBox(node.bounds,origin,dir,maxDist))return false;
  if(node.leaf)return node.leaf.some(t=>hitsTriangle(t,origin,dir,maxDist));
  return occludes(node.left,origin,dir,maxDist)||
    occludes(node.right,origin,dir,maxDist);
 }
 const visible=new Uint8Array(count);
 const tolerance=Math.max(.0003,Math.min(.004,radius*.008));
 for(let i=0;i<count;i++){
  if(!eligible[i])continue;
  const d=[px(i)-eye[0],py(i)-eye[1],pz(i)-eye[2]];
  const len=Math.hypot(...d);
  if(len<tolerance){visible[i]=1;continue;}
  const dir=d.map(v=>v/len);
  visible[i]=occludes(tree,eye,dir,len-tolerance)?0:1;
 }
 return visible;
}
