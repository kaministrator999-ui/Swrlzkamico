// §wyrl§ v11.4 Model Atelier organic continuous tapered spline mesh.
// This script is embedded inside the existing ModelAtelier closure by the new
// append-only patch; previous v11.3 source and imported project bytes persist.
function atelierOrganicLoft(part){
  const points=part.path.map(p=>new THREE.Vector3(p[0],p[1],p[2]));
  const curve=new THREE.CatmullRomCurve3(points,false,'centripetal');
  const lengthSegments=Math.min(100,Math.max(12,Math.round(part.segments||48)));
  const rings=Math.min(24,Math.max(8,Math.round(part.radialSegments||12)));
  const positions=[],norms=[],uvs=[],colors=[],faces=[];
  const baseColor=new THREE.Color(part.color);
  function interpRadius(t){
    const f=t*(part.radii.length-1),left=Math.min(part.radii.length-2,Math.floor(f));
    const k=f-left,s=k*k*(3-2*k);
    return part.radii[left]*(1-s)+part.radii[left+1]*s;
  }
  for(let i=0;i<=lengthSegments;i++){
    const t=i/lengthSegments,center=curve.getPoint(t),tangent=curve.getTangent(t).normalize();
    let right=new THREE.Vector3(0,0,1).cross(tangent);
    if(right.lengthSq()<.0001)right=new THREE.Vector3(1,0,0).cross(tangent);
    right.normalize();
    const up=new THREE.Vector3().crossVectors(tangent,right).normalize();
    const r=interpRadius(t);
    for(let j=0;j<=rings;j++){
      const a=j/rings*2*Math.PI,radial=right.clone().multiplyScalar(Math.cos(a)).addScaledVector(up,Math.sin(a));
      const v=center.clone().addScaledVector(radial,r);
      positions.push(v.x,v.y,v.z);norms.push(radial.x,radial.y,radial.z);uvs.push(j/rings,t);
      const highlights=.86+.11*Math.sin(a*2.4)+.05*Math.sin(t*29);
      const shade=baseColor.clone().multiplyScalar(Math.min(1.09,Math.max(.7,highlights)));
      colors.push(shade.r,shade.g,shade.b);
    }
  }
  for(let i=0;i<lengthSegments;i++)for(let j=0;j<rings;j++){
    const a=i*(rings+1)+j,b=(i+1)*(rings+1)+j;
    faces.push(a,b,a+1,b,b+1,a+1);
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  g.setAttribute('normal',new THREE.Float32BufferAttribute(norms,3));
  g.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
  g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  g.setIndex(faces);
  g.computeBoundingSphere();
  return g;
}
