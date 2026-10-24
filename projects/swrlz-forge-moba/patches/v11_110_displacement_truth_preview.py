"""Preview only vertices actually moved by the native brush, not a false teal footprint."""
import hashlib
import json

def once(s,old,new):
    n=s.count(old)
    assert n==1,(old[:140],n)
    return s.replace(old,new,1)

def apply(html):
    # Geometry/source evaluation is owned by v11.108. The present patch only
    # improves visual truth: a zero-motion stroke MUST NOT paint a fake bulge.
    html=once(html,
      'const dots=[],rays=[],triangles=[],triangleSources=[];',
      'const dots=[],rays=[],triangles=[],triangleSources=[],triangleMoves=[];\n let maxMove=0;')
    html=once(html,
      'const changedFlags=new Uint8Array(count);',
      'const changedFlags=new Uint8Array(count),motion=new Float32Array(count);')
    html=once(html,
      '''    if(dx*dx+dy*dy+dz*dz<1e-12)continue;
    changedFlags[i]=1;affected++;''',
      '''    const travel=Math.hypot(dx,dy,dz);
    if(travel<1e-6)continue;
    changedFlags[i]=1;motion[i]=travel;
    maxMove=Math.max(maxMove,travel);affected++;''')
    html=once(html,
      '''     triangleSources.push(positions.getX(i),positions.getY(i),positions.getZ(i));
     to.set(dst.getX(i),dst.getY(i),dst.getZ(i));''',
      '''     triangleSources.push(positions.getX(i),positions.getY(i),positions.getZ(i));
     triangleMoves.push(motion[i]);
     to.set(dst.getX(i),dst.getY(i),dst.getZ(i));''')
    # Create a surface only when exact native replay actually moved vertices.
    html=once(html,
      'if(triangles.length){\n  // Render the exact proposed temporary surface',
      'if(triangles.length&&affected>0){\n  // Render the exact proposed temporary surface')
    html=once(html,
      "surface.setAttribute('brushSource',new THREE.Float32BufferAttribute(triangleSources,3));",
      "surface.setAttribute('brushSource',new THREE.Float32BufferAttribute(triangleSources,3));\n"+
      "  surface.setAttribute('brushMove',new THREE.Float32BufferAttribute(triangleMoves,1));")
    html=once(html,
      '''    brushCenter:{value:atelierSurfaceCenter(stroke)},
    brushRadius:{value:stroke.radius}''',
      '''    brushCenter:{value:atelierSurfaceCenter(stroke)},
    brushRadius:{value:stroke.radius},
    brushMaxMove:{value:maxMove}''')
    html=once(html,
      "vertexShader:'attribute vec3 brushSource; varying vec3 vBrushSource; void main(){vBrushSource=brushSource; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',",
      "vertexShader:'attribute vec3 brushSource; attribute float brushMove; varying vec3 vBrushSource; varying float vBrushMove; void main(){vBrushSource=brushSource; vBrushMove=brushMove; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',")
    html=once(html,
      "fragmentShader:'precision mediump float; varying vec3 vBrushSource; uniform vec3 brushCenter; uniform float brushRadius; void main(){float radial=distance(vBrushSource,brushCenter); if(radial>=brushRadius)discard; float fade=1.0-smoothstep(brushRadius*0.61,brushRadius,radial); if(fade<0.012)discard; gl_FragColor=vec4(0.17,0.95,0.87,0.28*fade);}',",
      "fragmentShader:'precision mediump float; varying vec3 vBrushSource; varying float vBrushMove; uniform vec3 brushCenter; uniform float brushRadius; uniform float brushMaxMove; void main(){float radial=distance(vBrushSource,brushCenter); if(radial>=brushRadius)discard; float fade=1.0-smoothstep(brushRadius*0.61,brushRadius,radial); float motionFade=smoothstep(0.025,0.22,vBrushMove/max(brushMaxMove,0.00001)); if(fade*motionFade<0.012)discard; gl_FragColor=vec4(0.17,0.95,0.87,0.28*fade*motionFade);}',")
    # The linework must ALSO ignore edges whose vertices do not move. Trim
    # individual segments according to interpolated real movement, retaining
    # the existing brush-radius clip as a second independent boundary.
    html=once(html,
      '''   const lo=Math.max(0,low),hi=Math.min(1,high);
   if(hi-lo<=1e-5)return;''',
      '''   let lo=Math.max(0,low),hi=Math.min(1,high);
   const m0=triangleMoves[first/3],m1=triangleMoves[second/3];
   const cutoff=Math.max(1e-6,maxMove*0.08);
   if(m0<=cutoff&&m1<=cutoff)return;
   if(Math.abs(m1-m0)>1e-10){
    const crossing=(cutoff-m0)/(m1-m0);
    if(m0<cutoff)lo=Math.max(lo,crossing);
    else if(m1<cutoff)hi=Math.min(hi,crossing);
   }
   if(hi-lo<=1e-5)return;''')
    html=once(html,
      '''  statusNode.textContent=sampled?
   ('Sampled pre-edit ''',
      '''  statusNode.textContent=!sampled&&affected===0?
   'No vertices move with these settings; only the yellow radius/depth guides are shown. Adjust depth, snap or brush placement.':
   sampled?
   ('Sampled pre-edit ''')
    html=once(html,
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_109_ROUND_SURFACE_BRUSH_PREVIEW',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_110_TRUE_DISPLACEMENT_PREVIEW')
    for old,new in [
      ('ENGINE · MAKER v11.109','ENGINE · MAKER v11.110'),
      ('v11.109 · round surface-following brush','v11.110 · displacement-accurate ghost'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.109'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.110'"),
      ('<title>§wyrl§ Engine · Maker v11.109</title>',
       '<title>§wyrl§ Engine · Maker v11.110</title>')
    ]:html=once(html,old,new)
    key="const SE_RELEASE_NOTES=";at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Deformation-accurate sculpt preview, no false displacement",
      date="2026-10-24",changes=[
       "Fade the existing round teal mesh overlay according to real per-vertex movement from the native pre-Apply brush evaluator.",
       "Clip teal wireframe edges to where source vertices actually move, in addition to the existing radius clip.",
       "Do not render a teal false bulge when depth, selection or snap produces zero vertex displacement; show a clear status instead.",
       "Preserve prior yellow radius/cyan normal/violet depth guides, selectable Shaded/Wireframe/X-Ray, mesh data, saved strokes, Undo, models, assets and phone controls."
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+n:]
    raw=html.encode("utf-8")
    print("SWRLZ_V11110_BUILD_MEASURE",len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
