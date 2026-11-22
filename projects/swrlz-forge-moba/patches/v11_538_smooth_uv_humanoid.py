"""§E v11.538 — replace the segmented mannequin with a single smooth UV-painted body."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIOUS='SWYRL_ENGINE_DEPLOY_MARKER: V11_537_ROBOTIC_HUMANOID_MANNEQUIN'
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_538_SMOOTH_UV_HUMANOID'

def once(html,before,after,label):
    n=html.count(before)
    if n!=1:
        raise AssertionError(('se538',label,n,before[:110]))
    return html.replace(before,after,1)

def apply(html):
    runtime=(ROOT/'runtime/smooth_humanoid_starter_v11_538.js').read_text('utf8')
    for token in ('se538ValidateHumanoid','se538OpenHumanoid',
                  'se537OpenMannequin=se538OpenHumanoid','SE538_SMOOTH_HUMANOID_END'):
        assert token in runtime,token
    # Append after the original v11.537 generator. Existing project routing and
    # direct deep links already call se537OpenMannequin by live binding.
    html=once(html,'window.SWRLZ_FORGE_BUILD=',runtime+'\nwindow.SWRLZ_FORGE_BUILD=','native loader')
    html=once(html,'<strong>Robotic Humanoid Mannequin</strong>',
              '<strong>Futuristic Humanoid · Smooth</strong>','starter name')
    html=once(html,
       '<span class="template-tag">STARTER MODEL · UNTEXTURED T-POSE</span>',
       '<span class="template-tag">STARTER MODEL · ONE SMOOTH UV BODY</span>',
       'card tag')
    previous=(
       '<p>Professional grayscale anatomical robot in a horizontal T-pose. Detailed cranial features,'
       ' organic chest and muscle plates, exposed shoulder/elbow/knee mechanisms, five individually'
       ' articulated fingers per hand and detailed feet. Native editable mesh sections; no textures.</p>'
    )
    updated=(
       '<p>One continuous sculpted organic humanoid in a horizontal T-pose.'
       ' Futuristic satin and graphite surface details, six UV atlas islands,'
       ' and one embedded editable PNG material. No floating armor chunks.</p>'
    )
    html=once(html,previous,updated,'starter description')
    for before,after in (
        (PREVIOUS,MARKER),
        ('ENGINE · MAKER v11.537','ENGINE · MAKER v11.538'),
        ('v11.537 · robotic humanoid T-pose mannequin','v11.538 · one smooth UV humanoid mesh'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.537'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.538'"),
        ('<title>§wyrl§ Engine · Maker v11.537</title>',
         '<title>§wyrl§ Engine · Maker v11.538</title>')
    ):
        html=once(html,before,after,'release identity')
    previous=" source.engine='§wyrl§ Engine · Maker v11.537';source.version=11.537;"
    assert html.count(previous)==5
    html=html.replace(previous,previous.replace('11.537','11.538'))
    start=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,width=json.JSONDecoder().raw_decode(html[start:])
    notes['history']=[n for n in notes['history'] if n.get('version')!='v11.537']
    notes['history'].insert(0,{'version':'v11.537','changes':notes['changes']})
    notes.update(version='v11.538',date='2026-11-22',
      title='Futuristic Humanoid — single smooth UV-painted mesh',
      changes=[
        'Replaced the visible 178-piece assembled anatomical model with one connected original humanoid body shell, smoothed at shoulders, hips, neck, torso, knees and hands.',
        'Baked UV-indexed topology and six dedicated islands for head, trunk, bilateral arms and bilateral legs. Embedded an original 1024 px grayscale/graphite/teal material atlas directly into the native project.',
        'Only one topologyMesh object is used. Native Model Studio selection, sculpting, history, clone/save, rig studio and UV tools remain routed through the existing project system.',
        'No texture-network dependency or model generation on the phone; all geometry is pre-baked in the bundled editable scene. The prototype is not skeletal-rigged yet.',
        'Physical Moto and Quest appearance and rigging acceptance remain owner testing.'
      ])
    release=json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
    return html[:start]+release+html[start+width:]
