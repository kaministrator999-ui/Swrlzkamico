"""§E v11.301 — jointly fix the owner's face, painted UV and limp wrist feedback.

Only fresh Starter Models Hooded Vanguard is changed; historical geometry
patches and existing user-saved native scenes remain intact.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_301_VANGUARD_FACE_PAINT_HAND_ALIGNMENT'

def once(s,a,b,label):
    n=s.count(a)
    if n!=1:raise AssertionError(('v11.301',label,n,a[:110]))
    return s.replace(a,b,1)

def apply(html):
    for required in (
        'function se300BuildCharacter(scene){',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_300_VANGUARD_MESH_UV_COUPLED',
        "window.SWRLZ_FORGE_BUILD={version:'v11.300'",
        '<strong>Hooded Vanguard · Geometry + UV Rebuild</strong>'
    ):
        if required not in html:raise AssertionError(('v11.301 prerequisite missing',required))
    js=(ROOT/'runtime/hooded_vanguard_stylized_pose_v11_301.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
       'add face, deliberate texture maps and cuff pose repair')
    html=once(html,
       '<strong>Hooded Vanguard · Geometry + UV Rebuild</strong>',
       '<strong>Hooded Vanguard · Styled Face & Neutral Hands</strong>',
       'starter card identity')
    html=once(html,
       'New shape-matched Hooded Vanguard: rebuilt sculpted hood, layered hair, continuous face, actual draped scarf, tapered armor, curved pauldrons and two-sided flowing teal coats. Every surface has matched native UVs plus actual generated artwork details. 17 editable parts; static; no bird or weapon.',
       'Stylized hooded knight with refitted rounded face, UV-positioned painted eyes/nose/lips, eleven purpose-painted game material maps instead of cut-and-paste images, reshaped shield breastplate and wrist-aligned five-digit hands. 17 native editable parts; static, no bird or weapon.',
       'starter card description')
    old=" source.engine='§wyrl§ Engine · Maker v11.300';source.version=11.300;"
    if html.count(old)!=3:raise AssertionError(('v11.301 native version locations',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.301';source.version=11.301;")
    for a,b in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_300_VANGUARD_MESH_UV_COUPLED',MARKER),
      ('ENGINE · MAKER v11.300','ENGINE · MAKER v11.301'),
      ('v11.300 · coupled model geometry and painted UV rebuild',
       'v11.301 · styled facial UVs, material painting and neutral wrists'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.300'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.301'"),
      ('<title>§wyrl§ Engine · Maker v11.300</title>',
       '<title>§wyrl§ Engine · Maker v11.301</title>')
    ):
        html=once(html,a,b,'engine build identity')
    marker='const SE_RELEASE_NOTES='
    at=html.index(marker)+len(marker)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard: authored UV art, integrated face and neutral hand poses',
       date='2026-11-06',changes=[
        'Act on owner Android review: the face remained stretched, every texture looked like a magazine cutout, and both hands pointed vertically downward despite arms angling outward.',
        'Refine one continuous head mesh, moderately broaden the jaw, soften the nose protrusion, and create an authored front-only UV face painting with appropriately placed eyebrows, eye whites, irises, pupils, nose shading, cheeks and lips. No copied photographed face or back-of-head repetition.',
        'Replace every original-gallery crop with purpose-authored native UV atlas artwork: eleven coordinated stylized game albedo maps for skin, hair, cream hood, white scarf, charcoal uniform, engraved steel armor, curved pauldrons, teal coat, brown leather, white gloves and boots. Patterns are situated in part UV space; no pasted photograph rectangles.',
        'Preserve the 17 native editable part IDs and all existing saved projects. Improve breastplate lower outline to a tapered shield silhouette rather than an illustrated rectangle.',
        'Rotate both original five-digit hand geometries 0.64 radians about each cuff in opposite directions, following the forearms in a relaxed A-pose; reduce oversize hand length slightly without losing fingers or breaking the topology.',
        'Focused all-atlas lazy-load test verifies no missing texture maps, source-photo pastes, out-of-range topology or incorrectly oriented hand points. Owner front/three-quarter/back appearance acceptance remains pending.',
        'Do not change game starters, §C Chat, Sheep Tag, VR, rigging or historical patch lineage. Static character; no weapon/bird/full body rig.'
       ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
