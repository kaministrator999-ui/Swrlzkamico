// §E v11.23: explicitly close an oval UV face sheet into a sculptable
// head starter. This is manually controlled geometry, not inferred likeness.
// Front UVs remain attached to their original vertices; back is intentionally
// a neutral preview of the same atlas until a separate back texture exists.
let atelierFaceHeatmap=false;
function atelierFaceVolumeClose(front,p){
 const v=p.faceSheet;
 if(v.shape!=='oval'||!v.headDepth)return front;
 const seg=v.gridU,rings=v.gridV,backRings=Math.max(4,Math.min(24,Math.round(rings/2)));
 const pos=Array.from(front.attributes.position.array),uv=Array.from(front.attributes.uv.array);
 const idx=Array.from(front.index.array);
 const rim=1+(rings-1)*seg;
 let outer=Array.from({length:seg},(_,j)=>rim+j);
 const [cx,cy,cw,ch]=v.crop;
 for(let layer=1;layer<backRings;layer++){
   const t=layer/backRings,r=.5*Math.cos(t*Math.PI/2);
   const depth=-v.headDepth*Math.sin(t*Math.PI/2);
   const inner=[];
   for(let j=0;j<seg;j++){
     const theta=2*Math.PI*j/seg,x=Math.sin(theta)*r,y=Math.cos(theta)*r;
     inner.push(pos.length/3);pos.push(x,y,depth);
     uv.push(cx+cw*(.5+x),cy+ch*(.5+y));
   }
   for(let j=0;j<seg;j++){
     const next=(j+1)%seg,a=outer[j],b=outer[next],c=inner[next],d=inner[j];
     idx.push(a,b,c,a,c,d);
   }
   outer=inner;
 }
 const end=pos.length/3;pos.push(0,0,-v.headDepth);uv.push(cx+cw*.5,cy+ch*.5);
 for(let j=0;j<seg;j++)idx.push(outer[j],outer[(j+1)%seg],end);
 const result=new THREE.BufferGeometry();
 result.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
 result.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
 result.setIndex(idx);
 result.computeVertexNormals();
 result.userData.faceVolume=true;
 front.dispose();
 return result;
}
function atelierFaceVolumeStats(geometry,part){
 const index=geometry.index,p=geometry.attributes.position,uv=geometry.attributes.uv;
 if(!p||!uv||part.kind!=='faceSheet')return {maximum:0,mean:0,count:0,triangles:0};
 const crop=part.faceSheet.crop;
 let max=0,sum=0,count=0,faces=(index?index.count:p.count)/3;
 const at=(i)=>index?index.getX(i):i;
 const bad=new Float32Array(p.count);
 const distortion=(i,j)=>{
   const u=(uv.getX(i)-uv.getX(j))/crop[2],v=(uv.getY(i)-uv.getY(j))/crop[3];
   const expected=Math.hypot(u,v),d=Math.hypot(p.getX(i)-p.getX(j),
     p.getY(i)-p.getY(j),p.getZ(i)-p.getZ(j));
   return expected<1e-7?0:Math.max(0,Math.abs(d/expected-1));
 };
 for(let i=0;i<faces;i++){
   const a=at(i*3),b=at(i*3+1),c=at(i*3+2);
   // Front distortion only: back cap UV projection deliberately compresses
   // toward the rear pole and is not a photographed surface.
   const faceZ=(p.getZ(a)+p.getZ(b)+p.getZ(c))/3;
   if(part.faceSheet.headDepth&&faceZ<-1e-5)continue;
   const d=Math.max(distortion(a,b),distortion(b,c),distortion(c,a));
   if(!Number.isFinite(d))continue;
   max=Math.max(max,d);sum+=d;count++;
   bad[a]=Math.max(bad[a],d);bad[b]=Math.max(bad[b],d);bad[c]=Math.max(bad[c],d);
 }
 return {maximum:max,mean:count?sum/count:0,count,triangles:faces,bad};
}
function atelierFaceVolumeHeatmap(mesh,part){
 if(!atelierFaceHeatmap||part.kind!=='faceSheet')return;
 const stats=atelierFaceVolumeStats(mesh.geometry,part);
 const a=mesh.geometry.attributes.position,colors=[];
 for(let i=0;i<a.count;i++){
   const t=THREE.MathUtils.clamp((stats.bad?.[i]||0)*2.5,0,1);
   const c=new THREE.Color().setRGB(t,t<.5?1:t*.3,.17+(.83*(1-t)));
   colors.push(c.r,c.g,c.b);
 }
 mesh.geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
 mesh.material=new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide});
 mesh.material.userData.atelierViewportClone=true;
}
function atelierFaceVolumeRefresh(){
 const p=partById(selection);
 if(p?.kind!=='faceSheet')return;
 const el=$m('FaceSheetHeadDepth'),button=$m('FaceSheetUVHeatmap'),info=$m('FaceSheetUVStats');
 if(el)el.value=String(p.faceSheet.headDepth||0);
 if(button)button.checked=atelierFaceHeatmap;
 if(info){
   const mesh=modelRoot?.children.find(o=>o.isMesh&&o.userData.atelierId===p.id);
   const s=mesh?atelierFaceVolumeStats(mesh.geometry,p):null;
   info.textContent=s?
     'Front UV stretch: average '+(s.mean*100).toFixed(1)+'%, max '+(s.maximum*100).toFixed(1)+
     '% · '+s.triangles+' evaluated triangles. '+(p.faceSheet.headDepth?'Closed head profile':'Open face sheet'):
     'Select image face sheet to inspect UV distortion.';
 }
}
function atelierFaceVolumeInstall(){
 $m('FaceSheetUVHeatmap').addEventListener('change',e=>{
   atelierFaceHeatmap=e.target.checked;
   renderParts();atelierFaceVolumeRefresh();
 });
}
