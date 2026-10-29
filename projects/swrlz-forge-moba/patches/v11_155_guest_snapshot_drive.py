"""§E v11.155: move guest-owned sheep on the live host world tick."""
from pathlib import Path
import json
def once(s,old,new):
 assert s.count(old)==1,(old[:100],s.count(old))
 return s.replace(old,new,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/sheep_guest_snapshot_drive_v11_155.js').read_text(encoding='utf8')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_154_GUEST_INPUT_ACK',
                'SWYRL_ENGINE_DEPLOY_MARKER: V11_155_SNAPSHOT_DRIVEN_GUEST')
 for a,b in [
  ('ENGINE · MAKER v11.154','ENGINE · MAKER v11.155'),
  ('v11.154 · host-acknowledged guest Sheep Tag controls',
   'v11.155 · snapshot-driven guest sheep movement'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.154'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.155'"),
  ('<title>§wyrl§ Engine · Maker v11.154</title>',
   '<title>§wyrl§ Engine · Maker v11.155</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 pos=html.index(key)+len(key)
 data,n=json.JSONDecoder().raw_decode(html[pos:])
 data.update(title='Guest movement applied on host authoritative world ticks',
 date='2026-10-27',changes=[
  'Two-phone field telemetry showed the host acknowledged joystick input yet applied zero movement frames.',
  'Host guest movement now executes on the existing 130ms world snapshot clock, which field tests confirm is active.',
  'Guest sheep movement uses validated host-owned seat and collision geometry and is replicated in the same snapshot.',
  'The legacy per-frame guest-input movement path is bypassed to avoid double motion.',
  'Host shows applied moves, blocked counts, snapshot ticks and rejection reason for physical diagnosis.',
  'No new tick, gameplay server or GitHub verification jobs; deployment remains package and upload only.'
 ])
 html=html[:pos]+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
 return html
