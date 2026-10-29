// V11_13_REFERENCE_ASSEMBLIES: original editable surfaces and independent living attachments.
let atelierAssemblyPlaying=false,atelierAssemblyLast=0,atelierAssemblyTime=4,atelierAssemblyRestart=true;
const atelierAssemblyMeshes=new Map();
function atelierReferenceGeometry(part){
  if(part.kind==='sphere'&&part.surfaceStyle==='portrait-head'){
    const g=new THREE.SphereGeometry(1,36,28),a=g.attributes.position;
    for(let i=0;i<a.count;i++){let x=a.getX(i),y=a.getY(i),z=a.getZ(i);
      // A rounded cranium, cheek shelf and tapered jaw. Positive Z is the face.
      const jaw=y<-.12?1-.31*Math.pow((-y-.12)/.88,.65):1;
      x*=jaw;z*=y<-.35?.92:1;
      if(z>0){z+=.055*Math.exp(-((x/.52)**2+((y+.2)/.4)**2));}
      a.setXYZ(i,x,y,z);
    }g.computeVertexNormals();g.computeBoundingSphere();return g;
  }
  if(part.kind!=='loft')return null;
  if(part.surfaceStyle==='hair-lock'||part.surfaceStyle==='anatomy-smooth'&&model()?.assemblies){const g=atelierOrganicLoft(part),idx=g.index;for(let i=0;i<idx.count;i+=3){const b=idx.getX(i+1);idx.setX(i+1,idx.getX(i+2));idx.setX(i+2,b);}g.computeVertexNormals();return g;}
  if(part.surfaceStyle==='paper-leaf')return atelierReferenceLeaf(part);
  if(part.surfaceStyle!=='paper-plume')return null;
  const curve=new THREE.CatmullRomCurve3(part.path.map(q=>new THREE.Vector3(...q)),false,'centripetal');
  const v=[],colors=[],uv=[];
  const palette=part.group==='Azure frost'?['#38c8dc','#6edbe4','#2099b9','#78e8e7','#1bb0cd']:['#f46b60','#ff9c6b','#df4d56','#ffc17c','#f68060'];
  const radius=t=>{const f=t*(part.radii.length-1),i=Math.min(part.radii.length-2,Math.floor(f));return THREE.MathUtils.lerp(part.radii[i],part.radii[i+1],f-i);};
  const tri=(a,b,c,col)=>{for(const p of [a,b,c]){v.push(...p.toArray());colors.push(col.r,col.g,col.b);uv.push(0,0);}};
  const rings=Math.min(40,Math.max(12,Math.round(Number(part.layers)||28))),facets=Math.min(12,Math.max(6,Math.round(Number(part.facets)||10)));
  for(let i=0;i<rings;i++)for(let j=0;j<facets;j++){
    const t=(i+.35)/rings,a=(j+(i%2)*.5)*Math.PI*2/facets;
    const center=curve.getPoint(t),tan=curve.getTangent(t).normalize();
    let right=new THREE.Vector3(0,0,1).cross(tan).normalize();if(right.lengthSq()<.01)right.set(1,0,0);
    const up=new THREE.Vector3().crossVectors(tan,right).normalize();
    const normal=right.clone().multiplyScalar(Math.cos(a)).addScaledVector(up,Math.sin(a));
    const across=right.clone().multiplyScalar(-Math.sin(a)).addScaledVector(up,Math.cos(a));
    const r=radius(t),width=r*.76,span=.20+.09*Math.sin(t*Math.PI),col=new THREE.Color(palette[(i+j*3)%palette.length]);
    // Each overlapping paper scale has a raised crease, asymmetric torn end,
    // bent lower half and physical thickness, including the rear and underside.
    const rows=[];
    for(let k=0;k<4;k++){
      const f=k/3,points=[];
      for(let h=0;h<3;h++){
        const u=h-1,tear=k===3?(h===1?.032:-.014)*Math.sin(i*2.1+j):0;
        points.push(center.clone().addScaledVector(normal,r+.018+Math.sin(f*Math.PI)*.035+(h===1?.025:0)+f*f*.05)
          .addScaledVector(across,u*width*.5*(1-.14*f)).addScaledVector(tan,(f-.18)*span+tear));
      }rows.push(points);
    }
    for(let k=0;k<3;k++)for(let h=0;h<2;h++){
      const q=[rows[k][h],rows[k+1][h],rows[k+1][h+1],rows[k][h+1]];
      const tint=col.clone().multiplyScalar(h===0?.90:1.08);tri(q[0],q[1],q[2],tint);tri(q[0],q[2],q[3],tint);
    }
    const edge=col.clone().multiplyScalar(.68);
    for(let h=0;h<2;h++){const a=rows[3][h],b=rows[3][h+1],c=b.clone().addScaledVector(normal,-.012),d=a.clone().addScaledVector(normal,-.012);tri(a,b,c,edge);tri(a,c,d,edge);}
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.computeVertexNormals();g.computeBoundingSphere();return g;
}
function atelierReferenceLeaf(p){
  const curve=new THREE.CatmullRomCurve3(p.path.map(q=>new THREE.Vector3(...q)),false,'centripetal'),v=[],c=[],idx=[];
  const col=new THREE.Color(p.color),n=8;
  for(let i=0;i<=n;i++){const t=i/n,f=t*(p.radii.length-1),j=Math.min(p.radii.length-2,Math.floor(f)),w=THREE.MathUtils.lerp(p.radii[j],p.radii[j+1],f-j),q=curve.getPoint(t);
    for(let side=-1;side<=1;side++){v.push(q.x+side*w,q.y,q.z+(side===0?.018:0));const color=col.clone().multiplyScalar(side===-1?.84:side===0?1.07:.98);c.push(color.r,color.g,color.b);}
    if(i<n)for(let side=0;side<2;side++){const k=i*3+side;idx.push(k,k+3,k+1,k+1,k+3,k+4);}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));g.setAttribute('color',new THREE.Float32BufferAttribute(c,3));g.setIndex(idx);g.computeVertexNormals();g.computeBoundingSphere();return g;
}
function atelierValidateAssemblies(data,parts){
  if(data==null)return null;
  const vec=v=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&Math.abs(n)<=30);
  if(data.schema!=='swyrl-assemblies-v1'||!Array.isArray(data.sockets)||data.sockets.length>32||!Array.isArray(data.components)||data.components.length>16)throw Error('Invalid assembly schema or limits.');
  if(!Number.isFinite(data.time)||data.time<0||data.time>30||!Number.isFinite(data.duration)||data.duration<1||data.duration>30)throw Error('Invalid assembly duration.');
  const ids=new Set(),sockets=new Set(),groups=new Set();
  for(const s of data.sockets){if(typeof s.id!=='string'||s.id.length>60||sockets.has(s.id)||s.owner!=='hero'||!vec(s.position)||typeof s.name!=='string'||s.name.length>80||s.partId!==undefined&&(!parts.some(p=>p.id===s.partId)||!vec(s.local)||!s.bind||!vec(s.bind.position)||!vec(s.bind.rotation)||!vec(s.bind.scale)||s.bind.scale.some(v=>v<=.005)))throw Error('Invalid named socket.');sockets.add(s.id);}
  for(const c of data.components){if(typeof c.id!=='string'||c.id.length>60||ids.has(c.id)||typeof c.group!=='string'||groups.has(c.group)||!parts.some(p=>p.group===c.group)||typeof c.name!=='string'||c.name.length>80||!['attached','free'].includes(c.state)||!vec(c.pivot)||!vec(c.offset)||!vec(c.rotation)||c.socketId!=null&&!sockets.has(c.socketId)||c.state==='attached'&&!sockets.has(c.socketId)||!Number.isFinite(c.amplitude)||c.amplitude<0||c.amplitude>.3||!Number.isFinite(c.speed)||c.speed<.1||c.speed>4||c.scale!==undefined&&(!Number.isFinite(c.scale)||c.scale<.1||c.scale>3))throw Error('Invalid independent model or socket.');if(c.freeMatrix!==undefined&&(!Array.isArray(c.freeMatrix)||c.freeMatrix.length!==16||!c.freeMatrix.every(n=>Number.isFinite(n)&&Math.abs(n)<=100)||[3,7,11].some(i=>Math.abs(c.freeMatrix[i])>1e-8)||Math.abs(c.freeMatrix[15]-1)>1e-8||Math.abs(new THREE.Matrix4().fromArray(c.freeMatrix).determinant())<1e-8))throw Error('Invalid detached world matrix.');if(c.keys!==undefined&&(!Array.isArray(c.keys)||c.keys.length>24||c.keys.some((k,i)=>!Number.isFinite(k.time)||k.time<0||k.time>data.duration||i>0&&k.time<=c.keys[i-1].time||!vec(k.offset)||!vec(k.rotation)||!Number.isFinite(k.scale)||k.scale<.1||k.scale>3)))throw Error('Invalid model motion keys.');ids.add(c.id);groups.add(c.group);}
  return structuredClone(data);
}
function atelierAssemblyData(){return model()?.assemblies||null;}
function atelierAssemblySample(c,time){
  const data=atelierAssemblyData(),socket=data?.sockets.find(s=>s.id===c.socketId),restPivot=new THREE.Vector3(...c.pivot);
  const parentDelta=new THREE.Matrix4();let pivot=c.pivot.slice();
  const poseMatrix=p=>new THREE.Matrix4().compose(new THREE.Vector3(...p.position),new THREE.Quaternion().setFromEuler(new THREE.Euler(...p.rotation)),new THREE.Vector3(...p.scale));
  if(c.state==='attached'&&socket?.partId){
    const part=partById(socket.partId);if(part&&socket.bind){
      const current=poseMatrix(part),rest=poseMatrix(socket.bind);parentDelta.copy(current).multiply(rest.invert());
      pivot=new THREE.Vector3(...socket.local).applyMatrix4(current).toArray();
    }
  }else if(c.state==='attached'&&socket){parentDelta.makeTranslation(...socket.position.map((v,i)=>v-c.pivot[i]));pivot=socket.position.slice();}
  let offset=c.offset.slice(),rot=c.rotation.slice(),scale=c.scale||1;
  if(c.state==='attached'){
    const t=Math.min(1,Math.max(0,time/3.6)),ease=t*t*t*(t*(t*6-15)+10),sign=c.pivot[0]<0?-1:1;
    offset=[sign*1.1*(1-ease),-.8*(1-ease),.32*(1-ease)];rot=[0,sign*.55*(1-ease),sign*-.52*(1-ease)];scale=.62+.38*ease;
  }
  if(c.keys?.length){
    const keys=c.keys;let a=keys[0],b=a;
    for(const k of keys){if(k.time<=time)a=k;if(k.time>=time){b=k;break;}b=k;}
    const f=b.time===a.time?0:THREE.MathUtils.clamp((time-a.time)/(b.time-a.time),0,1),u=f*f*(3-2*f);
    offset=a.offset.map((v,i)=>THREE.MathUtils.lerp(v,b.offset[i],u));
    const qa=new THREE.Quaternion().setFromEuler(new THREE.Euler(...a.rotation)),qb=new THREE.Quaternion().setFromEuler(new THREE.Euler(...b.rotation));qa.slerp(qb,u);rot=new THREE.Euler().setFromQuaternion(qa).toArray().slice(0,3);scale=THREE.MathUtils.lerp(a.scale,b.scale,u);
  }
  const matrix=new THREE.Matrix4();
  if(c.state==='free'&&c.freeMatrix&&!c.keys?.length){
    matrix.fromArray(c.freeMatrix);const p=new THREE.Vector3(),q=new THREE.Quaternion(),s=new THREE.Vector3();matrix.decompose(p,q,s);rot=new THREE.Euler().setFromQuaternion(q).toArray().slice(0,3);scale=Math.cbrt(Math.abs(s.x*s.y*s.z));offset=restPivot.clone().applyMatrix4(matrix).sub(restPivot).toArray();
  }else{
    const q=new THREE.Quaternion().setFromEuler(new THREE.Euler(...rot));
    matrix.compose(restPivot.clone().add(new THREE.Vector3(...offset)),q,new THREE.Vector3(scale,scale,scale));matrix.multiply(new THREE.Matrix4().makeTranslation(...c.pivot.map(v=>-v)));matrix.premultiply(parentDelta);
  }
  return {pivot,offset,rotation:rot,scale,matrix:matrix.toArray()};
}
function atelierBindAssemblyMeshes(){
  atelierAssemblyMeshes.clear();const data=atelierAssemblyData();if(!data)return;
  for(const c of data.components){const meshes=[];for(const mesh of modelRoot?.children||[]){const p=partById(mesh.userData.atelierId);if(p?.group!==c.group)continue;
    meshes.push(mesh);mesh.userData.assemblyBase={position:mesh.position.clone(),quaternion:mesh.quaternion.clone(),scale:mesh.scale.clone()};
    if(p.surfaceStyle==='paper-plume'){const a=mesh.geometry.attributes.position;mesh.userData.paperRest=a.array.slice();}}
    atelierAssemblyMeshes.set(c.id,meshes);}
  atelierAssemblyTime=data.time;atelierApplyAssemblyTime(atelierAssemblyTime);
}
function atelierApplyAssemblyTime(time){
  const data=atelierAssemblyData();if(!data||!modelRoot)return;
  atelierAssemblyTime=Math.max(0,Math.min(data.duration,time));
  for(const c of data.components){const sample=atelierAssemblySample(c,atelierAssemblyTime),matrix=new THREE.Matrix4().fromArray(sample.matrix);
    if(c.id==='bunny')matrix.premultiply(new THREE.Matrix4().makeTranslation(0,Math.max(0,Math.sin(atelierAssemblyTime*c.speed*3))*c.amplitude,0));
    for(const mesh of atelierAssemblyMeshes.get(c.id)||[]){const base=mesh.userData.assemblyBase;if(!base)continue;
      mesh.matrixAutoUpdate=false;mesh.matrix.copy(matrix).multiply(new THREE.Matrix4().compose(base.position,base.quaternion,base.scale));
      const rest=mesh.userData.paperRest;if(rest){const a=mesh.geometry.attributes.position;
        for(let i=0;i<a.count;i++){const x=rest[i*3],y=rest[i*3+1],z=rest[i*3+2],w=Math.min(1,Math.hypot(x-c.pivot[0],y-c.pivot[1],z-c.pivot[2])/2.8);
          const wave=c.amplitude*w*w*Math.sin(atelierAssemblyTime*c.speed*2.3-w*3.5);
          a.setXYZ(i,x+wave,y+wave*.28,z+wave*1.7);}
        a.needsUpdate=true;mesh.geometry.computeVertexNormals();mesh.geometry.computeBoundingSphere();mesh.geometry.computeBoundingBox();}

    }}
  modelRoot.updateMatrixWorld(true);
  const scrub=$m('AssemblyTime');if(scrub)scrub.value=String(atelierAssemblyTime);const label=$m('AssemblyTimeLabel');if(label)label.textContent=atelierAssemblyTime.toFixed(2)+' s';
}
function atelierAssemblyTick(now){
  if(!atelierAssemblyPlaying||!atelierAssemblyData())return;const dt=Math.min(.08,Math.max(0,(now-atelierAssemblyLast)/1000));atelierAssemblyLast=now;
  atelierApplyAssemblyTime(atelierAssemblyTime+dt);
  if(atelierAssemblyTime>=atelierAssemblyData().duration){atelierAssemblyPlaying=false;atelierAssemblyRestart=true;$m('AssemblyPlay').textContent='▶ Play transform';}
}
function atelierAssemblyChoose(){return atelierAssemblyData()?.components.find(c=>c.id===$m('AssemblyComponent')?.value);}
function atelierAssemblyRefresh(){
  const deck=$m('AssemblyDeck');if(!deck)return;const d=atelierAssemblyData();deck.hidden=!d;
  if(!d)return;
  const pick=$m('AssemblyComponent'),old=pick.value;pick.replaceChildren();for(const c of d.components){const op=document.createElement('option');op.value=c.id;op.textContent=c.name+' · '+c.state;pick.append(op);}if(d.components.some(c=>c.id===old))pick.value=old;
  const c=atelierAssemblyChoose();if(c){$m('AssemblyAmplitude').value=String(c.amplitude);$m('AssemblySpeed').value=String(c.speed);atelierAssemblyFields();}
  $m('AssemblyTime').max=String(d.duration);$m('AssemblyTime').value=String(atelierAssemblyTime);
}
function atelierAssemblyAttach(attached){
  const c=atelierAssemblyChoose();if(!c)return;if(attached&&!c.socketId){status('This standalone companion has no hair socket.');return;}
  const pose=atelierAssemblySample(c,atelierAssemblyTime);checkpoint();model().assemblies.time=atelierAssemblyTime;
  if(!attached){c.offset=pose.offset.slice();c.rotation=pose.rotation.slice();c.scale=pose.scale;c.freeMatrix=pose.matrix.slice();c.state='free';delete c.keys;}
  else {c.state='attached';delete c.keys;delete c.freeMatrix;c.offset=[0,0,0];c.rotation=[0,0,0];c.scale=1;atelierAssemblyTime=4;model().assemblies.time=4;}
  atelierAssemblyPlaying=false;signalEdited();atelierAssemblyRefresh();status(attached?'Snapped independent model to its real pigtail socket.':'Detached model, conserving its current world transform. Undo restores attachment.');
}
function atelierAssemblyFields(){
 const c=atelierAssemblyChoose();if(!c)return;const pose=atelierAssemblySample(c,atelierAssemblyTime);
 for(const key of ['offset','rotation'])for(let i=0;i<3;i++){const el=$m('Assembly'+key+i);if(el)el.value=String(+pose[key][i].toFixed(4));}
 const el=$m('AssemblyScale');if(el)el.value=String(+pose.scale.toFixed(4));
 const label=$m('AssemblyKeyCount');if(label)label.textContent=(c.keys?.length||0)+' saved motion keys';
}
function atelierAssemblySaveKey(){
 const c=atelierAssemblyChoose(),data=atelierAssemblyData();if(!c)return;
 const offset=[0,1,2].map(i=>Number($m('Assemblyoffset'+i).value)),rotation=[0,1,2].map(i=>Number($m('Assemblyrotation'+i).value)),scale=Number($m('AssemblyScale').value);
 if([...offset,...rotation].some(n=>!Number.isFinite(n)||Math.abs(n)>30)||!Number.isFinite(scale)||scale<.1||scale>3){status('Motion transform is out of range.',true);return;}
 const time=+atelierAssemblyTime.toFixed(3),keys=structuredClone(c.keys||[]),at=keys.findIndex(k=>Math.abs(k.time-time)<.001);
 if(keys.length>=24&&at<0){status('Maximum 24 motion keys per model.',true);return;}
 const key={time,offset,rotation,scale};if(at<0)keys.push(key);else keys[at]=key;keys.sort((a,b)=>a.time-b.time);
 checkpoint();c.keys=keys;delete c.freeMatrix;data.time=time;atelierAssemblyPlaying=false;signalEdited();atelierAssemblyRefresh();status('Saved independent model key at '+time.toFixed(2)+' s. Preview, undo and JSON retain its motion.');
}
function atelierAssemblyInstall(){
 $m('AssemblySaveKey')?.addEventListener('click',atelierAssemblySaveKey);
 $m('AssemblyClearKeys')?.addEventListener('click',()=>{const c=atelierAssemblyChoose();if(!c||!c.keys?.length)return;checkpoint();delete c.keys;signalEdited();atelierAssemblyRefresh();});
  $m('AssemblyComponent')?.addEventListener('change',atelierAssemblyRefresh);
  $m('AssemblyPlay')?.addEventListener('click',()=>{if(!atelierAssemblyData())return;atelierAssemblyPlaying=!atelierAssemblyPlaying;if(atelierAssemblyPlaying){if(atelierAssemblyRestart||atelierAssemblyTime>=atelierAssemblyData().duration)atelierAssemblyTime=0;atelierAssemblyRestart=false;atelierAssemblyLast=performance.now();} $m('AssemblyPlay').textContent=atelierAssemblyPlaying?'Ⅱ Pause':'▶ Play transform';});
  $m('AssemblyStop')?.addEventListener('click',()=>{atelierAssemblyPlaying=false;atelierAssemblyRestart=true;atelierApplyAssemblyTime(atelierAssemblyData()?.time??4);$m('AssemblyPlay').textContent='▶ Play transform';});
  $m('AssemblyTime')?.addEventListener('input',e=>{atelierAssemblyPlaying=false;atelierAssemblyRestart=false;atelierApplyAssemblyTime(Number(e.target.value));atelierAssemblyFields();});
  $m('AssemblyAttach')?.addEventListener('click',()=>atelierAssemblyAttach(true));$m('AssemblyDetach')?.addEventListener('click',()=>atelierAssemblyAttach(false));
  $m('AssemblyMotionApply')?.addEventListener('click',()=>{const c=atelierAssemblyChoose(),amplitude=Number($m('AssemblyAmplitude').value),speed=Number($m('AssemblySpeed').value);if(!c||!Number.isFinite(amplitude)||amplitude<0||amplitude>.3||!Number.isFinite(speed)||speed<.1||speed>4){status('Flex must be 0–0.3 and speed 0.1–4.',true);return;}checkpoint();c.amplitude=amplitude;c.speed=speed;signalEdited();});
  $m('AssemblyExport')?.addEventListener('click',()=>{const c=atelierAssemblyChoose();if(!c)return;download(c.id+'.independent-model.json',JSON.stringify({schema:'swyrl-independent-model-v1',component:structuredClone(c),socket:structuredClone(atelierAssemblyData().sockets.find(s=>s.id===c.socketId)||null),parts:structuredClone(model().parts.filter(p=>p.group===c.group))},null,2),'application/json');});
  atelierAssemblyRefresh();
}
function atelierReferenceCameraFit(){
 if(!modelRoot||!camera)return null;camera.updateMatrixWorld(true);const box=new THREE.Box3().setFromObject(modelRoot),points=[];
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])points.push(new THREE.Vector3(x,y,z).project(camera));
 return {left:Math.min(...points.map(p=>p.x)),right:Math.max(...points.map(p=>p.x)),bottom:Math.min(...points.map(p=>p.y)),top:Math.max(...points.map(p=>p.y)),aspect:camera.aspect};
}
function atelierAssemblyStatus(){
  const d=atelierAssemblyData();return {enabled:!!d,time:atelierAssemblyTime,playing:atelierAssemblyPlaying,cameraFit:atelierReferenceCameraFit(),components:(d?.components||[]).map(c=>({id:c.id,state:c.state,socketId:c.socketId,...atelierAssemblySample(c,atelierAssemblyTime),parts:(atelierAssemblyMeshes.get(c.id)||[]).length,bounds:(()=>{const b=new THREE.Box3();for(const m of atelierAssemblyMeshes.get(c.id)||[])b.expandByObject(m);if(b.isEmpty())return null;return {min:b.min.toArray(),max:b.max.toArray()};})()})),metrics:atelierGeometryStats()};
}
