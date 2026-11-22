"""§E v11.537 — original untextured editable robotic humanoid mannequin starter."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_536_NATIVE_ACCOUNT_IMAGE_REFERENCE'
MARKER = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_537_ROBOTIC_HUMANOID_MANNEQUIN'

def one(html, before, after, label):
    count = html.count(before)
    if count != 1:
        raise AssertionError(('se537', label, count, before[:120]))
    return html.replace(before, after, 1)

def apply(html):
    runtime = (ROOT/'runtime/robotic_humanoid_mannequin_v11_537.js').read_text('utf8')
    for required in ('se537MakeMannequin','se537ValidateScene','SE537_HUMANOID_END',
                     'ModelAtelier.syncProject()','se232ActivateSelectedModelWorkspace()'):
        assert required in runtime, required
    html = one(html, 'window.SWRLZ_FORGE_BUILD=', runtime+'\nwindow.SWRLZ_FORGE_BUILD=', 'native geometry starter')
    card = (
      '<button class="project-card den" data-project-template="robotic-humanoid-mannequin">'
      '<span class="project-icon">♙</span>'
      '<strong>Robotic Humanoid Mannequin</strong>'
      '<span class="template-tag">STARTER MODEL · UNTEXTURED T-POSE</span>'
      '<p>Professional grayscale anatomical robot in a horizontal T-pose. Detailed cranial features,'
      ' organic chest and muscle plates, exposed shoulder/elbow/knee mechanisms, five individually'
      ' articulated fingers per hand and detailed feet. Native editable mesh sections; no textures.</p>'
      '<span class="hint den-glow">Open in Model Studio</span>'
      '</button>'
    )
    html = one(html,'<button class="project-card den" data-project-template="sorting-hat">',
               card+'<button class="project-card den" data-project-template="sorting-hat">',
               'Starter Models card')
    html = one(html, 'function se128LaunchStartupProject(){',
      """function se128LaunchStartupProject(){
 if(new URLSearchParams(location.search).get('project')==='robotic-humanoid-mannequin'){
  window.se128StartupPending=true;
  queueMicrotask(()=>Promise.resolve(se537OpenMannequin(true))
   .catch(error=>console.error('Humanoid mannequin startup',error))
   .finally(()=>{window.se128StartupPending=false;}));
  return;
 }
""", 'deep-link route')
    for before,after in (
      (PREVIOUS,MARKER),
      ('ENGINE · MAKER v11.536','ENGINE · MAKER v11.537'),
      ('v11.536 · native Google code and image references','v11.537 · robotic humanoid T-pose mannequin'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.536'","window.SWRLZ_FORGE_BUILD={version:'v11.537'"),
      ('<title>§wyrl§ Engine · Maker v11.536</title>','<title>§wyrl§ Engine · Maker v11.537</title>')
    ):
        html=one(html,before,after,'version')
    previous=" source.engine='§wyrl§ Engine · Maker v11.536';source.version=11.536;"
    assert html.count(previous)==5
    html=html.replace(previous,previous.replace('11.536','11.537'))
    start=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,width=json.JSONDecoder().raw_decode(html[start:])
    notes['history']=[n for n in notes['history'] if n.get('version')!='v11.536']
    notes['history'].insert(0,{'version':'v11.536','changes':notes['changes']})
    notes.update(version='v11.537',date='2026-11-22',
      title='Robotic Humanoid — professional untextured T-pose starter',
      changes=[
        'Added a fully native robotic humanoid mannequin to Projects → Starter Models with optional direct Model Studio launch.',
        'Procedurally authored smooth organic proportions, a mechanical cranial face, sculpted torso, shoulders, arms, hips and legs, exposed joints, individual finger segments and five toes per foot.',
        'Original indexed topology geometry: no image texture, external mesh, texture download or substitute renderer. Separate named parts remain selectable and editable.',
        'Native asset and project routing keep existing save/clone, part selection, mobile/Quest workflows, UV tooling and project histories intact.',
        'This is an unrigged T-pose modeling starter; physical phone and Quest acceptance remains owner testing.'
      ])
    release=json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')
    return html[:start]+release+html[start+width:]
