"""Character-specific fitted body pieces and native rest-layout authoring."""
import json
import re
from pathlib import Path

def apply(html):
    root = Path(__file__).resolve().parent.parent
    scene = root / 'scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json'
    if scene.exists():
        data = json.loads(scene.read_text(encoding='utf-8'))
        assert all('layout' in c for c in data['project']['animeRigs']['characters'].values())
        encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n', lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT='+encoded+';\n', html, count=1)
        assert count == 1
    html = html.replace('V9_2_LAYERED_SCENERY_FACES', 'V9_3_CONNECTED_CHARACTER_PIECES')
    html = html.replace('Maker v9.2', 'Maker v9.3').replace('MAKER v9.2', 'MAKER v9.3')
    html = html.replace("version:'v9.2'", "version:'v9.3'").replace('version:9.2', 'version:9.3')
    html = html.replace('§E v9.2 Tools', '§E v9.3 Tools')
    html = html.replace('v9.2 · LAYERED SCENERY · PAPER THEATRE', 'v9.3 · CONNECTED CHARACTERS · PAPER THEATRE')
    html = html.replace('§wyrl§ Engine v9.2 · layered scenery and aligned anime faces', '§wyrl§ Engine v9.3 · connected character pieces and saved body fitting')
    return html
