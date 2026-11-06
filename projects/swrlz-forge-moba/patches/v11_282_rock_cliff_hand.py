"""§E v11.282 — true rock-cliff hand instead of armor over smooth glove.
Append-only, specific to the Rocky Anime Hand starter only.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(html,old,new,reason):
    count=html.count(old)
    if count!=1:raise AssertionError(("v11.282",reason,count,old[:128]))
    return html.replace(old,new,1)
def apply(html):
    js=(ROOT/"runtime/rock_cliff_hand_v11_282.js").read_text("utf8")
    for x in (
      "const se281RockId='rocky-anime-hand';",
      "function se281RockScene(){",
      "const se281PreviousTemplate=createProjectFromTemplate;",
      "function se220RigValidate(rig){",
      "function se281CrackTopology(path,radius){",
      "window.SWRLZ_FORGE_BUILD=",
      'data-project-template="rocky-anime-hand"',
    ):assert x in html,("v11.282 missing dependency",x)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",
      js+"\nwindow.SWRLZ_FORGE_BUILD=",
      "append true rock-body generator after existing starter")
    html=once(html,
      '<span class="template-tag">STARTER MODEL · FACETED ROCK + 17-BONE RIG</span>',
      '<span class="template-tag">STARTER MODEL · 360° CLIFF ROCK + 17-BONE RIG</span>',
      "rock hand card visible descriptor")
    html=once(html,
      '<p>Chiseled gray stone palm, wrist and segmented fingers, amber glowing '
      'cracks and independently editable knuckle rocks. Opens in Model Atelier '
      'with real bone posing and an open/fist animation.</p>',
      '<p>Entirely cliff-rock anatomy: angular stone palm, sides, thumb, '
      'fingers and rooted wrist. No exposed smooth glove. Amber fractures, '
      'editable 17-bone posing and animation.</p>',
      "rock hand model card description")
    before=" source.engine='§wyrl§ Engine · Maker v11.281';source.version=11.281;"
    n=html.count(before)
    assert n==3,("v11.282 source scene version occurrences",n)
    html=html.replace(before," source.engine='§wyrl§ Engine · Maker v11.282';source.version=11.282;")
    for old,new in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_281_ROCKY_ANIME_HAND",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_282_ROCK_CLIFF_HAND"),
      ("ENGINE · MAKER v11.281","ENGINE · MAKER v11.282"),
      ("v11.281 · Rocky Anime Hand Emberstone native starter model",
       "v11.282 · solid 360° cliff-rock hand, no exposed glove"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.281'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.282'"),
      ("<title>§wyrl§ Engine · Maker v11.281</title>",
       "<title>§wyrl§ Engine · Maker v11.282</title>"),
    ):html=once(html,old,new,"release identity")
    at=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,size=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title="Rocky Anime Hand: full cliff-rock anatomy and jagged silhouette",
      date="2026-11-05",changes=[
        "Replace the Rocky Anime Hand starter's exposed smooth underlying organic glove and sparse armor overlays with actual solid, closed faceted rock anatomy: full polygonal palm, back, sides, wrist, thumb and all four fingers.",
        "Each finger now consists of three full-circumference irregular stone shafts with thick rocky bulges and jagged side outcrops. The complete angular thumb has three individual solid stone sections following actual CMC/MCP/IP bone pivots.",
        "Build interlocking raised cliff strata on dorsal and palmar surfaces, overlapping side ridges on thumb and little-finger edges and stepped wrist rock outcrops. Hard flat stone facets deliberately replace smooth skin normals.",
        "Keep editable branched amber magma crevices and fracture gaps at actual finger and thumb joints; do not cover the rock with ornamental glove materials, armor rings or a flat texture.",
        "All rock/energy geometry remains separate native editable topology meshes using the existing verified 17-bone Rig/Animate studio, save/export path and editable keyframes. No additional XR loop, game actors or remote assets.",
        "Scope strictly to opening a new Rocky Anime Hand starter. Prior saved rock projects are not silently migrated; original Arcane Glove, mirrored glove, blank VR hand game, Mage Spell Lab and Sheep Tag remain untouched. Owner visual acceptance pending."
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[at+size:]
