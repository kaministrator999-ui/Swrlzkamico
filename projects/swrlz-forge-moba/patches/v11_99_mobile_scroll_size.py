"""Enlarge phone modeling sheets and restore finger-scroll hit testing."""
import hashlib
import json

def one(s,a,b):
    count=s.count(a)
    assert count==1,(a[:130],count)
    return s.replace(a,b,1)

CSS = """
/* §E 11.99 mobile native editing: prioritize scrollable tool sheets. */
@media (max-width:980px), (pointer:coarse) {
 .model-atelier.atelier-tools-docked:not(.atelier-tools-closed) .atelier-inspector {
  position:fixed!important;
  top:auto!important;left:8px!important;right:8px!important;
  bottom:calc(70px + env(safe-area-inset-bottom,0px) + var(--atelier-keyboard-offset,0px))!important;
  width:calc(100vw - 16px)!important;
  height:min(64dvh,calc(var(--atelier-visible-height,100dvh) - 142px))!important;
  max-height:calc(var(--atelier-visible-height,100dvh) - 142px)!important;
  min-height:0!important;
  padding:12px!important;gap:11px!important;
  pointer-events:auto!important;
  touch-action:pan-y!important;
  overflow-x:hidden!important;overflow-y:auto!important;
  overscroll-behavior-y:contain!important;
  -webkit-overflow-scrolling:touch;
  scrollbar-width:auto;
  z-index:2167!important;
 }
 /* Older desktop dock has pointer-events:none on empty inspector areas.
    Re-enable those areas as draggable page scrolling targets on mobile. */
 .model-atelier .atelier-inspector :is(fieldset,section,div,p,small,h3,strong,label) {
  touch-action:pan-y;
 }
 /* Inspector's handle stays an independent draggable control. */
 .model-atelier.atelier-tools-docked .atelier-tool-rail {
  position:fixed!important;
  top:auto!important;left:8px!important;right:8px!important;
  bottom:calc(5px + env(safe-area-inset-bottom,0px))!important;
  width:calc(100vw - 16px)!important;max-width:none!important;
  height:58px!important;max-height:58px!important;
  display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;
  justify-content:flex-start!important;align-items:center!important;
  overflow-x:auto!important;overflow-y:hidden!important;
  touch-action:pan-x!important;overscroll-behavior-x:contain;
  z-index:2169!important;
 }
 .model-atelier.atelier-tools-docked .atelier-tool-rail button {
  flex:0 0 auto!important;
  min-width:73px!important;max-width:none!important;
  min-height:44px!important;font-size:13px!important;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector label,
 .model-atelier.atelier-tools-docked .atelier-inspector legend {
  font-size:14px!important;line-height:1.4;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector p,
 .model-atelier.atelier-tools-docked .atelier-inspector small {
  font-size:13px!important;line-height:1.45;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector :is(button,input:not([type="checkbox"]):not([type="radio"]):not([type="color"]):not([type="range"]):not([type="file"]),select,textarea) {
  min-height:44px!important;
  font-size:16px!important;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector :is(section,fieldset) {
  min-width:0;max-width:100%;
 }
 .model-atelier.atelier-tools-docked .atelier-inspector :is(section,fieldset,[id^="modelAtelierSculptBrush"]) {
  scroll-margin-top:65px;
 }
 .model-atelier.atelier-mobile-upgrade .atelier-context-workbench:not([hidden]) {
  height:min(60dvh,calc(var(--atelier-visible-height,100dvh) - 135px))!important;
  max-height:calc(var(--atelier-visible-height,100dvh) - 135px)!important;
  overflow:hidden!important;
 }
 .model-atelier.atelier-mobile-upgrade .atelier-context-workbench[data-mobile-size="expanded"]:not([hidden]) {
  height:min(80dvh,calc(var(--atelier-visible-height,100dvh) - 135px))!important;
 }
 .model-atelier.atelier-mobile-upgrade .atelier-context-workbench[data-mobile-size="compact"]:not([hidden]) {
  height:52px!important;max-height:52px!important;
 }
 .model-atelier .atelier-context-workbench :is(.atelier-context-right,.atelier-context-left,.atelier-context-body) {
  min-height:0;pointer-events:auto!important;touch-action:pan-y!important;
  -webkit-overflow-scrolling:touch;overscroll-behavior-y:contain;
 }
 .model-atelier .atelier-context-workbench :is(.atelier-context-right,.atelier-context-left) {
  overflow-y:auto!important;
 }
}
"""

def apply(html):
    # Widen prior mobile supervisor's width trigger to include touch browsers
    # in desktop-site/zoomed layout. Keep desktop mouse layouts unchanged.
    html=one(html,
        "matchMedia('(max-width:700px), (max-height:600px) and (pointer:coarse)')",
        "matchMedia('(max-width:980px), (pointer:coarse)')")
    html=one(html,
        "@media (max-width:700px),(max-height:600px) and (pointer:coarse){",
        "@media (max-width:980px),(pointer:coarse){")
    assert '</head>' in html
    html=html.replace('</head>','<style id="se-v1199-mobile-scroll-size">'+CSS+'</style>\n</head>',1)
    html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_98_MOBILE_NUMPAD_TOUCH_FIX',
                 'SWYRL_ENGINE_DEPLOY_MARKER: V11_99_MOBILE_SCROLL_SIZE')
    for a,b in [
      ('ENGINE · MAKER v11.98','ENGINE · MAKER v11.99'),
      ('v11.98 · stable mobile number pad','v11.99 · enlarged scrollable mobile menus'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.98'","window.SWRLZ_FORGE_BUILD={version:'v11.99'"),
      ('<title>§wyrl§ Engine · Maker v11.98</title>','<title>§wyrl§ Engine · Maker v11.99</title>'),
    ]:html=one(html,a,b)
    p='const SE_RELEASE_NOTES='
    at=html.index(p)+len(p)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Larger scrollable mobile Model Atelier menus',date='2026-10-23',changes=[
      'Fix mobile inspector swipe targeting, including empty panel space, by restoring pointer events and vertical touch scrolling.',
      'Enlarge and widen touch-screen editing panels and make the tool rail horizontally scrollable.',
      'Ensure coarse-pointer/desktop-site phones can activate existing mobile controls.',
      'Preserve native sculpt, numeric keypad, saves, assets and existing character geometry.'
    ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    raw=html.encode('utf8')
    print('SWRLZ_V1199_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
