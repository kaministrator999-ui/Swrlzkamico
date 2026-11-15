/* SE462_MODEL_WIRE_CLARITY_START */
// Display-only companion to the native ModelAtelier renderer. The model,
// indexed face IDs, UVs, authored materials and native Undo are never edited.
const se462WirePrefs={triangles:false,hidden:false};
function se462EligibleWire(mesh){
 const geo=mesh?.geometry;
 const n=geo?.getIndex?.()?.count||geo?.getAttribute?.('position')?.count||0;
 return !!mesh?.isMesh&&!mesh.isSkinnedMesh&&n>=3&&n<=72000;
}
function se462PrimaryColor(part){
 return part?.id===selection?0x63ffe1:0xe4f4ff;
}
function se462DisposeWire(mesh){
 for(const child of [...(mesh?.children||[])]){
  if(!child.userData?.se462WireOwned)continue;
  mesh.remove(child);
  child.geometry?.dispose?.();child.material?.dispose?.();
 }
}
function se462AddLine(mesh,geom,opts){
 const line=new THREE.LineSegments(geom,new THREE.LineBasicMaterial({
  color:opts.color,transparent:true,opacity:opts.opacity,
  depthTest:opts.depthTest!==false,depthWrite:false
 }));
 line.name=opts.name;line.renderOrder=opts.order||10;
 line.userData.atelierHelper=true;
 line.userData.se455DisplayEdges=true;
 line.userData.se455OwnedGeometry=true;
 line.userData.se462WireOwned=true;
 line.userData.se462Primary=!!opts.primary;
 mesh.add(line);return line;
}
function se462EnhanceMaterial(mesh,part){
 if(!se461LowPolyEditable(part,mesh))return;
 const base=mesh.material;
 if(!base||Array.isArray(base)||base.flatShading||typeof base.clone!=='function')return;
 const sharp=base.clone();
 sharp.flatShading=true;sharp.needsUpdate=true;
 sharp.userData={...base.userData,atelierViewportClone:true,se462SharpMaterial:true};
 mesh.material=sharp;
 if(base!==mesh.userData.se455OriginalMaterial&&base.userData?.atelierViewportClone)base.dispose?.();
}
const se462PreviousApply=atelierViewModeApply;
atelierViewModeApply=function(mesh,part){
 const result=se462PreviousApply.apply(this,arguments);
 if(!mesh?.isMesh||!part)return result;
 se462DisposeWire(mesh);
 const mode=atelierViewModeFor(part);
 if(mode==='shaded'){
  se462EnhanceMaterial(mesh,part); // Correct the apparent inset-cap smoothing.
 }
 if(mode==='overlay'){
  for(const child of mesh.children){
   if(child.name!=='Viewport wireframe overlay')continue;
   child.material?.color?.setHex?.(se462PrimaryColor(part));
   if(child.material){child.material.transparent=true;child.material.opacity=1;child.material.depthTest=true;child.material.depthWrite=false;child.material.needsUpdate=true;}
   child.renderOrder=10;
  }
 }
 if(['solid','flat','clay'].includes(mode)){
  for(const child of mesh.children){
   if(!child.userData?.se461HardEdges&&!child.userData?.se458Contour)continue;
   child.material?.color?.setHex?.(se462PrimaryColor(part));
   if(child.material){child.material.opacity=part.id===selection?1:.84;child.material.depthTest=true;}
  }
 }
 if(!se462EligibleWire(mesh)||!['wireframe','overlay'].includes(mode))return result;
 if(mode==='wireframe'){
  // Render mesh to DEPTH ONLY, followed by angle-filtered primary edges.
  // Thus internal triangulation is not the default visible wireframe.
  const old=mesh.material;
  const depth=new THREE.MeshBasicMaterial({
   color:0xffffff,colorWrite:false,depthTest:true,depthWrite:true,
   polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1,
   side:THREE.DoubleSide
  });
  depth.userData={atelierViewportClone:true,se462DepthOnly:true};
  mesh.material=depth;
  if(old!==mesh.userData.se455OriginalMaterial&&old?.userData?.atelierViewportClone)old.dispose?.();
  const edges=new THREE.EdgesGeometry(mesh.geometry,18);
  if(se462WirePrefs.hidden)se462AddLine(mesh,edges.clone(),{
   color:0x8aa4c2,opacity:.23,depthTest:false,name:'Hidden wire guide',order:7
  });
  se462AddLine(mesh,edges,{
   color:se462PrimaryColor(part),opacity:1,depthTest:true,
   name:'Clean topology wire',order:10,primary:true
  });
 }
 if(se462WirePrefs.triangles){
  se462AddLine(mesh,new THREE.WireframeGeometry(mesh.geometry),{
   color:0x85b1d2,opacity:.27,depthTest:true,
   name:'Optional triangle diagnostics',order:9
  });
 }
 return result;
};
function se462Recolor(){
 if(!modelRoot)return;
 for(const mesh of modelRoot.children){
  if(!mesh?.isMesh||!mesh.userData?.atelierId)continue;
  const p=partById(mesh.userData.atelierId);if(!p)continue;
  for(const child of mesh.children){
   if(child.userData?.se462Primary||child.userData?.se461HardEdges||
      child.userData?.se458Contour||child.name==='Viewport wireframe overlay'){
    child.material?.color?.setHex?.(se462PrimaryColor(p));
    if(child.userData?.se461HardEdges||child.userData?.se458Contour)
     child.material.opacity=p.id===selection?1:.84;
   }
  }
 }
}
window.addEventListener('swrlz:model-workshop-change',()=>queueMicrotask(se462Recolor));
function se462SetPref(name,enabled){
 if(!Object.hasOwn(se462WirePrefs,name))return false;
 if(!!se430BeginnerAPI?.()?.inspect?.()?.preview?.active){
  status('Apply or cancel the mesh preview before changing wire diagnostics.',true);
  return false;
 }
 se462WirePrefs[name]=!!enabled;atelierViewRebuild();
 return true;
}
const se462PreviousInstall=se430BeginnerInstall;
se430BeginnerInstall=function(panel){
 const result=se462PreviousInstall(panel);
 const menu=panel?.querySelector('#se455ViewMenu');
 if(!menu||menu.querySelector('[data-se462-wire]'))return result;
 const group=document.createElement('div');
 group.className='se462-wire-options';group.setAttribute('role','group');
 group.setAttribute('aria-label','Wireframe diagnostics');
 for(const [name,title] of [['triangles','Show triangulation'],['hidden','Show hidden edges']]){
  const label=document.createElement('label'),input=document.createElement('input');
  input.type='checkbox';input.dataset.se462Wire=name;input.checked=se462WirePrefs[name];
  label.append(input,document.createTextNode(title));group.append(label);
  input.addEventListener('change',()=>{
   if(!se462SetPref(name,input.checked))input.checked=se462WirePrefs[name];
  });
 }
 menu.append(group);return result;
};
window.SWYRL_ENGINE_WIRES_462=Object.freeze({
 version:'v11.462',inspect:()=>({...se462WirePrefs}),
 setOption:se462SetPref,refresh:se462Recolor
});
/* SE462_MODEL_WIRE_CLARITY_END */