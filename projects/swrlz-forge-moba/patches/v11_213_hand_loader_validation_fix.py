"""§E v11.213: correct the Floating Hand sleeve primitive for native model validation.

v11.212 shipped cylinder.meshDensity with v=1; the Model Atelier validator
reserves meshDensity for sphere/loft and requires v >= 4. A single invalid part
caused native loadProject() to reject the entire 39-part hand. Fix only this
hand-authored primitive; never weaken the validator or touch other projects.
"""
from pathlib import Path
import json

def once(html, old, new):
    n=html.count(old)
    if n!=1: raise AssertionError(("v11.213 source anchor",old[:140],n))
    return html.replace(old,new,1)

def apply(html):
    html=once(html,
      "return push(name,'cylinder',c,mat,group,{position:center,scale,meshDensity:{u:32,v:1}});",
      "return push(name,'cylinder',c,mat,group,{position:center,scale});")
    for old,new in [
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_212_FLOATING_HAND_MODEL_STARTER',
       'SWYRL_ENGINE_DEPLOY_MARKER: V11_213_HAND_PRIMITIVE_SCHEMA_FIX'),
      ('ENGINE · MAKER v11.212','ENGINE · MAKER v11.213'),
      ('v11.212 · native floating hand glove Model Atelier starter',
       'v11.213 · floating hand model loader validation fix'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.212'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.213'"),
      ('<title>§wyrl§ Engine · Maker v11.212</title>',
       '<title>§wyrl§ Engine · Maker v11.213</title>')
    ]:html=once(html,old,new)
    tag='const SE_RELEASE_NOTES='
    pos=html.index(tag)+len(tag)
    notes,n=json.JSONDecoder().raw_decode(html[pos:])
    notes.update(title='Floating Hand loader: native model validation compatibility',
      date='2026-11-02',changes=[
        'Correct the Floating Hand wrist sleeve cylinder authored with an invalid meshDensity property (v=1). Native Model Atelier only accepts meshDensity for sphere/loft and requires the appropriate density range.',
        'Leave all 39 authored glove meshes, sculpted core, armor, colors, crest, ring arrangement, and prior starter identities intact.',
        'Do not relax editor validation, modify user projects or change Sheep Tag, Quest controls, chat or other runtime systems.',
        'Add browser regression for direct starter link and native validator load. Physical owner mobile/Quest visual acceptance remains pending.'
      ])
    return html[:pos]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[pos+n:]
