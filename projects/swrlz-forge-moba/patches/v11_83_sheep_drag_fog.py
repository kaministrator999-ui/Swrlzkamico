"""Direct build drags, joystick movement and smooth cosmetic fog."""
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1,(old[:120],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    html=once(html,"if (event.pointerType==='touch' && event.target===$('viewport')) stTouchPlacement.touchPointers.add(event.pointerId);", "if (event.pointerType==='touch' && (event.target===$('viewport') || event.target?.closest?.('button[data-st-skill^=st-]'))) stTouchPlacement.touchPointers.add(event.pointerId);")
    html=once(html,"const stMobileMedia=matchMedia('(pointer:coarse), (max-width:620px)');","const stMobileMedia=matchMedia('(min-width:0px)');")
    html=once(html,"f.updateAt=s.elapsed+.35;f.visible.fill(0)","f.updateAt=s.elapsed+.1;f.visible.fill(0)")
    start=html.index("  const ctx=f.canvas.getContext('2d'),data=ctx.createImageData(f.width,f.width);")
    end=html.index('\n}',start)
    html=html[:start]+'  stSoftFogPaint(s);'+html[end:]
    start=html.index("    const visible = new Set(fog.visible || []), explored = new Set(fog.explored || []);")
    end=html.index('\n  }\n  for (const building',start)
    html=html[:start]+"    if(stSession?.fog?.softMemory){context.imageSmoothingEnabled=true;context.drawImage(stSession.fog.canvas,0,0,size,size);}"+html[end:]
    for old,new in [('Tap ground to move; tap units or farms to select them.','Use the left joystick to move. Drag a house icon onto the meadow and release to build; the preview stays above your finger. Tap units or houses to select them.'),('Tap ground to move. Build houses to block wolves; reach wisps to rescue allies.','Use the joystick to move. Drag house icons onto the meadow and release to build.'),('Building selected. Tap ground to run again.','Building selected. Use the joystick to move.'),('Tap an upper wall destination. Your unit needs a connected ramp to reach it.','Use the joystick to move along connected raised routes.')]:
        if old in html:html=html.replace(old,new)
    html=once(html,"' selected. Tap ground to run again.'","' selected. Use the joystick to move.'")
    html=once(html,'window.SWRLZ_FORGE_BUILD=',(root/'runtime/sheep_drag_fog_v11_83.js').read_text()+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_82_TOUCH_BUILD_SKILLS','SWYRL_ENGINE_DEPLOY_MARKER: V11_83_DRAG_BUILD_SOFT_FOG'),('ENGINE · MAKER v11.82','ENGINE · MAKER v11.83'),('v11.82 · mobile build skills & joystick','v11.83 · drag building & smooth fog'),("window.SWRLZ_FORGE_BUILD={version:'v11.82'","window.SWRLZ_FORGE_BUILD={version:'v11.83'"),('<title>§wyrl§ Engine · Maker v11.82</title>','<title>§wyrl§ Engine · Maker v11.83</title>')]:html=once(html,old,new)
    return html
