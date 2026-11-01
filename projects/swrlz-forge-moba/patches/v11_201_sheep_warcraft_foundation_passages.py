"""§E v11.201: Warcraft-style farm foundations and safe local passage guides.
Append-only presentation; all navigation, fog and multiplayer rules unchanged.
"""
from pathlib import Path
import json

def once(s,old,new):
    count=s.count(old)
    assert count==1,('v11.201 anchor',old[:140],count)
    return s.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    script=(root/'runtime/sheep_warcraft_foundation_passages_v11_201.js').read_text(encoding='utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_200_SHEEP_VR_STABILIZED_SPOTLIGHT',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_201_SHEEP_CLEARANCE_FOUNDATIONS'),
      ('ENGINE · MAKER v11.200','ENGINE · MAKER v11.201'),
      ('v11.200 · Sheep Tag stabilized overhead camera and direct movement',
       'v11.201 · Warcraft-style Sheep Tag foundations and passage guides'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.200'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.201'"),
      ('<title>§wyrl§ Engine · Maker v11.200</title>',
       '<title>§wyrl§ Engine · Maker v11.201</title>'),
    ]:
        html=once(html,old,new)
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    obj,n=json.JSONDecoder().raw_decode(html[at:])
    obj.update(title='Sheep Tag: smooth Warcraft-like house foundations and true passability',
     date='2026-11-01',changes=[
      'Built houses display softened terrain-conforming interior foundation plates and exact native square/rotated footprint borders, plus a faint outer sheep-center stopping-distance band derived from the native collision radius.',
      'Live build ghosts preserve native green/red placement validation and snap positions. A muted grid and nearby teal/amber/red corridors indicate comfortably open, narrowly passable, and blocked local sheep gaps.',
      'Passability guides use existing stClarityGap swept-collision tests, native stUnitRadius and stSafeLaneWidth thresholds. Never change collision physics or accept invalid buildings.',
      'Batch completed foundations and lane polygons into seven reusable render layers rather than individual house boxes and per-gap canvas textures. Rebuild only on navigation/visible-house changes, reuse preview geometry across aiming, free resources when Play ends.',
      'Preserve visibility-filtered fog-of-war, Quest thumbsticks and WebXR tracking, LAN authority, 2D mobile controls, model editor, previous visual fixes, release checks and all 68 assets. Physical Quest 2 visual acceptance remains pending.'
     ])
    return html[:at]+json.dumps(obj,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+n:]
