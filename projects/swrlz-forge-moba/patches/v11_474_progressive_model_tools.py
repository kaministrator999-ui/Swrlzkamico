"""§E v11.474: progressive family/tool/specific-mode/inspector navigation."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_474_PROGRESSIVE_MODEL_TOOLS'

def once(html,old,new):
    count=html.count(old)
    assert count==1,('v11.474 source anchor',old[:80],count)
    return html.replace(old,new,1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_473_FOLDING_WORKSPACE' in html
    assert '/* SE473_MODEL_TOOL_RAIL_FOLD_END */' in html
    assert '/* SE466_RING_UI_START */' in html
    assert '/* SE452_NATIVE_FACE_FLYOUTS_START */' in html
    assert '/* SE430_MODEL_BEGINNER_UI_START */' in html
    js=(ROOT/'runtime/model_progressive_tools_v11_474.js').read_text('utf8')
    css=(ROOT/'runtime/model_progressive_tools_v11_474.css').read_text('utf8')
    assert 'SE474_PROGRESSIVE_MODEL_TOOLS_START' in js
    assert 'SE474_PROGRESSIVE_MODEL_TOOLS_STYLES_START' in css
    html=once(html,'/* SE473_MODEL_TOOL_RAIL_FOLD_END */',
                  '/* SE473_MODEL_TOOL_RAIL_FOLD_END */\n'+js)
    assert '</head>' in html,('v11.474 missing document head')
    html=html.replace('</head>','<style id="se474ProgressiveModelTools">\n'+css+'\n</style>\n</head>',1)
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_473_FOLDING_WORKSPACE',MARKER),
      ('ENGINE · MAKER v11.473','ENGINE · MAKER v11.474'),
      ('v11.473 · floating UV and collapsible workspace','v11.474 · progressive mobile modeling tools'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.473'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.474'"),
      ('<title>§wyrl§ Engine · Maker v11.473</title>',
       '<title>§wyrl§ Engine · Maker v11.474</title>')
    ]:html=once(html,before,after)
    old=" source.engine='§wyrl§ Engine · Maker v11.473';source.version=11.473;"
    assert html.count(old)==5,('v11.474 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.474';source.version=11.474;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.473']
    notes['history'].insert(0,{'version':'v11.473','changes':notes.get('changes',[])})
    notes.update(version='v11.474',date='2026-11-16',
        title='Progressive mobile modeling toolbars',
        changes=[
          'Select a main modeling family from the existing vertical rail; its actual tool choices appear in a compact flyout directly to the left.',
          'Selecting a tool reveals a single horizontally scrolling row of specific operation modes at the top of the Model Studio viewport.',
          'The far-right inspector remains closed until a specific mode with parameters is selected; hiding settings never clears the active tool or geometry selection.',
          'Sculpt and Topology expose native-backed Vertex Single, Ring and Ring Fill operations, plus Inset and Extrude with Face/Region variants.',
          'Ring modes reuse connected-edge selection, center, radius and arc inputs from v11.466; they do not claim to flood arbitrary lasso-shaped loops.',
          'Original manual mesh operations retain their native preview, Apply, Cancel, Undo, UV preservation and selection guards.',
          'The previous Face flyout is consolidated into the progressive navigation, not left overlapping the new controls.',
          'Category rail folding, screen-wide UV window, existing camera/VR/editor systems and projects remain available. Physical Moto/Quest acceptance remains pending.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+length:]
