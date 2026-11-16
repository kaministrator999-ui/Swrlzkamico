"""§E v11.475 — restore visible progressive flyout and accurate family highlighting."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_475_PROGRESSIVE_RAIL_VISIBILITY'
def once(src,old,new):
    count=src.count(old)
    assert count==1,('v11.475 unique anchor',old[:120],count)
    return src.replace(old,new,1)
def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_474_PROGRESSIVE_MODEL_TOOLS' in html
    assert '/* SE474_PROGRESSIVE_MODEL_TOOLS_END */' in html
    assert '/* SE473_MODEL_TOOL_RAIL_FOLD_END */' in html
    js=(ROOT/'runtime/model_progressive_rail_fix_v11_475.js').read_text('utf8')
    css=(ROOT/'runtime/model_progressive_rail_fix_v11_475.css').read_text('utf8')
    assert 'SE475_PROGRESSIVE_RAIL_VISIBILITY_START' in js
    assert 'SE475_PROGRESSIVE_RAIL_VISIBILITY_STYLES_START' in css
    # v11.466 declared the ring UI inside ModelAtelier's private closure, but
    # atelierAdaptiveInstall (a separate native UI scope) called its bare name.
    # Export ONLY this original installer; keep workshop and topology private.
    html=once(html,'/* SE466_RING_UI_END */',
      'window.SWYRL_ENGINE_RING_UI_INSTALL_475=se466RingUIInstall;\n/* SE466_RING_UI_END */')
    html=once(html,'se430BeginnerInstall(panel);se466RingUIInstall(panel);',
      'se430BeginnerInstall(panel);'+
      'if(typeof window.SWYRL_ENGINE_RING_UI_INSTALL_475!=="function")'+
      'throw Error("Native ring UI installer unavailable");'+
      'window.SWYRL_ENGINE_RING_UI_INSTALL_475(panel);')
    html=once(html,'/* SE474_PROGRESSIVE_MODEL_TOOLS_END */',
      '/* SE474_PROGRESSIVE_MODEL_TOOLS_END */\n'+js)
    assert '</head>' in html
    html=html.replace('</head>','<style id="se475ProgressiveVisibility">\n'+css+
                      '\n</style>\n</head>',1)
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_474_PROGRESSIVE_MODEL_TOOLS',MARKER),
      ('ENGINE · MAKER v11.474','ENGINE · MAKER v11.475'),
      ('v11.474 · progressive mobile modeling tools','v11.475 · visible mobile tool flyouts'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.474'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.475'"),
      ('<title>§wyrl§ Engine · Maker v11.474</title>',
       '<title>§wyrl§ Engine · Maker v11.475</title>')
    ]:html=once(html,before,after)
    prior=" source.engine='§wyrl§ Engine · Maker v11.474';source.version=11.474;"
    assert html.count(prior)==5,('v11.475 provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.475';source.version=11.475;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.474']
    notes['history'].insert(0,{'version':'v11.474','changes':notes.get('changes',[])})
    notes.update(version='v11.475',date='2026-11-16',
      title='Restore visible mobile tool flyouts and selected highlights',
      changes=[
        'Fixed tool flyout being clipped by the old right-category rail scroll container. The original live flyout node is moved to the native modeling body and anchored beside the selected family.',
        'Selected main tool-family button now reflects the progressive navigation state; old Meshes highlight is cleared when Sculpt or another family is selected.',
        'Top specific-mode bar repositions inside the viewport beneath the existing transform toolbar once a tool is selected, without overlapping canvas controls.',
        'Mobile desktop-site and compact layouts both use actual toolbar geometry rather than coarse-pointer detection to place flyouts.',
        'Original operation selection, vertex center, Undo, ring, native mesh editing, transform bar, UV and VR controls remain unchanged.',
        'Automated release and browser checks do not replace physical Moto and Quest acceptance testing.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
