"""§E v11.466 candidate: bounded ring/arc selection, transforms, refinement, extrusion."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_466_RING_ARC_MODELING'
def one(src,old,new):
    count=src.count(old)
    assert count==1, ('v11.466 unique source anchor',old[:140],count)
    return src.replace(old,new,1)
def runtime(name):
    return (ROOT/'runtime'/name).read_text('utf8')
def apply(html):
    html=one(html,'/* SE430_MODEL_MESH_OPERATIONS_END */',
        '/* SE430_MODEL_MESH_OPERATIONS_END */\n'+runtime('model_ring_kernel_v11_466.js'))
    # Extend the original native mesh candidate, not a second editor.
    html=one(html,
        "const depth=options.depth??.15;if(typeof depth!=='number'||!Number.isFinite(depth)||Math.abs(depth)<.005||Math.abs(depth)>4)return fail('Extrusion depth must be a signed value from 0.005 to 4 local units.');",
        "const depth=options.depth??.15;if(typeof depth!=='number'||!Number.isFinite(depth)||Math.abs(depth)<.005||Math.abs(depth)>30)return fail('Extrusion depth must be a signed value from 0.005 to 30 local units.');")
    html=one(html,
        "const r=region(data,triangleIds);if(!r.ok)return r;if(!r.convex)return fail('Extrude currently needs one convex planar region.');",
        """const r=region(data,triangleIds);if(!r.ok)return r;if(!r.convex)return fail('Extrude currently needs one convex planar region.');
  const scale=options.scale??1,leftScale=options.leftScale??1,rightScale=options.rightScale??1,offset=options.offset??[0,0,0],tilt=options.tilt??[0,0,0];
  const capOptions={scale,leftScale,rightScale,offset,tilt};
  if(!se466RingKernel.capPoint(r.centroid,r.centroid,capOptions))return fail('Invalid extrusion scale, axis offset or rotation.');
  if(depth<0&&(scale!==1||leftScale!==1||rightScale!==1||offset.some(n=>n!==0)||tilt.some(n=>n!==0)))
   return fail('Nonuniform inward face extrusion needs a fuller collision solver. Use regular inward Extrude or move the face outward first.');""")
    html=one(html,
        "for(const id of used){mapping.set(id,next.positions.length/3);next.positions.push(...add(point(data,id),mul(r.normal,depth)));next.uvs.push(...add(uv(data,id),shift));}",
        """for(const id of used){mapping.set(id,next.positions.length/3);
   next.positions.push(...se466RingKernel.capPoint(point(data,id),r.centroid,{...capOptions,offset:add(offset,mul(r.normal,depth))}));
   next.uvs.push(...add(uv(data,id),shift));}""")
    html=one(html,
        "const clone=value=>structuredClone(value),ops=['inset','extrude','deleteFaces','solidify','splitEdge','subdivide','fillHole','repairNormals'];",
        "const clone=value=>structuredClone(value),ops=['inset','extrude','deleteFaces','solidify','splitEdge','subdivide','fillHole','repairNormals','ringTransform','ringRefine','ringExtrude'];")
    html=one(html,
        "  const ids=faceIds(p),r=ids.length?region(p,ids):null;",
        """  const ids=faceIds(p),r=ids.length?region(p,ids):null;
  const verts=selectedRingVertices(p);
  for(const op of ['ringTransform','ringRefine','ringExtrude'])
   result[op]={available:verts.length>0,reason:verts.length?
    (op==='ringExtrude'?'Select one complete open boundary loop; interior ring caps use Face Extrude.':'Edit the selected real mesh vertices, keeping native Undo and UVs.'):
    'Switch to Vertex mode and select a ring or arc.'};""")
    html=one(html,
        "   ...availability(),message};",
        "    ...availability(),ring:{centered:!!ringAnchor&&ringAnchor.partId===selection&&ringAnchor.documentToken===native().documentToken&&ringAnchor.revision===native().revision},message};")
    html=one(html,
        " function convert(){\n  if(active)return fail('Apply or cancel this preview before converting another mesh.');",
        runtime('model_ring_bridge_v11_466.js')+"\n function convert(){\n  if(active)return fail('Apply or cancel this preview before converting another mesh.');")
    html=one(html,
        "if(operation==='extrude')return se430MeshOps.extrude(p.topologyMesh,ids,{depth:amount??.15});",
        "if(operation==='extrude')return se430MeshOps.extrude(p.topologyMesh,ids,{depth:amount??.15,scale:params.scale,leftScale:params.leftScale,rightScale:params.rightScale,offset:params.offset,tilt:params.tilt});")
    html=one(html,
        "  return fail('This topology operation is not implemented.');",
        """   const verts=selectedRingVertices(p);
   if(operation==='ringTransform')return se466RingKernel.transform(p.topologyMesh,verts,params);
   if(operation==='ringRefine')return se466RingKernel.refine(p.topologyMesh,verts);
   if(operation==='ringExtrude')return se466RingKernel.extrudeBoundary(p.topologyMesh,verts,{...params,depth:amount??.15});
   return fail('This topology operation is not implemented.');""")
    html=one(html,
        """if(!ops.includes(operation)||!params||typeof params!=='object'||Array.isArray(params)||Object.keys(params).some(k=>k!=='amount')||
   Object.hasOwn(params,'amount')&&(typeof params.amount!=='number'||!Number.isFinite(params.amount)))return fail('Choose a supported topology operation and a finite local amount.');""",
        """if(!ops.includes(operation)||!params||typeof params!=='object'||Array.isArray(params)||
   Object.keys(params).some(k=>!['amount','offset','tilt','scale','leftScale','rightScale','falloff','axis'].includes(k))||
   Object.hasOwn(params,'amount')&&(typeof params.amount!=='number'||!Number.isFinite(params.amount)))
   return fail('Choose a supported topology operation and finite controls.');""")
    html=one(html,
        "  record.selectedFaces=Array.isArray(result.selectedFaces)?[...result.selectedFaces]:[];",
        """  record.selectedFaces=Array.isArray(result.selectedFaces)?[...result.selectedFaces]:[];
  record.selectedVertices=Array.isArray(result.selectedVertices)?[...result.selectedVertices]:[];""")
    html=one(html,
        """  atelierComponentMode=record.selectedFaces.length?'face':record.mode;atelierComponentIds=[...record.selectedFaces];refreshComponents();""",
        """  atelierComponentMode=record.selectedVertices?.length?'vertex':record.selectedFaces.length?'face':record.mode;
  if(record.selectedVertices?.length){
   const mesh=meshFor(),top=mesh&&atelierComponentTopology(mesh);
   const keys=new Set(record.selectedVertices.map(id=>top?.keys?.[id]));
   atelierComponentIds=top?.vertices?.map((id,i)=>keys.has(top.keys[id])?i:-1).filter(i=>i>=0)||[];
  }else atelierComponentIds=[...record.selectedFaces];
  refreshComponents();""")
    html=one(html,
        "return Object.freeze({inspect,create,convert,selectRegion,setComponentMode,preview,apply,cancel});",
        "return Object.freeze({inspect,create,convert,selectRegion,setComponentMode,setRingAnchor,selectRing,preview,apply,cancel});")
    # Extend the SAME manual workshop UI; its existing Preview/Apply/Cancel remains authoritative.
    html=one(html,
        """native.querySelector('#modelAtelierWorkshopPreview').addEventListener('click',()=>{const amount=Number(native.querySelector('#modelAtelierWorkshopAmount').value);se430BeginnerResult(se430BeginnerAPI()?.preview(operation.value,se430BeginnerAmount(operation.value)?{amount}:{}));});""",
        """native.querySelector('#modelAtelierWorkshopPreview').addEventListener('click',()=>{
   const amount=Number(native.querySelector('#modelAtelierWorkshopAmount').value);
   const val=id=>Number(native.querySelector('#'+id)?.value);
   const ext=operation.value==='extrude'?{
    scale:val('modelAtelierWorkshopExtrudeScale'),leftScale:val('modelAtelierWorkshopExtrudeLeft'),
    rightScale:val('modelAtelierWorkshopExtrudeRight'),
    offset:['X','Y','Z'].map(a=>val('modelAtelierWorkshopExtrude'+a)),
    tilt:['X','Y','Z'].map(a=>val('modelAtelierWorkshopExtrudeTilt'+a))}:{};
   se430BeginnerResult(se430BeginnerAPI()?.preview(operation.value,se430BeginnerAmount(operation.value)?{amount,...ext}:{}));
  });""")
    html=one(html,'/* SE465_NARROW_INSPECTOR_END */',
        '/* SE465_NARROW_INSPECTOR_END */\n'+runtime('model_ring_ui_v11_466.js'))
    html=one(html,'se430BeginnerInstall(panel);','se430BeginnerInstall(panel);se466RingUIInstall(panel);')
    html=one(html,"['Manual mesh modeling',['WorkshopOperation','WorkshopAmount','WorkshopConvert'",
        "['Manual mesh modeling',['WorkshopOperation','WorkshopAmount','WorkshopExtrudeScale','WorkshopExtrudeLeft','WorkshopExtrudeRight','WorkshopExtrudeX','WorkshopExtrudeY','WorkshopExtrudeZ','WorkshopExtrudeTiltX','WorkshopExtrudeTiltY','WorkshopExtrudeTiltZ','WorkshopConvert'")
    css=runtime('model_ring_ui_v11_466.css')
    html=one(html,'</head>','<style id="se466RingModelStyles">\n'+css+'\n</style>\n</head>')
    html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_465_INSPECTOR_READABILITY',MARKER)
    html=one(html,'ENGINE · MAKER v11.465','ENGINE · MAKER v11.466')
    html=one(html,'v11.465 · readable mobile inspector','v11.466 · ring and arc modeling')
    html=one(html,"window.SWRLZ_FORGE_BUILD={version:'v11.465'","window.SWRLZ_FORGE_BUILD={version:'v11.466'")
    html=one(html,'<title>§wyrl§ Engine · Maker v11.465</title>','<title>§wyrl§ Engine · Maker v11.466</title>')
    prior=" source.engine='§wyrl§ Engine · Maker v11.465';source.version=11.465;"
    assert html.count(prior)==5,('v11.466 provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.466';source.version=11.466;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.465']
    notes['history'].insert(0,{'version':'v11.465','changes':notes.get('changes',[])})
    notes.update(version='v11.466',date='2026-11-15',title='Native ring, arc and graduated extrusion candidates',changes=[
     'Vertex mode adds graph-radius outline/fill and adjustable arc selection, topology-aware edge refinement, selected-ring move/scale/tilt with falloff, and validated open-boundary extrusion.',
     'Face Extrude supports larger signed depth and graded outward cap scaling, offset and tilt. Negative extrusions with shape modifiers remain guarded pending stronger collision detection.',
     'Operations reuse native candidate preview, Apply, Cancel, source validation and Undo. UV data remains indexed; the selected newly created ring is retained where possible.',
     'These controls extend the existing Model Studio UI without replacing global toolbars, VR, camera, projects or materials; real device acceptance remains separate.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+length:]
