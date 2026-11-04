"""§E v11.255: restore Particle Studio real viewport interaction and draw ownership.

Root cause: the visible studio viewport ignores pointer events, its invisible
shell-wide camera shield is a separate hit target, and the Game Editor's orbit
controller updates AFTER the authoring chamber positions the shared camera.
That conflicts with the native chamber pose on every engine frame.
Do not alter Sheep Tag / XR / project serialization / material editors.
"""
from pathlib import Path
import json

def once(s, old, new, label):
    n=s.count(old)
    if n!=1:
        raise AssertionError(("v11.255",label,"matches",n,old[:160]))
    return s.replace(old,new,1)

def apply(html):
    # 1. Camera ownership. The shared scene gets its view pose from the
    # particle chamber while active. Game orbit controls must not rewrite it.
    html=once(html,
      "if(!playing&&!renderer.xr.isPresenting)orbit.update();",
      "if(!playing&&!renderer.xr.isPresenting&&"
      "!window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.())orbit.update();",
      "prevent game orbit camera override in particle editor")

    # 2. Keep the chamber's original camera and renderer. Expand its native
    # adjust API with orbit/pan/zoom delta operations (not a new render loop).
    old="""if(kind==='zoom'){state.distance=Math.max(3.2,Math.min(23,state.distance+Number(value||0)));if(state.active)frame();return true;}"""
    new="""if(kind==='orbit'){
        const dx=Number(value?.dx)||0,dy=Number(value?.dy)||0;
        state.yaw-=dx*.007;
        state.pitch=Math.max(-.15,Math.min(1.54,state.pitch+dy*.006));
        if(state.active)frame();return true;
      }
      if(kind==='pan'){
        const dx=Number(value?.dx)||0,dy=Number(value?.dy)||0;
        state.targetX-=dx*.012;state.targetZ+=dy*.012;
        if(state.active)frame();return true;
      }
      if(kind==='zoom'){
        const change=Number(value);
        if(!Number.isFinite(change))return false;
        state.distance=Math.max(1.25,Math.min(48,state.distance+change));
        if(state.active)frame();return true;
      }"""
    html=once(html,old,new,"native camera gesture support and real zoom range")

    # 3. Give the visible viewport direct hit testing and release the old
    # invisible shell-wide input shield when Particle Studio UI is mounted.
    css="""body[data-se225-workspace=particles] #se249Root .se249-stage{
 pointer-events:auto!important;touch-action:none!important;cursor:grab!important
}
body[data-se225-workspace=particles] #se249Root .se249-stage:active{
 cursor:grabbing!important
}
body[data-se225-workspace=particles] #se240ParticleStageOrbit{
 pointer-events:none!important
}
body[data-se225-workspace=particles] #se249Root .se249-stage-status{
 max-width:86%;pointer-events:none
}
"""
    html=html.replace("</head>",
      '<style id="se255ParticleViewportInput">'+css+'</style>\n</head>',1)

    gesture=r"""function se255BindViewportInput(surface){
 const fingers=new Map();
 let pinch=0;
 function stage(){
  const api=window.SWYRL_ENGINE_PARTICLE_STAGE_240;
  if(!api?.active?.()&&window.SWYRL_ENGINE_STUDIOS?.active?.()==='particles'){
   api?.open?.();
  }
  return api?.active?.()?api:null;
 }
 function gap(){
  const two=[...fingers.values()];
  return two.length<2?0:Math.hypot(two[0].x-two[1].x,two[0].y-two[1].y);
 }
 function ignored(node){
  return !!node?.closest?.('button,input,select,textarea,a,summary');
 }
 surface.addEventListener('pointerdown',e=>{
  if(e.button!==0||ignored(e.target)||!stage())return;
  fingers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(fingers.size===2)pinch=gap();
  try{surface.setPointerCapture(e.pointerId)}catch{}
  e.preventDefault();e.stopPropagation();
 });
 surface.addEventListener('pointermove',e=>{
  const prev=fingers.get(e.pointerId);if(!prev)return;
  const dx=e.clientX-prev.x,dy=e.clientY-prev.y;
  fingers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  const api=stage();if(!api)return;
  if(fingers.size>=2){
   const current=gap();
   if(pinch)api.adjust?.('zoom',(pinch-current)*.026);
   pinch=current;
  }else{
   const tool=state.tool;
   if(tool==='pan')api.adjust?.('pan',{dx,dy});
   else if(tool==='zoom')api.adjust?.('zoom',dy*.04);
   else api.adjust?.('orbit',{dx,dy});
  }
  e.preventDefault();e.stopPropagation();
 });
 const release=e=>{
  if(!fingers.has(e.pointerId))return;
  fingers.delete(e.pointerId);
  pinch=fingers.size===2?gap():0;
  try{if(surface.hasPointerCapture(e.pointerId))surface.releasePointerCapture(e.pointerId)}catch{}
  e.stopPropagation();
 };
 surface.addEventListener('pointerup',release);
 surface.addEventListener('pointercancel',release);
 surface.addEventListener('lostpointercapture',e=>{fingers.delete(e.pointerId);pinch=0});
 surface.addEventListener('wheel',e=>{
  if(ignored(e.target))return;
  const api=stage();if(!api)return;
  api.adjust?.('zoom',(e.deltaY>0?1:-1)*Math.min(2.4,Math.max(.22,Math.abs(e.deltaY)*.008)));
  e.preventDefault();e.stopPropagation();
 },{passive:false});
}"""
    html=once(html,
      "function build(){\n const shell=vq('#se225Shell'),panel=getPanel();",
      gesture+"\nfunction build(){\n const shell=vq('#se225Shell'),panel=getPanel();",
      "install real viewport pointer/touch handlers in Particle workstation closure")
    html=once(html,
      " const viewing=vn('div','se249-stage');",
      " const viewing=vn('div','se249-stage');\n se255BindViewportInput(viewing);",
      "bind gestures to actual centered 3D viewport")

    # 4. Preview action must be able to start the native chamber if its
    # scene was not yet ready when lazy studio mounting first ran.
    html=once(html,
      "case 'preview':state.paused=false;action('se223Preview');break;",
      """case 'preview':
   state.paused=false;
   if(!stage?.active?.()){
    if(!stage?.open?.()){report('Particle chamber unavailable — select Edit mode');break;}
    se223State.preview=true;se223State.playingLast=false;
    se223UIRefresh();
   }else action('se223Preview');
   break;""",
      "ensure authoring chamber is active before switching preview")
    html=once(html,
      "case 'focus':stage?.adjust?.('reset');break;",
      "case 'focus':if(!stage?.active?.())stage?.open?.();stage?.adjust?.('reset');break;",
      "focus native chamber even on late mount")
    html=once(html,
      "case 'zoomin':stage?.adjust?.('zoom',-.9);break;",
      "case 'zoomin':if(!stage?.active?.())stage?.open?.();stage?.adjust?.('zoom',-.9);break;",
      "zoom in after late-mounted chamber start")
    html=once(html,
      "case 'zoomout':stage?.adjust?.('zoom',1.1);break;",
      "case 'zoomout':if(!stage?.active?.())stage?.open?.();stage?.adjust?.('zoom',1.1);break;",
      "zoom out after late-mounted chamber start")

    # 5. A small real status readout gives the owner a useful diagnosis if
    # the effect still fails: chamber open, active count, current zoom.
    html=once(html,
      " const b=vq('#se249Play');if(b)b.textContent=se223State.preview?'■ Stop preview':'▶ Preview';",
      """ const b=vq('#se249Play');if(b)b.textContent=se223State.preview?'■ Stop preview':'▶ Preview';
 if(!state.se255LastStatus||now-state.se255LastStatus>450){
  state.se255LastStatus=now;
  const meta=window.SWYRL_ENGINE_PARTICLE_STAGE_240?.inspect?.();
  const particles=[...se223State.live.values()].reduce((n,r)=>n+r.particles.length,0);
  const status=vq('#se249Status');
  if(status)status.textContent=
   (meta?.active?'Chamber ON':'Chamber OFF')+
   ' · Preview '+(se223State.preview?'ON':'OFF')+
   ' · '+particles+' points · Zoom '+(meta?.zoomDistance?.toFixed?.(1)??'—');
 }""",
      "visible native scene state, particle count and zoom readout")

    old=" source.engine='§wyrl§ Engine · Maker v11.254';source.version=11.254;"
    assert html.count(old)==2,("v11.255 provenance",html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.255';source.version=11.255;")
    for before,after in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_254_PARTICLE_DOCK_PREVIEW_CAMERA",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_255_PARTICLE_VIEWPORT_OWNERSHIP"),
      ("ENGINE · MAKER v11.254","ENGINE · MAKER v11.255"),
      ("v11.254 · particle editor dock, preview and zoom repairs",
       "v11.255 · native particle viewport ownership and input"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.254'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.255'"),
      ("<title>§wyrl§ Engine · Maker v11.254</title>",
       "<title>§wyrl§ Engine · Maker v11.255</title>")
    ):html=once(html,before,after,"release identity")
    key="const SE_RELEASE_NOTES="
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Live particle chamber: direct orbit, pan and zoom controls",
      date="2026-11-04",changes=[
       "Fix camera ownership: while the edit-mode Particle Chamber is active, the Game Editor orbit controller no longer overwrites the dedicated camera pose later in the same render frame.",
       "The actual center viewport now accepts direct mouse/touch input: drag to orbit, choose Pan/Zoom tools for their gestures, use wheel or two-finger pinch to zoom, and use existing +/− buttons to adjust the real chamber camera.",
       "Disable the obsolete invisible shell-wide input shield while the Particle Studio workstation is displayed; native toolbar and sidebars remain clickable independently.",
       "Preview button can start a late-mounted native chamber before playback; the chamber shows real-time ON/OFF state, point count, and zoom distance for diagnosis.",
       "Retain v11.254 dock fixes, v11.252 model and particle load tests, native VFX emitters/curves, one WebGL renderer, Sheep Tag gameplay, saves and Quest controls. Real-device verification pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
