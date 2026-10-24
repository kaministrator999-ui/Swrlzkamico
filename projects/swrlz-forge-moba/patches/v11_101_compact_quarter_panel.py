"""Actual quarter-screen phone defaults for native Atelier inspector and context."""
import hashlib
import json

CSS = """
/* §E v11.101: user-tested compact phone panel; deliberately less than half-screen. */
@media (max-width:980px), (pointer:coarse) {
 .model-atelier.atelier-tools-docked:not(.atelier-tools-closed) .atelier-inspector,
 .model-atelier.atelier-tools-docked.atelier-mobile-upgrade:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {
  width:min(320px,calc(100vw - 56px))!important;
  height:min(26dvh,255px)!important;
  max-height:min(26dvh,255px)!important;
  left:auto!important;right:20px!important;
  min-height:0!important;
  pointer-events:auto!important;
  overflow-x:hidden!important;overflow-y:auto!important;
  touch-action:pan-y!important;overscroll-behavior-y:contain!important;
 }
 .model-atelier.atelier-tools-docked.se-mobile-inspector-expanded:not(.atelier-tools-closed) .atelier-inspector,
 .model-atelier.atelier-tools-docked.atelier-mobile-upgrade.se-mobile-inspector-expanded:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {
  width:min(375px,calc(100vw - 40px))!important;
  height:min(38dvh,385px)!important;
  max-height:min(38dvh,385px)!important;
 }
 .model-atelier.atelier-mobile-upgrade .atelier-context-workbench:not([hidden]),
 .model-atelier .atelier-context-workbench:not([hidden]){
  height:min(26dvh,255px)!important;
  max-height:min(26dvh,255px)!important;
 }
 .model-atelier.atelier-mobile-upgrade .atelier-context-workbench[data-mobile-size="expanded"]:not([hidden]),
 .model-atelier .atelier-context-workbench[data-mobile-size="expanded"]:not([hidden]){
  height:min(38dvh,385px)!important;
  max-height:min(38dvh,385px)!important;
 }
 .model-atelier.atelier-mobile-upgrade .atelier-context-workbench[data-mobile-size="compact"]:not([hidden]),
 .model-atelier .atelier-context-workbench[data-mobile-size="compact"]:not([hidden]){
  height:52px!important;max-height:52px!important;
 }
}
"""

def once(html,a,b):
    count=html.count(a)
    assert count==1,(a[:120],count)
    return html.replace(a,b,1)

def apply(html):
    # Append scoped overrides after 11.100 rules to win normal cascade; the
    # more specific adaptive-mobile selector overrides old 11.62 !important.
    assert '</head>' in html
    html=html.replace('</head>','<style id="se-v11101-compact-quarter-panel">'+CSS+'</style>\n</head>',1)
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_100_HOLD_SCROLL_GUTTERS',
                   'SWYRL_ENGINE_DEPLOY_MARKER: V11_101_COMPACT_QUARTER_PANEL')
    for a,b in [
      ('ENGINE · MAKER v11.100','ENGINE · MAKER v11.101'),
      ('v11.100 · comfortable scrolling and hold-to-edit','v11.101 · quarter-screen compact tools'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.100'","window.SWRLZ_FORGE_BUILD={version:'v11.101'"),
      ('<title>§wyrl§ Engine · Maker v11.100</title>','<title>§wyrl§ Engine · Maker v11.101</title>'),
    ]:html=once(html,a,b)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Genuinely compact quarter-screen mobile tool panel',date='2026-10-23',changes=[
      'Reduce mobile inspector default from roughly 49% viewport height to at most 26% and 255 CSS px; reduce width to at most 320 CSS px.',
      'Expand explicitly to only 38% / 385 CSS px and at most 375 CSS px wide, rather than 62% screen height.',
      'Correct specificity against the older adaptive mobile sheet; reduce context panels similarly.',
      'Preserve side swipe gutters, press-and-hold numeric entry, native sculpt controls and all existing meshes.'
    ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    raw=html.encode('utf-8')
    print('SWRLZ_V11101_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
    return html
