"""§E v11.363 — clear inherited Prism Jester sockets in four WebXR model starters."""
from pathlib import Path
import json
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_363_WEBXR_STARTER_SOCKET_FIX'

def once(s,old,new,description):
    n=s.count(old)
    if n!=1:
        raise AssertionError(('v11.363',description,n,old[:130]))
    return s.replace(old,new,1)

def apply(html):
    # Prior v11.294 Vanguard fix documented this exact failure path:
    # replacing canonical model parts leaves assemblies.sockets[].partId
    # pointing to nonexistent Prism Jester parts. The real loadProject()
    # validator throws "Invalid named socket" before opening the modeler.
    # Preserve the new controller meshGroups assembly, but remove only the
    # unrelated inherited canonical attachment/socket graph.
    html=once(html,
        ' m.meshGroups=[];m.poseFrames=[];m.poseNeutral=null;m.editedAt=\'local\';',
        ' m.meshGroups=[];m.assemblies=null;m.poseFrames=[];m.poseNeutral=null;m.editedAt=\'local\';',
        'hand model stale named sockets')
    html=once(html,
        ' model.poseFrames=[];model.poseNeutral=null;model.editedAt=\'local\';',
        ' model.assemblies=null;model.poseFrames=[];model.poseNeutral=null;model.editedAt=\'local\';',
        'controller model stale named sockets')
    html=once(html,
        '  const parts=source?.project?.modelAtelier?.parts;',
        "  // All four reference starters replace Prism Jester's original parts.\n"
        "  // Never carry its stale named socket/attachment graph into loadProject.\n"
        "  if(source?.project?.modelAtelier)source.project.modelAtelier.assemblies=null;\n"
        '  const parts=source?.project?.modelAtelier?.parts;',
        'starter-opening native load guard')
    for old,new,why in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_362_QUEST_CONTROLLER_HINTS',MARKER,'marker'),
        ('ENGINE · MAKER v11.362','ENGINE · MAKER v11.363','visible version'),
        ('v11.362 · live Quest Touch controllers and tool-aware labels',
         'v11.363 · WebXR hand and controller starter open repair','headline'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.362'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.363'",'runtime version'),
        ('<title>§wyrl§ Engine · Maker v11.362</title>',
         '<title>§wyrl§ Engine · Maker v11.363</title>','title')
    ]:
        html=once(html,old,new,why)
    old=" source.engine='§wyrl§ Engine · Maker v11.362';source.version=11.362;"
    count=html.count(old)
    if count!=5:raise AssertionError(('v11.363 provenance',count))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.363';source.version=11.363;")
    at=html.index('const SE_RELEASE_NOTES=')+len('const SE_RELEASE_NOTES=')
    notes,length=json.JSONDecoder().raw_decode(html[at:])
    if not any(item.get('version')=='v11.362' for item in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.362','changes':notes.get('changes',[])})
    notes.update(version='v11.363',date='2026-11-08',
        title='WebXR anatomy and Quest 2 controller starter project loading fixed',
        changes=[
         'Fix WebXR Left Hand and WebXR Right Hand failing when clicked in Projects → Starter Models with Invalid named socket.',
         'Fix the same inherited named-socket problem for Quest 2 Touch Left/Right Controller project starters, retaining their seven editable sections, painted UVs and single native mesh group.',
         'Remove only the obsolete Prism Jester socket/attachment assembly on the four independent reference projects, exactly as the engine already does for the Vanguard model.',
         'Use the native Model Studio viewport, selection, UV import/export and project save system without new UI panels or geometry changes.',
         'Retain the v11.362 VR live Quest controller visuals and button labels, as well as previous modeling and game projects.'
        ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+length:]
