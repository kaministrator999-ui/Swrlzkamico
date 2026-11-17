"""§E v11.483 — editable Sorting Hat starter, native Projects/Model Studio route."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = "SWYRL_ENGINE_DEPLOY_MARKER: V11_483_SORTING_HAT_STARTER"

def once(html, old, new, label):
    count = html.count(old)
    if count != 1:
        raise AssertionError(("se483", label, count, old[:110]))
    return html.replace(old, new, 1)

def apply(html):
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_482_GEOMETRIC_RING_HEIGHT" in html
    script = (ROOT / "runtime/sorting_hat_starter_v11_483.js").read_text("utf8")
    for word in ("se483ValidateSortingHat", "se483OpenSortingHat",
                 "se232ActivateSelectedModelWorkspace", "ModelAtelier.syncProject()",
                 "SE483_SORTING_HAT_END"):
        assert word in script, word

    html = once(html, "window.SWRLZ_FORGE_BUILD=",
                script + "\nwindow.SWRLZ_FORGE_BUILD=", "native model-starter loader")
    card = (
        '<button class="project-card den" data-project-template="sorting-hat">'
        '<span class="project-icon">🎩</span>'
        '<strong>The Sorting Hat</strong>'
        '<span class="template-tag">STARTER MODEL · EDITABLE CLOTH SCULPT</span>'
        '<p>Expressive wrinkled crown, crooked fabric face, folded speaking mouth,'
        ' floppy asymmetric brim, cloth band, rear patches and stitched seams.'
        ' Fully editable native mesh project.</p>'
        '<span class="hint den-glow">Open in Model Studio</span>'
        '</button>'
    )
    html = once(html,
        '<button class="project-card den" data-project-template="webxr-touch-left">',
        card + '<button class="project-card den" data-project-template="webxr-touch-left">',
        "integrated Starter Models card")

    html = once(html, "function se128LaunchStartupProject(){",
        """function se128LaunchStartupProject(){
 if(new URLSearchParams(location.search).get('project')==='sorting-hat'){
  window.se128StartupPending=true;
  queueMicrotask(()=>Promise.resolve(se483OpenSortingHat(true))
   .catch(error=>console.error('Sorting Hat startup',error))
   .finally(()=>{window.se128StartupPending=false;}));
  return;
 }
""", "direct model deep link")

    for old, new, label in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_482_GEOMETRIC_RING_HEIGHT",
         MARKER, "deploy marker"),
        ("ENGINE · MAKER v11.482", "ENGINE · MAKER v11.483", "visible title"),
        ("v11.482 · geometric rings and draggable height",
         "v11.483 · The Sorting Hat editable starter", "release headline"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.482'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.483'", "runtime build label"),
        ("<title>§wyrl§ Engine · Maker v11.482</title>",
         "<title>§wyrl§ Engine · Maker v11.483</title>", "browser title")
    ):
        html = once(html, old, new, label)

    prior = " source.engine='§wyrl§ Engine · Maker v11.482';source.version=11.482;"
    if html.count(prior) != 5:
        raise AssertionError(("se483 provenance count", html.count(prior)))
    html = html.replace(prior,
        " source.engine='§wyrl§ Engine · Maker v11.483';source.version=11.483;")

    key = "const SE_RELEASE_NOTES="
    start = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[start:])
    notes["history"] = [n for n in notes.get("history", [])
                        if n.get("version") != "v11.482"]
    notes["history"].insert(0, {
        "version": "v11.482",
        "changes": notes.get("changes", [])
    })
    notes.update(version="v11.483", date="2026-11-17",
        title="The Sorting Hat — native editable Model Studio starter",
        changes=[
            "Added The Sorting Hat to Projects → Starter Models as a true native model project, not an image overlay or separate preview.",
            "49 selectable topology parts include a continuous bent fabric crown, 3D wavy double-sided brim, folded face with recessed eye shadows and talking-mouth slit, band, cheek seams, old patches and sewn details.",
            "The supplied sketch was the front expression guide; researched multi-angle textile references informed actual volume, tip, brim and patches. All source geometry is original procedural study.",
            "Model Studio receives this starter through its existing validated load path. Project saving, cloning, mobile/VR operation, mesh tools and user projects are preserved.",
            "Original v11.482 model ring editing and all existing starters remain intact. Physical phone and Quest acceptance remains owner testing."
        ])
    return (html[:start] +
            json.dumps(notes, ensure_ascii=False, separators=(",", ":")).replace("</", r"<\/") +
            html[start+width:])
