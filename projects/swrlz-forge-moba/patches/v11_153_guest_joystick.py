"""§E v11.153 mobile WebRTC guest joystick controls assigned host animal."""
from pathlib import Path
import json
def once(s,a,b):
 assert s.count(a)==1,(a[:95],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_guest_joystick_v11_153.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_152_HOST_AUTHORITATIVE_WORLD',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_153_GUEST_JOYSTICK_CONTROL')
 for a,b in [
 ('ENGINE · MAKER v11.152','ENGINE · MAKER v11.153'),
 ('v11.152 · host-authoritative shared Sheep Tag world','v11.153 · guest controls their Sheep Tag character'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.152'","window.SWRLZ_FORGE_BUILD={version:'v11.153'"),
 ('<title>§wyrl§ Engine · Maker v11.152</title>','<title>§wyrl§ Engine · Maker v11.153</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 index=html.index(key)+len(key)
 notes,n=json.JSONDecoder().raw_decode(html[index:])
 notes.update(title='Guest Sheep Tag joystick authority fix',date='2026-10-27',
 changes=[
 'Guest mobile joystick sends pointer direction directly through its verified peer channel, without requiring local simulation.',
 'Host owns each guest animal and moves it in native game frames with obstacle checks; stale inputs stop automatically.',
 'Guest input transmission and host receive counters are available under SWYRL_ENGINE_LAN.guestInput() for physical debugging.',
 'The same host simulation continues to replicate actor/building/economy state to every connected browser.',
 'The dedicated HF workflow remains build and upload only; two-device movement acceptance is pending.'
 ])
 html=html[:index]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[index+n:]
 return html
