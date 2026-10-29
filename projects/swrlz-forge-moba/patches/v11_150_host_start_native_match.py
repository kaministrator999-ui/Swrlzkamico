"""§E v11.150 host controls synchronized start signal and native Gameplay transition."""
from pathlib import Path
import hashlib,json
def once(a,old,new):
 assert a.count(old)==1,(old[:90],a.count(old))
 return a.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_lan_match_start_v11_150.js').read_text(encoding='utf8')
 css=(root/'runtime/sheep_lan_match_start_v11_150.css').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se150-match-start">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_149_PEER_MENU_PARITY',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_150_HOST_START_NATIVE_MATCH')
 for old,new in [
 ('ENGINE · MAKER v11.149','ENGINE · MAKER v11.150'),
 ('v11.149 · playable editor preview and invite-only browser LAN host',
  'v11.150 · host starts peer-connected Sheep Tag game'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.149'",
  "window.SWRLZ_FORGE_BUILD={version:'v11.150'"),
 ('<title>§wyrl§ Engine · Maker v11.149</title>',
  '<title>§wyrl§ Engine · Maker v11.150</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[pos:])
 notes.update(title='Host starts Sheep Tag on connected LAN guests',
 date='2026-10-27',changes=[
  'A host with at least one verified WebRTC guest can start the native Gameplay level.',
  'Connected guests receive an authenticated direct-channel match-start command and transition to their own native Gameplay level.',
  'Peer channels persist after menu teardown and close on native Stop; host shutdown sends a match-end command.',
  'The start event is coordinated, but native sheep/wolf positions, houses, actions, and physics are NOT replicated yet. Match gameplay remains locally simulated on each device.',
  'The existing LAN Bridge host/join waiting rooms remain independent of the browser peer start protocol.',
  'Preserve editor levels, all prior Sheep Tag gameplay logic and 68 packaged assets.'
 ])
 html=html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
 raw=html.encode('utf8')
 print('SE150_EXACT_SOURCE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
