/* SE362_MODEL_VR_CONTROLLER_LABELS_START */
// Quest 2 controller models + labels. Presentation only: no input dispatch or native edits.
const se362ControllerLabels=(()=>{
 const models=new Map(), entries=new Map();
 let generation=0, currentLayer='', loadError='', disposed=true;
 const singleKeys=['RT','LT','RG','LG','RS','LS','A','B','X','Y'];
 const partKey={RT:'trigger',LT:'trigger',RG:'squeeze',LG:'squeeze',RS:'thumbstick',LS:'thumbstick',A:'a_button',B:'b_button',X:'x_button',Y:'y_button'};
 const title={
  select:'Select',multiselect:'Add',grab:'Edit',pan:'Workbench',navigate:'Pan',orbit:'Orbit',
  tool:'Next tool','tool-wheel':'Tool wheel',cancel:'Cancel',palette:'Palette',
  'category-wheel':'Studios',undo:'Undo',redo:'Redo',focus:'Focus',precision:'Precision',
  snap:'Snap',stroke:'Sculpt',sample:'Sample',radius:'Size / Power',strength:'Strength',
  'temporary-smooth':'Smooth','two-hand':'Two hands',zoom:'Zoom',fine:'Fine',
  'open-settings':'Settings',wireframe:'Wireframe','toggle-snap':'Snap',
  'reset-camera':'Recenter',mirror:'Mirror',preview:'Preview'
 };
 const short=(value)=>String(value||'').replace(/[<>]/g,'').slice(0,27);
 const tint=(s)=>s==='left'?-1:1;
 const defaults=(side)=>{
  const h=tint(side);
  return {
   [side==='left'?'LT':'RT']:[h*.006,-.060,-.060],
   [side==='left'?'LG':'RG']:[h*.042,-.030,.009],
   [side==='left'?'LS':'RS']:[h*.027,-.019,-.053],
   [side==='left'?'X':'A']:[-h*.005,-.007,-.032],
   [side==='left'?'Y':'B']:[-h*.005,-.022,-.045]
  };
 };
 function posFor(key,side,asset){
  const fallback=defaults(side)[key]||[0,0,0];
  const mesh=asset?.parts?.find(p=>p.key===partKey[key])?.mesh;
  if(!mesh?.positions?.length)return fallback;
  const mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity];
  for(let i=0;i<mesh.positions.length;i+=3)
   for(let j=0;j<3;j++){const n=mesh.positions[i+j];mn[j]=Math.min(mn[j],n);mx[j]=Math.max(mx[j],n);}
  return mn.map((n,i)=>(n+mx[i])*.05-(i===1?.21:0));
 }
 function label(entry,key){
  const c=document.createElement('canvas');c.width=384;c.height=112;
  const texture=new THREE.CanvasTexture(c);texture.colorSpace=THREE.SRGBColorSpace||texture.colorSpace;
  const material=new THREE.SpriteMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false,opacity:.92});
  const sprite=new THREE.Sprite(material);sprite.scale.set(.073,.021,1);
  sprite.renderOrder=9050;sprite.frustumCulled=false;sprite.userData.se362Key=key;
  entry.root.add(sprite);entry.labels.set(key,{sprite,texture,material,canvas:c,text:'',pressed:false});
 }
 function repaint(b,key,description){
  const text=short(description);if(b.text===text)return;b.text=text;
  const c=b.canvas,ctx=c.getContext('2d');if(!ctx)return;
  ctx.clearRect(0,0,c.width,c.height);
  ctx.fillStyle='rgba(17,24,43,.91)';
  ctx.beginPath();if(ctx.roundRect)ctx.roundRect(2,3,380,105,18);else ctx.rect(2,3,380,105);ctx.fill();
  ctx.lineWidth=3;ctx.strokeStyle='rgba(144,240,221,.62)';ctx.stroke();
  ctx.font='bold 25px system-ui,sans-serif';ctx.textBaseline='middle';ctx.textAlign='left';
  ctx.fillStyle='#84f3de';ctx.fillText(key,17,54);
  ctx.fillStyle='#f6f8ff';ctx.font='600 25px system-ui,sans-serif';
  const usable=298;let size=25;
  while(ctx.measureText(text).width>usable&&size>15){size--;ctx.font='600 '+size+'px system-ui,sans-serif';}
  ctx.fillText(text,78,54,usable);
  b.texture.needsUpdate=true;
 }
 function setup(records){
  dispose();disposed=false;generation++;
  for(const record of records){
   const root=new THREE.Group();root.name='Quest Touch · controller model and labels';
   root.userData.editorOnly=true;record.grip.add(root);
   const entry={record,root,labels:new Map(),model:null,texture:null,material:null,side:null,asset:null,abort:null,attempted:null,ready:false};
   entries.set(record,entry);
   for(const key of singleKeys)label(entry,key);
  }
 }
 function renderAsset(entry,asset,side,epoch){
  if(disposed||epoch!==generation||entry.side!==side)return;
  if(asset?.schema!=='swrlz-webxr-controller-v1'||asset.side!==side||!Array.isArray(asset.parts)||asset.parts.length!==7)
   throw Error('Quest controller asset schema mismatch.');
  const texture=new THREE.TextureLoader().load(asset.colorTexturePNG);
  texture.flipY=false;texture.colorSpace=THREE.SRGBColorSpace||texture.colorSpace;
  const material=new THREE.MeshStandardMaterial({map:texture,color:0xffffff,roughness:.67,metalness:.07,side:THREE.DoubleSide});
  const model=new THREE.Group();model.name='Quest 2 Touch · '+side+' · WebXR reference mesh';
  model.position.set(0,-.21,0);model.scale.setScalar(.1);model.userData.editorOnly=true;
  try{
   for(const part of asset.parts){
    const m=part.mesh;
    if(!Array.isArray(m?.positions)||m.positions.length<9||m.positions.length>27000||
      !Array.isArray(m.uvs)||m.uvs.length!==m.positions.length/3*2||!Array.isArray(m.indices)||m.indices.length>48000)
      throw Error('Invalid controller mesh.');
    const geometry=new THREE.BufferGeometry();
    geometry.setAttribute('position',new THREE.Float32BufferAttribute(m.positions,3));
    geometry.setAttribute('uv',new THREE.Float32BufferAttribute(m.uvs,2));
    geometry.setIndex(m.indices);geometry.computeVertexNormals();
    const mesh=new THREE.Mesh(geometry,material);mesh.name=part.title;mesh.frustumCulled=false;model.add(mesh);
   }
   entry.root.add(model);entry.model=model;entry.texture=texture;entry.material=material;entry.asset=asset;entry.ready=true;
   models.set(side,true);
   for(const [key,b] of entry.labels){
    const base=posFor(key,side,asset),h=tint(side),offset=(key==='LG'||key==='RG')?[h*.042,0,.018]:
      (key==='LT'||key==='RT')?[h*.023,.010,-.032]:
      (key==='LS'||key==='RS')?[h*.012,.033,-.025]:[h*.034,.025,-.027];
    b.sprite.position.set(base[0]+offset[0],base[1]+offset[1],base[2]+offset[2]);
   }
  }catch(error){
   for(const m of model.children)m.geometry?.dispose();texture.dispose();material.dispose();throw error;
  }
 }
 function load(entry,side){
  if(entry.attempted===side)return;entry.attempted=side;entry.side=side;
  const epoch=generation,controller=new AbortController();entry.abort=controller;
  const url=new URL('assets/models/webxr-touch-v3/'+side+'.json',document.baseURI);
  fetch(url.href,{signal:controller.signal}).then(response=>{
   if(!response.ok)throw Error('HTTP '+response.status+' loading '+side+' controller');
   return response.json();
  }).then(asset=>renderAsset(entry,asset,side,epoch)).catch(error=>{
   if(error.name!=='AbortError')loadError=String(error?.message||error).slice(0,110);
  });
 }
 function labelFor(action,s){
  if(action==='grab')return ({move:'Move',rotate:'Rotate',scale:'Scale',extrude:'Extrude',
   'two-hand':'Two hands',inspect:'No edit',draw:'Transform',sculpt:'Transform'})[s.mode]||'Edit';
  if(action==='stroke')return s.mode==='draw'?'Draw outline':s.mode==='lasso'?'Trace lasso':s.mode==='sculpt'?
   (s.sculptTool||'sculpt').replace(/^./,c=>c.toUpperCase()):'Select';
  if(action==='tool')return s.mode==='sculpt'?'Next brush':'Next tool';
  if(action==='tool-wheel')return s.mode==='sculpt'?'Brush wheel':'Tool wheel';
  if(action==='sample'&&s.mode==='draw')return 'Sample';
  return title[action]||action;
 }
 function bindings(s){
  const ctx=['sculpt','draw','lasso'].includes(s.mode)?'sculpt':'model';
  let profile;try{profile=window.SWYRL_VR_CONTROLS?.currentProfile?.();}catch(_){}
  const source=profile?.bindings||SE350_MODEL_VR_BINDINGS;
  const result={};
  const rows=[...(source[ctx]||[]),...(source.global||[])];
  for(const row of rows){
   const [action,expression]=row;
   if(typeof expression!=='string'||!['tap:','hold:','axis:'].some(k=>expression.startsWith(k)))continue;
   const key=expression.split(':')[1];if(!singleKeys.includes(key))continue;
   const value=labelFor(action,s);
   if(!result[key])result[key]=value;
   else if(expression.startsWith('hold:')&&result[key]!==value)result[key]+=' / '+value;
  }
  if(s.mode==='extrude')result.RG='Extrude';
  if(s.mode==='two-hand'){result.RG='Two hands';result.LG='Two hands';}
  if(s.mode==='draw')result.RT='Draw outline';
  if(s.mode==='lasso')result.RT='Trace lasso';
  if(s.mode==='inspect')result.RG='No edit';
  return result;
 }
 function frame(s){
  if(disposed)return;
  const profile=s.inputSample?.profile?.id||'default';
  const layer=[s.mode,s.sculptTool,s.page,profile].join(':');
  if(layer!==currentLayer||s.inputSample?.profileChanged){
   currentLayer=layer;const map=bindings(s);
   for(const entry of entries.values()){
    for(const [key,b] of entry.labels)repaint(b,key,map[key]||'—');
   }
  }
  for(const entry of entries.values()){
   const r=entry.record,side=r.input?.handedness;
   if((side==='left'||side==='right')&&entry.attempted!==side)load(entry,side);
   entry.root.visible=!!r.gripTracked&&!!side;
   if(!entry.ready){
    const fallback=defaults(side==='left'?'left':'right');
    for(const [key,b] of entry.labels){
     const a=fallback[key];if(a)b.sprite.position.set(a[0],a[1],a[2]);
    }
   }
   for(const [key,b] of entry.labels){
    const down=!!s.inputSample?.buttons?.[key]?.physical;
    if(b.pressed!==down){
     b.pressed=down;b.material.color.setHex(down?0x86ffe8:0xffffff);
     b.sprite.scale.set(down ? .082 : .073,down ? .023 : .021,1);
    }
    // All main inputs remain discoverable, but physically unused side buttons are hidden.
    b.sprite.visible=side==='left'?['LT','LG','LS','X','Y'].includes(key):
      side==='right'?['RT','RG','RS','A','B'].includes(key):false;
   }
  }
 }
 function hasModel(record){return !!entries.get(record)?.ready;}
 function dispose(){
  disposed=true;generation++;
  for(const entry of entries.values()){
   entry.abort?.abort();
   entry.root.removeFromParent();
   for(const b of entry.labels.values()){b.material.dispose();b.texture.dispose();}
   if(entry.model)entry.model.traverse(o=>{if(o.isMesh)o.geometry?.dispose();});
   entry.texture?.dispose();entry.material?.dispose();
  }
  entries.clear();models.clear();currentLayer='';
 }
 return Object.freeze({setup,frame,dispose,hasModel,inspect:()=>({ready:[...models.keys()],
  layer:currentLayer,labelCount:[...entries.values()].reduce((n,e)=>n+e.labels.size,0),
  assetSource:'bundled oculus-touch-v3 MIT',loadError})});
})();
/* SE362_MODEL_VR_CONTROLLER_LABELS_END */
