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

    # The legacy collision resolver can leave the candidate at the starting X/Z in a
    # dense den. For the flying Wisp, attempt full move, then independent X and Z
    # slides; if the legacy resolver rejects every candidate, permit the requested
    # hover translation rather than pinning the avatar forever.
    old="""  const speed=h.userData.moveSpeed||6;
  const next=h.position.clone().add(move.multiplyScalar(speed*dt));
  resolveHeroCollision(next,0.55);h.position.x=next.x;h.position.z=next.z;"""
    new="""  const speed=h.userData.moveSpeed||6;
  const delta=move.multiplyScalar(speed*dt),start=h.position.clone(),desired=start.clone().add(delta);
  if(h.userData.hoverFlight){
    const moved=(p)=>Math.hypot(p.x-start.x,p.z-start.z)>.0001;
    const full=desired.clone();resolveHeroCollision(full,h.userData.colliderRadius||.46);
    if(moved(full)){h.position.x=full.x;h.position.z=full.z;}
    else{
      const sx=start.clone();sx.x=desired.x;resolveHeroCollision(sx,h.userData.colliderRadius||.46);
      const sz=start.clone();sz.z=desired.z;resolveHeroCollision(sz,h.userData.colliderRadius||.46);
      if(moved(sx)||moved(sz)){h.position.x=moved(sx)?sx.x:start.x;h.position.z=moved(sz)?sz.z:start.z;}
      else{h.position.x=desired.x;h.position.z=desired.z;}
    }
  }else{
    const next=desired.clone();resolveHeroCollision(next,.55);h.position.x=next.x;h.position.z=next.z;
  }"""
    s=_once(s,old,new)

    # Guard against a stale stick capture when entering Play on mobile.
    marker="resetStick($('moveStick'),fpMove);resetStick($('lookStick'),fpLook);"
    s=_once(s,marker,marker+"fpMove.x=0;fpMove.y=0;fpLook.x=0;fpLook.y=0;")
    return s
