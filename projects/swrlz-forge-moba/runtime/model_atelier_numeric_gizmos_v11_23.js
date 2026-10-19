// §E v11.23 accessible numeric group transform; works with the real vertex
// selection and native edit history, no synthetic browser-only geometry.
const atelierGroupModes=['translate','rotate','scale'];
const atelierGroupSpaces=['object','world','surface'];
function atelierGroupEdit(mesh,ids,mode,space,vector,snap=0){
 if(!mesh?.isMesh||!atelierGroupModes.includes(mode)||!atelierGroupSpaces.includes(space)||
   !Array.isArray(ids)||ids.length<1||ids.length>256||
   !Array.isArray(vector)||vector.length!==3||vector.some(v=>!Number.isFinite(v)))return null;
 const geometry=mesh.geometry,position=geometry.attributes.position,normal=geometry.attributes.normal;
 if(ids.some(i=>!Number.isInteger(i)||i<0||i>=position.count)||new Set(ids).size!==ids.length)return null;
 if(mode==='translate'&&vector.some(v=>Math.abs(v)>.5))return null;
 if(mode==='rotate'&&vector.some(v=>Math.abs(v)>180))return null;
 if(mode==='scale'&&vector.some(v=>v<.1||v>3))return null;
 if(!Number.isFinite(snap)||snap<0||snap>.1)return null;
 mesh.updateMatrixWorld(true);
 const points=ids.map(i=>new THREE.Vector3().fromBufferAttribute(position,i));
 const pivot=points.reduce((sum,p)=>sum.add(p),new THREE.Vector3()).multiplyScalar(1/points.length);
 const localToWorld=mesh.matrixWorld.clone(),worldToLocal=localToWorld.clone().invert();
 const normals=ids.map(i=>normal?new THREE.Vector3().fromBufferAttribute(normal,i):new THREE.Vector3(0,0,1));
 const axis=normals.reduce((sum,n)=>sum.add(n),new THREE.Vector3()).normalize();
 if(axis.lengthSq()<1e-8)axis.set(0,0,1);
 const alignment=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,1),axis);
 const unalignment=alignment.clone().invert();
 const originWorld=pivot.clone().applyMatrix4(localToWorld);
 const rot=new THREE.Euler(...vector.map(d=>THREE.MathUtils.degToRad(d)),'XYZ');
 const scale=new THREE.Vector3(...vector);
 const movements=[];
 for(const point of points){
   let after=point.clone();
   if(space==='world'){
     const before=point.clone().applyMatrix4(localToWorld);
     if(mode==='translate')before.add(new THREE.Vector3(...vector));
     else if(mode==='rotate')before.sub(originWorld).applyEuler(rot).add(originWorld);
     else before.sub(originWorld).multiply(scale).add(originWorld);
     after=before.applyMatrix4(worldToLocal);
   }else if(space==='surface'){
     if(mode==='translate')after.add(new THREE.Vector3(...vector).applyQuaternion(alignment));
     else if(mode==='rotate'){
       after.sub(pivot).applyQuaternion(unalignment).applyEuler(rot).applyQuaternion(alignment).add(pivot);
     }else{
       after.sub(pivot).applyQuaternion(unalignment).multiply(scale).applyQuaternion(alignment).add(pivot);
     }
   }else{
     if(mode==='translate')after.add(new THREE.Vector3(...vector));
     else if(mode==='rotate')after.sub(pivot).applyEuler(rot).add(pivot);
     else after.sub(pivot).multiply(scale).add(pivot);
   }
   const move=after.sub(point).toArray().map(v=>snap>0?Math.round(v/snap)*snap:v);
   if(move.some(v=>!Number.isFinite(v)||Math.abs(v)>.5))return null;
   movements.push(move);
 }
 return {
   indices:[...ids],moves:movements,
   maxDisplacement:Math.max(...movements.map(a=>Math.hypot(...a)))
 };
}
function atelierGroupApplyNumeric(){
 const p=partById(selection);
 if(!p){status('Select a mesh part first.',true);return;}
 if(p.refinementLayers?.some(l=>l.enabled)){
   status('Disable refinement layers before moving base vertex indices; this protects their source IDs.',true);return;
 }
 const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===selection);
 if(!mesh||!atelierSculptVertexIDs.length){status('Select mesh vertices first (indices or cyan markers).',true);return;}
 const ids=atelierSculptExpandedIndices(mesh.geometry,atelierSculptVertexIDs);
 const mode=$m('GroupMode').value,space=$m('GroupSpace').value;
 const vector=[0,1,2].map(i=>Number($m('GroupValue'+i).value));
 const snap=Number($m('SculptBrushSnap').value);
 const edit=atelierGroupEdit(mesh,ids,mode,space,vector,snap);
 if(!edit){status('Numeric transform rejected: check valid XYZ, ≤256 vertices and ≤0.5 local displacement.',true);return;}
 if(edit.maxDisplacement<1e-7){status('No vertex movement to commit.');return;}
 const record={indices:edit.indices,moves:edit.moves,resolution:atelierSculptResolution(p)};
 const next={...p,sculptVertexEdits:[...(p.sculptVertexEdits||[]),record]};
 if(!checkPart(next)){status('Transform rejected by native validation/vertex budget.',true);return;}
 checkpoint();p.sculptVertexEdits=next.sculptVertexEdits;const id=p.id;
 signalEdited();select(id);
 status('Saved '+edit.indices.length+' vertex '+mode+' operations in '+space+' space; Undo and OBJ/JSON replay supported.');
}
function atelierGroupInstall(){
 $m('GroupApply').addEventListener('click',atelierGroupApplyNumeric);
 $m('GroupMode').addEventListener('change',()=>{
   const mode=$m('GroupMode').value;
   const vals=mode==='scale'?[1,1,1]:[0,0,0];
   for(let i=0;i<3;i++)$m('GroupValue'+i).value=String(vals[i]);
   $m('GroupHelp').textContent=mode==='rotate'?'XYZ Euler degrees (±180)':mode==='scale'?
    'Multipliers 0.1–3; unchanged scale is 1':'Translation XYZ in local or world units (±0.5)';
 });
}
