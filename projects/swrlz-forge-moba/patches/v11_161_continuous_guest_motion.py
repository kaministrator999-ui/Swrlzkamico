"""§E v11.161: continuous guest interpolation without per-packet ease-to-zero."""
from pathlib import Path
import json
def once(source,old,new):
 assert source.count(old)==1,(old[:90],source.count(old))
 return source.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_continuous_guest_motion_v11_161.js').read_text(encoding='utf-8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_160_GUEST_BUILD_WOLF_RELEASE',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_161_CONTINUOUS_GUEST_MOTION')
 for old,new in [
  ('ENGINE · MAKER v11.160','ENGINE · MAKER v11.161'),
  ('v11.160 · visible guest houses and timed wolf release',
   'v11.161 · continuous LAN guest sheep motion'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.160'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.161'"),
  ('<title>§wyrl§ Engine · Maker v11.160</title>',
   '<title>§wyrl§ Engine · Maker v11.161</title>')
 ]:html=once(html,old,new)
 tag='const SE_RELEASE_NOTES='
 pos=html.index(tag)+len(tag)
 notes,end=json.JSONDecoder().raw_decode(html[pos:])
 notes.update(title='Continuous multiplayer sheep motion between host snapshots',
 date='2026-10-27',changes=[
  'Preserve the already working live LAN-style discovery and one-tap join; host remains authoritative.',
  'Replace per-snapshot smoothstep ease-in/ease-out (which decelerated to zero every 130ms) with continuous bounded velocity prediction and exponential visual correction.',
  'Use only the existing guest requestAnimationFrame loop; suppress redundant native guest animation, without enabling a second gameplay simulation.',
  'Handle network jitter, captured units, teleport/rescue jumps and stale updates with bounded prediction and host correction.',
  'Do not touch guest building synchronization, fog, wolf countdown or host input authority.',
  'Focused deterministic JS test: 11 snapshots/85 frame simulation, positive motion throughout after startup, no duplicate guest native frame.',
  'GitHub Actions remains only package and Hugging Face upload. Physical two-browser visual acceptance pending.'
 ])
 html=html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+end:]
 return html
