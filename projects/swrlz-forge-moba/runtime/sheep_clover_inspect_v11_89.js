const stCloverVisualBase=stCourierVisualStatus;
stCourierVisualStatus=function(object){
 const model=object.getObjectByName('CloverMeadowSheep');if(!model)return stCloverVisualBase(object);
 const textures=new Map(),pivots=[],ids=[];let triangles=0,meshes=0;
 model.traverse(node=>{if(/^st(?:Leg[0-3]|Head|Tail)$/.test(node.name))pivots.push({name:node.name,rotation:node.rotation.toArray().slice(0,3),children:node.children.length});if(!node.isMesh)return;meshes++;ids.push(node.userData.cloverPartId);triangles+=(node.geometry.index?.count||node.geometry.attributes.position.count)/3;for(const material of Array.isArray(node.material)?node.material:[node.material])for(const channel of ['map','normalMap']){const texture=material[channel];if(texture&&!textures.has(texture.source.uuid))textures.set(texture.source.uuid,{channel,width:texture.image?.width||0,height:texture.image?.height||0,source:texture.source.uuid});}});
 return {visualModel:'clover-meadow-sheep',visualMeshes:meshes,visualTriangles:triangles,visualSourceTriangles:model.userData.sourceTriangles,visualPartIds:ids,visualTextures:[...textures.values()],visualPivots:pivots};
};
