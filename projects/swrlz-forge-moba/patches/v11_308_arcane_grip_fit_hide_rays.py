"""§E v11.308 — grip-anchored Arcane gloves and ray-free spellcasting view.

The Quest controller target ray stays live for spell aim and existing input.
Only the two Blank VR · Arcane Hands meshes use grip-space mounting and
visually hide the cyan/yellow XR pointer lines. Other game/editor XR unchanged.
"""
import json

MARKER='SWYRL_ENGINE_DEPLOY_MARKER: V11_308_ARCANE_HAND_GRIP_FIT'

def once(html,old,new,why):
    n=html.count(old)
    if n!=1:raise AssertionError(('v11.308',why,n,old[:160]))
    return html.replace(old,new,1)

def apply(html):
    for key in (
      'SE307_DORSAL_UP_CONTROLLER_GLOVES',
      'function se279BuildGlove(side){',
      'function se279Cleanup(){',
      'function se279XRFrame(){',
      'function se280MageFrame(){',
      'SWYRL_ENGINE_DEPLOY_MARKER: V11_307_ARCANE_VR_GLOVE_ORIENTATION'
    ):
        assert key in html,('v11.308 prerequisite',key)

    # Proper grip-space mounts follow the actual held Touch controller rather
    # than its target-ray pose. Keep the already-verified v11.307 hand axes.
    html=once(html,
      " poseGroup.position.set(side==='left'?-.014:.014,-.034,.108);",
      " // SE308_GLOVE_FIT: slight inward/wrist clearance correction in grip space.\n poseGroup.position.set(side==='left'?-.012:.012,-.022,.116);",
      'nudge wrist anchor for Quest Touch grip-space fit')
    html=once(html,
      ' const modelGroup=new THREE.Group();modelGroup.scale.setScalar(.12);poseGroup.add(modelGroup);',
      ' const modelGroup=new THREE.Group();modelGroup.scale.setScalar(.112);poseGroup.add(modelGroup);',
      'modestly reduce oversized glove proportions while keeping sculpt intact')

    html=once(html,
      "const se279Hands={attached:new Map(),lastError:'',updates:0};",
      "const se279Hands={attached:new Map(),gripAnchors:new Map(),lastError:'',updates:0};",
      'track studio-owned grip anchor groups for cleanup')
    html=once(html,
      'function se279Cleanup(){\n for(const view of se279Hands.attached.values())se279ReleaseHand(view);\n se279Hands.attached.clear();\n}',
      """function se279Cleanup(){
 for(const view of se279Hands.attached.values())se279ReleaseHand(view);
 se279Hands.attached.clear();
 for(const grip of se279Hands.gripAnchors.values())grip.removeFromParent();
 se279Hands.gripAnchors.clear();
}""",
      'release grip-space objects on VR session or project exit')

    anchor="""// SE308_GRIP_ANCHOR: WebXR gripSpace tracks the held controller body.
 // The target-ray controller remains in use for spell direction and button input.
function se308GloveAnchor(side,record){
 if(!record?.input?.gripSpace||typeof renderer.xr.getControllerGrip!=='function')
  return record.controller; // safe for ray-only input devices
 const grip=renderer.xr.getControllerGrip(record.index);
 if(!grip)return record.controller;
 if(!grip.parent){scene.add(grip);se279Hands.gripAnchors.set(side,grip);}
 return grip;
}
function se308DropGrip(side){
 const grip=se279Hands.gripAnchors.get(side);
 if(grip)grip.removeFromParent();
 se279Hands.gripAnchors.delete(side);
}
"""
    html=once(html,'function se279XRFrame(){',anchor+'function se279XRFrame(){',
      'give gloves their own tracked grip-space anchor without changing aim rays')
    html=once(html,
      """function se279XRFrame(){
 if(!se181XR.session||!renderer.xr.isPresenting||currentProject?.kind!==se279GameId){""",
      """function se279XRFrame(){
 const se308Active=!!se181XR.session&&renderer.xr.isPresenting&&currentProject?.kind===se279GameId;
 // SE308_HIDE_XR_RAYS: presentation-only; raycasts, trigger spells and UI events remain intact.
 for(const r of se181XR.controllers)if(r.ray)r.ray.visible=!se308Active;
 if(!se308Active){""",
      'hide controller beams in Arcane Hands and restore in every other starter')

    html=once(html,
      """  if(!record){
   if(previous){se279ReleaseHand(previous);se279Hands.attached.delete(side);}
   continue;
  }""",
      """  if(!record){
   if(previous){se279ReleaseHand(previous);se279Hands.attached.delete(side);}
   se308DropGrip(side);
   continue;
  }""",
      'dispose disconnected grip mounts')

    html=once(html,
      """  if(!hand){
   try{
    hand=se279BuildGlove(side);record.controller.add(hand.root);
    se279Hands.attached.set(side,hand);
   }catch(e){se279Hands.lastError=String(e);console.error('VR glove build',e);continue;}
  }
  if(hand.root.parent!==record.controller)record.controller.add(hand.root);
  se279Animate(hand,record);""",
      """  const anchor=se308GloveAnchor(side,record);
  if(!hand){
   try{
    hand=se279BuildGlove(side);anchor.add(hand.root);
    se279Hands.attached.set(side,hand);
   }catch(e){se279Hands.lastError=String(e);console.error('VR glove build',e);continue;}
  }
  if(hand.root.parent!==anchor)anchor.add(hand.root);
  se279Animate(hand,record);""",
      'mount gesture-driven glove meshes in grip space with ray-only fallback')

    # Keep floating spell labels anchored to the same pose as the glove, not
    # the physically different aim ray, preserving all spell directions.
    html=once(html,
      ' sprite.scale.set(.36,.098,1);sprite.renderOrder=10012;record.controller.add(sprite);',
      """ sprite.scale.set(.36,.098,1);sprite.renderOrder=10012;
 const gloveMount=se279Hands.attached.get(side)?.root?.parent||record.controller;
 gloveMount.add(sprite);""",
      'locate equipped spell label beside the glove rather than a detached aim ray')

    old=" source.engine='§wyrl§ Engine · Maker v11.307';source.version=11.307;"
    if html.count(old)!=3:raise AssertionError(('v11.308 provenance',html.count(old)))
    html=html.replace(old," source.engine='§wyrl§ Engine · Maker v11.308';source.version=11.308;")
    for before,after in (
      ('SWYRL_ENGINE_DEPLOY_MARKER: V11_307_ARCANE_VR_GLOVE_ORIENTATION',MARKER),
      ('ENGINE · MAKER v11.307','ENGINE · MAKER v11.308'),
      ('v11.307 · Arcane VR glove dorsal orientation',
       'v11.308 · Arcane grip-pose fit and hidden XR beams'),
      ("window.SWRLZ_FORGE_BUILD={version:'v11.307'",
       "window.SWRLZ_FORGE_BUILD={version:'v11.308'"),
      ('<title>§wyrl§ Engine · Maker v11.307</title>',
       '<title>§wyrl§ Engine · Maker v11.308</title>')
    ):html=once(html,before,after,'release identity')

    key='const SE_RELEASE_NOTES='
    at=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[at:])
    notes.update(title='Arcane VR grip-space glove alignment and hidden rays',
      date='2026-11-06',changes=[
        'Owner Quest screenshot: both gloves render in correct dorsal-up orientation, but are still slightly misaligned; visible cyan and yellow target-ray beams clutter the Arcane Hand spellcasting view.',
        'Use WebXR gripSpace for glove meshes when available (e.g. Quest Touch); preserve target-ray fallback and 17-bone analog trigger/grip gestures. Apply a small wrist and proportional fit adjustment.',
        'Hide only the colored controller ray LINE renderables in Blank VR Arcane Hands; keep target-ray transforms, hit tests and spell casting active. Restore rays automatically for other XR game/editor views.',
        'Attach equipped spell labels to the glove pose for consistent position; preserve independent spell loadouts and all particle and gesture logic.',
        'Owner Quest 2 visual fit acceptance pending; source-build and localized behavior checks do not prove physical calibration.'
      ])
    return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[at+width:]
