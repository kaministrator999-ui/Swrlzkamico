"""Much larger joystick moved diagonally up/right; larger right-side building and ability icons; seven-minute matches, including saved maps using the old twenty-minute default."""
from pathlib import Path
import json

def once(html,old,new):
    assert html.count(old)==1,(old[:100],html.count(old))
    return html.replace(old,new,1)

def apply(html):
    r=Path(__file__).resolve().parents[1]
    data=json.loads((r/'scenes/sheep-tag-seven-minute-v11-85.swyrl.json').read_text());prefix='const ST_CANONICAL_PROJECT=';start=html.index(prefix)+len(prefix);_,size=json.JSONDecoder().raw_decode(html[start:]);html=html[:start]+json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+html[start+size:]
    html=once(html,"const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-wide-walkways-v11-84.swyrl.json';","const ST_ARCHIVE_SOURCE_SCENE='scenes/sheep-tag-seven-minute-v11-85.swyrl.json';")
    html=once(html,'duration:1200,headstart:30,bounds:40','duration:420,headstart:30,bounds:40')
    at=html.index('</head>');html=html[:at]+'<style id="sheepLargeControls">'+(r/'runtime/sheep_large_controls_v11_85.css').read_text()+'</style>\n'+html[at:]
    html=once(html,'window.SWRLZ_FORGE_BUILD=',(r/'runtime/sheep_seven_minutes_v11_85.js').read_text()+'\nwindow.SWRLZ_FORGE_BUILD=')
    for old,new in [('SWYRL_ENGINE_DEPLOY_MARKER: V11_84_BUILD_RECOVERY_WALKWAYS','SWYRL_ENGINE_DEPLOY_MARKER: V11_85_LARGE_CONTROLS_SEVEN_MINUTES'),('ENGINE · MAKER v11.84','ENGINE · MAKER v11.85'),('v11.84 · reliable building & connected walkways','v11.85 · larger controls & seven-minute matches'),("window.SWRLZ_FORGE_BUILD={version:'v11.84'","window.SWRLZ_FORGE_BUILD={version:'v11.85'"),('<title>§wyrl§ Engine · Maker v11.84</title>','<title>§wyrl§ Engine · Maker v11.85</title>')]:html=once(html,old,new)
    return html
