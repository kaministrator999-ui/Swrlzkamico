"""§E v11.479 · rim-first vertex rings and front-visible material+vertex editing."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_479_RIM_VISIBLE_SIDE'

def once(html,old,new):
    count=html.count(old)
    assert count==1,('v11.479 unique source anchor',old[:130],count)
    return html.replace(old,new,1)

def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_478_RING_VERTEX_HIGHLIGHT' in html
    runtime=(ROOT/'runtime/model_ring_rim_visibility_v11_479.js').read_text('utf8')
    css=(ROOT/'runtime/model_ring_rim_visibility_v11_479.css').read_text('utf8')
    assert '/* SE479_RIM_VISIBILITY_END */' in runtime
    assert '/* SE479_RIM_VISIBILITY_STYLES_END */' in css
    # Keep all §E modeling operations in the same native component picker.
    # The existing center-based ring behavior remains behind its explicit toggle.
    html=once(html,'/* SE478_RING_HEIGHT_SLIDER_END */',
      '/* SE478_RING_HEIGHT_SLIDER_END */\n'+runtime)
    html=once(html,
      "   if(result?.ok!==false)selectRing(shape==='fill'?'fill':'outline');",
      """   if(result?.ok!==false){
     if(window.SWYRL_ENGINE_RIM_VISIBILITY_479?.inspect?.()?.centerMode)
      selectRing(shape==='fill'?'fill':'outline');
     else{
      atelierComponentIds=[];atelierComponentRefresh();
      feedback('Tap a vertex on the rim to select its connected circumference. Use Set Ring Center for center-first mode.');
     }
    }""")
    assert '</head>' in html
    html=html.replace('</head>',
      '<style id="se479RimVisibleSideStyles">\n'+css+'\n</style>\n</head>',1)
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_478_RING_VERTEX_HIGHLIGHT',MARKER),
      ('ENGINE · MAKER v11.478','ENGINE · MAKER v11.479'),
      ('v11.478 · complete vertex-ring highlighting','v11.479 · rim-first and visible-side vertex editing'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.478'","window.SWRLZ_FORGE_BUILD={version:'v11.479'"),
      ('<title>§wyrl§ Engine · Maker v11.478</title>',
       '<title>§wyrl§ Engine · Maker v11.479</title>')
    ):html=once(html,old,new)
    original=" source.engine='§wyrl§ Engine · Maker v11.478';source.version=11.478;"
    assert html.count(original)==5,('v11.479 provenance',html.count(original))
    html=html.replace(original,
      " source.engine='§wyrl§ Engine · Maker v11.479';source.version=11.479;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,size=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[item for item in notes.get('history',[]) if item.get('version')!='v11.478']
    notes['history'].insert(0,{'version':'v11.478','changes':notes.get('changes',[])})
    notes.update(version='v11.479',date='2026-11-16',
      title='Rim-first vertex selections and material-aware front-only picking',
      changes=[
       'Vertex Ring and Filled Vertex Ring interpret the tapped vertex as a point on the rim, not the center. The full topology-connected projected rim or filled radius becomes the native selected vertex group.',
       'An explicit Set Ring Center toggle retains the original center-based connected graph selection when desired.',
       'Material + Vertices offers a native shaded/material view with editable vertex highlights, without changing the material or mesh source.',
       'Visible Side Only uses real camera-to-mesh surface occlusion to exclude hidden vertices from rim group and box/lasso selections; original and highlighted vertex markers obey mesh depth.',
       'Switching to all-sides mode restores through-mesh selection; changing either view mode does not change UVs, mesh topology or Undo history.',
       'Existing Extrude/Inset height preview, Apply/Cancel, viewport camera, saved projects and VR code are preserved; device acceptance remains independent.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+size:]
