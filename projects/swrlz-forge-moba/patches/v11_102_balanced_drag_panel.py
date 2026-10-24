"""Restore real touch dragging and balanced compact mobile Model Atelier sizing."""
import hashlib
import json

def once(src,old,new):
    count=src.count(old)
    assert count==1,(old[:110],count)
    return src.replace(old,new,1)

CSS = """
/* §E v11.102: the inspector uses sensible default dimensions AND real dragging. */
@media (max-width:980px), (pointer:coarse) {
 .model-atelier.atelier-tools-docked:not(.atelier-tools-closed) .atelier-inspector,
 .model-atelier.atelier-tools-docked.atelier-mobile-upgrade:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {
  width:min(390px,calc(100vw - 44px))!important;
  height:min(34dvh,350px)!important;
  max-height:min(34dvh,350px)!important;
  min-height:0!important;
  top:auto!important;left:auto!important;
  right:20px!important;
  bottom:calc(68px + env(safe-area-inset-bottom,0px) + var(--atelier-keyboard-offset,0px))!important;
  pointer-events:auto!important;
  touch-action:pan-y!important;
  overflow-y:auto!important;-webkit-overflow-scrolling:touch;
  overscroll-behavior-y:contain!important;
 }
 .model-atelier.atelier-tools-docked.se-mobile-inspector-expanded:not(.atelier-tools-closed) .atelier-inspector,
 .model-atelier.atelier-tools-docked.atelier-mobile-upgrade.se-mobile-inspector-expanded:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {
  width:min(440px,calc(100vw - 32px))!important;
  height:min(43dvh,440px)!important;
  max-height:min(43dvh,440px)!important;
 }
 /* Critical: original free-drag JS moves via top and left inline styles, but
    mobile rules pinned top/left:auto and right/bottom with !important.
    When the old handler moves, use its requested coordinates explicitly. */
 .model-atelier.atelier-tools-docked.se-mobile-inspector-dragged:not(.atelier-tools-closed) .atelier-inspector,
 .model-atelier.atelier-tools-docked.atelier-mobile-upgrade.se-mobile-inspector-dragged:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {
  position:fixed!important;
  left:var(--se-mobile-drag-left,auto)!important;
  top:var(--se-mobile-drag-top,auto)!important;
  right:auto!important;
  bottom:auto!important;
  transform:none!important;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector .atelier-tool-handle {
  touch-action:none!important;
  cursor:grab;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector .atelier-tool-handle:active {cursor:grabbing}
 .model-atelier.atelier-tools-docked .atelier-inspector .atelier-tool-handle :is(button,input,select) {
  touch-action:manipulation!important;
 }
 .model-atelier .atelier-context-workbench:not([hidden]){
  height:min(34dvh,350px)!important;max-height:min(34dvh,350px)!important;
 }
 .model-atelier .atelier-context-workbench[data-mobile-size="expanded"]:not([hidden]){
  height:min(43dvh,440px)!important;max-height:min(43dvh,440px)!important;
 }
 .model-atelier .atelier-context-workbench[data-mobile-size="compact"]:not([hidden]){
  height:52px!important;max-height:52px!important;
 }
}
"""

def apply(html):
    # Patch only the assembled runtime's existing drag handler. Do not add a
    # separate pointer listener or change native model/mesh event handlers.
    html=once(html,
      "inspector.style.left=left+'px';inspector.style.top=top+'px';inspector.style.right='auto';",
      "panel.classList.add('se-mobile-inspector-dragged');"+
      "inspector.style.setProperty('--se-mobile-drag-left',left+'px');"+
      "inspector.style.setProperty('--se-mobile-drag-top',top+'px');"+
      "inspector.style.left=left+'px';inspector.style.top=top+'px';inspector.style.right='auto';")
    assert '</head>' in html
    html=html.replace('</head>','<style id="se-v11102-balanced-drag-panel">'+CSS+'</style>\n</head>',1)
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_101_COMPACT_QUARTER_PANEL',
                   'SWYRL_ENGINE_DEPLOY_MARKER: V11_102_BALANCED_DRAGGABLE_PANEL')
    for a,b in [
       ('ENGINE · MAKER v11.101','ENGINE · MAKER v11.102'),
       ('v11.101 · quarter-screen compact tools','v11.102 · balanced draggable mobile tools'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.101'","window.SWRLZ_FORGE_BUILD={version:'v11.102'"),
       ('<title>§wyrl§ Engine · Maker v11.101</title>','<title>§wyrl§ Engine · Maker v11.102</title>'),
    ]:html=once(html,a,b)
    k='const SE_RELEASE_NOTES=';p=html.index(k)+len(k)
    notes,size=json.JSONDecoder().raw_decode(html[p:])
    notes.update(title='Balanced mobile panels with restored manual dragging',
      date='2026-10-23',changes=[
       'Raise default inspector size from 26dvh/320px wide to a balanced 34dvh/390px max width and cap optional Expand at 43dvh/440px max width.',
       'Let the original Model Atelier header pointer-drag actually position its inspector despite former mobile !important right/bottom docking overrides.',
       'Keep touch-only scrolling gutters, intentional press-and-hold numeric edits, built-in tool navigation and existing models unchanged.'
    ])
    html=html[:p]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[p+size:]
    b=html.encode('utf8')
    print('SWRLZ_V11102_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
    return html
