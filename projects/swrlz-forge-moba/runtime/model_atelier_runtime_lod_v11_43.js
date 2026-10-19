// §E v11.43 — opt-in per-part camera-distance LOD from two REAL, saved
// indexed geometries. A verified low mesh is embedded in native Model JSON.
// Display mode is transient; source high and low topology never mutate during
// camera movement. Selected mesh stays high for safe sculpt and topology edits.
const atelierRuntimeLODCenter=new THREE.Vector3();
function atelierRuntimeLODChoose(part,distance,selected=false,previous='high'){
 if(part?.kind!=='topologyMesh'||!part.runtimeLOD?.enabled||
    !Number.isFinite(distance)||selected)return 'high';
 const d=part.runtimeLOD.switchDistance;
 return distance>(previous==='low'?d*.92:d*1.08)?'low':'high';
}
function atelierRuntimeLODDispose(mesh){
 const state=mesh?.userData;
 if(!state)return;
 for(const key of ['atelierLODHigh','atelierLODLow']){
   const geometry=state[key];
   if(geometry&&geometry!==mesh.geometry)geometry.dispose();
   state[key]=null;
 }
}
let atelierRuntimeLODFrame=0;
function atelierRuntimeLODStart(){
 if(atelierRuntimeLODFrame||!modelRoot||!renderer||!panel||panel.hidden)return;
 const tick=()=>{
   // Separate opt-in candidate loop; it stops by itself when the editor
   // closes, without modifying the source engine's other scene renderers.
   if(!modelRoot||!renderer||!panel||panel.hidden){
     atelierRuntimeLODFrame=0;return;
   }
   atelierRuntimeLODUpdate();
   atelierRuntimeLODFrame=requestAnimationFrame(tick);
 };
 atelierRuntimeLODFrame=requestAnimationFrame(tick);
}
function atelierRuntimeLODUpdate(){
 if(!modelRoot||!camera)return;
 for(const mesh of modelRoot.children){
   const p=mesh.userData.atelierRuntimeLODPart;
   if(!p||!mesh.isMesh||!p.runtimeLOD?.enabled)continue;
   if(!mesh.userData.atelierLODHigh){
      mesh.userData.atelierLODHigh=mesh.geometry;
      mesh.userData.atelierLODActive='high';
   }
   mesh.updateWorldMatrix(true,false);
   const distance=camera.position.distanceTo(mesh.getWorldPosition(atelierRuntimeLODCenter));
   const mode=atelierRuntimeLODChoose(p,distance,selection===p.id,
     mesh.userData.atelierLODActive);
   if(mode!==mesh.userData.atelierLODActive){
      if(mode==='low'){
        if(!mesh.userData.atelierLODLow){
          mesh.userData.atelierLODLow=atelierTopologyGeometry({
             kind:'topologyMesh',topologyMesh:p.runtimeLOD.low});
        }
        mesh.geometry=mesh.userData.atelierLODLow;
      }else mesh.geometry=mesh.userData.atelierLODHigh;
      mesh.userData.atelierLODActive=mode;
   }
 }
}
function atelierRuntimeLODRefresh(){
 const p=partById(selection),pane=$m('RuntimeLODTools');if(!pane)return;
 pane.hidden=p?.kind!=='topologyMesh';
 if(p?.kind!=='topologyMesh')return;
 const lod=p.runtimeLOD,stats=$m('RuntimeLODStats');
 if(lod){
   $m('RuntimeLODDistance').value=String(lod.switchDistance);
   $m('RuntimeLODEnabled').checked=lod.enabled;
   stats.textContent='HIGH '+p.topologyMesh.indices.length/3+' triangles · LOW '+
      lod.low.indices.length/3+' triangles; '+
      (lod.enabled?'distance-switching ON':'profile saved, switching OFF')+
      '. Selected mesh remains HIGH for editing. Switch hysteresis ±8%; native JSON contains both.';
 }else{
   $m('RuntimeLODEnabled').checked=false;
   stats.textContent='No low-detail profile yet. Generate one from this baked mesh and save both levels.';
 }
}
function atelierRuntimeLODInstall(){
 const id=k=>$m('RuntimeLOD'+k);
 id('Generate').addEventListener('click',()=>{
   const p=partById(selection);
   if(p?.kind!=='topologyMesh'){status('Select an indexed baked mesh first.',true);return;}
   const ratio=Number(id('Ratio').value),d=Number(id('Distance').value);
   if(!Number.isFinite(d)||d<.5||d>120){
     status('LOD distance must be 0.5–120 world units.',true);return;
   }
   const high=atelierTopologyGeometry(p);
   const plan=atelierLODPlan(high,ratio);
   high.dispose();
   if(!plan.ok||!plan.canBake){
      status('Cannot build portable runtime LOD: '+(plan.reason||
         'Generated low-detail geometry exceeds native mesh limits.'),true);
      return;
   }
   const profile={enabled:true,switchDistance:d,low:plan.data};
   const candidate={...p,runtimeLOD:profile};
   if(!checkPart(candidate)){status('Native LOD profile rejected; original untouched.',true);return;}
   checkpoint();p.runtimeLOD=profile;
   signalEdited();select(p.id);
   status('Generated saved HIGH/LOW topology: '+plan.before+' → '+
       plan.after+' triangles, switching beyond '+d+' units for unselected objects.');
 });
 id('Enabled').addEventListener('change',()=>{
   const p=partById(selection),enabled=id('Enabled').checked;
   if(p?.kind!=='topologyMesh'||!p.runtimeLOD){
     id('Enabled').checked=false;return;
   }
   if(p.runtimeLOD.enabled===enabled)return;
   checkpoint();p.runtimeLOD.enabled=enabled;signalEdited();select(p.id);
 });
 id('Distance').addEventListener('change',()=>{
   const p=partById(selection);
   if(p?.kind!=='topologyMesh'||!p.runtimeLOD)return;
   const distance=Number(id('Distance').value);
   if(!Number.isFinite(distance)||distance<.5||distance>120){
     status('Distance must be between 0.5 and 120 units.',true);
     atelierRuntimeLODRefresh();return;
   }
   if(p.runtimeLOD.switchDistance===distance)return;
   checkpoint();p.runtimeLOD.switchDistance=distance;signalEdited();select(p.id);
 });
 id('Clear').addEventListener('click',()=>{
   const p=partById(selection);if(p?.kind!=='topologyMesh'||!p.runtimeLOD)return;
   checkpoint();delete p.runtimeLOD;signalEdited();select(p.id);
   status('Removed saved low-detail profile, retained original high-resolution mesh.');
 });
 window.SWYRL_ENGINE_RUNTIME_LOD=Object.freeze({report:()=>({
   enabled:model()?.parts.filter(p=>p.runtimeLOD?.enabled).length||0,
   meshes:modelRoot?.children.filter(m=>m.userData.atelierRuntimeLODPart)
     .map(m=>({id:m.userData.atelierId,
       active:m.userData.atelierLODActive||'high',
       triangles:(m.geometry?.index?.count||m.geometry?.attributes?.position?.count||0)/3,
       lowTriangles:m.userData.atelierRuntimeLODPart.runtimeLOD?.low?.indices?.length/3||0
     }))||[]
 })});
}
