"""§E v11.229 — repair all five sheep-faction Model Atelier starter loads.

Append-only correction to the v11.226 native house authoring function:
gloss/emissive material strings occupied optional angle slots of two indexed-box
calls, producing NaN rotations and breaking native validParts().
No project migration or Sheep Tag build/collision gameplay change.
"""
from pathlib import Path
import json


def once(s, old, new):
    n=s.count(old)
    if n!=1:
        raise AssertionError(('v11.229 sheep-house patch anchor',old[:160],n))
    return s.replace(old,new,1)


def apply(html):
    # Native box(name,x,y,z,w,h,depth,color,group,angle=0,material='matte')
    # expects the numeric angle before the material. Two decorations had
    # mistakenly passed the material as angle, converting to NaN in
    # number(angle) and causing all five model loads to be rejected.
    html=once(html,
        "box('Window · amber glow',x,y,z+.065,.58,.57,.055,P.glass,'Windows','gloss');",
        "box('Window · amber glow',x,y,z+.065,.58,.57,.055,P.glass,'Windows',0,'gloss');")
    html=once(html,
        "box('Lantern · glowing glass',x,y,z,.15,.28,.15,P.glass,'Decor / lantern','emissive');",
        "box('Lantern · glowing glass',x,y,z,.15,.28,.15,P.glass,'Decor / lantern',0,'emissive');")

    html=once(html,
        " source.engine='§wyrl§ Engine · Maker v11.226';source.version=11.226;",
        " source.engine='§wyrl§ Engine · Maker v11.229';source.version=11.229;")

    old=" source.engine='§wyrl§ Engine · Maker v11.228';source.version=11.228;"
    new=" source.engine='§wyrl§ Engine · Maker v11.229';source.version=11.229;"
    if html.count(old)!=2:
        raise AssertionError(('v11.229 native source version slots',html.count(old)))
    html=html.replace(old,new)

    for a,b in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_228_GAME_GUI_MENU_STUDIO',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_229_SHEEP_HOUSE_NATIVE_LOAD_REPAIR'),
      ('ENGINE · MAKER v11.228','ENGINE · MAKER v11.229'),
      ('v11.228 · Game Engine GUI and Menu Setup mini-tab',
       'v11.229 · Sheep Tag house model load validation repair'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.228'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.229'"),
      ('<title>§wyrl§ Engine · Maker v11.228</title>',
       '<title>§wyrl§ Engine · Maker v11.229</title>')
    ]:
        html=once(html,a,b)

    marker='const SE_RELEASE_NOTES='
    i=html.index(marker)+len(marker)
    notes,n=json.JSONDecoder().raw_decode(html[i:])
    notes.update(
      title='Sheep Tag house starter model loading: invalid transform repair',
      date='2026-11-02',
      changes=[
        'Repair all five sheep building Model Atelier starters failing to open with Invalid editable model parts.',
        'The house model authoring function supplied gloss and emissive strings as angle arguments to indexed 3D boxes, generating NaN rotations; set explicit zero rotation and preserve their intended materials.',
        'Deep-linked modeler.html starter and the Projects starter-card native load path now use finite validated transforms, without changing the designed house geometry or part identities.',
        'Add focused actual 390px Model Atelier browser loading regression for all five starters. Keep Sheep Tag game build costs, LAN authority and collision unchanged.',
        'Preserve existing saved projects, wolf and glove rigging, game GUI/Menu mini-tab, Materials/Textures, Particle Studio and native workspace state. Physical Moto/Quest visual acceptance stays with the owner.'
      ]
    )
    return html[:i]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[i+n:]
