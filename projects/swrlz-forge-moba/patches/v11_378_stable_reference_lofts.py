"""§E v11.378 — edit-approved 2D outlines → stable opt-in 3D blockout."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_378_STABLE_3D_BLOCKOUT'

def once(html,a,b,label):
 n=html.count(a)
 if n!=1:raise AssertionError(('v11.378 source anchor',label,n,a[:120]))
 return html.replace(a,b,1)

def apply(html):
 helper=(ROOT/'runtime/model_image_stable_lofts_v11_378.js').read_text('utf8')
 for token in ('SE378_STABLE_LOFT_START','function se378Blockout()',
               'function se378Rows(','function se378Span(','se375Blockout=se378Blockout;'):
  if token not in helper:raise AssertionError(('missing stable loft source',token))
 html=once(html,'const se371CloudLinks=new Map();',helper+'\nconst se371CloudLinks=new Map();','reuse existing §C image host')
 for a,b,label in [
 ('SWYRL_ENGINE_DEPLOY_MARKER: V11_377_REFERENCE_OUTLINES',MARKER,'deploy marker'),
 ('ENGINE · MAKER v11.377','ENGINE · MAKER v11.378','header'),
 ('v11.377 · reference image 2D outlines','v11.378 · stable editable 3D blockout','headline'),
 ("window.SWRLZ_FORGE_BUILD={version:'v11.377'","window.SWRLZ_FORGE_BUILD={version:'v11.378'",'build identity'),
 ('<title>§wyrl§ Engine · Maker v11.377</title>','<title>§wyrl§ Engine · Maker v11.378</title>','html title')
 ]:html=once(html,a,b,label)
 old=" source.engine='§wyrl§ Engine · Maker v11.377';source.version=11.377;"
 if html.count(old)!=5:raise AssertionError(('v11.378 provenance count',html.count(old)))
 html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.378';source.version=11.378;")
 key='const SE_RELEASE_NOTES='
 at=html.index(key)+len(key)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 if not any(x.get('version')=='v11.377' for x in notes.get('history',[])):
  notes.setdefault('history',[]).insert(0,{'version':'v11.377','changes':notes.get('changes',[])})
 notes.update(version='v11.378',date='2026-11-10',
  title='Experimental 3D blockout from corrected 2D silhouettes',
  changes=[
   'Both reference experiments remain available in the original integrated §C image panel. 2D tracing is still the automatic default.',
   'The optional improved 3D builder now reads the user-edited 2D front silhouette, rather than combining unrelated full-width pixel rows and incompatible side-view horizontal centers.',
   'Front contour supplies three independently editable upper, middle and lower loft profiles; side-view silhouettes supply a bounded depth estimate while retaining a stable forward axis.',
   'Neighbor smoothing, capped center shift and separated band seams reduce the twisted rose-tornado geometry and preserve silhouette proportions; the optional detached prop scanner stays available.',
   'This is still an approximate 3D blockout, not exact anatomical recognition, texture baking, automatic UV mapping or a completed multi-view photogrammetry solution.',
   'The previous Blank Model only, project clone, native mesh validation, Undo, local Save, §C transport, 2D SVG export and VR selection remain unchanged.'
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
