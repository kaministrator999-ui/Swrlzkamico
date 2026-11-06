"""§E v11.302: native-UV PBR relief after the v11.301 face/wrist repair.

Append only. New Hooded Vanguard starter scene uses matching normal/roughness
in addition to its deliberate painted texture sheets. Other starters, saved
models, version lineage and engine editor behavior stay unchanged.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_302_MAPPED_PBR_SURFACE_RELIEF'
def once(html,a,b,label):
    n=html.count(a)
    if n!=1:raise AssertionError(('v11.302',label,n,a[:120]))
    return html.replace(a,b,1)
def apply(html):
    for token in (
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_301_VANGUARD_FACE_PAINT_HAND_ALIGNMENT',
      "window.SWRLZ_FORGE_BUILD={version:'v11.301'",
      '<strong>Hooded Vanguard · Styled Face & Neutral Hands</strong>',
      'se300DrawArtwork=function(_reference,family,canvas){'
    ):
        if token not in html:raise AssertionError(('v11.302 prerequisite',token))
    js=(ROOT/'runtime/hooded_vanguard_uv_pbr_v11_302.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
       'install lightweight shape-aligned PBR surface maps')
    html=once(html,'<strong>Hooded Vanguard · Styled Face & Neutral Hands</strong>',
       '<strong>Hooded Vanguard · Painted PBR Study</strong>',
       'Starter Models card title')
    html=once(html,
       'Stylized hooded knight with refitted rounded face, UV-positioned painted eyes/nose/lips, eleven purpose-painted game material maps instead of cut-and-paste images, reshaped shield breastplate and wrist-aligned five-digit hands. 17 native editable parts; static, no bird or weapon.',
       'Stylized knight with authored UV color painting plus tangent-space normal and grayscale roughness maps aligned to hood/scarf folds, hair grain, armor engravings, teal coat, gloves, leather and boots. Refined face and forearm-aligned hands retained. 17 editable meshes; static.',
       'Starter Models card description')
    old=" source.engine='§wyrl§ Engine · Maker v11.301';source.version=11.301;"
    if html.count(old)!=3:raise AssertionError(('v11.302 native save identity',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.302';source.version=11.302;")
    for a,b in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_301_VANGUARD_FACE_PAINT_HAND_ALIGNMENT',MARKER),
      ('ENGINE · MAKER v11.301','ENGINE · MAKER v11.302'),
      ('v11.301 · styled facial UVs, material painting and neutral wrists',
       'v11.302 · aligned sculpted material normal and roughness maps'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.301'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.302'"),
      ('<title>§wyrl§ Engine · Maker v11.301</title>',
       '<title>§wyrl§ Engine · Maker v11.302</title>')
    ):html=once(html,a,b,'release identity')
    anchor='const SE_RELEASE_NOTES='
    at=html.index(anchor)+len(anchor)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard: painted UV maps with matched normal and roughness relief',
      date='2026-11-06',changes=[
       'Continue the owner-approved rapid visual refinement loop from v11.301 without changing unrelated editor/game/VR systems or historical Starter Models/saved projects.',
       'Retain reconstructed geometry, corrected sculpted face, naturally angled five-finger hands, shield breastplate and eleven purpose-designed, native UV-aligned painted color atlases.',
       'Add 256px cached tangent-space normal maps with deliberately drawn seam, fold, engraved plate, hair strand and leather relief; normal intensity is conservative per material and avoids sculpting fake human anatomy.',
       'Add matching linear grayscale roughness maps with material-specific response and subtle micro-grain; metallic panels stay distinct from fabric and skin. Draw no image photographs, whole concept sheets or collage tiles.',
       'Generate only eleven cached PBR map sets for the eleven existing surface families: no new meshes, extra textures from arbitrary sources or expensive full-resolution bake. Mobile/Quest performance and real-world appearance acceptance are owner tests.',
       'Verify source and native map assignments separately from visual quality, preserve previous successful v11.301 face/hand fixes, §C chat, Sheep Tag and VR behavior.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
