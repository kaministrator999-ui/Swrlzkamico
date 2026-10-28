"""§E v11.163: visible guest construction growth from host-owned progress."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_authoritative_growth_v11_163.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_162_RELIABLE_GUEST_HOUSE_ORDERS',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_163_GUEST_BUILDING_GROWTH')
 for a,b in [
  ('ENGINE · MAKER v11.162','ENGINE · MAKER v11.163'),
  ('v11.162 · reliable guest house construction',
   'v11.163 · host-synchronized growing guest houses'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.162'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.163'"),
  ('<title>§wyrl§ Engine · Maker v11.162</title>',
   '<title>§wyrl§ Engine · Maker v11.163</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 i=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[i:])
 notes.update(title='Authoritative guest house growth and rejected-site recovery',
 date='2026-10-28',changes=[
  'A screenshot showed guest house replicas existing but one stuck at flat roof/foundation height after repeated placement attempts.',
  'Guest snapshots now drive one final construction mesh-scale renderer using the real host progress for each host-owned house ID.',
  'Interpolate growth between host updates on the already-running guest requestAnimationFrame loop, with bounded prediction; never fake a completed building if host progress stalls.',
  'When host reports 100% complete, the guest immediately restores full original model height and keeps the mesh parent/visibility consistent.',
  'Show host-percent versus displayed-percent construction diagnostics in LAN status and SWYRL_ENGINE_LAN.constructionProgress().',
  'Rejected guest building sites restore House placement mode, displaying the host rejection reason instead of silently requiring a fresh skill selection.',
  'Prior v11.161 smooth continuous sheep motion, live-game browser, guest order protocol, wolf countdown and team fog remain unchanged.',
  'Focused JS test covered 0→35→100% host construction progress, interpolated height changes and rejected-site recovery. Physical two-device acceptance pending.',
  'Only the existing minimal GitHub Actions package and Hugging Face upload workflow is used.'
 ])
 html=html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
 return html
