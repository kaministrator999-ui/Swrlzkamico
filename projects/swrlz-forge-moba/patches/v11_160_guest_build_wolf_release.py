"""§E v11.160: reliable guest building create event and wolf headstart visibility."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:90],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_guest_build_wolf_release_v11_160.js').read_text(encoding='utf-8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_159_LIVE_GAME_DIRECTORY',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_160_GUEST_BUILD_WOLF_RELEASE')
 for old,new in [
  ('ENGINE · MAKER v11.159','ENGINE · MAKER v11.160'),
  ('v11.159 · automatic live multiplayer game discovery',
   'v11.160 · visible guest houses and timed wolf release'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.159'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.160'"),
  ('<title>§wyrl§ Engine · Maker v11.159</title>',
   '<title>§wyrl§ Engine · Maker v11.160</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[pos:])
 notes.update(title='Guest Sheep Tag buildings render and wolves release on countdown',
 date='2026-10-27',changes=[
  'On real host structure creation, send a verified room/match-bound building-created event to connected guests, in addition to all ongoing authoritative world snapshots.',
  'Guest renders the new host-owned house using its real model, preserves host IDs, updates native scene placement, and clears the local ghost only after confirmed host construction.',
  'Existing v11.157 snapshot reconciler stays authoritative and recovers missed events; houses remain allied-visible even with active team fog.',
  'Protect a sheep approaching an accepted building site from the older guest joystick handler cancelling its build order.',
  'Wolf models are hidden for the entire initial head-start; they become visible once the actual release countdown expires on both host and guest, while existing movement and attack locks stay intact.',
  'Focused JavaScript tests covered host building creation event, guest house rendering, wolf visibility before and after release.',
  'No new game simulation, service or CI jobs. HF deployment remains package and upload only.'
 ])
 html=html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
 return html
