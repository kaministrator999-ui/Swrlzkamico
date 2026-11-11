"""§E v11.412 — guided beginner satchel quest in native Model Studio.

Append after previous governed source patch; no startup-project mutation.
Requires manifest and final artifact integrity reseal before publishing.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_412_APPRENTICE_SATCHEL_TUTORIAL'

def one(src, old, new):
    n=src.count(old)
    if n!=1: raise AssertionError(('v11.412 anchor', old[:100], n))
    return src.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/model_satchel_tutorial_v11_412.js').read_text('utf8')
    css=(ROOT/'runtime/model_satchel_tutorial_v11_412.css').read_text('utf8')
    for required in ('function loadCourierProject(', 'async function se371Clone(',
                     'const se371PriorSnapshot=se175Snapshot;', 'const se320ProjectDataBase=projectData;',
                     'window.SWRLZ_FORGE_BUILD='):
        if required not in html: raise AssertionError(('v11.412 prerequisite',required))
    assert html.index('</head>') < html.index('<body')
    html=html.replace('</head>', '<style id="se412TutorialStyles">'+css+'</style>\n</head>', 1)
    html=one(html, 'if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(',
                js+'\nif(ALLOWED_PARENTS.has(location.origin))queueMicrotask(')
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_411_SHEEP_QUEST_AI_FRAME_BUDGET',MARKER),
        ('ENGINE · MAKER v11.411','ENGINE · MAKER v11.412'),
        ('v11.411 · smooth Quest sheep NPC planning', 'v11.412 · apprentice satchel guided modeling tutorial'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.411'", "window.SWRLZ_FORGE_BUILD={version:'v11.412'"),
        ('<title>§wyrl§ Engine · Maker v11.411</title>', '<title>§wyrl§ Engine · Maker v11.412</title>')]:
        html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.411';source.version=11.411;"
    if html.count(old)!=5: raise AssertionError(('v11.412 provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.412';source.version=11.412;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    if not any(i.get('version')=='v11.411' for i in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0, {'version':'v11.411','changes':notes.get('changes',[])})
    notes.update(version='v11.412',date='2026-11-11',title='Guided Apprentice Satchel modeling quest',changes=[
      'Projects adds a Tutorials tab with Apprentice Satchel. Start creates a fresh editable native model copy with a practice cube; original starter templates remain unchanged.',
      'A movable/collapsible quest panel stays within the ordinary Model Studio work area, with seven selectable objectives, real tool names, explanation, hints, next/previous navigation and project-specific checkoffs.',
      'Body proportions and material assignments can be verified against the real project; geometry-dependent objectives explicitly require visual confirmation rather than claiming unsupported automatic inspection.',
      'Progress is device-local and keyed by saved project ID, with Resume and existing native Save Project/account sync. No duplicate model editor, geometry overlay, VR hand control or source ownership changes.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]