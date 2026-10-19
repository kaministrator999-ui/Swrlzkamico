// §E v11.27 opt-in, native-scene-backed surface brush operators.
// Older saved push/intrude strokes are evaluated by their untouched legacy path.
// All new operators evaluate the same source positions before writing results;
// UV seams remain closed through position-welded smoothing neighborhoods.
function atelierSculptNeighborAverages(geometry){
 const a=geometry.attributes.position,index=geometry.index,count=a.count;
 const idByPosition=new Map(),ids=new Int32Array(count),coords=[];
 for(let i=0;i<count;i++){
   const p=[a.getX(i),a.getY(i),a.getZ(i)];
   const key=p.map(v=>Math.round(v*1e5)).join(',');
   let id=idByPosition.get(key);
   if(id===undefined){id=coords.length;coords.push(p);idByPosition.set(key,id);}
   ids[i]=id;
 }
 const sums=new Float64Array(coords.length*3),degree=new Uint32Array(coords.length);
 const add=(i,j)=>{
   if(i===j)return;
   const p=coords[j],k=i*3;
   sums[k]+=p[0];sums[k+1]+=p[1];sums[k+2]+=p[2];degree[i]++;
 };
 const triangles=Math.floor((index?index.count:count)/3);
 for(let t=0;t<triangles;t++){
   const id=k=>ids[index?index.getX(3*t+k):3*t+k];
   const u=id(0),v=id(1),w=id(2);
   add(u,v);add(v,u);add(v,w);add(w,v);add(w,u);add(u,w);
 }
 return {ids,sums,degree};
}
function atelierSculptApplyOperator(geometry,s){
 const a=geometry.attributes.position,normal=geometry.attributes.normal,count=a.count;
 const operation=s.operation||'push',originalCenter=atelierSurfaceCenter(s);
 const normalAxis=new THREE.Vector3(...s.axis)
   .applyEuler(new THREE.Euler(s.pitch,s.yaw,0,'YXZ')).normalize();
 const primary=atelierSurfaceWeights(geometry,s);
 const mirrored=!!s.mirrorX;
 const reflectedStroke=mirrored?{...s,center:[-originalCenter.x,originalCenter.y,originalCenter.z],
   axis:[-s.axis[0],s.axis[1],s.axis[2]],cameraLocal:s.cameraLocal?[-s.cameraLocal[0],s.cameraLocal[1],s.cameraLocal[2]]:undefined,offsetU:0,offsetV:0}:null;
 const secondary=reflectedStroke?atelierSurfaceWeights(geometry,reflectedStroke):null;
 const secondaryCenter=new THREE.Vector3(-originalCenter.x,originalCenter.y,originalCenter.z);
 const secondaryAxis=normalAxis.clone();secondaryAxis.x*=-1;
 const neighbor=operation==='smooth'?atelierSculptNeighborAverages(geometry):null;
 const pos=new THREE.Vector3(),delta=new THREE.Vector3(),move=new THREE.Vector3();
 // Return the before-edit weight and vector. Never apply two mirrored passes to
 // overlapping brush areas, which would double-strength centerline vertices.
 const evaluate=(i,center,selection,axis)=>{
   pos.set(a.getX(i),a.getY(i),a.getZ(i));
   delta.subVectors(pos,center);
   const dist=(s.surfaceMode==='connected'||s.surfaceMode==='visible-geodesic')?selection.dist[i]:delta.length();
   if(!Number.isFinite(dist)||dist>=s.radius||selection.dist[i]>selection.radius)return null;
   let weight=typeof atelierSculptCurveWeight==='function'?
    atelierSculptCurveWeight(dist/s.radius,s):
    atelierSculptFalloff(dist/s.radius,s.falloff,s.plateau,s.taper);
   if(s.half)weight*=THREE.MathUtils.smoothstep(delta.dot(axis),-s.radius*.18,0);
   if(weight<=0)return null;
   move.set(0,0,0);
   if(operation==='smooth'){
     const key=neighbor.ids[i],n=neighbor.degree[key],k=key*3;
     if(!n)return null;
     move.set(neighbor.sums[k]/n-pos.x,neighbor.sums[k+1]/n-pos.y,
       neighbor.sums[k+2]/n-pos.z);
     move.multiplyScalar(Math.min(1,Math.abs(s.strength)*2)*weight);
   }else if(operation==='pinch'){
     move.copy(delta).addScaledVector(axis,-delta.dot(axis)).multiplyScalar(-1);
     const length=move.length();
     if(length<1e-8)return null;
     move.multiplyScalar(Math.min(length,Math.abs(s.strength))/length*
       weight*Math.sign(s.strength||1));
   }else if(operation==='inflate'){
     if(normal)move.set(normal.getX(i),normal.getY(i),normal.getZ(i)).normalize();
     else move.copy(axis);
     move.multiplyScalar(s.strength*weight);
   }else{
     const signed=delta.dot(axis);
     const amount=operation==='flatten'||(operation==='push'&&s.level)?
       s.strength-signed:s.strength;
     move.copy(axis).multiplyScalar(amount*weight);
   }
   for(let k=0;k<3;k++){
     let amount=move.getComponent(k);
     if(s.snap>0)amount=Math.round(amount/s.snap)*s.snap;
     move.setComponent(k,atelierSculptClamp(amount,-.5,.5));
   }
   return {weight,delta:move.toArray()};
 };
 for(let i=0;i<count;i++){
   const first=evaluate(i,originalCenter,primary,normalAxis);
   const second=secondary?evaluate(i,secondaryCenter,secondary,secondaryAxis):null;
   let chosen=first;
   if(second&&(!first||second.weight>first.weight+1e-8||
       (Math.abs(second.weight-first.weight)<1e-8&&a.getX(i)<0)))chosen=second;
   if(!chosen)continue;
   const [dx,dy,dz]=chosen.delta,x=a.getX(i);
   a.setXYZ(i,mirrored&&Math.abs(x)<1e-6?x:x+dx,
     a.getY(i)+dy,a.getZ(i)+dz);
 }
 a.needsUpdate=true;
}
