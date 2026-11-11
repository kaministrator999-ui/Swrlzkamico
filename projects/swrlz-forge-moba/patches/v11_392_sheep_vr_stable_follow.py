"""§E v11.392 — stabilize the Sheep Tag immersive VR follow camera.

Owner test: FREE stopped repainting/geometric distortion; small hard freezes
persisted. Avoid mutating XR reference space every headset display frame.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_392_SHEEP_VR_STABLE_FOLLOW'
def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise AssertionError(('v11.392',label,n,old[:90]))
    return s.replace(old,new,1)
def apply(html):
    script=(ROOT/'runtime/sheep_vr_stable_follow_v11_392.js').read_text('utf8')
    for t in ('function se392FollowPlan(distance,at)','SWYRL_ENGINE_SHEEP_STABLE_FOLLOW_392'):
        assert t in script,t
    assert 'SWYRL_ENGINE_SHEEP_VR_Y_MENU_391' in html
    before="""  const remaining=wanted.sub(se200.applied);
  if(remaining.lengthSq()<.000625){se200.idleFrames++;return;}
  const delta=remaining.multiplyScalar(1-Math.exp(-timeStep*9));
  const maxStep=timeStep*13;
  if(maxStep>0&&delta.length()>maxStep)delta.setLength(maxStep);
  if(delta.lengthSq()<.000004){se200.idleFrames++;return;}
  if(se195MoveRig(delta.x,delta.y,delta.z)){
    se200.applied.add(delta);se200.referenceWrites++;
  }else se200.lastError='XR reference space translation unavailable';"""
    after="""  const remaining=wanted.sub(se200.applied);
  if(remaining.lengthSq()<.000625){se200.idleFrames++;return;}
  let delta;
  if(se193.follow){
    const distance=remaining.length();
    const allowed=se392FollowPlan(distance,performance.now());
    if(!allowed){se200.idleFrames++;return;}
    delta=remaining.multiplyScalar(allowed/distance);
  }else{
    // FREE is preserved as the owner's validated low-distortion fallback.
    delta=remaining.multiplyScalar(1-Math.exp(-timeStep*9));
    const maxStep=timeStep*13;
    if(maxStep>0&&delta.length()>maxStep)delta.setLength(maxStep);
  }
  if(delta.lengthSq()<.000004){se200.idleFrames++;return;}
  if(se195MoveRig(delta.x,delta.y,delta.z)){
    se200.applied.add(delta);se200.referenceWrites++;
    if(se193.follow)se392FollowCommit(performance.now(),delta.length());
  }else se200.lastError='XR reference space translation unavailable';"""
    html=once(html,before,after,'v11.200 follow reference-space writes')
    html=once(html,"""    se200.applied.copy(wanted);
    se200.anchorReady=true;se200.trackedUnit=unit.id;""",
     """    se200.applied.copy(wanted);
    se392FollowCommit(performance.now(),offset.length());
    se200.anchorReady=true;se200.trackedUnit=unit.id;""",'one-time anchor counts toward cadence')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',script+'\nwindow.SWRLZ_FORGE_BUILD=','late follow metrics')
    for before,after in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_391_SHEEP_QUEST_Y_TOOLS_RADIAL',MARKER),
        ('ENGINE · MAKER v11.391','ENGINE · MAKER v11.392'),
        ('v11.391 · Quest Sheep Tag Y quick tools radial',
         'v11.392 · stable Sheep Tag VR follow camera'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.391'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.392'"),
        ('<title>§wyrl§ Engine · Maker v11.391</title>',
         '<title>§wyrl§ Engine · Maker v11.392</title>')
    ]:html=once(html,before,after,'release identity')
    previous=" source.engine='§wyrl§ Engine · Maker v11.391';source.version=11.391;"
    assert html.count(previous)==5,('v11.392 provenance',html.count(previous))
    html=html.replace(previous," source.engine='§wyrl§ Engine · Maker v11.392';source.version=11.392;")
    key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
    notes,size=json.JSONDecoder().raw_decode(html[at:])
    if not any(x.get('version')=='v11.391' for x in notes.get('history',[])):
        notes.setdefault('history',[]).insert(0,{'version':'v11.391','changes':notes.get('changes',[])})
    notes.update(version='v11.392',date='2026-11-10',
      title='Quest Sheep Tag: bounded follow-camera reference-space updates',
      changes=[
        'Owner Quest A/B: FREE eliminates full-scene geometric distortion and most lag, but a few hard freezes persist. Isolate the follow-camera feedback rather than reducing graphics indiscriminately.',
        'Limit FOLLOW to at most one XR origin adjustment per 140ms and require at least 12cm of target error; clamp each applied adjustment to 62cm. Initial game framing and native headset tracking are retained.',
        'FREE camera logic is unchanged; native game physics, multiplayer host/guest, fog, building, mouse/touch, controller shortcuts and saved projects are untouched.',
        'Follow-write diagnostics added; existing frame-gap/head-motion statistics remain the separate evidence for intermittent hard freezes. Quest hardware verification pending.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+size:]
