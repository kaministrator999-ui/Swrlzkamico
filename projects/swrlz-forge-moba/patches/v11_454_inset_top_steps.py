"""§E v11.454: compact two-stage Inset rim and inward depth at viewport top.

No new topology owner: v11.430 native preview/Apply/Cancel and v11.453
coplanar border remain authoritative, with one Undo checkpoint per Set.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_454_INSET_TOP_STEPS'
def once(s,a,b):
 n=s.count(a)
 if n!=1:raise AssertionError(('v11.454 anchor',a[:170],n))
 return s.replace(a,b,1)

def apply(html):
 js=(ROOT/'runtime/model_inset_top_steps_v11_454.js').read_text('utf8')
 css=(ROOT/'runtime/model_inset_top_steps_v11_454.css').read_text('utf8')
 assert js.startswith('/* SE454_INSET_TOP_STEPS_START */')
 assert js.rstrip().endswith('/* SE454_INSET_TOP_STEPS_END */')
 assert css.startswith('/* SE454_INSET_TOP_STEPS_STYLES_START */')
 html=once(html,'SWYRL_ENGINE_DEPLOY_MARKER: V11_453_INSET_RIM_WIDTH',MARKER)
 html=once(html,'/* SE453_INSET_RIM_WIDTH_END */',
 '/* SE453_INSET_RIM_WIDTH_END */\n'+
 '/* Historical v11.453 marker: SWYRL_ENGINE_DEPLOY_MARKER: V11_453_INSET_RIM_WIDTH */\n'+js)
 html=html.replace('</head>','<style id="se454InsetTopStepsStyles">\n'+css+'\n</style>\n</head>',1)
 for old,new in [
   ('ENGINE · MAKER v11.453','ENGINE · MAKER v11.454'),
   ('v11.453 · visible adjustable inset rim','v11.454 · top-bar rim then inward depth'),
   ("window.SWRLZ_FORGE_BUILD={version:'v11.453'","window.SWRLZ_FORGE_BUILD={version:'v11.454'"),
   ('<title>§wyrl§ Engine · Maker v11.453</title>','<title>§wyrl§ Engine · Maker v11.454</title>')
 ]:html=once(html,old,new)
 prior=" source.engine='§wyrl§ Engine · Maker v11.453';source.version=11.453;"
 assert html.count(prior)==5,('v11.454 provenance',html.count(prior))
 html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.454';source.version=11.454;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes['history']=[e for e in notes.get('history',[]) if e.get('version')!='v11.453']
 notes['history'].insert(0,{'version':'v11.453','changes':notes.get('changes',[])})
 notes.update(version='v11.454',date='2026-11-14',
 title='Guided Inset top slider: rim width, Set, inward depth, Set',
 changes=[
  'Choosing Inset opens one compact slider at the top of the actual modeling viewport. If no face is selected, it prompts for a square face; the previous native face-pick and safe conversion behavior remains intact.',
  'Stage 1 previews adjustable Inset rim width using the native source-safe preview. Set rim explicitly commits only that Inset and retains its inner cap selection, as one Undo checkpoint.',
  'Stage 2 immediately presents inward cavity depth on the same top slider, with bounded local depth and native collision validation. Changing the slider previews negative Extrude; Set depth explicitly commits a second Undo checkpoint.',
  'Set is disabled without a valid native preview; a failed depth attempt preserves the last valid candidate. Cancel in stage 1 discards Inset; Cancel in stage 2 keeps the already-applied rim. Undo steps remain individually reversible.',
  'The previous Face modifier drawer and gold diamond hide only during the guided flow to prevent duplicate controls; the native advanced inspector, v11.452 flyouts, viewport gestures, camera, and VR modeling remain available outside it.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
