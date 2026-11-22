"""§E v11.237 candidate — Quest stereo ground, fog and character visibility.

Append-only correction to the Quest WebXR visual adapter; preserves authored
terrain, native headset orientation, game fog knowledge, controllers and host.
Release only after official build SHA/bytes are verified and deployed.
"""
from pathlib import Path
import json

def once(html, old, new):
    count=html.count(old)
    assert count==1, ('v11.237 source anchor',old[:110],count)
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    js=(root/'runtime/engine_xr_stereo_fog_character_guard_v11_237.js').read_text(encoding='utf-8')
    for dep in ('function se193XRFrame()', 'function se195MoveRig(', 'function se193XRGameActive()',
                'window.SWYRL_ENGINE_SHEEP_BIOMES_208', 'window.SWYRL_ENGINE_QUEST_OS_STABILITY_211'):
        assert dep in html, ('v11.237 missing source dependency',dep)
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')

    prior=" source.engine='§wyrl§ Engine · Maker v11.236';source.version=11.236;"
    assert html.count(prior)==2,('v11.237 source provenance',html.count(prior))
    html=html.replace(prior,
        " source.engine='§wyrl§ Engine · Maker v11.237';source.version=11.237;")
    for before,after in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_236_SHEEP_GABLES_WOLF_ROOT_STARTER_GROUPS',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_237_QUEST_STEREO_FOG_CHARACTER_GUARD'),
      ('ENGINE · MAKER v11.236','ENGINE · MAKER v11.237'),
      ('v11.236 · sheep gables, wolf root preview, starter categories',
       'v11.237 · Quest stereo fog, ground and sheep visual stability'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.236'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.237'"),
      ('<title>§wyrl§ Engine · Maker v11.236</title>',
       '<title>§wyrl§ Engine · Maker v11.237</title>'),
    ]:
        html=once(html,before,after)
    marker='const SE_RELEASE_NOTES='
    start=html.index(marker)+len(marker)
    notes,n=json.JSONDecoder().raw_decode(html[start:])
    notes.update(
       title='Quest stereo fog/ground depth and moving-character culling guard',
       date='2026-11-02',
       changes=[
          'Maintain rendering eligibility of the native ground and one world-space fog plane in both Quest stereo views. Do not change fog masks, visibility rules, world positions or game simulation.',
          'Prevent animated, multi-part geometry from being individually clipped at an XR view edge for only the controlled sheep/wolf character; preserve original culling outside VR.',
          'Stop non-authoritative translucent 3D waymarker decorations from writing occluding depth into the meadow/fog while keeping the game fog depth testing enabled.',
          'Restore every changed culling/depth setting on VR exit, round stop, change of selected character or scene. Limit world inspection to 240ms intervals to avoid adding frame-time load.',
          'Expose stereo guard counts through SWYRL_ENGINE_QUEST_STEREO_GUARD_237 and append them to the existing VR debug capture metadata.',
          'Quest 2 owner testing must establish whether right-eye clipping, fog drift and missing fleece geometry improve. WebXR compositor/reprojection problems remain possible.'
       ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+n:]
