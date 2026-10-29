// Gameplay and visible clearance use the same native footprints and radii.
const stClarityCleanRulesBase=stCleanRules;
stCleanRules=function(value={}){const r=stClarityCleanRulesBase(value);if(Math.abs(r.sheepSpeed-5.4)<1e-6)r.sheepSpeed=6;if(Math.abs(r.wolfRadius-.78)<1e-6)r.wolfRadius=.9;return r;};
const stClarityVisualBase=stMakeVisual;
stMakeVisual=function(type){const v=stClarityVisualBase(type);if(type==='st-wolf')for(const child of v.children){child.position.multiplyScalar(.9/.78);child.scale.multiplyScalar(.9/.78);}return v;};
function stHuntReleased(s=stSession){return !!s&&s.elapsed>=s.rules.headstart;}
const stClarityPerceivesBase=stPerceives;
stPerceives=function(observer,target){
 if(!stHuntReleased()&&(observer?.kind==='wolf'||target?.kind==='wolf'))return false;
 // Bot knowledge always needs an actual sighting, including spectator/fog-off games.
 if(observer?.kind==='wolf')return stPerceivesDirect(observer,target)||(stSession.rules.fogMode==='team'&&stSession.units.some(u=>u.kind==='wolf'&&stPerceivesDirect(u,target)));
 return stClarityPerceivesBase(observer,target);
};
const stClarityPhysicalBase=stLanesPhysical;
stLanesPhysical=function(unit){return (unit.kind!=='wolf'||stHuntReleased())&&stClarityPhysicalBase(unit);};
const stClarityViewBase=stViewStatus;
stViewStatus=function(){const result=stClarityViewBase();if(!stSession)return result;result.sanctuary={x:stSession.pen.x,z:stSession.pen.z,radius:stSanctuaryRadius()};
 if(!stHuntReleased()){result.units=result.units.filter(u=>u.kind!=='wolf'&&(stSession.role!=='wolf'||u.kind==='wisp'));result.lastKnown=[];result.scentClues=[];if(stSession.role==='wolf'){result.buildings=[];result.attacks=[];}}
 return result;};
function stSanctuaryRadius(s=stSession){return Math.max(s.pen.reserveX||7,s.pen.reserveZ||7,s.rules.bounds*.1625+1.2);}
function stSanctuaryOverlaps(footprint,s=stSession){return stIntersectsObstacle(s.pen.x,s.pen.z,stSanctuaryRadius(s),footprint);}
const stClarityCanBuildBase=stCanBuild;
stCanBuild=function(...args){const fit=stClarityCanBuildBase(...args);if(stSession&&fit.corners&&stSanctuaryOverlaps(fit))return {...fit,ok:false,reason:'Sanctuary · no building inside the marked central court. Move beyond the boundary.'};return fit;};
stChooseBase=function(unit){
 const s=stSession,known=stBotKnownEnemies(unit),candidates=[],margin=Math.min(12,Math.max(4,(s.rules.bounds-stSanctuaryRadius(s))/3)),radius=Math.min(stSanctuaryRadius(s)+13,s.rules.bounds-margin);
 // Central spawn is a starting point, never an illegal fallback building base.
 for(const extra of [0,12,24])for(let j=0;j<16;j++){const a=(unit.botIndex%8)*Math.PI/4+j*Math.PI/8;candidates.push(new THREE.Vector3(s.pen.x+Math.cos(a)*(radius+extra),0,s.pen.z+Math.sin(a)*(radius+extra)));}
 let best=null,score=-Infinity;
 for(const p of candidates){p.x=Math.round(p.x/.15)*.15;p.z=Math.round(p.z/.15)*.15;
  if(Math.abs(p.x)>s.rules.bounds-margin||Math.abs(p.z)>s.rules.bounds-margin||stBlocked(p.x,p.z,stUnitRadius(unit)))continue;
  if(![[-3,-3],[3,-3],[-3,3],[3,3]].some(([dx,dz])=>stCanBuild('st-farm',p.x+dx,p.z+dz,unit.id).ok))continue;
  const peers=s.units.filter(u=>u!==unit&&u.base),spread=peers.length?Math.min(...peers.map(u=>u.base.distanceToSquared(p))):400;
  const safety=known.length?Math.min(...known.map(e=>p.distanceToSquared(e.pos))):200,value=Math.min(spread,400)+Math.min(safety,400)-unit.pos.distanceToSquared(p)*.3;
  if(value>score&&stPath(unit.pos,p,stUnitRadius(unit))){score=value;best=p;}
 }
 return best;
};
function stClarityGap(a,b,buildings=stSession?.buildings||[],rules=stSession?.rules){
 // Parallel house faces only: diagonally separated corners are not corridors.
 if(!ST_LANE_HOUSES.has(a.kind)||!ST_LANE_HOUSES.has(b.kind))return null;
 if(Math.abs(Math.sin((a.rotation||0)*2))>.001||Math.abs(Math.sin((b.rotation||0)*2))>.001)return null;
 const gapX=Math.abs(a.pos.x-b.pos.x)-a.halfX-b.halfX,gapZ=Math.abs(a.pos.z-b.pos.z)-a.halfZ-b.halfZ;
 const axis=gapX>=0&&gapZ<-.1?'x':gapZ>=0&&gapX<-.1?'z':null;if(!axis)return null;
 const cross=axis==='x'?'z':'x',half=axis==='x'?'halfX':'halfZ',otherHalf=axis==='x'?'halfZ':'halfX',width=axis==='x'?gapX:gapZ;
 if(width>3.6)return null;const low=a.pos[axis]<b.pos[axis]?a:b,high=low===a?b:a;
 const start=low.pos[axis]+low[half],end=high.pos[axis]-high[half],lo=Math.max(a.pos[cross]-a[otherHalf],b.pos[cross]-b[otherHalf]),hi=Math.min(a.pos[cross]+a[otherHalf],b.pos[cross]+b[otherHalf]),mid=(start+end)/2;
 const from={x:0,z:0},to={x:0,z:0};from[axis]=to[axis]=mid;from[cross]=lo-1;to[cross]=hi+1;
 const obstacles=buildings.filter(v=>v.hp>0).map(stBuildingObstacle),context={rules,obstacles:[...(stSession?.obstacles||[]),...obstacles]};
 const sheep=width+1e-6>=rules.sheepRadius*2&&stSegmentClear(context,from,to,rules.sheepRadius),wolf=sheep&&width+1e-6>=rules.wolfRadius*2&&stSegmentClear(context,from,to,rules.wolfRadius);
 return {axis,width,x:axis==='x'?mid:(lo+hi)/2,z:axis==='z'?mid:(lo+hi)/2,length:hi-lo,sheep,wolf,label:wolf?'BOTH':sheep?'SHEEP ONLY':'BLOCKED',color:wolf?0xe5c66a:sheep?0x48e6ed:0xf17d74};
}
let stClarityOverlay=null,stClarityOverlayKey='';
function stClarityDisposeOverlay(){if(stClarityOverlay){stClarityOverlay.traverse(n=>{n.geometry?.dispose();n.material?.map?.dispose();n.material?.dispose();});scene.remove(stClarityOverlay);}stClarityOverlay=null;stClarityOverlayKey='';document.getElementById('stClearanceLegend')?.remove();}
function stClarityUpdateOverlay(state){
 if(!stSession||!stUi.shown)return;
 const visible=state.buildings.filter(b=>ST_LANE_HOUSES.has(b.kind)),focus=state.buildings.find(b=>b.id===state.selectedId)?.pos||state.units.find(u=>u.controlled)?.pos||[stUi.focus.x,0,stUi.focus.z];
 const nearby=visible.filter(b=>Math.hypot(b.pos[0]-focus[0],b.pos[2]-focus[2])<30).slice(0,60);
 const key=[window.innerWidth,window.innerHeight,stSession.navVersion,visible.map(b=>b.id).join(','),nearby.map(b=>b.id).join(','),state.role,stHuntReleased(),stUnitRadius('sheep'),stUnitRadius('wolf')].join('|');if(key===stClarityOverlayKey){stClarityPositionLabel(focus);return;}
 stClarityDisposeOverlay();stClarityOverlayKey=key;const root=new THREE.Group();root.name='Live collision footprints and measured clearances';root.userData.sheepTagPreview=true;stClarityOverlay=root;scene.add(root);
 const line=(points,color,opacity=1)=>{const v=new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color,transparent:true,opacity,depthWrite:false}));root.add(v);return v;};
 for(const b of visible){const points=b.corners.map(([x,z])=>new THREE.Vector3(x,terrainHeight(x,z)+.075,z));line(points,0xeed9a0,.9);
  // A solid foundation extends all the way to the actual blocking edge.
  const mesh=new THREE.Mesh(new THREE.BoxGeometry(b.localHalfX*2,.06,b.localHalfZ*2),new THREE.MeshBasicMaterial({color:0x795d39}));mesh.position.set(b.pos[0],terrainHeight(b.pos[0],b.pos[2])+.025,b.pos[2]);mesh.rotation.y=b.rotation||0;root.add(mesh);
 }
 const radius=stSanctuaryRadius(),pen=stSession.pen;line(Array.from({length:128},(_,i)=>{const a=i*Math.PI/64,x=pen.x+Math.cos(a)*radius,z=pen.z+Math.sin(a)*radius;return new THREE.Vector3(x,terrainHeight(x,z)+.08,z);}),0xe5c66a,.8);
 const convert=b=>({...b,pos:new THREE.Vector3(...b.pos)}),all=state.buildings.map(convert),close=nearby.map(convert),gaps=[];
 for(let i=0;i<close.length;i++)for(let j=i+1;j<close.length;j++){const gap=stClarityGap(close[i],close[j],all,stSession.rules);if(!gap)continue;gaps.push(gap);
  const strip=new THREE.Mesh(new THREE.PlaneGeometry(gap.axis==='x'?Math.max(.035,gap.width):gap.length,gap.axis==='z'?Math.max(.035,gap.width):gap.length),new THREE.MeshBasicMaterial({color:gap.color,transparent:true,opacity:.35,depthWrite:false,side:THREE.DoubleSide}));strip.rotation.x=-Math.PI/2;strip.position.set(gap.x,terrainHeight(gap.x,gap.z)+.085,gap.z);root.add(strip);
  const canvas=document.createElement('canvas');canvas.width=512;canvas.height=96;const ctx=canvas.getContext('2d');ctx.fillStyle='#12231fee';ctx.fillRect(0,0,512,96);ctx.fillStyle='#'+gap.color.toString(16).padStart(6,'0');ctx.font='bold 35px sans-serif';ctx.textAlign='center';ctx.fillText(gap.width.toFixed(2)+' m · '+gap.label,256,61);
  const texture=new THREE.CanvasTexture(canvas),sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,depthTest:false,depthWrite:false}));sprite.position.set(gap.x,terrainHeight(gap.x,gap.z)+.24,gap.z);sprite.scale.set(3.6,.675,1);sprite.renderOrder=5;sprite.userData.clearanceGap=gap;root.add(sprite);
 }
 root.userData.gaps=gaps;const legend=document.createElement('div');legend.id='stClearanceLegend';legend.style.cssText='position:fixed;left:12px;top:112px;max-width:calc(100vw - 48px);padding:6px 9px;border:1px solid #aaad79;border-radius:7px;background:#172b22ed;color:#f3edcd;z-index:39;font:11px/1.5 system-ui;pointer-events:none';
 legend.textContent='House outline = blocked ground · Cyan: sheep only · Gold: both · Red: blocked. Sheep need '+(stUnitRadius('sheep')*2).toFixed(2)+' m; wolves '+(stUnitRadius('wolf')*2).toFixed(2)+' m. Gold circle: no building.';legend.style.top=Math.ceil(Math.max(document.getElementById('stPhase')?.getBoundingClientRect().bottom||0,(document.querySelector('#sheepTagHUD .st-score')?.getBoundingClientRect().bottom||0)+40)+8)+'px';document.body.append(legend);stClarityPositionLabel(focus);
}
window.SWYRL_ENGINE_SHEEP_TAG.clearanceStatus=()=>({active:!!stClarityOverlay,sanctuary:stSession?{...stSession.pen,radius:stSanctuaryRadius()}:null,sheepDiameter:stSession?stUnitRadius('sheep')*2:null,wolfDiameter:stSession?stUnitRadius('wolf')*2:null,gaps:(stClarityOverlay?.userData.gaps||[]).map(g=>({...g})),legend:document.getElementById('stClearanceLegend')?.textContent||''});

function stClarityPositionLabel(focus){
 if(!stClarityOverlay)return;const gaps=stClarityOverlay.userData.gaps||[];let nearest=null,distance=144;
 for(const gap of gaps){const d=(gap.x-focus[0])**2+(gap.z-focus[2])**2;if(d<distance){nearest=gap;distance=d;}}
 const pixels=$('viewport').getBoundingClientRect().height;
 for(const sprite of stClarityOverlay.children){if(!sprite.userData.clearanceGap)continue;sprite.visible=sprite.userData.clearanceGap===nearest;if(!sprite.visible)continue;
  const depth=-sprite.position.clone().applyMatrix4(perspectiveCamera.matrixWorldInverse).z;
  const width=Math.max(3.6,144*2*Math.tan(THREE.MathUtils.degToRad(perspectiveCamera.fov/2))*Math.max(.1,depth)/Math.max(1,pixels));sprite.scale.set(width,width*96/512,1);
 }
 const legend=document.getElementById('stClearanceLegend');if(!legend)return;let detail=document.getElementById('stNearestGap');if(!detail){detail=document.createElement('strong');detail.id='stNearestGap';detail.style.cssText='display:block;font-size:12px';legend.append(detail);}detail.textContent=nearest?'Nearest gap: '+nearest.width.toFixed(2)+' m · '+nearest.label:'';
}
function stClarityPositionLegend(){
 const legend=document.getElementById('stClearanceLegend');if(!legend)return;
 const score=document.querySelector('#sheepTagHUD .st-score')?.getBoundingClientRect(),phase=document.getElementById('stPhase')?.getBoundingClientRect();
 legend.style.top=Math.ceil(Math.max(score?.bottom||0,phase?.bottom||0)+8)+'px';
}
// The score wraps on phones and the phase text changes after the camera pass.
// Position after the native HUD has written its final current-frame text.
if(typeof stRefreshHUD==='function'){
 const stClarityRefreshBase=stRefreshHUD;
 stRefreshHUD=function(...args){const result=stClarityRefreshBase(...args);if(stClarityOverlay)stClarityPositionLegend();return result;};
}
// Sub-grid lanes need exact centerline portals: a 0.60 m gap leaves only
// 0.06 m of sheep-center clearance, less than the native 0.15 m grid pitch.
function stClarityPortalRoute(context,start,target,radius){
 const houses=context.obstacles.filter(o=>ST_LANE_HOUSES.has(o.kind)&&Math.abs(Math.sin((o.rotation||0)*2))<.001);
 let best=null,bestLength=Math.hypot(target.x-start.x,target.z-start.z)*1.35+2;
 for(let i=0;i<houses.length;i++)for(let j=i+1;j<houses.length;j++){
  const a=houses[i],b=houses[j],gx=Math.abs(a.x-b.x)-a.halfX-b.halfX,gz=Math.abs(a.z-b.z)-a.halfZ-b.halfZ;
  const axis=gx>=0&&gz<-.1?'x':gz>=0&&gx<-.1?'z':null;if(!axis)continue;
  const gap=axis==='x'?gx:gz;if(gap<radius*2-1e-6||gap>radius*2+ST_GRID*1.5)continue;
  const cross=axis==='x'?'z':'x',half=axis==='x'?'halfX':'halfZ',other=axis==='x'?'halfZ':'halfX',low=a[axis]<b[axis]?a:b,high=low===a?b:a;
  const mid=(low[axis]+low[half]+high[axis]-high[half])/2,p=new THREE.Vector3(),q=new THREE.Vector3();p[axis]=q[axis]=mid;
  p[cross]=Math.min(a[cross]-a[other],b[cross]-b[other])-radius-.15;q[cross]=Math.max(a[cross]+a[other],b[cross]+b[other])+radius+.15;
  const inLane=v=>Math.abs(v[axis]-mid)<=gap/2-radius+1e-6&&v[cross]>=p[cross]&&v[cross]<=q[cross];
  for(const [outsideEntry,outsideExit] of [[p,q],[q,p]]){
   const entry=inLane(start)?new THREE.Vector3(start.x,0,start.z):outsideEntry,exit=inLane(target)?new THREE.Vector3(target.x,0,target.z):outsideExit;
   const length=Math.hypot(entry.x-start.x,entry.z-start.z)+entry.distanceTo(exit)+Math.hypot(target.x-exit.x,target.z-exit.z);
   if(length>=bestLength||!stSegmentClear(context,start,entry,radius)||!stSegmentClear(context,entry,exit,radius)||!stSegmentClear(context,exit,target,radius))continue;
   bestLength=length;best=[entry.clone(),exit.clone(),new THREE.Vector3(target.x,0,target.z)];
  }
 }
 return best;
}
const stClarityPathBase=stPath;
stPath=function(start,target,radius){
 if(stSession&&stSession.rules.bounds<=80){const context={rules:stSession.rules,obstacles:stObstacles()};if(!stSegmentClear(context,start,target,radius)){const route=stClarityPortalRoute(context,start,target,radius);if(route)return route;}}
 return stClarityPathBase(start,target,radius);
};
