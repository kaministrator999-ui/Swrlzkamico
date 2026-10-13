"""Append a separate native Wintermaul Wars arena and local Tower Wars mode."""
import json
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Wars anchor missing or ambiguous: ' + old[:100]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    source = root / 'scenes/maul-wars-frostveil.swyrl.json'
    canonical = json.loads(source.read_text()) if source.exists() else None
    js = 'const WARS_CANONICAL_PROJECT=' + json.dumps(canonical, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';\n'
    js += '\n'.join((root / 'runtime' / name).read_text() for name in ('maul_wars_core.js', 'maul_wars_visuals.js', 'maul_wars_ui.js', 'maul_wars_integration.js'))
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, '\n<script type="module">\n', '<style id="warsStyles">\n' + (root / 'runtime/maul_wars_ui.css').read_text() + '\n</style>\n<script type="module">\n')
    html = once(html, '  if(MAUL_TYPES.includes(type))o=maulPrefab(type,[0,0,0],false);', '  if(WARS_TYPES.includes(type))o=warsPrefab(type,[0,0,0],false);\n  if(MAUL_TYPES.includes(type))o=maulPrefab(type,[0,0,0],false);')
    html = once(html, '  if(MAUL_TYPES.includes(d.type))o=maulPrefab(d.type,d.position,d.baked!==false,d.name);', '  if(WARS_TYPES.includes(d.type))o=warsPrefab(d.type,d.position,d.baked!==false,d.name);\n  if(MAUL_TYPES.includes(d.type))o=maulPrefab(d.type,d.position,d.baked!==false,d.name);')
    html = once(html, "else if(template==='maul-frostveil')maulLoadStarter();else loadCanonicalGlitchDen();", "else if(template==='maul-frostveil')maulLoadStarter();else if(template==='maul-wars-frostveil')warsLoadStarter();else loadCanonicalGlitchDen();")
    html = once(html, "else if(new URLSearchParams(location.search).get('project')==='maul-frostveil')maulLoadStarter();else loadCanonicalGlitchDen();", "else if(new URLSearchParams(location.search).get('project')==='maul-frostveil')maulLoadStarter();else if(new URLSearchParams(location.search).get('project')==='maul-wars-frostveil')warsLoadStarter();else loadCanonicalGlitchDen();")
    card = '<button class="project-card den" data-project-template="maul-wars-frostveil"><span class="project-icon">❄️</span><strong>Wintermaul Wars · Frostveil Divide</strong><span class="template-tag">TWO TEAMS · THREE BUILDERS EACH</span><p>Mirrored snowy lanes, raised sender islands, cliff turns and team ships. Maze your defenses, send creeps and grow income against a local opposing team.</p><span class="hint den-glow">Open Wintermaul Wars</span></button>'
    html = once(html, '<button class="project-card den" data-project-template="maul-frostveil">', card + '<button class="project-card den" data-project-template="maul-frostveil">')
    html = once(html, 'stRunInstallUI();maulInstallUI();refreshAssetList();', 'stRunInstallUI();maulInstallUI();warsInstallUI();refreshAssetList();')
    html = once(html, "if(currentProject.kind==='maul')maulUpdate(dt);", "if(currentProject.kind==='maul')maulUpdate(dt);\n    if(currentProject.kind==='maul-wars')warsUpdate(dt);")
    html = once(html, "if(playing&&currentProject.kind!=='maul'){updateHero(dt,t);updateTeleportRecovery(t);}", "if(playing&&!['maul','maul-wars'].includes(currentProject.kind)){updateHero(dt,t);updateTeleportRecovery(t);}")
    html = once(html, 'maulAfterView();stRunAfterTick(dt);', 'maulAfterView();warsAfterView();stRunAfterTick(dt);')
    html = once(html, "    const entities=Object.values(state.entities),follow=get('stRunObserver').value;", "    if(state.game?.kind==='maul-wars'){const game=state.game;lines.push('North '+(game.teams?.[0]?.lives??'?')+' lives; South '+(game.teams?.[1]?.lives??'?')+' lives.');if([0,1].includes(game.winner))lines.push('Winner: '+(game.winner===0?'North':'South')+'.');lines.push('Builder wallets: '+(game.players||[]).map(p=>'player '+(p.id+1)+' '+Math.floor(p.gold)+' gold / '+p.income+' income').join('; ')+'.');}\n    const entities=Object.values(state.entities),follow=get('stRunObserver').value;")
    html = once(html, '  buildMaul:()=>maulLoadStarter(),', '  buildMaul:()=>maulLoadStarter(),\n  buildMaulWars:()=>warsLoadStarter(),\n  configureMaulWars:(rules)=>warsConfigureRules(rules),')
    html = html.replace("(currentProject.kind==='maul'?38:", "(currentProject.kind==='maul-wars'?52:currentProject.kind==='maul'?38:").replace("(currentProject.kind==='maul'?42:", "(currentProject.kind==='maul-wars'?56:currentProject.kind==='maul'?42:")
    html = once(html, "  }else if(currentProject.kind==='maul'){\n    const result=maulAuthoredMap();", "  }else if(currentProject.kind==='maul-wars'){\n    const result=warsAuthoredMap();issues.push(...result.errors);\n  }else if(currentProject.kind==='maul'){\n    const result=maulAuthoredMap();")
    html = once(html, "if(currentProject.kind==='maul')maulFrameMap();editorLog", "if(currentProject.kind==='maul')maulFrameMap();if(currentProject.kind==='maul-wars')warsFrameMap();editorLog")
    html = once(html, "starterModes:['workspace','anime','moba','sheep-tag','maul']", "starterModes:['workspace','anime','moba','sheep-tag','maul','maul-wars']")
    html = once(html, 'V10_6_MAUL_TOWER_DEFENSE', 'V10_7_WINTERMAUL_WARS')
    html = html.replace('Maker v10.6', 'Maker v10.7').replace('MAKER v10.6', 'MAKER v10.7')
    html = html.replace("version:'v10.6'", "version:'v10.7'").replace('version:10.6', 'version:10.7').replace('§E v10.6 Tools', '§E v10.7 Tools')
    html = html.replace('v10.6 · FROSTVEIL MAUL · MAZE TOWER DEFENSE', 'v10.7 · WINTERMAUL WARS · FROSTVEIL DIVIDE')
    html = html.replace('§wyrl§ Engine v10.6 · Frostveil Maul tower defense', '§wyrl§ Engine v10.7 · Wintermaul Wars')
    return html
