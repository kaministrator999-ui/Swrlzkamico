"""§wyrl§ Engine v7.2: restore Wisp horizontal locomotion with safe slide fallback."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.2 token missing: "+old[:220])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V7_1_FRACTURE_FORGE_BREATHING_ROOM":"V7_2_WISP_LOCOMOTION_REPAIR",
      "Maker v7.1":"Maker v7.2","MAKER v7.1":"MAKER v7.2",
      "v7.1 · FRACTURE FORGE BREATHING ROOM":"v7.2 · WISP LOCOMOTION REPAIR",
      "version:'v7.1'":"version:'v7.2'",
      "version:'swyrl-engine-agent-v5.1'":"version:'swyrl-engine-agent-v5.2'",
      "engine:'§wyrl§ Engine · Maker v7.1'":"engine:'§wyrl§ Engine · Maker v7.2'",
      "version:7.1":"version:7.2",
      "editorLog('§wyrl§ Engine v7.1 initialized · expanded Fracture Forge · mobile breathing room','ok')":"editorLog('§wyrl§ Engine v7.2 initialized · Wisp horizontal locomotion repaired','ok')"
    }.items(): s=_once(s,a,b)

    # v6.7 intentionally preserved the historical horizontal controller. The current
    # symptom is a dense-scene collision deadlock, so bypass horizontal collision only
    # for the flying Wisp after updateHero has run; vertical hover remains unchanged.
    marker="  h.rotation.y=fpYaw;"
    inject="""  if(h.userData.hoverFlight){
    const keyRight=(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0);
    const keyForward=(keys.has('w')||keys.has('arrowup')?1:0)-(keys.has('s')||keys.has('arrowdown')?1:0);
    const ri=THREE.MathUtils.clamp(keyRight+fpMove.x,-1,1),fi=THREE.MathUtils.clamp(keyForward-fpMove.y,-1,1);
    const fwd=new THREE.Vector3(Math.sin(fpYaw),0,-Math.cos(fpYaw)),rgt=new THREE.Vector3(Math.cos(fpYaw),0,Math.sin(fpYaw)),freeMove=new THREE.Vector3().addScaledVector(fwd,fi).addScaledVector(rgt,ri);
    if(freeMove.lengthSq()>1)freeMove.normalize();
    if(freeMove.lengthSq()>.0001){const sp=h.userData.moveSpeed||6;h.position.addScaledVector(freeMove,sp*dt);}
  }
"""
    s=_once(s,marker,inject+marker)

    # Guard against a stale stick capture when entering Play on mobile.
    marker="resetStick($('moveStick'),fpMove);resetStick($('lookStick'),fpLook);"
    s=_once(s,marker,marker+"fpMove.x=0;fpMove.y=0;fpLook.x=0;fpLook.y=0;")
    return s
