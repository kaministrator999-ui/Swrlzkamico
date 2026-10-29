// §E v11.145 · nonflickering aim, safe Rapid correction and immersive Play.
// No new game clock, native validator bypass or extra scene ownership.
const se145={mode:'',keptGhost:0,safeMagnets:0};
let se145Exit=null;
function se145RuntimeMode(){
 if(seLevels.playingMenu)return 'menu';
 return stSession&&!stSession.simulate&&stUi.shown?'game':'';
}
function se145SyncRuntime(){
 const mode=se145RuntimeMode();
 if(mode===se145.mode)return;
 se145.mode=mode;
 document.body.classList.toggle('se145-runtime',!!mode);
 document.body.classList.toggle('se145-menu',mode==='menu');
 document.body.classList.toggle('se145-game',mode==='game');
 if(!se145Exit){
  const node=document.createElement('button');
  node.type='button';node.id='se145ExitEditor';
  node.textContent='✕ Exit to editor';
  node.setAttribute('aria-label','Stop Play and return to the editor');
  node.addEventListener('pointerdown',event=>event.stopPropagation());
  node.addEventListener('click',event=>{
   event.preventDefault();event.stopPropagation();
   stopSession();
  });
  // Host is the actual CANVAS parent, not a canvas fallback child.
  se143ViewportHost()?.appendChild(node);se145Exit=node;
 }
 if(se145Exit)se145Exit.hidden=!mode;
}
const se145PlayMenuBase=seLevelsPlayMenu;
seLevelsPlayMenu=function(...args){const result=se145PlayMenuBase(...args);se145SyncRuntime();return result;};
const se145StopMenuBase=seLevelsStopMenu;
seLevelsStopMenu=function(...args){const result=se145StopMenuBase(...args);se145SyncRuntime();return result;};
const se145PlayBase=beginPlay;
beginPlay=function(...args){const result=se145PlayBase(...args);se145SyncRuntime();return result;};
const se145StopBase=stopSession;
stopSession=function(...args){const result=se145StopBase(...args);se145SyncRuntime();return result;};
const se145HudBase=stRefreshHUD;
stRefreshHUD=function(...args){const result=se145HudBase(...args);se145SyncRuntime();return result;};
// A transient ray/HUD overlap should invalidate a DROP without removing the
// previously rendered ghost. A fresh valid sample immediately restores green.
const se145HideBase=stTouchPlacementHide;
stTouchPlacementHide=function(reason){
 if(reason&&stBuildInput.pointer!==null&&stBuildInput.session===stSession&&
    stBuildInput.source==='meadow'&&stUi.build&&stUi.preview){
  stTouchPlacement.valid=false;
  stTouchPlacement.reason=reason;
  stUi.preview.visible=true;se145.keptGhost++;
  stUi.preview.traverse(object=>{
   const materials=Array.isArray(object.material)?object.material:[object.material];
   for(const m of materials){if(m?.color)m.color.set(0xff7777);
    if(m?.emissive)m.emissive.set(0x481414);}
  });
  if(stPlacementGridState.guide)stPlacementGridState.guide.root.visible=false;
  if(stUi.footprint)stUi.footprint.visible=false;
  stUiText('stPlacement',reason);
  $('stPlacement')?.classList.add('error');
  return;
 }
 return se145HideBase(reason);
};
// Rapid's older magnet tries only one tight diagonal. Try other near-neighbor
// ALIGNMENTS, but accept only a site cleared by the complete prior validator.
const se145CanBuildBase=stCanBuild;
let se145Snap=null;
function se145HouseCorrection(fit,kind,ownerId,rotation){
 if(!fit||fit.ok||!st132Rapid||!stSession||!ST_LANE_HOUSES.has(kind)||
    !/^(A diagonal crack is not a sheep passage\.|This opening would trap a sheep\.|A house or obstacle blocks this sheep passage\.)/.test(fit.reason||''))return fit;
 const fx=fit.x,fz=fit.z,halfX=fit.halfX??1.2,halfZ=fit.halfZ??1.2;
 if(!Number.isFinite(fx)||!Number.isFinite(fz))return fit;
 const limit=1.65,options=[];
 for(const other of stSession.buildings){
  if(other.hp<=0||!ST_LANE_HOUSES.has(other.kind)||
     Math.abs(Math.sin(2*(other.rotation||0)))>.001)continue;
  const x=halfX+other.halfX+.002,z=halfZ+other.halfZ+.002;
  for(const sx of [-1,1])for(const sz of [-1,1])
   options.push([other.pos.x+sx*x,other.pos.z+sz*z]);
  // Straight-row alignments are stable and avoid side-notch placements.
  for(const sx of [-1,1])options.push([other.pos.x+sx*x,other.pos.z]);
  for(const sz of [-1,1])options.push([other.pos.x,other.pos.z+sz*z]);
 }
 let best=null,score=Infinity;
 for(const [x,z] of options){
  const distance=Math.hypot(x-fx,z-fz);
  if(distance>limit)continue;
  const candidate=st139NativeCanBuild(kind,x,z,ownerId,rotation);
  if(!candidate?.ok||Math.hypot(candidate.x-x,candidate.z-z)>.31)continue;
  const d=Math.hypot(candidate.x-fx,candidate.z-fz);
  if(d>limit+.02)continue;
  const sticky=se145Snap?.session===stSession&&
     se145Snap.kind===kind&&Math.hypot(se145Snap.x-candidate.x,se145Snap.z-candidate.z)<.05;
  const ranking=d-(sticky?.18:0);
  if(ranking<score){score=ranking;best=candidate;}
 }
 if(best){
  se145.safeMagnets++;
  se145Snap={session:stSession,kind,x:best.x,z:best.z};
  best.se145SafeSnap=true;best.se145Requested=[fx,fz];
  return best;
 }
 se145Snap=null;
 return fit;
}
stCanBuild=function(kind,x,z,ownerId=null,rotation=0){
 const fit=se145CanBuildBase(kind,x,z,ownerId,rotation);
 return se145HouseCorrection(fit,kind,ownerId,rotation);
};
const se145StopRoundBase=stStop;
stStop=function(...args){se145Snap=null;const result=se145StopRoundBase(...args);se145SyncRuntime();return result;};
const se145StatusBase=stUiStatus;
stUiStatus=function(){return {...se145StatusBase(),
 se145:{mode:se145.mode,keptGhost:se145.keptGhost,safeMagnets:se145.safeMagnets,
  previewVisible:!!stUi.preview?.visible,exitVisible:!!se145Exit&&!se145Exit.hidden}};};
