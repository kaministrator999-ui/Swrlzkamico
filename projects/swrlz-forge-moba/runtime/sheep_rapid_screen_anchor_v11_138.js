// §E v11.138 · Rapid Build remembers the LAST SUCCESSFUL HOUSE'S SCREEN
// coordinates, not its old world coordinates. New preview follows camera pan
// only while idle; meadow dragging uses screen delta from this anchor.
let st138Memory=null,st138LastPinTick=-Infinity,st138LastPinned=null;
function st138ActiveMemory(){
 const m=st138Memory,s=stSession;
 return st132Rapid&&m&&s===m.session&&s.controlledId===m.owner&&
  !s.simulate&&!s.winner&&stUi.shown?m:null;
}
function st138Pixels(memory){
 const rect=$('viewport')?.getBoundingClientRect();
 if(!rect||rect.width<=0||rect.height<=0)return null;
 return {x:rect.left+memory.u*rect.width,y:rect.top+memory.v*rect.height,rect};
}
function st138RayForScreen(memory,dx=0,dy=0){
 const pixel=st138Pixels(memory);
 if(!pixel)return null;
 const x=pixel.x+dx,y=pixel.y+dy;
 if(x<pixel.rect.left||x>=pixel.rect.right||
    y<pixel.rect.top||y>=pixel.rect.bottom||
    !stTouchPlacementClearCanvas(x,y))return null;
 const point=stTouchPlacementOriginalGround(x,y);
 if(!point||![point.x,point.z].every(Number.isFinite))return null;
 point.y=terrainHeight(point.x,point.z);
 return Number.isFinite(point.y)?point:null;
}
function st138RememberLastScreenPosition(){
 const s=stSession,fit=stUi.placement;
 if(!st132Rapid||!s||!stUi.build||!fit?.ok||
    !Number.isFinite(fit.x)||!Number.isFinite(fit.z))return false;
 // Capture the ACTUAL validated/snapped building center before native
 // stBuildInputFinish clears the completed placement.
 const world=new THREE.Vector3(fit.x,terrainHeight(fit.x,fit.z),fit.z);
 const projected=world.project(camera);
 const u=(projected.x+1)/2,v=(1-projected.y)/2;
 if(![u,v,projected.z].every(Number.isFinite)||
    u<0||u>=1||v<0||v>=1||projected.z<-1||projected.z>1){
  st138Memory=null;return false;
 }
 st138Memory={session:s,owner:s.controlledId,u,v,kind:stUi.build};
 st138LastPinned=null;st138LastPinTick=-Infinity;
 return true;
}
function st138SeedFromScreen(){
 const memory=st138ActiveMemory();
 if(!memory||!stUi.preview||!stUi.build)return false;
 const point=st138RayForScreen(memory);
 if(!point)return false;
 // A ghost seed is not a construction order. Avoid using stale gesture
 // validity left from the successful build or from skill button input.
 const gesture=stTouchPlacement.gesture,context=stTouchPlacement.context;
 stTouchPlacement.gesture=null;stTouchPlacement.context=null;
 try{stUiPlacePreview(point);}
 finally{stTouchPlacement.gesture=gesture;stTouchPlacement.context=context;}
 stUi.preview.visible=true;
 if(stPlacementGridState.guide)stPlacementGridState.guide.root.visible=false;
 if(stUi.footprint)stUi.footprint.visible=false;
 stTouchPlacement.valid=false;st138LastPinned=point.clone();
 return true;
}
function st138AttachAim(anchor){
 const memory=st138ActiveMemory();
 if(memory&&anchor&&anchor.session===stSession)
  anchor.st138Screen={u:memory.u,v:memory.v};
}
// Return undefined only when NORMAL (sheep-origin) aim is intended.
// A null target means rapid's intended destination went outside clear meadow;
// never fall back to a sheep-origin jump.
function st138RapidTarget(anchor,x,y){
 if(!anchor?.st138Screen)return undefined;
 return st138RayForScreen(anchor.st138Screen,x-anchor.x,y-anchor.y);
}
function st138PinIdleGhost(){
 const memory=st138ActiveMemory();
 if(!memory||!stUi.build||!stUi.preview||stBuildInput.pointer!==null)return;
 const now=performance.now();
 if(now-st138LastPinTick<72)return;
 st138LastPinTick=now;
 const target=st138RayForScreen(memory);
 if(!target)return;
 // Camera moves often; avoid rebuilding the placement footprint if the
 // projected world point has barely changed.
 if(st138LastPinned&&Math.hypot(target.x-st138LastPinned.x,
      target.z-st138LastPinned.z)<.065)return;
 st138SeedFromScreen();
}
const st138CameraBase=stUpdateCamera;
stUpdateCamera=function(...args){
 const result=st138CameraBase(...args);
 st138PinIdleGhost();
 return result;
};
// The normal sheep-origin seed is retained when Rapid is OFF or when there
// has not been a successful prior build. Rapid ON with memory wins over it.
const st138SheepSeedBase=st135SeedSheepGhost;
st135SeedSheepGhost=function(){
 const result=st138SheepSeedBase();
 if(result)st138SeedFromScreen();
 return result;
};
const st138ChooseBase=stUiChooseBuild;
stUiChooseBuild=function(kind){
 const result=st138ChooseBase(kind);
 if(stUi.build===kind)st138SeedFromScreen();
 return result;
};
// Switching Rapid off, restarting or stopping must never resurrect a
// previous sheep's screen anchor in a new round.
const st138RapidBase=st132SetRapid;
st132SetRapid=function(enabled){
 if(!enabled){st138Memory=null;st138LastPinned=null;}
 return st138RapidBase(enabled);
};
const st138StopBase=stStop;
stStop=function(...args){
 st138Memory=null;st138LastPinned=null;
 return st138StopBase(...args);
};
const st138StatusBase=stUiStatus;
stUiStatus=function(){
 const result=st138StatusBase();
 const m=st138ActiveMemory();
 return {...result,rapidScreenAnchor:m?{u:m.u,v:m.v,kind:m.kind}:null};
};
