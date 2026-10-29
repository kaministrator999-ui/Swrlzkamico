"""§wyrl§ Engine v5.9: softer Wisp particles, stable dragon contact, visible Undo/Redo."""
def _once(s,old,new):
    if old not in s: raise RuntimeError("v5.9 token missing: "+old[:220])
    return s.replace(old,new,1)
def apply(html):
    s=html
    for a,b in {
      "V5_8_WISP_ALPHA_FOOT_SUPPORT":"V5_9_WISP_SOFT_CONTACT_HISTORY",
      "Maker v5.8":"Maker v5.9","MAKER v5.8":"MAKER v5.9",
      "v5.8 · SUPPORT CONTACT":"v5.9 · SOFT CONTACT + HISTORY",
      "version:'v5.8'":"version:'v5.9'",
      "version:'swyrl-engine-agent-v3.8'":"version:'swyrl-engine-agent-v3.9'",
      "engine:'§wyrl§ Engine · Maker v5.8'":"engine:'§wyrl§ Engine · Maker v5.9'",
      "version:5.8":"version:5.9",
      "editorLog('§wyrl§ Engine v5.8 initialized · clean Wisp alpha · support-aware dragon feet','ok')":"editorLog('§wyrl§ Engine v5.9 initialized · soft Wisp · stable foot support · visible history','ok')"
    }.items(): s=_once(s,a,b)

    # Restore soft radial falloff. v5.8's alphaTest converted the glow into a crisp circular cutout.
    s=_once(s,
      "transparent:true,opacity,alphaTest:.018,depthWrite:false,depthTest:true,blending:THREE.AdditiveBlending,premultipliedAlpha:true",
      "transparent:true,opacity,alphaTest:0,depthWrite:false,depthTest:true,blending:THREE.AdditiveBlending,premultipliedAlpha:true"
    )
    s=_once(s,
      "g.addColorStop(.62,'rgba(70,180,255,.32)');\n  g.addColorStop(1,'rgba(70,160,255,0)');",
      "g.addColorStop(.62,'rgba(70,180,255,.22)');\n  g.addColorStop(.82,'rgba(70,170,255,.055)');\n  g.addColorStop(.96,'rgba(70,160,255,.006)');\n  g.addColorStop(1,'rgba(70,160,255,0)');"
    )

    # Stop chasing support every frame. A paw may acquire a bounded support correction,
    # then it stays planted until support is actually lost.
    old="""      if(supported.length<samples.length){
        let cx=0,cz=0;for(const h of supported){cx+=h.sx;cz+=h.sz;}cx/=supported.length;cz/=supported.length;
        const supportGain=supported.length<=3?.95:.62;
        const desiredX=foot.position.x+cx*supportGain,desiredZ=foot.position.z+cz*supportGain;
        const maxShift=leg.kind==='rear'?.58:.46;
        targetX=THREE.MathUtils.clamp(desiredX,leg.restFootX-maxShift,leg.restFootX+maxShift);
        targetZ=THREE.MathUtils.clamp(desiredZ,leg.restFootZ-maxShift,leg.restFootZ+maxShift);
      }"""
    new="""      const supportRatio=supported.length/samples.length;
      if(supportRatio<.72){
        let cx=0,cz=0;for(const h of supported){cx+=h.sx;cz+=h.sz;}cx/=supported.length;cz/=supported.length;
        if(!leg.supportLocked){
          const supportGain=supported.length<=3?.72:.46,maxShift=leg.kind==='rear'?.48:.38;
          leg.plantX=THREE.MathUtils.clamp(foot.position.x+cx*supportGain,leg.restFootX-maxShift,leg.restFootX+maxShift);
          leg.plantZ=THREE.MathUtils.clamp(foot.position.z+cz*supportGain,leg.restFootZ-maxShift,leg.restFootZ+maxShift);
          leg.supportLocked=true;
        }
        targetX=leg.plantX;targetZ=leg.plantZ;
      }else{
        leg.supportLocked=false;leg.plantX=leg.restFootX;leg.plantZ=leg.restFootZ;
      }"""
    s=_once(s,old,new)

    # Undo/Redo already exist in the engine/history system and mobile Tools drawer.
    # Surface them in the main top bar so mobile users do not have to hunt for them.
    s=_once(s,
      '<div class="camera-speed-control" title="Editor rotate + scroll/zoom speed">',
      '<div class="history-quick-controls"><button id="quickUndoBtn" title="Undo last editor action">↶</button><button id="quickRedoBtn" title="Redo undone editor action">↷</button></div><div class="camera-speed-control" title="Editor rotate + scroll/zoom speed">'
    )
    s=_once(s,"</style>","""
.history-quick-controls{display:flex;gap:4px;flex:0 0 auto}
.history-quick-controls button{min-width:34px;padding:7px 8px;font-size:18px;line-height:1}
.app.runtime-play .history-quick-controls{display:none}
@media(max-width:620px){.history-quick-controls button{min-width:32px;padding:6px}}
</style>""")
    s=_once(s,
      "$('cameraView').onchange=()=>setCameraView($('cameraView').value);",
      "$('quickUndoBtn').onclick=()=>$('undoBtn')?.click();$('quickRedoBtn').onclick=()=>$('redoBtn')?.click();\n$('cameraView').onchange=()=>setCameraView($('cameraView').value);"
    )
    s=_once(s,"wispAlpha:'premultiplied-cutout'","wispAlpha:'premultiplied-soft'")
    return s
