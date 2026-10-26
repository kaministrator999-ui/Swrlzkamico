"""§E v11.134: immediate Rapid-OFF cancellation, deterministic sheep-centered
house preview, visible ability slots and Free/Income position swap."""
from pathlib import Path
import json,hashlib

def once(s,old,new):
 n=s.count(old)
 assert n==1,(old[:160],n)
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/sheep_rapid_cancel_seed_skills_swap_v11_134.css').read_text(encoding='utf8')
 js=(root/'runtime/sheep_rapid_cancel_seed_skills_swap_v11_134.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se134-build-skill-layout">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_133_TOUCHABLE_RAPID_AND_PERSISTENT_SHEEP_GHOST',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_134_RAPID_CANCEL_SHEEP_MARKER_VISIBLE_SKILLS_HOUSE_SWAP')
 for old,new in [
  ('ENGINE · MAKER v11.133','ENGINE · MAKER v11.134'),
  ('v11.133 · tappable rapid and sheep house preview','v11.134 · rapid cancel and reliable build HUD'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.133'","window.SWRLZ_FORGE_BUILD={version:'v11.134'"),
  ('<title>§wyrl§ Engine · Maker v11.133</title>',
   '<title>§wyrl§ Engine · Maker v11.134</title>')
 ]:html=once(html,old,new)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Rapid OFF immediately cancels the building ghost, sheep-centered marker, visible abilities, swapped Free/Income positions',
 date='2026-10-26',changes=[
  'Switching Rapid Build from ON to OFF with an unplaced hologram immediately clears the active building tool, ghost mesh, placement point and pending touch gesture. Previously completed houses and valid existing orders remain untouched. Switching Rapid ON still does not place a building.',
  'Selecting a house/ramp/walkway immediately seeds and shows the live building ghost at the ACTUAL controlled sheep position, not merely at a potentially shifted grid-fit location. Works from touch, click, and keyboard. Subsequent meadow drag continues using native snap, green/red collision feedback and release-to-build checks.',
  'The mobile HUD always shows BOTH Mirror and Totem sheep ability slots; if a custom Sheep Tag rule disables one, its icon remains visible but disabled with explanatory accessible text. Explicit custom game rules, cooldowns and prerequisites are not overridden.',
  'The bottom-right mobile building circle is now Income House; Free House moves into the former Income House slot. These are spatial UI changes only: original free/costly structures, icons, IDs, shortcuts, permissions and native click handlers remain unchanged.',
  'Retains v11.133 Android pointer/click gesture fixes, v11.132 rapid building and wireframe routes, Mirror decoy, anti-page-zoom guard and all 68 assets.'
 ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11134_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
