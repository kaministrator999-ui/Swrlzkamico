"""§E v11.540: smooth one-piece mannequin with individually modeled fingertips."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OLD='SWYRL_ENGINE_DEPLOY_MARKER: V11_539_IMMERSIVE_SCULPT_LOAD'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_540_HUMANOID_FIVE_DIGIT'

def once(html,old,new,label):
    n=html.count(old)
    if n!=1:
        raise AssertionError(('se540',label,n,old[:100]))
    return html.replace(old,new,1)

def apply(html):
    runtime=(ROOT/'runtime/futuristic_humanoid_five_digit_v11_540.js').read_text('utf8')
    for token in ('se540OpenHumanoid','se540ValidateHandScene',
                  'se537OpenMannequin=se540OpenHumanoid',
                  'SE540_HUMANOID_HANDS_END'):
        assert token in runtime,token
    html=once(html,'window.SWRLZ_FORGE_BUILD=',runtime+'\nwindow.SWRLZ_FORGE_BUILD=','runtime')
    html=once(html,'<strong>Futuristic Humanoid · Smooth</strong>',
              '<strong>Futuristic Humanoid · Detailed Hands</strong>','starter title')
    html=once(html,'<span class="template-tag">STARTER MODEL · ONE SMOOTH UV BODY</span>',
              '<span class="template-tag">ONE UV BODY · FIVE FINGERS PER HAND</span>','starter label')
    html=once(html,
      '<p>One continuous sculpted organic humanoid in a horizontal T-pose.'
      ' Futuristic satin and graphite surface details, six UV atlas islands,'
      ' and one embedded editable PNG material. No floating armor chunks.</p>',
      '<p>Refined organic sci-fi anatomy with wrists, broad palms, four'
      ' separated tapered fingers and an opposable thumb on each hand.'
      ' One continuous UV-ready body, not assembled floating parts.</p>',
      'starter description')
    for before,after in (
        (OLD,MARKER),
        ('ENGINE · MAKER v11.539','ENGINE · MAKER v11.540'),
        ('v11.539 · responsive immersive sculpt and VR project loading',
         'v11.540 · anatomical humanoid with five-digit hands'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.539'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.540'"),
        ('<title>§wyrl§ Engine · Maker v11.539</title>',
         '<title>§wyrl§ Engine · Maker v11.540</title>')
    ):
        html=once(html,before,after,'release')
    before=" source.engine='§wyrl§ Engine · Maker v11.539';source.version=11.539;"
    assert html.count(before)==5
    html=html.replace(before,
      " source.engine='§wyrl§ Engine · Maker v11.540';source.version=11.540;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[h for h in notes['history'] if h.get('version')!='v11.539']
    notes['history'].insert(0,{'version':'v11.539','changes':notes['changes']})
    notes.update(version='v11.540',date='2026-11-22',
      title='Futuristic Humanoid — refined unified anatomy and five-digit hands',
      changes=[
        'Rebuilt humanoid with a rounded defined palm, four independently silhouetted tapered fingers and an opposable thumb on each hand. All hand surfaces fuse into one watertight body.',
        'Improved forearm/wrist transition, shoulder cap, upper torso, hips, knees and ankles without recreating floating anatomical parts.',
        'Selective fine-resolution geometry around hands retains finger separation while preserving phone/Quest native 9000-UV-vertex/16000-triangle limits.',
        'Retains existing six-region UV mapping and original embedded editable material atlas; no new image dependencies, extra renderers or forced reimports.',
        'Legacy starter identity, account saves, VR registration and other immersive sculpt improvements remain intact. Skeletal animation is separate work.'
      ])
    release=json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
    return html[:at]+release+html[at+n:]
