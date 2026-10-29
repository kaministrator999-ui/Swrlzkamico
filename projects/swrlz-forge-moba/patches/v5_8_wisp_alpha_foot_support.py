"""§wyrl§ Engine v5.8: clean Wisp sprite alpha + support-aware dragon paw placement."""
from __future__ import annotations
def _once(s,old,new):
    if old not in s: raise RuntimeError("v5.8 token missing: "+old[:220])
    return s.replace(old,new,1)
def _replace_block(s,start,end,block):
    a=s.find(start)
    if a<0: raise RuntimeError("v5.8 block start missing: "+start[:220])
    b=s.find(end,a)
    if b<0: raise RuntimeError("v5.8 block end missing: "+end[:220])
    return s[:a]+block+s[b:]
def apply(html):
    s=html
    repl={
      "V5_7_PRECISION_CONTACT_CAMERA_SPEED":"V5_8_WISP_ALPHA_FOOT_SUPPORT",
      "Maker v5.7":"Maker v5.8",
      "MAKER v5.7":"MAKER v5.8",
      "v5.7 · PRECISION CONTACT":"v5.8 · SUPPORT CONTACT",
      "version:'v5.7'":"version:'v5.8'",
      "version:'swyrl-engine-agent-v3.7'":"version:'swyrl-engine-agent-v3.8'",
      "engine:'§wyrl§ Engine · Maker v5.7'":"engine:'§wyrl§ Engine · Maker v5.8'",
      "version:5.7":"version:5.8",
      "editorLog('§wyrl§ Engine v5.7 initialized · precision foot contact · camera speed slider','ok')":"editorLog('§wyrl§ Engine v5.8 initialized · clean Wisp alpha · support-aware dragon feet','ok')"
    }
    for a,b in repl.items(): s=_once(s,a,b)

    # Canvas sprite alpha: explicitly clear alpha, premultiply texture, and discard near-zero fringe pixels.
    s=_once(s,
      "const c=document.createElement('canvas');c.width=c.height=128;const x=c.getContext('2d');",
      "const c=document.createElement('canvas');c.width=c.height=128;const x=c.getContext('2d',{alpha:true});x.clearRect(0,0,128,128);"
    )
    s=_once(s,
      "const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;wispTextureCache.set(color,tex);return tex;",
      "const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;tex.premultiplyAlpha=true;tex.needsUpdate=true;wispTextureCache.set(color,tex);return tex;"
    )
    s=_once(s,
      "const m=new THREE.SpriteMaterial({map:wispGlowTexture(glowColor),transparent:true,opacity,depthWrite:false,blending:THREE.AdditiveBlending});",
      "const m=new THREE.SpriteMaterial({map:wispGlowTexture(glowColor),transparent:true,opacity,alphaTest:.018,depthWrite:false,depthTest:true,blending:THREE.AdditiveBlending,premultipliedAlpha:true});"
    )

    contact=r"""function groundDragonFeet(dragon,dt=.016,surfaces=null){
  const rig=dragon.userData?.dragonRig;
  if(!rig?.legs?.length)return;
  surfaces=surfaces||surfaceContactMeshes(dragon);
  if(!surfaces.length)return;
  scene.updateMatrixWorld(true);dragon.updateMatrixWorld(true);
  const invDragon=dragon.matrixWorld.clone().invert();

  for(const leg of rig.legs){
    const foot=leg.foot;foot.updateMatrixWorld(true);
    const halfW=leg.halfWidth||.25,halfL=leg.halfLength||.34;
    const samples=[[0,0],[-halfW*.82,-halfL*.82],[halfW*.82,-halfL*.82],[-halfW*.82,halfL*.82],[halfW*.82,halfL*.82],[0,-halfL*.96],[0,halfL*.96]];
    const hits=[];
    for(const [sx,sz] of samples){
      const sampleWorld=new THREE.Vector3(sx,0,sz);foot.localToWorld(sampleWorld);
      dragonFootOrigin.copy(sampleWorld);dragonFootOrigin.y+=Math.max(2.8,dragon.scale.y*3.4);
      dragonFootRaycaster.set(dragonFootOrigin,dragonFootDown);dragonFootRaycaster.far=Math.max(8,dragon.scale.y*9);
      const hit=dragonFootRaycaster.intersectObjects(surfaces,false)[0];
      if(hit)hits.push({hit,sx,sz});
    }

    let targetY=leg.restFootY,contactNormal=null;
    let targetX=leg.restFootX,targetZ=leg.restFootZ;
    if(hits.length){
      const highest=hits.reduce((a,b)=>b.hit.point.y>a.hit.point.y?b:a);
      dragonFootLocal.copy(highest.hit.point).applyMatrix4(invDragon);
      targetY=dragonFootLocal.y+(leg.soleClearance??.035);

      const band=Math.max(.22,.32*dragon.scale.y),supported=hits.filter(h=>highest.hit.point.y-h.hit.point.y<=band);
      const normalSum=new THREE.Vector3();let normalCount=0;
      for(const h of supported){
        if(!h.hit.face)continue;
        const n=h.hit.face.normal.clone().transformDirection(h.hit.object.matrixWorld).normalize();
        if(n.y<.15)continue;normalSum.add(n);normalCount++;
      }
      if(normalCount)contactNormal=normalSum.multiplyScalar(1/normalCount).normalize();

      // If the sole is only partly supported, pull the paw horizontally toward the supported samples.
      // This fixes the visible "heel hanging off the rock" case instead of merely raising the paw.
      if(supported.length<samples.length){
        let cx=0,cz=0;for(const h of supported){cx+=h.sx;cz+=h.sz;}cx/=supported.length;cz/=supported.length;
        const supportGain=supported.length<=3?.95:.62;
        const desiredX=foot.position.x+cx*supportGain,desiredZ=foot.position.z+cz*supportGain;
        const maxShift=leg.kind==='rear'?.58:.46;
        targetX=THREE.MathUtils.clamp(desiredX,leg.restFootX-maxShift,leg.restFootX+maxShift);
        targetZ=THREE.MathUtils.clamp(desiredZ,leg.restFootZ-maxShift,leg.restFootZ+maxShift);
      }
    }else{
      const wp=foot.getWorldPosition(new THREE.Vector3());
      const terrainWorld=new THREE.Vector3(wp.x,terrainHeight(wp.x,wp.z),wp.z);terrainWorld.applyMatrix4(invDragon);
      targetY=terrainWorld.y+(leg.soleClearance??.035);contactNormal=new THREE.Vector3(0,1,0);
    }

    targetY=THREE.MathUtils.clamp(targetY,leg.restFootY-.65,leg.restFootY+1.65);
    const alpha=1-Math.exp(-dt*22);
    leg.contactY=THREE.MathUtils.lerp(leg.contactY??leg.restFootY,targetY,alpha);
    leg.contactX=THREE.MathUtils.lerp(leg.contactX??leg.restFootX,targetX,alpha*.72);
    leg.contactZ=THREE.MathUtils.lerp(leg.contactZ??leg.restFootZ,targetZ,alpha*.72);
    foot.position.set(leg.contactX,leg.contactY,leg.contactZ);

    if(contactNormal){
      const localNormal=contactNormal.clone().transformDirection(invDragon).normalize();
      dragonFootQuat.setFromUnitVectors(dragonFootUp,localNormal);
      const maxTilt=.38,e=new THREE.Euler().setFromQuaternion(dragonFootQuat,'XYZ');
      e.x=THREE.MathUtils.clamp(e.x,-maxTilt,maxTilt);e.z=THREE.MathUtils.clamp(e.z,-maxTilt,maxTilt);e.y=0;
      foot.quaternion.slerp(new THREE.Quaternion().setFromEuler(e),alpha*.72);
    }
    const knee=new THREE.Vector3(...leg.knee),ankle=foot.position.clone();ankle.y+=.18;setCylinderBetween(leg.lower,knee,ankle);
  }
}

"""
    s=_replace_block(s,"function groundDragonFeet(dragon,dt=.016,surfaces=null){","function updateDragonSurfaceContacts(dt){",contact)
    s=_once(s,
      "rigLegs.push({kind:def.kind,side:def.side,foot:footGroup,lower,knee:def.knee,restFootY:def.foot[1],soleClearance:.035,halfWidth:rear?.31:.25,halfLength:rear?.39:.34,contactY:def.foot[1]});",
      "rigLegs.push({kind:def.kind,side:def.side,foot:footGroup,lower,knee:def.knee,restFootX:def.foot[0],restFootY:def.foot[1],restFootZ:def.foot[2],soleClearance:.035,halfWidth:rear?.31:.25,halfLength:rear?.39:.34,contactX:def.foot[0],contactY:def.foot[1],contactZ:def.foot[2]});"
    )
    s=_once(s,"dragonModel:'anatomy-v3.1',surfaceContact:'multi-sample-raycast',cameraSpeedControl:'slider'","dragonModel:'anatomy-v3.2',surfaceContact:'support-aware-raycast',cameraSpeedControl:'slider',wispAlpha:'premultiplied-cutout'")
    return s
