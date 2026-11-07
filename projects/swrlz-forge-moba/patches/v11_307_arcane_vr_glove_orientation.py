"""§E v11.307 — correct Arcane Hands controller glove orientation.

Retain both independently editable starter models, skeletons and gesture poses.
This changes only the blank VR game glove mount: palm down, dorsal armor up,
fingers forward, thumbs inward, using the existing controller/ray/cast systems.
"""
import json

MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_307_ARCANE_VR_GLOVE_ORIENTATION'

def once(html,old,new,label):
    count=html.count(old)
    if count!=1:
        raise AssertionError(('v11.307',label,count,old[:120]))
    return html.replace(old,new,1)

def apply(html):
    assert 'function se279BuildGlove(side){' in html
    # Source coordinates: fingers +Y, palm +Z, dorsal -Z. XR target ray
    # coordinates: fingers -Z, dorsal +Y, palm -Y. A proper rotation also
    # inverts X, so use the oppositely authored mirrored glove per controller:
    # right gets thumb -X in XR, left gets thumb +X in XR.
    html=once(html,
       " const source=side==='left'?se279LeftScene():se212HandScene();",
       " // SE307_DORSAL_UP_CONTROLLER_GLOVES: match XR finger, palm, dorsal and thumb axes.\n const source=side==='left'?se212HandScene():se279LeftScene();",
       'select authored geometry with correct inward thumb after rotation')
    html=once(html,
       ' poseGroup.rotation.x=-Math.PI/2;',
       ' // Local +Y -> XR -Z (fingers forward); local -Z -> XR +Y (dorsal up).\n poseGroup.rotation.set(-Math.PI/2,Math.PI,0);',
       'orient armored backhand above the Quest controller instead of the palm')
    old_version=" source.engine='§wyrl§ Engine · Maker v11.306';source.version=11.306;"
    if html.count(old_version)!=3:
        raise AssertionError(('v11.307 model provenance',html.count(old_version)))
    html=html.replace(old_version,
      " source.engine='§wyrl§ Engine · Maker v11.307';source.version=11.307;")
    for before,after in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_306_SHEEP_PURSUIT_PERFORMANCE',MARKER),
      ('ENGINE · MAKER v11.306','ENGINE · MAKER v11.307'),
      ('v11.306 · Sheep Tag pursuit routing and frame diagnostics',
       'v11.307 · Arcane VR glove dorsal orientation'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.306'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.307'"),
      ('<title>§wyrl§ Engine · Maker v11.306</title>',
       '<title>§wyrl§ Engine · Maker v11.307</title>')
    ):
        html=once(html,before,after,'runtime identity')
    marker='const SE_RELEASE_NOTES='
    at=html.index(marker)+len(marker)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Arcane VR Gloves: correct upright dorsal orientation',
      date='2026-11-06',changes=[
        'Correct Blank VR Arcane Hands glove orientation: fingertips point along the controller target ray, the armored dorsal surface faces upward, and the palm faces downward when held level.',
        'The rotation needed to restore the backhand also inverts the X thumb axis; select the mirrored authored geometry on the opposite XR side so the physical right thumb remains inward on the left and vice versa.',
        'Preserve independently editable starter models, 17-bone rig weights, animations, grip and trigger gestures, tracked controller handedness, equipped spells, ray direction, Spell Lab casting and Sheep Tag.',
        'Owner Quest 2 visual acceptance remains pending; only source orientation and smoke checks are verified.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
