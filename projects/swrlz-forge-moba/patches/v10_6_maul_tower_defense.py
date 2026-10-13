"""Separate native Frostveil Maul starter, original models and maze gameplay."""
import json
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Maul anchor missing or ambiguous: ' + old[:100]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    source = root / 'scenes/maul-frostveil.swyrl.json'
    canonical = json.loads(source.read_text()) if source.exists() else None
    js = 'const MAUL_CANONICAL_PROJECT=' + json.dumps(canonical, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';\n'
    js += '\n'.join((root / 'runtime' / name).read_text() for name in ('maul_core.js', 'maul_visuals.js', 'maul_ui.js', 'maul_integration.js'))
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, '\n<script type="module">\n', '<style id="maulStyles">\n' + (root / 'runtime/maul_ui.css').read_text() + '\n</style>\n<script type="module">\n')
    html = once(html, "  if(ST_TYPES.includes(type))o=stPrefab(type,[0,0,0],false);", "  if(MAUL_TYPES.includes(type))o=maulPrefab(type,[0,0,0],false);\n  if(ST_TYPES.includes(type))o=stPrefab(type,[0,0,0],false);")
    html = once(html, "  if(ST_TYPES.includes(d.type))o=stPrefab(d.type,d.position,d.baked!==false,d.name);", "  if(MAUL_TYPES.includes(d.type))o=maulPrefab(d.type,d.position,d.baked!==false,d.name);\n  if(ST_TYPES.includes(d.type))o=stPrefab(d.type,d.position,d.baked!==false,d.name);")
    html = once(html, "else if(template==='sheep-tag-meadow')stLoadStarter();else loadCanonicalGlitchDen();", "else if(template==='sheep-tag-meadow')stLoadStarter();else if(template==='maul-frostveil')maulLoadStarter();else loadCanonicalGlitchDen();")
    html = once(html, "else if(new URLSearchParams(location.search).get('project')==='sheep-tag-meadow')stLoadStarter();else loadCanonicalGlitchDen();", "else if(new URLSearchParams(location.search).get('project')==='sheep-tag-meadow')stLoadStarter();else if(new URLSearchParams(location.search).get('project')==='maul-frostveil')maulLoadStarter();else loadCanonicalGlitchDen();")
    card = '<button class="project-card den" data-project-template="maul-frostveil"><span class="project-icon">🏰</span><strong>Maul · Frostveil Bastion</strong><span class="template-tag">MAZE TOWER DEFENSE STARTER</span><p>Nine connected sectors, thirty waves and a shared final stand. Build tower mazes, slow ground raiders and prepare anti-air defenses.</p><span class="hint den-glow">Open Frostveil Maul</span></button>'
    html = once(html, '<span class="hint den-glow">Open Sheep Tag</span></button>', '<span class="hint den-glow">Open Sheep Tag</span></button>' + card)
    html = once(html, 'storyEditorInstall();stInstallUI();stInstallCreator();stRunInstallUI();refreshAssetList();', 'storyEditorInstall();stInstallUI();stInstallCreator();stRunInstallUI();maulInstallUI();refreshAssetList();')
    html = once(html, "if(currentProject.kind==='sheep-tag')stUpdate(dt,t);", "if(currentProject.kind==='sheep-tag')stUpdate(dt,t);\n    if(currentProject.kind==='maul')maulUpdate(dt);")
    html = once(html, 'if(playing){updateHero(dt,t);updateTeleportRecovery(t);}', "if(playing&&currentProject.kind!=='maul'){updateHero(dt,t);updateTeleportRecovery(t);}")
    html = once(html, 'stRunAfterTick(dt);if(shouldRenderFrame(frameNow))', 'maulAfterView();stRunAfterTick(dt);if(shouldRenderFrame(frameNow))')
    html = once(html, '  buildSheepTag:()=>{stLoadStarter();return true;},', '  buildSheepTag:()=>{stLoadStarter();return true;},\n  buildMaul:()=>maulLoadStarter(),\n  configureMaul:(rules)=>maulConfigureRules(rules),')
    html = html.replace("(currentProject.kind==='sheep-tag'?stRules().bounds:24)", "(currentProject.kind==='maul'?38:currentProject.kind==='sheep-tag'?stRules().bounds:24)").replace("(currentProject.kind==='sheep-tag'?stRules().bounds:20)", "(currentProject.kind==='maul'?42:currentProject.kind==='sheep-tag'?stRules().bounds:20)")
    html = once(html, "  }else if(currentProject.kind==='sheep-tag'){\n    for(const [type,label]", "  }else if(currentProject.kind==='maul'){\n    const result=maulAuthoredMap();issues.push(...result.errors);\n  }else if(currentProject.kind==='sheep-tag'){\n    for(const [type,label]")
    html = once(html, "if(currentProject.kind==='sheep-tag')stFrameMap();editorLog", "if(currentProject.kind==='sheep-tag')stFrameMap();if(currentProject.kind==='maul')maulFrameMap();editorLog")
    html = once(html, "starterModes:['workspace','anime','moba','sheep-tag']", "starterModes:['workspace','anime','moba','sheep-tag','maul'],maulControl:'rts-grid'")
    html = once(html, 'V10_5_SHEEP_RUN_RECORDER', 'V10_6_MAUL_TOWER_DEFENSE')
    html = html.replace('Maker v10.5', 'Maker v10.6').replace('MAKER v10.5', 'MAKER v10.6')
    html = html.replace("version:'v10.5'", "version:'v10.6'").replace('version:10.5', 'version:10.6').replace('§E v10.5 Tools', '§E v10.6 Tools')
    html = html.replace('v10.5 · SHEEP TAG · PLAY RUN RECORDER', 'v10.6 · FROSTVEIL MAUL · MAZE TOWER DEFENSE')
    html = html.replace('§wyrl§ Engine v10.5 · Sheep Tag play-run recorder', '§wyrl§ Engine v10.6 · Frostveil Maul tower defense')
    return html
