"""§E v11.333: self-contained original Cliff Hand atlas for mobile reliability.

The user sees the flat tan preload fallback although the hosted original atlas
is available. Remove the second network dependency from this one starter.
No artwork, UVs, model geometry, shaders, or rigging are redesigned.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_333_CLIFF_EMBEDDED_ATLAS'
ATLAS=ROOT/'assets/cliff-hand/cliff_pbr_atlas_384.jpg'
EXPECTED_SHA='fc56730c8019d8079794c7b7379c75c8c07381794104eb56a439a94588647cbe'
EXPECTED_BYTES=404577

def once(html,old,new,label):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('v11.333',label,n,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    image=ATLAS.read_bytes()
    if len(image)!=EXPECTED_BYTES or hashlib.sha256(image).hexdigest()!=EXPECTED_SHA:
        raise AssertionError('Original owner-provided Cliff Hand atlas changed unexpectedly')
    image_url='data:image/jpeg;base64,'+base64.b64encode(image).decode('ascii')
    if not image.startswith(b'\\xff\\xd8\\xff') or not image.endswith(b'\\xff\\xd9'):
        raise AssertionError('Rock atlas must remain a complete original JPEG')
    for token in (
        'function se292TextureSet(){',
        '  image.src=SE288_ATLAS;',
        'se332OverlayRockFractures(img,albedo);',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_332_CLIFF_CRACK_ATLAS',
        'window.SWRLZ_FORGE_BUILD=',
    ):
        if token not in html:
            raise AssertionError(('v11.333','missing prerequisite',token))
    # Native CanvasTexture composition remains unchanged. An inline JPEG image
    # delivers the exact same pixels without relying on browser iframe URLs,
    # network state, or a second asset request during editor startup.
    html=once(html,'function se292TextureSet(){',
        "const SE333_EMBEDDED_CLIFF_ATLAS='"+image_url+"';\n"+
        'function se292TextureSet(){',
        'inline exact original JPEG bytes ahead of PBR texture loader')
    html=once(html,'  image.src=SE288_ATLAS;',
        "  se292State.atlasSource='embedded-original-jpeg';\n"+
        '  image.src=SE333_EMBEDDED_CLIFF_ATLAS;',
        'load original atlas within current HTML instead of a remote request')

    old=" source.engine='§wyrl§ Engine · Maker v11.332';source.version=11.332;"
    if html.count(old)!=3:
        raise AssertionError(('v11.333','scene provenance',html.count(old)))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.333';source.version=11.333;")
    for prior,next_ in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_332_CLIFF_CRACK_ATLAS',MARKER),
      ('ENGINE · MAKER v11.332','ENGINE · MAKER v11.333'),
      ('v11.332 · authored rock fracture mask on Smooth Cliff Hand',
       'v11.333 · original rock atlas embedded in Smooth Cliff Hand'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.332'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.333'"),
      ('<title>§wyrl§ Engine · Maker v11.332</title>',
       '<title>§wyrl§ Engine · Maker v11.333</title>'),
    ):
        html=once(html,prior,next_,'release identity')
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,used=json.JSONDecoder().raw_decode(html[at:])
    if not any(i.get('version')=='v11.332' for i in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.332','changes':notes.get('changes',[])})
    notes.update(
      version='v11.333',
      title='Smooth Cliff Hand: load original PBR rock atlas even when external image fetch fails',
      date='2026-11-07',
      changes=[
        'A physical Android screenshot showed the original flat tan preloaded color while the independently verified v11.332 desktop and emulated-mobile browsers displayed the intended rock fractures.',
        'Verify the exact original owner 1536×768 Cliff Hand atlas JPEG by fixed byte count and SHA-256 during compilation, then embed its byte-identical data URI in the modeler source for the Smooth Cliff Hand material loader.',
        'Remove that starter’s asynchronous external JPEG network request: rock albedo, authored fracture mask, normal, roughness, AO, wrist-only moss, and four knuckle lines now derive entirely from the already loaded engine HTML.',
        'Keep native single connected stone/gauntlet topology and all 17-bone editing, posing, animation, GPU materials, UV maps and unrelated scene/studio assets unchanged.',
        'Verify the embedded bytes, browser viewport imagery and absence of external atlas requests; physical Moto/Quest visual acceptance remains separate.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+used:]
