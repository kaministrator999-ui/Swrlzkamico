"""§E v11.212: original editable floating hand / arcane glove Model Atelier starter.
Append-only addition: preserve all existing game starters, user scenes, XR and controls.
"""
from pathlib import Path
import json

def once(html, old, new):
    matches=html.count(old)
    if matches!=1:
        raise AssertionError(("v11.212 source anchor", old[:140], matches))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/model_atelier_floating_hand_v11_212.js').read_text(encoding='utf-8')
    # The organic mesh construction helpers are private to the native modeler
    # closure; expose only these two focused operations to the starter source.
    html=once(html,"  function refreshList(){",
      "  window.SWYRL_ENGINE_HAND_SURFACE=Object.freeze({surface:atelierAnimalSurface,weld:atelierAnimalWeld});\n  function refreshList(){")
    html=once(html,"window.SWRLZ_FORGE_BUILD=",js+"\nwindow.SWRLZ_FORGE_BUILD=")
    card=(
      '<button class="project-card den" data-project-template="floating-hand-glove">'
      '<span class="project-icon">🖐️</span><strong>Floating Hand · Arcane Glove</strong>'
      '<span class="template-tag">NATIVE 3D MODEL · GLOWING HAND</span>'
      '<p>Organic five-finger glove with editable armor plates, palm crest, purple runes and floating wrist rings. Open in Model Atelier.</p>'
      '<span class="hint den-glow">Sculpt floating hand starter</span></button>'
    )
    html=once(html,
      '<button class="project-card den" data-project-template="festival-girl-saved">',
      card+'<button class="project-card den" data-project-template="festival-girl-saved">')
    # The default selector automatically discovers button[data-project-template].
    # Explicit links must bypass Dragon Den without changing saved preferences.
    html=once(html, "function se128LaunchStartupProject(){",
      "function se128LaunchStartupProject(){\n"
      " if(new URLSearchParams(location.search).get('project')==='floating-hand-glove'){\n"
      "  se212OpenHand(true);window.se128StartupPending=false;return;\n"
      " }")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_211_QUEST_OS_CAMERA_OVERLAY_STABILITY',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_212_FLOATING_HAND_MODEL_STARTER'),
      ('ENGINE · MAKER v11.211','ENGINE · MAKER v11.212'),
      ('v11.211 · Quest OS Camera menu overlay and XR tracking stability',
       'v11.212 · native floating hand glove Model Atelier starter'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.211'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.212'"),
      ('<title>§wyrl§ Engine · Maker v11.211</title>',
       '<title>§wyrl§ Engine · Maker v11.212</title>')
    ]:html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    start=html.index(tag)+len(tag)
    notes,length=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Floating Hand: a native editable arcane glove Model Atelier starter',
      date='2026-11-02',changes=[
        'Added Floating Hand · Arcane Glove as an independent Model Atelier starter card, accessible through Projects, saved default selection, and ?project=floating-hand-glove.',
        'The glove has an original connected organic polygonal core (palm, wrist, thumb and four fingers), rather than a flat reference image. It is built with the existing native surface and UV mesh machinery.',
        'Separate editable silver/dark knuckle armor, purple dorsal seams, fingertip glows, dual-sided hand crests, metallic cuff and floating energy ring meshes provide a stylized purple/black armor study.',
        'Native project JSON remains editable and saveable. Existing model sculpt tools and mesh/GLB exporters apply to the authored meshes. No new renderer, external texture fetch, XR input mapping or default project takeover.',
        'The initial starter is an open neutral hand; skeleton skin weights, pose blending, and animation playback are not invented by this release and remain separate authoring work.',
        'Prior model starters, Sheep Tag, editor/game workspace separation, Quest VR and account projects remain unchanged. Owner mobile and Quest visual acceptance is pending.'
      ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+length:]
