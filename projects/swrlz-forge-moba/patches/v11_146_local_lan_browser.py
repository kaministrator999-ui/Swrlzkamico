"""§E v11.146: LAN browser UI, local bridge detection, honest capabilities."""
from pathlib import Path
import json,hashlib
def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_local_lan_browser_v11_146.js').read_text(encoding='utf8')
 css=(root/'runtime/sheep_local_lan_browser_v11_146.css').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se146-lan-browser">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_145_PLAY_GHOST_SAFE_SNAP','SWYRL_ENGINE_DEPLOY_MARKER: V11_146_LOCAL_LAN_BROWSER')
 for a,b in [
  ('ENGINE · MAKER v11.145','ENGINE · MAKER v11.146'),
  ('v11.145 · immersive Play and stable safe house ghost','v11.146 · local LAN directory and host menu'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.145'","window.SWRLZ_FORGE_BUILD={version:'v11.146'"),
  ('<title>§wyrl§ Engine · Maker v11.145</title>','<title>§wyrl§ Engine · Maker v11.146</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Sheep Tag local network game directory',
  date='2026-10-27',changes=[
   'Main Menu Play now includes Local LAN, which opens a dedicated browser with Host Game above the real local game list, Refresh and Back.',
   'HTTPS browsers cannot enumerate private IPs or serve LAN sockets; the hosted Space provides an explicit unavailable state, never fake sessions or hidden IP requests.',
   'The optional local LAN Bridge uses Python standard library, UDP discovery with bounded /24 IP probes, and same-origin HTTP to host and discover real Sheep Tag lobbies. LAN play must open through its local HTTP address.',
   'Joining a lobby establishes only lobby presence, not synchronized Sheep Tag matches. Real multiplayer game-state replication remains a separate task.',
   'Original editable levels, native Start Game, main menu camera, 177 historical patches and 68 packaged game assets are preserved.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11146_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
