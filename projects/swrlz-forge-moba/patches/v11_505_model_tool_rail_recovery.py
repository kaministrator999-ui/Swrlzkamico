"""§E v11.505: recover native modeling family rail from stuck folded/inspector state.

Change only the existing v11.473 fold preference and v11.320 capture guard;
do not duplicate tool handlers or replace the original inspector/viewport.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_505_MODEL_TOOL_RAIL_RECOVERY'

def once(html, old, new, label):
    count = html.count(old)
    if count != 1:
        raise AssertionError(('se505', label, count, old[:110]))
    return html.replace(old, new, 1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_504_SMOOTH_WITCH_HAT' in html
    assert 'SE473_MODEL_TOOL_RAIL_FOLD_START' in html
    assert 'SE496_MINI_STUDIOS' in html or 'SWYRL_ENGINE_MINI_STUDIOS_496' in html

    # Fold state v1 could survive even when the user could not expand the rail.
    # Retire that single preference key; v2 starts expanded, then remembers any
    # NEW explicit user folds. Do not reset project/mesh/camera/studio settings.
    html = once(
        html,
        "const key='swyrl.engine.modeler.tool-rail-fold.v1';",
        "const key='swyrl.engine.modeler.tool-rail-fold.v2';",
        'recover persisted collapsed rail once'
    )

    # The old capture listener responds to ALL rail buttons, including the
    # fold toggle. When the inspector is closed that triggers another dock
    # transition before the native fold handler gets its click.
    html = once(
        html,
        """   rail.addEventListener('click',event=>{
    if(!event.target.closest('button'))return;
    if(panel.dataset.se251RightCollapsed==='true')q('.se251-external-collapse',panel)?.click();
   },true);""",
        """   rail.addEventListener('click',event=>{
    if(!event.target.closest('button')||event.target.closest('#se473RailFold'))return;
    if(panel.dataset.se251RightCollapsed==='true')q('.se251-external-collapse',panel)?.click();
   },true);""",
        'fold button must not toggle inspector'
    )

    css = (ROOT / 'runtime/model_tool_rail_recovery_v11_505.css').read_text('utf-8')
    assert 'SE505_MODEL_TOOL_RAIL_RECOVERY_STYLES_END' in css
    html = once(html, '</head>',
        '<style id="se505ModelToolRailRecovery">\\n' + css + '\\n</style>\\n</head>',
        'late scoped rail visibility CSS')

    for old, new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_504_SMOOTH_WITCH_HAT', MARKER),
        ('ENGINE · MAKER v11.504', 'ENGINE · MAKER v11.505'),
        ('v11.504 · independent smooth textured witch hat starter',
         'v11.505 · restore modeling toolset rail on mobile'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.504'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.505'"),
        ('<title>§wyrl§ Engine · Maker v11.504</title>',
         '<title>§wyrl§ Engine · Maker v11.505</title>')
    ):
        html = once(html, old, new, 'version identity')
    old = " source.engine='§wyrl§ Engine · Maker v11.504';source.version=11.504;"
    assert html.count(old) == 5, ('se505 project provenance', html.count(old))
    html = html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.505';source.version=11.505;")
    key = 'const SE_RELEASE_NOTES='
    start = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[start:])
    notes['history'] = [x for x in notes.get('history', [])
                        if x.get('version') != 'v11.504']
    notes['history'].insert(0, {'version': 'v11.504',
                                 'changes': notes.get('changes', [])})
    notes.update(
        version='v11.505', date='2026-11-18',
        title='Recover the native Modeling toolset rail',
        changes=[
            'Restored the Meshes, Sculpt, Lasso, Topology, Face, Appearance, Motion and References toolset rail in Modeling mode after an inaccessible persisted folded state.',
            'Migrated only the tool-rail fold preference to v2 (initially expanded, future user folds still saved); model files, selected mesh, texture, UVs, project revisions and camera preferences are unchanged.',
            'The fold/expand control no longer incorrectly opens the settings inspector through the older rail click capture handler.',
            'Scoped rail visibility to the Modeling mini-studio, preserving intentionally hidden modeling controls in Rigging and Animation.'
        ])
    return html[:start] + json.dumps(notes, ensure_ascii=False,
        separators=(',', ':')).replace('</', r'<\\/') + html[start+width:]
