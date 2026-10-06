"""§wyrl§ Engine v6.7: restore Wisp translation, root-plant dragons, organize Tools."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v6.7 token missing: "+old[:180])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V6_6_HOVER_DRAGON_IK":"V6_7_CONTACT_TOOLS",
      "Maker v6.6":"Maker v6.7","MAKER v6.6":"MAKER v6.7",
      "v6.6 · HOVER + DRAGON IK":"v6.7 · CONTACT + TOOLS",
      "version:'v6.6'":"version:'v6.7'",
      "version:'swyrl-engine-agent-v4.6'":"version:'swyrl-engine-agent-v4.7'",
      "engine:'§wyrl§ Engine · Maker v6.6'":"engine:'§wyrl§ Engine · Maker v6.7'",
      "version:6.6":"version:6.7",
      "editorLog('§wyrl§ Engine v6.6 initialized · Wisp hover collision · planted dragon idle rig','ok')":"editorLog('§wyrl§ Engine v6.7 initialized · Wisp flight restored · dragon contact root solve · organized tools','ok')"
    }.items(): s=_once(s,a,b)

    # The v6.6 hover patch already preserves the known-working first-person X/Z controller.
    # Do not rewrite it again here; keep hover collision metadata and add explicit mobile altitude input.
    if "h.userData.hoverFlight" not in s or "resolveHeroCollision(next" not in s:
      raise RuntimeError("v6.7 expected Wisp hover/controller integration missing")

    # Mobile hover controls: move stick remains translation; dedicated altitude buttons avoid
    # stealing the look stick.
    css=r"""
.hover-alt-controls{position:absolute;right:22px;bottom:142px;display:none;flex-direction:column;gap:8px;pointer-events:auto}
.hover-alt-btn{width:54px;height:46px;border-radius:14px;border:1px solid #8fe7ff88;background:#102236dd;color:#dff8ff;font:800 20px system-ui;touch-action:none}
.app.runtime-play .hover-alt-controls{display:flex}
@media (pointer:fine){.hover-alt-controls{display:none!important}}
.tool-section{border:1px solid #26384c;border-radius:15px;background:#0b1420aa;margin:10px 0;overflow:hidden}
.tool-section-title{padding:10px 13px;font:800 12px system-ui;letter-spacing:.1em;color:#89dfff;background:#111e2d;text-transform:uppercase}
.tool-section-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;padding:10px}
.tool-section-grid>*{min-width:0}
"""
    s=_once(s,"</style>",css+"\n</style>")
    hudneedle='''          <div id="lookStick" class="joy joy-right"><div class="joy-knob"></div><div class="joy-label">LOOK</div></div>'''
    hudnew=hudneedle+'''\n          <div class="hover-alt-controls"><button id="hoverUp" class="hover-alt-btn" aria-label="Float up">▲</button><button id="hoverDown" class="hover-alt-btn" aria-label="Float down">▼</button></div>'''
    s=_once(s,hudneedle,hudnew)
    controlmarker="bindVirtualStick('moveStick',fpMove);bindVirtualStick('lookStick',fpLook);"
    s=_once(s,controlmarker,controlmarker+"\nlet hoverUpHeld=false,hoverDownHeld=false;for(const [id,key] of [['hoverUp','up'],['hoverDown','down']]){const el=$(id);if(!el)continue;const set=v=>{if(key==='up')hoverUpHeld=v;else hoverDownHeld=v;};el.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();set(true);el.setPointerCapture?.(e.pointerId)});for(const ev of ['pointerup','pointercancel','lostpointercapture'])el.addEventListener(ev,()=>set(false));}")
    s=_once(s,"const rise=(keys.has(' ')||keys.has('e')?1:0)-(keys.has('shift')||keys.has('q')?1:0);","const rise=((keys.has(' ')||keys.has('e')||hoverUpHeld)?1:0)-((keys.has('shift')||keys.has('q')||hoverDownHeld)?1:0);")

    # Replace v6.6 paw-only Y motion. Find lowest contact error and move the dragon root
    # so the lowest paw lands; then articulate each paw/leg residual in local space.
    old="""    const feet=[];d.traverse(o=>{if(o.userData.dragonFoot)feet.push(o);});
    for(const foot of feet){
      const contact=solidContactHeight(d,foot),parentY=d.position.y,localTarget=(contact-parentY)/s+.11;
      foot.position.y=THREE.MathUtils.lerp(foot.position.y,localTarget,.32);
    }"""
    new="""    const feet=[],legs=[];d.traverse(o=>{if(o.userData.dragonFoot)feet.push(o);if(o.name==='DragonLowerLeg')legs.push(o);});
    if(feet.length){
      d.updateMatrixWorld(true);let rootDelta=Infinity;
      for(const foot of feet){const wp=new THREE.Vector3();foot.getWorldPosition(wp);rootDelta=Math.min(rootDelta,solidContactHeight(d,foot)+.055-wp.y);}
      if(Number.isFinite(rootDelta))d.position.y+=THREE.MathUtils.clamp(rootDelta,-.18,.18)*.42;
      d.updateMatrixWorld(true);
      for(let i=0;i<feet.length;i++){const foot=feet[i],wp=new THREE.Vector3();foot.getWorldPosition(wp),contact=solidContactHeight(d,foot)+.055,worldDelta=contact-wp.y;
        foot.position.y+=THREE.MathUtils.clamp(worldDelta/s,-.22,.22)*.55;
        const leg=legs[i];if(leg){const rear=new THREE.Vector3(foot.position.x,foot.position.y+.10,foot.position.z+.24),top=leg.position.clone().multiplyScalar(2).sub(rear),dir=rear.clone().sub(top),len=dir.length();leg.position.copy(top.clone().add(rear).multiplyScalar(.5));leg.scale.y=Math.max(.72,len);leg.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),dir.normalize());}
      }
    }"""
    s=_once(s,old,new)

    # Organize existing mobile Tools without changing button IDs/handlers: headings are
    # injected around logical runs, preserving all established controls.
    panelStart='<div class="mobile-tools-body">'
    if panelStart not in s: raise RuntimeError("v6.7 mobile tools body missing")
    replacements=[
      ("<button id=\"projectsBtn\"","<div class=\"tool-section\"><div class=\"tool-section-title\">Project & History</div><div class=\"tool-section-grid\"><button id=\"projectsBtn\""),
      ("<button id=\"moveBtn\"","</div></div><div class=\"tool-section\"><div class=\"tool-section-title\">Transform</div><div class=\"tool-section-grid\"><button id=\"moveBtn\""),
      ("<button id=\"terrainSnapBtn\"","</div></div><div class=\"tool-section\"><div class=\"tool-section-title\">World & Build</div><div class=\"tool-section-grid\"><button id=\"terrainSnapBtn\""),
      ("<button id=\"simulateBtn\"","</div></div><div class=\"tool-section\"><div class=\"tool-section-title\">Play & Content</div><div class=\"tool-section-grid\"><button id=\"simulateBtn\""),
      ("<button id=\"saveBtn\"","</div></div><div class=\"tool-section\"><div class=\"tool-section-title\">File & View</div><div class=\"tool-section-grid\"><button id=\"saveBtn\"")
    ]
    for old,new in replacements:
      if old in s:s=s.replace(old,new,1)
    # close last injected section immediately before tools-body close near the view help.
    helptext="Perspective can orbit under the terrain. Orthographic views are rotation-locked."
    i=s.find(helptext)
    if i<0: raise RuntimeError("v6.7 tools help marker missing")
    close=s.rfind("</div>",0,i)
    if close<0: raise RuntimeError("v6.7 tools close marker missing")
    s=s[:close]+"</div></div>"+s[close:]
    return s
