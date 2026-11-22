"""§E v11.543 — source-grounded Find Tool / jump-to-area navigation.

The owner's UV editor displays "UV wireframe"; earlier user-facing guidance
incorrectly called it "Current UV Guide". Search indexes literal real labels
and accepts documented synonyms, invoking native workspace/mode/UV actions.
A small Find button is integrated into the existing workspace nav and
Model Studio header; no new editor, geometry, or account data.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_542_HUMANOID_RELAXED_UV_ATLAS'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_543_TOOL_NAVIGATION_SEARCH'

def once(html,before,after,label):
    count=html.count(before)
    if count!=1:
        raise AssertionError(('se543',label,count,before[:140]))
    return html.replace(before,after,1)

def apply(html):
    script=(ROOT/'runtime/tool_navigation_search_v11_543.js').read_text('utf8')
    css=(ROOT/'runtime/tool_navigation_search_v11_543.css').read_text('utf8')
    for token in ('SE543_TOOL_SEARCH_END','Find tool or area','UV wireframe',
                  'SWYRL_E_TOOL_SEARCH_543','window.SWYRL_E_UNIFIED_TOOLS',
                  'SWYRLZ_E_UV_POPUP'):
        assert token in script,token
    assert 'se543-search-dialog' in css
    html=once(html,'</head>','<style>\n'+css+'\n</style>\n</head>','search styles')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=','native search')
    for before,after in (
      (OLD,MARKER),
      ('ENGINE · MAKER v11.542','ENGINE · MAKER v11.543'),
      ('v11.542 · relaxed humanoid UV atlas and safe editor projection',
       'v11.543 · find tools and navigate directly to real §E panels'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.542'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.543'"),
      ('<title>§wyrl§ Engine · Maker v11.542</title>',
       '<title>§wyrl§ Engine · Maker v11.543</title>')
    ):
        html=once(html,before,after,'release')
    old=" source.engine='§wyrl§ Engine · Maker v11.542';source.version=11.542;"
    assert html.count(old)==5,('source provenance',html.count(old))
    html=html.replace(old,
       " source.engine='§wyrl§ Engine · Maker v11.543';source.version=11.543;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes['history'] if x.get('version')!='v11.542']
    notes['history'].insert(0,{'version':'v11.542','changes':notes['changes']})
    notes.update(
       version='v11.543',date='2026-11-22',
       title='Find Tool — searchable native commands, workspaces and UV destinations',
       changes=[
        'Added compact Find controls in the native workspace tab strip and Model Studio header with mobile-friendly search, keyboard entry, result labels and Escape dismissal.',
        'Search returns actual native destinations: workspace tabs, model category and operation modes, Meshes, Sculpt, Face, Rigging, Animation, UV Editor, UV wireframe, Applied texture, Surface map and Stretch heatmap.',
        'Search distinguishes the UV wireframe preview from the real Export UV wireframe action. Searching Current UV Guide leads to the real export button, not the preview toggle.',
        'Moves the one native Export UV wireframe button beside the UV preview, preserving its bound handler, disabled state and original PNG output rather than duplicating the export.',
        'Uses actual Model Studio native APIs to activate categories/modes, mini-studio rigging/animation and UV Editor popup. No mesh, UV, material, save or account mutation occurs from searching.',
        'No persistent indexing of private projects or chat data; navigation-only entries live locally in browser memory. Old model assets, starter project categories and UV editor state are preserved.',
        'Source/runtime validation and destination tests run before release; final owner mobile and Quest menu usability remains device acceptance.'
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
