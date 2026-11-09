"""§E v11.366 · exact mesh UV authoring marker, orientation and inverse paint mapping."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_366_UV_AUTHORING_MARKER'

def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.366',label,n,old[:110]))
    return s.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/model_uv_art_marker_v11_366.js').read_text('utf8')
    css=(ROOT/'runtime/model_uv_art_marker_v11_366.css').read_text('utf8')
    required=[
        'function se366NativeToArt(u,v,m)',
        'function se366ArtToNative(x,y,m)',
        'function se366AuthorGuide(canvas,mesh,marker)',
        'function se366BakeArtwork(canvas,image,marker)',
        'function se366ImportAuthored(file)',
        'function se366UseMeshPoint(event)',
        'function se366UseUVPoint(event)',
        'function se366DrawMarker(ctx,size,marker)',
        'window.SWYRLZ_E_UV_ART_MARKER=Object.freeze',
        "const se366BaseCheckPart=checkPart;"
    ]
    for item in required:
        if item not in js:raise AssertionError(('v11.366 missing marker logic',item))
    for existing in [
        'function se336UVLayout(mesh, canvas)',
        'function se336ImportPaint(file)',
        'function se356UVPick3D(event)',
        'function se356UVRender()',
        'function se364DrawAlignedPaint(canvas, image, offset)',
        'window.SWYRLZ_E_UV_POPUP=Object.freeze',
        "window.SWYRLZ_E_MODEL_UV_SLIDE=Object.freeze",
        'data-se320-history="undo"'
    ]:
        if existing not in html:raise AssertionError(('v11.366 missing original UV flow',existing))
    html=once(html,'  function ensurePanel(){',
        js+'\n  function ensurePanel(){','inside same native Model Atelier closure')
    assert html.index('</head>')<html.index('<body'), 'v11.366 real document header'
    html=html.replace('</head>',
        '<style id="se366UVArtMarkerStyle">\n'+css+'\n</style>\n</head>',1)
    # Expose a successful native import result for the optional marker import.
    # Without this, a reimport of identical pixels could leave the old UV slide active.
    success="        (cleanedGuidePixels ? ' Cyan UV guide lines automatically cleaned.' : '') + ' Save Project to keep it.');"
    html=once(html,success,success+'\n      return true;','native importer success signal')
    old='  if(se356UVPin?.id===target.part.id)se356UVDrawPin(ctx,canvas,se356UVPin.u,se356UVPin.v);'
    new=(old+'\n  const se366Overlay=document.getElementById("se366MarkerTools");\n'
        '  if(se366Overlay?.open)se366DrawMarker(ctx,size,se366Marker(target.part));')
    html=once(html,old,new,'draw marker on native UV preview when expanded')
    for before,after,label in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_365_HAND_REFERENCE_FIT',MARKER,'marker'),
        ('ENGINE · MAKER v11.365','ENGINE · MAKER v11.366','visible version'),
        ('v11.365 · WebXR anatomy fit for stone hand starters',
         'v11.366 · UV authoring alignment marker','headline'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.365'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.366'",'build'),
        ('<title>§wyrl§ Engine · Maker v11.365</title>',
         '<title>§wyrl§ Engine · Maker v11.366</title>','title')
    ]:
        html=once(html,before,after,label)
    prev=" source.engine='§wyrl§ Engine · Maker v11.365';source.version=11.365;"
    count=html.count(prev)
    if count!=5:raise AssertionError(('v11.366 scene version',count))
    html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.366';source.version=11.366;")
    start=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    note,length=json.JSONDecoder().raw_decode(html[start:])
    if not any(x.get('version')=='v11.365' for x in note.get('history',[])):
        note.setdefault('history',[]).insert(0,{'version':'v11.365','changes':note.get('changes',[])})
    note.update(version='v11.366',date='2026-11-08',
      title='Mesh-linked UV marker and rotated authoring guide',
      changes=[
        'Optional UV marker tools live inside the existing scrollable Model Studio UV Editor, not a new editor or floating toolbar.',
        'Tap the selected model surface or UV image preview to place an accurate image center marker on that mesh.',
        'Rotate the authoring guide ±180 degrees and scale 0.5–2x; position, rotation, and scale persist on each mesh in original project JSON with native Undo/Redo.',
        'Export a transparent UV wireframe guide shifted/rotated around the marker and a compact JSON correspondence profile for artwork creation.',
        'Import artwork authored against that marked guide: inverse affine reprojection bakes pixels onto the existing UV coordinates and resets the old UV Slide offset in the same Undo operation.',
        'Existing freeform image import, UV Slide, aligned PNG export, 5 MB import and cyan guide cleanup remain available; no change to geometry/UV attributes.',
        'Preserve Model VR gestures, current hand starters, game editor and material studio. On-device mapping quality remains owner acceptance.'
      ])
    return html[:start]+json.dumps(note,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+length:]
