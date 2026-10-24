"""Double Model Atelier's mobile inspector height without changing width or drag behavior."""
import hashlib
import json

CSS = """
/* §E v11.103: double the user-confirmed v11.102 tool window height only. */
@media (max-width:980px), (pointer:coarse) {
 .model-atelier.atelier-tools-docked:not(.atelier-tools-closed) .atelier-inspector,
 .model-atelier.atelier-tools-docked.atelier-mobile-upgrade:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {
  height:min(68dvh,700px)!important;
  max-height:min(68dvh,700px)!important;
 }
 /* Expand remains larger than default, rather than becoming a shrink toggle. */
 .model-atelier.atelier-tools-docked.se-mobile-inspector-expanded:not(.atelier-tools-closed) .atelier-inspector,
 .model-atelier.atelier-tools-docked.atelier-mobile-upgrade.se-mobile-inspector-expanded:not(.atelier-mobile-context-mode):not(.atelier-tools-closed) .atelier-inspector {
  height:min(78dvh,800px)!important;
  max-height:min(78dvh,800px)!important;
 }
}
"""

def once(s,a,b):
    assert s.count(a)==1,(a[:105],s.count(a))
    return s.replace(a,b,1)

def apply(html):
    assert '</head>' in html
    html=html.replace('</head>','<style id="se-v11103-double-inspector-height">'+CSS+'</style>\n</head>',1)
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_102_BALANCED_DRAGGABLE_PANEL',
                   'SWYRL_ENGINE_DEPLOY_MARKER: V11_103_DOUBLE_INSPECTOR_HEIGHT')
    for a,b in [
      ('ENGINE · MAKER v11.102','ENGINE · MAKER v11.103'),
      ('v11.102 · balanced draggable mobile tools','v11.103 · taller draggable mobile tools'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.102'","window.SWRLZ_FORGE_BUILD={version:'v11.103'"),
      ('<title>§wyrl§ Engine · Maker v11.102</title>','<title>§wyrl§ Engine · Maker v11.103</title>'),
    ]:html=once(html,a,b)
    p='const SE_RELEASE_NOTES='
    at=html.index(p)+len(p)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Doubled mobile Model Atelier tool panel height',
      date='2026-10-24',changes=[
       'Double the mobile default tool inspector height from 34dvh/350px maximum to 68dvh/700px maximum while preserving its existing width.',
       'Keep Expand taller than default at 78dvh/800px maximum, without changing panel positioning or dragging.',
       'Preserve side scroll gutters, press-and-hold numeric editing, scene geometry, exports and existing native controls.'
    ])
    html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
    b=html.encode('utf-8')
    print('SWRLZ_V11103_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
    return html
