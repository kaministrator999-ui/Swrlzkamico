"""MOBA-style mobile building skills, native joystick and lifted touch aim."""
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1,(old[:120],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    root=Path(__file__).resolve().parents[1]
    # Placement owns only viewport touches; a second thumb may steer the stick.
    html=once(html,"if (event.pointerType==='touch') stTouchPlacement.touchPointers.add(event.pointerId);", "if (event.pointerType==='touch' && event.target===$('viewport')) stTouchPlacement.touchPointers.add(event.pointerId);")
    html=once(html,"(event.isPrimary===false || stTouchPlacement.touchPointers.size>1)","(stTouchPlacement.touchPointers.size>1)")
    html=once(html,"if (gesture && (event.pointerType!=='touch' || event.target!==$('viewport'))) {", "if (gesture && (event.pointerType!=='touch' || event.target!==$('viewport')) && !event.target?.closest?.('#stMoveStick')) {")
    css=(root/'runtime/sheep_touch_controls_v11_82.css').read_text();js=(root/'runtime/sheep_touch_controls_v11_82.js').read_text()
    at=html.index('</head>');assert at<html.index('<body');html=html[:at]+'<style id="sheepMobileSkillsStyles">'+css+'</style>\n'+html[at:]
    html=once(html,'window.SWRLZ_FORGE_BUILD=',js+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_81_SHEEP_CLEARANCE','SWYRL_ENGINE_DEPLOY_MARKER: V11_82_TOUCH_BUILD_SKILLS'),('ENGINE · MAKER v11.81','ENGINE · MAKER v11.82'),('v11.81 · clear paths & hidden hunters','v11.82 · mobile build skills & joystick'),("window.SWRLZ_FORGE_BUILD={version:'v11.81'","window.SWRLZ_FORGE_BUILD={version:'v11.82'"),('<title>§wyrl§ Engine · Maker v11.81</title>','<title>§wyrl§ Engine · Maker v11.82</title>')]:html=once(html,old,new)
    return html
