"""§E v11.158: captured network guest retains its owned sheep/wisp."""
from pathlib import Path
import json
def once(s,old,new):
 assert s.count(old)==1,(old[:100],s.count(old))
 return s.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_fixed_guest_lives_v11_158.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_157_AUTHORITATIVE_BUILD_REPLICA',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_158_GUEST_LIVES_FIXED_SEAT')
 for a,b in [
  ('ENGINE · MAKER v11.157','ENGINE · MAKER v11.158'),
  ('v11.157 · reliable host-to-guest building replication',
   'v11.158 · stable guest ownership after capture'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.157'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.158'"),
  ('<title>§wyrl§ Engine · Maker v11.157</title>',
   '<title>§wyrl§ Engine · Maker v11.158</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 npos=html.index(key)+len(key)
 notes,count=json.JSONDecoder().raw_decode(html[npos:])
 notes.update(title='Stable multiplayer sheep ownership through capture and rescue',
 date='2026-10-27',changes=[
  'Captured guest sheep keep their original reserved LAN player seat; another sheep or a wolf is never silently taken over after death.',
  'Captured LAN players remain wisps awaiting rescue; on rescue their original sheep becomes playable again.',
  'Live unassigned peers may still receive an available sheep or wolf when first joining, without stealing another player animal.',
  'Guest movement is disabled while their own sheep is captured, but the shared host world continues updating.',
  'A small owned-character status API and captured/wisp label help field acceptance.',
  'Preserve confirmed v11.156 guest smoothing, v11.157 building replication and minimal HF package/upload workflow.'
 ])
 html=html[:npos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[npos+count:]
 return html
