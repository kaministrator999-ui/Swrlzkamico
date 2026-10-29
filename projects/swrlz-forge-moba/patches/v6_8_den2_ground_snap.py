"""§wyrl§ Engine v6.8: hard-snap Fracture Forge dragons to support surfaces."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v6.8 token missing: "+old[:200])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V6_7_CONTACT_TOOLS":"V6_8_DEN2_GROUND_SNAP",
      "Maker v6.7":"Maker v6.8","MAKER v6.7":"MAKER v6.8",
      "v6.7 · CONTACT + TOOLS":"v6.8 · DEN 2 GROUND SNAP",
      "version:'v6.7'":"version:'v6.8'",
      "version:'swyrl-engine-agent-v4.7'":"version:'swyrl-engine-agent-v4.8'",
      "engine:'§wyrl§ Engine · Maker v6.7'":"engine:'§wyrl§ Engine · Maker v6.8'",
      "version:6.7":"version:6.8",
      "editorLog('§wyrl§ Engine v6.7 initialized · Wisp flight restored · dragon contact root solve · organized tools','ok')":"editorLog('§wyrl§ Engine v6.8 initialized · Fracture Forge dragons hard-snapped to support','ok')"
    }.items(): s=_once(s,a,b)

    # Den 2 / Fracture Forge had explicit levitation offsets. Remove them and settle
    # each dragon only after its final yaw is known.
    old="""  const sw=makeGlitchDragonV3([17,0,8],'#7c55ff',true,'§wyrl§ Glitch Dragon',2.8,'#5cecff');sw.position.y+=3.3;sw.rotation.y=-2.2;sw.userData.role='primary-lalm-avatar';
  const frost=makeGlitchDragonV3([-18,0,-5],'#4fcfff',true,'Frost Forge Dragon',2.15,'#d7fbff');frost.position.y+=2.05;frost.rotation.y=1.3;
  const ember=makeGlitchDragonV3([14,0,-15],'#ff4f88',true,'Ember Glitch Dragon',2.0,'#ffb15c');ember.position.y+=1.9;ember.rotation.y=-.4;"""
    new="""  const sw=makeGlitchDragonV3([17,0,8],'#7c55ff',true,'§wyrl§ Glitch Dragon',2.8,'#5cecff');sw.rotation.y=-2.2;sw.userData.role='primary-lalm-avatar';snapDragonToSupport(sw);
  const frost=makeGlitchDragonV3([-18,0,-5],'#4fcfff',true,'Frost Forge Dragon',2.15,'#d7fbff');frost.rotation.y=1.3;snapDragonToSupport(frost);
  const ember=makeGlitchDragonV3([14,0,-15],'#ff4f88',true,'Ember Glitch Dragon',2.0,'#ffb15c');ember.rotation.y=-.4;snapDragonToSupport(ember);"""
    s=_once(s,old,new)

    # Initial placement is deterministic: use the lowest world-space paw, find its
    # support directly below, and shift the whole dragon once by the full delta.
    marker="function updateDragonRigs(t){"
    snap=r'''function snapDragonToSupport(d){
  d.updateMatrixWorld(true);const feet=[];d.traverse(o=>{if(o.userData.dragonFoot)feet.push(o);});
  if(!feet.length)return;
  let best=null;
  for(const foot of feet){const wp=new THREE.Vector3();foot.getWorldPosition(wp);const support=solidContactHeight(d,foot)+.055;const delta=support-wp.y;if(!best||wp.y<best.y)best={y:wp.y,delta};}
  if(best&&Number.isFinite(best.delta)){d.position.y+=best.delta;d.updateMatrixWorld(true);}
  d.userData.supportSnapped=true;
}
'''
    if marker not in s: raise RuntimeError("v6.8 dragon rig marker missing")
    s=s.replace(marker,snap+"\n"+marker,1)

    # Maintenance correction follows the lowest paw rather than the most-negative
    # error, preventing a high paw from dragging the whole body through the floor.
    old2="""      d.updateMatrixWorld(true);let rootDelta=Infinity;
      for(const foot of feet){const wp=new THREE.Vector3();foot.getWorldPosition(wp);rootDelta=Math.min(rootDelta,solidContactHeight(d,foot)+.055-wp.y);}
      if(Number.isFinite(rootDelta))d.position.y+=THREE.MathUtils.clamp(rootDelta,-.18,.18)*.42;"""
    new2="""      d.updateMatrixWorld(true);let lowestY=Infinity,rootDelta=0;
      for(const foot of feet){const wp=new THREE.Vector3();foot.getWorldPosition(wp),delta=solidContactHeight(d,foot)+.055-wp.y;if(wp.y<lowestY){lowestY=wp.y;rootDelta=delta;}}
      if(Number.isFinite(rootDelta))d.position.y+=THREE.MathUtils.clamp(rootDelta,-.24,.24)*.55;"""
    s=_once(s,old2,new2)
    return s
