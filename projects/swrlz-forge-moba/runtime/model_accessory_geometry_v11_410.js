/* SE410_ACCESSORY_GEOMETRY_START */
// Reusable native indexed geometry. No renderer, model document, history,
// image texture or scene mutation is owned by this module.
const se410AccessoryGeometry=(()=>{
 const round=n=>Math.abs(n)<1e-10?0:+n.toFixed(8);
 const empty=()=>({positions:[],uvs:[],indices:[]});
 const vertex=(d,p,uv=[0,0])=>{const i=d.positions.length/3;d.positions.push(...p.map(round));d.uvs.push(...uv.map(round));return i;};
 const face=(d,a,b,c)=>d.indices.push(a,b,c);
 const quad=(d,a,b,c,e)=>{face(d,a,b,c);face(d,a,c,e);};
 function merge(items){const d=empty();for(const x of items){const base=d.positions.length/3;d.positions.push(...x.positions);d.uvs.push(...x.uvs);d.indices.push(...x.indices.map(i=>i+base));}return d;}
 function orient(d){
  const count=d.indices.length/3,edges=new Map(),adj=Array.from({length:count},()=>[]),parity=new Int8Array(count).fill(-1),components=[];
  for(let f=0;f<count;f++){const ids=d.indices.slice(f*3,f*3+3);for(let i=0;i<3;i++){const a=ids[i],b=ids[(i+1)%3],key=a<b?a+':'+b:b+':'+a;if(!edges.has(key))edges.set(key,[]);edges.get(key).push([f,a,b]);}}
  for(const edge of edges.values()){if(edge.length!==2)throw Error('ACCESSORY_CLOSED_SURFACE_REQUIRED');const [a,b]=edge,same=a[1]===b[1];adj[a[0]].push([b[0],same]);adj[b[0]].push([a[0],same]);}
  for(let seed=0;seed<count;seed++){if(parity[seed]!==-1)continue;const queue=[seed];parity[seed]=0;for(let i=0;i<queue.length;i++)for(const [other,same]of adj[queue[i]]){const next=parity[queue[i]]^(same?1:0);if(parity[other]===-1){parity[other]=next;queue.push(other);}else if(parity[other]!==next)throw Error('ACCESSORY_ORIENTATION_CONFLICT');}components.push(queue);}
  for(let f=0;f<count;f++)if(parity[f]){const i=f*3;[d.indices[i+1],d.indices[i+2]]=[d.indices[i+2],d.indices[i+1]];}
  for(const component of components){
   const used=new Set(component.flatMap(f=>d.indices.slice(f*3,f*3+3))),center=[0,0,0];for(const id of used)for(let k=0;k<3;k++)center[k]+=d.positions[id*3+k]/used.size;
   let volume=0;for(const f of component){const p=d.indices.slice(f*3,f*3+3).map(id=>d.positions.slice(id*3,id*3+3).map((n,k)=>n-center[k]));const [a,b,c]=p;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;}
   if(Math.abs(volume)<1e-13)throw Error('ACCESSORY_ZERO_VOLUME');if(volume<0)for(const f of component){const i=f*3;[d.indices[i+1],d.indices[i+2]]=[d.indices[i+2],d.indices[i+1]];}
  }
  return d;
 }
 function roundedProfile(width,depth,radius,steps=5){
  const a=width/2,b=depth/2,r=Math.min(radius,a*.95,b*.95),points=[];
  for(const [cx,cy,start]of [[a-r,b-r,0],[-a+r,b-r,Math.PI/2],[-a+r,-b+r,Math.PI],[a-r,-b+r,Math.PI*1.5]])
   for(let i=0;i<=steps;i++){const angle=start+i/steps*Math.PI/2;points.push([cx+r*Math.cos(angle),cy+r*Math.sin(angle)]);}
  return points;
 }
 function joinLoops(d,a,b,n){for(let i=0;i<n;i++)quad(d,a+i,a+(i+1)%n,b+(i+1)%n,b+i);}
 function cap(d,start,n,center,reverse=false){const id=vertex(d,center,[.5,.5]);for(let i=0;i<n;i++)face(d,id,start+(reverse?(i+1)%n:i),start+(reverse?i:(i+1)%n));}
 function shell(p){
  const d=empty(),w=p.width,h=p.height,z=p.depth,t=p.thickness;
  const rows=[[-.5,.76,.68],[-.36,.94,.92],[-.10,1,1],[.25,1,1],[.5,.96,.94]],n=24,outer=[],inner=[];
  for(let k=0;k<rows.length;k++){const [y,sx,sz]=rows[k],rw=w*sx,rd=z*sz,r=Math.min(p.rounding*sx,rd*.44,rw*.25);outer.push(d.positions.length/3);
   roundedProfile(rw,rd,r).forEach(([x,zz],i)=>vertex(d,[x,y*h,zz],[i/n,k/(rows.length-1)]));}
  for(let k=0;k<rows.length;k++){const [y,sx,sz]=rows[k],rw=w*sx-2*t,rd=z*sz-2*t,r=Math.max(.001,Math.min(p.rounding*sx-t,rd*.44,rw*.25));inner.push(d.positions.length/3);
   roundedProfile(rw,rd,r).forEach(([x,zz],i)=>vertex(d,[x,k===0?-.5*h+t:y*h,zz],[i/n,k/(rows.length-1)]));}
  for(let i=0;i<rows.length-1;i++){joinLoops(d,outer[i],outer[i+1],n);joinLoops(d,inner[i],inner[i+1],n);}
  joinLoops(d,outer.at(-1),inner.at(-1),n);cap(d,outer[0],n,[0,-h*.5,0]);cap(d,inner[0],n,[0,-h*.5+t,0]);return orient(d);
 }
 function curve(points,closed=false){return new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)),closed,'centripetal');}
 function tube(points,radius,segments=32,sides=6,closed=false){
  const c=curve(points,closed),frames=c.computeFrenetFrames(segments,closed),d=empty(),rings=closed?segments:segments+1;
  for(let i=0;i<rings;i++){const at=c.getPointAt(i/segments);for(let j=0;j<sides;j++){const a=j/sides*Math.PI*2,p=at.clone().addScaledVector(frames.normals[i],Math.cos(a)*radius).addScaledVector(frames.binormals[i],Math.sin(a)*radius);vertex(d,p.toArray(),[i/segments,j/sides]);}}
  for(let i=0;i<(closed?rings:rings-1);i++)joinLoops(d,i*sides,((i+1)%rings)*sides,sides);
  if(!closed){cap(d,0,sides,c.getPointAt(0).toArray());cap(d,(rings-1)*sides,sides,c.getPointAt(1).toArray());}return orient(d);
 }
 function ribbon(points,width,thickness,segments=18,closed=false){
  const c=curve(points,closed),d=empty(),rings=closed?segments:segments+1,axis=new THREE.Vector3(1,0,0);
  for(let i=0;i<rings;i++){const t=i/segments,at=c.getPointAt(t),tangent=c.getTangentAt(t),normal=new THREE.Vector3().crossVectors(tangent,axis).normalize();
   for(const [x,z]of [[-1,-1],[1,-1],[1,1],[-1,1]])vertex(d,at.clone().addScaledVector(axis,x*width/2).addScaledVector(normal,z*thickness/2).toArray(),[t,(x+z+2)/4]);}
  for(let i=0;i<(closed?rings:rings-1);i++)joinLoops(d,i*4,((i+1)%rings)*4,4);
  if(!closed){face(d,0,1,2);face(d,0,2,3);const b=(rings-1)*4;face(d,b,b+1,b+2);face(d,b,b+2,b+3);}return orient(d);
 }
 function plate(contour,thickness,position=[0,0,0],angle=0,bevel=0){
  const d=empty(),n=contour.length,bounds=new THREE.Box2().setFromPoints(contour.map(p=>new THREE.Vector2(...p))),extent=Math.min(...bounds.getSize(new THREE.Vector2()).toArray());
  const center=bounds.getCenter(new THREE.Vector2()),b=Math.min(bevel,thickness*.3,extent*.15),inset=1-b/Math.max(extent*.5,.001);
  const levels=b>0?[[-thickness/2,inset],[-thickness/2+b,1],[thickness/2-b,1],[thickness/2,inset]]:[[-thickness/2,1],[thickness/2,1]];
  for(const [z,s]of levels)for(const [x,y]of contour){const px=center.x+(x-center.x)*s,py=center.y+(y-center.y)*s;vertex(d,[position[0]+px*Math.cos(angle)-py*Math.sin(angle),position[1]+px*Math.sin(angle)+py*Math.cos(angle),position[2]+z],[(x-bounds.min.x)/Math.max(.001,bounds.max.x-bounds.min.x),(y-bounds.min.y)/Math.max(.001,bounds.max.y-bounds.min.y)]);}
  for(let k=0;k<levels.length-1;k++)joinLoops(d,k*n,(k+1)*n,n);
  const triangles=THREE.ShapeUtils.triangulateShape(contour.map(p=>new THREE.Vector2(...p)),[]);
  for(const ids of triangles){face(d,...ids);face(d,...ids.map(i=>i+(levels.length-1)*n));}return orient(d);
 }
 function ringPlate(width,height,border,thickness,position){
  const outer=roundedProfile(width,height,Math.min(width,height)*.2,4),inner=roundedProfile(width-border*2,height-border*2,Math.min(width,height)*.10,4),n=outer.length,d=empty();
  for(const z of [-thickness/2,thickness/2])for(const loop of [outer,inner])for(const [x,y]of loop)vertex(d,[x+position[0],y+position[1],z+position[2]],[x/width+.5,y/height+.5]);
  joinLoops(d,0,n,n);joinLoops(d,2*n,3*n,n);joinLoops(d,0,2*n,n);joinLoops(d,n,3*n,n);return orient(d);
 }
 function flap(p){
  const w=p.width,h=p.height,z=p.depth,t=p.thickness*.8,bottom=(.5-p.flap)*h;
  const c=curve([[0,h*.50,-z*.46],[0,h*.56,-z*.16],[0,h*.49,z*.44],[0,h*.36,z*.58],[0,bottom,z*.59]]),d=empty(),cols=10,rows=16,stride=cols+1;
  function point(u,v,offset=0){const edge=Math.max(0,(Math.abs(u)-.68)/.32),end=1-.13*(1-Math.sqrt(Math.max(0,1-edge*edge))),at=v*end,center=c.getPoint(at),tan=c.getTangent(at),normal=new THREE.Vector3(0,tan.z,-tan.y).normalize();return center.add(new THREE.Vector3(u*w*.46,0,0)).addScaledVector(normal,offset).toArray();}
  for(const side of [-1,1])for(let y=0;y<=rows;y++)for(let x=0;x<=cols;x++)vertex(d,point(x/cols*2-1,y/rows,side*t/2),[x/cols,y/rows]);
  const layer=stride*(rows+1);for(let side=0;side<2;side++)for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){const a=side*layer+y*stride+x;quad(d,a,a+1,a+stride+1,a+stride);}
  const border=[];for(let x=0;x<=cols;x++)border.push(x);for(let y=1;y<=rows;y++)border.push(y*stride+cols);for(let x=cols-1;x>=0;x--)border.push(rows*stride+x);for(let y=rows-1;y>0;y--)border.push(y*stride);
  for(let i=0;i<border.length;i++){const a=border[i],b=border[(i+1)%border.length];quad(d,a,b,b+layer,a+layer);}return {data:orient(d),point};
 }
 function stitches(points,spacing,radius,closed=false){
  const c=curve(points,closed),length=c.getLength(),n=Math.max(4,Math.min(58,Math.floor(length/spacing))),pieces=[];
  for(let i=0;i<n;i++){const center=(i+.5)/n,half=Math.min(.28/n,.012/Math.max(.001,length));const a=c.getPointAt(Math.max(0,center-half)),b=c.getPointAt(Math.min(1,center+half));pieces.push(tube([a.toArray(),b.toArray()],radius,1,6));}return merge(pieces);
 }
 function build(input={}){
  const fail=error=>({ok:false,error,reason:error});if(!input||typeof input!=='object'||Array.isArray(input))return fail('INVALID_ACCESSORY_PARAMETERS');
  const ranges={width:[.35,1.8,.8],height:[.35,1.8,.9],depth:[.15,.75,.32],thickness:[.012,.10,.035],rounding:[.02,.25,.12],flap:[.25,.85,.48],strap:[0,1,.32]};
  const p={};for(const [key,[min,max,value]]of Object.entries(ranges)){const v=input[key]===undefined?value:input[key];if(typeof v!=='number'||!Number.isFinite(v)||v<min||v>max)return fail('INVALID_ACCESSORY_'+key.toUpperCase());p[key]=v;}
  p.detail=input.detail===undefined?true:input.detail;if(typeof p.detail!=='boolean')return fail('INVALID_ACCESSORY_DETAIL');
  for(const [key,value]of Object.entries({bodyColor:'#704b39',flapColor:'#8b6044',trimColor:'#d7b47c',metalColor:'#cda16a'})){p[key]=input[key]===undefined?value:input[key];if(typeof p[key]!=='string'||!/^#[0-9a-fA-F]{6}$/.test(p[key]))return fail('INVALID_ACCESSORY_COLOR');}
  p.emblem=input.emblem===undefined?'leaf':input.emblem;if(!['leaf','star','none'].includes(p.emblem))return fail('INVALID_ACCESSORY_EMBLEM');
  if(p.thickness>=Math.min(p.depth*.22,p.height*.12,p.width*.12))return fail('ACCESSORY_WALL_TOO_THICK');
  p.rounding=Math.min(p.rounding,p.depth*.44,p.width*.25);const w=p.width,h=p.height,z=p.depth,t=p.thickness,parts=[];
  const part=(componentKey,name,data,color,material='matte')=>{parts.push({componentKey,name,kind:'topologyMesh',group:'Hip pouch',position:[0,0,0],rotation:[0,0,0],scale:[1,1,1],color,material,topologyMesh:data});};
  try{
   part('body','Pouch · hollow body',shell(p),p.bodyColor);
   const f=flap(p);part('flap','Pouch · curved flap',f.data,p.flapColor);
   const loops=[],loopHeight=h*(.22+p.strap*.24),loopDepth=Math.max(t*2.2,z*.18);
   for(const x of [-w*.25,w*.25]){const centerY=h*.48,centerZ=-z*.5-t*.5,profile=roundedProfile(loopDepth,loopHeight,Math.min(loopDepth,loopHeight)*.42,4),points=profile.map(([zz,y])=>[x,centerY+y,centerZ+zz]);loops.push(ribbon(points,w*.105,t*.65,24,true));}
   part('beltLoops','Pouch · belt loops',merge(loops),p.bodyColor);
   const flapY=(.5-p.flap)*h,strapLength=h*(.13+p.strap*.24),front=z*.59+t*.6;
   part('closureStrap','Pouch · closure strap',ribbon([[0,flapY+h*.13,front],[0,flapY+h*.025,front+t*.4],[0,flapY-strapLength,front-t*.15]],w*.13,t*.65,12),p.bodyColor);
   const buckleAt=[0,flapY+h*.035,front+t*.6],buckle=ringPlate(w*.22,h*.13,Math.min(w*.025,h*.02),t*.65,buckleAt);
   const pin=plate(roundedProfile(w*.15,h*.017,h*.006,3),t*.65,[0,buckleAt[1],buckleAt[2]+t*.45],0,t*.12);
   part('clasp','Pouch · brass buckle',merge([buckle,pin]),p.metalColor,'metal');
   if(p.detail){
    const seam=[];for(let i=0;i<=10;i++)seam.push(f.point(-.88,.08+i/10*.85,t*.55));for(let i=1;i<=12;i++)seam.push(f.point(-.88+i/12*1.76,.94,t*.55));for(let i=1;i<=10;i++)seam.push(f.point(.88,.93-i/10*.85,t*.55));
    const bodySeam=[[-w*.39,h*.32,z*.505],[-w*.41,-h*.2,z*.505],[-w*.30,-h*.41,z*.43],[w*.30,-h*.41,z*.43],[w*.41,-h*.2,z*.505],[w*.39,h*.32,z*.505]];
    part('piping','Pouch · edge piping',merge([tube(seam,t*.10,60,6),tube(bodySeam,t*.10,40,6)]),p.trimColor);
    part('stitches','Pouch · stitched seams',merge([stitches(seam,.045,t*.062),stitches(bodySeam,.045,t*.062)]),p.trimColor,'silk');
   }
   if(p.emblem!=='none'){
    const emblem=[],at=[0,flapY+h*.22,z*.59+t*1.05],thick=t*.32;
    if(p.emblem==='star'){const points=[];for(let i=0;i<10;i++){const a=Math.PI/2+i*Math.PI/5,r=(i%2?.44:1)*Math.min(w,h)*.105;points.push([Math.cos(a)*r,Math.sin(a)*r]);}emblem.push(plate(points,thick,at,0,t*.07));}
    else{
     const leaf=(width,height)=>{const points=[];for(let i=0;i<=7;i++){const q=i/7;points.push([Math.sin(q*Math.PI)*width/2,q*height]);}for(let i=6;i>=1;i--){const q=i/7;points.push([-Math.sin(q*Math.PI)*width/2,q*height]);}return points;};
     for(const [x,y,angle,scale]of [[0,-h*.06,0,1],[-w*.045,-h*.025,.72,.8],[w*.045,-h*.025,-.72,.8]])emblem.push(plate(leaf(w*.070*scale,h*.15*scale),thick,[at[0]+x,at[1]+y,at[2]],angle,t*.05));
     emblem.push(plate(roundedProfile(w*.014,h*.20,w*.005,3),thick,[at[0],at[1]+h*.015,at[2]-thick*.25],0,t*.05));
    }
    part('emblem','Pouch · '+p.emblem+' emblem',merge(emblem),p.metalColor,'metal');
   }
  }catch(error){return fail(String(error?.message||'ACCESSORY_GEOMETRY_FAILED'));}
  const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];let vertices=0,triangles=0;
  for(const p of parts){vertices+=p.topologyMesh.positions.length/3;triangles+=p.topologyMesh.indices.length/3;for(let i=0;i<p.topologyMesh.positions.length;i+=3)for(let k=0;k<3;k++){const v=p.topologyMesh.positions[i+k];min[k]=Math.min(min[k],v);max[k]=Math.max(max[k],v);}}
  return {ok:true,parts,parameters:p,bounds:{min,max,size:max.map((v,i)=>v-min[i])},mount:{position:[0,h*.18,-z*.5-t*1.8],normal:[0,0,-1],up:[0,1,0]},stats:{parts:parts.length,vertices,triangles}};
 }
 return Object.freeze({build,roundedProfile,shell,tube,ribbon,plate,ringPlate,merge});
})();
function se410BuildAccessoryRecipe(params={}){return se410AccessoryGeometry.build(params);}
/* SE410_ACCESSORY_GEOMETRY_END */
