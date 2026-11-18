/* SE512_DISPLAY_PLATFORM_START */
// The 2D editor plaque is a scene prop, never parented under the model.
// The Quest regular browser and desktop share this explicit display-only UI.
let se512BrowserFloor=null,se512BrowserFloorVisible=true,se512PlatformControl=null;
let se512PlatformStage=null,se512PlatformStagePosition=null;
function se512PlatformBrowserAttach(floor,stage){
 se512PlatformBrowserDetach();
 if(!floor||!stage)return;
 se512BrowserFloor=floor;se512BrowserFloor.visible=se512BrowserFloorVisible;
 se512PlatformStage=stage;
 const computed=typeof getComputedStyle==='function'?getComputedStyle(stage).position:stage.style.position;
 if(!computed||computed==='static'){
  se512PlatformStagePosition=stage.style.position;
  stage.style.position='relative';
 }
 const btn=document.createElement('button');
 btn.type='button';btn.id='se512PlatformToggle';btn.setAttribute('aria-label','Show or hide display platform');
 btn.style.cssText='position:absolute;right:10px;top:10px;z-index:40;padding:8px 12px;border:1px solid #7391b9;border-radius:8px;background:#171c32ed;color:#e6f7ff;font:600 13px system-ui,sans-serif;cursor:pointer;touch-action:manipulation';
 const refresh=()=>{btn.textContent=se512BrowserFloorVisible?'Hide platform':'Show platform';btn.setAttribute('aria-pressed',String(!se512BrowserFloorVisible));};
 btn.addEventListener('click',()=>{se512BrowserFloorVisible=!se512BrowserFloorVisible;
  if(se512BrowserFloor)se512BrowserFloor.visible=se512BrowserFloorVisible;
  refresh();});
 refresh();stage.append(btn);se512PlatformControl=btn;
}
function se512PlatformBrowserDetach(){
 se512PlatformControl?.remove();se512PlatformControl=null;se512BrowserFloor=null;
 if(se512PlatformStage&&se512PlatformStagePosition!==null)
  se512PlatformStage.style.position=se512PlatformStagePosition;
 se512PlatformStage=null;se512PlatformStagePosition=null;
}
/* SE512_DISPLAY_PLATFORM_END */
