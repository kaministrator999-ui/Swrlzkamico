// Optional portrait finish preserves the exact geometry of unannotated heads.
function atelierPortraitFinish(p){
 const g=atelierHDSphere(p),a=g.attributes.position,c=g.attributes.color,f=p.portraitFinish;
 const bell=(x,y,sx,sy)=>Math.exp(-((x/sx)**2+(y/sy)**2));
 for(let i=0;i<a.count;i++){
  const x=a.getX(i),y=a.getY(i);let z=a.getZ(i);
  if(z>0){
   const front=THREE.MathUtils.smoothstep(z,.20,.65),tip=bell(x,y+.31,.095,.075);
   const bridge=bell(x,y+.12,.085,.22),alar=bell(x-.12,y+.33,.055,.05)+bell(x+.12,y+.33,.055,.05);
   z+=front*f.noseDefinition*(.008*bridge+.032*tip+.006*alar);
   const cheek=bell(x-.47,y+.17,.24,.17)+bell(x+.47,y+.17,.24,.17);
   const nostrils=bell(x-.085,y+.335,.027,.018)+bell(x+.085,y+.335,.027,.018);
   const color=new THREE.Color(c.getX(i),c.getY(i),c.getZ(i));
   color.lerp(new THREE.Color('#df8990'),f.warmth*front*(.22*cheek+.18*tip));
   color.lerp(new THREE.Color('#a76b70'),f.noseDefinition*front*.18*nostrils);
   c.setXYZ(i,color.r,color.g,color.b);
  }
  a.setXYZ(i,x,y+f.chinLift*THREE.MathUtils.smoothstep(-y,.18,1),z);
 }
 g.computeVertexNormals();g.computeBoundingSphere();return g;
}
// Project an editable contour onto the actual generated head, in component rest space.
function atelierPortraitFit(part,head,offset){
 if(part?.kind!=='loft'||head?.surfaceStyle!=='portrait-head'||head.hdFinish?.style!=='portrait'||part.group!==head.group||!Number.isFinite(offset)||offset<0||offset>.01)return null;
 const matrix=p=>new THREE.Matrix4().compose(new THREE.Vector3(...p.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...p.rotation)),new THREE.Vector3(...p.scale));
 const g=atelierHDGeometry(head),material=new THREE.MeshBasicMaterial({side:THREE.DoubleSide}),mesh=new THREE.Mesh(g,material);
 mesh.applyMatrix4(matrix(head));mesh.updateMatrixWorld(true);const box=new THREE.Box3().setFromObject(mesh),partMatrix=matrix(part),inverse=partMatrix.clone().invert();
 const curve=new THREE.CatmullRomCurve3(part.path.map(q=>new THREE.Vector3(...q)),false,'centripetal'),ray=new THREE.Raycaster(),path=[],radii=[];
 let valid=true;
 for(let i=0;i<=32;i++){
  const t=i/32,q=curve.getPoint(t).applyMatrix4(partMatrix);
  ray.set(new THREE.Vector3(q.x,q.y,box.max.z+1),new THREE.Vector3(0,0,-1));
  const hit=ray.intersectObject(mesh,false)[0];if(!hit){valid=false;break;}
  path.push(hit.point.add(new THREE.Vector3(0,0,offset)).applyMatrix4(inverse).toArray());
  radii.push(atelierHDRadius(part,t));
 }
 g.dispose();material.dispose();return valid?{...part,path,radii}:null;
}
function atelierPortraitRefresh(){
 const p=partById(selection),deck=$m('PortraitFinish');if(!deck)return;
 deck.hidden=!(p?.surfaceStyle==='portrait-head'&&p.hdFinish?.style==='portrait');
 if(!deck.hidden){$m('ChinLift').value=p.portraitFinish?.chinLift??0;$m('NoseDefinition').value=p.portraitFinish?.noseDefinition??0;$m('SkinWarmth').value=p.portraitFinish?.warmth??0;}
 $m('FaceFitDeck').hidden=p?.kind!=='loft';
}
function atelierPortraitInstall(){
 $m('PortraitApply').addEventListener('click',()=>{
  const p=partById(selection);if(!p)return;
  const next={...p,portraitFinish:{chinLift:Number($m('ChinLift').value),noseDefinition:Number($m('NoseDefinition').value),warmth:Number($m('SkinWarmth').value)}};
  if(!checkPart(next)){status('Portrait finish rejected: select a portrait head and use valid contour values.',true);return;}
  checkpoint();Object.assign(p,next);signalEdited();select(p.id);status('Portrait finish saved. Chin, nose and skin warmth remain editable.');
 });
 $m('FaceFit').addEventListener('click',()=>{
  const p=partById(selection),head=model()?.parts.find(q=>q.group===p?.group&&q.surfaceStyle==='portrait-head');
  const next=atelierPortraitFit(p,head,Number($m('FaceFitOffset').value));
  if(!next||!checkPart(next)){status('Face fit rejected: select a contour inside the head silhouette and an offset from 0 to 0.01.',true);return;}
  checkpoint();Object.assign(p,next);signalEdited();select(p.id);status('Contour fitted to the actual head surface. The saved spline remains editable.');
 });
}
