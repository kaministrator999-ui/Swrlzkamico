"""§E v11.377 — reference-image 2D contour-first workflow in integrated §C."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_377_REFERENCE_OUTLINES'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.377 source anchor',label,count,old[:110]))
    return html.replace(old,new,1)

def apply(html):
    helper=(ROOT/'runtime/model_image_outlines_v11_377.js').read_text('utf8')
    for token in ('SE377_IMAGE_PART_OUTLINES_START','function se377Analyze()',
                  'function se377TraceView(','function se377Outline(',
                  'function se377PointerDown(','function se377Export()',
                  "se375Load=async function(file)"):
        if token not in helper:raise AssertionError(('missing 2D trace workflow',token))
    # Runs inside integrated §C host closure, after the v11.375 tool and before
    # the existing account Save/Clone code; no new iframe/channel/credential link.
    html=once(html,'const se371CloudLinks=new Map();',
              helper+'\nconst se371CloudLinks=new Map();','trace inside existing §C panel')
    for old,new,label in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_376_VR_SELECTOR_LASSO',MARKER,'release marker'),
      ('ENGINE · MAKER v11.376','ENGINE · MAKER v11.377','header'),
      ('v11.376 · VR selector and area lasso','v11.377 · reference image 2D outlines','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.376'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.377'",'build version'),
      ('<title>§wyrl§ Engine · Maker v11.376</title>',
       '<title>§wyrl§ Engine · Maker v11.377</title>','browser title')
    ):
        html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.376';source.version=11.376;"
    count=html.count(old)
    if count!=5:raise AssertionError(('v11.377 provenance count',count))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.377';source.version=11.377;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.376' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.376','changes':notes.get('changes',[])})
    notes.update(version='v11.377',date='2026-11-10',
       title='Reference image → editable 2D part outlines first',
       changes=[
        'The existing §C image importer now drafts 2D outer silhouettes and color-connected regions for the five reference views before any 3D geometry is generated.',
        'Select a view and region, rename it, show or hide the contour, and tap to move, add or remove outline points on phone, desktop or Quest browser.',
        'Re-trace after adjusting five-view guides; export visible outlines as scalable SVG vector paths. Original image pixels remain in browser memory.',
        'This first pass is local color-based segmentation, NOT semantic AI identification of individual body parts; outlines require user review.',
        'The old five-view rough 3D loft builder remains available only under a clearly labeled experimental disclosure; it is not run on image import.',
        'Existing Model Studio workspace, §C image transport, VR selection, Undo, account save/clone and canonical starter protections are unchanged.'
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
