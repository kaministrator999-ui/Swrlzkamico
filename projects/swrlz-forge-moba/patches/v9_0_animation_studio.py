"""Reusable saved animation authoring and native illustrated paper-stage actors."""
import json
import re
from pathlib import Path

def once(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError('v9.0 integration anchor mismatch: ' + old[:100])
    return source.replace(old, new, 1)

def apply(html):
    root = Path(__file__).resolve().parent.parent
    runtime = root / 'runtime'
    css = (runtime / 'anime_editor.css').read_text(encoding='utf-8')
    css += (runtime / 'anime_stage.css').read_text(encoding='utf-8')
    js = '\n'.join((runtime / name).read_text(encoding='utf-8') for name in
        ('anime_timeline.js', 'anime_stage.js', 'anime_editor.js'))
    assert '<script type="module">' in html
    result = html.replace('<script type="module">', '<style id="storyStudioStyles">'+css+'</style>\n<script type="module">',1)
    result = once(result, "window.SWRLZ_FORGE_BUILD={version:'v8.9'", js+"\nwindow.SWRLZ_FORGE_BUILD={version:'v8.9'")
    result = once(result, 'installAnimeStarterUI();animeDirectorInstall();refreshAssetList();',
        'installAnimeStarterUI();animeDirectorInstall();storyEditorInstall();refreshAssetList();')
    # Replace the historical iframe's default Watch action, not the entire
    # preserved original screening implementation. Keep the same scoped button.
    result = once(result, "button.type='button';button.textContent='▶ Watch Episode 01';button.hidden=true;",
        "button.type='button';button.textContent='▶ Watch 2.5D Episode 01';button.hidden=true;")
    result = once(result, "button.addEventListener('click',openAnimeScreening);",
        "button.addEventListener('click',storyWatchNativeEpisode);")
    # Legacy 62-actor studio source remains preserved. The new canonical package
    # is the actual native editor export, with saved visual actors and tracks.
    scene = root / 'scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert data['project']['canonicalId'] == 'ghosts-different-forms-ep01'
        assert data['project']['animeTimeline']['schema'] == 'anime-timeline-v1'
        assert len([a for a in data['scene']['actors'] if a['type'] in ('animeCel','animeBook')]) == 8
        # Keep the original 62-actor prototype editable, but its three
        # production layers must be hidden in the authored paper theatre.
        legacy = {'layer-ep-sets', 'layer-ep-fx', 'layer-ep-cast'}
        layers = {layer['id']: layer for layer in data['editor']['layers']}
        assert all(layers[layer]['visible'] is False for layer in legacy)
        assert all(layers['anime-layer-'+layer]['visible'] is True for layer in
                   ('background','atmosphere','midground','kami','swyrlz','effects','foreground','book'))
        assert data['editor']['activeLayerId'] == 'anime-layer-kami'
        encoded = json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
        result,count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n',lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n',result,count=1)
        assert count == 1
    result = once(result, 'V8_9_CINEMATIC_STAGING_SAFE', 'V9_0_AUTHORED_PAPER_THEATRE')
    result = result.replace('Maker v8.9','Maker v9.0').replace('MAKER v8.9','MAKER v9.0')
    result = result.replace("version:'v8.9'","version:'v9.0'").replace('version:8.9','version:9.0')
    result = result.replace('§E v8.9 Tools','§E v9.0 Tools')
    result = result.replace('v8.9 · SAFE CINEMATIC POP-UP STAGING','v9.0 · ANIMATION STUDIO · PAPER THEATRE')
    result = result.replace('§wyrl§ Engine v8.9 · camera-safe 3D pop-up storybook cinema',
        '§wyrl§ Engine v9.0 · saved animation tracks and illustrated paper theatre')
    return result
