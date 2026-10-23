// The existing shorts and armor owners receive fitted opaque surfaces. The
// connected skin remains intact underneath; no camera angle exposes the pelvis.
function atelierFestivalCoverageV1193(scene){
 const model=scene.project.modelAtelier,parts=model.parts,skin=parts.find(p=>p.id==='girl-organic-body').topologyMesh;
 const shorts=parts.find(p=>p.id==='festival-shorts');if(!shorts)throw Error('Existing festival underlayer is missing');
 shorts.topologyMesh=atelierAnimeClothShell(skin,[(x,y,z)=>y-1.98,(x,y,z)=>2.84-y,(x,y,z)=>.62-Math.abs(x)],.016);
 shorts.position=[0,0,0];shorts.rotation=[0,0,0];shorts.scale=[1,1,1];shorts.color='#123e48';shorts.material='silk';shorts.name='Costume · fitted opaque festival shorts';shorts.textureBinding={set:'festival-4k',tile:'cloth',normalStrength:.10};
 const combine=(a,b)=>{const offset=a.positions.length/3;return {positions:a.positions.concat(b.positions),uvs:a.uvs.concat(b.uvs),indices:a.indices.concat(b.indices.map(i=>i+offset))};};
 const canonical=MODEL_ATELIER_CANONICAL_PROJECT.project.modelAtelier.parts;
 const armor=[];
 for(const id of ['right-arm-band','left-wrist-cuff','bodice-stitch-2','right-wrist-0','right-wrist-1','right-wrist-2']){
  const source=canonical.find(p=>p.id===id);if(!source?.path?.length)throw Error('Native armor path missing: '+id);
  const matrix=new THREE.Matrix4().compose(new THREE.Vector3(...source.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...source.rotation)),new THREE.Vector3(...source.scale)),a=new THREE.Vector3(...source.path[0]).applyMatrix4(matrix),b=new THREE.Vector3(...source.path.at(-1)).applyMatrix4(matrix),axis=b.clone().sub(a).normalize(),length=a.distanceTo(b),radius=Math.max(...source.radii)*1.45+.015;
  // Match the armor's diagonal native hem planes, rather than slicing a cuff
  // horizontally through the bent arm. The radial guard excludes nearby torso.
  const distance=(x,y,z)=>new THREE.Vector3(x,y,z).sub(a).dot(axis);
  armor.push([id,[(x,y,z)=>distance(x,y,z),(x,y,z)=>length-distance(x,y,z),(x,y,z)=>{const rel=new THREE.Vector3(x,y,z).sub(a);return radius-rel.addScaledVector(axis,-rel.dot(axis)).length();}]]);
 }
 const lined=[];
 for(const [id,planes] of armor){const part=parts.find(p=>p.id===id);if(!part)continue;const matrix=new THREE.Matrix4().compose(new THREE.Vector3(...part.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...part.rotation)),new THREE.Vector3(...part.scale)),data=structuredClone(part.topologyMesh);
  for(let i=0;i<data.positions.length;i+=3){const p=new THREE.Vector3().fromArray(data.positions,i).applyMatrix4(matrix);data.positions.splice(i,3,...p.toArray().map(v=>+v.toFixed(6)));}
  const lining=atelierAnimeClothShell(skin,planes,.014);if(!lining.indices.length)throw Error('Armor lining is empty: '+id);
  part.topologyMesh=combine(data,lining);part.position=[0,0,0];part.rotation=[0,0,0];part.scale=[1,1,1];lined.push(id);
 }
 model.coverageRefinement={version:'v11.93',underlayer:'festival-shorts',opaque:true,coveredRange:{minimumY:1.98,maximumY:2.84},armorLinings:lined,armorFit:'native diagonal hem planes',skinRetained:true};return scene;
}
const atelierCoverageMaterialBaseV1193=material;
material=function(part){const value=atelierCoverageMaterialBaseV1193(part);if(part.id==='festival-shorts'||['right-arm-band','left-wrist-cuff','bodice-stitch-2'].includes(part.id)||/^right-wrist-\d+$/.test(part.id)){value.transparent=false;value.opacity=1;value.depthWrite=true;value.side=THREE.DoubleSide;}return value;};
