"""Add connected house placement, construction ejection and physical unit traffic."""
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Sheep lanes anchor missing or ambiguous: ' + old[:90]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    js = (root / 'runtime' / 'sheep_lanes.js').read_text()
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html,
        'snap=s?.rules.buildSnap??.15,snappedX=Math.round(Number(x)/snap)*snap,snappedZ=Math.round(Number(z)/snap)*snap,angle=',
        'snap=s?.rules.buildSnap??.15,aligned=stLanesSnapHouse(kind,x,z,snap),snappedX=aligned.x,snappedZ=aligned.z,angle=')
    html = once(html, "for(const u of s.units)if(!u.captured&&!u.isIllusion&&!(kind==='st-wall'&&stEntityHeight(u)<(s.rules.wallHeight??3.3)-1.2)&&stIntersectsObstacle",
                        'for(const u of s.units)if(u.id!==owner.id&&!u.captured&&!u.isIllusion&&stIntersectsObstacle')
    html = once(html, "stUiFeedback(name + ' ordered. Your sheep will walk to the construction site.');",
                        "stUiFeedback(name + ' ordered at the displayed footprint.');")
    # A migration in the appended module upgrades the old saved default while
    # custom collision radii remain configurable. Old map assets stay intact.
    html = once(html, 'ST_WOLF_RADIUS=.68;', 'ST_WOLF_RADIUS=.78;')
    html = once(html, 'sheepRadius:.27,wolfRadius:.68,houseLimit:', 'sheepRadius:.27,wolfRadius:.78,houseLimit:')
    html = once(html, 'V10_3_SHEEP_TOUCH_OFFSET', 'V10_4_SHEEP_LANES')
    html = html.replace('Maker v10.3', 'Maker v10.4').replace('MAKER v10.3', 'MAKER v10.4')
    html = html.replace("version:'v10.3'", "version:'v10.4'").replace('version:10.3', 'version:10.4')
    html = html.replace('§E v10.3 Tools', '§E v10.4 Tools')
    html = html.replace('v10.3 · SHEEP TAG · TOUCH PLACEMENT OFFSET', 'v10.4 · SHEEP TAG · HOUSE LANES AND UNIT TRAFFIC')
    html = html.replace('§wyrl§ Engine v10.3 · Sheep Tag placement above the finger', '§wyrl§ Engine v10.4 · Sheep Tag house lanes and unit traffic')
    return html
