"""§E v11.149: editor Main Menu parity + browser-local peer hosting without fake discovery."""
from pathlib import Path
import hashlib,json
def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_peer_menu_v11_149.js').read_text(encoding='utf8')
 css=(root/'runtime/sheep_peer_menu_v11_149.css').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se149-peer-menu">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_148_LAN_WAITING_ROOM',
                  'SWYRL_ENGINE_DEPLOY_MARKER: V11_149_PEER_MENU_PARITY')
 for a,b in [
 ('ENGINE · MAKER v11.148','ENGINE · MAKER v11.149'),
 ('v11.148 · host-controlled LAN waiting lobby','v11.149 · playable editor preview and invite-only browser LAN host'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.148'","window.SWRLZ_FORGE_BUILD={version:'v11.149'"),
 ('<title>§wyrl§ Engine · Maker v11.148</title>','<title>§wyrl§ Engine · Maker v11.149</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[pos:])
 obj.update(title='Editor Main Menu parity and direct-peer hosting',
  date='2026-10-27',changes=[
  'Edit mode shows the same Main Menu launch controls as Play, including Local LAN, without running the cinematic or enabling preview input.',
  'Public HTTPS Host Game now creates a genuine browser-local eight-slot waiting room with manual WebRTC guest invites and replies on local Wi-Fi.',
  'Live guest names and seats appear only on direct peer connection; no fabricated network sessions or private IP scanning.',
  'Existing local Python bridge hosting/auto-discovery still works on a trusted Wi-Fi server.',
  'WebRTC local peer signaling is exchanged manually, with no public signaling server or relay. Peer establishment depends on local browser/network support.',
  'Start Match stays disabled because synchronized Sheep Tag physics/match gameplay has not been implemented.'
  ])
 html=html[:pos]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
 raw=html.encode('utf8')
 print('SE149_SOURCE_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
