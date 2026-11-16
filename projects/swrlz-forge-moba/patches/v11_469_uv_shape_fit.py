"""§E v11.469: transform-aware UV stretch overlay and reversible texture shape-fit."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_469_UV_SHAPE_FIT'

def once(src,old,new):
    count=src.count(old)
    assert count==1,('v11.469 unique insertion',old[:120],count)
    return src.replace(old,new,1)

def apply(html):
    for token in (
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_468_STANDALONE_STUDIO_ASSETS',
        'function se336SelectedMesh()',
        'function se356UVRender()',
        'function se356UVInstallPreview()',
        'window.SWYRLZ_E_UV_POPUP=Object.freeze',
        'SE468_STANDALONE_STUDIO_ASSETS_START',
        '  function ensurePanel(){',
    ):
        assert token in html,('missing previous runtime anchor',token)
    math=(ROOT/'runtime/model_uv_distortion_math_v11_469.js').read_text('utf8')
    ui=(ROOT/'runtime/model_uv_shape_fit_v11_469.js').read_text('utf8')
    css=(ROOT/'runtime/model_uv_shape_fit_v11_469.css').read_text('utf8')
    html=once(html,'  function ensurePanel(){',math+'\n'+ui+'\n  function ensurePanel(){')
    html=once(html,'</head>','<style id="se469UVShapeFitStyles">\n'+css+'\n</style>\n</head>')
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_468_STANDALONE_STUDIO_ASSETS',MARKER),
        ('ENGINE · MAKER v11.468','ENGINE · MAKER v11.469'),
        ('v11.468 · standalone model and particle assets','v11.469 · UV stretch diagnostic and shape-fit'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.468'","window.SWRLZ_FORGE_BUILD={version:'v11.469'"),
        ('<title>§wyrl§ Engine · Maker v11.468</title>',
         '<title>§wyrl§ Engine · Maker v11.469</title>'),
    ):
        html=once(html,old,new)
    prior=" source.engine='§wyrl§ Engine · Maker v11.468';source.version=11.468;"
    assert html.count(prior)==5,('model provenance',html.count(prior))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.469';source.version=11.469;")
    key='const SE_RELEASE_NOTES='
    start=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[start:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.468']
    notes['history'].insert(0,{'version':'v11.468','changes':notes.get('changes',[])})
    notes.update(version='v11.469',date='2026-11-15',
        title='UV stretch heatmap and non-destructive shape-aware texture fitting',
        changes=[
            'Selected procedural and indexed meshes show sampled, world-space per-triangle UV anisotropy as an opt-in color heatmap in the existing UV Editor.',
            'Shape-fit previews a transform-aware U/V sampling correction for imported paintings, including flattened spheres. A selected UV pin anchors an artwork point when provided.',
            'Preview, Cancel, Apply, Reset and native Undo protect mesh topology and painted PNG bytes; applied per-mesh sampling scale is saved with the model.',
            'Texture repeat and UV Slide offset work together; normal mesh transforms and game-studio projects retain their existing behavior.',
            'A global correction may crop or repeat portions of an atlas and cannot fix inaccurate artwork-to-island alignment; preview before applying.',
            'Automated source checks do not substitute for Moto or Quest owner acceptance.'
        ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[start+width:]
