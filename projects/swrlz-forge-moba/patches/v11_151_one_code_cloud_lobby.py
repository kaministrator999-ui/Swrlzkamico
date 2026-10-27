"""§E v11.151: one-code guest admission via cloud-mediated PeerJS signaling."""
from pathlib import Path
import json,hashlib
def once(s,a,b):
 assert s.count(a)==1,(a[:120],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_one_code_cloud_lobby_v11_151.js').read_text(encoding='utf-8')
 css=(root/'runtime/sheep_one_code_cloud_lobby_v11_151.css').read_text(encoding='utf-8')
 html=once(html,'</head>','<style id="se151-one-code-lobby">'+css+'</style>\n</head>')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_150_HOST_START_NATIVE_MATCH',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_151_ONE_CODE_AUTOMATIC_JOIN')
 for a,b in [
 ('ENGINE · MAKER v11.150','ENGINE · MAKER v11.151'),
 ('v11.150 · host starts peer-connected Sheep Tag game','v11.151 · automatic one-code LAN guest join'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.150'","window.SWRLZ_FORGE_BUILD={version:'v11.151'"),
 ('<title>§wyrl§ Engine · Maker v11.150</title>','<title>§wyrl§ Engine · Maker v11.151</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 data,n=json.JSONDecoder().raw_decode(html[pos:])
 data.update(title='One-code Sheep Tag LAN guest joining',date='2026-10-27',changes=[
  'Host Game registers a short invitation on PeerJS Cloud (0.peerjs.com).',
  'Guest pastes the invitation once, without copying an answer back to host.',
  'PeerJS Cloud handles WebRTC offer-answer signaling automatically; gameplay data is peer-to-peer if connectivity succeeds.',
  'Real connected guests occupy slots and enable the host Start Match control.',
  'This uses a third-party internet signaling provider; unavailable on isolated Wi-Fi or blocked networks. No TURN relay is included.',
  'Game positions, buildings and combat are not yet synchronized; Start Match coordinates entering native Gameplay.',
  'Original editable scenes and historical assets preserved.'
 ])
 html=html[:pos]+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
 print('SE151_BUILT_BYTES_SHA256',len(html.encode()),hashlib.sha256(html.encode()).hexdigest(),flush=True)
 return html
