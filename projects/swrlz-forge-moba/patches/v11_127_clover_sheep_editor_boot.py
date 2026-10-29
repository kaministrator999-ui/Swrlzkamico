"""§E v11.127: real organic Clover Sheep Tag model, playful walk swurvs,
and editor boot visibility only after workspace/UI stabilization."""
from pathlib import Path
import json,hashlib

def once(s,old,new):
 assert s.count(old)==1,(old[:100],s.count(old))
 return s.replace(old,new,1)

def apply(html):
 root=Path(__file__).resolve().parents[1]
 css=(root/'runtime/engine_editor_boot_gate_v11_127.css').read_text(encoding='utf8')
 organic=(root/'runtime/sheep_clover_organic_walk_swurv_v11_127.js').read_text(encoding='utf8')
 boot=(root/'runtime/engine_editor_boot_gate_v11_127.js').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se127-editor-boot">'+css+'</style>\n</head>',1)
 html=once(html,'window.SWRLZ_FORGE_BUILD=',organic+'\n'+boot+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_126_SHEEP_CENTERED_BUILD_PERMANENT_ROUTES_READY_SKILLS',
  'SWYRL_ENGINE_DEPLOY_MARKER: V11_127_CLOVER_SHEEP_SWURV_AND_STABLE_EDITOR_BOOT')
 for a,b in [
  ('ENGINE · MAKER v11.126','ENGINE · MAKER v11.127'),
  ('v11.126 · sheep-centered build and permanent routes','v11.127 · organic sheep and steady editor boot'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.126'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.127'"),
  ('<title>§wyrl§ Engine · Maker v11.126</title>',
   '<title>§wyrl§ Engine · Maker v11.127</title>')
 ]:html=once(html,a,b)
 tag='const SE_RELEASE_NOTES='
 at=html.index(tag)+len(tag)
 notes,n=json.JSONDecoder().raw_decode(html[at:])
 notes.update(title='Organic Clover Sheep Tag sheep and flicker-free final editor startup',
  date='2026-10-26',changes=[
   'Sheep Tag now uses the same native Model Atelier Clover organic starter sheep shape: fleece, muzzle, ears, cloven hooves and sculpted face, sampled once at mobile gameplay density and shared between animals, not the older low-poly body.',
   'Distance-driven native four-leg walk remains; individual sheep occasionally perform a small, playful visual-only pounce/swurv, with varied timing, soft body hop, ear/head tilt and immediate return to normal walk. Movement, collisions, map routes and build commands are unchanged.',
   'The original authored Sheep Tag actors and saving are preserved. If the organic model cannot be created, the existing sheep model stays usable.',
   'Editor startup covers the temporary legacy/default shell with a simple loading state until the final restored project/toolbars settle; includes a bounded fallback and honors reduced-motion preference.',
   'Previous v11.126 permanent routes, sheep-centered building, faster abilities and all preceding engine and editor work remain unchanged.'
  ])
 html=html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11127_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
