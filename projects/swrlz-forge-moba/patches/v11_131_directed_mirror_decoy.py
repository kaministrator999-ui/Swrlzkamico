"""§E v11.131: drag-to-direct a short-lived moving decoy, with HUD counter."""
from pathlib import Path
import hashlib,json

def once(html,old,new):
 n=html.count(old)
 assert n==1,(old[:130],n)
 return html.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/sheep_directed_mirror_decoy_v11_131.css').read_text(encoding='utf8')
 js=(root/'runtime/sheep_directed_mirror_decoy_v11_131.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se131-directed-mirror">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_130_SECOND_TOUCH_BROWSER_ZOOM_AND_SHEEP_BUILD_SEED',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_131_DIRECTED_SHORT_MIRROR_DECOY_COOLDOWN')
 for old,new in [
  ('ENGINE · MAKER v11.130','ENGINE · MAKER v11.131'),
  ('v11.130 · mobile page zoom and sheep placement','v11.131 · directed mirror and mobile controls'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.130'","window.SWRLZ_FORGE_BUILD={version:'v11.131'"),
  ('<title>§wyrl§ Engine · Maker v11.130</title>',
   '<title>§wyrl§ Engine · Maker v11.131</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Directed moving Mirror decoy with skill cooldown number, plus mobile starter/house tap fixes',
  date='2026-10-26',changes=[
  'Mirror (Illusive Split) now shows a live numeric countdown overlay directly on the skill icon, in addition to the existing textual cooldown.',
  'Drag the Mirror ability icon toward any screen direction and release: the fake sheep darts off in that direction using native safe navigation and a boosted decoy running speed. Simple tap also casts, using the current movement heading where possible.',
  'The real sheep preserves its current order and is not moved, redirected, or stopped by the Mirror cast; the ability can be activated while a second finger holds the joystick.',
  'The illusion expires after at most four seconds (or shorter authored lifetime), gently fading in the final 0.7 seconds, using only the decoy cloned materials; wolf contact can still dissolve it sooner.',
  'Normal recharge remains from actual rule cooldown (12 seconds in the updated starter), with no charge consumed when no legal escape route is found. Native role/ability validity and same actor asset are retained.',
  'The previously sealed v11.130 second-touchstart browser page-zoom prevention and skill-button sheep-centered house seeding are included along with every older feature and 68 bundled assets.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 raw=html.encode('utf8')
 print('SE_V11131_BUILD_MEASURE',len(raw),hashlib.sha256(raw).hexdigest(),flush=True)
 return html
