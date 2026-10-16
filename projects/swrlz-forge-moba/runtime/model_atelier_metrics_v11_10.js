// V11_10_MEASURED_GEOMETRY_PROFILER — measured generated geometry, never guessed budgets.
// Installed inside the existing ModelAtelier closure by the governed append-only patch.
function atelierGeometryStats(){
  const totals={meshObjects:0,triangles:0,vertices:0,geometryBytes:0,estimatedMeshDraws:0};
  const groups=Object.create(null);
  for(const mesh of modelRoot?.children||[]){
    if(!mesh.isMesh)continue;
    const part=partById(mesh.userData?.atelierId);
    if(!part)continue; // Exclude floor, grid and selection helpers.
    const geo=mesh.geometry,pos=geo?.getAttribute('position'),index=geo?.getIndex();
    if(!pos)continue;
    const count=index?index.count:pos.count;
    const record=groups[part.group||'Ungrouped']||(groups[part.group||'Ungrouped']={meshObjects:0,triangles:0,vertices:0,geometryBytes:0});
    const triangles=Math.floor(count/3);
    let bytes=index?.array?.byteLength||0;
    for(const key in geo.attributes)bytes+=geo.attributes[key]?.array?.byteLength||0;
    record.meshObjects++;record.triangles+=triangles;record.vertices+=pos.count;record.geometryBytes+=bytes;
    totals.meshObjects++;totals.triangles+=triangles;totals.vertices+=pos.count;totals.geometryBytes+=bytes;
    totals.estimatedMeshDraws++;
  }
  return {schema:'swyrl-model-metrics-v1',basis:'generated Three.js BufferGeometry; CPU buffers only',
    ...totals,groups:Object.fromEntries(Object.entries(groups).sort((a,b)=>b[1].triangles-a[1].triangles))};
}
function refreshModelMetrics(){
  const target=$m('MetricsBody');if(!target)return;
  const data=atelierGeometryStats();
  const fmt=n=>Number(n||0).toLocaleString('en-US');
  target.replaceChildren();
  function line(label,value){
    const node=document.createElement('div');node.className='atelier-metric-row';
    const name=document.createElement('span');name.textContent=label;
    const number=document.createElement('strong');number.textContent=value;
    node.append(name,number);target.append(node);
  }
  line('Editable rendered mesh objects',fmt(data.meshObjects));
  line('Triangles · exact generated topology',fmt(data.triangles));
  line('Buffer position vertices',fmt(data.vertices));
  line('Geometry buffers · CPU only',fmt(Math.round(data.geometryBytes/1024))+' KiB');
  line('Mesh draws · estimate, not GPU calls',fmt(data.estimatedMeshDraws));
  const title=document.createElement('strong');title.textContent='By model group';target.append(title);
  for(const [name,record] of Object.entries(data.groups)){
    line(name,fmt(record.meshObjects)+' meshes · '+fmt(record.triangles)+' tris');
  }
  const note=document.createElement('p');note.className='atelier-metric-note';
  note.textContent='These are real generated buffer counts, not topology quality, unique welded vertices, textures, GPU memory, FPS, or actual renderer draw calls.';
  target.append(note);
}
