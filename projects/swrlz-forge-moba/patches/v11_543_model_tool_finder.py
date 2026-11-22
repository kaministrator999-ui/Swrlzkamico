"""§E v11.543 — discover existing tools and move actual UV export into preview.

Only one source action per tool. Search navigates and highlights native buttons or
selects the native mode. The original export button itself is moved, not copied.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_542_HUMANOID_RELAXED_UV_ATLAS'
NEW='SWYRL_ENGINE_DEPLOY_MARKER: V11_543_TOOL_FINDER_AND_UV_EXPORT'

def once(html,before,after,context):
    count=html.count(before)
    if count!=1:
        raise AssertionError(('se543',context,count,before[:120]))
    return html.replace(before,after,1)

def apply(html):
    script=(ROOT/'runtime/model_tool_finder_v11_543.js').read_text('utf8')
    for token in ('SE543_FIND_TOOLS_END','destination.prepend(original)',
                  'SWYRL_ENGINE_FIND_TOOLS_543','SWYRL_E_UNIFIED_TOOLS',
                  'se355UVPopup', 'se336UVExport'):
        assert token in script,token
    # The model studio opener and all Model Atelier UI are defined before
    # the release/build identity. The new finder mounts lazily via DOM.
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=','finder install')
    for before,after in (
      (OLD,NEW),
      ('ENGINE · MAKER v11.542','ENGINE · MAKER v11.543'),
      ('v11.542 · relaxed humanoid UV atlas and safe editor projection',
       'v11.543 · find existing tools and move UV export beside preview'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.542'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.543'"),
      ('<title>§wyrl§ Engine · Maker v11.542</title>',
       '<title>§wyrl§ Engine · Maker v11.543</title>')
    ):
        html=once(html,before,after,'release identity')
    prior=" source.engine='§wyrl§ Engine · Maker v11.542';source.version=11.542;"
    assert html.count(prior)==5,('source provenance',html.count(prior))
    html=html.replace(prior,
      " source.engine='§wyrl§ Engine · Maker v11.543';source.version=11.543;")
    start=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,width=json.JSONDecoder().raw_decode(html[start:])
    notes['history']=[n for n in notes['history'] if n.get('version')!='v11.542']
    notes['history'].insert(0,{'version':'v11.542','changes':notes['changes']})
    notes.update(version='v11.543',date='2026-11-22',
      title='Find existing Model Studio tools and move UV export next to preview',
      changes=[
       'Add a compact Find tool control to Model Studio. Search discovers the live category/mode registry and actual mounted controls, including UV export, sculpt, topology, file, materials and projects.',
       'Choosing a search result navigates to the existing panel or native mode, expands details and highlights the real control. It never auto-executes destructive commands. Keyboard Enter and Escape and Ctrl/Cmd+K are supported.',
       'Re-parent the original Export UV wireframe button beside the UV preview rather than duplicating the export action; original mesh selection guards, handlers and file output remain authoritative.',
       'Search handles the separate UV Editor popup and avoids creating duplicate actions, fake buttons, project mutations, extra 3D viewers or network dependencies.',
       'Preserve Starter Models including the unified humanoid, saved projects, existing tool categories, UV textures, and Model/VR/Account workflows. Owner phone/Quest UX acceptance remains outstanding.'
      ])
    rendered=json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
    return html[:start]+rendered+html[start+width:]
