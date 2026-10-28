"""§E v11.166: bounded guest-local joystick visual prediction."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_guest_input_visual_v11_166.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_165_GUEST_FRAME_PERFORMANCE',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_166_GUEST_INPUT_VISUAL')
 for a,b in [
  ('ENGINE · MAKER v11.165','ENGINE · MAKER v11.166'),
  ('v11.165 · smooth many-house guest rendering',
   'v11.166 · responsive guest sheep movement'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.165'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.166'"),
  ('<title>§wyrl§ Engine · Maker v11.165</title>',
   '<title>§wyrl§ Engine · Maker v11.166</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='More responsive multiplayer sheep under host snapshot delay',
 date='2026-10-28',changes=[
  'Retain v11.165 reduced guest frame workload: coalesced team fog and cached unchanged house records.',
  'When a LAN guest holds the joystick, the guest-only visual movement target can anticipate the next authoritative host snapshot by at most 0.8 world units.',
  'Do not predict through blocked terrain, move a captured sheep, move a pre-release wolf, or predict when paused or ended.',
  'Preserve authoritative host positions at all times: the temporary render bias is restored immediately after the single existing guest frame, and released inputs smoothly return to the host position.',
  'Build orders, physics, network authority, lobby discovery and building synchronization are unchanged, with no additional intervals, WebRTC traffic or game simulation.',
  'Expose SWYRL_ENGINE_LAN.inputResponse() for visual lead and collision-suppression counters.',
  'Focused V8 test passed: responsive local visual movement, maximum lead 0.8 units, host anchor never mutated, smooth convergence when released, collision rejection and host role untouched.',
  'Browser-suspended hosts cannot guarantee fresh server snapshots; physical two-device smoothness acceptance remains pending.',
  'GitHub Action is still only package and upload to Hugging Face, no Chromium/remote audits.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 return html
