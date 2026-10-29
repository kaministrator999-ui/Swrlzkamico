"""§E v11.139 · safely magnetize invalid Rapid corner cracks to flush corners."""
from pathlib import Path
import hashlib,json
def once(s,a,b):
 assert s.count(a)==1,(a[:150],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_rapid_corner_snap_v11_139.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_138_RAPID_LAST_BUILD_SCREEN_ANCHOR',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_139_SAFE_RAPID_CORNER_SNAP')
 for old,new in [
  ('ENGINE · MAKER v11.138','ENGINE · MAKER v11.139'),
  ('v11.138 · rapid remembers last placement on screen','v11.139 · safe rapid house corner snap'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.138'","window.SWRLZ_FORGE_BUILD={version:'v11.139'"),
  ('<title>§wyrl§ Engine · Maker v11.138</title>','<title>§wyrl§ Engine · Maker v11.139</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Rapid safe corner snapping for sheep housing',
  date='2026-10-26',changes=[
  'Fix the red diagonal-crack placement seen in owner Android screenshot: a near-corner Rapid house now tries the closest flush corner within a small radius, but only after the existing validator reports a diagonal slit.',
  'The proposed snapped house must independently pass ALL original native collision, sheep passage, ownership, and bounds checks; invalid locations remain red. The ghost uses the same returned validated snapped center as the final build command.',
  'No weakening of minimum 1.20m safe sheep routes or diagonal-blocker detection. Structures far from a corner or normal Rapid OFF placements behave exactly as before.',
  'Preserve v11.138 screen-position memory, touch meadow-first drag, bots, wolves, performance, abilities, 68 original assets and multiplayer plans.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SE_V11139_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
