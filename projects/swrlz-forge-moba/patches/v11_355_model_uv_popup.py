"""§E v11.355: UV tool window, native controls relocated intact."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_355_MODEL_UV_POPUP'

def once(html,old,new):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.355 anchor',old[:100],count))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/model_studio_uv_popup_v11_355.js').read_text('utf8')
    css=(ROOT/'runtime/model_studio_uv_popup_v11_355.css').read_text('utf8')
    for needle in [
        "single.parentElement!==host)host.append(single)",
        "repair.parentElement!==host)host.append(repair)",
        "id='se355UVEditorOpen'",
        "id='se355UVPopup'",
        "q('#se320ModelTransform .se320-transform-uv',panel)?.remove()",
        "window.SWYRLZ_E_UV_POPUP=Object.freeze",
        "slideApi()?.toggle?.()", "data-se355-section",
        "aria-modal','false'"
    ]:
        if needle not in js:raise AssertionError(('v11.355 UV UI integration',needle))
    for needle in [
        "se336InstallUI()", "se345AtlasInstall()",
        'data-se320-history="undo"', 'data-se320-history="redo"',
        'window.SWYRLZ_E_MODEL_UV_SLIDE=Object.freeze'
    ]:
        if needle not in html:raise AssertionError(('v11.355 native editor linkage',needle))
    html=once(html,'</head>','<style id="se355ModelUVPopupStyle">\n'+css+'\n</style>\n</head>')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_354_MODEL_UV_SLIDE_HISTORY',MARKER),
        ('ENGINE · MAKER v11.354','ENGINE · MAKER v11.355'),
        ('v11.354 · on-model UV texture slide and viewport history',
         'v11.355 · separate Model Studio UV editor popup'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.354'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.355'"),
        ('<title>§wyrl§ Engine · Maker v11.354</title>',
         '<title>§wyrl§ Engine · Maker v11.355</title>')
    ]:
        html=once(html,old,new)
    old=" source.engine='§wyrl§ Engine · Maker v11.354';source.version=11.354;"
    assert html.count(old)==3
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.355';source.version=11.355;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.354' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.354','changes':notes.get('changes',[])})
    notes.update(version='v11.355',date='2026-11-08',
        title='Model Studio independent UV Editor window',
        changes=[
          'The permanent UV Editor button in the Model Studio top header opens a separate, movable, scrollable UV window, even with the inspector collapsed.',
          'Move original selected-mesh UV guide, surface-direction export, mapping JSON, painted texture import/removal and whole-model atlas DOM into the popup; retain native event listeners, project mappings and history.',
          'UV Slide, fine U/V nudges and reset live in the same UV editor popup; remove the duplicate UV Slide row from the transform viewport toolbar while preserving Undo/Redo and transform tools.',
          'Selected mesh and whole-model atlas are reachable through compact tabs; Close/Escape hides only the popup. Pop-up controls work without taking over the 3D viewport.',
          'Responsive window sizing and optional desktop drag keep buttons reachable on phones, browsers and Quest. No changes to saved models, UV coordinates, rigging or other studios.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
