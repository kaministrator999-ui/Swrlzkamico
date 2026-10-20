"""§E v11.60 preview-only floating Model Atelier tool dock.

Keeps v11.59 native inspector DOM and every existing editing event handler.
Not part of the production source manifest until browser and owner approval.
"""

CSS = r"""
/* §E v11.60 presentation-only preview. */
.model-atelier.atelier-tools-docked .atelier-body{display:flex!important;flex:1 1 auto;min-height:0;overflow:hidden;position:relative}
.model-atelier.atelier-tools-docked .atelier-scene{flex:1 1 auto;min-height:0!important;width:100%;height:100%;max-height:none!important}
/* Native camera/viewport controls remain above the floating inspector, so Frame Selected and zoom stay tappable. */
.model-atelier.atelier-tools-docked .atelier-viewport-controls{z-index:220}

.model-atelier.atelier-tools-docked .atelier-inspector{
 position:fixed!important;z-index:90;top:64px;right:61px;left:auto;
 width:min(400px,calc(100vw - 82px));height:min(72dvh,730px);
 min-height:0!important;max-height:calc(100dvh - 110px)!important;
 display:flex;flex-direction:column;overflow-y:auto;overscroll-behavior:contain;
 border:1px solid #75a8c7;border-radius:12px;box-shadow:0 14px 36px #000a;
 background:#182640f2;padding:8px;gap:8px;flex:0 0 auto!important;
 pointer-events:none
}
.model-atelier.atelier-tools-docked.atelier-tools-closed .atelier-inspector{display:none!important}
.model-atelier.atelier-tools-docked .atelier-inspector :is(button,input,select,textarea,label,summary,a,[role="button"],.atelier-tool-handle){pointer-events:auto}
.model-atelier .atelier-tool-handle{position:sticky;z-index:8;top:-8px;margin:-8px -8px 2px;
 padding:7px 8px;background:#263d5e;display:flex;justify-content:space-between;
 align-items:center;gap:5px;touch-action:none;cursor:grab;user-select:none;
 border-bottom:1px solid #7898bc;border-radius:10px 10px 0 0}
.model-atelier .atelier-tool-handle:active{cursor:grabbing}
.model-atelier .atelier-tool-handle strong{font-size:13px;color:#e0f4ff}
.model-atelier .atelier-tool-handle button{min-height:32px;padding:5px 9px;touch-action:manipulation}
.model-atelier .atelier-tool-rail{position:fixed;z-index:2150;right:5px;top:22dvh;
 display:flex;flex-direction:column;gap:5px;max-height:68dvh;overflow-y:auto;
 padding:5px;border:1px solid #547d9d;border-radius:12px;
 background:#182a46f0;box-shadow:0 9px 25px #0008}
.model-atelier .atelier-tool-rail button{min-height:40px;min-width:47px;max-width:56px;
 padding:5px 3px;font-size:10px;line-height:1.2;touch-action:manipulation}
.model-atelier .atelier-tool-rail button[aria-pressed="true"]{border-color:#65e9e4;background:#1d6475}
.model-atelier .atelier-tool-rail button:focus-visible,.model-atelier .atelier-tool-handle button:focus-visible{outline:2px solid #7dffeb;outline-offset:1px}
@media(max-width:900px),(pointer:coarse){
 .model-atelier.atelier-tools-docked .atelier-inspector{top:auto;bottom:54px;right:58px;
  width:min(390px,calc(100vw - 69px));height:min(48dvh,460px);
  max-height:calc(100dvh - 104px)!important}
 .model-atelier.atelier-tools-docked .atelier-scene{min-height:0!important}
 /* Keep native reference photo controls separately scrollable above the lower mobile tool popup. */
 .model-atelier.atelier-tools-docked:not(.atelier-tools-closed) #modelAtelierReferenceDock:not([hidden]){max-height:min(36dvh,340px)!important}
}
@media(max-height:520px){
 .model-atelier .atelier-tool-rail{top:80px;max-height:calc(100dvh - 125px)}
 .model-atelier.atelier-tools-docked .atelier-inspector{top:46px;height:calc(100dvh - 95px)}
}
"""

JS = r"""
// §E v11.60 tool-dock preview: presentation only, no mesh state mutations.
function atelierToolDockInstall(panel){
 if(panel.querySelector('#modelAtelierToolRail'))return;
 const inspector=panel.querySelector('.atelier-inspector');
 if(!inspector)return;
 panel.classList.add('atelier-tools-docked');
 const rail=document.createElement('nav');
 rail.id='modelAtelierToolRail';rail.className='atelier-tool-rail';
 rail.setAttribute('role','toolbar');rail.setAttribute('aria-label','Model Atelier tool shortcuts');
 const handle=document.createElement('div');handle.className='atelier-tool-handle';
 handle.innerHTML='<strong>⠿ Move tools</strong><button type="button" aria-label="Hide editing tools">✕ Hide</button>';
 inspector.prepend(handle);panel.append(rail);
 const items=[
  ['Meshes','#modelAtelierParts'],
  ['Sculpt','#modelAtelierSculptBrush'],
  ['Lasso','#modelAtelierLassoTools'],
  ['Face','#modelAtelierFaceSheetControls'],
  ['Topology','#modelAtelierTopologyTools'],
  ['More','#modelAtelierInspectorControls']
 ];
 let open=true; // discoverable on first launch; one tap hides without shrinking canvas
 let lastChoice='Meshes';
 const buttons=[];
 function setOpen(value){
  open=!!value;
  panel.classList.toggle('atelier-tools-closed',!open);
  buttons.forEach(b=>{
   b.setAttribute('aria-expanded',String(open));
   b.setAttribute('aria-pressed',String(open&&b.textContent===lastChoice));
  });
  inspector.setAttribute('aria-hidden',String(!open));
  if(!open&&inspector.contains(document.activeElement))rail.querySelector('button')?.focus();
 }
 for(const [label,selector] of items){
  const b=document.createElement('button');b.type='button';b.textContent=label;
  b.setAttribute('aria-controls','modelAtelierInspectorDock');
  b.setAttribute('aria-label','Open '+label+' editing tools');
  b.addEventListener('click',()=>{
   if(open&&lastChoice===label){setOpen(false);return;}
   lastChoice=label;setOpen(true);
   const section=inspector.querySelector(selector);
   const hidden=section&&section.closest('[hidden]');
   const target=!section||hidden?inspector.querySelector('#modelAtelierParts'):section;
   if(target)inspector.scrollTop=Math.max(0,target.getBoundingClientRect().top-inspector.getBoundingClientRect().top+inspector.scrollTop-55);
  });
  rail.append(b);buttons.push(b);
 }
 inspector.id='modelAtelierInspectorDock';
 handle.querySelector('button').addEventListener('click',()=>setOpen(false));
 panel.addEventListener('keydown',e=>{
  if(e.key==='Escape'&&open){e.stopImmediatePropagation();e.preventDefault();setOpen(false);}
 },true);
 let drag=null;
 handle.addEventListener('pointerdown',e=>{
  if(e.button!==0||e.target.closest('button'))return;
  const box=inspector.getBoundingClientRect();
  drag={pointer:e.pointerId,x:e.clientX,y:e.clientY,left:box.left,top:box.top};
  try{handle.setPointerCapture(e.pointerId);}catch(_e){}
  e.preventDefault();
 });
 handle.addEventListener('pointermove',e=>{
  if(!drag||e.pointerId!==drag.pointer)return;
  const bounds=panel.getBoundingClientRect();
  const left=Math.min(bounds.right-inspector.offsetWidth-5,Math.max(bounds.left+5,drag.left+e.clientX-drag.x));
  const top=Math.min(bounds.bottom-Math.min(60,inspector.offsetHeight)-5,Math.max(bounds.top+5,drag.top+e.clientY-drag.y));
  inspector.style.left=left+'px';inspector.style.top=top+'px';inspector.style.right='auto';
  e.preventDefault();
 });
 const end=e=>{if(drag&&e.pointerId===drag.pointer)drag=null;};
 handle.addEventListener('pointerup',end);handle.addEventListener('pointercancel',end);
 setOpen(open);
}
"""

def apply(html: str) -> str:
    """Apply UI only atop an exact sealed v11.59 source; never publish directly."""
    module_start='const ModelAtelier=(()=>{'
    panel_anchor='    document.body.append(panel);\n    const action=(id,fn)=>'
    assert html.count(module_start)==1, 'Missing/ambiguous Model Atelier module'
    assert html.count(panel_anchor)==1, 'Missing/ambiguous native panel setup'
    assert html.count('SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER')==1
    assert 'atelierToolDockInstall(panel)' not in html
    html=html.replace(module_start,JS+'\n'+module_start,1)
    html=html.replace(panel_anchor,'    document.body.append(panel);\n    atelierToolDockInstall(panel);\n    const action=(id,fn)=>',1)
    assert html.count('</head>')>=1
    return html.replace('</head>','<style id="modelAtelierFloatingDockPreview">'+CSS+'</style>\n</head>',1)
