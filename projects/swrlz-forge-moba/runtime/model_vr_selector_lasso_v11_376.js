/* SE376_VR_SELECTOR_LASSO_START */
// Selection is a transient VR input mode, not an edit to the source mesh.
// Left-trigger's reversible sweep is kept; left Grip draws a lasso only while
// the dedicated Selector panel has a Lasso mode armed.
const SE376_LASSO_MAX_POINTS=180;
function se376Inside(p,poly){
 let inside=false;
 for(let i=0,j=poly.length-1;i<poly.length;j=i++){
  const a=poly[i],b=poly[j];
  if((a.y>p.y)!==(b.y>p.y)&&p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x)inside=!inside;
 }
 return inside;
}
function se376SegCross(a,b,c,d){
 const cross=(u,v,w)=>(v.x-u.x)*(w.y-u.y)-(v.y-u.y)*(w.x-u.x);
 const x=cross(a,b,c),y=cross(a,b,d),z=cross(c,d,a),w=cross(c,d,b),eps=1e-9;
 if(x*y< -eps&&z*w< -eps)return true;
 const on=(p,q,r)=>r.x>=Math.min(p.x,q.x)-eps&&r.x<=Math.max(p.x,q.x)+eps&&
  r.y>=Math.min(p.y,q.y)-eps&&r.y<=Math.max(p.y,q.y)+eps;
 return (Math.abs(x)<=eps&&on(a,b,c))||(Math.abs(y)<=eps&&on(a,b,d))||
  (Math.abs(z)<=eps&&on(c,d,a))||(Math.abs(w)<=eps&&on(c,d,b));
}
function se376RectOverlap(poly,minX,minY,maxX,maxY){
 const rect=[{x:minX,y:minY},{x:maxX,y:minY},{x:maxX,y:maxY},{x:minX,y:maxY}];
 if(poly.some(p=>p.x>=minX&&p.x<=maxX&&p.y>=minY&&p.y<=maxY)||rect.some(p=>se376Inside(p,poly)))return true;
 for(let i=0;i<poly.length;i++)
  for(let j=0;j<4;j++)if(se376SegCross(poly[i],poly[(i+1)%poly.length],rect[j],rect[(j+1)%4]))return true;
 return false;
}
function se376PolygonArea(points){
 let twice=0;
 for(let i=0;i<points.length;i++){
  const a=points[i],b=points[(i+1)%points.length];
  twice+=a.x*b.y-a.y*b.x;
 }
 return Math.abs(twice)*.5;
}
function se376SelectionBand(candidates,depthRange,through){
 if(through||!candidates.length)return candidates;
 const nearest=Math.min(...candidates.map(x=>x.depth));
 const band=THREE.MathUtils.clamp(depthRange*.15,.06,.13);
 return candidates.filter(x=>x.depth<=nearest+band);
}
function se376PanelMode(action){
 const s=se340XR;
 if(action==='selector'){s.page='selector';s.se376SelectionMode||='sweep';}
 else if(['selector-sweep','selector-lasso-front','selector-lasso-through'].includes(action)){
  s.page='selector';s.se376SelectionMode=action.slice('selector-'.length);
 }else return false;
 if(s.gesture)se340CancelGesture('Selection mode changed · unfinished gesture canceled.');
 const title={'sweep':'Trigger sweep: sweep forward to add, retrace to remove.',
  'lasso-front':'Front lasso: hold Left Grip and outline the visible mesh cluster.',
  'lasso-through':'Through lasso: hold Left Grip; include meshes behind the outline.'};
 se340Notice(title[s.se376SelectionMode]||title.sweep);
 se340SyncUI();se340Publish();return true;
}
function se376ShouldLasso(record,purpose){
 const s=se340XR;
 return purpose==='pan'&&record.input?.handedness==='left'&&
  s.page==='selector'&&['lasso-front','lasso-through'].includes(s.se376SelectionMode);
}
function se376RayPlane(g){
 const cast=se340Cast(g.record);if(!cast)return null;
 const den=cast.ray.direction.dot(g.normal);
 if(Math.abs(den)<.07)return null;
 const distance=g.origin.clone().sub(cast.ray.origin).dot(g.normal)/den;
 if(!Number.isFinite(distance)||distance<.035||distance>5)return null;
 const p=cast.ray.at(distance,new THREE.Vector3()).sub(g.origin);
 return {x:p.dot(g.right),y:p.dot(g.up)};
}
function se376LassoDraw(g){
 const n=g.points.length,attr=g.line.geometry.attributes.position;
 for(let i=0;i<n;i++){
  const p=g.points[i],world=g.origin.clone().addScaledVector(g.right,p.x).addScaledVector(g.up,p.y);
  attr.setXYZ(i,world.x,world.y,world.z);
 }
 if(n>=3){
  const p=g.points[0],world=g.origin.clone().addScaledVector(g.right,p.x).addScaledVector(g.up,p.y);
  attr.setXYZ(n,world.x,world.y,world.z);
 }
 attr.needsUpdate=true;
 g.line.geometry.setDrawRange(0,n+(n>=3?1:0));
}
function se376LassoUpdate(g,force=false){
 if(g?.kind!=='selection-lasso')return false;
 const p=se376RayPlane(g);if(!p)return false;
 const last=g.points[g.points.length-1];
 if(last&&Math.hypot(p.x-last.x,p.y-last.y)<(force?.001:.008))return true;
 if(g.points.length>=SE376_LASSO_MAX_POINTS)return true;
 g.points.push(p);se376LassoDraw(g);return true;
}
function se376LassoBegin(record,purpose){
 if(!se376ShouldLasso(record,purpose))return false;
 const s=se340XR,viewer=s.lastViewer||s.anchor;
 if(!viewer||!s.rig||!s.scene){se340Notice('Model workspace is not ready for lasso.',true);return true;}
 const normal=s.rig.position.clone().sub(viewer.position).normalize();
 if(normal.lengthSq()<.05)normal.copy(viewer.forward).normalize();
 const right=new THREE.Vector3().crossVectors(normal,new THREE.Vector3(0,1,0));
 if(right.lengthSq()<.02)right.set(1,0,0);right.normalize();
 const up=new THREE.Vector3().crossVectors(right,normal).normalize();
 const origin=s.rig.position.clone();
 const position=new Float32Array((SE376_LASSO_MAX_POINTS+1)*3);
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute('position',new THREE.BufferAttribute(position,3));
 geometry.setDrawRange(0,0);
 const material=new THREE.LineBasicMaterial({color:0x74f3e7,transparent:true,opacity:.98,
  depthTest:false,depthWrite:false,toneMapped:false});
 const line=new THREE.Line(geometry,material);line.frustumCulled=false;line.renderOrder=9500;
 line.userData.editorOnly=true;line.name='Model VR · selector lasso guide';s.scene.add(line);
 const g={kind:'selection-lasso',record,mode:s.se376SelectionMode,origin,normal,right,up,points:[],
  line,started:performance.now()};
 s.gesture=g;
 if(!se376LassoUpdate(g,true)){se376LassoDispose(g);s.gesture=null;
  se340Notice('Aim the left controller ray toward the model before holding Grip.',true);return true;}
 se340Notice(g.mode==='lasso-through'?'Through lasso · outline an area · release Grip to select all depths.':
  'Front lasso · outline a cluster · release Grip to select nearby-depth parts.');
 se340Pulse(record,.15,18);
 return true;
}
function se376LassoDispose(g){
 if(!g?.line)return;
 g.line.removeFromParent();g.line.geometry?.dispose?.();g.line.material?.dispose?.();g.line=null;
}
function se376MeshRect(entry,g){
 const mesh=entry.mesh,box=se340PartBox(mesh);
 if(!box||box.isEmpty())return null;
 const min=box.min,max=box.max,corners=[];
 for(const x of [min.x,max.x])for(const y of [min.y,max.y])for(const z of [min.z,max.z])corners.push(new THREE.Vector3(x,y,z));
 let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;
 for(const v of corners){
  const d=v.sub(g.origin),x=d.dot(g.right),y=d.dot(g.up);
  minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);
 }
 const center=box.getCenter(new THREE.Vector3()),depth=center.clone().sub(g.viewerPosition).dot(g.normal);
 if(!Number.isFinite(depth))return null;
 return {id:entry.id,depth,minX,minY,maxX,maxY,center:{
   x:center.clone().sub(g.origin).dot(g.right),y:center.clone().sub(g.origin).dot(g.up)
 }};
}
function se376LassoCommit(g){
 if(g?.kind!=='selection-lasso')return false;
 se376LassoUpdate(g,true);se376LassoDispose(g);
 if(g.points.length<3||se376PolygonArea(g.points)<.00015){
  se340Notice('Lasso was too small · outline a wider area and release Grip.',true);return false;
 }
 const s=se340XR,poly=g.points,viewer=s.lastViewer||s.anchor;
 g.viewerPosition=viewer?.position||g.origin.clone().addScaledVector(g.normal,-1.12);
 s.pivot?.updateWorldMatrix(true,true);
 const entries=se340PartEntries().filter(e=>e.mesh?.visible!==false);
 const bounds=se340SourceBounds(entries);
 const spans=bounds.getSize(new THREE.Vector3()),range=Math.max(spans.x,spans.y,spans.z);
 const candidates=[];
 for(const e of entries){
  const projected=se376MeshRect(e,g);
  if(!projected||!se376RectOverlap(poly,projected.minX,projected.minY,projected.maxX,projected.maxY))continue;
  candidates.push(projected);
 }
 const selected=se376SelectionBand(candidates,range,g.mode==='lasso-through');
 const already=new Set(se350Tools().selection().ids);
 let added=0,limit=false;
 for(const item of selected){
  if(already.has(item.id))continue;
  if(already.size>=32){limit=true;break;}
  const result=se350Tools().select(item.id,{additive:true});
  if(result?.ok===false){limit=result.error==='MODEL_SELECTION_LIMIT_32';break;}
  already.add(item.id);added++;
 }
 if(added)se350Invalidate();
 se340Notice((g.mode==='lasso-through'?'Through lasso':'Front lasso')+' · '+added+
  ' meshes added · '+already.size+' total'+(limit?' · 32-part selection limit reached':'')+'.',limit);
 se340Publish();return true;
}
/* SE376_VR_SELECTOR_LASSO_END */
