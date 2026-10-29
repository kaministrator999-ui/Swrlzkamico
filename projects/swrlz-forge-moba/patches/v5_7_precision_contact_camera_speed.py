"""§wyrl§ Engine v5.7: precision multi-sample foot planting, corrected dragon teeth, camera speed slider."""
from __future__ import annotations

def _once(s: str, old: str, new: str) -> str:
    if old not in s:
        raise RuntimeError("v5.7 patch token missing: " + old[:220])
    return s.replace(old, new, 1)

def _replace_block(s: str, start: str, end: str, block: str) -> str:
    a=s.find(start)
    if a<0: raise RuntimeError("v5.7 block start missing: "+start[:220])
    b=s.find(end,a)
    if b<0: raise RuntimeError("v5.7 block end missing: "+end[:220])
    return s[:a]+block+s[b:]

def apply(html: str) -> str:
    s=html

    repl={
      "<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_6_DRAGON_GROUND_CONTACT -->":"<!-- SWYRL_ENGINE_DEPLOY_MARKER: V5_7_PRECISION_CONTACT_CAMERA_SPEED -->",
      "<title>§wyrl§ Engine · Maker v5.6</title>":"<title>§wyrl§ Engine · Maker v5.7</title>",
      '<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.6</div>':'<div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.7</div>',
      '<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.6 · CONTACT PASS</div>':'<div class="build-stamp" id="buildStamp">§wyrl§ ENGINE · v5.7 · PRECISION CONTACT</div>',
      "window.SWRLZ_FORGE_BUILD={version:'v5.6',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',lookMode:'natural',grouping:'hierarchical',defaultDenAvatar:'wisp',dragonModel:'anatomy-v3',surfaceContact:'raycast-feet'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;":
        "window.SWRLZ_FORGE_BUILD={version:'v5.7',name:'§wyrl§ Engine',stamp:'2026.10.05',source:'GitHub → Hugging Face',projectSystem:'templates',defaultProject:'dragons-den',playMode:'first-person',mobileControls:'twin-stick',lookMode:'natural',grouping:'hierarchical',defaultDenAvatar:'wisp',dragonModel:'anatomy-v3.1',surfaceContact:'multi-sample-raycast',cameraSpeedControl:'slider'};window.SWYRL_ENGINE_BUILD=window.SWRLZ_FORGE_BUILD;",
      "version:'swyrl-engine-agent-v3.6',":"version:'swyrl-engine-agent-v3.7',",
      "editorLog('§wyrl§ Engine v5.6 initialized · dragon wing detail · surface contact grounding','ok')":
        "editorLog('§wyrl§ Engine v5.7 initialized · precision foot contact · camera speed slider','ok')",
      "engine:'§wyrl§ Engine · Maker v5.6',":"engine:'§wyrl§ Engine · Maker v5.7',",
      "version:5.6,":"version:5.7,"
    }
    for a,b in repl.items(): s=_once(s,a,b)

    # Camera speed lives in the actual top bar so it remains accessible on mobile.
    s=_once(
      s,
      '    <div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.7</div>\n    <div class="sep"></div>',
      '    <div class="brand"><b>§wyrl§</b> ENGINE · MAKER v5.7</div>\n    <div class="camera-speed-control" title="Editor rotate + scroll/zoom speed"><span>CAM</span><input id="cameraSpeedSlider" type="range" min="0.35" max="3" step="0.05" value="1"><output id="cameraSpeedValue">1.00×</output></div>\n    <div class="sep"></div>'
    )
    s=_once(
      s,
      '        <select id="cameraSpeed"><option value="0.6">Cam 1</option><option value="1" selected>Cam 2</option><option value="1.6">Cam 3</option><option value="2.4">Cam 4</option></select>',
      ''
    )

    css=r"""
.camera-speed-control{display:flex;align-items:center;gap:6px;flex:0 0 auto;padding:3px 7px;border:1px solid #28364a;border-radius:8px;background:#111925;color:#9fb0c7;white-space:nowrap}
.camera-speed-control span{font-size:9px;font-weight:900;letter-spacing:.08em}
.camera-speed-control input[type=range]{width:110px;padding:0;height:22px;background:transparent;border:0}
.camera-speed-control output{min-width:38px;font-size:10px;color:#cfe6ff;font-variant-numeric:tabular-nums}
@media (max-width:620px){
  .camera-speed-control{padding:2px 5px;gap:4px}
  .camera-speed-control span{display:none}
  .camera-speed-control input[type=range]{width:100px}
  .camera-speed-control output{min-width:34px;font-size:9px}
  .app.runtime-play .camera-speed-control{display:none}
}
"""
    s=_once(s,"</style>",css+"\n</style>")

    # Replace old select handler with continuous slider + persistence.
    s=_once(
      s,
      "$('cameraView').onchange=()=>setCameraView($('cameraView').value); $('cameraSpeed').onchange=()=>{const v=Number($('cameraSpeed').value)||1;orbit.rotateSpeed=v;orbit.panSpeed=v;orbit.zoomSpeed=v;};",
      """function setEditorCameraSpeed(value,persist=true){
  const v=THREE.MathUtils.clamp(Number(value)||1,.35,3);
  orbit.rotateSpeed=v;orbit.panSpeed=v;orbit.zoomSpeed=v;
  if($('cameraSpeedSlider'))$('cameraSpeedSlider').value=String(v);
  if($('cameraSpeedValue'))$('cameraSpeedValue').textContent=v.toFixed(2)+'×';
  if(persist){try{localStorage.setItem('swyrl.engine.cameraSpeed',String(v));}catch(_){}}
}
$('cameraView').onchange=()=>setCameraView($('cameraView').value);
$('cameraSpeedSlider').oninput=()=>setEditorCameraSpeed($('cameraSpeedSlider').value,true);
let initialCameraSpeed=1;try{initialCameraSpeed=Number(localStorage.getItem('swyrl.engine.cameraSpeed'))||1;}catch(_){}
setEditorCameraSpeed(initialCameraSpeed,false);"""
    )

    # Precision foot contact: multi-point sole samples, highest valid surface, averaged contact normal.
    contact=r"""function groundDragonFeet(dragon,dt=.016,surfaces=null){
  const rig=dragon.userData?.dragonRig;
  if(!rig?.legs?.length)return;
  surfaces=surfaces||surfaceContactMeshes(dragon);
  if(!surfaces.length)return;

  scene.updateMatrixWorld(true);
  dragon.updateMatrixWorld(true);
  const invDragon=dragon.matrixWorld.clone().invert();

  for(const leg of rig.legs){
    const foot=leg.foot;
    foot.updateMatrixWorld(true);
    const halfW=leg.halfWidth||.25,halfL=leg.halfLength||.34;
    const samples=[
      [0,0],
      [-halfW*.82,-halfL*.82],[halfW*.82,-halfL*.82],
      [-halfW*.82, halfL*.82],[halfW*.82, halfL*.82],
      [0,-halfL*.96]
    ];

    const hits=[];
    for(const [sx,sz] of samples){
      const sampleWorld=new THREE.Vector3(sx,0,sz);
      foot.localToWorld(sampleWorld);
      dragonFootOrigin.copy(sampleWorld);
      dragonFootOrigin.y+=Math.max(2.8,dragon.scale.y*3.4);
      dragonFootRaycaster.set(dragonFootOrigin,dragonFootDown);
      dragonFootRaycaster.far=Math.max(8,dragon.scale.y*9);
      const hit=dragonFootRaycaster.intersectObjects(surfaces,false)[0];
      if(hit)hits.push(hit);
    }

    let targetY=leg.restFootY;
    let contactNormal=null;
    if(hits.length){
      // Highest sole sample wins vertical placement so no corner can sink through a rock/pedestal.
      const highest=hits.reduce((a,b)=>b.point.y>a.point.y?b:a);
      dragonFootLocal.copy(highest.point).applyMatrix4(invDragon);
      targetY=dragonFootLocal.y+(leg.soleClearance??.035);

      // Average normals near the highest contact only; ignore distant lower floor hits.
      const normalSum=new THREE.Vector3();
      let normalCount=0;
      const band=Math.max(.22,.32*dragon.scale.y);
      for(const h of hits){
        if(highest.point.y-h.point.y>band||!h.face)continue;
        const n=h.face.normal.clone().transformDirection(h.object.matrixWorld).normalize();
        if(n.y<.15)continue;
        normalSum.add(n);normalCount++;
      }
      if(normalCount)contactNormal=normalSum.multiplyScalar(1/normalCount).normalize();
    }else{
      const wp=foot.getWorldPosition(new THREE.Vector3());
      const terrainWorld=new THREE.Vector3(wp.x,terrainHeight(wp.x,wp.z),wp.z);
      terrainWorld.applyMatrix4(invDragon);
      targetY=terrainWorld.y+(leg.soleClearance??.035);
      contactNormal=new THREE.Vector3(0,1,0);
    }

    targetY=THREE.MathUtils.clamp(targetY,leg.restFootY-.65,leg.restFootY+1.65);
    const alpha=1-Math.exp(-dt*22);
    leg.contactY=THREE.MathUtils.lerp(leg.contactY??leg.restFootY,targetY,alpha);
    foot.position.y=leg.contactY;

    if(contactNormal){
      const localNormal=contactNormal.clone().transformDirection(invDragon).normalize();
      dragonFootQuat.setFromUnitVectors(dragonFootUp,localNormal);
      const maxTilt=.38;
      const e=new THREE.Euler().setFromQuaternion(dragonFootQuat,'XYZ');
      e.x=THREE.MathUtils.clamp(e.x,-maxTilt,maxTilt);
      e.z=THREE.MathUtils.clamp(e.z,-maxTilt,maxTilt);
      e.y=0;
      foot.quaternion.slerp(new THREE.Quaternion().setFromEuler(e),alpha*.72);
    }

    const knee=new THREE.Vector3(...leg.knee);
    const ankle=foot.position.clone();ankle.y+=.18;
    setCylinderBetween(leg.lower,knee,ankle);
  }
}

function updateDragonSurfaceContacts(dt){
  const surfaces=surfaceContactMeshes(null);
  for(const a of actors){
    if(a.userData?.actorType==='dragon'&&a.userData?.dragonRig)groundDragonFeet(a,dt,surfaces);
  }
}
"""
    s=_replace_block(s,"function groundDragonFeet(dragon,dt=.016){","function makeDragon(pos",contact)

    # Teeth no longer pierce through the lower jaw.
    s=_once(
      s,
      "const tooth=mesh(new THREE.ConeGeometry(.055,.25,5),claw.clone(),'DragonTooth');tooth.position.set(side*.22,3.98,-2.26);tooth.rotation.x=Math.PI;",
      "const tooth=mesh(new THREE.ConeGeometry(.048,.16,6),claw.clone(),'DragonTooth');tooth.position.set(side*.22,4.105,-2.22);tooth.rotation.x=Math.PI;"
    )

    # Foot metadata for multi-sample ground contact.
    s=_once(
      s,
      "rigLegs.push({kind:def.kind,side:def.side,foot:footGroup,lower,knee:def.knee,restFootY:def.foot[1],soleOffset:.10,contactY:def.foot[1]});",
      "rigLegs.push({kind:def.kind,side:def.side,foot:footGroup,lower,knee:def.knee,restFootY:def.foot[1],soleClearance:.035,halfWidth:rear?.31:.25,halfLength:rear?.39:.34,contactY:def.foot[1]});"
    )

    # Bump dragon blueprint/tag lineage without touching the Wisp/player.
    s=_once(s,"blueprintClass:'BP_DragonAvatarV3'","blueprintClass:'BP_DragonAvatarV3_1'");
    s=_once(s,"'dragon-anatomy-v3','surface-foot-contact'","'dragon-anatomy-v3.1','surface-foot-contact','multi-sample-feet'");

    return s
