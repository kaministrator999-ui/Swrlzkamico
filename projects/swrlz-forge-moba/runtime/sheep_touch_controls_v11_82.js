// One native game clock, shared orders/collisions, independent pointer owners.
const stMobile={pointer:null,session:null,unit:null,captured:false,x:0,y:0,strength:0,origin:null,enabled:false,utilities:[],open:false,lastReset:'initial'};
const stMobileMedia=matchMedia('(pointer:coarse), (max-width:620px)');
function stMobileReset(reason='released'){
 const unit=stMobile.unit;if(stMobile.session===stSession&&unit){if(unit.order?.joystick)stSetOrder(unit,null);if(stMobile.captured)unit.spiritOrder=null;}
 stMobile.pointer=null;stMobile.session=null;stMobile.unit=null;stMobile.x=stMobile.y=stMobile.strength=0;stMobile.origin=null;stMobile.lastReset=reason;
 const knob=$('stMoveKnob');if(knob)knob.style.transform='translate(-50%,-50%)';$('stMoveStick')?.classList.remove('held');
}
function stMobileCanMove(){const s=stSession;return !!s&&!s.simulate&&stUi.shown&&!paused&&!s.winner&&$('stHelpPanel')?.hidden!==false&&(s.role!=='wolf'||stHuntReleased(s));}
function stMobileStickPoint(event){
 if(stMobile.pointer!==event.pointerId)return;const r=$('stMoveStick').getBoundingClientRect(),limit=r.width*.30,dx=event.clientX-(r.left+r.width/2),dy=event.clientY-(r.top+r.height/2),distance=Math.hypot(dx,dy),amount=Math.min(1,distance/limit);
 stMobile.x=distance?dx/distance:0;stMobile.y=distance?dy/distance:0;stMobile.strength=amount<.16?0:(amount-.16)/.84;
 $('stMoveKnob').style.transform=`translate(calc(-50% + ${stMobile.x*Math.min(distance,limit)}px),calc(-50% + ${stMobile.y*Math.min(distance,limit)}px))`;
}
function stMobileDrive(unit,dt,update){
 if(stMobile.unit!==unit||stMobile.pointer===null)return update(unit,dt);
 if(!stMobileCanMove()||stMobile.session!==stSession||unit.captured!==stMobile.captured){stMobileReset('session, capture or pause changed');return update(unit,dt);}
 const amount=stMobile.strength;
 if(!amount){if(unit.order?.joystick)stSetOrder(unit,null);unit.spiritOrder=null;return update(unit,dt);}
 const direction=new THREE.Vector3(stMobile.x,0,stMobile.y); // Fixed RTS camera: screen up is world -Z.
 if(unit.captured){unit.spiritOrder={x:unit.spirit.position.x+direction.x,z:unit.spirit.position.z+direction.z};return update(unit,dt*amount);}
 const context={rules:stSession.rules,obstacles:stObstacles()},radius=stUnitRadius(unit);let target=null;
 // Do not turn a directional stick into a long automatic detour. Sweep ahead,
 // then allow sliding along a wall while preserving all unit-traffic checks.
 for(const distance of [1.2,.6,.3,.12]){const p=unit.pos.clone().addScaledVector(direction,distance);if(stSegmentClear(context,unit.pos,p,radius)){target=p;break;}}
 if(!target)for(const axis of Math.abs(direction.x)>Math.abs(direction.z)?['x','z']:['z','x']){const p=unit.pos.clone();p[axis]+=direction[axis]*.35;if(p.distanceToSquared(unit.pos)>.0001&&stSegmentClear(context,unit.pos,p,radius)){target=p;break;}}
 if(target){if(!unit.order?.joystick)stSetOrder(unit,{action:'move',x:target.x,z:target.z,joystick:true});else{unit.order.x=target.x;unit.order.z=target.z;unit.destination.copy(target);}}
 else if(unit.order?.joystick)stSetOrder(unit,null);
 const speed=unit.speed;unit.speed=speed*amount;try{return update(unit,dt);}finally{unit.speed=speed;}
}
const stMobileSheepBase=stUpdateSheep,stMobileWolfBase=stUpdateWolf;
stUpdateSheep=function(unit,dt){return stMobileDrive(unit,dt,stMobileSheepBase);};
stUpdateWolf=function(unit,dt){return stMobileDrive(unit,dt,stMobileWolfBase);};
function stMobileIcon(kind){
 const art={
 'st-farm':'<path fill="#fff0bd" d="M15 29h34v26H15z"/><path fill="#efbd51" d="M8 30 32 9l24 21z"/><path fill="#614c35" d="M27 39h11v16H27z"/><path fill="#62d9d4" d="M19 35h7v9h-7zM40 35h6v9h-6z"/>',
 'st-income':'<path fill="#80d8aa" d="M15 29h34v26H15z"/><path fill="#248f7d" d="M7 31 32 10l25 21z"/><path fill="#173a34" d="M26 37h12v18H26z"/><circle fill="#ffe18a" stroke="#a66f24" stroke-width="2" cx="47" cy="43" r="11"/><path stroke="#9c6b2d" stroke-width="3" d="M47 36v14m4-11h-7l-1 4h7l-1 4h-7"/>',
 'st-fort':'<path fill="#c9e1de" d="M12 20h40v35H12z"/><path fill="#698897" d="M9 14h10v10H9zm18 0h10v10H27zm18 0h10v10H45z"/><path fill="#233d4b" d="M25 38a7 7 0 0 1 14 0v17H25z"/><path fill="#f4d279" d="m33 23 11 4v8c0 8-11 13-11 13s-11-5-11-13v-8z"/><path stroke="#805c36" stroke-width="3" d="m28 34 4 4 7-8"/>',
 'st-wall':'<path fill="#b8ccd4" d="M8 25h48v28H8zM8 14h10v15H8zm18 0h12v15H26zm20 0h10v15H46z"/><path stroke="#69818d" stroke-width="3" d="M9 37h46M24 27v10m15 0v16M8 47h30"/>',
 'st-ramp':'<path fill="#bd8d52" d="M8 50 51 16l6 35z"/><path stroke="#f0d7a2" stroke-width="4" d="m8 42 44-34M16 48V36m13 1V26m13 1V16"/><path stroke="#79502d" stroke-width="2" d="m20 43 6 8m3-16 8 16m1-23 12 23"/>',
 wolf:'<path fill="#9adbe9" d="m12 10 15 13 12-4 13-11-3 25 5 12-22 13-20-14 5-14z"/><path fill="#24394d" d="m20 31 10 5-8 4zm24 0-10 5 8 4zM26 45h13l-7 7z"/>'};
 return '<svg class="st-skill-icon" aria-hidden="true" viewBox="0 0 64 64">'+(art[kind]||art['st-farm'])+'</svg>';
}
function stMobileOpen(open){stMobile.open=!!open;$('stTouchUtilities').hidden=!open;$('stTouchOptions').setAttribute('aria-expanded',String(!!open));}
function stMobileInstall(){
 if($('stMoveStick'))return;
 const root=document.createElement('div');root.id='stTouchDeck';root.innerHTML='<div id="stMoveStick" role="group" aria-label="Movement joystick: drag to move, release to stop"><i class="st-stick-compass"></i><span id="stMoveKnob"></span><small>MOVE</small></div><button type="button" id="stTouchOptions" aria-label="Unit actions and camera controls" aria-expanded="false">•••</button><section id="stTouchUtilities" hidden aria-label="Unit actions"><header><b>Unit actions</b><button type="button" id="stTouchClose" aria-label="Close unit actions">×</button></header></section><svg id="stTouchAim" aria-hidden="true"><line/><circle r="8"/><circle class="finger" r="19"/></svg>';
 $('sheepTagHUD').append(root);$('stTouchOptions').onclick=()=>stMobileOpen(!stMobile.open);$('stTouchClose').onclick=()=>stMobileOpen(false);$('stHelp').addEventListener('click',()=>stMobileOpen(false));$('stCancelBuild').addEventListener('click',()=>{if(stMobile.enabled)stUiFeedback('Build cancelled.');});
 for(const [id,kind] of [...stUiBuildButtons,['stWolfUpgrade','wolf']]){const b=$(id);b.dataset.stSkill=kind;b.insertAdjacentHTML('afterbegin',stMobileIcon(kind));b.insertAdjacentHTML('beforeend','<span class="st-skill-cost" aria-hidden="true"></span>');}
 const stick=$('stMoveStick');stick.addEventListener('pointerdown',event=>{
  if(!stMobile.enabled||!stMobileCanMove()||event.button!==0||stMobile.pointer!==null)return;event.preventDefault();event.stopPropagation();
  const unit=stSession.units.find(u=>u.id===stSession.controlledId);if(!unit)return;
  stMobileReset('new stick gesture');stMobile.pointer=event.pointerId;stMobile.session=stSession;stMobile.unit=unit;stMobile.captured=unit.captured;
  stUi.buildingId=null;stUi.follow=true;stUiCommand('select',{id:unit.id});stSetOrder(unit,null);unit.spiritOrder=null;unit.archiveRoute=null;
  stick.setPointerCapture(event.pointerId);stick.classList.add('held');stMobileStickPoint(event);
 });
 stick.addEventListener('pointermove',event=>{if(event.pointerId!==stMobile.pointer)return;event.preventDefault();event.stopPropagation();stMobileStickPoint(event);});
 for(const type of ['pointerup','pointercancel','lostpointercapture'])stick.addEventListener(type,event=>{if(event.pointerId!==stMobile.pointer)return;event.preventDefault();event.stopPropagation();stMobileReset(type);});
}
function stMobileSync(){
 if(!$('stMoveStick'))return;const enabled=!!stSession&&!stSession.simulate&&stUi.shown&&stMobileMedia.matches;
 if(enabled!==stMobile.enabled){stMobileReset('control layout changed');stMobile.enabled=enabled;document.body.classList.toggle('st-touch-controls',enabled);
  if(enabled){const panel=$('stTouchUtilities');for(const selector of ['.st-selection','.st-farm-actions','.st-camera','#stPlacementTools','#stMoreActions','#stExtraActions','#stMagicReadout']){const node=$('sheepTagHUD').querySelector(selector);if(!node)continue;const marker=document.createComment('native mobile action position');node.before(marker);stMobile.utilities.push({node,marker});panel.append(node);}}
  else {for(const {node,marker} of stMobile.utilities)marker.replaceWith(node);stMobile.utilities=[];stMobileOpen(false);$('stPhase').style.removeProperty('top');}
 }
 if(!enabled)return;
 if(!stMobileCanMove())stMobileReset('controls unavailable');
 document.body.classList.toggle('st-touch-building',!!stUi.build);document.body.classList.toggle('st-touch-wolf',stSession.role==='wolf');
 document.documentElement.style.setProperty('--st-touch-top',($('viewport').getBoundingClientRect().top+5)+'px');
 const hudTop=$('sheepTagHUD').getBoundingClientRect().top,scoreBottom=$('sheepTagHUD').querySelector('.st-score').getBoundingClientRect().bottom;$('stPhase').style.top=(scoreBottom-hudTop+8)+'px';stClarityPositionLegend();
 stTouchPlacement.desiredOffsetPx=Math.max(72,Math.min(112,$('viewport').getBoundingClientRect().height*.16));
 for(const [id,kind] of [...stUiBuildButtons,['stWolfUpgrade','wolf']]){const b=$(id),small=b.querySelector('small'),label=small?.textContent.split(' · ')[0]||'';b.querySelector('.st-skill-cost').textContent=label.replace(' gold','');b.setAttribute('aria-label',(kind==='wolf'?'Wolf upgrade':stUiBuildNames[kind])+': '+label);}
 const legend=$('stClearanceLegend');if(legend)legend.dataset.clearance='Gaps · sheep '+(stUnitRadius('sheep')*2).toFixed(2)+' m · wolves '+(stUnitRadius('wolf')*2).toFixed(2)+' m';
 const aim=$('stTouchAim'),gesture=stTouchPlacement.gesture;aim.style.display=gesture&&stUi.placement&&stTouchPlacement.valid?'block':'none';
 if(gesture&&stUi.placement&&stTouchPlacement.valid){const fit=stUi.placement,p=new THREE.Vector3(fit.x,terrainHeight(fit.x,fit.z),fit.z).project(camera),rect=$('viewport').getBoundingClientRect(),x=rect.left+(p.x+1)*rect.width/2,y=rect.top+(1-p.y)*rect.height/2,color=fit.ok?'#96ffd0':'#ff7777';const line=aim.querySelector('line');for(const [k,v] of Object.entries({x1:gesture.x,y1:gesture.y,x2:x,y2:y,stroke:color}))line.setAttribute(k,v);const circles=aim.querySelectorAll('circle');for(const [circle,cx,cy] of [[circles[0],x,y],[circles[1],gesture.x,gesture.y]]){circle.setAttribute('cx',cx);circle.setAttribute('cy',cy);circle.setAttribute('stroke',color);}}
}
const stMobileInstallBase=stInstallUI;stInstallUI=function(){stMobileInstallBase();stMobileInstall();};
const stMobileHudBase=stRefreshHUD;stRefreshHUD=function(...args){const result=stMobileHudBase(...args);stMobileSync();return result;};
const stMobileChooseBase=stUiChooseBuild;stUiChooseBuild=function(kind){stMobileOpen(false);return stMobileChooseBase(kind);};
const stMobileDisposeBase=stDisposeUI;stDisposeUI=function(){stMobileReset('Stop');const result=stMobileDisposeBase();stMobileSync();return result;};
const stMobileStatusBase=stUiStatus;stUiStatus=function(){return {...stMobileStatusBase(),mobileControls:{enabled:stMobile.enabled,joystick:{active:stMobile.pointer!==null,pointerId:stMobile.pointer,x:stMobile.x,y:stMobile.y,strength:stMobile.strength,lastReset:stMobile.lastReset},utilitiesOpen:stMobile.open}};};
for(const type of ['blur','pagehide'])window.addEventListener(type,()=>stMobileReset(type));
window.addEventListener('resize',()=>{stMobileReset('viewport resized');if(stTouchPlacement.gesture){stTouchPlacementReset('viewport resized',true);stTouchPlacementHide(null);}stMobileSync();});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stMobileReset('document hidden');});
stMobileMedia.addEventListener('change',()=>stMobileSync());
// Honor the last visible footprint when a stationary aiming finger releases
// while the other thumb/camera is moving. Native placement revalidates it.
const stMobileGroundBase=stTouchPlacementGround;
stTouchPlacementGround=function(x,y){
 const raw=stTouchPlacement.rawScreen,target=stTouchPlacement.targetScreen;
 if(stMobile.enabled&&stTouchPlacement.context?.type==='pointerup'&&stTouchPlacementEnabled()&&stUi.placementPoint&&raw&&target&&Math.hypot(x-raw[0],y-raw[1])<.75&&stTouchPlacementClearCanvas(x,y)&&stTouchPlacementClearCanvas(...target)){
  const point=stUi.placementPoint.clone();stTouchPlacement.ground=point.toArray();return point;
 }
 return stMobileGroundBase(x,y);
};
