"""§E v11.371 — native Save / Clone Project and immutable template protection."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_371_SAFE_SAVE_CLONE_PROJECTS'

def once(html,old,new,label):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.371 anchor',label,n,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/project_safe_save_v11_371.js').read_text('utf8')
    css=(ROOT/'runtime/project_safe_save_v11_371.css').read_text('utf8')
    for token in ('async function se371Clone(name)', 'async function se371SaveLocal()',
                  'const se371PreviousSaveCloud=saveCloud;', 'window.SWYRL_ENGINE_SAFE_PROJECTS_371'):
        if token not in js:raise AssertionError(('missing native project runtime',token))
    for token in ('function se175Snapshot()', 'function se175StampProject(',
                  'async function saveCloud()', 'async function loadCloud('):
        if token not in html:raise AssertionError(('missing native project prerequisite',token))
    html=html.replace('</head>','<style id="se371ProjectSave">\n'+css+'\n</style>\n</head>',1)
    html=once(html,'if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(',js+'\nif(ALLOWED_PARENTS.has(location.origin))queueMicrotask(','Chat-host-closure runtime')
    for old,new,label in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_370_CLIFF_STONE_SURFACE_POLISH',MARKER,'release marker'),
        ('ENGINE · MAKER v11.370','ENGINE · MAKER v11.371','header'),
        ('v11.370 · refined Cliff cracks, moss and worn cuff',
         'v11.371 · safe Save Project and Clone Project','headline'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.370'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.371'",'build version'),
        ('<title>§wyrl§ Engine · Maker v11.370</title>',
         '<title>§wyrl§ Engine · Maker v11.371</title>','browser title'),
    ]:html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.370';source.version=11.370;"
    n=html.count(old)
    if n not in (3,5,6):raise AssertionError(('provenance count',n))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.371';source.version=11.371;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version')=='v11.370' for item in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.370','changes':notes.get('changes',[])})
    notes.update(version='v11.371',date='2026-11-09',
        title='Safe Save Project and Clone Project across native studios',
        changes=[
          'Canonical starter templates stay immutable. Save on a starter creates an independent editable copy with a fresh ID, never modifying the starter.',
          'Clone Project creates a new full native project from a starter or another saved copy, keeping model meshes, UV, materials, rigs, particles and game levels intact.',
          'Save Project updates only the active saved copy in the existing on-device project library; names alone never select overwrite targets.',
          'When signed into Google, account saves use the existing Chat RPC with optimistic account revision protection; no parallel backend or credential storage is added.',
          'Cloud project IDs and revisions are mirrored as metadata with the on-device project and revalidated after restart; stale or foreign links block account overwrite while retaining local work.',
          'Save/Clone actions sit in existing Game, Model, Particle and Projects command bars. No existing export or modeling control is replaced.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
