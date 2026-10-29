"""§E v11.162 — reliable guest building command and authoritative results."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_reliable_guest_build_v11_162.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_161_CONTINUOUS_GUEST_MOTION',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_162_RELIABLE_GUEST_HOUSE_ORDERS')
 for old,new in [
  ('ENGINE · MAKER v11.161','ENGINE · MAKER v11.162'),
  ('v11.161 · continuous LAN guest sheep motion',
   'v11.162 · reliable guest house construction'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.161'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.162'"),
  ('<title>§wyrl§ Engine · Maker v11.161</title>',
   '<title>§wyrl§ Engine · Maker v11.162</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Host-validated guest houses with acceptance and completion receipts',
 date='2026-10-28',changes=[
  'Treat guest build requests as discrete host commands, separate from the v11.152 shared joystick throttle that could silently discard construction taps.',
  'Validate house type, owner, live player seat, request ID, current match and site on the host using the native build command and navigation rules; never invent local structures.',
  'Send explicit host accepted/rejected/completed feedback. Completion is emitted only on real host stNewBuilding with matching owner and location.',
  'Guest placement preview is advisory against snapshot lag, while the host alone validates final resources, bounds, geometry and path; invalid sites receive a rejection.',
  'Clear lingering joystick input after a host accepts construction so its order is not immediately cancelled. Preserve owner control and prior movement smoothing.',
  'Expose diagnostic SWYRL_ENGINE_LAN.houseOrders() for guest sent/accepted/rejected/completed and host pending/completed counts.',
  'Focused JS test passed for a build arriving within an existing joystick-throttle interval, completion receipt, host rejection and guest local-preview fallback.',
  'All existing engine assets, lobby autodiscovery, LAN peer world, fog, wolf countdown and v11.161 guest motion remain unchanged. GitHub Action is package+upload only.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 return html
