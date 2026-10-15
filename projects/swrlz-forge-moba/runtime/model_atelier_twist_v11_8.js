// §E v11.8: three-dimensional, twistable, editable broken-S paper-piñata loft.
// Radii and points remain standard native Model Atelier JSON. No external assets.
function atelierPinataTwist(part){
  const pts=part.path.map(p=>new THREE.Vector3(...p));
  const curve=new THREE.CatmullRomCurve3(pts,false,'centripetal');
  const steps=Math.min(64,Math.max(20,Math.round(part.layers||36)));
  const facets=Math.min(12,Math.max(6,Math.round(part.facets||8)));
  const twist=(Number(part.twistDegrees)||0)*Math.PI/180;
  const depthScale=Math.max(.5,Math.min(2,Number(part.depthScale)||1));
  const colors=part.group==='Azure frost'
     ?['#27bfd3','#79e9e5','#1192b5','#b5f4e4','#217f9c']
     :['#f46f55','#ffd092','#df544d','#f6a074','#a83844'];
  const v=[],tints=[],uvs=[];
  function tri(a,b,c,color,u=0,w=0){
    const q=new THREE.Color(color);
    for(const p of [a,b,c]){v.push(p.x,p.y,p.z);tints.push(q.r,q.g,q.b);uvs.push(u,w);}
  }
  function quad(a,b,c,d,c1,u){tri(a,b,c,c1,u,0);tri(a,c,d,c1,u,1);}
  function radius(t){
    const f=t*(part.radii.length-1),j=Math.min(part.radii.length-2,Math.floor(f)),w=f-j;
    return part.radii[j]*(1-w)+part.radii[j+1]*w;
  }
  function crossSection(t,r,shift){
    const center=curve.getPoint(t),tan=curve.getTangent(t).normalize();
    let side=new THREE.Vector3(0,0,1).cross(tan);
    if(side.lengthSq()<.00001)side=new THREE.Vector3(1,0,0).cross(tan);
    side.normalize();
    const depth=new THREE.Vector3().crossVectors(tan,side).normalize();
    const angle=twist*t+shift;
    const vertices=[];
    for(let j=0;j<facets;j++){
      const a=j*2*Math.PI/facets+angle;
      const planar=side.clone().multiplyScalar(Math.cos(a))
        .addScaledVector(depth,Math.sin(a)*depthScale);
      vertices.push(center.clone().addScaledVector(planar,r*(j%2?.976:1.04)));
    }
    return {center,vertices,tan};
  }
  for(let i=0;i<steps;i++){
    const t0=(i+.018)/steps,t1=(i+.965)/steps;
    // Overlapping but separate capped frustums show the paper's physical construction.
    const taper0=.93+.05*Math.sin(i*1.7),taper1=1+.04*Math.cos(i*1.12);
    const lo=crossSection(t0,radius(t0)*taper0,0);
    const hi=crossSection(t1,radius(t1)*taper1,.03*Math.sin(i*.8));
    const base=new THREE.Color(colors[i%colors.length]);
    for(let k=0;k<facets;k++){
      const n=(k+1)%facets;
      const shade=base.clone().multiplyScalar(.82+.045*((k+i)%5));
      quad(lo.vertices[k],lo.vertices[n],hi.vertices[n],hi.vertices[k],shade,i/steps);
      tri(lo.center,lo.vertices[n],lo.vertices[k],base.clone().multiplyScalar(.67),i/steps);
      tri(hi.center,hi.vertices[k],hi.vertices[n],base.clone().multiplyScalar(1.16),i/steps);
      if(k%2===0){
        const outer=hi.vertices[k].clone().lerp(hi.vertices[n],.46);
        const slip=outer.clone().sub(hi.center).multiplyScalar(1.18).add(hi.center)
           .addScaledVector(hi.tan,-.055);
        tri(hi.vertices[k],hi.vertices[n],slip,base.clone().multiplyScalar(1.04),i/steps);
      }
    }
  }
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));
  g.setAttribute('color',new THREE.Float32BufferAttribute(tints,3));
  g.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));
  g.computeVertexNormals();g.computeBoundingSphere();
  return g;
}