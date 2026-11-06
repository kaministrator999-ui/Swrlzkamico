"""§E v11.289 · sculpt a modest connected gauntlet forearm onto Smooth Cliff Hand."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:raise AssertionError(('v11.289',label,count,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/cliff_gauntlet_forearm_v11_289.js').read_text('utf8')
    assert 'function se289ExtendGauntletTopology(part){' in js
    for key in ('function se288SmoothCliffHandScene(){',
      'const vertices=se288ProjectCliffUV(stone);',
      'model.parts=[stone];model.meshGroups=[];',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_288_SMOOTH_CLIFF_PBR',
      'window.SWRLZ_FORGE_BUILD=',
      '<strong>Plain Hand Base · Smooth Cliff Hand</strong>'):
        if key not in html:raise AssertionError(('missing prerequisite',key))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'install gauntlet sculpt helper')
    html=once(html,'const vertices=se288ProjectCliffUV(stone);',
      'const gauntlet=se289ExtendGauntletTopology(stone);\n'
      ' const vertices=se289ProjectGauntletUV(stone);',
      'lengthen existing connected hand mesh before remapping its material')
    html=once(html,
      "model.editedAt='local';\n scene.project.name=model.name;",
      "model.reference+=' Short tapered stone gauntlet forearm sculpted into the same connected mesh; no separate rock, cuff or crack pieces.';\n"
      " model.editedAt='local';\n scene.project.name=model.name;",
      'include gauntlet description in native model metadata')
    html=once(html,
      '<p>One smooth connected hand mesh with rock strata, recessed cracks and selective moss drawn in mapped PBR textures. No separate stone chunks or 3D crack objects. Native 17-joint poses.</p>',
      '<p>Smooth connected cliff-stone hand with a short tapered gauntlet forearm. Stone cracks, roughness and selective moss remain mapped in PBR textures, not separate 3D objects. Native 17-joint rig.</p>',
      'starter card appearance')
    html=once(html,
      'Smooth Cliff Hand · connected mesh, mapped stone cracks and 17-joint rig',
      'Smooth Cliff Hand · short stone gauntlet forearm and 17-joint rig',
      'starter ready toast')
    old=" source.engine='§wyrl§ Engine · Maker v11.288';source.version=11.288;"
    if html.count(old)!=3:raise AssertionError(('provenance references',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.289';source.version=11.289;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_288_SMOOTH_CLIFF_PBR',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_289_SHORT_CLIFF_GAUNTLET'),
      ('ENGINE · MAKER v11.288','ENGINE · MAKER v11.289'),
      ('v11.288 · smooth connected hand and mapped stone surfaces',
       'v11.289 · short tapered stone gauntlet forearm'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.288'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.289'"),
      ('<title>§wyrl§ Engine · Maker v11.288</title>',
       '<title>§wyrl§ Engine · Maker v11.289</title>'),
    ):html=once(html,old,new,'release identity')
    token='const SE_RELEASE_NOTES='
    at=html.index(token)+len(token)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Short forearm addition to the smooth textured Cliff Hand',
      date='2026-11-05',changes=[
      'Lengthen the same smooth, connected Plain Hand Base / Cliff Hand mesh into a modest tapered gauntlet forearm without introducing any separate mesh pieces.',
      'Reshape only lower carpal/forearm vertices using a smooth monotonic falloff: approximately 0.74 model units of additional arm and a subtle rounded 9 percent cuff flare.',
      'Preserve upper palm, anatomical fingers and thumb, and the same native 17-bone skeleton/animation controls.',
      'Remap the existing 384px/tile rock material UVs across the new connected forearm to prevent the lower-end texture from clamping or smearing.',
      'Keep all cracks, cliff plates and moss represented by albedo/normal/roughness/AO maps, not 3D rock objects.',
      'Do not modify independent Rocky Anime Hand, Arcane Gloves, sheep/wolf models, saved projects, game physics, Sheep Tag, or VR controls.',
      'Validate engine source and JS syntax; actual phone and Quest visual shape/animation acceptance remains with owner.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
