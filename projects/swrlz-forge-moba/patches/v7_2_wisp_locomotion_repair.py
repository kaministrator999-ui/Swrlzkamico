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

    # Patch the current controller around its collision call, independent of the
    # historical whitespace/body form.
    candidates=["resolveHeroCollision(next,0.55);h.position.x=next.x;h.position.z=next.z;","resolveHeroCollision(next,h.userData.colliderRadius||.46);if(Number.isFinite(next.x)&&Number.isFinite(next.z)){h.position.x=next.x;h.position.z=next.z;}"]
    needle=next((q for q in candidates if q in s),None)
    if not needle: raise RuntimeError("v7.2 current Wisp collision statement missing")
    repl="""if(h.userData.hoverFlight){
    const start=h.position.clone(),desired=next.clone(),moved=p=>Math.hypot(p.x-start.x,p.z-start.z)>.0001;
    resolveHeroCollision(next,h.userData.colliderRadius||.46);
    if(moved(next)){h.position.x=next.x;h.position.z=next.z;}
    else{
      const sx=start.clone();sx.x=desired.x;resolveHeroCollision(sx,h.userData.colliderRadius||.46);
      const sz=start.clone();sz.z=desired.z;resolveHeroCollision(sz,h.userData.colliderRadius||.46);
      if(moved(sx)||moved(sz)){h.position.x=moved(sx)?sx.x:start.x;h.position.z=moved(sz)?sz.z:start.z;}
      else{h.position.x=desired.x;h.position.z=desired.z;}
    }
  }else{resolveHeroCollision(next,.55);h.position.x=next.x;h.position.z=next.z;}"""
    s=_once(s,needle,repl)

    # Guard against a stale stick capture when entering Play on mobile.
    marker="resetStick($('moveStick'),fpMove);resetStick($('lookStick'),fpLook);"
    s=_once(s,marker,marker+"fpMove.x=0;fpMove.y=0;fpLook.x=0;fpLook.y=0;")
    return s
