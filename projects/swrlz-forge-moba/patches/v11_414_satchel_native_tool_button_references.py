"""§E v11.414: native control/button appearance shown beside satchel tool words.

Append only after v11.413. Flat editor references use the real DOM button
look and label; VR icons are drawn by the actual existing VR console painter.
Never create extra model controls, mutate a starter, or start a second XR loop.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_414_SATCHEL_NATIVE_BUTTON_GUIDES'

def one(source,old,new):
    count=source.count(old)
    if count!=1:raise AssertionError(('v11.414 anchor',old[:110],count))
    return source.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/model_satchel_tool_references_v11_414.js').read_text('utf8')
    css=(ROOT/'runtime/model_satchel_tool_references_v11_414.css').read_text('utf8')
    assert 'SE413_SATCHEL_VR_QUEST_START' in html
    # Existing painter supplies EXACT SAME SVG-like canvas icon paths to help
    # text. The mini-icon API is read-only and survives until its VR UI disposal.
    html=one(html,
      'return Object.freeze({root,targets,update,hover,press,hitTest,dispose,openWheel,closeWheel,releaseWheel,tick,',
      "return Object.freeze({root,targets,drawGuideIcon:(ctx,action,x,y,size,color)=>icon(ctx,iconType(action),x,y,size,color),update,hover,press,hitTest,dispose,openWheel,closeWheel,releaseWheel,tick,")
    html=one(html,
      '  se413PaintDemo(panel,current);',
      '  se413PaintDemo(panel,current);\n  window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414?.renderFlat(panel,current,step);')
    html=one(html,
      "  wrap(c,'TOOL: '+(step?.tool||''),32,322,948,34,2);",
      "  if(!window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414?.renderVR(c,step,se340XR.ui))wrap(c,'TOOL: '+(step?.tool||''),32,322,948,34,2);")
    html=one(html,
      "  wrap(c,step?.task||'',32,408,950,37,4);",
      "  if(window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414)window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414.vrTask(c,step,se340XR.ui);else wrap(c,step?.task||'',32,408,950,37,4);")
    html=one(html,
      "  wrap(c,'TIP: '+(step?.hint||''),32,559,947,32,2);",
      "  if(window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414)window.SWYRL_E_SATCHEL_BUTTON_GUIDE_414.vrHint(c,step,se340XR.ui);else wrap(c,'TIP: '+(step?.hint||''),32,559,947,32,2);")
    # The new helper mounts before the host/bootstrap event handler.
    html=one(html,
      'if(ALLOWED_PARENTS.has(location.origin))queueMicrotask(',
      js+'\nif(ALLOWED_PARENTS.has(location.origin))queueMicrotask(')
    assert html.index('</head>')<html.index('<body')
    html=html.replace('</head>','<style id="se414SatchelButtonReferences">'+css+'</style>\n</head>',1)
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_413_SATCHEL_VR_TUTORIAL',MARKER),
      ('ENGINE · MAKER v11.413','ENGINE · MAKER v11.414'),
      ('v11.413 · satchel modeling plus VR quest','v11.414 · matching native tool button references'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.413'","window.SWRLZ_FORGE_BUILD={version:'v11.414'"),
      ('<title>§wyrl§ Engine · Maker v11.413</title>','<title>§wyrl§ Engine · Maker v11.414</title>')
    ]:html=one(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.413';source.version=11.413;"
    if html.count(old)!=5:raise AssertionError(('v11.414 provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.414';source.version=11.414;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.setdefault('history',[]).insert(0,{'version':'v11.413','changes':notes.get('changes',[])})
    notes.update(version='v11.414',date='2026-11-11',title='Apprentice Satchel recognizes its actual modeling buttons',changes=[
      'The lesson displays noninteractive visual miniatures of the real native Model Studio tool buttons next to each referenced tool name and embedded instructional mention.',
      'The VR quest shows icons drawn with the existing VR menu icon painter alongside matching action labels, including Cube, Move, Rotate, Scale, Duplicate, and Save project.',
      'The guide clarifies that flat Model Studio Add sphere creates a sphere and its Shape selector changes the new part to box; VR Create > Cube places a cube directly.',
      'Material and Color remain flat-inspector fields, not imaginary VR buttons. All visual references are read-only, responsive and project-save neutral.',
      'All existing XR controls, VR tool menu, rendering loop, geometry editing, account projects, starters, and Sheep Tag remain independently owned.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
