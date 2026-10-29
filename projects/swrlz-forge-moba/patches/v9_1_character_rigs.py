"""Articulated paper characters, portable poses and native facial controls."""
import json
import re
from pathlib import Path

def apply(html):
    root = Path(__file__).resolve().parent.parent
    runtime = root / 'runtime'
    js = '\n'.join((runtime / name).read_text(encoding='utf-8') for name in
                   ('anime_rig_model.js', 'anime_socket_model.js', 'anime_rig_renderer.js', 'anime_rig_editor.js', 'anime_socket_editor.js'))
    anchor = "window.SWRLZ_FORGE_BUILD={version:'v9.0'"
    assert html.count(anchor) == 1
    html = html.replace(anchor, js + '\n' + anchor, 1)
    css = '\n'.join((runtime / name).read_text(encoding='utf-8') for name in ('anime_rig_editor.css', 'anime_socket_editor.css'))
    html = html.replace('<script type="module">', '<style id="characterRigStyles">'+css+'</style>\n<script type="module">', 1)
    scene = root / 'scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert data['project']['animeRigs']['schema'] == 'anime-character-rigs-v1'
        assert set(data['project']['animeRigs']['characters']) == {'kami', 'swyrlz'}
        encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n', lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n', html, count=1)
        assert count == 1
    html = html.replace('V9_0_AUTHORED_PAPER_THEATRE', 'V9_1_ARTICULATED_PAPER_RIGS')
    html = html.replace('Maker v9.0', 'Maker v9.1').replace('MAKER v9.0', 'MAKER v9.1')
    html = html.replace("version:'v9.0'", "version:'v9.1'").replace('version:9.0', 'version:9.1')
    html = html.replace('§E v9.0 Tools', '§E v9.1 Tools')
    html = html.replace('v9.0 · ANIMATION STUDIO · PAPER THEATRE', 'v9.1 · CHARACTER RIGS · PAPER THEATRE')
    html = html.replace('§wyrl§ Engine v9.0 · saved animation tracks and illustrated paper theatre', '§wyrl§ Engine v9.1 · articulated paper characters and facial animation')
    return html
