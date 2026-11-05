"""§E v11.279 — blank game world using the original Arcane Glove as two live
tracked Quest controller hands; independently editable left-hand starter model.

Append-only to v11.278. All old models, saved levels, game/VR controls,
Sheep Tag/LAN, particles and §C are preserved.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def once(source,old,new,why):
    count=source.count(old)
    if count!=1:
        raise AssertionError(("v11.279",why,count,old[:130]))
    return source.replace(old,new,1)

def apply(html):
    js=(ROOT/"runtime/blank_vr_arcane_hands_v11_279.js").read_text(encoding="utf-8")
    for symbol in (
        "function se212HandScene(){",
        "function se212OpenHand(force=false){",
        "function se232ActivateSelectedModelWorkspace(){",
        "function se220RigWeights(pt,rig){",
        "function se221GesturePose(rig,kind){",
        "function se223WavePose(rig,side,flutter=0){",
        "function se181XRRender(){",
        "function se181XRRelease(){",
        "function se128LaunchStartupProject(){",
        "function se236InstallStarterGroups(){",
        "window.SWRLZ_FORGE_BUILD=",
    ):
        assert symbol in html,("v11.279 prerequisite",symbol)

    html=once(html,"window.SWRLZ_FORGE_BUILD=",js+"\nwindow.SWRLZ_FORGE_BUILD=",
              "ship dual-hand runtime after prior feature modules")

    cards=(
      '<button class="project-card den" data-project-template="blank-vr-hands">'
      '<span class="project-icon">🥽</span><strong>Blank VR · Arcane Hands</strong>'
      '<span class="template-tag">STARTER GAME · EMPTY WORLD + TWO VR GLOVES</span>'
      '<p>Clean native ground and no actors or enemies. Enter Quest VR to use '
      'the animated Arcane Glove as your left and right Touch controller hands.</p>'
      '<span class="hint den-glow">Create blank immersive game</span></button>'
      '<button class="project-card den" data-project-template="arcane-glove-left">'
      '<span class="project-icon">🫲</span><strong>Floating Hand · Arcane Glove (Left)</strong>'
      '<span class="template-tag">STARTER MODEL · MIRRORED 17-BONE RIG</span>'
      '<p>Physically mirrored thumb and finger mesh, native skeleton, skinning, '
      'all saved gesture poses and matching thumb, wrist and wave animations.</p>'
      '<span class="hint den-glow">Open editable left glove model</span></button>'
    )
    html=once(html,
      '<button class="project-card den" data-project-template="floating-hand-glove">',
      cards+'<button class="project-card den" data-project-template="floating-hand-glove">',
      "new games/models cards beside original glove")
    html=once(html,"function se128LaunchStartupProject(){",
      """function se128LaunchStartupProject(){
 const se279Requested=new URLSearchParams(location.search).get('project');
 if(se279Requested==='blank-vr-hands'){
  se279CreateBlank();window.se128StartupPending=false;return;
 }
 if(se279Requested==='arcane-glove-left'){
  se279OpenLeft(true);window.se128StartupPending=false;return;
 }""",
      "direct URLs reuse native starter loaders")

    # Attach GPU-skinned hands to the existing XR controllers after they are
    # acquired. No additional WebGL renderer or requestAnimationFrame.
    html=once(html,
      "function se181XRRender(){\n if(!se181XR.session||!renderer.xr.isPresenting)return;",
      "function se181XRRender(){\n if(!se181XR.session||!renderer.xr.isPresenting)return;\n se279XRFrame();",
      "render tracked gloves once per native XR frame")
    html=once(html,
      "function se181XRRelease(){",
      "function se181XRRelease(){\n se279Cleanup();",
      "dispose GPU skin geometry on XR session exit")

    before=" source.engine='§wyrl§ Engine · Maker v11.278';source.version=11.278;"
    count=html.count(before)
    assert count==2,("v11.279 model provenance",count)
    html=html.replace(before," source.engine='§wyrl§ Engine · Maker v11.279';source.version=11.279;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_278_QUEST_MENU_CADENCE',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_279_BLANK_VR_ARCANE_HANDS'),
      ('ENGINE · MAKER v11.278','ENGINE · MAKER v11.279'),
      ('v11.278 · Quest metrics wrist clearance and menu cadence',
       'v11.279 · blank VR hands and mirrored left glove'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.278'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.279'"),
      ('<title>§wyrl§ Engine · Maker v11.278</title>',
       '<title>§wyrl§ Engine · Maker v11.279</title>'),
    ):
        html=once(html,old,new,"release identity")

    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Blank VR Arcane Hands and mirrored left glove starter",
      date="2026-11-05",changes=[
      "Add Blank VR · Arcane Hands under Starter Games, with clean ground, no pawns, enemies or scenery, and a native editable scene that can be saved and reset.",
      "When immersed in this specific project, bind actual original Arcane Glove geometry and the mirrored left-hand glove to their respective tracked Quest WebXR Touch controllers, not to world-space placeholders or a second renderer.",
      "Retain the original starter glove intact; add a separate Left Arcane Glove under Starter Models. Mirror actual native mesh vertices, triangle winding, transform orientation, thumb placement, bone rest pivots, skin ownership and saved keyframe rotations.",
      "All 14 native gesture presets work on the mirrored model; preview wrist wave, thumb opposition, grabs and fists through the same 17-joint skeletal authoring tools.",
      "In VR, trigger blends toward precision pinch and grip blends toward grasp/fist on each controller independently. Same native controller render loop, material-merged meshes for lower draw count and resource cleanup on leaving VR or changing games.",
      "No changes to controller menu buttons, Sheep Tag, LAN, VR locomotion or existing user projects. Headset fit and performance require the owner's Quest 2 acceptance."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+width:]
