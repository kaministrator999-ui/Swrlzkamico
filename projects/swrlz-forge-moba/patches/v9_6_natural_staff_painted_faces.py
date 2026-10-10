"""Natural socketed staff grip and independently animated painted faces."""
import json
import re
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent
    runtime = root / 'runtime'
    anchor = "window.SWRLZ_FORGE_BUILD={version:'v9.5'"
    assert html.count(anchor) == 1
    js = '\n'.join((runtime / name).read_text(encoding='utf-8') for name in
                   ('anime_staff_art.js', 'anime_face_painter.js', 'anime_staff_magic.js'))
    html = html.replace(anchor, js + '\n' + anchor, 1)
    scene = root / 'scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert data['project']['animeSockets']['schema'] == 'anime-rig-sockets-v1'
        assert data['project']['animeRelief']['schema'] == 'anime-character-relief-v1'
        assert 'shaft' in data['project']['animeSockets']['characters']['kami']['parts']['staff']['sockets']
        encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n', lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n', html, count=1)
        assert count == 1
    html = html.replace('V9_5_FITTED_STAFF_CHARACTER_RELIEF', 'V9_6_NATURAL_STAFF_PAINTED_FACES')
    html = html.replace('Maker v9.5', 'Maker v9.6').replace('MAKER v9.5', 'MAKER v9.6')
    html = html.replace("version:'v9.5'", "version:'v9.6'").replace('version:9.5', 'version:9.6')
    html = html.replace('§E v9.5 Tools', '§E v9.6 Tools')
    html = html.replace('v9.5 · FITTED STAFF · RIGHT-FACING GRIP', 'v9.6 · NATURAL STAFF GRIP · PAINTED FACES')
    html = html.replace('v9.5 · COSTUME DEPTH · LIMB SOCKETS', 'v9.6 · NATURAL STAFF GRIP · PAINTED FACES')
    html = html.replace('§wyrl§ Engine v9.5 · fitted staff mount and a viewer-right gripping hand',
                        '§wyrl§ Engine v9.6 · natural staff grip and animated painted faces')
    return html
