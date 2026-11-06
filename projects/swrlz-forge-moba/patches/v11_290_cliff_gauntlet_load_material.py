"""§E v11.290 · repair real-hand gauntlet startup, enrich mapped rock PBR."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.290',label,count,old[:135]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/cliff_gauntlet_surface_material_v11_290.js').read_text('utf8')
    assert 'function se290BuildGauntletSurface(part){' in js
    for token in ('const gauntlet=se289ExtendGauntletTopology(stone);',
                  'const vertices=se289ProjectGauntletUV(stone);',
                  "mat=part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se288CliffMaterial(part):",
                  'SWYRL_ENGINE_DEPLOY_MARKER: V11_289_SHORT_CLIFF_GAUNTLET',
                  'window.SWRLZ_FORGE_BUILD='):
        if token not in html:raise AssertionError(('missing prerequisite',token))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'install connected gauntlet generator and enriched material')
    # v11.289 rejects actual v11.217 hand bounds. Do not call its fixed-bottom
    # vertex stretch: re-mesh the *one connected* anatomy+forearm SDF instead.
    html=once(html,'const gauntlet=se289ExtendGauntletTopology(stone);',
      'const gauntlet=se290BuildGauntletSurface(stone);',
      'repair real hand model load')
    html=once(html,'const vertices=se289ProjectGauntletUV(stone);',
      'const vertices=se290GauntletUV(stone);',
      'project full-length stone maps on repaired forearm')
    html=once(html,
      "mat=part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se288CliffMaterial(part):",
      "mat=part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se290CliffMaterial(part):",
      'deeper stone normal shadows and warm PBR')
    html=once(html,
      '<p>Smooth connected cliff-stone hand with a short tapered gauntlet forearm. Stone cracks, roughness and selective moss remain mapped in PBR textures, not separate 3D objects. Native 17-joint rig.</p>',
      '<p>Connected smooth Cliff Hand and short stone gauntlet forearm with enhanced sandstone normal depth, dark texture-mapped cracks, selective moss and the native 17-bone rig.</p>',
      'starter card accurately describes improved material')
    html=once(html,
      'Smooth Cliff Hand · short stone gauntlet forearm and 17-joint rig',
      'Smooth Cliff Hand · seamless gauntlet and enhanced rock PBR ready',
      'starter ready toast')
    old=" source.engine='§wyrl§ Engine · Maker v11.289';source.version=11.289;"
    count=html.count(old)
    if count!=3:raise AssertionError(('provenance count',count))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.290';source.version=11.290;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_289_SHORT_CLIFF_GAUNTLET',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_290_CLIFF_GAUNTLET_LOAD_MATERIAL'),
      ('ENGINE · MAKER v11.289','ENGINE · MAKER v11.290'),
      ('v11.289 · short tapered stone gauntlet forearm',
       'v11.290 · seamless gauntlet load and dimensional rock material'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.289'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.290'"),
      ('<title>§wyrl§ Engine · Maker v11.289</title>',
       '<title>§wyrl§ Engine · Maker v11.290</title>')
    ):html=once(html,old,new,'release provenance')
    token='const SE_RELEASE_NOTES='
    at=html.index(token)+len(token)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Repair gauntlet loader and deepen texture-mapped cliff sandstone',
      date='2026-11-06',changes=[
      'Fix the owner-reported Plain Hand Base startup failure: v11.289 incorrectly rejected the active v11.217 hand shape because its lower vertex extent was higher than a hardcoded .57 assumption.',
      'Create a smooth, short tapered forearm as part of the original connected 3D hand signed-distance field and native mesh generation; preserve single topology, natural palm/thumb/fingers and original 17-bone pose system.',
      'Close the gauntlet end cleanly and blend into wrist anatomy without added 3D cuffs, boulders, crack lines or separate geometry.',
      'Enhance the owner-provided 384px/tile sandstone atlas with stronger tangent-space normal relief, mapped crack AO and a rougher natural-stone light response, keeping selective moss and continuous UV coverage.',
      'Repair actual hand load rather than relaxing a failing test. Add a real anatomical field integration test and report concrete model generation errors in console/status diagnostics.',
      'Preserve independent Rocky Anime Hand, Arcane Gloves, other starters, existing saved projects, VR input, Sheep Tag and §C.',
      'Validate exact sealed source and native simulation; final Android/Quest appearance and rig acceptance remain with owner.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
