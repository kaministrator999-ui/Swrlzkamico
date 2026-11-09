// §E v11.369 · Real WebXR hand geometry, real Cliff stone PBR maps.
// Replace only the Plain Hand Base / Smooth Cliff starter: the independent
// left/right WebXR references, 89-piece Rocky Hand and saved scenes are untouched.
const se369CliffCloneState={loaded:0,partCount:1,source:'webxr-hand-right',
 textureAtlas:SE288_ATLAS,sourceVerts:1360,sourceTriangles:2314,
 nativeBones:17,originalUV:true,oldProceduralFieldUsed:false};
const se369CliffCloneTransform=Object.freeze({xScale:1.17,xPivot:.09,xOffset:-.135,
 yScale:1.06,yOffset:.28,zScale:.68,zPivot:.40});
function se369MapReferenceVertex(x,y,z){
 const c=se369CliffCloneTransform;
 // WebXR's palm spans local Z (index->pinky). §E spans X instead.
 // Swapping those axes and reversing the source palm normal preserves
 // triangle handedness while aligning the actual MCPs with the §E rig.
 return [(z-c.xPivot)*c.xScale+c.xOffset,
         y*c.yScale+c.yOffset,(c.zPivot-x)*c.zScale];
}
async function se369CliffFromXRScene(){
 const scene=await se358WebXRHandScene('right'); // cached bundled asset
 const m=scene?.project?.modelAtelier,part=m?.parts?.[0],t=part?.topologyMesh;
 if(m?.parts?.length!==1||part?.kind!=='topologyMesh'||!t||
  t.positions?.length!==4080||t.uvs?.length!==2720||
  t.indices?.length!==6942||m.referenceJoints?.length!==25)
  throw Error('WebXR source hand unavailable or changed; do not fallback to old Cliff geometry.');
 // se358 returns its own freshly cloned topology. Change this copy only.
 const p=t.positions;
 for(let i=0;i<p.length;i+=3){
  const xyz=se369MapReferenceVertex(p[i],p[i+1],p[i+2]);
  p[i]=+xyz[0].toFixed(6);p[i+1]=+xyz[1].toFixed(6);p[i+2]=+xyz[2].toFixed(6);
 }
 m.referenceJoints=m.referenceJoints.map(j=>({
  ...j,position:se369MapReferenceVertex(...j.position).map(x=>+x.toFixed(6))
 }));
 // Reuse the original hand's seamless authored UVs; the same UV coordinates
 // sample all four source Cliff atlas tiles. Do not stamp on old projections.
 part.id='plain-hand-webxr-cliff-shell';
 part.name='Cliff Hand · WebXR anatomical stone surface';
 part.group='Cliff Hand · stone-mapped WebXR mesh';
 part.color='#ffffff';part.material='matte';
 part.cliffPBR={atlas:'cliff_pbr_atlas_384',variant:'webxr-cliff',
  method:'source-WebXR-UV;cliff-color-normal-roughness-AO'};
 part.organicSurface={species:'cliff-hand',region:'shell'};
 part.position=[0,0,0];part.rotation=[0,0,0];part.scale=[1,1,1];
 m.name='Smooth Cliff Hand · WebXR Anatomy + Stone';
 m.meshGroups=[];m.assemblies=null;m.poseFrames=[];m.poseNeutral=null;
 m.rigging=se220CreateHandRig(se217FingerSpec);
 if(!se220RigValidate(m.rigging)||m.rigging.bones.length!==17)
  throw Error('Native hand rig failed to attach to the new cliff anatomy.');
 m.reference='Actual cloned MIT-licensed WebXR generic-hand/right.glb geometry, not procedural Cliff SDF. Original 1360-vertex 2314-triangle anatomical topology and UV islands transformed into native Model Studio bone coordinates. Original Cliff four-map owner PBR sandstone atlas (color, normals, roughness, AO); 25 source reference joints retained and transformed. Native 17-bone rig assigned by Model Atelier spatial skin weights. Previous dorsal geodes are disabled on this different UV layout. No source WebXR hand or Rocky Anime Hand starter was modified.';
 m.editedAt='local';
 scene.project.kind='model-atelier';scene.project.name=m.name;
 scene.project.canonicalId='plain-hand-base';scene.project.template='plain-hand-base';
 scene.project.environmentSettings={...scene.project.environmentSettings,
  showTerrain:false,showScenery:false,background:'#161c27'};
 scene.engine='§wyrl§ Engine · Maker v11.369';scene.version=11.369;
 se369CliffCloneState.loaded++;
 return scene;
}
let se369CliffLoading=false;
async function se369OpenCliffHand(force=false){
 if(se369CliffLoading)return false;
 if(dirty&&!force&&!confirm('Open WebXR-based Cliff Hand and discard unsaved changes?'))
  return false;
 se369CliffLoading=true;
 try{
  toast('Loading WebXR Cliff Hand and mapping sandstone textures…');
  const source=await se369CliffFromXRScene();
  ModelAtelier.close();
  loadProject(source,{workspaceLocal:true});
  if(currentProject?.kind!=='model-atelier'||
     currentProject?.modelAtelier?.parts?.length!==1)
   throw Error('The native modeling project did not open.');
  se232ActivateSelectedModelWorkspace();
  if(window.SWYRL_ENGINE_STUDIOS?.active?.()!=='modeler')
   window.SWYRL_ENGINE_STUDIOS?.change?.('modeler');
  ModelAtelier.syncProject();
  if(!ModelAtelier.status()?.open)
   throw Error('Model Studio viewport did not become active.');
  initializeHistory('Opened Cliff Hand · WebXR anatomical stone mesh');
  markSaved();
  document.getElementById('projectHub')?.classList.remove('show');
  requestAnimationFrame(()=>requestAnimationFrame(()=>
    window.SWYRL_ENGINE_MODEL_ATELIER?.view?.('three')));
  toast('Cliff Hand · real WebXR hand geometry with sandstone texture maps ready');
  return true;
 }catch(error){
  console.error('§E Cliff WebXR stone model load',error);
  toast('Could not open WebXR Cliff Hand: '+String(error?.message||error).slice(0,140));
  return false;
 }finally{se369CliffLoading=false;}
}
// The old registered starter calls se284OpenPlainHand by name, so hook it AND
// the dynamic template router, not an unrelated floating preview or card clone.
se284OpenPlainHand=se369OpenCliffHand;
const se369PriorTemplate=createProjectFromTemplate;
createProjectFromTemplate=function(template,force=false){
 if(template==='plain-hand-base')return se369OpenCliffHand(force);
 return se369PriorTemplate(template,force);
};
window.SWYRL_ENGINE_WEBXR_CLIFF_369=Object.freeze({
 createScene:se369CliffFromXRScene,open:se369OpenCliffHand,
 mapVertex:se369MapReferenceVertex,
 status:()=>({...se369CliffCloneState,loading:se369CliffLoading,
  isolatedStarterId:'plain-hand-base'})
});
