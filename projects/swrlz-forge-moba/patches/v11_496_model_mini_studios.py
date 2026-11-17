"""§E v11.496 — shared viewport Model, Rigging and Animation mini-studios.
Append-only adapter; preserve the original project, GPU skinning and tool architecture.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_496_MODEL_MINI_STUDIOS'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.496',label,count,old[:100]))
    return html.replace(old,new,1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_495_FAST_REVISION_TRANSFER' in html
    js=(ROOT/'runtime/model_mini_studios_v11_496.js').read_text('utf8')
    css=(ROOT/'runtime/model_mini_studios_v11_496.css').read_text('utf8')
    assert 'window.SWYRL_ENGINE_MINI_STUDIOS_496=se496MiniStudios' in js
    assert '#se496ModeTabs' in css
    html=once(html,'  function refreshList(){',
        js+'\n  function refreshList(){','live model-scoped mini-studio controller')
    html=once(html,'</head>',
        '<style id="se496MiniStudios">'+css+'</style>\n</head>',
        'focus and mobile layout styles')
    # The existing saved workspace is the only persisted mode owner.
    # The model is not reloaded or cloned when changing the active studio.
    html=once(html,
        "return {schema:'swyrl-model-workspace-v2',",
        "return {schema:'swyrl-model-workspace-v2',studioMode:window.SWYRL_ENGINE_MINI_STUDIOS_496?.mode?.()||'model',",
        'native per-project workspace snapshot')
    html=once(html,
        "   if(saved.tool)window.SWYRL_E_UNIFIED_TOOLS?.select?.(saved.tool.category,saved.tool.mode);",
        "   if(['model','rig','animate'].includes(saved.studioMode))\n"
        "    window.SWYRL_ENGINE_MINI_STUDIOS_496?.set?.(saved.studioMode,false);\n"
        "   if(saved.tool)window.SWYRL_E_UNIFIED_TOOLS?.select?.(saved.tool.category,saved.tool.mode);",
        'native workspace restoration')
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_495_FAST_REVISION_TRANSFER',MARKER),
        ('ENGINE · MAKER v11.495','ENGINE · MAKER v11.496'),
        ('v11.495 · faster model updates with compact revision history',
         'v11.496 · Model, Rigging and Animation mini-studios'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.495'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.496'"),
        ('<title>§wyrl§ Engine · Maker v11.495</title>',
         '<title>§wyrl§ Engine · Maker v11.496</title>')
    ):
        html=once(html,old,new,'runtime identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.495';source.version=11.495;"
    if html.count(old)!=5:
        raise AssertionError(('v11.496 provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.496';source.version=11.496;")
    marker='const SE_RELEASE_NOTES='
    at=html.index(marker)+len(marker)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.495']
    notes['history'].insert(0,{'version':'v11.495','changes':notes.get('changes',[])})
    notes.update(version='v11.496',date='2026-11-17',
        title='Model, Rigging and Animation in one Model Studio viewport',
        changes=[
            'Three mini-studios switch the native tool interface without restarting the WebGL renderer, reloading the model, losing the camera, or creating duplicate projects.',
            'Rigging reuses weighted GPU SkinnedMesh deformation and enables basic cloth armature creation from an unrigged selected mesh, hierarchical child joints, bounded joint rest transforms and automatic influence tuning.',
            'Animation exposes the original editable clip selector, joint poses, keyframe timeline, looping, playback, and save/load through the same live model.',
            'Mode choice is included in existing per-project workspace capture and restore, while project revisions, source mesh, UV texture, GPU rendering, and camera state remain authoritative.',
            'Modeling keeps its existing sculpt, vertex, ring and UV tool architecture. Mobile and VR share the same modes without introducing a second viewport.',
            'Automatic influence envelopes are the first rig-authoring tool; freehand skin weight painting is not implemented in this release.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
