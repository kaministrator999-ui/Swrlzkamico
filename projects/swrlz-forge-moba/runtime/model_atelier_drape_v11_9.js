// v11.9 native editable layered-cloth contour; no baked triangles in project saves.
// Each independent panel is authored by center spline knots + matching half-widths.
function atelierFabricPanel(part){
  const curve=new THREE.CatmullRomCurve3(part.path.map(p=>new THREE.Vector3(...p)),false,'centripetal');
  const count=36, vertices=[],tints=[],uvs=[],index=[];
  const base=new THREE.Color(part.color);
  const radius=t=>{const f=t*(part.radii.length-1),i=Math.min(part.radii.length-2,Math.floor(f)),s=f-i;
    return part.radii[i]*(1-s)+part.radii[i+1]*s;};
  for(let i=0;i<=count;i++){
    const t=i/count,p=curve.getPoint(t),w=radius(t);
    // Directional folds, curved front/back relief and flared cloth edges.
    for(let side=-1;side<=1;side+=2){
      vertices.push(p.x+side*w,p.y,p.z+Math.sin(t*Math.PI)*.025+side*.025*Math.sin(t*11));
      uvs.push(side<0?0:1,t);
      const shade=base.clone().multiplyScalar(side<0?.84:1.04);
      tints.push(shade.r,shade.g,shade.b);
    }
    if(i<count){const k=i*2;index.push(k,k+2,k+1,k+1,k+2,k+3);}
  }
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
  geo.setAttribute('color',new THREE.Float32BufferAttribute(tints,3));
  geo.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
  geo.setIndex(index);geo.computeVertexNormals();geo.computeBoundingSphere();return geo;
}
