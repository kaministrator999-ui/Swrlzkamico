// Original terrain for the cooperative Maul silhouette: snow bays, cliff masses
// and a southern harbor. The published tile-board art remains available.
const MAUL_LAYOUT_TYPES=['maul-snowfield','maul-water','maul-route-turn'];
const MAUL_LAYOUT_COLORS=['#e46360','#5a86ed','#56d7ce','#efa550','#e1d26c','#b48cdd','#6cc382','#ccd5de','#e89bc7'];
let maulSnowTexture=null,maulSeaTexture=null;
function maulLayoutTexture(sea=false){
  if(sea?maulSeaTexture:maulSnowTexture)return sea?maulSeaTexture:maulSnowTexture;
  const canvas=document.createElement('canvas');canvas.width=128;canvas.height=128;const ctx=canvas.getContext('2d');ctx.fillStyle=sea?'#244c70':'#c8dfe6';ctx.fillRect(0,0,128,128);
  let seed=171;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  for(let i=0;i<1800;i++){ctx.fillStyle=sea?(i%3?'#315e80':'#1f4263'):(i%3?'#d9e8ea':'#abc7d2');ctx.globalAlpha=sea?.24:.14;const x=rand()*128,y=rand()*128;ctx.fillRect(x,y,sea?3+rand()*12:1+rand()*4,sea?1:1+rand()*3);}
  const texture=new THREE.CanvasTexture(canvas);texture.wrapS=texture.wrapT=THREE.RepeatWrapping;texture.repeat.set(4,4);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=2;if(sea)maulSeaTexture=texture;else maulSnowTexture=texture;return texture;
}
function maulLayoutSurface(kind){
  const object=new THREE.Group(),water=kind==='water',mesh=new THREE.Mesh(new THREE.BoxGeometry(2,water?.15:.24,2),new THREE.MeshStandardMaterial({color:water?'#86b4d1':'#f3ffff',map:maulLayoutTexture(water),roughness:water?.45:1,metalness:water?.2:0}));
  mesh.position.y=water?-.28:-.15;mesh.receiveShadow=true;object.add(mesh);return object;
}
function maulLayoutPrefab(type,position=[0,0,0],baked=true,name=null){const kind=type.slice(5),object=kind==='route-turn'?maulMakeVisual('gate'):maulLayoutSurface(kind==='water'?'water':'snow');object.position.fromArray(position);return markActor(object,type,{name:name||'Frostveil '+kind,baked,folder:kind==='route-turn'?'Maul/Gameplay':'Maul/Terrain',components:['Transform','Scene','StaticMesh'],blueprintClass:'Maul/'+kind,colliderRadius:0,role:kind,tags:['maul','classic-maul']});}
const maulLayoutPreviousVisual=maulMakeVisual;
maulMakeVisual=function(kind,level=1){
  if(currentProject?.maulLayout!=='classic-v2')return maulLayoutPreviousVisual(kind,level);
  const group=new THREE.Group(),material=color=>new THREE.MeshStandardMaterial({color,roughness:.95,flatShading:true});
  const box=(size,color,p=[0,0,0])=>{const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),material(color));mesh.position.fromArray(p);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);return mesh;};
  if(kind==='cliff'){box([2,2.1,2],'#2c4556',[0,.9,0]);box([1.96,.18,1.96],'#c1dbe4',[0,2.02,0]);box([2.02,.10,2.02],'#557787',[0,.45,0]);return group;}
  if(kind==='exit'){
    const hull=new THREE.Mesh(new THREE.CylinderGeometry(.75,1.25,3.4,6),material('#766049'));hull.rotation.x=Math.PI/2;hull.scale.z=.6;hull.position.y=.62;group.add(hull);box([1.75,.14,3.2],'#c6aa7e',[0,1,0]);
    const mast=new THREE.Mesh(new THREE.CylinderGeometry(.065,.09,3.8,7),material('#c7b994'));mast.position.y=2.1;group.add(mast);box([1.6,1.6,.055],'#eaf2ef',[.45,2.5,0]);box([.5,.35,.06],'#6bd8bd',[.4,3.8,0]);
    const halo=new THREE.Mesh(new THREE.TorusGeometry(1.75,.055,6,32),new THREE.MeshBasicMaterial({color:'#9dedce'}));halo.rotation.x=-Math.PI/2;halo.position.y=.055;group.add(halo);return group;
  }
  const original=maulLayoutPreviousVisual(kind,level);if(kind==='banner')original.traverse(n=>{if(n.isMesh&&n.geometry?.type==='BoxGeometry')n.name='MaulCloth';});return original;
};
function maulLayoutTint(actor){const sector=actor.userData.maul?.sector;if(!Number.isInteger(sector)||sector<0||sector>8)return;const color=MAUL_LAYOUT_COLORS[sector];actor.traverse(n=>{if(n.name==='BuilderRobe'||n.name==='MaulCloth'||actor.userData.actorType==='maul-builder'&&n.geometry?.type==='ConeGeometry')n.material?.color.set(color);});}
for(const type of MAUL_LAYOUT_TYPES)ASSET_LIBRARY.push({id:type,name:type==='maul-water'?'Maul harbor water':type==='maul-route-turn'?'Maul lower route turn':'Maul continuous snowfield',path:'/Engine/Maul/Terrain',desc:'Native terrain and route pieces for the classic cooperative Maul map.'});
