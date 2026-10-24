"""Non-destructive before-Apply sculpt deformation preview on the existing yellow brush."""
import hashlib
import json

GHOST_JS = r"""
// §E v11.108: editor-only, temporary before-Apply mesh deformation ghost.
// Never mutate part data, the source BufferGeometry, material mode or Undo.
let atelierSculptGhost=null,atelierSculptGhostFrame=0,atelierSculptGhostStatus=null;
function atelierSculptGhostClear(){
 if(!atelierSculptGhost)return;
 const group=atelierSculptGhost;atelierSculptGhost=null;
 group.parent?.remove(group);
 group.traverse(o=>{
  o.geometry?.dispose?.();
  const m=Array.isArray(o.material)?o.material:(o.material?[o.material]:[]);
  for(const item of m)item?.dispose?.();
 });
 atelierHDDirty=true;
}
function atelierSculptGhostSchedule(){
 if(atelierSculptGhostFrame)cancelAnimationFrame(atelierSculptGhostFrame);
 atelierSculptGhostFrame=requestAnimationFrame(()=>{
  atelierSculptGhostFrame=0;
  try{atelierSculptGhostDraw();}
  catch(e){atelierSculptGhostClear();const note=document.getElementById('modelAtelierSculptGhostInfo');
   if(note)note.textContent='Preview unavailable for this mesh; Apply behavior unchanged.';
   console.warn('Sculpt preview failed safely',e);}
 });
}
function atelierSculptGhostDraw(){
 atelierSculptGhostClear();
 if(!atelierSculptGhostStatus)atelierSculptGhostStatus=document.getElementById('modelAtelierSculptGhostInfo');
 const statusNode=atelierSculptGhostStatus;
 const toggle=document.getElementById('modelAtelierSculptGhostEnabled');
 if(statusNode)statusNode.textContent='';
 if(!toggle?.checked||!atelierSculptHit||!modelRoot||!world)return;
 const part=partById(atelierSculptHit.partId);
 const mesh=modelRoot.children.find(o=>o.isMesh&&o.userData.atelierId===atelierSculptHit.partId);
 const stroke=atelierSculptForm();
 if(!part||!mesh||!stroke||part.id!==selection)return;
 mesh.updateMatrixWorld(true);
 const source=mesh.geometry,positions=source.attributes.position;
 if(!positions)return;
 const count=positions.count;
 const root=new THREE.Group();
 root.name='Sculpt before-Apply ghost (editor only)';
 root.userData.atelierHelper=true;
 root.userData.sculptPreviewOnly=true;
 const dots=[],rays=[],triangles=[];
 let affected=0,sampled=false;
 const from=new THREE.Vector3(),to=new THREE.Vector3();
 if(count<=48000){
  // Evaluate the SAME production vertex sculpt function on an isolated clone.
  // Source geometry already includes previous strokes: replay ONLY the draft.
  const ghost=source.clone();
  try{
   const trial={...part,sculptBrushes:[stroke],sculptVertexEdits:[],
     sculptLassos:[],refinementLayers:[]};
   const changed=atelierSculptApply(ghost,trial);
   const dst=changed.attributes.position;
   const changedFlags=new Uint8Array(count);
   const stride=Math.max(1,Math.ceil(count/5000));
   for(let i=0;i<count;i++){
    const dx=dst.getX(i)-positions.getX(i),dy=dst.getY(i)-positions.getY(i),dz=dst.getZ(i)-positions.getZ(i);
    if(dx*dx+dy*dy+dz*dz<1e-12)continue;
    changedFlags[i]=1;affected++;
    if(i%stride)continue;
    from.set(positions.getX(i),positions.getY(i),positions.getZ(i));
    to.set(dst.getX(i),dst.getY(i),dst.getZ(i));
    const a=mesh.localToWorld(from.clone()),b=mesh.localToWorld(to.clone());
    dots.push(b.x,b.y,b.z);
    rays.push(a.x,a.y,a.z,b.x,b.y,b.z);
   }
   // Show ghosted new surface topology, not a detached flat circular decal.
   // Draw changed faces only; bound preview work on dense mobile meshes.
   const index=source.index,total=Math.floor((index?index.count:count)/3);
   const step=Math.max(1,Math.ceil(total/16000));
   for(let face=0;face<total;face+=step){
    const ids=[0,1,2].map(k=>index?index.getX(face*3+k):face*3+k);
    if(ids.some(i=>i>=count)||!ids.some(i=>changedFlags[i]))continue;
    for(const i of ids){
     to.set(dst.getX(i),dst.getY(i),dst.getZ(i));
     const q=mesh.localToWorld(to.clone());triangles.push(q.x,q.y,q.z);
    }
   }
   if(changed!==ghost)changed.dispose?.();
  }finally{ghost.dispose();}
 }else{
  // Dense organic models: lightweight sampled push preview. Sampling is
  // labeled explicitly, never advertised as identical to full mesh evaluation.
  sampled=true;
  if(stroke.operation==='push'&&!stroke.mirrorX&&
    ['front','inside','through'].includes(stroke.surfaceMode)){
   const axis=new THREE.Vector3(...stroke.axis).applyEuler(
      new THREE.Euler(stroke.pitch,stroke.yaw,0,'YXZ')).normalize();
   const origin=atelierSurfaceCenter(stroke),normal=source.attributes.normal;
   const stride=Math.ceil(count/4500),delta=new THREE.Vector3();
   for(let i=0;i<count;i+=stride){
    from.fromBufferAttribute(positions,i);delta.subVectors(from,origin);
    const d=delta.length(),n=normal?new THREE.Vector3().fromBufferAttribute(normal,i).dot(
      new THREE.Vector3(...stroke.axis)):1;
    if(d>=stroke.radius||d>stroke.selectionRadius||
      (stroke.surfaceMode==='front'&&n<=-.08)||
      (stroke.surfaceMode==='inside'&&n>=-.12))continue;
    let w=stroke.falloffCurve?atelierSculptCurveWeight(d/stroke.radius,stroke):
       atelierSculptFalloff(d/stroke.radius,stroke.falloff,stroke.plateau,stroke.taper);
    if(stroke.half)w*=THREE.MathUtils.smoothstep(delta.dot(axis),-stroke.radius*.18,0);
    let amount=w*(stroke.level?stroke.strength-delta.dot(axis):stroke.strength);
    if(stroke.snap>0)amount=Math.round(amount/stroke.snap)*stroke.snap;
    if(Math.abs(amount)<1e-6)continue;
    to.copy(from).addScaledVector(axis,amount);
    const a=mesh.localToWorld(from.clone()),b=mesh.localToWorld(to.clone());
    dots.push(b.x,b.y,b.z);rays.push(a.x,a.y,a.z,b.x,b.y,b.z);
    affected++;
   }
  }
 }
 const pointGeometry=new THREE.BufferGeometry();
 pointGeometry.setAttribute('position',new THREE.Float32BufferAttribute(dots,3));
 const points=new THREE.Points(pointGeometry,new THREE.PointsMaterial({
  color:0x55ffdb,size:6,sizeAttenuation:false,depthTest:false,depthWrite:false,
  transparent:true,opacity:.95
 }));
 points.renderOrder=986;root.add(points);
 const rayGeometry=new THREE.BufferGeometry();
 rayGeometry.setAttribute('position',new THREE.Float32BufferAttribute(rays,3));
 const spokes=new THREE.LineSegments(rayGeometry,new THREE.LineBasicMaterial({
  color:0x63ecee,transparent:true,opacity:.52,depthTest:false,depthWrite:false
 }));
 spokes.renderOrder=985;root.add(spokes);
 if(triangles.length){
  const surface=new THREE.BufferGeometry();
  surface.setAttribute('position',new THREE.Float32BufferAttribute(triangles,3));
  const membrane=new THREE.Mesh(surface,new THREE.MeshBasicMaterial({
   color:0x32dae3,transparent:true,opacity:.19,side:THREE.DoubleSide,
   depthTest:false,depthWrite:false
  }));
  membrane.renderOrder=983;root.add(membrane);
  const wire=new THREE.LineSegments(new THREE.WireframeGeometry(surface),
    new THREE.LineBasicMaterial({color:0x6affde,transparent:true,opacity:.62,
      depthTest:false,depthWrite:false}));
  wire.renderOrder=984;root.add(wire);
 }
 world.add(root);atelierSculptGhost=root;atelierHDDirty=true;
 if(statusNode){
  const mode=stroke.operation==='push'?(stroke.strength<0?'inward':'outward'):stroke.operation;
  statusNode.textContent=sampled?
   ('Sampled pre-edit '+mode+' preview: '+affected+' control points shown. '+
     (dots.length?'Large mesh: sampled motion, not exact topology.':'This mode shows radius/depth guides only on large meshes.')):
   ('Pre-edit '+mode+' ghost · radius '+stroke.radius.toFixed(3)+
    ' · center depth '+Math.abs(stroke.strength).toFixed(3)+
    ' · '+affected+' vertices displaced. Apply brush to commit.');
 }
}
function atelierSculptGhostInstall(){
 if(document.getElementById('modelAtelierSculptGhostEnabled'))return;
 const apply=$m('SculptBrushApply'),actions=apply?.closest('.atelier-inspector-actions');
 if(!actions)return;
 const field=document.createElement('div');
 field.className='atelier-ghost-controls';
 field.innerHTML='<label><input type="checkbox" id="modelAtelierSculptGhostEnabled" checked> '+
   'Show mesh preview before Apply</label><small>Amber ring = radius · teal mesh = temporary result; nothing is saved until Apply.</small>'+
   '<output id="modelAtelierSculptGhostInfo" role="status"></output>';
 actions.parentNode.insertBefore(field,actions);
 field.querySelector('input').addEventListener('change',atelierSculptGhostSchedule);
 const extra=['SculptBrushHalf','SculptBrushLevel','SculptBrushMirrorX',
   'SculptBrushSnap','SculptBrushCurveEnabled','SculptBrushCurveValues',
   'SculptBrushSurfaceMode','SculptBrushSelectRadius','SculptBrushSelectRadiusScreen',
   'SculptBrushOffsetU','SculptBrushOffsetV'];
 for(const stem of extra){
  const el=$m(stem);
  if(!el)continue;
  const refresh=()=>{if(atelierSculptHit)atelierSculptPickMarkerRefresh();};
  el.addEventListener('input',refresh);
  el.addEventListener('change',refresh);
 }
 atelierSculptGhostSchedule();
}
"""

CSS = """
/* §E v11.108: compact and legible non-destructive brush controls. */
.model-atelier .atelier-ghost-controls{display:grid;gap:7px;margin:12px 0;padding:11px;
 border:1px solid #547c83;border-radius:9px;background:#152b40}
.model-atelier .atelier-ghost-controls label{display:flex;align-items:center;gap:9px;
 color:#e1f8f6;font-size:14px;line-height:1.4}
.model-atelier .atelier-ghost-controls small{color:#a8d6d8;line-height:1.4}
.model-atelier .atelier-ghost-controls output{color:#f7e8aa;font-size:12.5px;line-height:1.5}
"""

def once(html, before, after):
    count=html.count(before)
    assert count==1,(before[:100],count)
    return html.replace(before,after,1)

def apply(html):
    html=once(html,'let atelierSculptArmed=false,atelierSculptHit=null;',
              GHOST_JS+'\nlet atelierSculptArmed=false,atelierSculptHit=null;')
    html=once(html,
      'function atelierSculptPickMarkerRefresh(){\n atelierSculptPickMarkerClear();',
      'function atelierSculptPickMarkerRefresh(){\n atelierSculptPickMarkerClear();\n atelierSculptGhostSchedule();')
    html=once(html,
      ' atelierSculptPreviewFieldsInstall();\n $m(\'SculptBrushPick\').addEventListener',
      ' atelierSculptPreviewFieldsInstall();\n atelierSculptGhostInstall();\n $m(\'SculptBrushPick\').addEventListener')
    assert '</head>' in html
    html=html.replace('</head>','<style id="se-v11108-sculpt-ghost">'+CSS+'</style>\n</head>',1)
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_107_RADIUS_DEPTH_PREVIEW',
                   'SWYRL_ENGINE_DEPLOY_MARKER: V11_108_SCULPT_GHOST_PREVIEW')
    for old,new in [
      ('ENGINE · MAKER v11.107','ENGINE · MAKER v11.108'),
      ('v11.107 · live radius and depth brush preview','v11.108 · pre-edit mesh ghost brush'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.107'","window.SWRLZ_FORGE_BUILD={version:'v11.108'"),
      ('<title>§wyrl§ Engine · Maker v11.107</title>','<title>§wyrl§ Engine · Maker v11.108</title>'),
    ]: html=once(html,old,new)
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Before-Apply sculpt mesh ghost and classic amber brush footprint',
      date='2026-10-24',changes=[
       'Retain the picked yellow radius ring, cyan axis and live depth guide; add a teal temporary mesh deformation ghost.',
       'Small and medium meshes preview using the exact existing native stroke evaluation on a disposable geometry clone.',
       'Large meshes display bounded sampled push motion with explicit accuracy labeling to protect mobile performance.',
       'Preview toggle and surface/brush control changes redraw without saving vertices, affecting Undo or changing Wireframe/X-Ray mode.'
      ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    raw=html.encode('utf-8')
    print('SWRLZ_V11108_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
