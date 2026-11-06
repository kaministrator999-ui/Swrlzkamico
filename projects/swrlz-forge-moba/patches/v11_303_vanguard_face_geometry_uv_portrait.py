"""§E v11.303: actual facial topology and matching portrait UV (not dot-eyes).

Append-only character-starter override. Other 14 model parts are untouched,
including verified shoulder/chest armor, original wrist rest pose and coat.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_303_VANGUARD_ANATOMICAL_PORTRAIT'
def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.303',label,n,old[:120]))
    return s.replace(old,new,1)
def apply(html):
    for token in (
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_302_MAPPED_PBR_SURFACE_RELIEF',
      "window.SWRLZ_FORGE_BUILD={version:'v11.302'",
      '<strong>Hooded Vanguard · Painted PBR Study</strong>',
      'function se302BuildSet(family){'
    ):
        if token not in html:raise AssertionError(('v11.303 missing prerequisite',token))
    js=(ROOT/'runtime/hooded_vanguard_facial_sculpt_v11_303.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'install anatomical head and UV portrait')
    html=once(html,
      '<strong>Hooded Vanguard · Painted PBR Study</strong>',
      '<strong>Hooded Vanguard · Anatomical Face Study</strong>',
      'starter model card title')
    html=once(html,
      'Stylized knight with authored UV color painting plus tangent-space normal and grayscale roughness maps aligned to hood/scarf folds, hair grain, armor engravings, teal coat, gloves, leather and boots. Refined face and forearm-aligned hands retained. 17 editable meshes; static.',
      'Hooded knight with rebuilt anatomical face topology: sculpted brow and eye sockets, eyelids, bridge/alar nose, cheekbones, lips and chin; 768px aligned facial UV portrait, reshaped hairline and brow-clear fringe. Keep styled armor, shoulders, natural hands, eleven painted material families. 17 editable static parts.',
      'starter model card description')
    old=" source.engine='§wyrl§ Engine · Maker v11.302';source.version=11.302;"
    if html.count(old)!=3:raise AssertionError(('v11.303 project metadata',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.303';source.version=11.303;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_302_MAPPED_PBR_SURFACE_RELIEF',MARKER),
      ('ENGINE · MAKER v11.302','ENGINE · MAKER v11.303'),
      ('v11.302 · aligned sculpted material normal and roughness maps',
       'v11.303 · anatomy sculpted face with aligned high-resolution UV portrait'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.302'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.303'"),
      ('<title>§wyrl§ Engine · Maker v11.302</title>',
       '<title>§wyrl§ Engine · Maker v11.303</title>')
    ):html=once(html,old,new,'build identity')
    anchor='const SE_RELEASE_NOTES='
    at=html.index(anchor)+len(anchor)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard: sculpted anatomically detailed face and UV portrait',
      date='2026-11-06',changes=[
        'Respond to owner device critique that the face still looks like a toddler drew eyes and mouth. Previous head had a near-smooth oval plus small markings, rather than coherent anatomy or substantial portrait artwork.',
        'Rebuild face in a single UV-paired, continuous 80x144 native topology surface with physical orbital recesses, eyebrow/eyelid ridges, cheekbones, nasal bridge, nose tip and alar wings, philtrum, upper/lower lip and chin volume. No floating cartoon feature meshes.',
        'Paint facial UVs with a new cached 768px atlas for subtle skin tonal transitions, pronounced brows, clearly readable almond eyelids/eyelashes, sclera, blue-gray iris details, pupils, catchlights, sculpt-matched nose and nostrils, lips, jaw shading and cheek volume. No photo, duplicate face on rear, or cutout texture.',
        'Fit upper scalp and natural hairline to the new forehead; revise side locks and short frontal bangs to reveal eyebrows/eye detail rather than retaining the bowl haircut.',
        'Preserve the other fourteen existing editable native mesh parts and geometry, in particular successful chest/shoulders, neutral hand wrists, scarf, teal cloth, belt and boots. Retain all eleven prior purpose-painted PBR material families and per-surface normal/roughness maps.',
        'Keep other starters, §C Chat, Sheep Tag, VR, saved models and append-only patch lineage intact. No bird/weapon/full rig. Source/model checks do not substitute for owner real-device visual acceptance.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
