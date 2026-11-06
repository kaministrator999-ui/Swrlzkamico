"""§E v11.287 — sculpt Plain Hand Base into the user's cliff-hand reference.

The native hand rig, native rock parts, starter identity and editable model
schema are preserved. Rock maps are derived from the user's attached ZIP; the
compact texture atlas ships as an ordinary Space asset, not a remote dependency.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def once(html, old, new, label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.287',label,count,old[:150]))
    return html.replace(old,new,1)

def apply(html):
    js=(ROOT/'runtime/cliff_hand_sculpt_pbr_v11_287.js').read_text('utf8')
    assert 'function se286CliffHandScene(){' in js
    for key in (
        'function se284PlainHandScene(){',
        'function se220RigMesh(part){',
        'function se282FullRockScene(){',
        'function se283WeatherRockTopology(topology){',
        'window.SWRLZ_FORGE_BUILD=',
        'data-project-template="plain-hand-base"',
    ):
        if key not in html:raise AssertionError(('missing v11.287 dependency',key[:100]))
    html=once(html,'window.SWRLZ_FORGE_BUILD=',
              js+'\nwindow.SWRLZ_FORGE_BUILD=',
              'inject native rock sculpt and PBR atlas material service')
    # Keep the original canonical starter ID and its route/handlers. Only the
    # generated source scene changes when owner explicitly opens the starter.
    html=once(html,'function se284PlainHandScene(){',
              'function se284PlainHandScene(){\n return se286CliffHandScene();',
              'replace plain clay starter with editable cliff sculpt')
    # Intercept the material at the native 17-bone mesh creation site.
    html=once(html,
        'const g=atelierSculptApply(geometry(part),part),mat=material(part);',
        'const g=atelierSculptApply(geometry(part),part),mat=part.cliffPBR?se286CreateCliffMaterial(part):material(part);\n'
        " if(part.cliffPBR&&g.getAttribute('uv')&&!g.getAttribute('uv2'))\n"
        "  g.setAttribute('uv2',g.getAttribute('uv').clone());",
        'lightmap AO support in 17-bone native mesh')
    html=once(html,'<strong>Plain Hand Base</strong>',
              '<strong>Plain Hand Base · Cliff Hand</strong>',
              'starter card title')
    html=once(html,'<span class="template-tag">STARTER MODEL · PLAIN RIGGED ANATOMY</span>',
              '<span class="template-tag">STARTER MODEL · CLIFF STONE / MOSS PBR / 17-BONE RIG</span>',
              'starter material tag')
    html=once(html,
      '<p>Clean connected five-finger hand and articulated thumb, neutral matte clay finish, no glove, rock, armor or effects. Native editable surface and 17-bone Rig/Animate starter.</p>',
      '<p>Sculpted sandstone palm, fingers, thumb and wrist with individually editable cliff plates, dark cracks, green moss and PBR rock maps. Native 17-joint poses and animation.</p>',
      'starter card materials description')
    html=once(html,'Sculpt an unadorned hand base',
              'Open sculpted Cliff Hand · editable rock and materials',
              'starter card action')
    html=once(html,'Plain Hand Base · clean anatomical mesh and 17-bone finger rig ready',
              'Cliff Hand · sculpted stone plates, moss PBR, 17-joint rig ready',
              'correct starter ready message')
    old_version=" source.engine='§wyrl§ Engine · Maker v11.286';source.version=11.286;"
    count=html.count(old_version)
    if count!=3:raise AssertionError(('v11.287 provenance count',count))
    html=html.replace(old_version,
       " source.engine='§wyrl§ Engine · Maker v11.287';source.version=11.287;")
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_286_SHEEP_HEAD_MOTION_DIAGNOSTICS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_287_CLIFF_SCULPT_PBR'),
      ('ENGINE · MAKER v11.286','ENGINE · MAKER v11.287'),
      ('v11.286 · Sheep Tag Quest head-motion Nerd Stats',
       'v11.287 · sculpted cliff hand, stone PBR and moss layers'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.286'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.287'"),
      ('<title>§wyrl§ Engine · Maker v11.286</title>',
       '<title>§wyrl§ Engine · Maker v11.287</title>'),
    ):
        html=once(html,old,new,'release provenance')
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Plain Hand Base sculpted as Cliff Hand with genuine PBR materials',
      date='2026-11-05',changes=[
       'Replace only the Plain Hand Base starter scene with a new native rocky cliff sculpt, keeping the existing plain-hand 17-joint pose timeline, selection ID, startup route and saved-project behavior.',
       'Use native separate solid closed stone finger/thumb segments, sculpted 360-degree palm and wrist, weathered rounded slabs and 32 additional individually editable layered sandstone plates. No exposed smooth glove or flat image billboard.',
       'Apply the owner-provided rock albedo, moss-composited rock color, OpenGL normal map, rock roughness, AO, height bump and dirt from an 8-tile 128px-per-map JPEG atlas compiled from cliff_hand_separate_material_assets.zip.',
       'Fix independent stone UV mapping, add uv2 to the skinned native mesh for AO and assign zero-metal PBR rough sandstone instead of fake glossy stone; use selective moss and dark non-emissive crevices.',
       'Leave Rocky Anime Hand, Arcane Gloves, saved scenes, other game/model starters, VR camera/controller logic, Sheep Tag and particle systems unchanged.',
       'Perform targeted source/JavaScript/asset checks. Final phone and Quest visual acceptance remains with the owner.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]