"""§E v11.167: authoritative host-frame guest movement and strict placement."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:120],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_guest_motion_placement_v11_167.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_166_GUEST_INPUT_VISUAL',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_167_HOST_DIRECT_MOVE_STRICT_BUILD')
 for a,b in [
  ('ENGINE · MAKER v11.166','ENGINE · MAKER v11.167'),
  ('v11.166 · responsive guest sheep movement',
   'v11.167 · real host sheep movement and legal build previews'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.166'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.167'"),
  ('<title>§wyrl§ Engine · Maker v11.166</title>',
   '<title>§wyrl§ Engine · Maker v11.167</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 i=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[i:])
 notes.update(title='Real host-driven guest joystick and protected no-build zones',
 date='2026-10-28',changes=[
  'Real Android guest screenshot: a prohibited central zone falsely displayed a green house preview, and the sheep circled in place instead of moving in the host world.',
  'Remove the v11.162 permissive client preview fallback. Preserve native Sheep Tag pen/no-build/obstacle/occupied-footprint rejection rules and host final placement authority.',
  'Send actual joystick inputs promptly on pointer motion, throttled to about 65ms, plus immediate press and release over existing authenticated PeerJS data connection.',
  'Apply host-verified guest movement in native authoritative gameplay steps, including the v11.164 host-background catch-up frames, instead of only once on the old 130ms world-snapshot tick.',
  'Use native collision checks and short tangent sliding to escape tight paths without allowing movement through buildings or rocks; protect accepted house build approach orders.',
  'Provide in-world host movement status for each guest (moving, blocked, stale packet, idle, captured) and telemetry through SWYRL_ENGINE_LAN.guestControlV165().',
  'Retain the already-deployed v11.165 frame-performance optimization and v11.166 bounded visual input prediction; new runtime state uses distinct se167 names.',
  'Focused JS checks: host moved in gameplay frame, no duplicate snapshot movement, protected placement remained invalid, joystick press/release delivered. Actual cross-device acceptance pending.',
  'Automatic LAN discovery, building replication/growth, team fog, wolf release and the HF build+upload-only deployment workflow unchanged.'
 ])
 html=html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
 return html
