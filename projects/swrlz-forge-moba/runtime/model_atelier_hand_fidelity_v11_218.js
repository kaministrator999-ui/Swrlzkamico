// §E v11.218 — Arcane Glove concept-fidelity geometry. Native editable parts.
// New starter opens only; no saved-project, engine renderer, XR or rig mutation.
const se218FingerSpec=Object.freeze([
 {x:-.397,from:2.170,to:3.055,r:.104,splay:-.055,z:.006,name:'index'},
 {x:-.131,from:2.197,to:3.255,r:.112,splay:-.017,z:-.009,name:'middle'},
 {x:.135,from:2.176,to:3.152,r:.103,splay:.028,z:-.009,name:'ring'},
 {x:.402,from:2.113,to:2.856,r:.084,splay:.083,z:.010,name:'pinky'}
]);
function se218HandDetails({digits,wire,sphere,color}){
 const metal=color.rim,dark=color.void,glow=color.light;
 // Every dorsal conduit has a socket at the shield and at its knuckle.
 // Raised joints clamp cables to the curved backhand, not midair.
 for(const [i,f] of digits.entries()){
  const root=[f.x*.58,1.825,-.380];
  const bend=[f.x*.83,1.995,-.329];
  const knuckle=[f.x,f.from+.066,-.241];
  const path=[root,bend,knuckle];
  wire('Backhand · anchored digit '+(i+1)+' conduit',path,.014,color.accent,'emissive','Backhand / harness');
  sphere('Backhand · conduit '+(i+1)+' socket',root,[.042,.048,.026],metal,'metal','Backhand / harness');
  sphere('Backhand · conduit '+(i+1)+' retaining bolt',[root[0],root[1],root[2]-.026],
   [.015,.018,.013],dark,'metal','Backhand / harness');
  sphere('Digit '+(i+1)+' · cable knuckle ferrule',knuckle,[f.r*.54,.055,.029],metal,'metal','Fingers / harness');
  // Metal straps physically bridge each raised glowing finger rail.
  for(const [j,t] of [.45,.69].entries()){
   const h=f.to-f.from,y=f.from+h*t,x=f.x+f.splay*(t*.83);
   const z=f.z-f.r*(t>.6?.83:.95)-.026;
   wire('Digit '+(i+1)+' · rail retainer '+(j+1),
    [[x-f.r*.80,y-.029,z+.019],[x-f.r*.52,y,z-.016],
     [x,y+.018,z-.033],[x+f.r*.52,y,z-.016],[x+f.r*.80,y-.029,z+.019]],
    .009,metal,'metal','Fingers / harness');
   sphere('Digit '+(i+1)+' · retainer '+(j+1)+' center',[x,y+.014,z-.040],
    [f.r*.28,.026,.020],color.plate,'metal','Fingers / harness');
  }
  const tip=[f.x+f.splay,f.to-.085,f.z-f.r*.77-.015];
  sphere('Digit '+(i+1)+' · fingertip bezel',tip,[f.r*.42,.049,.028],metal,'metal','Fingers / harness');
  sphere('Digit '+(i+1)+' · fingertip energy core',[tip[0],tip[1],tip[2]-.024],
   [f.r*.27,.035,.015],glow,'emissive','Fingers / harness');
 }
 // Curved two-segment thumb centerline. Theta begins/ends on negative Z,
 // creating a single continuous two-turn helix from dorsal root to back tip.
 const along=(t)=>{
  const a=[-.765,1.730,.175],b=[-.951,1.875,.205],c=[-1.115,2.011,.232];
  const u=Math.min(1,t*2),v=Math.max(0,(t-.50)*2);
  if(t<=.5)return a.map((n,j)=>n+(b[j]-n)*u);
  return b.map((n,j)=>n+(c[j]-n)*v);
 };
 const tangent=(t)=>{
  const l=along(Math.max(0,t-.006)),r=along(Math.min(1,t+.006));
  const dx=r[0]-l[0],dy=r[1]-l[1],len=Math.hypot(dx,dy)||1;
  return [-dy/len,dx/len];
 };
 const radius=(t)=>.163-(.062*t);
 const thumbPoint=(t,angle)=>{
  const c=along(t),n=tangent(t),r=radius(t);
  return [c[0]+n[0]*r*Math.cos(angle),c[1]+n[1]*r*Math.cos(angle),c[2]+r*Math.sin(angle)];
 };
 const spiral=Array.from({length:97},(_,i)=>{
  const t=i/96;
  return thumbPoint(t,-Math.PI/2+Math.PI*4*t);
 });
 wire('Thumb · continuous back-to-tip double helix',spiral,.0175,
  color.accent,'emissive','Thumb / helix');
 const start=spiral[0],end=spiral[spiral.length-1];
 wire('Thumb · dorsal joint to helix feed',
  [[-.729,1.704,-.259],[-.775,1.728,-.135],[-.786,1.731,-.052],start],
  .013,color.accent,'emissive','Thumb / helix');
 sphere('Thumb · helix root socket',[-.729,1.704,-.262],[.102,.097,.037],
  metal,'metal','Thumb / helix');
 sphere('Thumb · root socket dark center',[-.729,1.704,-.299],[.066,.065,.018],
  dark,'metal','Thumb / helix');
 for(const [j,t] of [.23,.53,.80].entries()){
  const points=Array.from({length:24},(_,i)=>thumbPoint(t,Math.PI*2*i/24));
  wire('Thumb · spiral retention band '+(j+1),points,.0078,metal,'metal','Thumb / helix',true);
  const socket=thumbPoint(t,-Math.PI/2+Math.PI*4*t);
  sphere('Thumb · spiral retention clasp '+(j+1),socket,
   [.035,.036,.029],color.plate,'metal','Thumb / helix');
 }
 sphere('Thumb · helix tip setting',end,[.047,.049,.029],metal,'metal','Thumb / helix');
 sphere('Thumb · glowing back-of-tip terminal',
  [end[0],end[1],end[2]-.026],[.031,.034,.017],glow,'emissive','Thumb / helix');
 // Metal-framed geometric sigil, editable bolted attachments at both flanks.
 const diamond=[[0,2.105,-.402],[-.204,1.88,-.408],
  [0,1.632,-.410],[.204,1.88,-.408]];
 wire('Backhand · diamond recessed dark bezel',diamond,.036,metal,'metal','Backhand / harness',true);
 wire('Backhand · diamond luminous inset',diamond.map(([x,y,z])=>[x*.93,y-.005,z-.035]),
  .018,glow,'emissive','Backhand / harness',true);
 for(const side of [-1,1]){
  const point=[side*.198,1.885,-.438];
  sphere((side<0?'Index':'Pinky')+' · shield conduit socket',point,
   [.054,.068,.028],metal,'metal','Backhand / harness');
  sphere((side<0?'Index':'Pinky')+' · shield socket cap',
   [point[0],point[1],point[2]-.026],[.025,.036,.016],color.plate,'metal','Backhand / harness');
 }
 for(const [i,y] of [.58,.82,1.025].entries()){
  sphere('Wrist · front ring segment '+(i+1),[0,y,.278],[.117,.033,.025],
   color.plate,'metal','Wrist / harness');
  sphere('Wrist · ring light insert '+(i+1),[0,y,.300],[.073,.012,.011],
   glow,'emissive','Wrist / harness');
 }
}
