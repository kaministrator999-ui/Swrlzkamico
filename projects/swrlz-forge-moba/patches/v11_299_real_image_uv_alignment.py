"""§E v11.299: correct the owner-confirmed broken v11.298 illustrated UV tiling.

Original artist-image bytes and model mesh history are preserved. Crop the
painted surfaces out of those bytes, restore actual local UVs, keep a neutral
back of head, and exclude empty presentation sheet backgrounds.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_299_REAL_IMAGE_UV_ALIGNMENT'

def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.299',label,n,old[:120]))
    return s.replace(old,new,1)

def apply(html):
    for token in (
      'function se297MakePBR(tile){',
      'const se298AtlasDataURL="data:image/jpeg;base64,',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_298_ACTUAL_IMAGE_UV_ATLAS',
      "window.SWRLZ_FORGE_BUILD={version:'v11.298'",
      '<strong>Hooded Vanguard · Real Artwork UV</strong>'
    ):
        if token not in html:raise AssertionError(('v11.299 prerequisite',token))
    js=(ROOT/'runtime/hooded_vanguard_uv_repair_v11_299.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'install actual-pixel surface crop/local UV repair')
    html=once(html,
      '<strong>Hooded Vanguard · Real Artwork UV</strong>',
      '<strong>Hooded Vanguard · Corrected Artwork UV</strong>',
      'corrected starter card')
    html=once(html,
      'Image-backed Hooded Vanguard: real pixels cropped from the generated concept-art texture sheet and UV-tiled across 17 editable native meshes (face, hair, hood, scarf, plate armor, cloth, coat, gloves and boots). Not procedural imitation. Static; no bird or weapon.',
      'Corrected image-backed Hooded Vanguard: original concept-art pixels separated into actual painted surfaces, aligned to each native mesh local UV instead of stretching entire illustrated cutouts. Front-only facial painting, no paper backgrounds. Static; no bird or weapon.',
      'correct project description')
    old=" source.engine='§wyrl§ Engine · Maker v11.298';source.version=11.298;"
    if html.count(old)!=3:raise AssertionError(('v11.299 native version count',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.299';source.version=11.299;")
    for a,b in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_298_ACTUAL_IMAGE_UV_ATLAS',MARKER),
      ('ENGINE · MAKER v11.298','ENGINE · MAKER v11.299'),
      ('v11.298 · actual generated artwork UV mapping','v11.299 · source-image material UV alignment'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.298'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.299'"),
      ('<title>§wyrl§ Engine · Maker v11.298</title>',
       '<title>§wyrl§ Engine · Maker v11.299</title>')
    ):html=once(html,a,b,'source build identity')
    anchor='const SE_RELEASE_NOTES='
    at=html.index(anchor)+len(anchor)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard: remove stretched source images and repair UV alignment',
      date='2026-11-06',changes=[
       'Repair owner-confirmed v11.298 mobile screenshots: illustrated clothing/face cut-outs were stretched all over the model because whole 128px concept-sheet tiles were mapped onto each mesh.',
       'Use the actual previously sealed reference-image pixels, not a new generated imitation. Extract tighter material surface crops at runtime from the existing JPEG and remove paper background from dark surfaces.',
       'Restore original part-local UVs by precisely inverting v11.298 mosaic transforms. Provide per-material CanvasTexture maps rather than sampling eleven full illustrated cut-outs from one page.',
       'Map the photographed/painted front face only onto frontal head UVs, feathering to neutral skin on sides and back instead of copying face art across the whole head circumference.',
       'Preserve 17 editable native mesh geometries, the model loader, historical patches, saved user projects, other model/game starters, Chat, VR and Sheep Tag. Owner Android/Quest acceptance is still pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
