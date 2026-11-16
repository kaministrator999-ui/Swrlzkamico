"""Release a two-controller VR workbench gesture on either grip release or tracking loss."""
import json
def one(src,old,new):
 assert src.count(old)==1,(old[:90],src.count(old))
 return src.replace(old,new,1)
def apply(html):
 html=one(html,
 "if(!record.gripTracked||!se340VisibleSession())return se340CancelGesture('Tracking changed; preview canceled.');",
 """if(!se340VisibleSession())return se340CancelGesture('VR session changed; preview canceled.');
  // A release event may arrive after the grip pose stops tracking. Release must
  // still terminate the camera gesture, never leave the workbench captured.
  if(g.kind!=='view'&&!record.gripTracked)return se340CancelGesture('Tracking changed; preview canceled.');""")
 html=one(html,
 "if(!se340VisibleSession()||!g.record.targetTracked||!g.record.gripTracked){se340CancelGesture('Tracking changed; preview canceled.');return;}",
 """if(!se340VisibleSession()||!g.record.targetTracked||!g.record.gripTracked){se340CancelGesture('Tracking changed; preview canceled.');return;}
  if(g.kind==='view'&&g.pair&&(!s.inputSample?.held.pan||!s.inputSample?.held.grab)){
   // Both hands are required for pinch/orbit; ending either grip ends capture.
   se340FinishGesture(g.record);return;
  }""")
 html=one(html,
 """if(!pair&&g.pair){const a=se340GripPose(g.pair.left),b=se340GripPose(g.pair.right);if(a&&b){const span=b.position.clone().sub(a.position);pair={a,b,span,distance:span.length(),mid:a.position.clone().add(b.position).multiplyScalar(.5)};}}""",
 """// Do not reconstruct a released pair from still-tracked controller poses.
   // Tracking persists after grip-up and would otherwise rotate indefinitely.""")
 html=one(html,
 """if(['grab','pan','two-hand'].includes(event.action)&&record)se340FinishGesture(record);""",
 """if(['grab','pan','two-hand'].includes(event.action)&&record)se340FinishGesture(record);""")
 html=one(html,
 """for(const record of s.controllers){
  const grip=sample.buttons[record.input?.handedness==='left'?'LG':'RG'];record.held=!!grip?.down;""",
 """// Frame-level physical-state fallback for missed WebXR squeezeend events.
  // Never hold a camera gesture hostage to a stale event or tracked grip pose.
  if(s.gesture?.kind==='view'){
   const g=s.gesture,side=g.record.input?.handedness;
   const primary=sample.buttons[side==='left'?'LG':'RG'];
   const pairEnded=g.pair&&(!sample.held.pan||!sample.held.grab);
   if(!primary?.down||pairEnded)se340FinishGesture(g.record);
  }
  for(const record of s.controllers){
  const grip=sample.buttons[record.input?.handedness==='left'?'LG':'RG'];record.held=!!grip?.down;""")
 html=one(html,"SWYRL_ENGINE_DEPLOY_MARKER: V11_466_RING_ARC_MODELING","SWYRL_ENGINE_DEPLOY_MARKER: V11_467_VR_GRIP_RELEASE")
 html=one(html,"window.SWRLZ_FORGE_BUILD={version:'v11.466'","window.SWRLZ_FORGE_BUILD={version:'v11.467'")
 html=one(html,"<title>§wyrl§ Engine · Maker v11.466</title>","<title>§wyrl§ Engine · Maker v11.467</title>")
 html=one(html,"ENGINE · MAKER v11.466","ENGINE · MAKER v11.467")
 html=one(html,"v11.466 · ring and arc modeling","v11.467 · VR grip release recovery")
 html=html.replace(" source.engine='§wyrl§ Engine · Maker v11.466';source.version=11.466;"," source.engine='§wyrl§ Engine · Maker v11.467';source.version=11.467;")
 key='const SE_RELEASE_NOTES=';at=html.index(key)+len(key)
 notes,length=json.JSONDecoder().raw_decode(html[at:])
 notes['history'].insert(0,{'version':'v11.466','changes':notes['changes']})
 notes.update(version='v11.467',title='VR two-grip camera release recovery',changes=[
  'VR two-controller pinch/zoom and workbench orbit end immediately when either grip is released.',
  'Missed squeezeend events are recovered from the current physical grip state; tracked poses no longer resurrect released grips.',
  'Release after tracking loss cannot leave the camera in a stuck gesture; model edits and VR menus remain unchanged.'
 ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':'))+html[at+length:]
