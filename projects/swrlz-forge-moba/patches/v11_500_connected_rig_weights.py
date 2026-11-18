"""§E v11.500 — weighted vertex display and connected rest-joint editing.
One live Model Atelier renderer; keep authored geometry/UV and clip lineage intact.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_500_CONNECTED_RIG_WEIGHTS'
def once(html,old,new,label):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.500',label,n,old[:120]))
    return html.replace(old,new,1)
def apply(html):
    assert 'SWYRL_ENGINE_DEPLOY_MARKER: V11_499_RIG_STUDIO_POLISH' in html
    math=(ROOT/'runtime/model_rig_connected_math_v11_500.js').read_text('utf8')
    ui=(ROOT/'runtime/model_rig_connected_edit_v11_500.js').read_text('utf8')
    css=(ROOT/'runtime/model_rig_connected_edit_v11_500.css').read_text('utf8')
    for key in ('se500RestMath','quaternionBetween','descendants'):
        assert key in math,key
    for key in ('se500RigEdit','se500WeightsCount','se500LockLength','syncRestTransform','collectWeights'):
        assert key in ui,key
    html=once(html,
      'window.SWYRL_ENGINE_RIG_POLISH_499=se499RigPolish;',
      'window.SWYRL_ENGINE_RIG_POLISH_499=se499RigPolish;\n'+math+'\n'+ui,
      'native rig studio code extension')
    if '</head>' not in html:raise AssertionError('Missing main HTML head')
    html=html.replace('</head>','<style id="se500ConnectedRig">'+css+'</style>\n</head>',1)
    for old,new in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_499_RIG_STUDIO_POLISH',MARKER),
      ('ENGINE · MAKER v11.499','ENGINE · MAKER v11.500'),
      ('v11.499 · isolated rig and animation studios with 3D bone controls',
       'v11.500 · connected bone editing and real weight visualization'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.499'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.500'"),
      ('<title>§wyrl§ Engine · Maker v11.499</title>',
       '<title>§wyrl§ Engine · Maker v11.500</title>')
    ):html=once(html,old,new,'version identity')
    old=" source.engine='§wyrl§ Engine · Maker v11.499';source.version=11.499;"
    if html.count(old)!=5:raise AssertionError(('model provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.500';source.version=11.500;")
    label='const SE_RELEASE_NOTES='
    at=html.index(label)+len(label)
    notes,n=json.JSONDecoder().raw_decode(html[at:])
    notes['history']=[x for x in notes.get('history',[]) if x.get('version')!='v11.499']
    notes['history'].insert(0,{'version':'v11.499','changes':notes.get('changes',[])})
    notes.update(version='v11.500',date='2026-11-17',
      title='Connected bone dragging and visible skin-weighted vertices',
      changes=[
        'Selecting a cloth bone from the rig panel or tapping a 3D joint highlights its actual attached mesh vertices using the already authored GPU skin indices and weights, with colored influence strength and a minimum-weight slider.',
        'Rigging joint drags are touch-friendly and constrained to maintain parent-child segment length by default; children and their automatic influence envelopes follow as a connected subtree.',
        'Optional unlocked translation, numeric joint transforms and bone-placement Undo use the same safe whole-chain editing path. Root movement translates the complete skeleton.',
        'Rest edits update the existing bind skeleton at neutral before restoring current pose; no separate mesh import, duplicate project, UV coordinate rewrite or unwanted animation clip replacement.',
        'Existing rigged Sorting Hat variants, hand animation controls, camera, model studio modes, project saves and revisions remain intact.',
        'Automated source and math checks verify connected joint lengths and stable geometry. On-device Moto/Quest usability remains a separate acceptance step.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</',r'<\/')+html[at+n:]
