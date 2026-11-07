"""§E v11.305: owner-requested complete Vanguard geometry + native UV rebuild.

Build each part's mesh and matching UVs in one factory. Preserve existing
17 part IDs, strongly improved armor proportions, head portrait and materials,
and all unrelated files, features and saved projects.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_305_VANGUARD_COMPLETE_MESH_UV'

def once(s,old,new,label):
    count=s.count(old)
    if count!=1:raise AssertionError(('v11.305',label,count,old[:110]))
    return s.replace(old,new,1)

def apply(html):
    for token in (
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_304_MODELER_DOCUMENT_VIEW_SYNC',
        "window.SWRLZ_FORGE_BUILD={version:'v11.304'",
        '<strong>Hooded Vanguard · Anatomical Face Study</strong>',
        'SE304_MODELER_DOCUMENT_VIEW_SYNC_START',
        'function se303HeadSurface(t,v){',
        'function se300Ribbon(rows,cols,fn,uvFn){'
    ):
        if token not in html:raise AssertionError(('v11.305 missing source prerequisite',token))
    js=(ROOT/'runtime/hooded_vanguard_full_mesh_uv_v11_305.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'insert new whole model surface/UV factory')
    html=once(html,
       '<strong>Hooded Vanguard · Anatomical Face Study</strong>',
       '<strong>Hooded Vanguard · Whole Mesh &amp; UV Reconstruction</strong>',
       'starter model title')
    html=once(html,
       'Hooded knight with rebuilt anatomical face topology: sculpted brow and eye sockets, eyelids, bridge/alar nose, cheekbones, lips and chin; 768px aligned facial UV portrait, reshaped hairline and brow-clear fringe. Keep styled armor, shoulders, natural hands, eleven painted material families. 17 editable static parts.',
       'Full character geometry and native UV rebuild: radial torso and sleeves with correct rear seams, refitted open hood and layered scarf, shaped ears, original fitted armor with added thickness, two-sided teal coat, formed belt/buckle, realistic forearm-aligned five-finger hands and shaped boots. Matches the existing painted skin, textile and metal UV materials. 17 editable parts, static model.',
       'starter description')
    old=" source.engine='§wyrl§ Engine · Maker v11.304';source.version=11.304;"
    if html.count(old)!=3:raise AssertionError(('v11.305 version count',html.count(old)))
    html=html.replace(old,
     " source.engine='§wyrl§ Engine · Maker v11.305';source.version=11.305;")
    for old,new in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_304_MODELER_DOCUMENT_VIEW_SYNC',MARKER),
        ('ENGINE · MAKER v11.304','ENGINE · MAKER v11.305'),
        ('v11.304 · loaded models refresh the existing viewport',
         'v11.305 · simultaneous full character mesh and UV sculpt'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.304'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.305'"),
        ('<title>§wyrl§ Engine · Maker v11.304</title>',
         '<title>§wyrl§ Engine · Maker v11.305</title>')
    ):html=once(html,old,new,'release identity')
    marker='const SE_RELEASE_NOTES='
    at=html.index(marker)+len(marker)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard: full native geometry and matched UV rebuild',
     date='2026-11-06',changes=[
       'Owner-directed whole-model reconstruction, not a further cosmetic texture-only patch: make physical mesh structure support native UVs and styled painted material layouts.',
       'Replace the old planar body atlas projection with actual front/side/back radial torso, upper/lower arm and trouser surfaces, seams at the back and separate cloth-flow UVs for sleeves and legs.',
       'Preserve detailed v11.303 head/face atlas and hair, while replacing lump ears with layered ear cartilage surfaces using lateral skin UV space.',
       'Refit the cloth hood as an open canopy, rear shoulder mantle and carefully aligned aperture binding; replace stiff neck/chest scarf with gathered neck folds and two overlapping, volume-contoured chest cloth strips.',
       'Keep the owner-approved fitted breastplate/pauldron outlines, adding a real back layer for thickness instead of changing the successful armor silhouette or piling decorative pieces over it.',
       'Give teal coat tails coherent front/back cloth surfaces with draped folds and consistent hem UVs. Add curved leather belt with an aligned formed buckle, fitted rounded boots with actual toes.',
       'Replace awkward rotated vertical glove geometry: construct palm, four independently tapered fingers, thumb and cuff along the actual forearm direction, with radial UVs generated from the same hand geometry; no unnatural broken wrist.',
       'All 17 existing native editable part IDs retained, no new scene dependencies or changes to stored projects, §C, VR, Sheep Tag or unrelated starters. Reuse 11 stylized albedo/normal/roughness material families. No full body rig, bird or weapon.',
       'Focused geometry/UV regression and source seal validate the implementation, but real Android/Quest visual acceptance remains with the owner.'
     ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
