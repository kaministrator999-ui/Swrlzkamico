"""§E v11.157: one canonical, host-authoritative multiplayer building mirror."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:120],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_authoritative_build_sync_v11_157.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_156_SMOOTH_BUILD_TEAM_FOG',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_157_AUTHORITATIVE_BUILD_REPLICA')
 for old,new in [
  ('ENGINE · MAKER v11.156','ENGINE · MAKER v11.157'),
  ('v11.156 · smooth guests, shared structures and team fog',
   'v11.157 · reliable host-to-guest building replication'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.156'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.157'"),
  ('<title>§wyrl§ Engine · Maker v11.156</title>',
   '<title>§wyrl§ Engine · Maker v11.157</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 i=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[i:])
 notes.update(title='One authoritative multiplayer structure reconciler',
 date='2026-10-27',changes=[
  'Stop overlapping old and new guest structure creation/removal passes; apply each host world snapshot once and reconcile every real host building by ID.',
  'Host houses, walls, ramps and other configured structures are created, updated and destroyed once per authoritative ID, keeping their correct owner and construction progress.',
  'Local authored prefabs can be reused by nearby position and kind without duplicating actors; house rotation and terrain fog remain consistent.',
  'Visible LAN debug now shows the guest mirrored house count versus the host snapshot house count, plus actual guest build requests and host confirmations.',
  'Keep the improved v11.156 smooth sheep movement, team sheep+house fog and single host simulation unchanged.',
  'Focused JS replica-lifecycle test covered host creation, repeated update without duplicates and removal; two-device acceptance pending.',
  'GitHub Actions remains package and upload only to the existing Hugging Face Space.'
 ])
 html=html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
 return html
