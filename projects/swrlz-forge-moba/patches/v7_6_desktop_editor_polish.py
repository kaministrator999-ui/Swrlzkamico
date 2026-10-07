"""§wyrl§ Engine v7.6: desktop editor chrome polish."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.6 token missing: "+old[:220])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V7_5_MOBILE_EDITOR_CHROME":"V7_6_DESKTOP_EDITOR_POLISH",
      "Maker v7.5":"Maker v7.6","MAKER v7.5":"MAKER v7.6",
      "v7.5 · MOBILE EDITOR CHROME":"v7.6 · DESKTOP EDITOR POLISH",
      "version:'v7.5'":"version:'v7.6'",
      "version:'swyrl-engine-agent-v5.5'":"version:'swyrl-engine-agent-v5.6'",
      "engine:'§wyrl§ Engine · Maker v7.5'":"engine:'§wyrl§ Engine · Maker v7.6'",
      "version:7.5":"version:7.6",
      "editorLog('§wyrl§ Engine v7.5 initialized · consolidated mobile editor chrome','ok')":"editorLog('§wyrl§ Engine v7.6 initialized · polished desktop editor chrome','ok')"
    }.items(): s=_once(s,a,b)

    css=r"""
/* v7.6 desktop authoring lanes */
@media(min-width:721px){
 .engine-menubar{top:0!important;left:0!important;right:0!important;height:38px!important;border-radius:0!important;border-width:0 0 1px!important;padding:3px 8px!important;box-sizing:border-box!important}
 .app{padding-top:38px!important}
 .engine-command-deck{display:none!important}
 .mobile-engine-trigger{display:none!important}
 .workspace-launcher{top:44px!important;left:12px!important;right:12px!important;max-height:72vh!important;overflow:auto!important}
 .engine-stats-pill{top:44px!important;right:12px!important;bottom:auto!important}
 .viewport-shortcuts,.viewport-hints,.camera-hints,.editor-hints{bottom:34px!important;top:auto!important;max-width:46%!important}
 .statusbar,.status-bar,.editor-status{z-index:44!important}
}
"""
    s=_once(s,"</style>",css+"\n</style>")

    # Add stable semantic classes to legacy viewport hint/status nodes when identifiable,
    # so future layout patches can dock them without relying on visual guesswork.
    marker="installEngineMenus();"
    js=r"""
function polishDesktopEditorChrome(){
  if(innerWidth<=720)return;
  // v7.4 Command Deck duplicated menu/workspace actions on desktop; the menu is authoritative now.
  document.querySelectorAll('.engine-command-deck').forEach(e=>e.setAttribute('aria-hidden','true'));
  // Classify the two small viewport help overlays by their actual text.
  document.querySelectorAll('div').forEach(e=>{
    const t=(e.textContent||'').trim();
    if(t.includes('W')&&t.includes('move')&&t.includes('rotate')&&t.includes('scale')&&e.children.length<12)e.classList.add('viewport-shortcuts');
    if(t.includes('Perspective')&&t.includes('orbit')&&t.includes('Top/Front/Right'))e.classList.add('camera-hints');
  });
}
polishDesktopEditorChrome();
addEventListener('resize',()=>{if(innerWidth>720)polishDesktopEditorChrome()},{passive:true});
"""
    s=_once(s,marker,marker+"\n"+js)
    return s
