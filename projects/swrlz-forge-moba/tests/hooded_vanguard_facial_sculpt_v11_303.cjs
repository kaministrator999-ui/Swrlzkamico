// Narrow v11.303 test: real head contour AND front-only 768px UV painting.
// No remote browser or unrelated game/editor suites.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const assert=require('node:assert/strict');
const src=fs.readFileSync(path.join(__dirname,'../runtime/hooded_vanguard_facial_sculpt_v11_303.js'),'utf8');
const draws=[],created=[];
function canvas(w=384,h=384){
 const calls=[];
 const ctx={
  fillStyle:'',strokeStyle:'',lineWidth:1,lineCap:'',
  beginPath(){},stroke(){calls.push('stroke');},fill(){calls.push('fill');},
  fillRect(){calls.push('rect');},moveTo(){},lineTo(){},
  bezierCurveTo(){calls.push('curve');},ellipse(){calls.push('ellipse');},
  createLinearGradient(){return {addColorStop(){}};},
  createRadialGradient(){return {addColorStop(){}};},
  save(){},restore(){},scale(){},
  drawImage(){draws.push('forbidden photo draw');},
 };
 const c={width:w,height:h,getContext(){return ctx;},calls};
 created.push(c);return c;
}
function ribbon(rows,cols,fn,uvfn){
 const g={positions:[],uvs:[],indices:[]};
 for(let i=0;i<=rows;i++)for(let j=0;j<=cols;j++){
  const u=i/rows,v=j/cols,p=fn(u,v),uv=uvfn?uvfn(u,v):[v,u];
  g.positions.push(...p);g.uvs.push(...uv);
  if(i<rows&&j<cols){
   const a=i*(cols+1)+j,b=a+cols+1;
   g.indices.push(a,a+1,b,a+1,b+1,b);
  }
 }
 return g;
}
function join(items){
 const g={positions:[],uvs:[],indices:[]};
 for(const item of items){
  const offset=g.positions.length/3;
  g.positions.push(...item.positions);g.uvs.push(...item.uvs);
  for(const i of item.indices)g.indices.push(i+offset);
 }
 return g;
}
const geom={positions:[0,0,0,1,0,0,0,1,0],indices:[0,1,2],uvs:[0,0,1,0,0,1]};
let baselineScene=null;
const oldFactory=()=>{
 baselineScene={project:{name:'previous',modelAtelier:{
  name:'previous',parts:Array.from({length:17},(_,i)=>({
   id:'vanguard-rebuilt-'+String(i).padStart(2,'0'),name:'Prior '+i,
   topologyMesh:i===1?ribbon(54,96,(u,v)=>[u,v,0]):structuredClone(geom),
   heroPBR:{tile:i===1?'v300:skin':'v300:armor'}
  }))
 }},version:11.302,engine:'old'};
 return baselineScene;
};
const textures=new Map(),atlasses=new Map();
let paints=0;
const context=vm.createContext({
 console,Math,Object,structuredClone,
 se300Canvas:canvas,se300Ribbon:ribbon,se300Join:join,
 se300DrawArtwork:(_img,family,c)=>{paints++;},
 se300InitArt:()=>{if(!atlasses.has('skin'))atlasses.set('skin',canvas());},
 se300Atlases:atlasses,se300MaterialTex:textures,
 se291HeroScene:oldFactory,
 se291OpenHero:()=>true,se291Stats:{successes:1},
 se300Status:{created:11},se301Result:{correctedHands:2,retouchedFamilies:11},
 se302SurfaceStatus:{generatedMapFamilies:11},
 window:{}
});
vm.runInContext(src,context,{timeout:18000});
const built=vm.runInContext('se291HeroScene()',context,{timeout:18000});
assert.equal(built.version,11.303);
const parts=built.project.modelAtelier.parts;
assert.equal(parts.length,17);
assert(parts[1].name.includes('sculpted orbit'));
assert(parts[2].name.includes('contoured upper hairline'));
assert(parts[3].name.includes('eyebrow-clear'));
const head=parts[1].topologyMesh;
assert.equal(head.positions.length/3,81*145);
assert.equal(head.indices.length/3,80*144*2);
assert.equal(head.uvs.length,head.positions.length/3*2);
for(const i of [1,2,3]){
 const g=parts[i].topologyMesh;
 assert(g.positions.every(Number.isFinite),parts[i].name);
 assert(g.uvs.every(n=>n>=0&&n<=1&&Number.isFinite(n)),parts[i].name);
 assert(g.indices.every(n=>Number.isInteger(n)&&n>=0&&n<g.positions.length/3));
}
for(let i of [0,4,5,6,7,8,9,10,11,12,13,14,15,16]){
 assert.deepEqual(parts[i].topologyMesh,geom,'no edits to non-face/hair parts '+i);
 assert.equal(parts[i].name,'Prior '+i,'part name preserved '+i);
}
function headAt(t,v){
 return vm.runInContext('se303HeadSurface('+t+','+v+')',context);
}
function baseZ(t){const lat=(t-.5)*Math.PI;return .045+.219*Math.pow(Math.max(.004,Math.cos(lat)),.65);}
const nose=headAt(.421,.5);
assert(nose[2]-baseZ(.421)>.056,'nose tip has actual forward relief');
const cheek=headAt(.495,.59);
assert(cheek[2]>.045,'3D cheeks exist');
const lip=headAt(.30,.5),adjacent=headAt(.30,.54);
assert(lip[2]>.045,'modeled mouth relief exists');
assert(lip[2]>adjacent[2],'lips actually project from base face');
const top=vm.runInContext('se303HeadSurface(1,.5)',context);
assert(top[1]>4.52,'forehead reaches scalp');
const img=canvas(768,768); // mimic cached native texture
textures.set('skin',{image:img,needsUpdate:false});
vm.runInContext('se300InitArt()',context,{timeout:18000});
const applied=atlasses.get('skin');
assert.equal(applied.width,768,'high-res UV face texture');
assert.equal(applied.height,768);
assert.equal(textures.get('skin').image,applied,'bind native texture');
assert.equal(textures.get('skin').needsUpdate,true);
assert(applied.calls.filter(s=>s==='ellipse').length>=14,
 'detailed eyes with iris, pupil and catchlight');
assert(applied.calls.filter(s=>s==='curve').length>=25,
 'nose, brow, eyelid and lips require deliberate paint');
assert.equal(draws.length,0,'no photo pasted onto the face');
const c1=applied;
vm.runInContext('se300InitArt()',context);
assert.equal(atlasses.get('skin'),c1,'share single high-res atlas');
const status=vm.runInContext('window.SWYRL_ENGINE_HOODED_VANGUARD.status()',context);
assert.equal(status.faceAtlasPixels,768);
assert.equal(status.faceVertexCount,81*145);
assert.equal(status.paintedAtlasReady,true);
assert.equal(status.unchangedArmorAndHands,true);
console.log('VANGUARD_REAL_FACE_SCULPT_UV_OK',JSON.stringify({
 version:'v11.303',editableParts:17,faceVertices:status.faceVertexCount,
 eyeDetails:applied.calls.filter(s=>s==='ellipse').length,
 faceBezierDetails:applied.calls.filter(s=>s==='curve').length,
 textureResolution:768,photographPastes:draws.length,
 armorAndHandsPreserved:true,ownerVisualAcceptance:false
}));
