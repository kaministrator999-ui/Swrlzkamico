"""§E v11.165: guest joystick frame movement and strict build preview rules."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:120],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_guest_motion_placement_v11_165.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_164_HOST_BACKGROUND_SIM',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_165_GUEST_DIRECT_MOVE_STRICT_BUILD')
 for old,new in [
  ('ENGINE · MAKER v11.164','ENGINE · MAKER v11.165'),
  ('v11.164 · background-safe host game simulation',
   'v11.165 · responsive guest movement and valid house placement'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.164'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.165'"),
  ('<title>§wyrl§ Engine · Maker v11.164</title>',
   '<title>§wyrl§ Engine · Maker v11.165</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[pos:])
 notes.update(title='Responsive guest joystick and legal building preview',
 date='2026-10-28',changes=[
  'A real guest phone screenshot showed a green building placement inside the central protected area, while guest joystick movement could appear to circle in place with no actual host translation.',
  'Restore the native Sheep Tag validation for all guest placement previews: never turn a Spirit Pen, no-build zone, obstacle or occupied house into a falsely green buildable site. The host remains the final source of truth.',
  'Send real guest joystick intent when pointer moves (throttled to roughly 65ms), with immediate start and release; retain the existing LAN joystick interval and authenticated PeerJS connection.',
  'Apply the verified guest joystick on the host native gameplay frames including the existing v11.164 host-background catch-up frames; do not move the sheep again on 130ms network snapshots.',
  'Use native collision constraints and bounded tangent movement around adjacent obstacles; never allow walking through blocked map objects or while a host-accepted build order approaches its site.',
  'Add per-snapshot host movement diagnostics (moving, collision, stale packet, idle, capture, etc.) to guest HUD and SWYRL_ENGINE_LAN.guestControlV165() so remaining failures can be isolated.',
  'Keep the v11.161 continuous guest renderer, v11.164 authoritative host simulation, auto room search, building synchronization, fog and timed wolf release unchanged.',
  'Focused JavaScript test passed: host movement in native frame, no double move on snapshot, central restricted placement rejected, joystick press/release packets transmitted.',
  'Physical two-browser acceptance remains pending. GitHub Actions keeps package and Hugging Face upload only.'
 ])
 html=html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
 return html
