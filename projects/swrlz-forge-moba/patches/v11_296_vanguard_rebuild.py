"""§E v11.296: owner-requested native knight reconstruction.

The v11.291 starter remains in lineage. Fresh Hooded Vanguard construction is
redirected to one redesigned anatomical/model and a proper UV texture generator.
Existing saved models, other starters and model tooling remain unchanged.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_296_VANGUARD_REBUILT'

def once(html,old,new,label):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('v11.296',label,n,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/hooded_vanguard_rebuild_v11_296.js').read_text('utf8')
    for token in (
      'function se291HeroScene(){',
      'model.parts=parts;model.meshGroups=[];model.assemblies=null;',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_295_CHAT_LOFT_SURFACE_NORMALS',
      'SE295_CHAT_LOFT_SURFACE_NORMALS_START',
      "window.SWRLZ_FORGE_BUILD={version:'v11.295'",
    ):
        if token not in html:
            raise AssertionError(('v11.296 missing prerequisite',token))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
       'install new character factory before starter is opened')
    html=once(html,
      '<strong>Hooded Vanguard · Material Study</strong>',
      '<strong>Hooded Vanguard · Rebuilt Character</strong>',
      'update starter card to correspond to actual rebuild')
    html=once(html,
      'Hooded male knight with native anatomy, shaped shoulder armor, folded scarf, teal coat tails and mapped gold engravings, cloth, leather and skin. No bird or weapon. Static editable model study.',
      'Rebuilt hooded knight: smooth fitted face, dark layered hair, curved cloth hood, sculpted scarf and armor, five-finger gloves, teal coat, UV-mapped fabric, metal, leather and skin. Static model; no bird or weapon.',
      'describe finished rebuilt model')
    old=" source.engine='§wyrl§ Engine · Maker v11.295';source.version=11.295;"
    if html.count(old)!=3:
        raise AssertionError(('v11.296 editor versions',html.count(old)))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.296';source.version=11.296;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_295_CHAT_LOFT_SURFACE_NORMALS',MARKER),
      ('ENGINE · MAKER v11.295','ENGINE · MAKER v11.296'),
      ('v11.295 · Chat loft surfaces keep their intended colors',
       'v11.296 · rebuilt hooded knight anatomy and materials'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.295'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.296'"),
      ('<title>§wyrl§ Engine · Maker v11.295</title>',
       '<title>§wyrl§ Engine · Maker v11.296</title>')
    ):
        html=once(html,old,new,'source identity')
    anchor='const SE_RELEASE_NOTES='
    at=html.index(anchor)+len(anchor)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Hooded Vanguard rebuilt: face, hair, hood, gloves and mapped materials',
      date='2026-11-06',changes=[
       'Reconstruct the Hooded Vanguard Starter Model after real-device feedback: replace separate chin and ear lumps with a continuous UV-mapped head and restrained nose; restore plausible eyes and lips using a mapped facial atlas.',
       'Build a fitted 3D hood shell with curved forward brim, layered dark hair, textured draped scarf, contoured engraved breastplate, tapered shoulder armor, teal coat panels, belt, sculpted boots and five-digit white gloves.',
       'Generate 384px tile-specific color, height-derived normal, and roughness maps for skin, hair, hood, scarf, armor, shoulder metal, cloth, teal fabric, leather, gloves and boots. Keep all artwork attached to native UV coordinates instead of adding decorative confetti meshes.',
       'Keep the original v11.291 factory source and saved model projects intact; replace only the fresh hooded-vanguard starter construction. No bird, weapon or full-body rig. Owner Android/Quest appearance acceptance remains pending.',
       'Preserve the v11.295 native Chat loft normal correction, existing Hand, Sheep Tag, Game and Particle studios and authoring history.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[at+width:]
