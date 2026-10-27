"""§E v11.154: host-acknowledged guest joystick and frame-authoritative control."""
from pathlib import Path
import json
def once(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)
def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/sheep_guest_input_ack_v11_154.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_153_GUEST_JOYSTICK_CONTROL',
                 'SWYRL_ENGINE_DEPLOY_MARKER: V11_154_GUEST_INPUT_ACK')
    for a,b in [
       ('ENGINE · MAKER v11.153','ENGINE · MAKER v11.154'),
       ('v11.153 · guest controls their Sheep Tag character','v11.154 · host-acknowledged guest Sheep Tag controls'),
       ("window.SWRLZ_FORGE_BUILD={version:'v11.153'","window.SWRLZ_FORGE_BUILD={version:'v11.154'"),
       ('<title>§wyrl§ Engine · Maker v11.153</title>',
        '<title>§wyrl§ Engine · Maker v11.154</title>')
    ]:html=once(html,a,b)
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Verified guest joystick input delivery and host authority',
        date='2026-10-27',changes=[
        'Guest sends explicit sequence-numbered joystick commands across its verified PeerJS/WebRTC connection.',
        'Host binds the real data connection to its registered guest seat, validates joystick packets and acknowledges actual receipt.',
        'Guest controls the assigned host-authoritative animal; the host moves it in game frames with bounds and obstacle checks.',
        'The on-screen input status now separates local TX attempts from host acknowledgements and successful movement frames.',
        'Host and guest still share a single game world. The user two-phone movement test remains the next acceptance step.',
        'HF deployment remains build+upload only, without Chromium or remote verification.'
        ])
    html=html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
    return html
