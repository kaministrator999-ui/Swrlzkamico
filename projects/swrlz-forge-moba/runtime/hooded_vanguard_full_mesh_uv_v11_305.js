// §E v11.305 · whole-character geometry and true surface-driven UV pass.
// Replaces only freshly created Hooded Vanguard native starter geometry.
// Historical editor, saves, §C, VR, other models and prior release patches stay.
// Deliberately fitted mesh and UVs are constructed in the SAME surface factory.
const se305State={version:'v11.305',rebuiltParts:0,vertices:0,triangles:0,
 nativeUVs:true,frontBackSeams:true,correctedWristAxes:true,
 repairedEars:true,ownerVisualAcceptance:false};
function se305Clamp(v,a=0,b=1){return Math.max(a,Math.min(b,v));}
function se305Mix(a,b,t){return a+(b-a)*t;}
function se305Vec(a,b,s){return a.map((x,i)=>se305Mix(x,b[i],s));}
function se305Unit(a){const l=Math.hypot(...a)||1;return a.map(v=>v/l);}
function se305Sweep(a,b,sections,radial,radii,uv=(u,v)=>[v,u]){
 const tangent=se305Unit(b.map((v,i)=>v-a[i]));
 let cross=se305Unit([-tangent[1],tangent[0],0]);
 if(Math.hypot(cross[0],cross[1])<.001)cross=[1,0,0];
 const other=se305Unit([
  tangent[1]*cross[2]-tangent[2]*cross[1],
  tangent[2]*cross[0]-tangent[0]*cross[2],
  tangent[0]*cross[1]-tangent[1]*cross[0]]);
 return se300Ribbon(sections,radial,(u,v)=>{
  const c=se305Vec(a,b,u),phase=v*2*Math.PI,
   [rx,rz]=radii(u),ca=Math.cos(phase),sa=Math.sin(phase);
  return c.map((p,i)=>p+cross[i]*rx*ca+other[i]*rz*sa);
 },uv);
}
function se305Combine(shapes){return se300Join(shapes);}
function se305MiterBand(rows,cols,position,uv){
 return se300Ribbon(rows,cols,position,uv||((u,v)=>[v,u]));
}
function se305Body(){
 const parts=[];
 // Closed radial UV seam is at the back, not a repeated front/back sticker.
 parts.push(se305MiterBand(52,80,(u,v)=>{
  const y=2.34+1.37*u,ang=(v-.5)*Math.PI*2;
  const chest=Math.exp(-Math.pow((u-.62)/.35,2));
  const neck=se305Clamp((u-.79)/.21);
  const rx=(.309+.102*chest)*(1-.45*neck);
  const rz=(.202+.026*chest)*(1-.29*neck);
  return [rx*Math.sin(ang),y,-.005+rz*Math.cos(ang)];
 }));
 for(const side of [-1,1]){
  // Sleeve/forearm segments are radial lofts, not planar UV projection.
  const shoulder=[side*.345,3.43,-.012],
    elbow=[side*.635,3.145,.017],
    wrist=[side*.883,2.727,.055];
  parts.push(se305Sweep(shoulder,elbow,23,32,u=>[
   .136-.022*u+.012*Math.sin(Math.PI*u),.126-.020*u]));
  parts.push(se305Sweep(elbow,wrist,27,32,u=>[
   .108-.030*u+.009*Math.sin(Math.PI*u),.100-.027*u]));
  // Subtle shoulder and elbow fabric caps hide hard loft segment joins.
  parts.push(se305Sweep(se305Vec(shoulder,elbow,.82),
   se305Vec(elbow,wrist,.14),9,32,u=>[
   .113-.012*u,.101-.010*u]));
  const hip=[side*.184,2.37,-.023],
   knee=[side*.239,1.32,.012],
   ankle=[side*.257,.32,.033];
  parts.push(se305Sweep(hip,knee,29,36,u=>[
   .164-.037*u+.009*Math.sin(Math.PI*u),
   .146-.029*u]));
  parts.push(se305Sweep(knee,ankle,26,32,u=>[
   .129-.037*u,.118-.025*u]));
 }
 return se305Combine(parts);
}
function se305Ear(side){
 // Ears are folded cartilage surfaces integrated in the FACE PART, not lumps.
 // Their UVs sample the unpainted lateral skin, never the front portrait.
 return se305MiterBand(26,17,(u,v)=>{
  const phi=(u-.5)*Math.PI,flare=Math.sin(Math.PI*v);
  const outer=.039+v*.016,inner=.021*(1-v);
  const x=side*(.257+outer*Math.sin(Math.PI*u));
  const y=4.187+.155*Math.sin(phi)-.025*v;
  const z=.018+outer*Math.cos(phi)+.018*flare-.011*Math.sin(3*Math.PI*v);
  return [x,y,z-inner*Math.sin(Math.PI*u)];
 },(u,v)=>[side<0?.075+.075*v:.85+.075*v,.43+.21*u]);
}
function se305Face(){
 // Preserve accurate v11.303 facial anatomy and its aligned portrait map.
 return se305Combine([
  se305MiterBand(80,144,se303HeadSurface),
  se305Ear(-1),se305Ear(1)
 ]);
}
function se305Hood(){
 const bits=[];
 // Draped upper canopy is open at the FRONT and rounded in back. No helmet.
 bits.push(se305MiterBand(38,84,(u,v)=>{
  const angle=.77+(2*Math.PI-1.54)*v;
  const radius=.363*Math.sin((.24+.76*u)*Math.PI*.5);
  const x=radius*Math.sin(angle);
  const front=Math.pow(Math.max(0,Math.cos(angle)),6);
  const y=4.665-.40*u*u+.065*u*u*front;
  return [x,y,-.048+.292*(radius/.363)*Math.cos(angle)];
 },(u,v)=>[.06+.88*v,.05+.86*u]));
 // Back mantle has fabric fullness over the shoulders instead of a bucket.
 bits.push(se305MiterBand(32,72,(u,v)=>{
  const angle=.73+(2*Math.PI-1.46)*v;
  const width=.365+.058*u+.018*Math.sin(Math.PI*u);
  return [width*Math.sin(angle),4.31-.67*u,
   -.062+(.286+.015*u)*Math.cos(angle)-.012*Math.sin(u*9)];
 },(u,v)=>[.09+.81*v,.08+.83*u]));
 // Actual forward-opening curved cloth binding, matching the painted hem UV.
 bits.push(se305MiterBand(7,56,(u,v)=>{
  const x=(v-.5)*.59,arch=Math.sqrt(Math.max(0,1-Math.pow((v-.5)*2,2)));
  return [x,4.402+.123*arch-.020*u,
   .237+.021*arch+.013*u];
 },(u,v)=>[.022+.075*u,.055+.88*v]));
 for(const s of [-1,1])bits.push(se305MiterBand(32,6,(u,v)=>{
  return [s*(.298+.021*Math.sin(Math.PI*u)),3.89+.54*u,
   .177+.027*u+.015*v];
 },(u,v)=>[.025+.067*v,.10+.79*u]));
 return se305Combine(bits);
}
function se305Scarf(){
 const neck=se305MiterBand(30,70,(u,v)=>{
  const a=2*Math.PI*(v-.5),bulge=.036*Math.sin(3*Math.PI*u);
  const rad=.184+bulge;
  return [rad*Math.sin(a),3.56+.29*u+.012*Math.sin(4*a+10*u),
   .045+(.164+bulge*.45)*Math.cos(a)];
 });
 return neck;
}
function se305Shawl(){
 // Two overlapping diagonal wraps; topology itself creates cloth volume.
 const cloth=[];
 for(const side of [-1,1])cloth.push(se305MiterBand(38,42,(u,v)=>{
  const t=u,s=v,wide=.36*(1-.56*u),offset=side*.107*(1-u);
  const x=(s-.5)*2*wide+offset,
    y=3.65-u*(.43+.14*(1-Math.abs(2*s-1)))+
     .033*Math.sin(2*Math.PI*s)*u;
  const z=.245+.036*Math.sin(Math.PI*s)+.026*Math.sin(Math.PI*u*2+2*s)
    +(side>0?.011:0);
  return [x,y,z];
 },(u,v)=>[.05+.9*v,.04+.91*u]));
 return se305Combine(cloth);
}
function se305Armor(current){
 // Preserve the owner's decent armor form, add a real back layer and bevel
 // around its existing front *without moving* its original contour/UV.
 const front=current,back={positions:[],uvs:[...front.uvs],indices:[]};
 for(let i=0;i<front.positions.length;i+=3)
  back.positions.push(front.positions[i],front.positions[i+1],
   front.positions[i+2]-.024);
 for(let i=0;i<front.indices.length;i+=3)
  back.indices.push(front.indices[i],front.indices[i+2],front.indices[i+1]);
 return se305Combine([front,back]);
}
function se305Cloth(side){
 const front=se305MiterBand(64,40,(u,v)=>{
  const radius=.245+.10*u+.049*Math.sin(Math.PI*u),h=(v-.5)*2;
  const shift=.068*Math.sin(u*Math.PI*1.5);
  const x=side*(.315+.092*u+shift)+h*radius,
   y=2.52-2.29*u+.038*u*v,
   z=-.117-.17*u+.055*Math.sin(Math.PI*u*1.5)+
    .066*Math.cos(h*Math.PI+u*3.5);
  return [x,y,z];
 });
 const rear=se305MiterBand(64,40,(u,v)=>{
  const radius=.245+.10*u+.049*Math.sin(Math.PI*u),h=(v-.5)*2;
  const shift=.068*Math.sin(u*Math.PI*1.5);
  return [
   side*(.315+.092*u+shift)+h*radius,
   2.52-2.29*u+.038*u*v,
   -.131-.17*u+.055*Math.sin(Math.PI*u*1.5)+
    .066*Math.cos(h*Math.PI+u*3.5)];
 },(u,v)=>[.065+.87*v,.05+.9*u]);
 return se305Combine([front,rear]);
}
function se305Belt(){
 const ring=se305MiterBand(10,80,(u,v)=>{
  const a=(v-.5)*Math.PI*2;
  const r=.324+.014*Math.sin(Math.PI*u);
  return [r*Math.sin(a),2.465+.133*u,
   -.004+.239*Math.cos(a)];
 });
 // Buckle form follows the curved front belt, preserving editability.
 const buckle=se305MiterBand(10,14,(u,v)=>{
  const x=(v-.5)*.126,depth=.256-.011*Math.pow(x/.063,2);
  return [x,2.458+.142*u,depth+.009*Math.sin(Math.PI*u)];
 },(u,v)=>[.43+.14*v,.34+.22*u]);
 return se305Combine([ring,buckle]);
}
function se305Glove(side){
 // For real neutral wrists, construct the hand ALONG the forearm, rather
 // than rotating a vertically posed SDF mitten around an arbitrary pivot.
 const wrist=[side*.878,2.738,.059];
 const direction=se305Unit([side*.27,-.43,.02]);
 const lateral=se305Unit([-.43,-side*.27,0]);
 const at=(distance,l=0,z=0)=>[
  wrist[0]+direction[0]*distance+lateral[0]*l,
  wrist[1]+direction[1]*distance+lateral[1]*l,
  wrist[2]+direction[2]*distance+z];
 const forms=[];
 forms.push(se305Sweep(at(-.04),at(.114),23,32,u=>[
  .073+.019*Math.sin(Math.PI*u),.055+.009*Math.sin(Math.PI*u)]));
 // Four anatomically distinct tapered fingers, following forearm direction.
 const lengths=[.089,.111,.101,.079];
 for(let i=0;i<4;i++){
  const l=(i-1.5)*.033,from=at(.099,l,.008),
    to=at(.116+lengths[i],l*.92,.016);
  forms.push(se305Sweep(from,to,17,14,u=>[
   .0155*(1-.49*u)+.002*Math.sin(Math.PI*u),
   .016*(1-.45*u)]));
 }
 // Thumb emerges inward/frontward with a natural resting bend.
 const thBase=at(.042,side*.071,.041),
  thJoint=at(.116,side*.107,.077),
  thTip=at(.155,side*.114,.105);
 forms.push(se305Sweep(thBase,thJoint,12,14,u=>[
  .024-.005*u,.021-.003*u]));
 forms.push(se305Sweep(thJoint,thTip,11,14,u=>[
  .019-.011*u,.018-.009*u]));
 // Glove opening cuff follows forearm / palm connection, not gravity.
 forms.push(se305Sweep(at(-.049),at(-.018),6,28,u=>[
  .085-.005*u,.073-.006*u]));
 return se305Combine(forms);
}
function se305Boot(side){
 const x=side*.259;
 const shaft=se305Sweep([x,.59,.025],[x,.15,.035],27,50,u=>[
  .117+.009*u,.112+.02*u]);
 const toe=se305MiterBand(30,50,(u,v)=>{
  const a=(v-.5)*2*Math.PI,cap=Math.sin(Math.PI*u);
  return [x+.14*cap*Math.sin(a),
   .14+.109*Math.cos(Math.PI*u),
   .139+.215*cap*Math.cos(a)];
 });
 const rim=se305Sweep([x,.67,.024],[x,.595,.026],7,46,u=>[
  .119-.007*u,.116-.006*u]);
 return se305Combine([shaft,toe,rim]);
}
const se305PreviousScene=se291HeroScene;
se291HeroScene=function(){
 const scene=se305PreviousScene(),model=scene?.project?.modelAtelier,
  parts=model?.parts;
 if(!Array.isArray(parts)||parts.length!==17||
     !parts.every(p=>p.id.startsWith('vanguard-rebuilt-')))
  throw Error('Vanguard joint mesh+UV patch expected 17 native parts');
 const identifiers=parts.map(p=>p.id);
 function replace(i,geometry,title,material){
  const p=parts[i];
  p.topologyMesh=geometry;p.name=title;
  if(material)p.heroPBR={...p.heroPBR,tile:'v300:'+material};
  p.heroPBR={...p.heroPBR,uvConstruction:'surface-driven-v11.305',
   surfaceId:'vanguard-'+i,uvCoordinates:'from-current-topology',
   photographCutouts:false};
 }
 replace(0,se305Body(),'Vanguard / fitted torso, radial sleeves and trousers','uniform');
 replace(1,se305Face(),'Vanguard / sculpted face, shaped cartilage ears','skin');
 // Retain the improved v11.303 hair geometry and skin-portrait atlas.
 parts[2].heroPBR={...parts[2].heroPBR,uvConstruction:'surface-driven-v11.305'};
 parts[3].heroPBR={...parts[3].heroPBR,uvConstruction:'surface-driven-v11.305'};
 replace(4,se305Hood(),'Vanguard / open cloth hood, canopy and mantle','hood');
 replace(5,se305Scarf(),'Vanguard / naturally gathered cowl','scarf');
 replace(6,se305Shawl(),'Vanguard / overlapping chest fabric folds','scarf');
 replace(7,se305Armor(parts[7].topologyMesh),
   'Vanguard / original tapered breastplate with thickness','armor');
 // Preserve the successful silhouette of both shoulder plates.
 for(const i of [8,9])
  replace(i,se305Armor(parts[i].topologyMesh),
   'Vanguard / '+(i===8?'left':'right')+' pauldron, formed metal thickness','pauldron');
 replace(10,se305Cloth(-1),'Vanguard / left two-sided teal cloth','teal');
 replace(11,se305Cloth(1),'Vanguard / right two-sided teal cloth','teal');
 replace(12,se305Belt(),'Vanguard / curved belt with actual buckle','leather');
 replace(13,se305Glove(-1),'Vanguard / left anatomical glove, neutral wrist','gloves');
 replace(14,se305Glove(1),'Vanguard / right anatomical glove, neutral wrist','gloves');
 replace(15,se305Boot(-1),'Vanguard / left fitted boot and rounded toe','boots');
 replace(16,se305Boot(1),'Vanguard / right fitted boot and rounded toe','boots');
 let verts=0,tris=0;
 for(let i=0;i<parts.length;i++){
  const p=parts[i],g=p.topologyMesh,n=g.positions.length/3;
  if(n<10||g.uvs.length!==2*n||g.indices.length%3||
    g.indices.some(k=>!Number.isInteger(k)||k<0||k>=n)||
    g.uvs.some(t=>!Number.isFinite(t)||t<0||t>1)||
    g.positions.some(x=>!Number.isFinite(x)))
   throw Error('Invalid mesh and UV pair on native part '+p.name);
  verts+=n;tris+=g.indices.length/3;
 }
 if(parts.some((p,i)=>p.id!==identifiers[i]))
  throw Error('Native part identity was mutated');
 se305State.rebuiltParts=17;se305State.vertices=verts;
 se305State.triangles=tris;
 model.name='Hooded Vanguard · Whole Mesh & UV Reconstruction';
 model.reference='v11.305: whole-character topology/UV pairing. Torso, radial upper/lower sleeves and trousers have real cylindrical seams; anatomically aligned cuff/palm/fingers, paired cloth sides and draped scarf, hood canopy/mantle, belt and boots refined. Preserves v11.303 high-resolution face portrait/hair, prior engraved chest and shoulders with formed thickness. All 17 editable IDs, 11 styled UV material families and normal/roughness maps retained. Not rigged.';
 scene.project.name=model.name;
 scene.engine='§wyrl§ Engine · Maker v11.305';scene.version=11.305;
 return scene;
};
window.SWYRL_ENGINE_HOODED_VANGUARD=Object.freeze({
 id:'hooded-vanguard',open:se291OpenHero,createScene:se291HeroScene,
 status:()=>({...se291Stats,...se300Status,...se301Result,
  ...se302SurfaceStatus,...se303FaceStats,...se305State,
  editableParts:17,geometryAndUVRebuiltTogether:true,rigged:false,
  bird:false,weapon:false})
});
