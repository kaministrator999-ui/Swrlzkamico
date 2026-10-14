// Project-owned narrative magic, rendered in the native paper theatre.
// Everything is sampled from the episode playhead: seeking never accumulates
// transforms, consumes randomness, or writes the saved project.
const STORY_EFFECTS_SCHEMA='anime-story-effects-v1';
const STORY_EFFECT_TYPES=Object.freeze(['page','burst','ink','portal']);
const STORY_EFFECT_BOUNDS=Object.freeze({strength:[.1,2],x:[-20,20],y:[-10,24],z:[-30,-.1],width:[.25,12],height:[.25,12],rotation:[-Math.PI,Math.PI]});
const STORY_EFFECT_DEFAULTS=Object.freeze({page:{width:1.6,height:2.1,label:'A memory in the margins'},burst:{width:4,height:4,label:'The spell breaks'},ink:{width:4.4,height:1.8,label:'Kami · §wyrlz'},portal:{width:4,height:6,label:'The door remembers'}});
let storyEffectsCacheProject=null,storyEffectsCacheSource=null,storyEffectsCacheDuration=null,storyEffectsCacheValue=null;
let storyEffectsStage=null,storyEffectsDurationDraft=null;
function storyEffectsProject(){return !!currentProject&&(currentProject.canonicalId==='ghosts-different-forms-ep01'||currentProject.animeTimeline?.schema===STORY_SCHEMA);}
function storyEffectsCleanCue(value,duration){
  if(!value||typeof value!=='object'||Array.isArray(value)||!STORY_EFFECT_TYPES.includes(value.effect))return null;
  const base=STORY_EFFECT_DEFAULTS[value.effect],time=storyTime(value.time,duration);
  if(time>=duration)return null;
  const id=storyText(value.id,'',80).trim();if(!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$/.test(id))return null;
  const cue={id,effect:value.effect,time,duration:storyNumber(value.duration,8,.1,Math.max(.1,duration-time)),label:storyText(value.label,base.label,100)};
  for(const [field,[low,high]] of Object.entries(STORY_EFFECT_BOUNDS))cue[field]=storyNumber(value[field],field==='strength'?1:field==='z'?-4:field==='width'||field==='height'?base[field]:0,low,high);
  return cue;
}
function storyEffectsSanitize(value,duration=storyTimeline().duration){
  duration=storyNumber(duration,134,1,3600);
  const raw=value&&typeof value==='object'&&!Array.isArray(value)?value:{},unique=new Map();
  for(const value of Array.isArray(raw.cues)?raw.cues.slice(0,64):[]){const cue=storyEffectsCleanCue(value,duration);if(cue)unique.set(cue.id,cue);}
  return {schema:STORY_EFFECTS_SCHEMA,enabled:raw.enabled===true,cues:[...unique.values()].sort((a,b)=>a.time-b.time||a.id.localeCompare(b.id))};
}
function storyEffectsModel(){
  const source=storyEffectsProject()?currentProject.animeStoryEffects:null,duration=storyTimeline().duration;
  if(storyEffectsCacheProject!==currentProject||storyEffectsCacheSource!==source||storyEffectsCacheDuration!==duration||!storyEffectsCacheValue){
    storyEffectsCacheProject=currentProject;storyEffectsCacheSource=source;storyEffectsCacheDuration=duration;storyEffectsCacheValue=storyEffectsSanitize(source,duration);
  }
  return storyEffectsCacheValue;
}
function storyEffectsInvalidate(){storyEffectsCacheProject=null;storyEffectsCacheSource=null;storyEffectsCacheValue=null;}
function storyEffectsSmooth(value){const u=Math.max(0,Math.min(1,value));return u*u*(3-2*u);}
function storyEffectsSample(id,time){
  const model=storyEffectsModel(),cue=model.cues.find(item=>item.id===id);if(!cue)return null;
  const t=storyNumber(time,0,0,storyTimeline().duration),p=Math.max(0,Math.min(1,(t-cue.time)/cue.duration));
  const active=model.enabled&&t>=cue.time&&t<cue.time+cue.duration;
  const envelope=active?storyEffectsSmooth(p/.12)*(1-storyEffectsSmooth((p-.9)/.1)):0;
  return {...cue,active,progress:p,opacity:envelope,draw:storyEffectsSmooth(p/(cue.effect==='portal'?.31:.55)),open:cue.effect==='portal'?storyEffectsSmooth((p-.31)/.24):0};
}
function storyEffectsNotify(){if(animeCine)storyRender();storyNotify();}
function storyEffectsMutate(label,callback){
  if(!storyEffectsProject()||!storyEditable()||typeof callback!=='function')return false;
  const previous=storyEffectsModel(),draft=storyCopy(previous);if(callback(draft)===false)return false;
  const next=storyEffectsSanitize(draft);if(JSON.stringify(next)===JSON.stringify(previous))return true;
  beginTransaction(label);currentProject.animeStoryEffects=next;storyEffectsInvalidate();commitTransaction(label);storyEffectsNotify();return true;
}
function storyEffectsUpsert(value){
  const cue=storyEffectsCleanCue(value,storyTimeline().duration);if(!cue)return false;
  return storyEffectsMutate('Story effect · '+cue.label,draft=>{const index=draft.cues.findIndex(item=>item.id===cue.id);if(index>=0)draft.cues[index]=cue;else if(draft.cues.length<64)draft.cues.push(cue);else return false;});
}
function storyEffectsRemove(id){return storyEffectsMutate('Remove story effect',draft=>{const index=draft.cues.findIndex(item=>item.id===id);if(index<0)return false;draft.cues.splice(index,1);});}
function storyEffectsConfigure(value){
  if(!value||typeof value!=='object'||Array.isArray(value))return false;
  return storyEffectsMutate('Story effects',draft=>{if(Object.hasOwn(value,'enabled'))draft.enabled=value.enabled===true;if(Array.isArray(value.cues))draft.cues=storyCopy(value.cues);});
}
const storyEffectsPreviousProjectData=projectData;
projectData=function(){const data=storyEffectsPreviousProjectData();if(storyEffectsProject()&&currentProject.animeStoryEffects)data.project.animeStoryEffects=storyCopy(storyEffectsModel());return data;};
const storyEffectsPreviousApplyMeta=applyProjectMeta;
applyProjectMeta=function(meta={}){storyEffectsDispose();const result=storyEffectsPreviousApplyMeta(meta);storyEffectsInvalidate();if(storyEffectsProject()&&meta?.animeStoryEffects)currentProject.animeStoryEffects=storyEffectsSanitize(meta.animeStoryEffects);if(typeof storyEffectsEditorSync==='function')storyEffectsEditorSync();return result;};
const storyEffectsPreviousSetDuration=storySetDuration,storyEffectsPreviousCommit=commitTransaction;
storySetDuration=function(value){
  const number=Number(value),duration=storyTimeline().duration,ownsModel=storyEffectsProject()&&!!currentProject.animeStoryEffects;
  if(!ownsModel||!storyEditable()||!Number.isFinite(number)||number<1||number>3600||number===duration)return storyEffectsPreviousSetDuration(value);
  const draft=storyCopy(storyEffectsModel()),ratio=number/duration;for(const cue of draft.cues){cue.time*=ratio;cue.duration*=ratio;}
  storyEffectsDurationDraft={project:currentProject,model:storyEffectsSanitize(draft,number)};
  try{return storyEffectsPreviousSetDuration(value);}finally{storyEffectsDurationDraft=null;}
};
commitTransaction=function(label,...args){
  // The pre-existing duration edit owns the transaction. Stage this model just
  // before its one commit so Undo restores shots, poses, scenery and cues.
  if(label==='Episode duration'&&storyEffectsDurationDraft?.project===currentProject){currentProject.animeStoryEffects=storyEffectsDurationDraft.model;storyEffectsInvalidate();storyEffectsDurationDraft=null;}
  return storyEffectsPreviousCommit(label,...args);
};
function storyEffectsMaterial(color,extra={}){return new THREE.MeshBasicMaterial({color,side:THREE.DoubleSide,transparent:true,depthWrite:false,depthTest:true,fog:false,toneMapped:false,...extra});}
function storyEffectsPaperTexture(label,kind){
  return animeDrawSurface((c,w,h)=>{
    c.clearRect(0,0,w,h);
    if(kind==='page'){
      const g=c.createLinearGradient(0,0,w,h);g.addColorStop(0,'#f3d9a4');g.addColorStop(.6,'#d6b479');g.addColorStop(1,'#ead0a0');c.fillStyle=g;c.fillRect(0,0,w,h);
      c.strokeStyle='#73542f';c.lineWidth=3;c.strokeRect(18,18,w-36,h-36);c.lineWidth=1;c.strokeRect(28,28,w-56,h-56);
      c.fillStyle='#87632e';c.beginPath();c.arc(w*.5,h*.37,w*.18,0,Math.PI*2);c.fill();c.fillStyle='#e2c18a';c.beginPath();c.arc(w*.55,h*.34,w*.15,0,Math.PI*2);c.fill();
      for(let i=0;i<6;i++){c.strokeStyle='#775435aa';c.beginPath();c.moveTo(w*.18,h*(.63+i*.042));c.lineTo(w*(.77-(i%3)*.045),h*(.63+i*.042));c.stroke();}
    }else{
      c.textAlign='center';c.textBaseline='middle';c.lineJoin='round';
      const line=(text,y,size)=>{c.font='bold '+size+'px Georgia, serif';c.strokeStyle='#25150f';c.lineWidth=9;c.shadowColor='#1b110e';c.shadowBlur=3;c.strokeText(text,w*.5,y,w*.94);c.shadowColor='#cf8e31';c.shadowBlur=8;c.fillStyle='#ffe9ad';c.fillText(text,w*.5,y,w*.94);};
      if(label.startsWith('Welcome back')){line('Welcome back',h*.33,54);line('Kami · §wyrlz',h*.74,41);}
      else line(label,w===384?h*.5:h*.48,60);
    }
  },kind==='page'?384:768,kind==='page'?512:196);
}
function storyEffectsDoorTexture(side){
  return animeDrawSurface((c,w,h)=>{
    const g=c.createLinearGradient(0,0,w,h);g.addColorStop(0,'#765437');g.addColorStop(.25,'#39281f');g.addColorStop(.55,'#573927');g.addColorStop(.85,'#241c1a');g.addColorStop(1,'#80603c');c.fillStyle=g;c.fillRect(0,0,w,h);
    for(let i=0;i<34;i++){const x=(i*.618%1)*w;c.strokeStyle=i%3===0?'#b2834733':'#120b0949';c.lineWidth=i%3===0?1.4:3;c.beginPath();for(let j=0;j<14;j++){const y=j*h/13,grain=x+Math.sin(j*.58+i*2.31)*5+Math.sin(j*1.7+i)*2;j?c.lineTo(grain,y):c.moveTo(grain,y);}c.stroke();}
    c.lineWidth=9;c.strokeStyle='#140e0d';c.strokeRect(19,19,w-38,h-38);c.lineWidth=5;c.strokeStyle='#be9150';c.strokeRect(24,24,w-48,h-48);c.lineWidth=2;c.strokeStyle='#efd6a0';c.strokeRect(29,29,w-58,h-58);c.strokeStyle='#634223';c.strokeRect(35,35,w-70,h-70);
    const x=w*.5,y=h*.34,r=w*.24;c.lineWidth=3;c.strokeStyle='#c7a16b';c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.stroke();c.lineWidth=1;c.beginPath();c.arc(x,y,r*.82,0,Math.PI*2);c.stroke();
    c.fillStyle='#ddba78';c.beginPath();c.arc(x-6,y,r*.59,0,Math.PI*2);c.fill();c.fillStyle='#3b291f';c.beginPath();c.arc(x+side*r*.22,y-r*.1,r*.54,0,Math.PI*2);c.fill();
    c.fillStyle='#edcf92';c.beginPath();c.moveTo(x+r*.68,y-12);c.lineTo(x+r*.77,y+6);c.lineTo(x+r*.92,y+9);c.lineTo(x+r*.76,y+15);c.lineTo(x+r*.69,y+29);c.lineTo(x+r*.64,y+15);c.lineTo(x+r*.51,y+10);c.lineTo(x+r*.63,y+7);c.closePath();c.fill();
    c.strokeStyle='#bd9152';c.lineWidth=2.5;
    for(const edge of [w*.15,w*.85])for(const yy of [h*.13,h*.62,h*.84]){c.beginPath();c.moveTo(edge,yy);c.bezierCurveTo(edge-side*w*.09,yy-36,edge+side*w*.2,yy-48,edge+side*w*.06,yy-8);c.bezierCurveTo(edge+side*w*.16,yy+35,edge-side*w*.16,yy+36,edge,yy);c.stroke();}
    for(let i=0;i<5;i++){const xx=w*(.26+i*.12),yy=h*.73;c.beginPath();c.moveTo(xx,yy+15);c.lineTo(xx-9,yy-10);c.lineTo(xx+8,yy-7);c.lineTo(xx-4,yy+4);c.stroke();}
    for(const xx of [w*.11,w*.89])for(const yy of [h*.06,h*.94]){c.fillStyle='#2d1b11';c.beginPath();c.arc(xx+2,yy+2,5,0,Math.PI*2);c.fill();c.fillStyle='#e0bb77';c.beginPath();c.arc(xx,yy,4,0,Math.PI*2);c.fill();}
  },384,768);
}
function storyEffectsTube(points,radius,color){return new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points.map(point=>new THREE.Vector3(...point))),Math.max(8,points.length*3),radius,5,false),storyEffectsMaterial(color));}
function storyEffectsExtrude(shape,depth,color){const geometry=new THREE.ExtrudeGeometry(shape,{depth,bevelEnabled:true,bevelThickness:.01,bevelSize:.015,bevelSegments:1,steps:1});geometry.translate(0,0,-depth*.5);return new THREE.Mesh(geometry,storyEffectsMaterial(color));}
function storyEffectsPage(cue){
  const group=new THREE.Group(),hinge=new THREE.Group(),shape=new THREE.Shape();group.add(hinge);
  const w=cue.width,h=cue.height;shape.moveTo(-w*.5,0);shape.lineTo(w*.5,0);shape.lineTo(w*.48,h*.9);shape.lineTo(w*.33,h);shape.lineTo(-w*.49,h*.97);shape.closePath();
  hinge.add(storyEffectsExtrude(shape,.055,'#b88e4e'));
  const ink=new THREE.Mesh(new THREE.PlaneGeometry(w*.94,h*.94),storyEffectsMaterial('#ffffff',{map:storyEffectsPaperTexture(cue.label,'page')}));ink.position.set(0,h*.48,.037);hinge.add(ink);
  for(const side of [-1,1]){const rib=new THREE.Mesh(new THREE.BoxGeometry(.025,h*.9,.09),storyEffectsMaterial('#f9dfa6'));rib.position.set(side*w*.47,h*.48,0);hinge.add(rib);}
  group.userData.storyEffectParts={hinge};return group;
}
function storyEffectsBurst(cue){
  const group=new THREE.Group(),rings=[],chips=[],radius=Math.min(cue.width,cue.height)*.5;
  for(let i=0;i<3;i++){const ring=new THREE.Mesh(new THREE.TorusGeometry(radius,.045+i*.012,6,64),storyEffectsMaterial(i===0?'#fff0bd':'#e8b267'));ring.position.z=-i*.16;group.add(ring);rings.push(ring);}
  for(let i=0;i<12;i++){const shape=new THREE.Shape();shape.moveTo(-.095,0);shape.lineTo(-.035,.17);shape.lineTo(0,.44);shape.lineTo(.1,.06);shape.lineTo(.14,-.08);shape.lineTo(0,-.15);shape.closePath();const chip=storyEffectsExtrude(shape,.09,i%3===0?'#fff0bf':'#e0b373');group.add(chip);chips.push(chip);}
  group.userData.storyEffectParts={rings,chips,radius};return group;
}
function storyEffectsInk(cue){
  const group=new THREE.Group(),vertices=[],trails=new THREE.Group();group.add(trails);
  for(let i=0;i<72;i++){const a=i*Math.PI*2/72,b=(i+1)*Math.PI*2/72,r=cue.height*.38;vertices.push(Math.cos(a)*r,Math.sin(a)*r,0,Math.cos(b)*r,Math.sin(b)*r,0);}
  for(let i=0;i<8;i++){const x=(i/7-.5)*cue.width*.91,y=(i%2?-.18:.18)*cue.height;vertices.push(x,y-.13,-.08,x+.12,y+.14,-.08);}
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));
  const strokes=new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({color:'#edc986',transparent:true,depthWrite:false,fog:false,toneMapped:false}));group.add(strokes);
  const radius=cue.height*.38;
  for(let i=0;i<24;i++){const a=i*Math.PI/12,b=(i+1)*Math.PI/12,mid=(a+b)*.5;const trail=storyEffectsTube([[Math.cos(a)*radius,Math.sin(a)*radius,.028],[Math.cos(mid)*radius,Math.sin(mid)*radius,.028],[Math.cos(b)*radius,Math.sin(b)*radius,.028]],.017,'#ffe4a3');trails.add(trail);}
  for(let i=0;i<8;i++){const x=(i/7-.5)*cue.width*.91,y=(i%2?-.18:.18)*cue.height;trails.add(storyEffectsTube([[x,y-.13,-.065],[x+.12,y+.14,-.065]],.02,'#ffe4a3'));}
  const names=new THREE.Mesh(new THREE.PlaneGeometry(cue.width,cue.height*.58),storyEffectsMaterial('#ffffff',{map:storyEffectsPaperTexture(cue.label,'ink')}));names.position.set(0,-cue.height*.56,.13);group.add(names);
  for(const side of [-1,1]){const dot=new THREE.Mesh(new THREE.OctahedronGeometry(.11,0),storyEffectsMaterial('#ffe0a0'));dot.position.set(side*cue.width*.46,-cue.height*.6,.05);group.add(dot);}
  group.userData.storyEffectParts={strokes,names,trails,vertices:vertices.length/3};return group;
}
function storyEffectsArchShape(w,h,inset=0){
  const half=Math.max(.05,w*.5-inset),bottom=inset,shoulder=h*.65-inset,top=h-inset,shape=new THREE.Shape();
  shape.moveTo(-half,bottom);shape.lineTo(half,bottom);shape.lineTo(half,shoulder);shape.quadraticCurveTo(half*.94,h*.88-inset,0,top);shape.quadraticCurveTo(-half*.94,h*.88-inset,-half,shoulder);shape.closePath();return shape;
}
function storyEffectsArchHole(shape,offset){return new THREE.Path(shape.getPoints(32).map(point=>new THREE.Vector2(point.x,point.y+offset)));}
function storyEffectsPortal(cue){
  const group=new THREE.Group(),w=cue.width,h=cue.height,outline=storyEffectsArchShape(w,h);outline.holes.push(storyEffectsArchHole(storyEffectsArchShape(w-.32,h-.32),.16));
  const frame=storyEffectsExtrude(outline,.17,'#cb9c51');group.add(frame);
  const rear=storyEffectsArchShape(w+.28,h+.14);rear.holes.push(storyEffectsArchHole(storyEffectsArchShape(w-.3,h-.28),.16));const backing=storyEffectsExtrude(rear,.14,'#67472d');backing.position.z=-.23;group.add(backing);
  const rimShape=storyEffectsArchShape(w-.05,h-.05);rimShape.holes.push(storyEffectsArchHole(storyEffectsArchShape(w-.16,h-.16),.06));const rim=storyEffectsExtrude(rimShape,.055,'#f1d49a');rim.position.z=.13;group.add(rim);
  const carvings=new THREE.Group();group.add(carvings);
  for(const side of [-1,1]){
    const column=new THREE.Mesh(new THREE.BoxGeometry(.09,h*.64,.12),storyEffectsMaterial('#a77439'));column.position.set(side*(w*.5+.095),h*.32,-.09);carvings.add(column);
    for(let i=0;i<4;i++){const y=h*(.15+i*.12),points=[];for(let j=0;j<=14;j++){const a=j*Math.PI/7,r=.095*(1-j/20);points.push([side*(w*.5+.04)+Math.sin(a)*r,y+Math.cos(a)*r,.12]);}carvings.add(storyEffectsTube(points,.017,'#e8c483'));}
    const buttress=new THREE.Mesh(new THREE.BoxGeometry(.2,.2,.28),storyEffectsMaterial('#d7af6b'));buttress.position.set(side*(w*.5+.07),.12,-.07);carvings.add(buttress);
    for(const fraction of [.67,.75,.83,.91]){const x=side*w*.5*(1-(fraction-.65)/.35),gem=new THREE.Mesh(new THREE.OctahedronGeometry(.045,0),storyEffectsMaterial('#f6dda5'));gem.position.set(x,h*fraction,.17);carvings.add(gem);}
  }
  const crest=new THREE.Mesh(new THREE.OctahedronGeometry(.12,0),storyEffectsMaterial('#f8dea4'));crest.position.set(0,h-.04,.2);carvings.add(crest);
  const doors=[];
  for(const side of [-1,1]){
    const hinge=new THREE.Group();hinge.position.set(side*(w*.5-.14),0,.015);group.add(hinge);
    const panel=new THREE.Mesh(new THREE.BoxGeometry(w*.46,h*.65,.09),storyEffectsMaterial('#755133'));panel.position.set(-side*w*.23,h*.325,0);hinge.add(panel);
    const ornament=new THREE.Mesh(new THREE.BoxGeometry(w*.44,h*.63,.025),storyEffectsMaterial('#c39856'));ornament.position.copy(panel.position);ornament.position.z=.06;hinge.add(ornament);
    const illustrated=new THREE.Mesh(new THREE.PlaneGeometry(w*.42,h*.61),storyEffectsMaterial('#ffffff',{map:storyEffectsDoorTexture(side)}));illustrated.position.copy(panel.position);illustrated.position.z=.085;hinge.add(illustrated);
    const pull=new THREE.Mesh(new THREE.TorusGeometry(.055,.017,6,20),storyEffectsMaterial('#e9c891'));pull.position.set(-side*w*.4,h*.29,.13);hinge.add(pull);
    const fastener=new THREE.Mesh(new THREE.OctahedronGeometry(.07,0),storyEffectsMaterial('#ddb56d'));fastener.position.set(pull.position.x,h*.31,.13);hinge.add(fastener);doors.push({side,hinge});
  }
  const stars=new THREE.Group();stars.position.z=-.72;group.add(stars);
  for(let i=0;i<28;i++){const u=((i*97+41)%997)/997,v=((i*223+71)%991)/991,star=new THREE.Mesh(new THREE.OctahedronGeometry(.018+(i%5)*.008,0),storyEffectsMaterial(i%3?'#e2c58b':'#c8d2e7'));star.position.set((u-.5)*w*.75,.2+v*h*.8,-.11*(i%4));stars.add(star);}
  // A translucent violet window has genuine separation from the front arch.
  const window=new THREE.Mesh(new THREE.ShapeGeometry(storyEffectsArchShape(w-.38,h-.34)),storyEffectsMaterial('#211b38',{opacity:.22}));window.position.set(0,.16,-1.05);group.add(window);
  const points=[];for(const p of outline.getPoints(64))points.push(p.x,p.y,.12);
  const traceGeometry=new THREE.BufferGeometry();traceGeometry.setAttribute('position',new THREE.Float32BufferAttribute(points,3));
  const trace=new THREE.Line(traceGeometry,new THREE.LineBasicMaterial({color:'#fff1bd',transparent:true,depthWrite:false,fog:false,toneMapped:false}));group.add(trace);
  group.userData.storyEffectParts={frame,backing,rim,carvings,doors,stars,window,trace,traceCount:points.length/3};return group;
}
function storyEffectsBuild(cue){const group=cue.effect==='page'?storyEffectsPage(cue):cue.effect==='burst'?storyEffectsBurst(cue):cue.effect==='ink'?storyEffectsInk(cue):storyEffectsPortal(cue);group.name=cue.label;group.userData.storyEffectId=cue.id;return group;}
function storyEffectsDispose(){
  const stage=storyEffectsStage;if(!stage)return;
  scene.remove(stage.group);const geometries=new Set(),materials=new Set(),textures=new Set();
  stage.group.traverse(object=>{if(object.geometry)geometries.add(object.geometry);for(const material of Array.isArray(object.material)?object.material:object.material?[object.material]:[]){materials.add(material);if(material.map)textures.add(material.map);}});
  for(const item of geometries)item.dispose();for(const item of materials)item.dispose();for(const item of textures)item.dispose();storyEffectsStage=null;
}
function storyEffectsEnsure(c,model){
  const signature=JSON.stringify(model.cues.map(cue=>[cue.id,cue.effect,cue.width,cue.height,cue.label]));
  if(storyEffectsStage?.owner===c&&storyEffectsStage.signature===signature)return storyEffectsStage;
  storyEffectsDispose();const group=new THREE.Group();group.name='Story effects · native paper magic';group.userData.editorOnly=true;scene.add(group);
  const items=new Map();for(const cue of model.cues){const object=storyEffectsBuild(cue);group.add(object);items.set(cue.id,object);}
  storyEffectsStage={owner:c,group,items,signature};return storyEffectsStage;
}
function storyEffectsPose(object,cue,sample){
  const p=sample.progress,s=cue.strength,data=object.userData.storyEffectParts;
  object.position.set(cue.x,cue.y,cue.z);object.rotation.set(0,0,cue.rotation);object.scale.setScalar(1);object.visible=sample.active&&sample.opacity>.001;
  storyApplyOpacity(object,sample.opacity);
  if(cue.effect==='page'){
    object.position.x+=Math.sin(p*Math.PI*2)*.38*s;object.position.y+=Math.sin(p*Math.PI)*.7*s;
    object.rotation.z+=Math.sin(p*Math.PI*4)*.07*s;data.hinge.rotation.set(-.75*(1-storyEffectsSmooth(p/.3)),Math.sin(p*Math.PI*3)*.18*s,0);
  }else if(cue.effect==='burst'){
    data.rings.forEach((ring,i)=>{const radius=.1+storyEffectsSmooth(Math.min(1,p*1.45-i*.1))*(1+i*.16)*s;ring.scale.setScalar(radius);ring.material.opacity=sample.opacity*(1-p*.55);});
    data.chips.forEach((chip,i)=>{const a=i*Math.PI/6+p*.4,r=(.15+p*data.radius)*s;chip.position.set(Math.cos(a)*r,Math.sin(a)*r,-.12*(i%3));chip.rotation.z=-a+p*.6;chip.scale.setScalar(1-p*.7);});
  }else if(cue.effect==='ink'){
    data.strokes.geometry.setDrawRange(0,Math.floor(data.vertices*sample.draw/2)*2);data.trails.children.forEach((trail,i)=>{trail.visible=i<Math.ceil(data.trails.children.length*sample.draw);});data.names.material.opacity=sample.opacity*storyEffectsSmooth((p-.22)/.33);data.strokes.rotation.z=.025*Math.sin(p*Math.PI);data.trails.rotation.z=data.strokes.rotation.z;object.position.y+=Math.sin(p*Math.PI)*.12*s;
  }else{
    data.frame.visible=p>=.31;data.backing.visible=p>=.31;data.rim.visible=p>=.31;data.carvings.visible=p>=.31;data.frame.material.opacity=sample.opacity*.9;data.backing.material.opacity=sample.opacity*.85;
    data.trace.geometry.setDrawRange(0,Math.max(1,Math.floor(data.traceCount*sample.draw)));data.trace.material.opacity=sample.opacity;
    for(const door of data.doors){door.hinge.visible=p>=.31;door.hinge.rotation.y=-door.side*sample.open*1.38;}
    data.stars.visible=sample.open>.005;data.stars.rotation.z=sample.open*.035;data.window.visible=sample.open>.005;data.window.material.opacity=.65*sample.opacity*sample.open;
    data.stars.children.forEach((star,i)=>{star.material.opacity=sample.opacity*sample.open*(.6+.4*Math.sin(p*8+i*1.71)**2);});
  }
}
function storyEffectsRender(){
  const c=animeCine,model=storyEffectsModel();if(!c||!storyEffectsProject()||!model.enabled||!model.cues.length){storyEffectsDispose();return;}
  const stage=storyEffectsEnsure(c,model),parent=c.layers.effects;
  stage.group.visible=!!parent?.visible&&storyAuthoredVisible('effects')&&c.layerSettings.effects!==false;
  const cast=[c.cast.kami,c.cast.wisp].filter(Boolean);scene.updateMatrixWorld(true);
  const behind=Math.min(...cast.map(object=>new THREE.Box3().setFromObject(object).min.z))-1.6;
  const parentOpacity=storySample('effects',c.elapsed).opacity;
  for(const cue of model.cues){const object=stage.items.get(cue.id),sample=storyEffectsSample(cue.id,c.elapsed);storyEffectsPose(object,cue,{...sample,opacity:sample.opacity*parentOpacity});if(!object.visible)continue;
    object.updateWorldMatrix(true,true);const bounds=new THREE.Box3().setFromObject(object),front=Math.min(behind,perspectiveCamera.position.z-7);
    if(bounds.max.z>front)object.position.z-=bounds.max.z-front+.002;
  }
  stage.group.updateWorldMatrix(true,true);
}
const storyEffectsPreviousRender=storyRender,storyEffectsPreviousEnd=animeEndCinematic,storyEffectsPreviousNotify=storyNotify;
storyRender=function(){const result=storyEffectsPreviousRender();storyEffectsRender();return result;};
animeEndCinematic=function(){storyEffectsDispose();return storyEffectsPreviousEnd();};
storyNotify=function(){storyEffectsInvalidate();storyEffectsPreviousNotify();if(typeof storyEffectsEditorSync==='function')storyEffectsEditorSync();};
function storyEffectsStatus(){
  const model=storyEffectsModel(),stage=storyEffectsStage,items=[];scene.updateMatrixWorld(true);perspectiveCamera.updateMatrixWorld(true);
  const c=animeCine,castMin=c?Math.min(...[c.cast.kami,c.cast.wisp].map(object=>new THREE.Box3().setFromObject(object).min.z)):null;
  for(const cue of model.cues){const object=stage?.items.get(cue.id);if(!object)continue;const bounds=new THREE.Box3().setFromObject(object),center=bounds.getCenter(new THREE.Vector3()),screen=center.clone().project(perspectiveCamera);let meshes=0;object.traverse(child=>{if(child.isMesh)meshes++;});
    const data=object.userData.storyEffectParts,parts=cue.effect==='page'?{hingeRotation:[data.hinge.rotation.x,data.hinge.rotation.y,data.hinge.rotation.z]}:
      cue.effect==='burst'?{ringScales:data.rings.map(ring=>ring.scale.toArray()),chipWorldPositions:data.chips.map(chip=>chip.getWorldPosition(new THREE.Vector3()).toArray())}:
      cue.effect==='ink'?{strokeDrawRange:{...data.strokes.geometry.drawRange},strokeVertexCount:data.strokes.geometry.getAttribute('position').count,nameOpacity:data.names.material.opacity,trailCount:data.trails.children.length,visibleTrails:data.trails.children.filter(trail=>trail.visible).length}:
      {traceDrawRange:{...data.trace.geometry.drawRange},traceVertexCount:data.trace.geometry.getAttribute('position').count,doors:data.doors.map(door=>({side:door.side,rotationY:door.hinge.rotation.y,visible:door.hinge.visible})),starsVisible:data.stars.visible,starCount:data.stars.children.length,windowOpacity:data.window.material.opacity};
    items.push({id:cue.id,effect:cue.effect,visible:object.visible&&stage.group.visible,position:object.position.toArray(),matrix:object.matrixWorld.toArray(),bounds:{min:bounds.min.toArray(),max:bounds.max.toArray()},screen:[screen.x*.5+.5,.5-screen.y*.5],depthSpan:bounds.max.z-bounds.min.z,meshCount:meshes,behindCast:bounds.max.z<castMin-1.59,cameraGap:perspectiveCamera.position.z-bounds.max.z,parts,sample:storyEffectsSample(cue.id,c?.elapsed||0)});
  }
  return {schema:STORY_EFFECTS_SCHEMA,enabled:model.enabled,active:!!stage,elapsed:c?.elapsed||0,poolSize:stage?.items.size||0,visibleLayer:stage?.group.visible||false,activeCues:items.filter(item=>item.visible).map(item=>item.id),items};
}
window.SWYRL_ENGINE_STORY_EFFECTS=Object.freeze({model:()=>storyCopy(storyEffectsModel()),upsert:storyEffectsUpsert,remove:storyEffectsRemove,configure:storyEffectsConfigure,sample:storyEffectsSample,status:storyEffectsStatus});
const storyEffectsPreviousCollectProject=stRunCollectProject;
stRunCollectProject=function(run){
  const record=storyEffectsPreviousCollectProject(run),c=animeCine;
  // Keep every older starter's export unchanged. This profile records the
  // actual cinematic clones and effect geometry, which are native Groups and
  // therefore do not appear in the recorder's original scene-extra Mesh scan.
  if(!c||!storyEffectsProject()||currentProject.animeStoryEffects?.schema!==STORY_EFFECTS_SCHEMA)return record;
  const frustum=stRunFrustum(),objects=[['kami',c.cast.kami],['swyrlz',c.cast.wisp],...['background','atmosphere','midground','effects','foreground','book'].map(id=>[id,c.layers[id]])];
  for(const [layer,object]of objects){if(!object)continue;const id='anime-live-'+layer;record.entities[id]=stRunBaseEntity(run,id,object,{name:layer+' · live paper theatre',type:'anime-live-'+layer,kind:layer==='kami'||layer==='swyrlz'?'paper-character':'paper-scenery',origin:'runtime',baked:false,authoredVisible:storyAuthoredVisible(layer),playerVisible:stRunObjectVisible(object),layers:[layer],tags:['anime-stage','cinematic-clone'],...stRunParts(run,object)},frustum);}
  const effects=storyEffectsStatus();
  for(const item of effects.items){const object=storyEffectsStage?.items.get(item.id);if(!object)continue;const id='anime-effect-'+item.id;record.entities[id]=stRunBaseEntity(run,id,object,{name:item.sample.label,type:'anime-effect-'+item.effect,kind:'paper-magic',origin:'runtime',baked:false,authoredVisible:true,playerVisible:item.visible,layers:['effects'],tags:['anime-stage','story-effect'],storyEffect:stRunSafe({cue:item.sample,parts:item.parts,visible:item.visible,behindCast:item.behindCast,cameraGap:item.cameraGap}),...stRunParts(run,object)},frustum);}
  record.game.cinematic={elapsed:stRunNumber(c.elapsed),duration:stRunNumber(storyTimeline().duration),rate:c.rate??1,chapter:storyBeat(c.elapsed)?.title||null,performance:typeof performanceStatus==='function'?stRunSafe(performanceStatus(c.elapsed)):null,storyEffects:stRunSafe({schema:effects.schema,enabled:effects.enabled,activeCues:effects.activeCues}),faces:stRunSafe({kami:c.cast.kami.userData.rig?.face?.applied||null,swyrlz:c.cast.wisp.userData.rig?.face?.applied||null})};
  return record;
};
