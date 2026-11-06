// §E v11.288: smooth, connected hand macro geometry; cliff stone is a material illusion.
// The owner's reference uses color/normal/AO/roughness to draw stone courses and
// recessed cracks, NOT 3D rock blocks, crack tubes, or separate fingertip stones.
const SE288_ATLAS = 'assets/cliff-hand/cliff_pbr_atlas_384.jpg';
const se288Textures = new Map();
const se288Status = { loaded:0, failed:0 };
function se288AtlasTile(tile, color=false){
 const key=tile+'|'+(color?'srgb':'linear');
 if(se288Textures.has(key))return se288Textures.get(key);
 const tex=new THREE.TextureLoader().load(SE288_ATLAS,()=>{se288Status.loaded++;},undefined,
  err=>{se288Status.failed++;console.warn('Smooth Cliff Hand material load failed',err);});
 // The owner-derived 1536 x 768 atlas contains 4 columns and 2 rows of
 // 384px rock maps; avoid cross-tile bilinear sampling at the borders.
 const c=tile%4,r=Math.floor(tile/4);
 const pad=3, side=384;
 tex.offset.set((c*side+pad)/(side*4),((1-r)*side+pad)/(side*2));
 tex.repeat.set((side-2*pad)/(side*4),(side-2*pad)/(side*2));
 tex.wrapS=THREE.ClampToEdgeWrapping;
 tex.wrapT=THREE.ClampToEdgeWrapping;
 tex.minFilter=THREE.LinearMipmapLinearFilter;
 tex.magFilter=THREE.LinearFilter;
 tex.anisotropy=2;
 tex.colorSpace=color?THREE.SRGBColorSpace:THREE.NoColorSpace;
 tex.needsUpdate=true;
 se288Textures.set(key,tex);
 return tex;
}
function se288CliffMaterial(part){
 // Same UV coordinates feed the maps, keeping fractures aligned across
 // color, normal, roughness and shadowing. No shader-generated geometry.
 return new THREE.MeshStandardMaterial({
  color:part.color||'#ffffff',
  map:se288AtlasTile(0,true),
  normalMap:se288AtlasTile(1),
  normalScale:new THREE.Vector2(.68,.68),
  aoMap:se288AtlasTile(3),
  aoMapIntensity:.9,
  roughnessMap:se288AtlasTile(2),
  roughness:.96,
  metalness:0,
  side:THREE.DoubleSide
 });
}
function se288ProjectCliffUV(part){
 const mesh=part.topologyMesh;
 if(!mesh||!Array.isArray(mesh.positions)||mesh.positions.length<9)
  throw Error('Smooth Cliff Hand requires the connected original anatomy topology.');
 // One continuous projection across the entire hand, instead of mapping a
 // complete rock tile onto EVERY disconnected rock object.
 // X/Y are the dominant frontal planes. The subtle Z warp spreads the
 // texture onto the curved sidewalls without changing a single vertex.
 const p=mesh.positions,uv=[];
 for(let i=0;i<p.length;i+=3){
  const x=p[i],y=p[i+1],z=p[i+2];
  const u=(x+1.52+.14*z)/2.35;
  const v=(y-.53+.045*z)/2.96;
  uv.push(Math.max(.002,Math.min(.998,u)),Math.max(.002,Math.min(.998,v)));
 }
 mesh.uvs=uv;
 return uv.length/2;
}
function se288SmoothCliffHandScene(){
 // The existing v11.212 organic shell supplies watertight connected
 // five-finger anatomy and v11.220 native skeletal deformation.
 const scene=se212HandScene(),model=scene.project.modelAtelier;
 const shell=model.parts.find(p=>p.kind==='topologyMesh'
   &&p.organicSurface?.region==='shell'
   &&Array.isArray(p.topologyMesh?.positions)
   &&p.topologyMesh.positions.length>9);
 if(!shell)throw Error('Plain Hand connected anatomical shell not found.');
 if(!se220RigValidate(model.rigging)||model.rigging.bones.length!==17)
  throw Error('Plain Hand native 17-bone rig is missing.');
 const stone=structuredClone(shell);
 stone.id='plain-hand-anatomy';
 stone.name='Cliff Hand · smooth connected stone surface';
 stone.group='Cliff stone · mapped material (not 3D chunks)';
 stone.color='#ffffff';stone.material='matte';
 stone.position=[0,0,0];stone.rotation=[0,0,0];stone.scale=[1,1,1];
 // Keeps native surface sculpt/editor support. Rendering uses cliffPBR.
 stone.organicSurface={species:'cliff-hand',region:'shell'};
 stone.cliffPBR={atlas:'cliff_pbr_atlas_384',variant:'subtle-moss',
  method:'one-shell-planar-UV;stone-cracks-in-color-normal-AO-only'};
 const vertices=se288ProjectCliffUV(stone);
 // The complete hand remains one editable native topology mesh, with
 // no extra crack geometry, plate objects, stones, or floating fragments.
 model.parts=[stone];model.meshGroups=[];
 model.name='Plain Hand Base · Smooth Cliff Hand';
 model.reference='Owner Cliff Hand: smooth, continuous palm/fingers/thumb/wrist with rock divisions drawn in a single mapped material. Original 17-bone rig and animation retained. Natural color, normal, roughness, AO and sparse moss derived from supplied reference ZIP. No modeled rock chunks, cracks or stone plate objects.';
 model.editedAt='local';
 scene.project.name=model.name;
 scene.project.kind='model-atelier';
 scene.project.template='plain-hand-base';
 scene.project.canonicalId='plain-hand-base';
 scene.project.environmentSettings={...scene.project.environmentSettings,
  showTerrain:false,showScenery:false,background:'#161c27'};
 scene.engine='§wyrl§ Engine · Maker v11.288';scene.version=11.288;
 if(vertices<100)throw Error('Cliff Hand anatomy unexpectedly low detail.');
 return scene;
}
window.SWYRL_ENGINE_SMOOTH_CLIFF_HAND_288=Object.freeze({
 id:'plain-hand-base',
 createScene:se288SmoothCliffHandScene,
 status:()=>({connectedMeshes:1,stoneObjects:0,crackObjects:0,
  nativeRigBones:17,atlas:SE288_ATLAS,maps:['albedo+moss','normal','roughness','AO'],
  texturesLoaded:se288Status.loaded,textureErrors:se288Status.failed})
});