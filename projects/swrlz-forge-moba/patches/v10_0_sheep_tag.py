"""Native editor-authored Sheep Tag starter and reusable RTS gameplay tools."""
import json
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Sheep Tag anchor missing/ambiguous: ' + old[:90]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    scene_path = root / 'scenes/sheep-tag-meadow.swyrl.json'
    # The empty source is only used while authoring the first native editor save.
    starter = json.loads(scene_path.read_text()) if scene_path.exists() else {
        'project': {'name': 'Sheep Tag · Moonbell Meadow', 'canonicalId': 'sheep-tag-meadow',
                    'template': 'sheep-tag-meadow', 'kind': 'sheep-tag',
                    'environment': 'spatial-workspace'},
        'scene': {'actors': [], 'paths': {}, 'background': '#b5d9db'}, 'editor': {'layers': []}}
    encoded = json.dumps(starter, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
    modules = ['sheep_tag_visuals.js', 'sheep_tag_game.js', 'sheep_tag_ui.js', 'sheep_tag_integration.js']
    js = '\n'.join((root / 'runtime' / file).read_text() for file in modules)
    js = 'const ST_CANONICAL_PROJECT=' + encoded + ';\n' + js
    html = once(html, "window.SWRLZ_FORGE_BUILD={version:'v9.9'", js + "\nwindow.SWRLZ_FORGE_BUILD={version:'v9.9'")
    css = (root / 'runtime/sheep_tag_ui.css').read_text()
    html = once(html, '\n<script type="module">\n', '<style id="sheepTagStyles">\n' + css + '\n</style>\n<script type="module">\n')
    html = once(html, "  if(type==='tower') o = makeTower", "  if(ST_TYPES.includes(type))o=stPrefab(type,[0,0,0],false);\n  if(type==='tower') o = makeTower")
    html = once(html, "  if(d.type==='ground') o = makeGroundActor();", "  if(ST_TYPES.includes(d.type))o=stPrefab(d.type,d.position,d.baked!==false,d.name);\n  if(d.type==='ground') o = makeGroundActor();")
    html = once(html, "else if(template==='anime-ghosts-ep01')loadCanonicalAnimeEpisode();else loadCanonicalGlitchDen();", "else if(template==='anime-ghosts-ep01')loadCanonicalAnimeEpisode();else if(template==='sheep-tag-meadow')stLoadStarter();else loadCanonicalGlitchDen();")
    card = '<button class="project-card den" data-project-template="sheep-tag-meadow"><span class="project-icon">🐑</span><strong>Sheep Tag · Moonbell Meadow</strong><span class="template-tag">RTS SURVIVAL STARTER</span><p>Build farm mazes, outrun wolf hunters, and rescue captured wisps from the central pen. Play either side with computer teammates.</p><span class="hint den-glow">Open Sheep Tag</span></button>'
    html = once(html, '<span class="hint den-glow">Open Anime Studio · Episode 01</span></button>', '<span class="hint den-glow">Open Anime Studio · Episode 01</span></button>' + card)
    html = once(html, "else if(new URLSearchParams(location.search).get('project')==='anime-ghosts-ep01')loadCanonicalAnimeEpisode();else loadCanonicalGlitchDen();", "else if(new URLSearchParams(location.search).get('project')==='anime-ghosts-ep01')loadCanonicalAnimeEpisode();else if(new URLSearchParams(location.search).get('project')==='sheep-tag-meadow')stLoadStarter();else loadCanonicalGlitchDen();")
    html = once(html, 'installAnimeStarterUI();animeDirectorInstall();storyEditorInstall();refreshAssetList();', 'installAnimeStarterUI();animeDirectorInstall();storyEditorInstall();stInstallUI();refreshAssetList();')
    html = once(html, "    if(currentProject.kind==='moba'&&t-lastWave>", "    if(currentProject.kind==='sheep-tag')stUpdate(dt,t);\n    if(currentProject.kind==='moba'&&t-lastWave>")
    html = once(html, 'animeUpdateCinematic(dt);if(shouldRenderFrame(frameNow))', 'animeUpdateCinematic(dt);if(stSession){stUpdateCamera(dt);stRefreshHUD();}if(shouldRenderFrame(frameNow))')
    html = once(html, '  inspectScene:()=>projectData(),', "  inspectScene:()=>projectData(),\n  loadScene:(data)=>{loadProject(structuredClone(data));initializeHistory('Imported native scene');return projectData();},\n  buildSheepTag:()=>{stLoadStarter();return true;},\n  configureSheepTag:(rules)=>stConfigureRules(rules),")
    html = once(html, "if(Math.abs(a.position.x)>24||Math.abs(a.position.z)>20)", "if(Math.abs(a.position.x)>(currentProject.kind==='sheep-tag'?stRules().bounds:24)||Math.abs(a.position.z)>(currentProject.kind==='sheep-tag'?stRules().bounds:20))")
    html = once(html, "  }else if(currentProject.kind==='dragons-den'){\n    if(!actors.some(a=>a.userData.actorType==='hero'))issues.push", "  }else if(currentProject.kind==='sheep-tag'){\n    for(const [type,label] of [['st-sheep','sheep'],['st-wolf','wolf'],['st-pen','Spirit Pen']])if(!actors.some(a=>a.userData.actorType===type&&a.userData.baked&&a.visible!==false))issues.push('Sheep Tag: add and bake a visible '+label);\n  }else if(currentProject.kind==='dragons-den'){\n    if(!actors.some(a=>a.userData.actorType==='hero'))issues.push")
    html = once(html, "setCameraView('perspective');editorLog('§wyrl§ Engine v9.9", "setCameraView('perspective');if(currentProject.kind==='sheep-tag')stFrameMap();editorLog('§wyrl§ Engine v9.9")
    html = once(html, "wispAlpha:'premultiplied-soft'};window.SWYRL_ENGINE_BUILD", "wispAlpha:'premultiplied-soft',sheepTagControl:'rts',starterModes:['workspace','anime','moba','sheep-tag']};window.SWYRL_ENGINE_BUILD")
    html = once(html, 'V9_9_EPISODE_SHUTTLE_CONTROLS', 'V10_0_SHEEP_TAG_STARTER')
    html = html.replace('Maker v9.9', 'Maker v10.0').replace('MAKER v9.9', 'MAKER v10.0')
    html = html.replace("version:'v9.9'", "version:'v10.0'").replace('version:9.9', 'version:10.0')
    html = html.replace("stamp:'2026.10.07'", "stamp:'2026.10.11'")
    html = html.replace('§E v9.9 Tools', '§E v10.0 Tools')
    html = html.replace('v9.9 · EPISODE SHUTTLE CONTROLS · PAPER THEATRE', 'v10.0 · SHEEP TAG · MOONBELL MEADOW')
    html = html.replace('§wyrl§ Engine v9.9 · episode shuttle controls and animated paper theatre', '§wyrl§ Engine v10.0 · Sheep Tag and native editor starters')
    return html
