"""§E v11.452: three-stage contextual Face menu using original native controls.

v11.451's guided controls already own native preview sliders and Apply/Cancel;
this patch relocates those exact DOM nodes rather than creating another
workshop or changing mesh geometry, Save/Load, camera, VR, or Undo.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_452_NATIVE_FACE_FLYOUTS'
def one(s,old,new):
 n=s.count(old)
 if n!=1:raise AssertionError(('v11.452 anchor drift',old[:145],n))
 return s.replace(old,new,1)

def apply(html):
 js=(ROOT/'runtime/model_face_flyouts_v11_452.js').read_text(encoding='utf8')
 css=(ROOT/'runtime/model_face_flyouts_v11_452.css').read_text(encoding='utf8')
 assert js.startswith('/* SE452_NATIVE_FACE_FLYOUTS_START */')
 assert js.rstrip().endswith('/* SE452_NATIVE_FACE_FLYOUTS_END */')
 assert css.startswith('/* SE452_NATIVE_FACE_FLYOUTS_CSS_START */')
 assert css.rstrip().endswith('/* SE452_NATIVE_FACE_FLYOUTS_CSS_END */')
 assert '/* SE451_GUIDED_FACE_WORKFLOW_END */' in html
 # Historical marker stays visible to v11.451 behavior-regression tests,
 # while one release marker remains authoritative.
 html=one(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_451_GUIDED_FACE_WORKFLOW',MARKER)
 html=one(html,'/* SE451_GUIDED_FACE_WORKFLOW_END */',
  '/* SE451_GUIDED_FACE_WORKFLOW_END */\n'+
  '/* Historical v11.451 source: SWYRL_ENGINE_DEPLOY_MARKER: V11_451_GUIDED_FACE_WORKFLOW */\n'+js)
 html=html.replace('</head>','<style id="se452FaceFlyoutStyles">\n'+css+'\n</style>\n</head>',1)
 for before,after in [
  ('ENGINE · MAKER v11.451','ENGINE · MAKER v11.452'),
  ('v11.451 · guided face tools and live modifiers','v11.452 · three-stage contextual Face flyouts'),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.451'","window.SWRLZ_FORGE_BUILD={version:'v11.452'"),
  ('<title>§wyrl§ Engine · Maker v11.451</title>','<title>§wyrl§ Engine · Maker v11.452</title>')
 ]:html=one(html,before,after)
 prior=" source.engine='§wyrl§ Engine · Maker v11.451';source.version=11.451;"
 assert html.count(prior)==5,('v11.452 provenance',html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.452';source.version=11.452;")
 key='const SE_RELEASE_NOTES=';i=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[i:])
 notes['history']=[entry for entry in notes.get('history',[]) if entry.get('version')!='v11.451']
 notes['history'].insert(0,{'version':'v11.451','changes':notes.get('changes',[])})
 notes.update(version='v11.452',date='2026-11-14',
  title='Three-stage Face → Inset/Extrude → native modifiers with preserved mobile viewport',
  changes=[
   'The existing far-right modeling rail remains the only primary tool list. Opening Face moves the original Shape/Face quick controls into a second sliding operations drawer, and choosing Inset or Extrude moves the existing v11.451 guided controls into a third modifier drawer.',
   'Original Inset/Extrude native buttons retain the real connected-square-face selection, editable-primitive safeguards, transient geometry preview, slider and exact amount, Apply/Cancel, and Undo. No duplicate workshop, source/mesh mutation or extra history transaction is created by menus.',
   'The full inspector hides only during the Face flyout, freeing viewport width. Advanced tools restores the native inspector and its original controls; closing a menu cannot discard a pending preview.',
   'On compact or narrow browser desktop-site layouts, operations and modifiers become successive accessible panels rather than covering the viewport simultaneously. Full-screen and headset VR operation ownership remains unchanged.',
   'Layout changes remain CSS-only and never synthesize a browser resize, model reframe, or camera pose change. The original native history, gizmos, pinch, orbit, selection, project save and VR controllers remain untouched.'
  ])
 return html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[i+width:]
