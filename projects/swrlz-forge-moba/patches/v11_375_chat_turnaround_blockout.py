"""§E v11.375 — integrated §C reference-sheet image-to-editable blockout.

New client-only image-guided silhouette tool, no additional model backend,
no hidden source upload, no overwrite of canonical starter projects.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_375_CHAT_TURNAROUND_BLOCKOUT'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.375 source anchor',label,count,old[:115]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/model_image_blockout_v11_375.js').read_text('utf8')
    for token in ('function se375Blockout()', 'function se375Run()', 'function se375Install()',
                  'ModelAtelier.chatAction(op)', 'se371Clone(', 'canvas.getContext'):
        if token not in js:raise AssertionError(('missing image blockout implementation',token))
    # All helper functions live within the existing credential-isolated
    # integrated §C host closure. No iframe credential/bytes crossing.
    html=once(html,'if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(mount);',
              js+'\nif(ALLOWED_PARENTS.has(location.origin))queueMicrotask(mount);',
              'integrated Chat-host blockout helpers')
    html=once(html,'panel.append(frame);document.body.append(toggle,panel);',
              'panel.append(frame);document.body.append(toggle,panel);se375Install();',
              'one collapsible image flow alongside existing chat controls')
    for old,new,label in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_374_QUEST_VR_FEEDBACK',MARKER,'release marker'),
      ('ENGINE · MAKER v11.374','ENGINE · MAKER v11.375','header'),
      ('v11.374 · VR gesture, selection and project menu usability',
       'v11.375 · image-guided editable 3D blockout','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.374'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.375'",'build version'),
      ('<title>§wyrl§ Engine · Maker v11.374</title>',
       '<title>§wyrl§ Engine · Maker v11.375</title>','browser title')
    ):
        html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.374';source.version=11.374;"
    count=html.count(old)
    if count not in (3,5,6):raise AssertionError(('v11.375 provenance count',count))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.375';source.version=11.375;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.374' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.374','changes':notes.get('changes',[])})
    notes.update(version='v11.375',date='2026-11-10',
      title='Integrated Chat five-view image to editable model blockout',
      changes=[
       'The §C panel now offers a collapsible Image → editable 3D blockout workflow while a blank Model Studio project is active.',
       'Upload a five-view turnaround (front, left, right, back, top). Preview/adjust guides and generate separate editable native loft silhouettes in the existing viewport.',
       'Images are sampled only in the browser; no picture pixels go to the model server or account store through this tool. Generated geometry uses the existing mesh/Undo/Save machinery.',
       'The canonical blank starter is protected: the flow creates an independent project first, and rejects nonblank projects instead of overwriting their parts.',
       'This first experiment is a 3D shape blockout, not a photogrammetry scan, rig, automatic UV texture mapping, or guarantee of anatomical reconstruction.',
       'Existing VR selection/manipulation, cloud revision protection, studio chrome, Chat transport and model route behavior are retained.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
