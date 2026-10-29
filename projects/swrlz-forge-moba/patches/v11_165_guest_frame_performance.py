"""§E v11.165: coalesce guest fog redraws and reuse unchanged structure states."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:110],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_guest_frame_performance_v11_165.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_164_HOST_BACKGROUND_SIM',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_165_GUEST_FRAME_PERFORMANCE')
 for a,b in [
  ('ENGINE · MAKER v11.164','ENGINE · MAKER v11.165'),
  ('v11.164 · background-safe host game simulation',
   'v11.165 · smooth many-house guest rendering'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.164'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.165'"),
  ('<title>§wyrl§ Engine · Maker v11.164</title>',
   '<title>§wyrl§ Engine · Maker v11.165</title>')
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES='
 at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Faster multiplayer rendering with many sheep houses',
 date='2026-10-28',changes=[
  'Real guest screenshot confirms house building works and all 36/36 structures replicate, but guest movement and camera rendering lag under many houses.',
  'Batch repeated guest fog-of-war requests from existing snapshot/building/visibility wrappers into the current single guest requestAnimationFrame, with around four repaints per second and immediate updates when teams, captures, or house counts change.',
  'Reuse valid host-owned building records when every authoritative field is unchanged, avoiding repeated mesh scaling, ownership work and transform updates on every 130ms packet. Changes to HP, progress, position, rotation or ownership still apply normally.',
  'Preserve v11.163 authoritative house growth and the existing shared-team fog mask; no new animation loop or second networking service.',
  'Show real guest render FPS and snapshot work milliseconds in the LAN badge and expose detailed SWYRL_ENGINE_LAN.performance() counters.',
  'Focused simulated 36-house load: 60 packets/480 guest frames, redundant building writes reduced from 2160 potential to 37, repeated fog paints reduced from 180 requests to 32. This is not a physical-device frame-rate guarantee.',
  'Host background simulation, one-tap LAN lobby discovery, wolf release, guest input and native gameplay logic remain untouched.',
  'Only build/package and Hugging Face upload run in the production GitHub workflow; no Chromium or remote verification.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 return html
