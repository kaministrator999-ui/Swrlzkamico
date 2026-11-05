"""§E v11.281 — Rocky Anime Hand · Emberstone.
Append-only, original multi-view image-inspired rigged stone hand starter.
New native Model Atelier project. No rewrite of existing models or saved games.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(html,old,new,reason):
    n=html.count(old)
    if n!=1:raise AssertionError(("v11.281",reason,n,old[:125]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/"runtime/rocky_anime_hand_starter_v11_281.js").read_text("utf8")
    for symbol in (
      "function se212HandScene(){",
      "function se220RigValidate(rig){",
      "function se232ActivateSelectedModelWorkspace(){",
      "function se128LaunchStartupProject(){",
      "const se281RockId='rocky-anime-hand';" if False else "const se279LeftId='arcane-glove-left';",
      "window.SWRLZ_FORGE_BUILD=",
      "function se236InstallStarterGroups(){",
    ):
        assert symbol in html,("v11.281 prerequisite",symbol)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
      js+"\nwindow.SWRLZ_FORGE_BUILD=","append original rock hand model runtime")
    card=(
      '<button class="project-card den" data-project-template="rocky-anime-hand">'
      '<span class="project-icon">🪨</span><strong>Rocky Anime Hand · Emberstone</strong>'
      '<span class="template-tag">STARTER MODEL · FACETED ROCK + 17-BONE RIG</span>'
      '<p>Chiseled gray stone palm, wrist and segmented fingers, amber glowing '
      'cracks and independently editable knuckle rocks. Opens in Model Atelier '
      'with real bone posing and an open/fist animation.</p>'
      '<span class="hint den-glow">Sculpt animated stone hand</span></button>'
    )
    html=once(html,
      '<button class="project-card den" data-project-template="floating-hand-glove">',
      card+'<button class="project-card den" data-project-template="floating-hand-glove">',
      "add rock starter to existing model gallery")
    html=once(html,"function se128LaunchStartupProject(){",
      """function se128LaunchStartupProject(){
 if(new URLSearchParams(location.search).get('project')==='rocky-anime-hand'){
  se281OpenRockyHand(true);window.se128StartupPending=false;return;
 }""","direct URL starter")
    before=" source.engine='§wyrl§ Engine · Maker v11.280';source.version=11.280;"
    count=html.count(before)
    assert count==3,("v11.281 model metadata versions",count)
    html=html.replace(before," source.engine='§wyrl§ Engine · Maker v11.281';source.version=11.281;")
    for old,new in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_280_MAGE_SPELL_LAB",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_281_ROCKY_ANIME_HAND"),
      ("ENGINE · MAKER v11.280","ENGINE · MAKER v11.281"),
      ("v11.280 · native Mage Spell particle library and VR glove casts",
       "v11.281 · Rocky Anime Hand Emberstone native starter model"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.280'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.281'"),
      ("<title>§wyrl§ Engine · Maker v11.280</title>",
       "<title>§wyrl§ Engine · Maker v11.281</title>"),
    ):html=once(html,old,new,"version identity and marker")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Rocky Anime Hand · Emberstone: native editable rigged model",
      date="2026-11-05",changes=[
        "Add Rocky Anime Hand · Emberstone to Projects → Starter Models, alongside the original Arcane Glove and independent left-handed mirrored model. Available as ?project=rocky-anime-hand.",
        "Native indexed low-poly stone faces: irregular beveled slate-gray polygons on front/back palms, angular cuff stones, finger phalanx plating, joint gaps, modeled thumb pieces and chipped edge fragments. Based on the generated multi-view rocky-hand concept, not a 2D card or texture billboard.",
        "Amber glowing fissures are independently editable topology-mesh curves, crossing knuckles, palm plates, thumb joints and wrist; material colors and sculpt geometry use existing Model Atelier tools.",
        "Inherit the existing valid 17-joint wrist/palm/finger/thumb skeleton, four-weight linear skinning and open → fist → open keyframes from the original native hand anatomy. The connected interior keeps segmented stone pieces attached when animating.",
        "Independent starter project opens in the Modeling workspace with standard scene save, mesh parts, group selection and Rig/Animate studio; no existing saved projects or glove assets altered.",
        "Do not replace the live Quest controllers or existing glove representations; a VR stone-hand swap is a later separate decision. Owner phone/Quest visual acceptance pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
