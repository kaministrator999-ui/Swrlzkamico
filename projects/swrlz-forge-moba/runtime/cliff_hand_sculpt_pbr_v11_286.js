// §E v11.286 · owner reference: the Plain Hand starter becomes a genuine
// sculpted cliff hand. Geometry is independent editable topology meshes, not
// a single textured glove or an image billboard. Other starters stay intact.
const SE286_ATLAS='assets/cliff-hand/cliff_pbr_atlas_128.jpg';
const se286AtlasCache=new Map();
const se286AtlasStatus={requested:0,loaded:0,errors:0};
const se286RockPalette=['#c78553','#b97447','#d69a6a','#a76543','#92593e','#c18b61','#ae7651','#b16b47'];
function se286AtlasTile(tile,kind='data'){
 const key=tile+'|'+kind;
 if(se286AtlasCache.has(key))return se286AtlasCache.get(key);
 const tex=new THREE.TextureLoader().load(SE286_ATLAS,
   ()=>{se286AtlasStatus.loaded++;},undefined,
   err=>{se286AtlasStatus.errors++;console.warn('Cliff Hand material atlas could not load',err);});
 // Eight owner-supplied maps in a 4 x 2 atlas. Inset prevents mip bleeding.
 const c=tile%4,r=Math.floor(tile/4),px=128;
 tex.wrapS=THREE.ClampToEdgeWrapping;tex.wrapT=THREE.ClampToEdgeWrapping;
 tex.offset.set((c*px+2)/(px*4),((1-r)*px+2)/(px*2));
 tex.repeat.set((px-4)/(px*4),(px-4)/(px*2));
 tex.minFilter=THREE.LinearMipmapLinearFilter;
 tex.magFilter=THREE.LinearFilter;
 tex.anisotropy=2;
 if(kind==='color')tex.colorSpace=THREE.SRGBColorSpace;
 else tex.colorSpace=THREE.NoColorSpace;
 tex.needsUpdate=true;
 se286AtlasCache.set(key,tex);se286AtlasStatus.requested++;
 return tex;
}
function se286CreateCliffMaterial(part){
 const variant=part.cliffPBR?.variant||'bare';
 const albedo=variant==='moss'?0:variant==='dirt'?5:4;
 return new THREE.MeshStandardMaterial({
  color:'#ffffff',
  map:se286AtlasTile(albedo,'color'),
  normalMap:se286AtlasTile(1,'normal'),
  normalScale:new THREE.Vector2(.30,.30),
  roughness:.96,
  roughnessMap:se286AtlasTile(2),
  metalness:0,
  aoMap:se286AtlasTile(3),
  aoMapIntensity:.77,
  bumpMap:se286AtlasTile(6),
  bumpScale:.009,
  side:THREE.DoubleSide
 });
}
// Unwrap each independently sculpted piece onto its own atlas tile. The native
// editor's existing planar UVs were world-projected, so most stones only
// sampled tiny unrelated fragments of the maps. Rebuild per-piece UVs only.
function se286Unwrap(part){
 const topo=part.topologyMesh;
 if(!topo||!Array.isArray(topo.positions)||topo.positions.length%3)return;
 const pos=topo.positions,lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
 for(let i=0;i<pos.length;i+=3)for(let k=0;k<3;k++){
  lo[k]=Math.min(lo[k],pos[i+k]);hi[k]=Math.max(hi[k],pos[i+k]);
 }
 const span=hi.map((h,k)=>h-lo[k]);
 const horizontal=span[0]>=span[2]?0:2;
 const uvs=[];
 for(let i=0;i<pos.length;i+=3){
  // No position changes here: preserve the original 17-joint skin rest pose.
  const u=(pos[i+horizontal]-lo[horizontal])/Math.max(.005,span[horizontal]);
  const v=(pos[i+1]-lo[1])/Math.max(.005,span[1]);
  uvs.push(Math.max(0,Math.min(1,u)),Math.max(0,Math.min(1,v)));
 }
 topo.uvs=uvs;
}
function se286CliffHandScene(){
 // Plain Hand supplies the canonical anatomical proportions and 17-joint rig;
 // the native rock construction supplies closed sculpted shapes all around.
 const scene=se212HandScene(),rock=se282FullRockScene();
 const model=scene.project.modelAtelier,source=rock.project.modelAtelier;
 if(!se220RigValidate(model.rigging)||model.rigging.bones.length!==17)
  throw Error('Cliff Hand requires the intact 17-bone Plain Hand rig.');
 const parts=structuredClone(source.parts);
 for(let i=0;i<parts.length;i++){
  const part=parts[i];
  if(part.material==='emissive'){
   // Real dark crevices rather than unrelated glowing orange spell glyphs.
   part.material='matte';part.color='#352a27';
   part.group='Crevices / stone seams';
   continue;
  }
  part.material='matte';
  part.color=se286RockPalette[(i*7+Math.floor(i/5))%se286RockPalette.length];
  const finger=/^Finger|^Thumb/i.test(part.name);
  const palm=/^Palm|^Back|foundation|Wrist|side/i.test(part.name);
  const moss=(palm&&(i%5===0||i%7===0))||(finger&&i%9===0);
  part.cliffPBR={atlas:'cliff_pbr_atlas_128',variant:moss?'moss':i%13===0?'dirt':'bare'};
  se286Unwrap(part);
 }
 // Additional native overlapping little sandstone scales are sculpted in the
 // palm/back and along the wrist, inspired by the segmented reference. Every
 // scale remains individually selectable, paintable and editable in Atelier.
 const tileCount=parts.length;
 for(const side of [-1,1])for(let row=0;row<4;row++)for(let col=0;col<4;col++){
  const y=1.12+row*.27+(col%2)*.035;
  const width=y>1.3?.30:.20;
  const x=(col-1.5)*(width*.89);
  const part={id:'cliff-sculpt-tile-'+side+'-'+row+'-'+col,
   name:(side<0?'Back':'Palm')+' · individually sculpted strata '+(row+1)+'-'+(col+1),
   kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],
   color:se286RockPalette[(row*3+col+7)%se286RockPalette.length],
   material:'matte',group:'Sandstone / sculpted palm plates',
   cliffPBR:{atlas:'cliff_pbr_atlas_128',variant:(row+col+Number(side>0))%5===0?'moss':'bare'},
   topologyMesh:se282CliffSlab({x,y,z:side*(.31+(row===0?-.025:0)),
     wx:.105+(row%2)*.016,hy:.11,depth:.078,side,
     seed:509+row*17+col*5+(side>0?80:0),angle:(col-1.5)*.10})};
  se286Unwrap(part);parts.push(part);
 }
 if(parts.length>MODEL_ATELIER_LIMIT)throw Error('Cliff Hand exceeded native part budget.');
 if(parts.some(p=>p.organicSurface))throw Error('Exposed smooth glove must not remain in Cliff Hand.');
 model.parts=parts;
 model.name='Plain Hand Base · Cliff Hand Sculpt';
 model.meshGroups=[...new Set(parts.map(p=>p.group))].map((group,i)=>({
  id:'cliff-sculpt-group-'+i,name:group,
  members:parts.filter(p=>p.group===group).map(p=>p.id)
 })).filter(g=>g.members.length>=2);
 model.poseFrames=[];model.poseNeutral=null;model.editedAt='local';
 model.reference='Owner Cliff Hand orthographic / growth / pose reference, sculpted from the Plain Hand 17-bone anatomy. 360-degree solid stone fingers, thumb, palm and wrist; individually editable weathered sandstone slabs; moss in selective crevices; textured color, OpenGL tangent normals, roughness, AO and height/bump from supplied maps. No glowing glove or exposed human skin.';
 scene.project.name=model.name;
 scene.project.canonicalId='plain-hand-base';
 scene.project.template='plain-hand-base';
 scene.project.kind='model-atelier';
 scene.project.environmentSettings={...scene.project.environmentSettings,
  showTerrain:false,showScenery:false,background:'#161c27'};
 scene.engine='§wyrl§ Engine · Maker v11.286';scene.version=11.286;
 return scene;
}
window.SWYRL_ENGINE_CLIFF_HAND_286=Object.freeze({
 id:'plain-hand-base',atlas:SE286_ATLAS,createScene:se286CliffHandScene,
 status:()=>({maps:8,atlasLoaded:se286AtlasStatus.loaded,
  atlasErrors:se286AtlasStatus.errors,textureCache:se286AtlasCache.size,
  rigBones:17,editableNative:true})
});