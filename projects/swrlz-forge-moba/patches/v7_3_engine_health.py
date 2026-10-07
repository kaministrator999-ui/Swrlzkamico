"""§wyrl§ Engine v7.3: unified flight controller + runtime diagnostics."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.3 token missing: "+old[:220])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V7_2_WISP_LOCOMOTION_REPAIR":"V7_3_ENGINE_HEALTH",
      "Maker v7.2":"Maker v7.3","MAKER v7.2":"MAKER v7.3",
      "v7.2 · WISP LOCOMOTION REPAIR":"v7.3 · ENGINE HEALTH",
      "version:'v7.2'":"version:'v7.3'",
      "version:'swyrl-engine-agent-v5.2'":"version:'swyrl-engine-agent-v5.3'",
      "engine:'§wyrl§ Engine · Maker v7.2'":"engine:'§wyrl§ Engine · Maker v7.3'",
      "version:7.2":"version:7.3",
      "editorLog('§wyrl§ Engine v7.2 initialized · Wisp horizontal locomotion repaired','ok')":"editorLog('§wyrl§ Engine v7.3 initialized · unified Wisp flight · runtime diagnostics','ok')"
    }.items(): s=_once(s,a,b)

    # v7.2's emergency second translation pass fixed the deadlock but could double-move.
    # Remove it and make the established movement block choose exactly one controller.
    emergency="""  if(h.userData.hoverFlight){
    const keyRight=(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0);
    const keyForward=(keys.has('w')||keys.has('arrowup')?1:0)-(keys.has('s')||keys.has('arrowdown')?1:0);
    const ri=THREE.MathUtils.clamp(keyRight+fpMove.x,-1,1),fi=THREE.MathUtils.clamp(keyForward-fpMove.y,-1,1);
    const fwd=new THREE.Vector3(Math.sin(fpYaw),0,-Math.cos(fpYaw)),rgt=new THREE.Vector3(Math.cos(fpYaw),0,Math.sin(fpYaw)),freeMove=new THREE.Vector3().addScaledVector(fwd,fi).addScaledVector(rgt,ri);
    if(freeMove.lengthSq()>1)freeMove.normalize();
    if(freeMove.lengthSq()>.0001){const sp=h.userData.moveSpeed||6;h.position.addScaledVector(freeMove,sp*dt);}
  }
"""
    s=_once(s,emergency,"")

    # Replace the horizontal collision statement after reconstruction, tolerating the
    # finite-guard form introduced by prior corrective patches.
    candidates=[
      "resolveHeroCollision(next,0.55);h.position.x=next.x;h.position.z=next.z;",
      "resolveHeroCollision(next,h.userData.colliderRadius||.46);if(Number.isFinite(next.x)&&Number.isFinite(next.z)){h.position.x=next.x;h.position.z=next.z;}"
    ]
    needle=next((q for q in candidates if q in s),None)
    if not needle: raise RuntimeError("v7.3 horizontal movement statement missing")
    unified="""if(h.userData.hoverFlight){
    // Flight uses the requested X/Z directly. Dense editor collision proxies cannot pin the Wisp.
    if(Number.isFinite(next.x)&&Number.isFinite(next.z)){h.position.x=next.x;h.position.z=next.z;}
  }else{
    resolveHeroCollision(next,.55);h.position.x=next.x;h.position.z=next.z;
  }"""
    s=_once(s,needle,unified)

    css=r"""
.runtime-diag{position:absolute;left:50%;bottom:12px;transform:translateX(-50%);z-index:31;display:none;pointer-events:none;padding:6px 10px;border:1px solid #31516a;border-radius:999px;background:#07111dcc;color:#9ee8ff;font:700 10px/1.2 ui-monospace,monospace;white-space:nowrap}
.app.runtime-play .runtime-diag{display:block}
@media(max-width:720px){.runtime-diag{bottom:150px;max-width:76vw;overflow:hidden;text-overflow:ellipsis}}
"""
    s=_once(s,"</style>",css+"\n</style>")

    marker="installEngineCommandDeck();"
    diag=r"""
function installRuntimeDiagnostics(){
  if($('runtimeDiag'))return;
  const host=document.querySelector('.app')||document.body,d=document.createElement('div');d.id='runtimeDiag';d.className='runtime-diag';host.appendChild(d);
  let last=0;function tick(now){requestAnimationFrame(tick);if(!playing||now-last<180)return;last=now;const h=heroActor();if(!h)return;
    const mag=Math.hypot(fpMove.x,fpMove.y),mode=h.userData.hoverFlight?'FLIGHT':'GROUND';
    d.textContent=mode+' · stick '+mag.toFixed(2)+' · xyz '+h.position.x.toFixed(1)+' / '+h.position.y.toFixed(1)+' / '+h.position.z.toFixed(1);
  }requestAnimationFrame(tick);
}
installRuntimeDiagnostics();
"""
    s=_once(s,marker,marker+"\n"+diag)
    return s
