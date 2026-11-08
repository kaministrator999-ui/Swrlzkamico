"""§E v11.334: owner hand photo silhouette; dorsal crystal knuckles cannot ghost onto palm."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_334_PHOTO_DORSAL_CRYSTALS'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.334',label,count,old[:100]))
    return html.replace(old,new,1)

def apply(html):
    source=(ROOT/'runtime/cliff_hand_photo_crystal_v11_334.js').read_text('utf8')
    assert 'function se334ReferenceHandField(math){' in source
    assert 'function se334DorsalOnlyCrystalMaterial(mat){' in source
    assert 'function se334PaintCrystal(ctx,k){' in source
    html=once(html,'window.SWRLZ_FORGE_BUILD=',source+'\nwindow.SWRLZ_FORGE_BUILD=',
              'register isolated photo and crystal texture implementation')
    # This field is called only for the Smooth Cliff Hand SDF generation.
    # Other hands, wolves, Sheep Tag and saved-project pipelines stay identical.
    html=once(html,
      ' const hand=se217OrganicHandSkin(se217FingerSpec,math);',
      ' const hand=se334ReferenceHandField(math);',
      'apply subtle user-photo contour only to cliff gauntlet field')
    # The previous shared 384px albedo/normal/AO stamps hit the palm because
    # front AND back of the same mesh have the same planar UV. Keep the
    # original cracks and wrist moss, but REMOVE those shared knuckle stamps.
    html=once(html,
      ' se292DrawKnuckleColor(albedo);',
      ' // v11.334: no knuckle plate or crystal paint on shared palm/dorsal UVs.',
      'remove knuckle geometry illusion from palmar rock color')
    html=once(html,
      " for(const type of ['normal','ao'])se292DrawKnuckleRelief(at(type).ctx,type);",
      ' // v11.334: do not emboss dorsal knuckle relief into shared palmar normal/AO.',
      'remove overlaid knuckle contours from palm-side normal and AO')
    # Composite faceted teal/cyan crystal texture only where the unposed mesh
    # normal faces dorsal (negative Z). Native skinning still transforms it.
    html=once(html,
      " mat.name='Cliff Hand · clean sandstone / relief knuckles / wrist-only moss';\n return mat;",
      ' return se334DorsalOnlyCrystalMaterial(mat);',
      'attach dorsal-only crystal sampler to native MeshStandardMaterial')
    old=" source.engine='§wyrl§ Engine · Maker v11.333';source.version=11.333;"
    if html.count(old)!=3:raise AssertionError(('v11.334','scene provenance',html.count(old)))
    html=html.replace(old,
      " source.engine='§wyrl§ Engine · Maker v11.334';source.version=11.334;")
    for prior,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_333_CLIFF_EMBEDDED_ATLAS',MARKER),
      ('ENGINE · MAKER v11.333','ENGINE · MAKER v11.334'),
      ('v11.333 · original rock atlas embedded in Smooth Cliff Hand',
       'v11.334 · photo-refined hand and dorsal crystal knuckles'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.333'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.334'"),
      ('<title>§wyrl§ Engine · Maker v11.333</title>',
       '<title>§wyrl§ Engine · Maker v11.334</title>')
    ):
      html=once(html,prior,new,'release identity')
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,used=json.JSONDecoder().raw_decode(html[at:])
    if not any(v.get('version')=='v11.333' for v in notes.get('history',[])):
      notes.setdefault('history',[]).insert(0,{'version':'v11.333','changes':notes.get('changes',[])})
    notes.update(
      version='v11.334',
      title='Smooth Cliff Hand: photo-guided shape with dorsal-only teal crystal knuckles',
      date='2026-11-07',
      changes=[
        'Use the owner-provided real left-palm photograph as a shape reference for small adjustments to middle/index/ring/pinky length hierarchy, soft finger splay, metacarpal palm width and thumb pad volume; do not trace personal photo into project assets.',
        'Remove old knuckle-paint stamps from shared color, normal and ambient-occlusion texture atlases. The same front/back planar UV previously displayed fake dorsal knuckle rocks through the palm.',
        'Paint four original cyan/teal faceted crystal formations onto a reusable transparent CanvasTexture and composite in MeshStandardMaterial only when the original object-space face normal points dorsally, never onto the palm.',
        'Retain the single native editable stone and gauntlet topology mesh, four-map original rock atlas, dark fracture outlines, wrist-only moss, all 17 native skin bones/poses, and other starters untouched.',
        'Maintain source-integrity and Android browser safeguards. Owner physical-device inspection determines final appearance and whether the crystal treatment needs tuning.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+used:]
