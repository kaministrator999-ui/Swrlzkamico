"""§E v11.152 — authoritative host world, guest replicated Sheep Tag gameplay."""
from pathlib import Path
import json,hashlib
def once(s,a,b):
 assert s.count(a)==1,(a[:110],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_shared_host_world_v11_152.js').read_text(encoding='utf-8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_151_ONE_CODE_AUTOMATIC_JOIN',
                 'SWYRL_ENGINE_DEPLOY_MARKER: V11_152_HOST_AUTHORITATIVE_WORLD')
 for a,b in [
 ('ENGINE · MAKER v11.151','ENGINE · MAKER v11.152'),
 ('v11.151 · automatic one-code LAN guest join','v11.152 · host-authoritative shared Sheep Tag world'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.151'","window.SWRLZ_FORGE_BUILD={version:'v11.152'"),
 ('<title>§wyrl§ Engine · Maker v11.151</title>','<title>§wyrl§ Engine · Maker v11.152</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Host-authoritative LAN Sheep Tag world',
 date='2026-10-27',changes=[
  'The host now owns the one native gameplay simulation; guest Sheep Tag worlds are visual replicas of host snapshots.',
  'Real connected guests receive distinct sheep/wolf units, can issue move/build/attack orders and use touchscreen movement, all validated by host.',
  'The host broadcasts units, captured wisps, buildings, gold, health, construction progress, match timer and winner state over existing WebRTC data channels.',
  'Guest-side AI, economy and gameplay simulation are disabled while synchronized; existing native renderer/HUD and input controls are retained.',
  'No public match server or extra game loop. Network partitions and unsupported third-party PeerJS signaling may interrupt play.',
  'This version has not yet been accepted on two physical devices. The optional Python LAN Bridge protocol remains separate.'
 ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 print('SE152_BUILD',len(html.encode()),hashlib.sha256(html.encode()).hexdigest(),flush=True)
 return html
