// Frostveil v11.2 original procedural art: no external textures or paid image services.
// 256px repeatable snow/ice/water maps replace flat tiles in the new starter only.
const MAUL_ART_PROFILE='glacial-v2';
MAUL_BATCH_CANONICAL_PROJECT.project.maulVisualStyle=MAUL_ART_PROFILE;
const maulArtEnabled=()=>currentProject?.kind==='maul'&&currentProject.maulVisualStyle===MAUL_ART_PROFILE;
const maulArtTextures=new Map();
const maulArtOldTexture=maulLayoutTexture;
maulLayoutTexture=function(sea=false){
  if(!maulArtEnabled())return maulArtOldTexture(sea);
  const key=sea?'sea':'snow';
  if(maulArtTextures.has(key))return maulArtTextures.get(key);
  const canvas=document.createElement('canvas');canvas.width=canvas.height=256;
  const ctx=canvas.getContext('2d');
  const grad=ctx.createLinearGradient(0,0,256,256);
  if(sea){grad.addColorStop(0,'#23506a');grad.addColorStop(.55,'#32708a');grad.addColorStop(1,'#173f60');}
  else{grad.addColorStop(0,'#e4f2ef');grad.addColorStop(.53,'#c6e0e3');grad.addColorStop(1,'#f2f9f5');}
  ctx.fillStyle=grad;ctx.fillRect(0,0,256,256);
  let seed=sea?0x513F21:0x71F05E;
  const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  // Fine-grain snow and sub-surface water flecks; one canvas per material.
  for(let i=0;i<2700;i++){
    const x=rand()*256,y=rand()*256,w=sea?2+rand()*8:1+rand()*3;
    ctx.fillStyle=sea?(i%3?'#6eb4bd':'#b0dadd'):(i%4?'#ffffff':'#8aabb9');
    ctx.globalAlpha=sea?.10:.14;ctx.fillRect(x,y,w,sea?1:1+rand()*2);
  }
  ctx.globalAlpha=sea?.20:.20;ctx.lineCap='round';
  if(sea){
    for(let i=0;i<85;i++){
      const y=rand()*256,x=rand()*256,length=15+rand()*75;
      ctx.strokeStyle=i%3?'#9fe1df':'#0b344f';ctx.lineWidth=.6+rand()*1.5;
      ctx.beginPath();ctx.moveTo(x,y);ctx.bezierCurveTo(x+length*.25,y-2,x+length*.7,y+3,x+length,y);ctx.stroke();
    }
  }else{
    for(let i=0;i<24;i++){
      const x=rand()*256,y=rand()*256,len=12+rand()*55;
      ctx.strokeStyle=i%3?'#ffffff':'#729eb2';ctx.lineWidth=.6+rand();
      ctx.beginPath();ctx.moveTo(x,y);ctx.quadraticCurveTo(x+len*.43,y-4-rand()*5,x+len,y+rand()*5);ctx.stroke();
    }
    for(let i=0;i<8;i++){
      const x=rand()*256,y=rand()*256;
      ctx.strokeStyle='#7faebb';ctx.lineWidth=.5;ctx.beginPath();ctx.moveTo(x,y);
      ctx.lineTo(x+8+rand()*20,y-9-rand()*15);ctx.lineTo(x+16+rand()*30,y-4-rand()*18);ctx.stroke();
    }
  }
  ctx.globalAlpha=1;
  const texture=new THREE.CanvasTexture(canvas);texture.wrapS=texture.wrapT=THREE.RepeatWrapping;
  texture.repeat.set(sea?7:6,sea?7:6);texture.colorSpace=THREE.SRGBColorSpace;
  texture.anisotropy=Math.min(4,renderer?.capabilities?.getMaxAnisotropy?.()||2);
  maulArtTextures.set(key,texture);return texture;
};
const maulArtOldVisual=maulMakeVisual;
maulMakeVisual=function(kind,level=1){
  const group=maulArtOldVisual(kind,level);
  if(!maulArtEnabled())return group;
  const add=(geo,color,x,y,z,roughness=.78)=>{
    const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color,roughness,metalness:.08,flatShading:true}));
    mesh.position.set(x,y,z);mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);return mesh;
  };
  if(kind==='builder'){
    for(const side of [-1,1]){
      const wing=new THREE.Group();wing.name='MaulBuilderWing'+side;wing.position.set(side*.35,1.02,-.05);group.add(wing);
      const feather=new THREE.Mesh(new THREE.ConeGeometry(.39,1.05,5),new THREE.MeshStandardMaterial({color:'#b8e8ea',emissive:'#397e93',emissiveIntensity:.25,roughness:.55,side:THREE.DoubleSide}));
      feather.rotation.z=side*Math.PI*.46;feather.rotation.x=-.3;feather.position.set(side*.50,.12,-.10);wing.add(feather);
      const blade=new THREE.Mesh(new THREE.BoxGeometry(.68,.055,.19),new THREE.MeshStandardMaterial({color:'#7cd9e9',emissive:'#25677b',emissiveIntensity:.3}));
      blade.position.set(side*.34,-.19,.12);blade.rotation.z=side*.35;wing.add(blade);
    }
    const halo=new THREE.Mesh(new THREE.TorusGeometry(.52,.035,6,28),new THREE.MeshBasicMaterial({color:'#8de4e5',transparent:true,opacity:.72}));
    halo.rotation.x=Math.PI/2;halo.position.y=.2;group.add(halo);
  }
  if(kind==='cliff'){
    add(new THREE.BoxGeometry(1.96,.12,1.96),'#879eaa',0,.78,0);
    add(new THREE.BoxGeometry(1.98,.07,1.98),'#557888',0,1.30,0);
    for(const [x,z,h]of [[-.61,-.6,.55],[.61,.55,.72]]){
      add(new THREE.ConeGeometry(.13,h,5),'#96d6e3',x,2.15+h*.3,z);
    }
  }
  if(kind==='pine'){
    for(const side of [-1,1])add(new THREE.ConeGeometry(.45,.62,5),'#d5eff0',side*.32,2.2,side*.09);
  }
  if(kind==='gate'||kind==='spawn'){
    const ring=new THREE.Mesh(new THREE.TorusGeometry(.87,.035,6,32),new THREE.MeshBasicMaterial({color:kind==='spawn'?'#f2a3b1':'#9af7e0',transparent:true,opacity:.78}));
    ring.position.y=.07;ring.rotation.x=-Math.PI/2;group.add(ring);
  }
  return group;
};
window.SWYRL_ENGINE_MAUL.artStatus=()=>({enabled:maulArtEnabled(),profile:MAUL_ART_PROFILE,textures:[...maulArtTextures.keys()]});
