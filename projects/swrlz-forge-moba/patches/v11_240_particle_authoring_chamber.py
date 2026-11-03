"""§E v11.240 — isolated Particle Studio 3D authoring chamber.

Append-only edit on v11.239. Reuse current renderer, scene, emitter library and
host-native operations. This does not write any actor or 3D stage into project
serialization, rewrite earlier patches, or modify immersive Quest render flow.
"""
from pathlib import Path
import json


def once(source, old, new, label):
    count = source.count(old)
    if count != 1:
        raise AssertionError(("v11.240 source anchor", label, count, old[:110]))
    return source.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parents[1]
    stage = (root / "runtime/particle_authoring_stage_v11_240.js").read_text(encoding="utf8")
    for marker in (
        "function se223Frame(dt,t)", "function se223Origin(cfg)",
        "function se223Runtime(config)", "function se223Reset()",
        "function se225Open(mode,push=true)", "function se225Hide(clearRoute=false)",
        "window.SWYRL_ENGINE_STUDIOS=Object.freeze",
        "function executeStudio(op)",
    ):
        if marker not in html:
            raise AssertionError(("v11.240 dependency not available", marker))

    # The current editor still owns the 3D scene and all project-native VFX data.
    # Only in the Particle Studio test chamber is the selected preset previewed
    # at the reference origin, independent of its saved world placement.
    html = once(html, "function se223Origin(cfg){\n if(cfg.attachActorId){",
        "function se223Origin(cfg){\n"
        " if(window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.())return new THREE.Vector3(0,1.7,0);\n"
        " if(cfg.attachActorId){", "preview emitter origin")
    html = once(html,
        " r.cloud.name='Particle Studio · '+config.name;\n r.material.size=config.size;",
        " r.cloud.name='Particle Studio · '+config.name;\n"
        " r.cloud.layers.set(window.SWYRL_ENGINE_PARTICLE_STAGE_240?.active?.()?25:0);\n"
        " r.material.size=config.size;", "preview-only render layer")
    html = once(html,
        " const active=!paused&&(!!playing||!!simulating||se223State.preview);",
        " const stageActive=window.SWYRL_ENGINE_PARTICLE_STAGE_240?.frame?.()===true;\n"
        " const active=!paused&&(!!playing||!!simulating||se223State.preview);",
        "test chamber per-frame camera")
    html = once(html,
        " const ids=new Set(data.emitters.map(x=>x.id));",
        " const editEmitters=stageActive?data.emitters.filter(e=>e.id===(se223State.selected||data.emitters[0]?.id)):data.emitters;\n"
        " const ids=new Set(editEmitters.map(x=>x.id));", "selected emitter only")
    html = once(html, " for(const cfg of data.emitters){",
        " for(const cfg of editEmitters){", "render only selected emitter")
    html = once(html, "function se225Hide(clearRoute=false){",
        "function se225Hide(clearRoute=false){\n"
        " window.SWYRL_ENGINE_PARTICLE_STAGE_240?.close?.();",
        "restore exact original camera and layers")
    html = once(html,
        "   se223State.panel=true;se223State.preview=true;se223UIRefresh();",
        "   se223State.panel=true;se223State.preview=true;se223UIRefresh();\n"
        "   window.SWYRL_ENGINE_PARTICLE_STAGE_240?.open?.();",
        "open VFX test chamber after editor mounts")
    html = once(html,
        "  'Emitter particles render into this native game viewport. Move the scene camera to inspect the result.':",
        "  'Dedicated effects test chamber · preview one emitter, drag to orbit and scroll to zoom. Sheep Tag actor positions remain unchanged.':",
        "studio preview note")

    html = once(html, "window.SWRLZ_FORGE_BUILD=", stage + "\nwindow.SWRLZ_FORGE_BUILD=",
        "single-renderer authoring stage")
    old = " source.engine='§wyrl§ Engine · Maker v11.239';source.version=11.239;"
    if html.count(old) != 2:
        raise AssertionError(("v11.240 save provenance", html.count(old)))
    html = html.replace(old, " source.engine='§wyrl§ Engine · Maker v11.240';source.version=11.240;")
    for before, after in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_239_QUEST_HEADTURN_RAYCAST_BUDGET",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_240_PARTICLE_AUTHORING_CHAMBER"),
        ("ENGINE · MAKER v11.239", "ENGINE · MAKER v11.240"),
        ("v11.239 · Quest fast-turn frame budget and native raycast removal",
         "v11.240 · isolated Particle Studio authoring chamber"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.239'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.240'"),
        ("<title>§wyrl§ Engine · Maker v11.239</title>",
         "<title>§wyrl§ Engine · Maker v11.240</title>"),
    ):
        html = once(html, before, after, "release identity")
    marker = "const SE_RELEASE_NOTES="
    at = html.index(marker) + len(marker)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Particle Studio standalone 3D authoring chamber",
                 date="2026-11-03",
                 changes=[
                     "Particle Studio now opens an isolated 3D emitter preview area rather than asking creators to use the Sheep Tag game scene as an effects workbench.",
                     "The existing WebGL renderer, THREE scene, 12-emitter library, particle physics, import/export, presets and editor transactions are reused; no second GPU canvas or renderer is created.",
                     "Camera render-layer isolation hides level actors only in the authoring stage; it restores the exact previous position, orientation and layer mask on exit.",
                     "Preview only the selected emitter at the chamber origin. Drag to orbit or wheel to zoom; no actor attachment is required and saved world placement is untouched.",
                     "Entering immersive VR or Play mode ends the 2D authoring chamber safely. Game/Modeler/Materials and real 3D world emitter output are unchanged.",
                     "Native §C Particle Studio commands still require an authenticated host, a single reviewed plan, owner approval and a real execution receipt. Source focus check and owner Quest/phone acceptance outstanding."
                 ])
    return html[:at] + json.dumps(notes, ensure_ascii=False,
                                  separators=(",", ":")).replace("</", "<\\/") + html[at+width:]
