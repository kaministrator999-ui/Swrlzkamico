"""Round, surface-conforming ghost preview: feathered shader and radius-clipped lines."""
import hashlib
import json

OLD_TRIANGLE_BLOCK = """    if(ids.some(i=>i>=count)||!ids.some(i=>changedFlags[i]))continue;
    for(const i of ids){
     to.set(dst.getX(i),dst.getY(i),dst.getZ(i));
     const q=mesh.localToWorld(to.clone());triangles.push(q.x,q.y,q.z);
    }"""
NEW_TRIANGLE_BLOCK = """    if(ids.some(i=>i>=count))continue;
    // Include original surface faces beyond moved vertices to support an
    // accurately rounded mask, without changing any actual stroke behavior.
    const near=stroke.radius*1.35,center=atelierSurfaceCenter(stroke);
    const candidate=ids.some(i=>changedFlags[i]||Math.hypot(
     positions.getX(i)-center.x,positions.getY(i)-center.y,
     positions.getZ(i)-center.z)<=near);
    if(!candidate)continue;
    for(const i of ids){
     triangleSources.push(positions.getX(i),positions.getY(i),positions.getZ(i));
     to.set(dst.getX(i),dst.getY(i),dst.getZ(i));
     const q=mesh.localToWorld(to.clone());triangles.push(q.x,q.y,q.z);
    }"""

OLD_SURFACE = """  const surface=new THREE.BufferGeometry();
  surface.setAttribute('position',new THREE.Float32BufferAttribute(triangles,3));
  const membrane=new THREE.Mesh(surface,new THREE.MeshBasicMaterial({
   color:0x32dae3,transparent:true,opacity:.19,side:THREE.DoubleSide,
   depthTest:false,depthWrite:false
  }));
  membrane.renderOrder=983;root.add(membrane);
  const wire=new THREE.LineSegments(new THREE.WireframeGeometry(surface),
    new THREE.LineBasicMaterial({color:0x6affde,transparent:true,opacity:.62,
      depthTest:false,depthWrite:false}));
  wire.renderOrder=984;root.add(wire);"""

NEW_SURFACE = r"""  // Render the exact proposed temporary surface but mask each fragment by
  // the brush's ORIGINAL object-local distance. Triangle edges are not masks.
  const surface=new THREE.BufferGeometry();
  surface.setAttribute('position',new THREE.Float32BufferAttribute(triangles,3));
  surface.setAttribute('brushSource',new THREE.Float32BufferAttribute(triangleSources,3));
  const surfaceMaterial=new THREE.ShaderMaterial({
   uniforms:{
    brushCenter:{value:atelierSurfaceCenter(stroke)},
    brushRadius:{value:stroke.radius}
   },
   vertexShader:'attribute vec3 brushSource; varying vec3 vBrushSource; void main(){vBrushSource=brushSource; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
   fragmentShader:'precision mediump float; varying vec3 vBrushSource; uniform vec3 brushCenter; uniform float brushRadius; void main(){float radial=distance(vBrushSource,brushCenter); if(radial>=brushRadius)discard; float fade=1.0-smoothstep(brushRadius*0.61,brushRadius,radial); if(fade<0.012)discard; gl_FragColor=vec4(0.17,0.95,0.87,0.28*fade);}',
   transparent:true,depthTest:false,depthWrite:false,side:THREE.DoubleSide
  });
  const membrane=new THREE.Mesh(surface,surfaceMaterial);
  membrane.renderOrder=983;root.add(membrane);
  // Clip every old wireframe edge against the radius in original local space,
  // then interpolate the NEW world-space positions at the clipped endpoints.
  const clipped=[];
  const center=atelierSurfaceCenter(stroke),r=stroke.radius*0.86;
  function addRadiusClippedEdge(first,second){
   const a=new THREE.Vector3(
    triangleSources[first],triangleSources[first+1],triangleSources[first+2]);
   const b=new THREE.Vector3(
    triangleSources[second],triangleSources[second+1],triangleSources[second+2]);
   const direction=b.clone().sub(a),offset=a.clone().sub(center);
   const A=direction.lengthSq();
   if(A<1e-14)return;
   const B=2*offset.dot(direction),C=offset.lengthSq()-r*r;
   const disc=B*B-4*A*C;
   if(disc<=0)return;
   const root=Math.sqrt(disc),low=(-B-root)/(2*A),high=(-B+root)/(2*A);
   const lo=Math.max(0,low),hi=Math.min(1,high);
   if(hi-lo<=1e-5)return;
   const from=new THREE.Vector3(triangles[first],triangles[first+1],triangles[first+2]);
   const to=new THREE.Vector3(triangles[second],triangles[second+1],triangles[second+2]);
   const u=from.clone().lerp(to,lo),v=from.lerp(to,hi);
   clipped.push(u.x,u.y,u.z,v.x,v.y,v.z);
  }
  for(let offset=0;offset<triangles.length;offset+=9){
   addRadiusClippedEdge(offset,offset+3);
   addRadiusClippedEdge(offset+3,offset+6);
   addRadiusClippedEdge(offset+6,offset);
  }
  if(clipped.length){
   const geometry=new THREE.BufferGeometry();
   geometry.setAttribute('position',new THREE.Float32BufferAttribute(clipped,3));
   const wire=new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({
    color:0x67ffe1,transparent:true,opacity:.35,
    depthTest:false,depthWrite:false
   }));
   wire.renderOrder=984;root.add(wire);
  }"""

def once(s,old,new):
    n=s.count(old)
    assert n==1,(old[:120],n)
    return s.replace(old,new,1)

def apply(html):
    html=once(html,"const dots=[],rays=[],triangles=[];",
              "const dots=[],rays=[],triangles=[],triangleSources=[];")
    html=once(html,OLD_TRIANGLE_BLOCK,NEW_TRIANGLE_BLOCK)
    html=once(html,OLD_SURFACE,NEW_SURFACE)
    html=once(html,
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_108_SCULPT_GHOST_PREVIEW",
      "SWYRL_ENGINE_DEPLOY_MARKER: V11_109_ROUND_SURFACE_BRUSH_PREVIEW")
    for old,new in [
      ("ENGINE · MAKER v11.108","ENGINE · MAKER v11.109"),
      ("v11.108 · pre-edit mesh ghost brush","v11.109 · round surface-following brush"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.108'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.109'"),
      ("<title>§wyrl§ Engine · Maker v11.108</title>",
       "<title>§wyrl§ Engine · Maker v11.109</title>"),
    ]: html=once(html,old,new)
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Round, feathered, surface-following sculpt ghost",
      date="2026-10-24",changes=[
       "Retain the yellow radius ring, center-depth guide and native non-destructive brush preview.",
       "Render smooth brush-radius alpha falloff over actual temporary deformed mesh faces instead of square/triangle face boundaries.",
       "Clip teal wireframe edges to the selected local brush radius so overlays do not extend outside the brush.",
       "Preserve true stroke geometry, Undo, native JSON/GLB, all viewport modes, phone menus and previous project assets."
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+n:]
    raw=html.encode("utf-8")
    print("SWRLZ_V11109_BUILD_MEASURE",len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
