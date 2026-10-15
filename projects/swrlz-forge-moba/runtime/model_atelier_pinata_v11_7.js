// v11.7 original paper construction: flat-faceted, individually stepped
// truncated-pyramid slice rings, NOT a continuous smooth loft ribbon.
// The editable loft path and radius profile remain owner-adjustable.
function atelierPinataStack(part){
  const points=part.path.map(p=>new THREE.Vector3(p[0],p[1],p[2]));
  const curve=new THREE.CatmullRomCurve3(points,false,'centripetal');
  const layers=Math.min(56,Math.max(16,Math.round(part.layers||36)));
  const facets=Math.min(12,Math.max(6,Math.round(part.facets||8)));
  const color=new THREE.Color(part.color);
  const positions=[],vertexColors=[];
  function push(a,b,c,tint){
    const pigment=new THREE.Color(tint);
    for(const v of [a,b,c]){positions.push(v.x,v.y,v.z);vertexColors.push(pigment.r,pigment.g,pigment.b);}
  }
  function quad(a,b,c,d,tint){push(a,b,c,tint);push(a,c,d,tint);}
  function ring(t,radius,offsetAngle=0){
    const center=curve.getPoint(t),tangent=curve.getTangent(t).normalize();
    let across=new THREE.Vector3(0,0,1).cross(tangent).normalize();
    if(across.lengthSq()<.01)across=new THREE.Vector3(1,0,0).cross(tangent).normalize();
    const depth=new THREE.Vector3().crossVectors(tangent,across).normalize();
    const vertices=[];
    for(let j=0;j<facets;j++){
      const angle=2*Math.PI*j/facets+Math.PI/facets+offsetAngle;
      const radial=across.clone().multiplyScalar(Math.cos(angle))
         .addScaledVector(depth,Math.sin(angle));
      // Alternating faceted planar corners produce the cut-paper outline.
      const serration=1+(j%2===0?.035:-.028);
      vertices.push(center.clone().addScaledVector(radial,radius*serration));
    }
    return {vertices,center};
  }
  function radiusAt(t){
    const i=t*(part.radii.length-1),low=Math.min(part.radii.length-2,Math.floor(i));
    const k=i-low;
    return part.radii[low]*(1-k)+part.radii[low+1]*k;
  }
  const band=part.group==='Azure frost'
    ?['#24bfcf','#86f1e9','#138ca8','#55dce3','#0b698c']
    :['#f06d54','#ffbf76','#c54a4e','#f99165','#93383e'];
  for(let i=0;i<layers;i++){
    // Visible recess between individually capped paper discs.
    const start=(i+.045)/layers,end=(i+.93)/layers;
    const tmid=(start+end)/2;
    const r0=radiusAt(start)*(.96+.035*Math.sin(i*1.79));
    const r1=radiusAt(end)*(1.01+.025*Math.cos(i*1.27));
    const lo=ring(start,r0),hi=ring(end,r1);
    const base=new THREE.Color(band[i%band.length]);
    for(let j=0;j<facets;j++){
      const k=(j+1)%facets;
      const tint=base.clone().multiplyScalar(.77+((j+2*i)%5)*.072);
      quad(lo.vertices[j],lo.vertices[k],hi.vertices[k],hi.vertices[j],tint);
      // Layered pyramid-disc caps explicitly visible at both ends.
      push(lo.center,lo.vertices[k],lo.vertices[j],base.clone().multiplyScalar(.64));
      push(hi.center,hi.vertices[j],hi.vertices[k],base.clone().multiplyScalar(1.16));
      // Torn paper tabs sit against the front, rear and outer edges.
      if(j%2===0){
        const a=lo.vertices[j],b=lo.vertices[k],middle=a.clone().lerp(b,.5);
        const tip=middle.clone().sub(lo.center).multiplyScalar(1.12)
          .add(lo.center).addScaledVector(curve.getTangent(tmid),-.07);
        push(a,b,tip,base.clone().multiplyScalar(1.05));
      }
    }
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
  g.setAttribute('color',new THREE.Float32BufferAttribute(vertexColors,3));
  g.computeVertexNormals();g.computeBoundingSphere();
  return g;
}
