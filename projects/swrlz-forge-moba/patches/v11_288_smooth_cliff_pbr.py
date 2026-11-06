"""§E v11.288: restore single connected hand; material maps create stone illusion."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def once(html,old,new,label):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.288',label,n,old[:100]))
    return html.replace(old,new,1)
def apply(html):
    js=(ROOT/'runtime/smooth_cliff_hand_v11_288.js').read_text('utf8')
    assert 'function se288SmoothCliffHandScene(){' in js
    for key in ('function se286CliffHandScene(){',
       'mat=part.cliffPBR?se286CreateCliffMaterial(part):material(part);',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_287_CLIFF_SCULPT_PBR',
       'window.SWRLZ_FORGE_BUILD=', 'Plain Hand Base · Cliff Hand'):
        if key not in html:raise AssertionError(('missing v11.288 prerequisite',key))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=',
      'register connected hand PBR builder')
    # Keep starter identity and existing startup/load handlers; remove old
    # stacked-stone construction from the actually invoked code path.
    html=once(html,'function se286CliffHandScene(){',
      'function se286CliffHandScene(){\n return se288SmoothCliffHandScene();',
      'route plain-hand starter to connected smooth hand')
    html=once(html,
      'mat=part.cliffPBR?se286CreateCliffMaterial(part):material(part);',
      "mat=part.cliffPBR?.atlas==='cliff_pbr_atlas_384'?se288CliffMaterial(part):part.cliffPBR?se286CreateCliffMaterial(part):material(part);",
      'use 384px owner material on native skinned mesh')
    html=once(html,'<strong>Plain Hand Base · Cliff Hand</strong>',
      '<strong>Plain Hand Base · Smooth Cliff Hand</strong>',
      'correct starter card title')
    html=once(html,
      '<span class="template-tag">STARTER MODEL · CLIFF STONE / MOSS PBR / 17-BONE RIG</span>',
      '<span class="template-tag">STARTER MODEL · SMOOTH HAND / ROCK MATERIAL / 17-BONE RIG</span>',
      'correct starter tag')
    html=once(html,
      '<p>Sculpted sandstone palm, fingers, thumb and wrist with individually editable cliff plates, dark cracks, green moss and PBR rock maps. Native 17-joint poses and animation.</p>',
      '<p>One smooth connected hand mesh with rock strata, recessed cracks and selective moss drawn in mapped PBR textures. No separate stone chunks or 3D crack objects. Native 17-joint poses.</p>',
      'correct starter description')
    html=once(html,'Open sculpted Cliff Hand · editable rock and materials',
      'Open smooth Cliff Hand · texture-mapped stone','starter action')
    html=once(html,'Cliff Hand · sculpted stone plates, moss PBR, 17-joint rig ready',
      'Smooth Cliff Hand · connected mesh, mapped stone cracks and 17-joint rig',
      'starter toast')
    old=" source.engine='§wyrl§ Engine · Maker v11.287';source.version=11.287;"
    if html.count(old)!=3:raise AssertionError(('v11.288 provenance count',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.288';source.version=11.288;")
    for old,new in (
     ('SWYRL_ENGINE_DEPLOY_MARKER: V11_287_CLIFF_SCULPT_PBR',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_288_SMOOTH_CLIFF_PBR'),
     ('ENGINE · MAKER v11.287','ENGINE · MAKER v11.288'),
     ('v11.287 · sculpted cliff hand, stone PBR and moss layers',
      'v11.288 · smooth connected hand and mapped stone surfaces'),
     ("window.SWRLZ_FORGE_BUILD={version:'v11.287'",
      "window.SWRLZ_FORGE_BUILD={version:'v11.288'"),
     ('<title>§wyrl§ Engine · Maker v11.287</title>',
      '<title>§wyrl§ Engine · Maker v11.288</title>'),
    ):html=once(html,old,new,'release identity')
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Smooth Cliff Hand: rock depth illusion comes from mapped material',
      date='2026-11-05',changes=[
      'Replace the previous 121-piece stacked-stone Plain Hand starter with a single smooth connected anatomical topology mesh. The v11.287 rocky blocks remain historical source but are not used by this starter.',
      'Remove 3D crack curves, finger boulders, separated cliff plates, giant rock tiles and scattered moss objects from the instantiated hand.',
      'Preserve original hand proportions, curved thumb, continuous palm, wrist, 17 native joints and animation timeline.',
      'Apply a higher-resolution 384px/tile owner-provided cliff atlas across the connected hand with one continuous UV projection, not one complete tile per rock object.',
      'Draw stone boundaries and fractures using albedo and tangent normal maps with matching roughness/AO and subtle moss; geometry stays smooth; no displacement-driven chunks.',
      'Leave independently editable Rocky Anime Hand, Arcane Gloves, Sheep Tag VR, saved projects and all other starters unchanged.',
      'Verify complete engine packaging, asset integrity and JavaScript syntax. Real handset/Quest visual acceptance pending.'
    ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
