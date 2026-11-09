"""§E v11.364 — calibrated UV Slide image export and correction metadata."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_364_UV_ALIGNMENT_EXPORT'

def once(s,old,new,label):
    found=s.count(old)
    if found!=1:
        raise AssertionError(('v11.364',label,found,old[:110]))
    return s.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/model_uv_aligned_export_v11_364.js').read_text('utf8')
    assert 'se364DrawAlignedPaint' in js and 'se364InstallControls' in js
    html=once(html,'  function ensurePanel(){',
      js+'\n  function ensurePanel(){','inside native Model Atelier closure')
    for old,new,label in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_363_WEBXR_STARTER_SOCKET_FIX',MARKER,'marker'),
      ('ENGINE · MAKER v11.363','ENGINE · MAKER v11.364','visible version'),
      ('v11.363 · WebXR hand and controller starter open repair',
       'v11.364 · export corrected UV placement','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.363'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.364'",'runtime version'),
      ('<title>§wyrl§ Engine · Maker v11.363</title>',
       '<title>§wyrl§ Engine · Maker v11.364</title>','title')
    ]:
        html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.363';source.version=11.363;"
    found=html.count(old)
    if found!=5:raise AssertionError(('v11.364 provenance',found))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.364';source.version=11.364;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,length=json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version')=='v11.363' for item in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.363','changes':notes.get('changes',[])})
    notes.update(version='v11.364',date='2026-11-08',
        title='Model Studio UV Slide corrected image export',
        changes=[
         'Model Studio UV Editor now provides a Save aligned PNG action once a painted mesh is selected.',
         'Export correction JSON records exact UV Slide offsets, pixel-shift convention, mesh identity and coordinate references.',
         'The aligned PNG bakes RepeatWrapping texture displacement and can be imported with offset 0,0 on the same UV layout.',
         'Save Project continues to retain the original painted source and live UV Slide offset; geometry and UV attributes are unchanged.',
         'Existing UV wireframe, surface-direction exports, viewport controls, undo/redo and Model VR remain intact.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+length:]
