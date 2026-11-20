"""§E v11.530 — continuous Quest ray/gizmo edits and controller-following three-stage menu.

Append-only release patch: keep earlier versions intact, use the existing
single WebXR renderer, authoritative modeling transactions and menu hit targets.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_530_QUEST_GIZMO_CONTROLLER_MENU'

def one(html,old,new,label):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('v11.530',label,n,old[:140]))
    return html.replace(old,new,1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_529_NATIVE_ACCOUNT_BROWSER_LIBRARY' in html
    runtime=(ROOT/'runtime/model_vr_controller_palette_v11_530.js').read_text('utf8')
    assert 'SE530_VR_CONTINUOUS_GIZMO_AND_CONTROLLER_PALETTE_END' in runtime
    html=one(html,'/* SE528_XR_RAY_AND_PARAMETER_CONTROLS_END */',
        '/* SE528_XR_RAY_AND_PARAMETER_CONTROLS_END */\n'+runtime,
        'install native XR ray/menu correction after previous input layers')

    # Add both sculpt directions to the actual second-level operation menu.
    # Face tools remain accessible under their existing first-level category.
    start='/* SE443_MODEL_VR_VERTICAL_DOCK_START */'
    end='/* SE445_VR_PROGRESSIVE_TOOLS_END */'
    a=html.index(start)
    b=html.index(end,a)
    dock=html[a:b]
    dock=one(dock,"sculpt:[['sculpt-push','Push'],['sculpt-smooth','Smooth']",
        "sculpt:[['sculpt-push','Pull / Raise'],['sculpt-indent','Indent / Lower'],['sculpt-smooth','Smooth']",
        'make outward/inward sculpt operations explicit')
    dock=one(dock,"['manual-subdivide','Subdivide'],['manual-mesh','Other face tools']]",
        "['manual-subdivide','Subdivide']]",
        'keep eleven operation rows without duplicate face category')
    html=html[:a]+dock+html[b:]

    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_529_NATIVE_ACCOUNT_BROWSER_LIBRARY',MARKER),
        ('ENGINE · MAKER v11.529','ENGINE · MAKER v11.530'),
        ('v11.529 · native account-save routing and professional browser My Projects',
         'v11.530 · continuous immersive gizmos and left-hand tool console'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.529'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.530'"),
        ('<title>§wyrl§ Engine · Maker v11.529</title>',
         '<title>§wyrl§ Engine · Maker v11.530</title>')
    ]:
        html=one(html,before,after,'release identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.529';source.version=11.529;"
    if html.count(old)!=5:
        raise AssertionError(('v11.530 provenance',html.count(old)))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.530';source.version=11.530;")
    marker='const SE_RELEASE_NOTES='
    at=html.index(marker)+len(marker)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.529']
    notes['history'].insert(0,{'version':'v11.529','changes':notes.get('changes',[])})
    notes.update(version='v11.530',date='2026-11-20',
        title='Continuous native VR model transformations and controller console',
        changes=[
            'Immersive Move/Rotate/Scale Trigger grips continuously sample the tracked controller ray and update the existing native preview; near-parallel ray positions fall back to controlled grip displacement instead of freezing.',
            'Selected-model direct Trigger movement now supports free translation without requiring a gizmo axis; precision switching and solver changes rebase without a sudden jump.',
            'The original three-stage Tools, Operations and Settings menu follows the left controller grip at a consistent comfortable forward offset, always facing the headset and retaining the existing ray hit targets and panel state.',
            'Sculpt second-stage operations expose both outward Raise and inward Indent. The third-stage sculpt inspector shows one focused operation and its original radius/strength parameter toolbar rather than repeating the full brush menu.',
            'The left Quest menu button still toggles the entire tool console when WebXR exposes it; X remains the fallback on Meta/browser builds that reserve that hardware button.',
            'No duplicate WebXR scene, model document, sculpt transaction, settings authority or cloud save path is introduced. Physical Quest acceptance is required.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
