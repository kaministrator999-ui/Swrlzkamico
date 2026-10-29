"""§E v11.156: smooth guest rendering, all building types and team fog vision."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:110],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_shared_visual_build_fog_v11_156.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_155_SNAPSHOT_DRIVEN_GUEST',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_156_SMOOTH_BUILD_TEAM_FOG')
 for old,new in [
  ('ENGINE · MAKER v11.155','ENGINE · MAKER v11.156'),
  ('v11.155 · snapshot-driven guest sheep movement',
   'v11.156 · smooth guests, shared structures and team fog'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.155'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.156'"),
  ('<title>§wyrl§ Engine · Maker v11.155</title>',
   '<title>§wyrl§ Engine · Maker v11.156</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Smooth Sheep Tag multiplayer, host house mirroring and team fog',
 date='2026-10-27',changes=[
  'Guest receives host animal positions and interpolates smoothly between authoritative snapshots with bounded predictive lookahead.',
  'Host built houses, walls, ramps and other supported game structures mirror on guests with real progress, ownership and rotation.',
  'The host acknowledges guest building orders and guest HUD clears the ghost placement, then mirrors actual completed structures.',
  'Sheep team fog of war reveals ground around living sheep and friendly owned houses, including on guest worlds without a simulation tick.',
  'Wolf team has independent wolf vision without borrowing sheep houses; fog exploration persists per current match.',
  'The host remains authoritative. No new game simulation or network service; GitHub deploy remains package and upload only.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 return html
