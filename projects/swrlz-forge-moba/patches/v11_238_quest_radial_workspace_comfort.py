"""§E v11.238 candidate — Quest app-radial stutter and 2D studio layout.

Append-only patch on the governed v11.236 source. Does not run until the
ordered manifest is extended and official final HTML seal rebuilt.
"""
from pathlib import Path
import json

def once(source, old, new, label):
    count=source.count(old)
    if count!=1:
        raise AssertionError(('v11.238 source anchor',label,count,old[:110]))
    return source.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    radial=(root/'runtime/engine_quest_radial_frame_guard_v11_238.js').read_text(encoding='utf-8')
    layout=(root/'runtime/engine_quest_workspace_navigation_v11_238.js').read_text(encoding='utf-8')
    styles=(root/'runtime/engine_quest_workspace_navigation_v11_238.css').read_text(encoding='utf-8')
    for dependency in (
      'function se211OnFrame()', 'function se211Cosmetics(', 'function se195RadialHit(',
      'function se195Text(', 'window.SWYRL_ENGINE_DEVICE',
      'window.SWYRL_ENGINE_QUEST_OS_STABILITY_211',
      'function se204WheelShow(',
    ):
        assert dependency in html, ('missing Quest runtime prerequisite',dependency)
    if '</head>' not in html:
        raise AssertionError('missing document head for Quest layout')
    html=html.replace('</head>','<style id="se238QuestBrowserLayout">\n'+styles+'\n</style>\n</head>',1)
    html=once(html,'window.SWRLZ_FORGE_BUILD=',
      radial+'\n'+layout+'\nwindow.SWRLZ_FORGE_BUILD=','runtime injection')

    before=" source.engine='§wyrl§ Engine · Maker v11.236';source.version=11.236;"
    after=" source.engine='§wyrl§ Engine · Maker v11.238';source.version=11.238;"
    if html.count(before)!=2:
        raise AssertionError(('v11.238 native save provenance',html.count(before)))
    html=html.replace(before,after)
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_236_SHEEP_GABLES_WOLF_ROOT_STARTER_GROUPS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_238_QUEST_RADIAL_AND_WORKSPACE'),
      ('ENGINE · MAKER v11.236','ENGINE · MAKER v11.238'),
      ('v11.236 · sheep gables, wolf root preview, starter categories',
       'v11.238 · Quest radial menu frame recovery and studio layout'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.236'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.238'"),
      ('<title>§wyrl§ Engine · Maker v11.236</title>',
       '<title>§wyrl§ Engine · Maker v11.238</title>'),
    ):
        html=once(html,old,new,'release identity')
    key='const SE_RELEASE_NOTES='
    pos=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(
      title='Quest game radial stutter stabilization and uncluttered editor controls',
      date='2026-11-02',
      changes=[
        'Classify 170–650ms WebXR callbacks as application slow frames, not as lost Quest OS focus, only while an already-open game radial is visible and the headset still reports the app as visible. Existing genuine blur/hidden and larger-gap safety logic is retained.',
        'Preserve the user-open radial and independent game panels during a visible-session application slowdown. Do not silently hide the dial as if Meta OS Camera had taken over.',
        'Cache same-frame radial raycast answers and native radial label textures between menu pages, preserving left-stick gameplay movement, right-stick camera view/zoom, controller selection and hit-testing.',
        'In Quest Browser 2D pages only, keep fast workspace tabs in one scrollable row and move the original Game Engine toolbar controls into an accessible Controls popover.',
        'In Model Atelier Quest Browser only, retain the native Close action, place other original header buttons in a Model actions popover, and show the existing tool rail on demand with an Edit tools control to avoid covering the wolf inspector.',
        'All changes restore original 2D controls when Quest UI is switched off. No Meta OS native window management or WebXR eye projection is changed.',
        'Quest 2 owner hands-on tests required. Source is a candidate until integrity seal and separate deployment approval are completed.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
