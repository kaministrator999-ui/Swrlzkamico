"""Reshape the cooperative Maul starter; preserve earlier authored boards."""
import json
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Classic Maul anchor missing or ambiguous: ' + old[:100]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    scene = root / 'scenes/maul-frostveil-classic.swyrl.json'
    canonical = json.loads(scene.read_text()) if scene.exists() else None
    js = 'const MAUL_LAYOUT_CANONICAL_PROJECT=' + json.dumps(canonical, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';\n'
    js += '\n'.join((root / 'runtime' / name).read_text() for name in ('maul_layout_core.js', 'maul_layout_visuals.js', 'maul_layout_integration.js'))
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, '  if(MAUL_TYPES.includes(type))o=maulPrefab(type,[0,0,0],false);', '  if(MAUL_LAYOUT_TYPES.includes(type))o=maulLayoutPrefab(type,[0,0,0],false);\n  if(MAUL_TYPES.includes(type))o=maulPrefab(type,[0,0,0],false);')
    html = once(html, '  if(MAUL_TYPES.includes(d.type))o=maulPrefab(d.type,d.position,d.baked!==false,d.name);', '  if(MAUL_LAYOUT_TYPES.includes(d.type))o=maulLayoutPrefab(d.type,d.position,d.baked!==false,d.name);\n  if(MAUL_TYPES.includes(d.type))o=maulPrefab(d.type,d.position,d.baked!==false,d.name);')
    # These branches affect only the new map. Legacy boards retain their z-ordered
    # route rules; explicit objective progress permits classic inward returns.
    html = once(html, 'function route(map,blocked,start,sector,air=false) {\n    start=cell(start);', "function route(map,blocked,start,sector,air=false,stage=0) {\n    if(map.layout==='classic-v2')return MAUL_LAYOUT_CORE.route(map,blocked,start,sector,air,stage);\n    start=cell(start);")
    html = once(html, '},u.sector);if(!p)return result(false,\'trapped\'', '},u.sector,false,u.stage||0);if(!p)return result(false,\'trapped\'')
    html = once(html, '},u.sector);if(p){u.path=p;', '},u.sector,false,u.stage||0);if(p){u.path=p;')
    html = once(html, 'pathIndex:1,progress:0,remaining:0,alive:true,', "pathIndex:1,...(s.map.layout==='classic-v2'?{stage:0}:{}),progress:0,remaining:0,alive:true,")
    html = once(html, 'u.progress+=distance;budget-=distance;u.pathIndex++;', "u.progress+=distance;budget-=distance;if(s.map.layout==='classic-v2')u.stage=Math.max(u.stage||0,u.path[u.pathIndex].stage||0);u.pathIndex++;")
    old_projection = '      return {x:width/2+r[0]/depth*focal,y:height/2-r[1]/depth*focal,d:depth,scale:focal/depth};'
    new_projection = '''      if(Array.isArray(c.projectionMatrix)&&c.projectionMatrix.length===16){const m=c.projectionMatrix,clipW=m[3]*r[0]+m[7]*r[1]+m[11]*r[2]+m[15];if(clipW<=0)return null;const nx=(m[0]*r[0]+m[4]*r[1]+m[8]*r[2]+m[12])/clipW,ny=(m[1]*r[0]+m[5]*r[1]+m[9]*r[2]+m[13])/clipW;return {x:width/2+nx*viewWidth/2,y:height/2-ny*viewHeight/2,d:depth,scale:Math.abs(m[5])*viewHeight/(2*clipW)};}
      return {x:width/2+r[0]/depth*focal,y:height/2-r[1]/depth*focal,d:depth,scale:focal/depth};'''
    html = once(html, old_projection, new_projection)
    html = once(html, 'V10_6_MAUL_TOWER_DEFENSE', 'V10_7_CLASSIC_MAUL_MAP')
    html = html.replace('Maker v10.6', 'Maker v10.7').replace('MAKER v10.6', 'MAKER v10.7').replace("version:'v10.6'", "version:'v10.7'").replace('version:10.6', 'version:10.7').replace('§E v10.6 Tools', '§E v10.7 Tools')
    html = html.replace('v10.6 · FROSTVEIL MAUL · MAZE TOWER DEFENSE', 'v10.7 · CLASSIC MAUL · FROSTVEIL COAST')
    html = html.replace('§wyrl§ Engine v10.6 · Frostveil Maul tower defense', '§wyrl§ Engine v10.7 · Classic Maul terrain')
    return html
