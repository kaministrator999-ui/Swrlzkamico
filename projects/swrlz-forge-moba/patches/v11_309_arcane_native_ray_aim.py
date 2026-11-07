"""§E v11.309 — native Arcane aim and complete ray-visual suppression.

v11.308 hid se181's legacy Line, leaving se192's independently authored
tapered beam, cursor and optional saved yaw trim active. Keep Quest WebXR
target-ray as the Arcane aim authority; leave editor ray tools untouched.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_309_ARCANE_NATIVE_RAY_AIM'

def once(html,old,new,why):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.309',why,n,old[:140]))
    return html.replace(old,new,1)

def apply(html):
    for key in (
      'function se192RenderRay(record,hit){','function se192VRFrame(){',
      'function se192Ray(record){','SE308_HIDE_XR_RAYS',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_308_ARCANE_HAND_GRIP_FIT'
    ):assert key in html,('v11.309 prerequisite',key)
    runtime=(ROOT/'runtime/arcane_ray_alignment_v11_309.js').read_text('utf8')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',runtime+'\nwindow.SWRLZ_FORGE_BUILD=',
      'suppress both independent controller-ray graphics in Arcane')
    old=" source.engine='§wyrl§ Engine · Maker v11.308';source.version=11.308;"
    if html.count(old)!=3:raise AssertionError(('v11.309 model metadata',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.309';source.version=11.309;")
    for before,after in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_308_ARCANE_HAND_GRIP_FIT',MARKER),
      ('ENGINE · MAKER v11.308','ENGINE · MAKER v11.309'),
      ('v11.308 · Arcane grip-pose fit and hidden XR beams',
       'v11.309 · native Arcane aim and complete VR ray hiding'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.308'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.309'"),
      ('<title>§wyrl§ Engine · Maker v11.308</title>',
       '<title>§wyrl§ Engine · Maker v11.309</title>')
    ):html=once(html,before,after,'release identity')
    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Arcane native WebXR ray aim and full controller beam cleanup',
      date='2026-11-06',changes=[
        'Owner Quest report: custom cyan/yellow §E ray beams sit to the left and slightly high compared with native Meta controller pointers; v11.308 did not actually suppress all controller-ray visuals.',
        'Source inspection revealed two independent renderers: se181 legacy Line and se192 tapered beam/cursor; se192 pivot can also inherit a saved yaw adjustment.',
        'In Blank VR Arcane Hands hide BOTH rendered beams and the se192 dot even after VR frame wrappers, and use zero extra yaw on the native WebXR target ray for Arcane hit tests.',
        'Preserve the raw target-ray pose for spell direction, the separate grip-space glove position, analog finger gestures, and existing spell controls. Outside Arcane, restore Spatial Editor beam ownership and the owner-saved yaw adjustment.',
        'Actual Meta pointer alignment and Quest 2 fit need the owner to verify; native OS aiming pose is not directly exposed for an automatic exact comparison.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
