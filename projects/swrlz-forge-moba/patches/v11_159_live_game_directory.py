"""§E v11.159: live discovered hosted Sheep Tag games without fake LAN scans."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:110],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_live_lan_directory_v11_159.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_158_GUEST_LIVES_FIXED_SEAT',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_159_LIVE_GAME_DIRECTORY')
 for a,b in [
  ('ENGINE · MAKER v11.158','ENGINE · MAKER v11.159'),
  ('v11.158 · stable guest ownership after capture',
   'v11.159 · automatic live multiplayer game discovery'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.158'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.159'"),
  ('<title>§wyrl§ Engine · Maker v11.158</title>',
   '<title>§wyrl§ Engine · Maker v11.159</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 i=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[i:])
 notes.update(title='Automatic live Sheep Tag lobby search and join',
 date='2026-10-27',changes=[
  'Opening Local LAN on the public HTTPS Space now searches automatically for actual advertised waiting Sheep Tag games and shows live player counts with direct Join buttons.',
  'Hosted lobby presence is refreshed every 5.5 seconds, responds immediately to refresh/probe messages, and expires without a heartbeat after 18 seconds. Full and in-progress games are not offered as joinable.',
  'Live discovery is scoped to a short hash of the browsers shared public IPv4 internet exit, which often matches devices on the same Wi-Fi; it cannot verify actual same-LAN membership or discover clients using unrelated mobile connections.',
  'Room notices use a public third-party MQTT test broker (broker.emqx.io) with no credentials, and carry only public lobby ID, count and phase. Public broker is a prototype dependency, not private or production infrastructure.',
  'Clicking Join uses the existing real PeerJS guest connection; a listing does not falsely imply a successful joined seat.',
  'The native local HTTP LAN Bridge still handles true UDP/subnet discovery when served locally; hosted HTTPS cannot scan local private addresses.',
  'Manual guest-invite joining, one authoritative shared world, guest movement, buildings and capture ownership remain unchanged.',
  'GitHub Action continues doing only package and Hugging Face upload; no Chromium or remote verification workflow.'
 ])
 html=html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
 return html
