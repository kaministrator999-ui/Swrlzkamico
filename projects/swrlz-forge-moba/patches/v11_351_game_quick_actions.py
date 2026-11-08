"""§E v11.351: restore the original Game Engine quick actions on phones and Quest."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_351_GAME_QUICK_ACTIONS'

def one(source, old, new):
    count = source.count(old)
    if count != 1:
        raise AssertionError(('v11.351 source anchor', old[:100], count))
    return source.replace(old, new, 1)

def apply(html):
    css = (ROOT/'runtime/game_quick_actions_v11_351.css').read_text('utf8')
    js = (ROOT/'runtime/game_quick_actions_v11_351.js').read_text('utf8')
    if '</head>' not in html:
        raise AssertionError('v11.351 missing document head')
    html = html.replace('</head>',
       '<style id="se351GameQuickActions">\n'+css+'\n</style>\n</head>', 1)
    html = one(html, 'window.SWRLZ_FORGE_BUILD=',
       js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for before, after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_350_MODEL_VR_TWO_HAND_TOOLS', MARKER),
        ('ENGINE · MAKER v11.350','ENGINE · MAKER v11.351'),
        ('v11.350 · two-hand VR modeling, live profiles, sculpt and draw',
         'v11.351 · restored Game Engine quick actions'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.350'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.351'"),
        ('<title>§wyrl§ Engine · Maker v11.350</title>',
         '<title>§wyrl§ Engine · Maker v11.351</title>')
    ]:
        html = one(html, before, after)
    before = " source.engine='§wyrl§ Engine · Maker v11.350';source.version=11.350;"
    if html.count(before) != 3:
        raise AssertionError(('v11.351 save provenance', html.count(before)))
    html = html.replace(before, " source.engine='§wyrl§ Engine · Maker v11.351';source.version=11.351;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes, width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.350' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.350','changes':notes.get('changes',[])})
    notes.update(version='v11.351',date='2026-11-08',
        title='Game Engine controls restored on phone and Quest',changes=[
        'Always expose the native Projects, Play, Stop, Enter VR and More options controls in a compact Game Engine action row; keep the original button listeners and disabled states.',
        'On Quest Browser, move the original controls out of the old extra Controls drawer and place scene/build options in the existing More options popover, without duplicate actions.',
        'Restore quick-action placement when the device profile changes; keep file-menu project entries available as secondary access.',
        'Do not change saved projects, scene state, VR rendering, Model Studio, other studio tools or player controller mappings.',
        'Physical Android and Quest 2 acceptance remains required.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
