"""§E v11.283 — weathered smoothish rock geometry on Rocky Anime Hand.
Append-only to v11.282; preserve full stone anatomy and original 17-bone rig.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(src,old,new,reason):
    n=src.count(old)
    if n!=1:raise AssertionError(("v11.283",reason,n,old[:128]))
    return src.replace(old,new,1)
def apply(html):
    js=(ROOT/"runtime/weathered_rock_hand_v11_283.js").read_text("utf8")
    for term in (
      "const se282PreviousRockScene=se281RockScene;",
      "function se282Mesh(){",
      "function se282FullRockScene(){",
      "function se281OpenRockyHand(force=false){",
      "function se220RigValidate(rig){",
      "window.SWRLZ_FORGE_BUILD=",
      'data-project-template="rocky-anime-hand"',
    ):
        assert term in html,("v11.283 missing dependency",term)
    html=once(html,"window.SWRLZ_FORGE_BUILD=",js+"\nwindow.SWRLZ_FORGE_BUILD=",
      "append isolated rock-weathering generator")
    html=once(html,
      '<span class="template-tag">STARTER MODEL · 360° CLIFF ROCK + 17-BONE RIG</span>',
      '<span class="template-tag">STARTER MODEL · WEATHERED STONE + 17-BONE RIG</span>',
      "model gallery label")
    html=once(html,
      '<p>Entirely cliff-rock anatomy: angular stone palm, sides, thumb, '
      'fingers and rooted wrist. No exposed smooth glove. Amber fractures, '
      'editable 17-bone posing and animation.</p>',
      '<p>A solid rock-cliff hand with softened weathered stone facets, '
      'rounded worn edges and separate articulated rock fingers. '
      'No exposed glove; amber faults and native 17-bone animation.</p>',
      "model gallery description")
    before=" source.engine='§wyrl§ Engine · Maker v11.282';source.version=11.282;"
    count=html.count(before)
    assert count==3,("v11.283 starter source provenance count",count)
    html=html.replace(before,
      " source.engine='§wyrl§ Engine · Maker v11.283';source.version=11.283;")
    for old,new in (
      ("SWYRL_ENGINE_DEPLOY_MARKER: V11_282_ROCK_CLIFF_HAND",
       "SWYRL_ENGINE_DEPLOY_MARKER: V11_283_WEATHERED_ROCK_HAND"),
      ("ENGINE · MAKER v11.282","ENGINE · MAKER v11.283"),
      ("v11.282 · solid 360° cliff-rock hand, no exposed glove",
       "v11.283 · weathered smoothish rock hand, no exposed glove"),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.282'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.283'"),
      ("<title>§wyrl§ Engine · Maker v11.282</title>",
       "<title>§wyrl§ Engine · Maker v11.283</title>")
    ):html=once(html,old,new,"release marker and visible provenance")
    start=html.index("const SE_RELEASE_NOTES=")+len("const SE_RELEASE_NOTES=")
    notes,n=json.JSONDecoder().raw_decode(html[start:])
    notes.update(title="Weathered Rocky Anime Hand: smoothish stone, not a smooth glove",
      date="2026-11-05",changes=[
       "The existing full-rock Rocky Anime Hand starter now uses gently rounded, weathered stone facets instead of hard flat-shaded polygon chunks, following the owner's request for more smoothish modeling.",
       "Within each separate rock, weld coincident vertices, split each triangle once, and gently relax neighboring vertices twice; generated shared indexed vertices produce softer vertex normals with no extra renderer or texture.",
       "Keep the solid full-coverage cliff-rock palm, side slabs, all 12 individual 360-degree stone finger segments, three solid thumb segments, rooted basalt wrist, amber fracture geometry and 17-bone rig and animations.",
       "Preserve separate editable native rock topology meshes, saved-project schema, names, rigging and existing Model Atelier controls; do not add a smooth organic glove beneath the stone.",
       "Original Arcane Gloves, other starters, Sheep Tag, VR game, §C and Mage Spell Lab are unchanged; existing saved projects are not silently modified. Hands-on mobile visual acceptance remains pending."
      ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")+html[start+n:]
