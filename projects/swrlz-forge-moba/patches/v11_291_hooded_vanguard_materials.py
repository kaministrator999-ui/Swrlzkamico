"""§E v11.291: native hooded armored character starter with mapped PBR surfaces."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def once(html,old,new,label):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('v11.291',label,n,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/hooded_vanguard_v11_291.js').read_text('utf8')
    for prerequisite in (
        'function se290CliffMaterial(part){',
        "mat=part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se290CliffMaterial(part):",
        "SWYRL_ENGINE_DEPLOY_MARKER: V11_290_CLIFF_GAUNTLET_LOAD_MATERIAL",
        "window.SWRLZ_FORGE_BUILD=",
        'data-project-template="floating-hand-glove"',
    ):
        if prerequisite not in html:
            raise AssertionError(('v11.291 missing prerequisite',prerequisite))
    html=once(html,"window.SWRLZ_FORGE_BUILD=",js+"\nwindow.SWRLZ_FORGE_BUILD=",
        'install native modeled character and real CanvasTexture maps')
    html=once(html,
        "mat=part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se290CliffMaterial(part):",
        "mat=part.heroPBR?se291HeroMaterial(part):part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se290CliffMaterial(part):",
        'render 2D mapped albedo/normal/roughness on actual native topology meshes')
    card=(
      '<button class="project-card den" data-project-template="hooded-vanguard">'
      '<span class="project-icon">🛡️</span><strong>Hooded Vanguard · Material Study</strong>'
      '<span class="template-tag">STARTER MODEL · MALE KNIGHT / MATERIAL-FIRST</span>'
      '<p>Hooded male knight with native anatomy, shaped shoulder armor, folded scarf, '
      'teal coat tails and mapped gold engravings, cloth, leather and skin. '
      'No bird or weapon. Static editable model study.</p>'
      '<span class="hint den-glow">Open native hooded knight study</span></button>'
    )
    html=once(html,
        '<button class="project-card den" data-project-template="floating-hand-glove">',
        card+'<button class="project-card den" data-project-template="floating-hand-glove">',
        'register in the existing Starter Models hub')
    old=" source.engine='§wyrl§ Engine · Maker v11.290';source.version=11.290;"
    n=html.count(old)
    if n!=3:raise AssertionError(('v11.291 source version occurrence count',n))
    html=html.replace(old,
        " source.engine='§wyrl§ Engine · Maker v11.291';source.version=11.291;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_290_CLIFF_GAUNTLET_LOAD_MATERIAL',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_291_HOODED_VANGUARD_MATERIALS'),
      ('ENGINE · MAKER v11.290','ENGINE · MAKER v11.291'),
      ('v11.290 · seamless gauntlet load and dimensional rock material',
       'v11.291 · Hooded Vanguard native sculpt and mapped material study'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.290'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.291'"),
      ('<title>§wyrl§ Engine · Maker v11.290</title>',
       '<title>§wyrl§ Engine · Maker v11.291</title>')
    ):
        html=once(html,old,new,'release provenance')
    anchor='const SE_RELEASE_NOTES='
    start=html.index(anchor)+len(anchor)
    notes,size=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Hooded Vanguard starter · sculpted forms and material-driven armor',
      date='2026-11-06',changes=[
      'Add a separate Starter Models card for Hooded Vanguard: an original native character study informed by owner-supplied hooded knight reference, without bird or weapon.',
      'Use a continuous anatomical male silhouette and a sculpted face; shaped hood, folded scarf, chest armor, shoulder protection, waist belt, gloves, boots and separately controllable teal coat tails. Prevent the previous many-small-parts modeling anti-pattern.',
      'Map distinct generated base-color, tangent-space normal and roughness texture sets onto explicit UVs. Gold engravings, leather grain, scarf folds and fabric threads are surface maps, not stacks of independent objects.',
      'Preserve all existing rocky hand, plain hand, anime girl, sheep/wolf, game starters and saved projects.',
      'This is a static native Model Atelier starter, not a complete skinned full-body rig, and final visual acceptance remains with owner on Android/Quest.'
    ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')+html[start+size:]
