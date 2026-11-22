"""§E v11.544 — material placement from real 3D anatomy, not guessed UV silhouettes.

Adds a properly 3D-baked starter texture and an explicit, reversible
native UV-Editor control to repair an owner-edited mannequin's current paint.
All mesh vertices, UVs, indices and user-saved projects are untouched.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_543_TOOL_NAVIGATION_SEARCH'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_544_HUMANOID_SURFACE_PAINT'

def once(html,before,after,what):
    n=html.count(before)
    if n!=1:raise AssertionError(('se544',what,n,before[:130]))
    return html.replace(before,after,1)

def apply(html):
    starter=(ROOT/'runtime/humanoid_semantic_starter_v11_544.js').read_text('utf8')
    repair=(ROOT/'runtime/humanoid_semantic_repair_v11_544.js').read_text('utf8')
    for t in ('SE544_MAPPED_HUMANOID_STARTER_END',
              'se537OpenMannequin=se544OpenHumanoid','se544ValidateSemanticHumanoid'):
        assert t in starter,t
    for t in ('SE544_MAPPED_MANNEQUIN_REPAIR_END','se544RestoreMannequinPaint',
              'checkpoint();','se544HasOriginalUVs','signalEdited()'):
        assert t in repair,t
    # Same native ModelAtelier lexical scope as the existing UV painter so
    # checkpoint/Undo, selected mesh, and save guards stay authoritative.
    html=once(html,'  function ensurePanel(){',repair+'\n  function ensurePanel(){','native UV editor repair')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',starter+'\nwindow.SWRLZ_FORGE_BUILD=','native starter loader')
    html=once(html,
      '<strong>Futuristic Humanoid · UV-Ready Hands</strong>',
      '<strong>Futuristic Humanoid · Surface-Mapped Robot</strong>','starter label')
    html=once(html,
      '<span class="template-tag">STARTER MODEL · ONE BODY · RELAXED PAINT-READY UVS</span>',
      '<span class="template-tag">STARTER MODEL · REAL 3D-TO-UV ROBOT PAINT</span>',
      'category / source tag')
    html=once(html,
      "'robotic-humanoid-mannequin':['Futuristic Humanoid · UV-Ready Hands','model-atelier','model-atelier']",
      "'robotic-humanoid-mannequin':['Futuristic Humanoid · Surface-Mapped Robot','model-atelier','model-atelier']",
      'VR starter library label')
    for old,new in (
      (OLD,MARKER),
      ('ENGINE · MAKER v11.543','ENGINE · MAKER v11.544'),
      ('v11.543 · find tools and navigate directly to real §E panels',
       'v11.544 · anatomically mapped robot material and safe paint recovery'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.543'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.544'"),
      ('<title>§wyrl§ Engine · Maker v11.543</title>',
       '<title>§wyrl§ Engine · Maker v11.544</title>')
    ):
      html=once(html,old,new,'release identity')
    previous=" source.engine='§wyrl§ Engine · Maker v11.543';source.version=11.543;"
    assert html.count(previous)==5,('source provenance',html.count(previous))
    html=html.replace(previous,
       " source.engine='§wyrl§ Engine · Maker v11.544';source.version=11.544;")
    offset=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,length=json.JSONDecoder().raw_decode(html[offset:])
    notes['history']=[x for x in notes['history'] if x.get('version')!='v11.543']
    notes['history'].insert(0,{'version':'v11.543','changes':notes['changes']})
    notes.update(
      version='v11.544',date='2026-11-22',
      title='Futuristic Humanoid — actual 3D-anchored robotic texture',
      changes=[
       'Replaced the previous misleading freehand atlas-art workflow for the humanoid with a semantic material baker that interpolates every atlas texel from the actual welded 3D surface and outward normals. No more guessing that a visually head-shaped UV region is actually a head.',
       'Painted real front +Z head/eyes, chest +Z, back -Z/spine, arms and palms along X, and hips/legs according to native surface coordinates, with clean white ceramic armor, graphite articulation and subtle teal tech details.',
       'Kept the same continuous manifold, 13,932 triangles, 8,792 UV vertices, 84 xatlas charts and native project ID. Original v11.542 UV guide and existing owner project saves remain unchanged.',
       'A new Restore mapped robot texture action in the UV Editor updates only the selected original UV-compatible mannequin painted PNG. It confirms before replacing artwork, checkpoints Undo, and does not mutate geometry, UVs or save to the account without owner action.',
       'Published the exact new PNG and generated a color-coded body-region diagnostic atlas plus orthographic front/back/side 3D render receipts to prove image details land on true mesh anatomy.',
       'Corrected mannequin starter label and VR library title, preserved global Find tool and historical starter categories; mobile/Quest owner appearance acceptance remains separate.'
      ])
    return html[:offset]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[offset+length:]
