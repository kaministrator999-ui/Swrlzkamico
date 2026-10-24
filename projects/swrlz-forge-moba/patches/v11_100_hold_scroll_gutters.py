"""Refine mobile Model Atelier panel size, scroll gutters and press-and-hold numeric edit."""
import hashlib
import json

def one(html,before,after):
    count=html.count(before)
    assert count==1,(before[:110],count)
    return html.replace(before,after,1)

CSS = """
/* §E v11.100: moderate panels, explicit expansion and safe swipe gutters. */
.se-mobile-inspector-size{display:none!important}
@media (max-width:980px),(pointer:coarse){
 .model-atelier.atelier-tools-docked:not(.atelier-tools-closed) .atelier-inspector {
  left:auto!important;right:20px!important;top:auto!important;
  bottom:calc(68px + env(safe-area-inset-bottom,0px) + var(--atelier-keyboard-offset,0px))!important;
  width:min(410px,calc(100vw - 40px))!important;
  height:min(49dvh,470px)!important;
  max-height:calc(var(--atelier-visible-height,100dvh) - 140px)!important;
  min-height:0!important;
  padding:12px 23px 16px!important;
  gap:8px!important;overflow-x:hidden!important;overflow-y:auto!important;
  touch-action:pan-y!important;pointer-events:auto!important;
  overscroll-behavior-y:contain!important;-webkit-overflow-scrolling:touch;
  z-index:2167!important;
 }
 .model-atelier.atelier-tools-docked.se-mobile-inspector-expanded:not(.atelier-tools-closed) .atelier-inspector{
  width:calc(100vw - 40px)!important;
  height:min(62dvh,620px)!important;
  max-height:calc(var(--atelier-visible-height,100dvh) - 136px)!important;
 }
 /* Padding on BOTH sides is scroll-only space, not another input hit target. */
 .model-atelier.atelier-tools-docked .atelier-inspector :is(input[type=number],input[type=text],textarea) {
  touch-action:pan-y!important;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector .atelier-tool-handle {
  margin:-12px -23px 3px!important;padding:7px 10px!important;
  gap:5px;flex-wrap:nowrap;align-items:center;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector .atelier-tool-handle strong{
  flex:1;min-width:0;font-size:12px!important;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector .atelier-tool-handle button{
  min-width:57px!important;min-height:38px!important;padding:5px 7px!important;
  font-size:12px!important;white-space:nowrap;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector .atelier-tool-handle .se-mobile-inspector-size{
  display:inline-flex!important;align-items:center;justify-content:center;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector :is(label,fieldset,section,div,p,small,legend){
  touch-action:pan-y;
 }
 .model-atelier .atelier-context-workbench:not([hidden]){
  left:20px!important;right:20px!important;
  width:calc(100vw - 40px)!important;max-width:none!important;
  height:min(49dvh,470px)!important;
  max-height:calc(var(--atelier-visible-height,100dvh) - 138px)!important;
 }
 .model-atelier .atelier-context-workbench[data-mobile-size="expanded"]:not([hidden]){
  height:min(63dvh,640px)!important;
 }
 .model-atelier .atelier-context-workbench[data-mobile-size="compact"]:not([hidden]){
  height:52px!important;max-height:52px!important;
 }
 .model-atelier .atelier-context-workbench :is(.atelier-context-right,.atelier-context-left){
  padding-left:23px!important;padding-right:23px!important;
  pointer-events:auto!important;touch-action:pan-y!important;
  overflow-y:auto!important;-webkit-overflow-scrolling:touch;
 }
}
"""

HOLD_OLD = """ // Capture before the native input receives touch focus and triggers browser zoom.
 document.addEventListener('pointerdown',event=>{
  const node=event.target;
  const input=node?.closest?.('.model-atelier input[type="number"]');
  if(!coarse()||!input||input.disabled||input.readOnly)return;
  event.preventDefault();
  event.stopImmediatePropagation();
  open(input);
 },true);
 // Touch platforms without Pointer Events: avoid activating native input focus.
 if(!window.PointerEvent)document.addEventListener('touchstart',event=>{
  const input=event.target?.closest?.('.model-atelier input[type="number"]');
  if(!coarse()||!input||input.disabled||input.readOnly)return;
  event.preventDefault();event.stopPropagation();open(input);
 },{capture:true,passive:false});
"""
HOLD_NEW = """ // On touch devices, deliberate 380ms press opens the numeric pad.
 // An ordinary tap never focuses the browser input; moving the finger or
 // scrolling before the threshold cancels the timer.
 const holdMilliseconds=380;
 const holdTravelPixels=10;
 let pendingNumberHold=null;
 function cancelNumberHold(){
  if(pendingNumberHold?.timer)clearTimeout(pendingNumberHold.timer);
  pendingNumberHold=null;
 }
 function scheduleNumberHold(input,x,y,pointerId){
  cancelNumberHold();
  const hold={input,x,y,pointerId,timer:0};
  hold.timer=setTimeout(()=>{
   if(pendingNumberHold!==hold||!input.isConnected)return;
   pendingNumberHold=null;
   open(input);
  },holdMilliseconds);
  pendingNumberHold=hold;
 }
 const numericTarget=event=>event.target?.closest?.('.model-atelier input[type="number"]');
 document.addEventListener('pointerdown',event=>{
  const input=numericTarget(event);
  if(!coarse()||!input||input.disabled||input.readOnly||event.pointerType==='mouse'||event.isPrimary===false)return;
  event.preventDefault();
  event.stopImmediatePropagation();
  scheduleNumberHold(input,event.clientX,event.clientY,event.pointerId);
 },true);
 document.addEventListener('pointermove',event=>{
  const h=pendingNumberHold;
  if(h?.pointerId===event.pointerId&&Math.hypot(event.clientX-h.x,event.clientY-h.y)>holdTravelPixels)cancelNumberHold();
 },true);
 document.addEventListener('pointerup',event=>{
  if(pendingNumberHold?.pointerId===event.pointerId)cancelNumberHold();
 },true);
 document.addEventListener('pointercancel',event=>{
  if(pendingNumberHold?.pointerId===event.pointerId)cancelNumberHold();
 },true);
 // Prevent quick taps or a completed hold from triggering Chrome's keyboard.
 document.addEventListener('click',event=>{
  const input=numericTarget(event);
  if(!coarse()||!input)return;
  event.preventDefault();event.stopImmediatePropagation();
 },true);
 document.addEventListener('contextmenu',event=>{
  if(coarse()&&numericTarget(event))event.preventDefault();
 },true);
 if(!window.PointerEvent){
  document.addEventListener('touchstart',event=>{
   const input=numericTarget(event);
   if(!coarse()||!input||event.touches.length!==1)return;
   const t=event.touches[0];
   scheduleNumberHold(input,t.clientX,t.clientY,'touch');
  },{capture:true,passive:true});
  document.addEventListener('touchmove',event=>{
   const h=pendingNumberHold,t=event.touches[0];
   if(h&&t&&Math.hypot(t.clientX-h.x,t.clientY-h.y)>holdTravelPixels)cancelNumberHold();
  },{capture:true,passive:true});
  document.addEventListener('touchend',cancelNumberHold,true);
  document.addEventListener('touchcancel',cancelNumberHold,true);
 }
"""
EXPAND_JS = """
function seMobileInspectorSizeInstall(){
 const panel=document.querySelector('.model-atelier');
 const inspector=panel?.querySelector('.atelier-inspector');
 const handle=inspector?.querySelector('.atelier-tool-handle');
 if(!panel||!handle||handle.querySelector('.se-mobile-inspector-size'))return;
 const btn=document.createElement('button');
 btn.type='button';btn.className='se-mobile-inspector-size';
 btn.setAttribute('aria-label','Expand modeling tool panel');
 btn.setAttribute('aria-pressed','false');
 btn.textContent='↗ Expand';
 const hide=handle.querySelector('button');
 if(hide)handle.insertBefore(btn,hide);else handle.append(btn);
 btn.addEventListener('click',()=>{
  const expanded=panel.classList.toggle('se-mobile-inspector-expanded');
  btn.textContent=expanded?'↙ Shrink':'↗ Expand';
  btn.setAttribute('aria-label',expanded?'Shrink modeling tool panel':'Expand modeling tool panel');
  btn.setAttribute('aria-pressed',String(expanded));
 });
}
"""

def apply(html):
    html=one(html,HOLD_OLD,HOLD_NEW)
    html=one(html,"seMobileNumberPadInstall();",
                 "seMobileNumberPadInstall();\nseMobileInspectorSizeInstall();")
    html=one(html,"function seMobileNumberPadInstall(){",
                 EXPAND_JS+"\nfunction seMobileNumberPadInstall(){")
    html=one(html,"</head>",'<style id="se-v11100-mobile-panel-ergonomics">'+CSS+"</style>\n</head>")
    html=one(html,"SWYRL_ENGINE_DEPLOY_MARKER: V11_99_MOBILE_SCROLL_SIZE",
                 "SWYRL_ENGINE_DEPLOY_MARKER: V11_100_HOLD_SCROLL_GUTTERS")
    for a,b in [
      ('ENGINE · MAKER v11.99','ENGINE · MAKER v11.100'),
      ('v11.99 · enlarged scrollable mobile menus','v11.100 · comfortable scrolling and hold-to-edit'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.99'","window.SWRLZ_FORGE_BUILD={version:'v11.100'"),
      ('<title>§wyrl§ Engine · Maker v11.99</title>','<title>§wyrl§ Engine · Maker v11.100</title>'),
    ]:html=one(html,a,b)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Compact mobile tool panels, scrolling gutters, press-and-hold numeric edits',
                 date='2026-10-23',changes=[
       'Restore a modest floating tool panel close to its original size, with a user-operated Expand/Shrink toggle.',
       'Reserve 23-pixel left and right internal swipe gutters, independent of numeric input surfaces.',
       'Require a deliberate 380ms stationary touch to open the native number pad; a tap or scrolling gesture does not edit values.',
       'Keep larger context-panel option, scrollable tool rail, original sculpt actions and saved models unchanged.'
    ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    data=html.encode('utf-8')
    print('SWRLZ_V11100_BUILD_MEASURE',len(data),hashlib.sha256(data).hexdigest(),flush=True)
    return html
