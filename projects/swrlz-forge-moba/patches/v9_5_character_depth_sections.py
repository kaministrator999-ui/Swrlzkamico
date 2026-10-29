"""Saved three-section costume relief on the socket-connected character rig."""
import json
import re
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent
    runtime = root / 'runtime'
    js = '\n'.join((runtime / name).read_text(encoding='utf-8') for name in
                   ('anime_relief_model.js', 'anime_relief_renderer.js', 'anime_relief_editor.js'))
    anchor = "window.SWRLZ_FORGE_BUILD={version:'v9.5'"
    assert html.count(anchor) == 1
    html = html.replace(anchor, js + '\n' + anchor, 1)
    css = (runtime / 'anime_relief_editor.css').read_text(encoding='utf-8')
    html = html.replace('<script type="module">', '<style id="characterReliefStyles">'+css+'</style>\n<script type="module">', 1)
    scene = root / 'scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert data['project']['animeRelief']['schema'] == 'anime-character-relief-v1'
        encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n', lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n', html, count=1)
        assert count == 1
    html = html.replace('V9_4_SOCKET_PUPPETS_BOOK_EMERGENCE', 'V9_5_FITTED_STAFF_CHARACTER_RELIEF')
    html = html.replace('Maker v9.4', 'Maker v9.5').replace('MAKER v9.4', 'MAKER v9.5')
    html = html.replace("version:'v9.4'", "version:'v9.5'").replace('version:9.4', 'version:9.5')
    html = html.replace('§E v9.4 Tools', '§E v9.5 Tools')
    html = html.replace('v9.4 · LIMB SOCKETS · BOOK OPENING', 'v9.5 · COSTUME DEPTH · LIMB SOCKETS')
    html = html.replace('§wyrl§ Engine v9.4 · connected limb sockets and a page-anchored book opening',
                        '§wyrl§ Engine v9.5 · articulated costume depth sections and connected limb sockets')
    return html
