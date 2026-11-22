/* SE534_SHARED_START */
const se534ShapeSchema='swrlz-forge-mesh-shape-edit-v1';
const se534ShapeKinds=Object.freeze(['sphere','box','cone','cylinder','loft']);
const se534ShapeFields=['path','radii','segments'];

function se534ShapeData(op){
 if(!op||typeof op!=='object'||Array.isArray(op)||op.op!=='mesh.reshape'||
    typeof op.id!=='string'||!op.id.length||!se534ShapeKinds.includes(op.kind))throw Error('INVALID_MESH_RESHAPE');
 const fields=op.kind==='loft'?['op','id','kind',...se534ShapeFields]:['op','id','kind'];
 if(Object.keys(op).length!==fields.length||!fields.every(k=>Object.hasOwn(op,k)))
  throw Error('INVALID_MESH_RESHAPE_FIELDS');
 return se293ShapeData(op);
}
/* SE534_SHARED_END */

/* SE534_ATELIER_START */
const se534PlainPartFields=new Set(['id','name','kind','group','position','rotation','scale','color','material']);

function se534ChatShapeEditable(id){
 const data=model(),part=partById(id);
 if(!data||!panel||panel.hidden||playing||simulating||window.SWYRL_ENGINE_WORKSPACES?.usingScratch?.()||
    data.rigging||data.wolfRig||data.wolfAnimations||data.sheepAnimations||data.poseFrames?.length||data.poseNeutral||
    !part||!se534ShapeKinds.includes(part.kind))return false;
 // An authored surface can depend on its original vertex or UV correspondence.
 if(!Object.keys(part).every(k=>se534PlainPartFields.has(k)||part.kind==='loft'&&se534ShapeFields.includes(k)))return false;
 return checkPart(part);
}

function se534ChatReshape(op){
 const shape=se534ShapeData(op);
 if(!se534ChatShapeEditable(op.id))throw Error('MESH_RESHAPE_TARGET_PROTECTED');
 if(se340ModelBridge.inspect().gesture||se350ModelTools.inspect().gesture||se350ModelSurface.inspect().active||
    se390ModelCreate.inspect().pending||se410ModelAccessory.inspect().pending||se430ModelWorkshop.hasGeometryPreview()||
    atelierMeshDrag||atelierComponentDrag||atelierComponentGesture||atelierSculptDrag)
  throw Error('MESH_RESHAPE_GESTURE_ACTIVE');
 const part=partById(op.id),candidate={...part,kind:op.kind};
 for(const key of se534ShapeFields)delete candidate[key];
 Object.assign(candidate,shape);
 if(!checkPart(candidate))throw Error('INVALID_NATIVE_PART');
 const matches=value=>value.kind===candidate.kind&&se534ShapeFields.every(k=>JSON.stringify(value[k])===JSON.stringify(candidate[k]));
 const changed=!matches(part);
 if(changed){
  checkpoint();
  part.kind=candidate.kind;
  for(const key of se534ShapeFields){
   if(Object.hasOwn(candidate,key))part[key]=candidate[key];
   else delete part[key];
  }
  selection=part.id;
  signalEdited();
 }
 if(partById(op.id)!==part||!matches(part))throw Error('MESH_RESHAPE_NOT_APPLIED');
 return {changed,id:part.id,name:part.name,kind:part.kind};
}
/* SE534_ATELIER_END */

/* SE534_HOST_START */
function se534ShapeCapability(rows){
 return {schema:se534ShapeSchema,kinds:[...se534ShapeKinds],
  editableIds:rows.filter(row=>ModelAtelier.chatShapeEditable(row.id)).map(row=>row.id)};
}

function se534ValidateShapeEdit(op,ctx){
 if(ctx.workspace!=='model-atelier'||ctx.mode!=='edit'||
    ctx.meshShapeEdit?.schema!==se534ShapeSchema)throw Error('MESH_RESHAPE_UNAVAILABLE');
 if(!bounded(op.id,160)||!ctx.meshShapeEdit.editableIds.includes(op.id)||
    !ctx.meshes.some(row=>row.id===op.id)||!ModelAtelier.chatShapeEditable(op.id))
  throw Error('MESH_RESHAPE_TARGET_PROTECTED');
 se534ShapeData(op);
}
/* SE534_HOST_END */
