/* SE362_CONTROLLER_HINTS_START */
// Quest 2 Touch models and low-cost, controller-attached contextual control labels.
// One WebXR renderer/input loop; native controller assets already shipped for Model Studio starters.
const se362LiveControllers=new Set();
const se362Keys={
 left:[['LT','trigger'],['LG','squeeze'],['LS','thumbstick'],['X','x_button'],['Y','y_button']],
 right:[['RT','trigger'],['RG','squeeze'],['RS','thumbstick'],['A','a_button'],['B','b_button']]
};
const se362TempCamera=new THREE.Vector3();
function se362PartCenter(part){
 const p=part?.mesh?.positions;if(!Array.isArray(p)||p.length<9)return null;
 let x=0,y=0,z=0,min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
 for(let i=0;i<p.length;i+=3)for(let axis=0;axis<3;axis++){
  const v=p[i+axis];min[axis]=Math.min(min[axis],v);max[axis]=Math.max(max[axis],v);
 }
 return new THREE.Vector3((min[0]+max[0])/2,(min[1]+max[1])/2,(min[2]+max[2])/2);
}
function se362FallbackPoint(key){
 const points={RT:[.033,-.013,-.05],LT:[-.033,-.013,-.05],
 RG:[-.035,-.04,.026],LG:[.035,-.04,.026],
 RS:[0,.030,-.018],LS:[0,.030,-.018],
 A:[.060,.016,-.015],B:[-.060,.016,-.015],
 X:[-.060,.016,-.015],Y:[.060,.016,-.015]};
 return new THREE.Vector3(...(points[key]||[0,0,0]));
}
function se362LabelPoint(side,key,part){
 if(!part)return se362FallbackPoint(key);
 // Asset coordinates are controller-model authoring units; origin is grip-space.
 const point=se362PartCenter(part).sub(new THREE.Vector3(0,1.79,0)).multiplyScalar(.09);
 const offsets={
  LT:[-.038,-.008,-.042],RT:[.038,-.008,-.042],
  LG:[.043,-.009,.035],RG:[-.043,-.009,.035],
  LS:[-.010,.042,-.012],RS:[.010,.042,-.012],
  X:[-.062,.019,-.019],Y:[.063,.019,-.019],
  A:[.063,.019,-.019],B:[-.062,.019,-.019]};
 return point.add(new THREE.Vector3(...(offsets[key]||[0,.025,0])));
}
function se362HintCanvas(key){
 const canvas=document.createElement('canvas');canvas.width=512;canvas.height=144;
 const texture=new THREE.CanvasTexture(canvas);
 if(THREE.SRGBColorSpace)texture.colorSpace=THREE.SRGBColorSpace;
 const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false,side:THREE.DoubleSide});
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(.094,.0264),material);
 mesh.renderOrder=9400;mesh.frustumCulled=false;mesh.name='Quest Touch · '+key+' contextual hint';
 mesh.userData.editorOnly=true;mesh.userData.se362Hint=true;
 return {key,mesh,canvas,texture,material,text:'',down:false};
}
function se362DrawHint(hint,title,down=false,expanded=false){
 const label=String(title||'').slice(0,34);
 if(hint.text===label&&hint.down===down&&hint.expanded===expanded)return;
 hint.text=label;hint.down=down;hint.expanded=expanded;
 const c=hint.canvas.getContext('2d');if(!c)return;
 c.clearRect(0,0,512,144);
 if(!label){hint.mesh.visible=false;return;}
 c.fillStyle=down?'rgba(29,101,94,.96)':'rgba(13,20,39,.88)';
 c.strokeStyle=down?'#adffee':'#a68bd9';c.lineWidth=5;
 c.beginPath();c.roundRect(5,7,502,130,22);c.fill();c.stroke();
 c.fillStyle=down?'#eafff4':'#d7c9fc';
 c.font='bold 28px system-ui,sans-serif';c.textAlign='left';c.textBaseline='middle';
 c.fillText(hint.key,21,73);
 c.fillStyle='#eef5ff';c.font='600 31px system-ui,sans-serif';
 let size=31;
 while(c.measureText(label).width>385&&size>19){size-=2;c.font='600 '+size+'px system-ui,sans-serif';}
 c.fillText(label,98,73,391);
 hint.texture.needsUpdate=true;hint.mesh.visible=true;
}
function se362CleanLabel(action,s){
 const mode=s.mode;
 const titles={
  select:'Select',multiselect:'Add selection',sample:'Sample surface',
  pan:'Move workspace',navigate:'Pan view',orbit:'Orbit camera',zoom:'Zoom view',
  radius:'Brush size/strength',strength:'Brush strength',
  tool:mode==='sculpt'?'Next brush':'Next tool',
  'tool-wheel':mode==='sculpt'?'Brush wheel':'Tool wheel',
  'category-wheel':'Studio wheel',palette:'Tool palette',undo:'Undo',redo:'Redo',
  cancel:'Cancel',focus:'Focus',precision:'Precision',snap:'Snap',
  'toggle-snap':'Toggle snap','open-settings':'VR settings',
  wireframe:'Wireframe',fine:'Fine edit',mirror:'Mirror',preview:'Preview',
  'reset-camera':'Recenter', 'temporary-smooth':'Hold smooth'
 };
 if(action==='stroke')return mode==='draw'?'Draw outline':mode==='lasso'?'Trace lasso':'Sculpt '+s.sculptTool;
 if(action==='grab'){
  if(mode==='move')return 'Move selected';
  if(mode==='rotate')return 'Rotate selected';
  if(mode==='scale')return 'Scale selected';
  if(mode==='extrude')return 'Pull to extrude';
  if(mode==='two-hand')return 'Two-hand edit';
  // Grip isn't an edit shortcut in Inspect, Sculpt, Draw or Lasso modes.
  return '';
 }
 if(action==='two-hand')return mode==='two-hand'?'Two-hand edit':'';
 return titles[action]||'';
}
function se362CurrentBindings(s){
 const context=['sculpt','draw','lasso'].includes(s.mode)?'sculpt':'model';
 let source=null;
 try{source=window.SWYRL_VR_CONTROLS?.currentProfile?.();}catch(_){}
 const rows=source?.bindings?.[context]||SE350_MODEL_VR_BINDINGS[context]||[];
 const globals=source?.bindings?.global||[];
 const direct=Object.create(null),secondary=Object.create(null),occupied=new Set();
 for(const row of [...rows,...globals]){
  if(!Array.isArray(row)||row.length<2)continue;
  const [action,binding]=row;
  const match=/^(tap|hold|axis):([A-Z]+)$/.exec(binding);
  if(!match)continue;
  const key=match[2];if(!Object.prototype.hasOwnProperty.call(direct,key))direct[key]=[];
  const text=se362CleanLabel(action,s);
  if(!text||occupied.has(match[1]+':'+key))continue;
  occupied.add(match[1]+':'+key);
  direct[key].push({kind:match[1],text});
 }
 for(const [key,entries] of Object.entries(direct)){
  entries.sort((a,b)=>({axis:0,tap:1,hold:2}[a.kind]-{axis:0,tap:1,hold:2}[b.kind]));
  const first=entries[0]?.text||'',second=entries.find(x=>x.text!==first)?.text;
  secondary[key]=second;
  direct[key]=first;
 }
 return {context,profile:source?.profileId||'default',direct,secondary};
}
function se362MakeVisual(record){
 const side=record.input?.handedness;
 if(!se362Keys[side])return null;
 const root=new THREE.Group();root.name='Quest Touch '+side+' · model and tool labels';
 root.userData.editorOnly=true;record.grip.add(root);
 const hints=new Map();
 for(const [key] of se362Keys[side]){
  const hint=se362HintCanvas(key);
  hint.mesh.position.copy(se362FallbackPoint(key));
  root.add(hint.mesh);hints.set(key,hint);
 }
 const visual={root,hints,side,token:Symbol('controller'),ready:false,model:null,texture:null,material:null,resources:[],lastSignature:''};
 record.se362Visual=visual;se362LiveControllers.add(record);
 return visual;
}
async function se362LoadVisual(record,visual){
 const side=visual.side,session=se340XR.session;
 try{
  let asset=se361ControllerCache.get(side);
  if(!asset){
   const response=await fetch(new URL('assets/models/webxr-touch-v3/'+side+'.json',document.baseURI).href);
   if(!response.ok)throw Error('Controller asset '+response.status);
   asset=await response.json();
   se361StarterCheck(asset,{side});se361ControllerCache.set(side,asset);
  }
  if(record.se362Visual!==visual||se340XR.session!==session||!session)return;
  const material=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.76,metalness:.09,side:THREE.DoubleSide});
  const texture=new THREE.TextureLoader().load(asset.colorTexturePNG);
  if(THREE.SRGBColorSpace)texture.colorSpace=THREE.SRGBColorSpace;
  texture.flipY=false;material.map=texture;material.needsUpdate=true;
  const model=new THREE.Group();model.name='WebXR oculus-touch-v3 '+side+' · MIT';
  // Preserve the original source meshes; normalize only the visual rig space.
  model.scale.setScalar(.09);model.position.y=-1.79*.09;
  const parts=new Map(),resources=[];
  for(const part of asset.parts){
   const source=part.mesh,geo=new THREE.BufferGeometry();
   geo.setAttribute('position',new THREE.Float32BufferAttribute(source.positions,3));
   geo.setAttribute('uv',new THREE.Float32BufferAttribute(source.uvs,2));
   geo.setIndex(source.indices);geo.computeVertexNormals();
   const mesh=new THREE.Mesh(geo,material);mesh.name=part.title;mesh.frustumCulled=false;
   mesh.userData.editorOnly=true;model.add(mesh);resources.push(geo);parts.set(part.key,part);
  }
  if(record.se362Visual!==visual||se340XR.session!==session){
   resources.forEach(g=>g.dispose());material.dispose();texture.dispose();return;
  }
  visual.root.add(model);visual.model=model;visual.material=material;visual.texture=texture;visual.resources=resources;visual.ready=true;
  for(const [key,partKey] of se362Keys[side]){
   const hint=visual.hints.get(key);hint.mesh.position.copy(se362LabelPoint(side,key,parts.get(partKey)));
  }
  record.body.visible=false;visual.lastSignature='';
 }catch(error){
  // Retain the existing tracked grip capsule and functional labels if the
  // optional visual model is unavailable or graphics assets fail.
  if(record.se362Visual===visual){visual.ready=false;visual.lastSignature='';}
 }
}
function se362ControllerConnected(record){
 se362ControllerDisconnected(record);
 if(!record.input||!se340XR.session)return;
 const visual=se362MakeVisual(record);if(visual)void se362LoadVisual(record,visual);
}
function se362ControllerDisconnected(record){
 const v=record.se362Visual;if(!v)return;
 record.se362Visual=null;se362LiveControllers.delete(record);
 v.root.removeFromParent();
 for(const h of v.hints.values()){
  h.mesh.geometry.dispose();h.material.dispose();h.texture.dispose();
 }
 for(const geo of v.resources)geo.dispose();
 v.material?.dispose();v.texture?.dispose();
 v.root.clear();record.body.visible=!!record.gripTracked;
}
function se362Frame(s){
 if(!s.session)return;
 const profile=se362CurrentBindings(s),sample=s.inputSample;
 const expanded=!!(s.helpVisible||s.wheel);
 const signature=JSON.stringify([s.mode,s.sculptTool,s.wheel,expanded,profile.context,profile.profile,profile.direct,profile.secondary]);
 const camera=renderer.xr.getCamera?.(s.camera)||s.camera;
 camera.getWorldPosition(se362TempCamera);
 for(const record of s.controllers){
  const v=record.se362Visual;
  if(!v)continue;
  v.root.visible=!!record.gripTracked;
  record.body.visible=!!record.gripTracked&&!v.ready;
  if(!record.gripTracked)continue;
  for(const [key,hint] of v.hints){
   const down=!!sample?.buttons?.[key]?.physical;
   const main=profile.direct[key]||'';
   const extra=expanded?profile.secondary[key]:'';
   const title=s.wheel&&((key==='A'&&s.wheel!=='studio')||(key==='X'&&s.wheel==='studio'))?'Release to choose':
    main&&extra?main+' / '+extra:main;
   if(v.lastSignature!==signature||hint.down!==down)se362DrawHint(hint,title,down,expanded);
   if(hint.mesh.visible)hint.mesh.lookAt(se362TempCamera);
  }
  v.lastSignature=signature;
 }
}
window.SWYRL_ENGINE_VR_CONTROLLER_HINTS=Object.freeze({
 inspect:()=>({active:!!se340XR.session,models:[...se362LiveControllers].filter(r=>r.se362Visual?.ready).map(r=>r.se362Visual.side),
  labels:[...se362LiveControllers].map(r=>({side:r.se362Visual?.side,visible:!!r.se362Visual?.root.visible,
   bindings:[...r.se362Visual.hints.values()].map(h=>({key:h.key,text:h.text,visible:h.mesh.visible}))}))})
});
 /* SE362_CONTROLLER_HINTS_END */