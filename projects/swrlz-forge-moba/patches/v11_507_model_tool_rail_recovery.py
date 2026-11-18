"""§E v11.507: recover native modeling family rail from stuck folded/inspector state.

Change only the existing v11.473 fold preference and v11.320 capture guard;
do not duplicate tool handlers or replace the original inspector/viewport.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_507_MODEL_TOOL_RAIL_RECOVERY'

def once(html, old, new, label):
    count = html.count(old)
    if count != 1:
        raise AssertionError(('se507', label, count, old[:110]))
    return html.replace(old, new, 1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_506_UV_BUTTON_OWNERSHIP' in html
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

    css = (ROOT / 'runtime/model_tool_rail_recovery_v11_507.css').read_text('utf-8')
    assert 'SE507_MODEL_TOOL_RAIL_RECOVERY_STYLES_END' in css
    assert '</head>' in html and html.index('</head>') < html.index('<body'), 'root HTML head missing'
    html = html.replace('</head>',
        '<style id="se507ModelToolRailRecovery">\\n' + css + '\\n</style>\\n</head>', 1)

    for old, new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_506_UV_BUTTON_OWNERSHIP', MARKER),
        ('ENGINE · MAKER v11.506', 'ENGINE · MAKER v11.507'),
        ('v11.506 · UV atlas preview button ownership and prerequisites',
         'v11.507 · restore modeling toolset rail on mobile'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.506'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.507'"),
        ('<title>§wyrl§ Engine · Maker v11.506</title>',
         '<title>§wyrl§ Engine · Maker v11.507</title>')
    ):
        html = once(html, old, new, 'version identity')
    old = " source.engine='§wyrl§ Engine · Maker v11.506';source.version=11.506;"
    assert html.count(old) == 5, ('se507 project provenance', html.count(old))
    html = html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.507';source.version=11.507;")
    key = 'const SE_RELEASE_NOTES='
    start = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[start:])
    notes['history'] = [x for x in notes.get('history', [])
                        if x.get('version') != 'v11.506']
    notes['history'].insert(0, {'version': 'v11.506',
                                 'changes': notes.get('changes', [])})
    notes.update(
        version='v11.507', date='2026-11-18',
        title='Recover the native Modeling toolset rail',
        changes=[
            'Restored the Meshes, Sculpt, Lasso, Topology, Face, Appearance, Motion and References toolset rail in Modeling mode after an inaccessible persisted folded state.',
            'Migrated only the tool-rail fold preference to v2 (initially expanded, future user folds still saved); model files, selected mesh, texture, UVs, project revisions and camera preferences are unchanged.',
            'The fold/expand control no longer incorrectly opens the settings inspector through the older rail click capture handler.',
            'Scoped rail visibility to the Modeling mini-studio, preserving intentionally hidden modeling controls in Rigging and Animation.'
        ])
    return html[:start] + json.dumps(notes, ensure_ascii=False,
        separators=(',', ':')).replace('</', r'<\\/') + html[start+width:]
