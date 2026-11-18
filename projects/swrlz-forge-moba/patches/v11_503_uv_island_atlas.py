"""§E v11.503: opt-in real UV seam duplication, front/back island projection and packing."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_503_UV_ISLAND_ATLAS'
def once(src,old,new):
    count=src.count(old)
    if count!=1:
        raise AssertionError(('v11.503 source anchor',old[:100],count))
    return src.replace(old,new,1)
def apply(html):
    for name in ('SWYRL_ENGINE_DEPLOY_MARKER: V11_502_UV_TOUCH_RESIZE',
                 'SE502_UV_TOUCH_RESIZE_START','SE501_UV_HEATMAP_EXPORT_START',
                 'function se336SelectedMesh()','function se356UVInstallPreview()',
                 'function se366Marker(part)','const se469Math=',
                 'function atelierTopologyValid(part)', '  function ensurePanel(){'):
        if name=='const se469Math=':
            # the deployed source names this pure helper se469Math.
            pass
        assert name in html, ('v11.503 missing required UV source',name)
    code=(ROOT/'runtime/model_uv_island_math_v11_503.js').read_text('utf8')+'\n'+(
         ROOT/'runtime/model_uv_island_ui_v11_503.js').read_text('utf8')
    style=(ROOT/'runtime/model_uv_island_v11_503.css').read_text('utf8')
    assert 'SE503_UV_ISLAND_MATH_START' in code
    assert 'SE503_UV_ISLAND_UI_END' in code
    html=once(html,'  function ensurePanel(){',code+'\n  function ensurePanel(){')
    html=once(html,'</head>','<style id="se503UVAtlasStyle">\n'+style+'\n</style>\n</head>')
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_502_UV_TOUCH_RESIZE',MARKER),
        ('ENGINE · MAKER v11.502','ENGINE · MAKER v11.503'),
        ('v11.502 · resizable mobile UV Editor with Max/Restore',
         'v11.503 · native UV seam and front/back island atlas'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.502'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.503'"),
        ('<title>§wyrl§ Engine · Maker v11.502</title>',
         '<title>§wyrl§ Engine · Maker v11.503</title>'),
    ):
        html=once(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.502';source.version=11.502;"
    assert html.count(old)==5,('v11.503 project origin tags',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.503';source.version=11.503;")
    key='const SE_RELEASE_NOTES='
    start=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[start:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.502']
    notes['history'].insert(0,{'version':'v11.502','changes':notes.get('changes',[])})
    notes.update(version='v11.503',date='2026-11-17',
       title='Experimental front/back seam-aware UV islands with bounded transforms',
       changes=[
         'Preview a four-region front/back/brim/underside UV atlas on a single indexed editable mesh, or select a two-panel variant.',
         'Create actual new UV coordinates by duplicating seam vertices only; 3D mesh positions and triangle count are unchanged.',
         'Per-island UV rotation, scaling and offsets are constrained within separate padded atlas rectangles.',
         'Export a 2048px candidate painting guide, inspect per-island triangle counts and collapsed UV faces, and apply with one Undo checkpoint.',
         'Existing painted PNGs are detached on apply because old artwork cannot safely map to new UVs; original UVs and paint remain in Undo and project revisions.',
         'This is a projection-based beta, not a general guaranteed overlap-free unwrap of folded geometry; inspect the candidate before painting.',
         'New tool is additive in the UV Editor; existing heatmaps, UV Slide, Rigging and Animation remain separate.'
       ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[start+width:]
