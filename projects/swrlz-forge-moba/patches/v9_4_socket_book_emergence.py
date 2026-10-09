"""Saved limb sockets, visible staff grip and page-anchored book opening."""
import json
import re
from pathlib import Path

def apply(html):
    root = Path(__file__).resolve().parent.parent
    runtime = root / 'runtime'
    js = '\n'.join((runtime / name).read_text(encoding='utf-8') for name in
                   ('anime_emergence.js', 'anime_emergence_editor.js'))
    anchor = "window.SWRLZ_FORGE_BUILD={version:'v9.3'"
    assert html.count(anchor) == 1
    html = html.replace(anchor, js + '\n' + anchor, 1)
    css = (runtime / 'anime_emergence_editor.css').read_text(encoding='utf-8')
    html = html.replace('<script type="module">', '<style id="bookEmergenceStyles">'+css+'</style>\n<script type="module">', 1)
    scene = root / 'scenes/ghosts-in-different-forms-ep01-sockets.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert data['project']['animeSockets']['schema'] == 'anime-rig-sockets-v1'
        assert data['project']['animeEmergence']['schema'] == 'anime-book-emergence-v1'
        encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n', lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n', html, count=1)
        assert count == 1
    html = html.replace('V9_3_CONNECTED_CHARACTER_PIECES', 'V9_4_SOCKET_PUPPETS_BOOK_EMERGENCE')
    html = html.replace('Maker v9.3', 'Maker v9.4').replace('MAKER v9.3', 'MAKER v9.4')
    html = html.replace("version:'v9.3'", "version:'v9.4'").replace('version:9.3', 'version:9.4')
    html = html.replace('§E v9.3 Tools', '§E v9.4 Tools')
    html = html.replace('v9.3 · CONNECTED CHARACTERS · PAPER THEATRE', 'v9.4 · LIMB SOCKETS · BOOK OPENING')
    html = html.replace('§wyrl§ Engine v9.3 · connected character pieces and saved body fitting', '§wyrl§ Engine v9.4 · connected limb sockets and a page-anchored book opening')
    return html
