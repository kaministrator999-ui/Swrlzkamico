"""§E v11.498: repair rig/animation UI leakage and show selectable 3D bones.
Additive repair on v11.497; source mesh, UV and rig payload untouched.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_498_RIG_STUDIO_POLISH'
def once(html,old,new,label):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.498',label,count,old[:110]))
    return html.replace(old,new,1)
def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_497_SCULPTED_SORTING_HAT' in html
    js=(ROOT/'runtime/model_rig_studio_polish_v11_498.js').read_text('utf8')
    css=(ROOT/'runtime/model_rig_studio_polish_v11_498.css').read_text('utf8')
    assert 'window.SWYRL_ENGINE_RIG_POLISH_498=se498RigPolish' in js
    assert 'data-se498-rig-kind=object' in css
    html=once(html,'window.SWYRL_ENGINE_MINI_STUDIOS_496=se496MiniStudios;',
      'window.SWYRL_ENGINE_MINI_STUDIOS_496=se496MiniStudios;\n'+js,
      'append overlay and bone adapter inside ModelAtelier')
    if '</head>' not in html:raise AssertionError('No HTML root head')
    html=html.replace('</head>','<style id="se498RigStudioPolish">'+css+'</style>\n</head>',1)
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_497_SCULPTED_SORTING_HAT',MARKER),
      ('ENGINE · MAKER v11.497','ENGINE · MAKER v11.498'),
      ('v11.497 · a second sculpted Sorting Hat starter',
       'v11.498 · isolated rig and animation studios with 3D bone controls'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.497'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.498'"),
      ('<title>§wyrl§ Engine · Maker v11.497</title>',
       '<title>§wyrl§ Engine · Maker v11.498</title>')
    ):html=once(html,old,new,'release identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.497';source.version=11.497;"
    if html.count(old)!=5:raise AssertionError(('provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.498';source.version=11.498;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.497']
    notes['history'].insert(0,{'version':'v11.497','changes':notes.get('changes',[])})
    notes.update(version='v11.498',date='2026-11-17',
      title='Dedicated rigging and animation UI with articulated bone handles',
      changes=[
        'Rigging and Animation now isolate inherited Model Studio transform strips, view modes, tool rails, inspector and selection overlays while keeping the existing renderer, project and camera.',
        'A lightweight viewport bone overlay replaces wire-only SkeletonHelper with colored root/child joints, tapered joint links, selection highlight, x-ray rendering and tap-to-select joints on phone and desktop.',
        'Hand gestures, thumb opposition, thumb curl and related hand controls are now gated to hand rigs and hidden for cloth and general object rigs.',
        'Rig mode exposes structural skeleton editing, while Animation keeps clip/keyframe/playback controls. Joint selection is shared across the modes.',
        'Existing model geometry, UV texture, GPU skinning, joint rest coordinates, clips, account saves and revision history are preserved.',
        'Focused source-integrity validation is automated; final Moto/Quest acceptance requires actual device testing.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
