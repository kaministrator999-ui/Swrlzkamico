// Sculpted swept locks: closed elliptical sections, broad satin planes and fine longitudinal ridges.
// All dimensions remain native editable spline data; no imported character asset.
function atelierSilkenLock(part){
 const curve=new THREE.CatmullRomCurve3(part.path.map(q=>new THREE.Vector3(...q)),false,'centripetal'),positions=[],colors=[],index=[];
 const n=32,rings=12,base=new THREE.Color(part.color);
 for(let i=0;i<=n;i++){
  const t=i/n,q=curve.getPoint(t),tangent=curve.getTangent(t).normalize();
  let across=new THREE.Vector3(0,0,1).cross(tangent).normalize();if(across.lengthSq()<.01)across.set(1,0,0);
  const depth=new THREE.Vector3().crossVectors(tangent,across).normalize(),f=t*(part.radii.length-1),j=Math.min(part.radii.length-2,Math.floor(f)),u=f-j,w=THREE.MathUtils.lerp(part.radii[j],part.radii[j+1],u*u*(3-2*u));
  for(let k=0;k<=rings;k++){
   const a=k/rings*Math.PI*2,v=q.clone().addScaledVector(across,Math.cos(a)*w).addScaledVector(depth,Math.sin(a)*w*.40*(1+.12*Math.cos(a*6)));
   positions.push(v.x,v.y,v.z);const c=base.clone().multiplyScalar(.89+.15*Math.sin(a)+.035*Math.cos(a*6));colors.push(c.r,c.g,c.b);
  }
  if(i<n)for(let k=0;k<rings;k++){const a=i*(rings+1)+k,b=a+rings+1;index.push(a,a+1,b,b,a+1,b+1);}
 }
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));g.setIndex(index);g.computeVertexNormals();g.computeBoundingSphere();return g;
}
// Curved cloth transverse sections give the pointed overskirt an actual side silhouette.
function atelierTailoredPanel(part){
 const curve=new THREE.CatmullRomCurve3(part.path.map(q=>new THREE.Vector3(...q)),false,'centripetal'),v=[],idx=[],colors=[],base=new THREE.Color(part.color),rows=32,cols=8;
 for(let i=0;i<=rows;i++){
  const t=i/rows,q=curve.getPoint(t),f=t*(part.radii.length-1),j=Math.min(part.radii.length-2,Math.floor(f)),w=THREE.MathUtils.lerp(part.radii[j],part.radii[j+1],f-j),sgn=q.z<0?-1:1;
  for(let k=0;k<=cols;k++){
   const u=k/cols*2-1,fold=Math.cos(u*Math.PI*3)*.012*Math.sin(t*Math.PI);
   if(part.panelAxis==='depth')v.push(q.x+Math.sign(q.x)*(fold-.055*u*u),q.y,q.z+u*w);
   else v.push(q.x+u*w,q.y,q.z+sgn*(fold-.085*u*u));
   const c=base.clone().multiplyScalar(.95+.05*Math.cos(u*Math.PI*3));colors.push(c.r,c.g,c.b);
   if(i<rows&&k<cols){const a=i*(cols+1)+k,b=a+cols+1;idx.push(a,b,a+1,a+1,b,b+1);}
  }
 }
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));g.setIndex(idx);g.computeVertexNormals();g.computeBoundingSphere();return g;
}
