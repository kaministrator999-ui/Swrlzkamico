"""Aligned anime faces and independently authored 2.5D scenery cutouts."""
import json
import re
from pathlib import Path

def apply(html):
    root = Path(__file__).resolve().parent.parent
    runtime = root / 'runtime'
    js = '\n'.join((runtime / name).read_text(encoding='utf-8') for name in
                   ('anime_scenery_model.js', 'anime_scenery_renderer.js', 'anime_scenery_editor.js'))
    anchor = "window.SWRLZ_FORGE_BUILD={version:'v9.1'"
    assert html.count(anchor) == 1
    html = html.replace(anchor, js+'\n'+anchor, 1)
    css = (runtime / 'anime_scenery_editor.css').read_text(encoding='utf-8')
    html = html.replace('<script type="module">', '<style id="sceneryDepthStyles">'+css+'</style>\n<script type="module">', 1)
    scene = root / 'scenes/ghosts-in-different-forms-ep01-depth.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert data['project']['animeScenery']['schema'] == 'anime-scenery-v1'
        assert len(data['project']['animeScenery']['objects']) == 34
        encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n', lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n', html, count=1)
        assert count == 1
    html = html.replace('V9_1_ARTICULATED_PAPER_RIGS', 'V9_2_LAYERED_SCENERY_FACES')
    html = html.replace('Maker v9.1', 'Maker v9.2').replace('MAKER v9.1', 'MAKER v9.2')
    html = html.replace("version:'v9.1'", "version:'v9.2'").replace('version:9.1', 'version:9.2')
    html = html.replace('§E v9.1 Tools', '§E v9.2 Tools')
    html = html.replace('v9.1 · CHARACTER RIGS · PAPER THEATRE', 'v9.2 · LAYERED SCENERY · PAPER THEATRE')
    html = html.replace('§wyrl§ Engine v9.1 · articulated paper characters and facial animation', '§wyrl§ Engine v9.2 · layered scenery and aligned anime faces')
    return html
