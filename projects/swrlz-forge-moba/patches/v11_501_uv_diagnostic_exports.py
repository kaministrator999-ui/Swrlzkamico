"""§E v11.501: center-aware read-only UV stretch and mapped-texture PNG diagnostics."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_501_UV_DIAGNOSTIC_EXPORTS'

def once(text, before, after):
    count=text.count(before)
    if count != 1:
        raise AssertionError(('v11.501 patch anchor', before[:100], count))
    return text.replace(before, after, 1)

def apply(html):
    for name in (
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_500_CONNECTED_RIG_WEIGHTS',
        'SE469_UV_SHAPE_FIT_START', 'function se336SelectedMesh()',
        'function se356UVRender()', 'function se366Marker(part)',
        'function se356UVPaintImage(ctx,img,part,size)',
        'window.SWYRL_ENGINE_RIG_CONNECTED_MATH_500',
        '  function ensurePanel(){',
    ):
        assert name in html, ('v11.501 missing inherited source', name)
    code=(ROOT/'runtime/model_uv_heatmap_export_v11_501.js').read_text('utf8')
    style=(ROOT/'runtime/model_uv_heatmap_export_v11_501.css').read_text('utf8')
    assert 'SE501_UV_HEATMAP_EXPORT_START' in code
    assert 'SE501_UV_HEATMAP_EXPORT_STYLES_START' in style
    html=once(html,'  function ensurePanel(){',code+'\n  function ensurePanel(){')
    assert '</head>' in html
    html=html.replace('</head>','<style id="se501UVDiagnosticsStyles">\n'+style+'\n</style>\n</head>',1)
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_500_CONNECTED_RIG_WEIGHTS',MARKER),
        ('ENGINE · MAKER v11.500','ENGINE · MAKER v11.501'),
        ('v11.500 · connected bone editing and real weight visualization',
         'v11.501 · center-aware UV heatmap and texture overlay exports'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.500'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.501'"),
        ('<title>§wyrl§ Engine · Maker v11.500</title>',
         '<title>§wyrl§ Engine · Maker v11.501</title>'),
    ):
        html=once(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.500';source.version=11.500;"
    assert html.count(old)==5,('v11.501 model provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.501';source.version=11.501;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.500']
    notes['history'].insert(0,{'version':'v11.500','changes':notes.get('changes',[])})
    notes.update(version='v11.501',date='2026-11-17',
      title='UV stretch PNG diagnostics with current texture overlay and selected center',
      changes=[
        'Export separate full-resolution UV stretch heatmap and aligned current painted texture plus distortion overlay PNGs in the existing UV Editor.',
        'Both outputs use the true selected mesh UVs and current image offset/repeat, with the tapped or saved UV center, authored rotation and scale when applicable.',
        'Optional center-framed view and heat opacity controls affect diagnostic previews and exports only; never move mesh vertices, UVs or texture pixels.',
        'Exports label sampled-triangle coverage; heat colors measure geometric distortion rather than falsely claiming automatic artwork misalignment detection.',
        'PNG resolutions 1024/2048/4096 and async image loading preserve original texture resolution; the existing editor, UV slide, rigging, animation and saved projects remain intact.',
        'Automated source checks and unit tests do not replace owner Moto/Quest acceptance.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
