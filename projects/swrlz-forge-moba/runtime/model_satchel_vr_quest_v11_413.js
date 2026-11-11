/* SE413_SATCHEL_VR_QUEST_START
 * Native Model VR quest: a stationary world-space window, NOT head-follow UI.
 * No second XR renderer/loop; controller input and models retain native ownership.
 * This source is injected after v11.412 tutorial and v11.410 VR integration.
 */
(function se413InstallSatchelVR(){
 'use strict';
 const LESSON='satchel-001', W=.70,H=.525,PX=1024,PY=768;
 const q=()=>se340XR.se413Quest, lesson=()=>window.SWYRL_ENGINE_TUTORIAL_412;
 const active=()=>lesson()?.status?.().active===true;
 const truncate=(s,n)=>String(s||'').slice(0,n);
 function rounded(ctx,x,y,w,h,r,color){
  ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fillStyle=color;ctx.fill();
 }
 function wrap(ctx,text,x,y,maxWidth,lh,maxLines=4){
  const words=String(text||'').split(/\s+/),lines=[];let line='';
  for(const word of words){const next=line?line+' '+word:word;
   if(ctx.measureText(next).width<=maxWidth){line=next;continue;}
   if(line)lines.push(line);line=word;
  }
  if(line)lines.push(line);
  for(let i=0;i<Math.min(lines.length,maxLines);i++){
   let shown=lines[i];if(i===maxLines-1&&lines.length>maxLines)shown=shown.replace(/.{0,2}$/,'…');
   ctx.fillText(shown,x,y+i*lh);
  }
  return Math.min(lines.length,maxLines)*lh;
 }
 function render(force=false){
  const box=q(),api=lesson();if(!box||!api)return;
  const rows=api.steps(),st=api.status(),index=Math.min(6,Math.max(0,box.index)),step=rows[index];
  const signature=JSON.stringify([box.folded,index,rows.map(r=>r.done),box.message,st.projectId]);
  if(!force&&signature===box.signature)return;
  box.signature=signature;
  const c=box.canvas.getContext('2d');c.clearRect(0,0,PX,PY);
  rounded(c,3,3,PX-6,box.folded?114:PY-6,26,'#1f1830');
  c.strokeStyle='#a981d9';c.lineWidth=7;c.strokeRect(4,4,PX-8,box.folded?110:PY-8);
  rounded(c,16,14,PX-32,90,18,'#443058');
  c.fillStyle='#fff2fd';c.font='bold 43px system-ui';c.fillText('APPRENTICE SATCHEL',32,73);
  c.fillStyle='#d9baff';c.font='bold 32px system-ui';c.fillText(box.folded?'OPEN':'FOLD',895,73);
  for(const btn of box.buttons)btn.visible=!box.folded||btn.userData.se340Action==='se413-fold';
  if(box.folded){box.texture.needsUpdate=true;return;}
  c.fillStyle='#aee7c7';c.font='bold 32px system-ui';
  c.fillText('OBJECTIVE '+(index+1)+' / 7',34,156);
  c.fillText(rows.filter(r=>r.done).length+' COMPLETE',790,156);
  rounded(c,32,177,960,13,6,'#4a3a59');
  rounded(c,32,177,960*rows.filter(r=>r.done).length/7,13,6,'#8cdbb6');
  c.fillStyle='#fff9ff';c.font='bold 37px system-ui';
  wrap(c,step?.title||'',32,244,947,42,2);
  c.font='29px system-ui';c.fillStyle='#c4a6ee';
  wrap(c,'TOOL: '+(step?.tool||''),32,322,948,34,2);
  c.font='29px system-ui';c.fillStyle='#f2e9fd';
  wrap(c,step?.task||'',32,408,950,37,4);
  c.fillStyle='#d0b8e8';c.font='italic 27px system-ui';
  wrap(c,'TIP: '+(step?.hint||''),32,559,947,32,2);
  if(box.message){
   c.fillStyle='#a8e8c3';c.font='bold 24px system-ui';
   wrap(c,truncate(box.message,180),32,626,944,28,2);
  }
  const buttons=[['se413-prev','PREV',34,657,185],['se413-check','VERIFY',239,657,220],
   ['se413-mark',step?.done?'REOPEN':'DONE',480,657,265],['se413-next','NEXT',765,657,224]];
  for(const [action,label,x,y,w] of buttons){
   rounded(c,x,y,w,85,14,action==='se413-mark'?'#356d57':'#5d447f');
   c.fillStyle='#fff';c.font='bold 29px system-ui';c.textAlign='center';
   c.fillText(label,x+w/2,y+53);c.textAlign='left';
  }
  box.texture.needsUpdate=true;
 }
 function hit(record){
  const box=q();if(!box||!box.root.visible||!active()||!record?.targetTracked||!se340VisibleSession())return null;
  const ray=se340Cast(record);if(!ray)return null;
  box.root.updateWorldMatrix(true,true);
  // A visible panel background is also a hit target. Never pass a ray through
  // tutorial text into editable geometry; folded state blocks only its fold tab.
  const targets=box.folded?box.buttons.filter(o=>o.visible):[...box.buttons,box.panel];
  const intersections=ray.intersectObjects(targets,false);
  const chosen=intersections[0];if(!chosen)return null;
  return {ui:true,quest:true,target:chosen.object,action:chosen.object.userData.se340Action,
   distance:chosen.distance,point:chosen.point};
 }
 function activate(action,record){
  const box=q(),api=lesson();if(!box||!active())return false;
  const steps=api.steps();
  if(action==='se413-fold'){box.folded=!box.folded;box.message='';}
  else if(action==='se413-prev'||action==='se413-next'){
   box.index=Math.max(0,Math.min(steps.length-1,box.index+(action==='se413-prev'?-1:1)));
   api.choose(box.index);box.message='';
  }else if(action==='se413-mark'){
   const result=api.mark(box.index);box.message=result?.message||'Progress saved on this device.';
  }else if(action==='se413-check'){
   const result=api.check(box.index);box.message=result?.message||'Inspect the actual model before checking off.';
  }else return false;
  se340Pulse(record,.17,22);
  render(true);return true;
 }
 function makeButton(box,id,x,y,w,h){
  const material=new THREE.MeshBasicMaterial({color:'#ffffff',transparent:true,opacity:0,
   depthWrite:false,depthTest:false,side:THREE.DoubleSide});
  const geo=new THREE.PlaneGeometry(w/PX*W,h/PY*H);
  const mesh=new THREE.Mesh(geo,material);
  mesh.position.set((x+w/2)/PX*W-W/2,H/2-(y+h/2)/PY*H,.009);
  mesh.userData.se340Action=id;mesh.userData.editorOnly=true;
  box.root.add(mesh);box.buttons.push(mesh);box.owned.push(material,geo);
 }
 function place(){
  const box=q(),ui=se340XR.ui;if(!box||!ui?.root)return;
  ui.root.updateWorldMatrix(true,true);
  // Deliberately offset in WORLD SPACE. Reposition only on explicit recenter.
  box.root.position.copy(ui.root.localToWorld(new THREE.Vector3(1.02,.07,.02)));
  box.root.quaternion.copy(ui.root.quaternion);
  box.root.updateWorldMatrix(true,true);
 }
 function build(){
  if(!active()||q())return;
  const root=new THREE.Group();root.name='Apprentice Satchel · fixed world-space quest';
  root.userData.editorOnly=true;
  const canvas=document.createElement('canvas');canvas.width=PX;canvas.height=PY;
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
  const material=new THREE.MeshBasicMaterial({map:texture,transparent:true,side:THREE.DoubleSide,
   depthTest:false,depthWrite:false});
  const geo=new THREE.PlaneGeometry(W,H),panel=new THREE.Mesh(geo,material);
  panel.renderOrder=8300;panel.userData.editorOnly=true;root.add(panel);
  const box={root,panel,canvas,texture,buttons:[],owned:[geo,material,texture],
   index:Math.max(0,Math.min(6,Number(lesson()?.status()?.current)||0)),folded:false,message:'',signature:''};
  se340XR.se413Quest=box;
  makeButton(box,'se413-fold',882,15,130,92);
  makeButton(box,'se413-prev',34,657,185,85);
  makeButton(box,'se413-check',239,657,220,85);
  makeButton(box,'se413-mark',480,657,265,85);
  makeButton(box,'se413-next',765,657,224,85);
  se340XR.scene.add(root);place();render(true);
 }
 function dispose(){
  const box=q();if(!box)return;
  box.root.removeFromParent();
  for(const obj of box.owned)try{obj.dispose();}catch(_){}
  se340XR.se413Quest=null;
 }
 const baseMakeStage=se340MakeStage;
 se340MakeStage=function(...a){const result=baseMakeStage.apply(this,a);build();return result;};
 const baseRecenter=se340Recenter;
 se340Recenter=function(...a){const result=baseRecenter.apply(this,a);place();return result;};
 const baseHit=se340Hit;
 se340Hit=function(record,precise=true){
  const ordinary=baseHit.call(this,record,precise),questHit=hit(record);
  return questHit&&(!ordinary||!Number.isFinite(ordinary.distance)||questHit.distance<ordinary.distance)
   ?questHit:ordinary;
 };
 const baseContact=se360MenuContact;
 se360MenuContact=function(record){
  const ordinary=baseContact.call(this,record),questHit=hit(record);
  return questHit&&(!ordinary||questHit.distance<ordinary.distance)?questHit:ordinary;
 };
 const baseTrigger=se340Trigger;
 se340Trigger=function(record,additive=false){
  if(!record?.targetTracked||record.blockTrigger||!se340VisibleSession())return;
  const found=se340Hit(record,false);
  if(found?.quest){record.hit=found;activate(found.action,record);return;}
  return baseTrigger.call(this,record,additive);
 };
 const baseAction=se340ModelXRAction;
 se340ModelXRAction=function(action,record=null){
  if(String(action).startsWith('se413-'))return activate(action,record);
  return baseAction.call(this,action,record);
 };
 const baseFrame=se340ModelXRFrameCore;
 se340ModelXRFrameCore=function(...a){
  if(q()&&se340XR.frameCount%8===0)render();
  return baseFrame.apply(this,a);
 };
 const baseCleanup=se340Cleanup;
 se340Cleanup=function(...a){dispose();return baseCleanup.apply(this,a);};
 window.SWYRL_ENGINE_TUTORIAL_VR_413=Object.freeze({
  inspect:()=>({active:active()&&!!q(),worldSpace:true,step:q()?.index??null,
   folded:!!q()?.folded,sceneOwned:!!q()?.root?.parent}),
  action:(action)=>activate('se413-'+action,null)
 });
})();
 /* SE413_SATCHEL_VR_QUEST_END */