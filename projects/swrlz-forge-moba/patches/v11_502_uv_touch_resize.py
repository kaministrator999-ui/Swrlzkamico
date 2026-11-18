"""§E v11.502: mobile UV popup edge/corner resizing and titlebar Max/Restore."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_502_UV_TOUCH_RESIZE'

def once(html,old,new,why):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.502',why,n,old[:90]))
    return html.replace(old,new,1)

def apply(html):
    for need in (
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_501_UV_DIAGNOSTIC_EXPORTS',
      'SE473_UV_SCREEN_DRAG_START','function se473RememberWindow()',
      'function se502ToggleMax(', # no prior definition; handled below
    )[:2]:
      assert need in html,need
    assert 'function se473RememberWindow()' in html
    assert 'window.SWYRLZ_E_UV_POPUP=Object.freeze' in html
    assert 'SE501_UV_HEATMAP_EXPORT_START' in html
    assert '  function mount(){\n    const next=q(\'#modelAtelierPanel\');' in html
    js=(ROOT/'runtime/model_uv_touch_resize_v11_502.js').read_text('utf8')
    css=(ROOT/'runtime/model_uv_touch_resize_v11_502.css').read_text('utf8')
    assert 'SE502_UV_TOUCH_RESIZE_START' in js
    assert 'SE502_UV_TOUCH_RESIZE_STYLES_START' in css
    html=once(html,"  function mount(){\n    const next=q('#modelAtelierPanel');",
      js+"\n  function mount(){\n    const next=q('#modelAtelierPanel');",
      'insert UV resize adapter inside native se355 popup closure')
    html=once(html,"    popup=q('#se355UVPopup',panel)||createPopup(panel);\n    const host=q('#se355UVNativeHost',popup);",
      "    popup=q('#se355UVPopup',panel)||createPopup(panel);\n    se502InstallResizable(popup);\n    const host=q('#se355UVNativeHost',popup);",
      'install controls without rebuilding existing UV widgets')
    html=once(html,'</head>','<style id="se502UVResizeStyles">\n'+css+'\n</style>\n</head>',
      'responsive resize style')
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_501_UV_DIAGNOSTIC_EXPORTS',MARKER),
        ('ENGINE · MAKER v11.501','ENGINE · MAKER v11.502'),
        ('v11.501 · center-aware UV heatmap and texture overlay exports',
         'v11.502 · resizable mobile UV Editor with Max/Restore'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.501'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.502'"),
        ('<title>§wyrl§ Engine · Maker v11.501</title>',
         '<title>§wyrl§ Engine · Maker v11.502</title>'),
    ):
      html=once(html,old,new,'release identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.501';source.version=11.501;"
    assert html.count(old)==5,('v11.502 model provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.502';source.version=11.502;")
    marker='const SE_RELEASE_NOTES=';at=html.index(marker)+len(marker)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[h for h in notes.get('history',[]) if h.get('version')!='v11.501']
    notes['history'].insert(0,{'version':'v11.501','changes':notes.get('changes',[])})
    notes.update(version='v11.502',date='2026-11-17',
      title='Touch-resizable UV Editor window, maximize/restore and persistent sizing',
      changes=[
        'UV Editor titlebar gains a Max/Restore button; full-size mode fits the visual viewport while retaining the previous window dimensions for restoration.',
        'Eight edge/corner handles support touch, pen, mouse and keyboard arrow resizing, including left/right edges, bottom edge and bottom corners with visible resize hints.',
        'Manual resizing retains the opposite edge, clamps within the phone browser viewport and saves position and dimensions to the existing UV popup settings.',
        'Prior titlebar dragging, viewport-fit on orientation change and current scrollable UV wireframe, image, heatmap, texture and atlas controls remain intact.',
        'No change to UV coordinates, textures, geometry, rigging, animation, project data or export format. Owner device acceptance remains pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+width:]
