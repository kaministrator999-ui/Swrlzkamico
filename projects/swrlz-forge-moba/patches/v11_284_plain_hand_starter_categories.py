"""§E v11.284 — independent Plain Hand Base and starter Model/Games sorting fix.
Append-only; no changes to saved projects, previous model starters or VR.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(html,old,new,why):
    count=html.count(old)
    if count!=1:raise AssertionError(("v11.284",why,count,old[:140]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/"runtime/plain_hand_model_v11_284.js").read_text("utf8")
    for term in (
      "function se212HandScene(){",
      "function se220RigValidate(rig){",
      "function se232ActivateSelectedModelWorkspace(){",
      "function se236InstallStarterGroups(){",
      "function se128LaunchStartupProject(){",
      "window.SWRLZ_FORGE_BUILD=",
      'data-project-template="floating-hand-glove"',
      'data-project-template="rocky-anime-hand"',
    ):
        assert term in html,("v11.284 missing prerequisite",term)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",js+"\nwindow.SWRLZ_FORGE_BUILD=",
       "install plain sculptable anatomy starter plus type-aware starter sorting")
    card=(
      '<button class="project-card den" data-project-template="plain-hand-base">'
      '<span class="project-icon">🖐️</span><strong>Plain Hand Base</strong>'
      '<span class="template-tag">STARTER MODEL · PLAIN RIGGED ANATOMY</span>'
      '<p>Clean connected five-finger hand and articulated thumb, neutral '
      'matte clay finish, no glove, rock, armor or effects. Native editable '
      'surface and 17-bone Rig/Animate starter.</p>'
      '<span class="hint den-glow">Sculpt an unadorned hand base</span></button>'
    )
    html=once(html,
      '<button class="project-card den" data-project-template="floating-hand-glove">',
      card+'<button class="project-card den" data-project-template="floating-hand-glove">',
      "add separate Plain Hand Base model starter card")
    html=once(html,"function se128LaunchStartupProject(){",
       """function se128LaunchStartupProject(){
 if(new URLSearchParams(location.search).get('project')==='plain-hand-base'){
  se284OpenPlainHand(true);window.se128StartupPending=false;return;
 }""","direct new starter route")
    before=" source.engine='§wyrl§ Engine · Maker v11.283';source.version=11.283;"
    count=html.count(before)
    assert count==3,("v11.284 model metadata versions",count)
    html=html.replace(before,
      " source.engine='§wyrl§ Engine · Maker v11.284';source.version=11.284;")
    for old,new in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_283_WEATHERED_ROCK_HAND",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_284_PLAIN_HAND_MODEL_CATEGORIES"),
      ("ENGINE · MAKER v11.283","ENGINE · MAKER v11.284"),
      ("v11.283 · weathered smoothish rock hand, no exposed glove",
       "v11.284 · plain anatomy hand and corrected starter models tabs"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.283'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.284'"),
      ("<title>§wyrl§ Engine · Maker v11.283</title>",
       "<title>§wyrl§ Engine · Maker v11.284</title>"),
    ):html=once(html,old,new,"release identity and marker")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Plain Hand Base and fixed Starter Models grouping",
      date="2026-11-05",changes=[
       "Add a new independent Plain Hand Base starter to Projects → Starter Models, keeping all existing Rock Hand, Arcane Gloves, sheep buildings and game projects untouched.",
       "The Plain Hand is one existing native sculptable connected anatomical mesh, a neutral matte color, no glove armor, decorations, effects, cracks or rocks. It uses the validated 17-joint hand Rig/Animate timeline with wrist, palm, 12 finger joints and three thumb joints.",
       "Repair the previously hard-coded Starter Games/Starter Models sorter to recognize newly added model template labels and known model IDs. Move the existing original card nodes to the Model tab without duplicating cards, destroying events or changing saved starter preferences.",
       "Explicit game cards such as Blank VR Arcane Hands stay under Starter Games. Other known model-only cards including Rocky Anime Hand, Arcane Glove Left, Floating Hand and sheep building prototypes are shown in Starter Models.",
       "Support the new ?project=plain-hand-base direct route. Native Model Atelier editing, poses, saves, exports and independent model project identity remain.",
       "No changes to existing rocky-hand designs, shaders, XR, particles, Sheep Tag, gameplay, multiplayer or AI Chat. Owner mobile UI/rig acceptance pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+n:]
