// §E v11.282 · Rock Cliff Hand revision: stone is the ANATOMY, not armor.
// Replaces v11.281's visibly smooth underlying hand with closed, faceted,
// interlocking rock masses covering palm/back/sides/thumb/fingers/wrist.
// Native Model Atelier topologyMesh, original 17-joint rig and save schema.
const se282PreviousRockScene=se281RockScene;
const se282Stone=Object.freeze({
 bed:'#57515a',slate:'#716b73',shade:'#494650',ridge:'#8a838b',
 pale:'#a49ca4',deep:'#393741',basalt:'#625d65',
 amber:'#ffb34d',ember:'#fbd17a'
});
// Hard-edged triangles deliberately do not share vertex normals: the silhouette
// and shading read as a fractured, angular cliff instead of smooth armor.
function se282Mesh(){
 const positions=[],uvs=[],indices=[];
 const addTri=(a,b,c)=>{
  for(const p of [a,b,c]){
   if(!p.every(Number.isFinite))throw Error('Invalid cliff-rock vertex');
   positions.push(...p.map(v=>+v.toFixed(5)));uvs.push(p[0]*.32,p[1]*.32);
  }
  const i=positions.length/3;indices.push(i-3,i-2,i-1);
 };
 const quad=(a,b,c,d)=>{addTri(a,b,c);addTri(c,b,d);};
 return {addTri,quad,result:()=>({positions,uvs,indices})};
}
const se282Noise=(s,k)=>Math.sin(s*12.9898+k*78.233)*.5+
 Math.cos(s*2.71828+k*19.139)*.27;
function se282RingColumn(sections,seed=1,sides=11){
 const mesh=se282Mesh(),rings=[];
 for(let j=0;j<sections.length;j++){
  const {x,y,z,rx,rz}=sections[j];
  rings.push(Array.from({length:sides},(_,i)=>{
   const a=(i+.065*Math.sin(seed+i*2.91))*2*Math.PI/sides;
   const variability=1+.11*se282Noise(seed+i*.23,j+.25)+.028*Math.sin(j*3+i*3);
   return [x+Math.cos(a)*rx*variability,
    y+(j===0||j===sections.length-1?0:.012*se282Noise(seed,j*sides+i)),
    z+Math.sin(a)*rz*variability];
  }));
 }
 for(let j=0;j<rings.length-1;j++)for(let i=0;i<sides;i++){
  const next=(i+1)%sides;
  mesh.quad(rings[j][i],rings[j+1][i],rings[j][next],rings[j+1][next]);
 }
 const cap=(ring,top)=>{
  const center=[0,0,0];
  for(const p of ring)for(let i=0;i<3;i++)center[i]+=p[i]/ring.length;
  for(let i=0;i<sides;i++){
   const next=(i+1)%sides;
   if(top)mesh.addTri(center,ring[next],ring[i]);
   else mesh.addTri(center,ring[i],ring[next]);
  }
 };
 cap(rings[0],false);cap(rings[rings.length-1],true);
 return mesh.result();
}
// A solid, chiseled stone joint, not a pair of floating front/back patches.
// Orientation is along any finger/thumb bone; each segment seals all 360°.
function se282StoneSegment(a,b,rStart,rEnd,seed,flatten=1){
 const mesh=se282Mesh(),n=9,axis=new THREE.Vector3(b[0]-a[0],b[1]-a[1],b[2]-a[2]).normalize();
 if(axis.lengthSq()<.01)throw Error('Zero-length stone finger segment');
 const ref=Math.abs(axis.z)>.87?new THREE.Vector3(0,1,0):new THREE.Vector3(0,0,1);
 const u=new THREE.Vector3().crossVectors(axis,ref).normalize();
 const v=new THREE.Vector3().crossVectors(axis,u).normalize();
 const sections=[{t:0,bulge:.80},{t:.16,bulge:1.10},
  {t:.52,bulge:1.17},{t:.84,bulge:1.04},{t:1,bulge:.76}];
 const rings=sections.map(({t,bulge},j)=>
  Array.from({length:n},(_,k)=>{
   const theta=2*Math.PI*(k+.13*Math.sin(seed))/n;
   const shape=1+.14*se282Noise(seed+k*.2,j+.3);
   const radius=(rStart*(1-t)+rEnd*t)*bulge*shape;
   return [
    a[0]+(b[0]-a[0])*t+radius*(u.x*Math.cos(theta)+v.x*Math.sin(theta)*flatten),
    a[1]+(b[1]-a[1])*t+radius*(u.y*Math.cos(theta)+v.y*Math.sin(theta)*flatten),
    a[2]+(b[2]-a[2])*t+radius*(u.z*Math.cos(theta)+v.z*Math.sin(theta)*flatten)
   ];
  }));
 for(let j=0;j<rings.length-1;j++)for(let i=0;i<n;i++){
  const k=(i+1)%n;
  // Basis (u,v) is oriented right-handed with axis; check exterior winding.
  mesh.quad(rings[j][i],rings[j][k],rings[j+1][i],rings[j+1][k]);
 }
 const center=(ring)=>ring[0].map((_,i)=>ring.reduce((sum,p)=>sum+p[i],0)/ring.length);
 for(let i=0;i<n;i++){
  const k=(i+1)%n;
  mesh.addTri(center(rings[0]),rings[0][k],rings[0][i]);
  mesh.addTri(center(rings.at(-1)),rings.at(-1)[i],rings.at(-1)[k]);
 }
 return mesh.result();
}
// Raised planar stone OUTCROPPINGS, thick enough to merge visibly with the
// solid cliff palm, rather than resembling thin plates on a glove.
function se282CliffSlab({x,y,z,wx,hy,depth,side,seed,angle=0}){
 const mesh=se282Mesh(),n=8;
 const cos=Math.cos(angle),sin=Math.sin(angle);
 const layers=[
  {r:.77,z:-side*depth*.55},
  {r:1.06,z:-side*depth*.18},
  {r:.89,z:side*depth*.67}
 ];
 const rings=layers.map(({r,z:offset},j)=>Array.from({length:n},(_,i)=>{
  const t=2*Math.PI*i/n;
  const noise=1+.15*se282Noise(seed,i);
  const lx=Math.cos(t)*wx*r*noise,ly=Math.sin(t)*hy*r*noise;
  return [x+lx*cos-ly*sin,y+lx*sin+ly*cos,
   z+offset+.018*se282Noise(seed+j,i)];
 }));
 for(let j=0;j<2;j++)for(let i=0;i<n;i++){
  const k=(i+1)%n;
  mesh.quad(rings[j][i],rings[j][k],rings[j+1][i],rings[j+1][k]);
 }
 const c=[x,y,z+side*depth*.79];
 for(let i=0;i<n;i++){
  const k=(i+1)%n;
  mesh.addTri(c,rings[2][i],rings[2][k]);
  mesh.addTri(rings[0][k],[x,y,z-side*depth*.60],rings[0][i]);
 }
 return mesh.result();
}
function se282FullRockScene(){
 const scene=se282PreviousRockScene();
 const m=scene.project.modelAtelier,rig=m.rigging,C=se282Stone;
 if(!se220RigValidate(rig))throw Error('Cliff hand requires the native 17-bone rig.');
 const parts=[];
 function add(name,group,color,topology,material='silk'){
  parts.push({id:'cliff-hand-'+String(parts.length).padStart(3,'0'),
   name,kind:'topologyMesh',position:[0,0,0],rotation:[0,0,0],
   scale:[1,1,1],color,material,group,topologyMesh:topology});
 }
 function line(name,group,path,r=.011,hot=false){
  add(name,group,hot?C.ember:C.amber,se281CrackTopology(path,r),'emissive');
 }
 const colors=[C.bed,C.slate,C.shade,C.ridge,C.basalt,C.pale];
 // The hand core IS a large watertight angular boulder from wrist to knuckles.
 // No organic/glove surface is retained in the visible model at all.
 add('Cliff foundation · entire faceted palm and deep jagged sides',
  'Rock foundation / no smooth skin',C.bed,se282RingColumn([
  {x:0,y:.56,z:0,rx:.30,rz:.23},
  {x:0,y:.76,z:0,rx:.37,rz:.28},
  {x:0,y:.98,z:-.015,rx:.37,rz:.26},
  {x:0,y:1.23,z:0,rx:.42,rz:.28},
  {x:-.01,y:1.45,z:0,rx:.59,rz:.315},
  {x:.01,y:1.70,z:0,rx:.67,rz:.35},
  {x:0,y:1.92,z:-.006,rx:.65,rz:.34},
  {x:0,y:2.14,z:-.016,rx:.59,rz:.30},
  {x:0,y:2.245,z:0,rx:.53,rz:.26}
 ],66,12));
 // Big overlapping cliff strata bury the entire front, back and side walls.
 const palmSlabs=[
  // x, y, breadth, height, angle, alternate color. Coverage overlaps.
  [-.28,1.18,.30,.31,.14,0],[.25,1.16,.28,.29,-.25,2],
  [-.34,1.44,.33,.32,.18,3],[.22,1.49,.36,.34,-.27,1],
  [-.19,1.76,.41,.35,-.11,4],[.32,1.78,.33,.35,.24,5],
  [-.33,2.04,.28,.28,-.16,1],[.24,2.07,.33,.27,.14,0],
  [-.05,1.48,.30,.34,.38,3],[.07,1.90,.31,.25,-.26,2]
 ];
 for(const side of [-1,1]){
  const label=side<0?'Back':'Palm';
  for(const [i,[x,y,wx,hy,angle,c]] of palmSlabs.entries()){
   const depth=.18+.05*(i%3===0);
   const centerZ=side*(y>2.0?.27:y<1.3?.265:.315);
   add(label+' · cliff stratum '+(i+1),
    label+' / cliff stone strata',colors[(c+(side>0?2:0))%colors.length],
    se282CliffSlab({x:x+(side>0?.013:0),y,z:centerZ,wx,hy,depth,side,
      seed:13+i+side*27,angle:angle*(side>0?-1:1)}));
  }
 }
 // Thick overlapping polygonal side ridges: lateral viewing angles no longer
 // reveal an uncovered hand-shaped center.
 for(const sign of [-1,1])for(let j=0;j<5;j++){
  const y=1.0+j*.245,full=(y>1.35&&y<2.05),x=sign*(full?.59:.36);
  const pos=[x,y,.009*(j%2?1:-1)];
  const dir=[x+sign*.026,y+.25,.017];
  add((sign<0?'Thumb':'Little')+' side · overhanging cliff block '+(j+1),
   'Side / solid jagged edges',colors[(j+2+(sign>0?2:0))%colors.length],
   se282StoneSegment(pos,dir,full?.245:.19,full?.19:.165,130+j+sign*15));
 }
 // Finger shafts are CLOSED rocky prisms all around, not dorsal armor strips.
 // Their proximal ends overlap the palm; joint rock seams remain bendable.
 const segmentRanges=[[ -.035,.485],[.475,.79],[.775,1.035]];
 for(const [fi,f] of rig.digits.entries()){
  const h=f.to-f.from;
  for(const [si,[start,end]] of segmentRanges.entries()){
   const t0=Math.max(-.035,start),t1=end;
   const point=t=>[f.x+f.splay*t,f.from+h*t,f.z+.006*t];
   const radius=[f.r*1.53,f.r*1.39,f.r*1.27][si];
   add('Finger '+f.name+' · solid '+['root','middle','tip'][si]+' cliff rock',
    'Fingers / solid '+f.name+' stone',
    colors[(fi*2+si+1)%colors.length],
    se282StoneSegment(point(t0),point(t1),radius,
     radius*(si===2?.79:.93),210+fi*18+si,1.02));
   // A small jagged side ridge breaks each finger's smooth cylinder outline.
   const sgn=fi<2?-1:1,center=point((t0+t1)*.49);
   add('Finger '+f.name+' · jutting outer rock '+(si+1),
    'Fingers / outer cliff chips',colors[(fi+si+4)%colors.length],
    se282CliffSlab({x:center[0]+sgn*radius*.87,y:center[1],
     z:center[2],wx:radius*.66,hy:h*(t1-t0)*.33,
     depth:radius*.9,side:sgn,seed:300+fi*10+si,angle:sgn*.25}));
  }
  // Glowing cracks are recess markers between massive rock finger sections.
  for(const [j,t] of [.485,.79].entries()){
   const p=[f.x+f.splay*t,f.from+h*t,f.z];
   const radius=f.r*(j===0?1.42:1.20);
   line('Finger '+f.name+' · bright knuckle fault '+(j+1),
    'Energy / finger fault lines',
    [[p[0]-radius*.65,p[1],p[2]+radius*.94],
     [p[0],p[1]+.015,p[2]+radius*1.06],
     [p[0]+radius*.66,p[1]-.008,p[2]+radius*.93]],.012);
   line('Finger '+f.name+' · back knuckle fault '+(j+1),
    'Energy / finger fault lines',
    [[p[0]-radius*.67,p[1],p[2]-radius*.95],
     [p[0],p[1]+.01,p[2]-radius*1.07],
     [p[0]+radius*.67,p[1],p[2]-radius*.95]],.009);
  }
 }
 // Full stone thumb shell follows genuine angled thumb bones, root to tip.
 const thumb=[
  [-.51,1.52,.11],[-.83,1.785,.19],
  [-1.005,1.94,.22],[-1.126,2.07,.235]
 ];
 for(let i=0;i<3;i++){
  add('Thumb · entire '+['base','middle','tip'][i]+' cliff stone',
   'Thumb / full 360-degree cliff blocks',colors[(i+2)%colors.length],
   se282StoneSegment(thumb[i],thumb[i+1],.245-i*.034,.210-i*.032,415+i,1.05));
 }
 for(const [i,p] of thumb.slice(1,-1).entries()){
  line('Thumb · molten flex seam '+(i+1),'Energy / thumb cracks',
   [[p[0]-.10,p[1]-.045,p[2]+.162],
    [p[0]-.025,p[1]+.025,p[2]+.18],
    [p[0]+.077,p[1]+.04,p[2]+.148]],.011,true);
 }
 // Wrist is the rocky root, not a narrow bracelet. Layers overlap both side
 // walls and continue down through the root rather than ending at a cuff.
 for(const [i,y] of [.62,.85,1.10].entries()){
  for(const side of [-1,1]){
   add('Wrist root · '+(side<0?'back':'front')+' broken basalt '+(i+1),
    'Wrist / rising cliff strata',colors[(i+2+(side>0?1:0))%colors.length],
    se282CliffSlab({x:(i%2?-.04:.05),y,z:side*(.255+i*.013),
      wx:.38+i*.015,hy:.155,depth:.20,side,seed:505+i+side*10,angle:.12*(i-1)}));
  }
  line('Wrist · transverse magma fault '+(i+1),'Energy / wrist faults',
   [[-.22,y+.07,.37],[-.055,y+.093,.381],[.115,y+.081,.386],
     [.27,y+.065,.36]],.012);
 }
 // Angular branching fissures across the outer stone faces, not the underlying
 // organic skin; intentionally sparse so the hand remains visibly solid rock.
 const cracks=[
  {side:-1,path:[[-.33,2.06,-.446],[-.21,1.89,-.465],[-.10,1.77,-.48],
    [-.22,1.64,-.470],[-.15,1.45,-.47]]},
  {side:-1,path:[[-.10,1.78,-.483],[.085,1.81,-.479],
    [.17,1.67,-.488],[.34,1.57,-.474]]},
  {side:1,path:[[-.30,2.02,.461],[-.17,1.86,.473],
    [-.23,1.71,.48],[.0,1.58,.487]]},
  {side:1,path:[[.28,2.02,.444],[.14,1.84,.476],
    [.23,1.64,.48],[.11,1.48,.466]]}
 ];
 for(const [i,c] of cracks.entries()){
  line((c.side<0?'Back':'Palm')+' · lava crevice '+(i+1),
    'Energy / branching rock fractures',c.path,.013,i===1);
 }
 if(parts.length>230)throw Error('Cliff rock part budget exceeded: '+parts.length);
 if(parts.some(p=>p.organicSurface||p.name.includes('Underlying')))
  throw Error('Cliff Hand must not expose smooth organic core.');
 m.name='Rocky Anime Hand · Emberstone';
 m.parts=parts;
 m.meshGroups=[...new Set(parts.map(p=>p.group))].map((group,i)=>({
   id:'cliff-rock-group-'+i,name:group,
   members:parts.filter(p=>p.group===group).map(p=>p.id)
 })).filter(g=>g.members.length>=2);
 m.reference='Cliff-rock revision: solid faceted 360° stone palm, fingers, wrist and thumb, no smooth exposed glove. Amber fault-line geometry. Editable native 17-bone rig intact.';
 scene.project.name=m.name;
 scene.engine='§wyrl§ Engine · Maker v11.282';scene.version=11.282;
 return scene;
}
// Use v11.281's existing starter card, route, animation UI and save machinery.
se281RockScene=se282FullRockScene;
window.SWYRL_ENGINE_ROCK_CLIFF_HAND=Object.freeze({
 scene:se282FullRockScene,
 status:()=>({registered:typeof se281OpenRockyHand==='function',
  noOrganicCore:true,sourceVersion:'v11.282'})
});
