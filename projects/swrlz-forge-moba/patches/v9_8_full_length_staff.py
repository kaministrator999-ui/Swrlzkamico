"""Replace the wand-shaped prop with an editable, connected full staff."""
import json
import re
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent
    anchor = "window.SWRLZ_FORGE_BUILD={version:'v9.7'"
    assert html.count(anchor) == 1
    js = (root / 'runtime/anime_full_staff.js').read_text(encoding='utf-8')
    html = html.replace(anchor, js + '\n' + anchor, 1)
    scene = root / 'scenes/ghosts-in-different-forms-ep01-full-staff.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert data['project']['animeRigs']['characters']['kami']['staffArt'] == 'painted-full-v1'
        assert data['project']['animeSockets']['schema'] == 'anime-rig-sockets-v1'
        encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n',
                             lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT=' + encoded + ';\n',
                             html, count=1)
        assert count == 1
    assert html.count('V9_7_ORNATE_MAGE_STAFF') == 1
    html = html.replace('V9_7_ORNATE_MAGE_STAFF', 'V9_8_FULL_LENGTH_MAGE_STAFF')
    html = html.replace('Maker v9.7', 'Maker v9.8').replace('MAKER v9.7', 'MAKER v9.8')
    html = html.replace("version:'v9.7'", "version:'v9.8'").replace('version:9.7', 'version:9.8')
    html = html.replace('§E v9.7 Tools', '§E v9.8 Tools')
    html = html.replace('v9.7 · ORNATE MAGE STAFF · PAPER THEATRE',
                        'v9.8 · FULL-LENGTH MAGE STAFF · PAPER THEATRE')
    html = html.replace('§wyrl§ Engine v9.7 · ornate mage staff and animated paper theatre',
                        '§wyrl§ Engine v9.8 · full-length mage staff and animated paper theatre')
    return html
