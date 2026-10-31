"""§E v11.190: measure real submitted FPS and batch only built-in vault decoration.

Preserve group actor IDs, materials/appearance, transforms, collision, authoring,
modeler and saved scene schema. Avoid generalized actor merging (selection risk).
"""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.190 source anchor',old[:165],count))
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_render_instrument_v11_190.js').read_text(encoding='utf8')
    css=(root/'runtime/engine_render_instrument_v11_190.css').read_text(encoding='utf8')
    html=html.replace('</head>','<style id="se190RenderAudit">\n'+css+'\n</style>\n</head>',1)
    # v8.x FPS counter counts requestAnimationFrame callbacks even when the
    # 45/60 FPS render caps skip WebGL submissions. Show actual *submitted*
    # frames and preserve the separate update/RAF counter for diagnostics.
    html=once(html,
      'renderLast:0,autoScale:.82,autoLast:0};',
      'renderLast:0,autoScale:.82,autoLast:0,submittedFrames:0,submittedFps:0,submittedFrameMs:0,submitSampleStart:performance.now(),totalSubmitted:0};')
    html=once(html,
      'const fps=performanceTelemetry.fps,ms=performanceTelemetry.frameMs,scale=',
      'const fps=performanceTelemetry.submittedFps,ms=performanceTelemetry.submittedFrameMs,scale=')
    html=once(html,
      "d.textContent=Math.round(fps)+' FPS · '+ms.toFixed(1)+' ms · '",
      "d.textContent=(fps?Math.round(fps):'--')+' rendered FPS · '+(ms?ms.toFixed(1):'--')+' ms · '")
    html=once(html,
      "fps:Number(performanceTelemetry.fps.toFixed(1)),\n  frameMs:Number(performanceTelemetry.frameMs.toFixed(1)),",
      "fps:Number(performanceTelemetry.submittedFps.toFixed(1)),\n  frameMs:Number(performanceTelemetry.submittedFrameMs.toFixed(1)),\n  updateFps:Number(performanceTelemetry.fps.toFixed(1)),")
    # Shadow texture reallocations are expensive when tapping presets; do not
    # dispose the map unless its actual resolution changed.
    html=once(html,
      'const size=performancePrefs.shadowSize;sun.shadow.mapSize.set(size,size);if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null}',
      '''const size=performancePrefs.shadowSize;
  if(sun.shadow.mapSize.x!==size||sun.shadow.mapSize.y!==size){
    sun.shadow.mapSize.set(size,size);
    if(sun.shadow.map){sun.shadow.map.dispose();sun.shadow.map=null}
  }''')
    html=once(html,
      'renderer.setPixelRatio(performancePixelRatio());\n  renderer.shadowMap.enabled=',
      '''const nextRatio=performancePixelRatio();
  if(Math.abs(renderer.getPixelRatio()-nextRatio)>0.001)renderer.setPixelRatio(nextRatio);
  renderer.shadowMap.enabled=''')
    html=once(html,
      'installPerformanceSettings();se189InstallPerfUI();applyPerformanceSettings();',
      'installPerformanceSettings();se189InstallPerfUI();se190InstallDiagnostics();applyPerformanceSettings();')
    html=once(html,
      'let se181MainLoopBooted=false;\nfunction tick(){',
      js+'\nlet se181MainLoopBooted=false;\nfunction tick(){')
    html=once(html,
      'se189TrackMainFrame(frameNow,se189RenderStart,se189Rendered);',
      'se189TrackMainFrame(frameNow,se189RenderStart,se189Rendered);\n  se190CountSubmittedFrame(performance.now(),se189Rendered);')

    # Native bundled DEN vault pieces are only non-skeletal, built-in
    # decorations. Use one non-indexed canopy/wall geometry rather than N
    # separately submitted meshes, preserving the same triangles/normals.
    old_canopy="""    for(let i=0;i<vaultPoints.length-1;i++){
      const [x1,y1]=vaultPoints[i],[x2,y2]=vaultPoints[i+1];
      for(const [z1,z2] of [[-16,-3],[-3,3],[3,16]]){
        if(z1===-3&&Math.abs(x1)<=7&&Math.abs(x2)<=7)continue;
        const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute([x1,y1,z1,x2,y2,z1,x2,y2,z2,x1,y1,z1,x2,y2,z2,x1,y1,z2],3));geo.computeVertexNormals();
        const q=new THREE.Mesh(geo,canopy);q.receiveShadow=false;g.add(q);
      }
    }"""
    new_canopy="""    const canopyVerts=[];
    for(let i=0;i<vaultPoints.length-1;i++){
      const [x1,y1]=vaultPoints[i],[x2,y2]=vaultPoints[i+1];
      for(const [z1,z2] of [[-16,-3],[-3,3],[3,16]]){
        if(z1===-3&&Math.abs(x1)<=7&&Math.abs(x2)<=7)continue;
        canopyVerts.push(x1,y1,z1,x2,y2,z1,x2,y2,z2,x1,y1,z1,x2,y2,z2,x1,y1,z2);
      }
    }
    const canopyGeometry=new THREE.BufferGeometry();
    canopyGeometry.setAttribute('position',new THREE.Float32BufferAttribute(canopyVerts,3));
    canopyGeometry.computeVertexNormals();
    const canopyMesh=new THREE.Mesh(canopyGeometry,canopy);
    canopyMesh.receiveShadow=false;g.add(canopyMesh);"""
    html=once(html,old_canopy,new_canopy)
    old_wall="""    for(let i=0;i<vaultPoints.length-1;i++){const [x1,y1]=vaultPoints[i],[x2,y2]=vaultPoints[i+1];const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute([x1,0,0,x2,0,0,x2,y2,0,x1,0,0,x2,y2,0,x1,y1,0],3));geo.computeVertexNormals();g.add(new THREE.Mesh(geo,wallMat));}"""
    new_wall="""    const wallVerts=[];
    for(let i=0;i<vaultPoints.length-1;i++){
      const [x1,y1]=vaultPoints[i],[x2,y2]=vaultPoints[i+1];
      wallVerts.push(x1,0,0,x2,0,0,x2,y2,0,x1,0,0,x2,y2,0,x1,y1,0);
    }
    const wallGeometry=new THREE.BufferGeometry();
    wallGeometry.setAttribute('position',new THREE.Float32BufferAttribute(wallVerts,3));
    wallGeometry.computeVertexNormals();g.add(new THREE.Mesh(wallGeometry,wallMat));"""
    html=once(html,old_wall,new_wall)

    # The same 8 vault-rib brass beams and 8 fine-light beams have a shared
    # material/radius per set. Instancing each set retains every beam position,
    # angle, thickness and actor-level group transform at 2 draws rather than 16.
    old_ribs="""    for(let i=0;i<vaultPoints.length-1;i++){
      const a=vaultPoints[i],b=vaultPoints[i+1];beam([a[0],a[1]-.25,0],[b[0],b[1]-.25,0],.25,brass);
      beam([a[0],a[1]-.48,-.18],[b[0],b[1]-.48,-.18],.035,trim);
    }"""
    new_ribs="""    const ribCount=vaultPoints.length-1;
    const ribBrass=new THREE.InstancedMesh(new THREE.CylinderGeometry(.25,.25,1,8),brass,ribCount);
    const ribTrim=new THREE.InstancedMesh(new THREE.CylinderGeometry(.035,.035,1,8),trim,ribCount);
    const ribY=new THREE.Vector3(0,1,0);
    const ribMatrix=(a,b)=>{
      const v=new THREE.Vector3(...a),w=new THREE.Vector3(...b);
      const span=w.clone().sub(v),length=span.length();
      return new THREE.Matrix4().compose(v.add(w).multiplyScalar(.5),
        new THREE.Quaternion().setFromUnitVectors(ribY,span.normalize()),
        new THREE.Vector3(1,length,1));
    };
    for(let i=0;i<ribCount;i++){
      const a=vaultPoints[i],b=vaultPoints[i+1];
      ribBrass.setMatrixAt(i,ribMatrix([a[0],a[1]-.25,0],[b[0],b[1]-.25,0]));
      ribTrim.setMatrixAt(i,ribMatrix([a[0],a[1]-.48,-.18],[b[0],b[1]-.48,-.18]));
    }
    for(const inst of [ribBrass,ribTrim]){
      inst.instanceMatrix.needsUpdate=true;inst.computeBoundingSphere();g.add(inst);
    }"""
    html=once(html,old_ribs,new_ribs)

    old_stars="""    for(let i=0;i<18;i++){const t=i*2.399963,r=.35+2.15*Math.sqrt((i+1)/18);const star=new THREE.Mesh(new THREE.SphereGeometry(i%4===0?.06:.025,6,4),glowMat('#e6d5a9',.5));star.position.set(Math.cos(t)*r,-.09,Math.sin(t)*r*.76);g.add(star);}"""
    new_stars="""    const starMaterial=glowMat('#e6d5a9',.5);
    const starSmall=new THREE.InstancedMesh(new THREE.SphereGeometry(.025,6,4),starMaterial,13);
    const starLarge=new THREE.InstancedMesh(new THREE.SphereGeometry(.06,6,4),starMaterial,5);
    let countSmall=0,countLarge=0;
    const starPosition=new THREE.Matrix4();
    for(let i=0;i<18;i++){
      const t=i*2.399963,r=.35+2.15*Math.sqrt((i+1)/18);
      starPosition.makeTranslation(Math.cos(t)*r,-.09,Math.sin(t)*r*.76);
      if(i%4===0)starLarge.setMatrixAt(countLarge++,starPosition);
      else starSmall.setMatrixAt(countSmall++,starPosition);
    }
    for(const inst of [starSmall,starLarge]){
      inst.instanceMatrix.needsUpdate=true;inst.computeBoundingSphere();g.add(inst);
    }"""
    html=once(html,old_stars,new_stars)

    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_189_MOBILE_RENDER_BOOST','SWYRL_ENGINE_DEPLOY_MARKER: V11_190_RENDER_FPS_VAULT_BATCHING'),
      ('ENGINE · MAKER v11.189','ENGINE · MAKER v11.190'),
      ('v11.189 · mobile graphics optimization','v11.190 · render FPS and safe vault batching'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.189'","window.SWRLZ_FORGE_BUILD={version:'v11.190'"),
      ('<title>§wyrl§ Engine · Maker v11.189</title>','<title>§wyrl§ Engine · Maker v11.190</title>')
    ]:html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,count=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Actual WebGL-rendered FPS, matched preset comparison and batched vault decoration',
      date='2026-10-31',changes=[
        'Correct FPS overlay to count actual renderer.render submissions rather than update loop callbacks; preserve update FPS separately in diagnostics.',
        'Add one-tap Low vs Mobile Boost comparison in the same scene and camera, with a shared temporary 60 FPS cap and automatic restoration of the original graphics settings.',
        'Improve Graphics & Performance draw-call audit with top actor submesh counts, sampled only when requested rather than every frame.',
        'Batch built-in vault canopy and chamber-wall panel triangles into single geometry; instance identical vault rib cylinders and small/large oculus stars, while keeping selectable parent actors and authored geometry identical.',
        'Avoid recreating an unchanged shadow map or renderer pixel ratio while switching presets; do not alter scene data, generalized sculpt meshes or dynamic actors.',
        'Low remains 45 FPS capped and Mobile Boost remains 60 FPS capped in normal use. Owner Android acceptance and real FPS comparisons remain necessary.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[pos+count:]
