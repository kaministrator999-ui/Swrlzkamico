"""§E v11.357: restore the simple native wireframe → image → UV Slide workflow."""
import json

MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_357_UV_GUIDE_FIRST'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.357',label,count,old[:100]))
    return html.replace(old,new,1)

def apply(html):
    for needle in (
        "se356UVMode='guide'",
        "Export UV wireframe",
        "Import painted image",
        "Advanced UV references (optional)",
        "window.SWYRLZ_E_MODEL_UV_SLIDE=Object.freeze",
        "se355UVEditorOpen",
        "function se336UVLayout(mesh, canvas)",
        "function se336ImportPaint(file)",
        "data-se320-history=\"undo\"",
    ):
        if needle not in html:
            raise AssertionError(('v11.357 missing native UV workflow',needle))
    for old,new,label in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_356_UV_PREVIEW_VR_CAMERA_ORBIT',MARKER,'deploy marker'),
      ('ENGINE · MAKER v11.356','ENGINE · MAKER v11.357','visible build'),
      ('v11.356 · precise UV preview and XR camera orbit',
       'v11.357 · wireframe-first UV import and export','headline'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.356'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.357'",'runtime build'),
      ('<title>§wyrl§ Engine · Maker v11.356</title>',
       '<title>§wyrl§ Engine · Maker v11.357</title>','title'),
    ]:
        html=once(html,old,new,label)
    old=" source.engine='§wyrl§ Engine · Maker v11.356';source.version=11.356;"
    assert html.count(old)==3,('v11.357 provenance',html.count(old))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.357';source.version=11.357;")
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    if not any(h.get('version')=='v11.356' for h in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.356','changes':notes.get('changes',[])})
    notes.update(version='v11.357',date='2026-11-08',
      title='UV mapping simplified: wireframe first',
      changes=[
        'The selected-mesh UV Editor now opens on its exact wireframe, matching the exported PNG by default.',
        'Export UV wireframe and Import painted image are primary controls; optional surface-direction and JSON references are tucked under Advanced UV references.',
        'Paint any detailed character illustration directly; align it with UV Slide on the mesh without moving the geometry.',
        'Original per-mesh UV coordinates, painted textures, save-size handling, cyan guide cleanup, Undo/Redo, and the latest VR/editor tools are preserved.',
        'Additional UV projection or texture-baking steps are not required for this normal paint/import workflow.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
