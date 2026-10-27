"""§E v11.145 · immersive runtime, safe Rapid snap, stable ghost."""
from pathlib import Path
import json,hashlib
def once(s,a,b):
 assert s.count(a)==1,(a[:180],s.count(a))
 return s.replace(a,b,1)
def apply(html):
 root=Path(__file__).resolve().parents[1]
 js=(root/'runtime/engine_play_scene_build_ghost_v11_145.js').read_text(encoding='utf8')
 css=(root/'runtime/engine_play_scene_build_ghost_v11_145.css').read_text(encoding='utf8')
 html=html.replace('</head>','<style id="se145-play-and-ghost">'+css+'</style>\n</head>',1)
 # Native v11.83 refresh must not recompute an actively dragged ghost from
 # stale raw pointer inputs while a newer validated aim owns its placement.
 html=once(html,
  'if(stUi.build&&stUi.placementPoint&&(args[0]||stSession.elapsed>=stDragPreviewAt)){',
  'if(stUi.build&&stUi.placementPoint&&stBuildInput.pointer===null&&(args[0]||stSession.elapsed>=stDragPreviewAt)){')
 html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_144_SHEEP_PORTRAIT_CAMERA',
 'SWYRL_ENGINE_DEPLOY_MARKER: V11_145_PLAY_GHOST_SAFE_SNAP')
 for a,b in [
  ('ENGINE · MAKER v11.144','ENGINE · MAKER v11.145'),
  ('v11.144 · one launch control and rotating sheep portraits','v11.145 · immersive Play and stable safe house ghost'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.144'","window.SWRLZ_FORGE_BUILD={version:'v11.145'"),
  ('<title>§wyrl§ Engine · Maker v11.144</title>','<title>§wyrl§ Engine · Maker v11.145</title>')
 ]:html=once(html,a,b)
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 obj,n=json.JSONDecoder().raw_decode(html[at:])
 obj.update(title='Immersive game playback and reliable sheep house placement',
  date='2026-10-27',changes=[
   'Playing the authored Main Menu or Gameplay hides editor toolbars, retaining the real 3D runtime and its game HUD. A small Exit to editor control returns through existing native Stop; editor controls return immediately.',
   'While dragging a house on Android, a transient invalid touch/HUD ray no longer destroys the preview. The hologram stays visible RED at its last location, remains unplaceable, and turns green only after a new valid native check. Routine HUD refresh cannot fight the active pointer.',
   'Rapid Build now searches more nearby flush-corner and straight-row house alignments when a blocked narrow passage is the ONLY rejection, and accepts an alternate solely when the existing complete stCanBuild independently confirms it. Keep true occupied, boundary, funding and unreachable sites blocked.',
   'All sheep passage safety, authored scenes, rapid screen memory, original build timing, 68 assets, and existing 3D camera logic remain unchanged.'
  ])
 html=html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
 b=html.encode('utf8')
 print('SE_V11145_BUILD_MEASURE',len(b),hashlib.sha256(b).hexdigest(),flush=True)
 return html
