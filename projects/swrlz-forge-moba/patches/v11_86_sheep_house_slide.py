"""Sheep steer toward the nearest clear side of a house while holding the joystick; safe corners and narrow lanes, with immediate release-to-stop."""
from pathlib import Path

def once(html,old,new):
    assert html.count(old)==1,(old[:100],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    r=Path(__file__).resolve().parents[1]
    html=once(html,'radius=stUnitRadius(unit);let target=null;','radius=stUnitRadius(unit);let target=stHouseSlideTarget(unit,direction,context,radius);')
    html=once(html,'for(const distance of [1.2,.6,.3,.12]){','if(!target)for(const distance of [1.2,.6,.3,.12]){')
    html=once(html,'window.SWRLZ_FORGE_BUILD=',(r/'runtime/sheep_house_slide_v11_86.js').read_text()+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_85_LARGE_CONTROLS_SEVEN_MINUTES','SWYRL_ENGINE_DEPLOY_MARKER: V11_86_SHEEP_HOUSE_SLIDE'),('ENGINE · MAKER v11.85','ENGINE · MAKER v11.86'),('v11.85 · larger controls & seven-minute matches','v11.86 · sheep steer around houses'),("window.SWRLZ_FORGE_BUILD={version:'v11.85'","window.SWRLZ_FORGE_BUILD={version:'v11.86'"),('<title>§wyrl§ Engine · Maker v11.85</title>','<title>§wyrl§ Engine · Maker v11.86</title>')]:html=once(html,old,new)
    return html
