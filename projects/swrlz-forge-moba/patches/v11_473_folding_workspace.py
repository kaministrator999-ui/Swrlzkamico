"""§E v11.473 — screen-wide UV dragging, tappable dock grips, folding tool rail."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_473_FOLDING_WORKSPACE'

def once(src,old,new,label):
    n=src.count(old)
    if n!=1:raise AssertionError(('v11.473 source anchor',label,n,old[:150]))
    return src.replace(old,new,1)

def apply(html):
    required=(
     'SWYRL_ENGINE_DEPLOY_MARKER: V11_472_FULL_RES_TEXTURES',
     'function safeBounds(){',
     'function fitWindow(reset=false){',
     'let panel=null,popup=null,button=null,scheduled=false,drag=null;',
     'function dragResize(node,what,side,dir){',
     'function modelLayout(){',
     'function ensurePanel(){',
     'SE472_NATIVE_TEXTURE_RESOLUTION_START',
     'SE471_UV_FINE_FIT_START'
    )
    for token in required:
        assert token in html,('v11.473 missing inherited source',token)

    # Replace ONLY the private UV window geometry helpers in the original
    # se355 closure. The native popup, selectors and listeners remain intact.
    uv_start=html.index('  // Fit the UV window inside the actual 3D work area,')
    uv_end=html.index('  const q=(selector,root=document)',uv_start)
    original=html[uv_start:uv_end]
    assert original.count('function safeBounds()')==1
    assert original.count('function fitWindow(reset=false)')==1
    floating=(ROOT/'runtime/model_uv_screen_drag_v11_473.js').read_text('utf8')
    assert 'SE473_UV_SCREEN_DRAG_START' in floating
    html=html[:uv_start]+floating+'\n'+html[uv_end:]
    html=once(html,
      """  function setOpen(open){
    if(!popup)return;
    popup.hidden=!open;""",
      """  function setOpen(open){
    if(!popup)return;
    if(!open&&isOpen())se473RememberWindow();
    popup.hidden=!open;""",
      'save UV position before close')
    html=once(html,
      """      drag=null;
      try{handle.releasePointerCapture(event.pointerId);}catch(_){}""",
      """      drag=null;
      try{handle.releasePointerCapture(event.pointerId);}catch(_){}
      se473RememberWindow();""",
      'save UV position after move')
    html=once(html,
      """    handle.addEventListener('pointercancel',end);
    return el;""",
      """    handle.addEventListener('pointercancel',end);
    // The browser resize corner is independent of the drag titlebar.
    // Save its final dimensions without rebuilding the native UV widgets.
    el.addEventListener('pointerup',()=>requestAnimationFrame(()=>se473RememberWindow()));
    return el;""",
      'remember optional resized popup')

    # The persisted v11.251 widths were already correct. A tap on its existing
    # divider flips only collapsed state; a drag keeps the native resize path.
    html=once(html,
      """ node.setAttribute('aria-label','Resize '+what+' '+side+' dock');""",
      """ node.setAttribute('aria-label','Tap to collapse or restore; drag to resize '+what+' '+side+' dock');
 node.title='Tap to collapse / restore · Drag to resize';""",
      'accessible splitter hint')
    html=once(html,
      """  start={pointer:e.pointerId,x:e.clientX,width:state[what][side]};""",
      """  start={pointer:e.pointerId,x:e.clientX,y:e.clientY,
   width:state[what][side],moved:false};""",
      'native splitter pointer origin')
    html=once(html,
      """  if(!start||e.pointerId!==start.pointer)return;
  const w=state[what][side];
  const next=start.width+(e.clientX-start.x)*dir;""",
      """  if(!start||e.pointerId!==start.pointer)return;
  if(!start.moved&&Math.hypot(e.clientX-start.x,e.clientY-start.y)<9)return;
  start.moved=true;
  const flag=side==='left'?'collapsed':'rightCollapsed';
  if(state[what][flag])state[what][flag]=false;
  const w=state[what][side];
  const next=start.width+(e.clientX-start.x)*dir;""",
      'tap versus drag threshold')
    # Capture phase runs before the original pointerup listener clears start.
    # Preserve its existing commit/save/release path rather than replacing it.
    html=once(html,
      """ node.addEventListener('keydown',e=>{""",
      """ node.addEventListener('pointerup',e=>{
  if(!start||start.pointer!==e.pointerId||start.moved||layout()!=='desktop')return;
  const flag=side==='left'?'collapsed':'rightCollapsed';
  state[what][flag]=!state[what][flag];
  sync();
 },true);
 node.addEventListener('keydown',e=>{
  const flag=side==='left'?'collapsed':'rightCollapsed';
  if(e.key==='Enter'||e.key===' '){
   e.preventDefault();state[what][flag]=!state[what][flag];
   sync();save();window.dispatchEvent(new Event('resize'));return;
  }
  if(e.key==='ArrowRight'||e.key==='ArrowLeft')state[what][flag]=false;""",
      'capture tap and keyboard fold before native resize completion')

    html=once(html,
      """||rail.querySelector('button');button?.click();""",
      """||rail.querySelector('button:not(#se473RailFold)');button?.click();""",
      'native tool restoration skips fold control')

    rail=(ROOT/'runtime/model_tool_rail_fold_v11_473.js').read_text('utf8')
    assert 'SE473_MODEL_TOOL_RAIL_FOLD_START' in rail
    html=once(html,'  function ensurePanel(){',
        rail+'\n  function ensurePanel(){','native Model Studio rail insertion')
    css=(ROOT/'runtime/model_folding_workspace_v11_473.css').read_text('utf8')
    assert 'SE473_MODEL_FOLDING_WORKSPACE_STYLES_START' in css
    assert html.index('</head>')<html.index('<body'),'HTML document head missing'
    html=html.replace('</head>','<style id="se473ModelFoldingWorkspace">\n'+css+
      '\n</style>\n</head>',1)

    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_472_FULL_RES_TEXTURES',MARKER),
      ('ENGINE · MAKER v11.472','ENGINE · MAKER v11.473'),
      ('v11.472 · preserve original imported textures','v11.473 · floating UV and collapsible workspace'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.472'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.473'"),
      ('<title>§wyrl§ Engine · Maker v11.472</title>',
       '<title>§wyrl§ Engine · Maker v11.473</title>')
    ]:html=once(html,old,new,'release identity '+old[:50])
    prior=" source.engine='§wyrl§ Engine · Maker v11.472';source.version=11.472;"
    assert html.count(prior)==5,('model provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.473';source.version=11.473;")
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.472']
    notes['history'].insert(0,{'version':'v11.472','changes':notes.get('changes',[])})
    notes.update(version='v11.473',date='2026-11-16',
      title='Free-moving UV dialog, tap-to-collapse sidebars and folding tool rail',
      changes=[
        'UV Editor titlebar drags the existing popup anywhere within the browser viewport, including over the hierarchy, sidebars, and header; it is no longer clipped to the 3D canvas.',
        'Popup position and resized dimensions persist locally; reopen restores them, while viewport changes keep the titlebar inside visible bounds.',
        'Model Studio native side divider handles now distinguish a tap (collapse or restore) from a drag (resize); existing saved side widths are retained on expansion.',
        'Divider Enter/Space toggles folded sidebars; Arrow keys continue to resize. Handles remain available while the inspector is collapsed.',
        'Vertical tool category rail has a top fold/expand handle; collapsed tools retract upward and release workspace width while preserving selected tools and mesh state.',
        'Tool rail folded state persists separately from the saved side-panel sizes. Compact touch layouts retain an accessible expand handle.',
        'UV texture import, shape-fit, local/account projects, undo history, VR tools and underlying rendering remain otherwise unchanged.',
        'Automated regression verification does not replace owner acceptance on Moto and Quest.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[pos+n:]
