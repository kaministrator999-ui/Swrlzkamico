"""Grouped minion arrivals, empty builder starts and visible touch placement."""
import json
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Maul batch anchor missing or ambiguous: ' + old[:100]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    project = json.loads((root / 'scenes/maul-frostveil-groups.swyrl.json').read_text())
    js = 'const MAUL_BATCH_CANONICAL_PROJECT=' + json.dumps(project, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';\n'
    js += '\n'.join((root / 'runtime' / name).read_text() for name in ('maul_batch_core.js', 'maul_batch_integration.js'))
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    loop = '    for(let index=0;index<count;index++)for(const spawn of s.map.spawns)s.spawnQueue.push({at:index*s.rules.spawnInterval+(spawn.sector%3)*.035,sector:spawn.sector,spawn:{x:spawn.x,z:spawn.z},air,boss:boss&&index===count-1,index});'
    html = once(html, loop, "    if(s.map?.spawnStyle==='grouped-v1')s.spawnQueue=MAUL_BATCH_CORE.schedule(s,count,air,boss);else\n" + loop)
    html = once(html, "event(s,'wave-started',{wave:s.wave,air,boss,count:s.spawnQueue.length});", "event(s,'wave-started',{wave:s.wave,air,boss,count:s.map?.spawnStyle==='grouped-v1'?MAUL_BATCH_CORE.queued(s):s.spawnQueue.length});")
    html = once(html, 's.waveElapsed+=step;while(s.spawnQueue.length&&s.spawnQueue[0].at<=s.waveElapsed+1e-9)spawnUnit(s,s.spawnQueue.shift());', "s.waveElapsed+=step;if(s.map?.spawnStyle==='grouped-v1')MAUL_BATCH_CORE.spawnDue(s,spawnUnit,event);else while(s.spawnQueue.length&&s.spawnQueue[0].at<=s.waveElapsed+1e-9)spawnUnit(s,s.spawnQueue.shift());")
    html = once(html, 'queued:s.spawnQueue.length,towers:s.towers.length', "queued:s.map?.spawnStyle==='grouped-v1'?MAUL_BATCH_CORE.queued(s):s.spawnQueue.length,towers:s.towers.length")
    html = once(html, 'const towers=[...s.towers,{kind,cx,cz,level:1}],check=preflight(s.map,towers);', "const towers=[...s.towers,{kind,cx,cz,level:1}],check=s.map?.spawnStyle==='grouped-v1'?MAUL_BATCH_CORE.preflight(s.map,towers):preflight(s.map,towers);")
    html = once(html, 'const check=preflight(s.map,s.towers);if(!check.ok)return result(false,\'blocked\'', "const check=s.map?.spawnStyle==='grouped-v1'?MAUL_BATCH_CORE.preflight(s.map,s.towers):preflight(s.map,s.towers);if(!check.ok)return result(false,'blocked'")
    old_allies = "const proposals=[{kind:'arrow',cx:sector.spawn.x-2,cz:sector.maxZ-2},{kind:'storm',cx:sector.spawn.x+2,cz:sector.maxZ-2}];"
    html = once(html, old_allies, "const proposals=s.map?.spawnStyle==='grouped-v1'?MAUL_BATCH_CORE.allyProposals(s,sector,canBuild):[{kind:'arrow',cx:sector.spawn.x-2,cz:sector.maxZ-2},{kind:'storm',cx:sector.spawn.x+2,cz:sector.maxZ-2}];")
    html = once(html, "const active=new Set(['preview','range','routes']);", "const active=new Set(['preview','range','routes',...(MAUL_BATCH_CORE.enabled(maulSession?.map)?['batch-arrivals']:[])]);")
    html = once(html, 'safeBottom=Math.min(safeBottom,(bar?.top||rect.bottom)-16-(touch?80:0));', 'safeBottom=Math.min(safeBottom,(bar?.top||rect.bottom)-16-(touch?maulBatchTouchLift():0));')
    css = '''
#maulBatchPlacementLabel{position:fixed;z-index:5000;pointer-events:none;transform:translate(-50%,-100%);max-width:190px;padding:7px 9px;border:2px solid #00ffd5;border-radius:7px;background:#05232ff5;color:#d7fff7;font:700 11px system-ui;box-shadow:0 2px 12px #000b;text-align:center}
#maulBatchPlacementLabel[data-valid="false"]{border-color:#ff4663;background:#391521f5;color:#ffe4e8}
@media(max-width:620px){.maul-batch-project.maul-batch-placement .maul-selection span,.maul-batch-project.maul-batch-placement .maul-hint{display:none}.maul-batch-project.maul-batch-placement .maul-commandbar{max-height:38%}.maul-batch-project.maul-batch-placement .maul-builds button{min-height:40px!important}.maul-batch-project.maul-batch-placement .maul-feedback:empty,.maul-batch-project.maul-batch-placement .maul-placement:empty{display:none}}
'''
    html = once(html, '</style>\n</head>', css + '\n</style>\n</head>')
    html = once(html, 'V10_7_CLASSIC_MAUL_MAP', 'V10_8_MAUL_BATCH_PLACEMENT')
    html = html.replace('Maker v10.7', 'Maker v10.8').replace('MAKER v10.7', 'MAKER v10.8').replace("version:'v10.7'", "version:'v10.8'").replace('version:10.7', 'version:10.8').replace('§E v10.7 Tools', '§E v10.8 Tools')
    html = html.replace('v10.7 · CLASSIC MAUL · FROSTVEIL COAST', 'v10.8 · FROSTVEIL MAUL · GROUPED ARRIVALS')
    html = html.replace('§wyrl§ Engine v10.7 · Classic Maul terrain', '§wyrl§ Engine v10.8 · Grouped Maul arrivals')
    return html
