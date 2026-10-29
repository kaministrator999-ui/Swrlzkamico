"""Fit the staff's painted shaft mount and the viewer-right gripping hand."""
import json
import re
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent
    scene = root / 'scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert data['project']['animeSockets']['schema'] == 'anime-rig-sockets-v1'
        assert 'shaft' in data['project']['animeSockets']['characters']['kami']['parts']['staff']['sockets']
        encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n', lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n', html, count=1)
        assert count == 1
    assert html.count("window.SWRLZ_FORGE_BUILD={version:'v9.4'") == 1
    html = html.replace('V9_4_SOCKET_PUPPETS_BOOK_EMERGENCE', 'V9_5_FITTED_STAFF_CHARACTER_RELIEF')
    html = html.replace('Maker v9.4', 'Maker v9.5').replace('MAKER v9.4', 'MAKER v9.5')
    html = html.replace("version:'v9.4'", "version:'v9.5'").replace('version:9.4', 'version:9.5')
    html = html.replace('§E v9.4 Tools', '§E v9.5 Tools')
    html = html.replace('v9.4 · LIMB SOCKETS · BOOK OPENING', 'v9.5 · FITTED STAFF · RIGHT-FACING GRIP')
    html = html.replace('§wyrl§ Engine v9.4 · connected limb sockets and a page-anchored book opening', '§wyrl§ Engine v9.5 · fitted staff mount and a viewer-right gripping hand')
    return html
