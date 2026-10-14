"""Editable character actions and a causally staged paper-book episode."""
import json
import re
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent
    files = ['anime_performance_model.js', 'anime_performance_editor.js',
             'anime_story_effects.js', 'anime_story_effects_editor.js']
    js = '\n'.join((root / 'runtime' / name).read_text(encoding='utf-8') for name in files)
    anchor = 'window.SWRLZ_FORGE_BUILD='
    assert html.count(anchor) == 1, 'Ambiguous episode performance integration anchor'
    html = html.replace(anchor, js + '\n' + anchor, 1)
    css = '\n'.join((root / 'runtime' / name).read_text(encoding='utf-8')
                    for name in ['anime_performance_editor.css', 'anime_story_effects_editor.css'])
    assert html.count('</style>\n</head>') == 1
    html = html.replace('</style>\n</head>', css + '\n</style>\n</head>', 1)
    scene = json.loads((root / 'scenes/ghosts-in-different-forms-ep01-performance.swyrl.json').read_text(encoding='utf-8'))
    assert scene['project']['animeRigs']['characters']['kami']['staffArt'] == 'painted-full-v1'
    encoded = json.dumps(scene, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html, count = re.subn(r'const CANONICAL_ANIME_EPISODE_PROJECT=.*?;\n',
                         lambda _: 'const CANONICAL_ANIME_EPISODE_PROJECT=' + encoded + ';\n', html, count=1)
    assert count == 1, 'Missing canonical native episode'
    assert html.count('V10_8_MAUL_BATCH_PLACEMENT') == 1
    html = html.replace('V10_8_MAUL_BATCH_PLACEMENT', 'V10_9_EPISODE_STORY_ACTIONS')
    html = html.replace('Maker v10.8', 'Maker v10.9').replace('MAKER v10.8', 'MAKER v10.9')
    html = html.replace("version:'v10.8'", "version:'v10.9'").replace('version:10.8', 'version:10.9')
    html = html.replace('§E v10.8 Tools', '§E v10.9 Tools')
    html = html.replace('v10.8 · FROSTVEIL MAUL · GROUPED ARRIVALS',
                        'v10.9 · STORY ACTIONS · PAPER THEATRE')
    html = html.replace('§wyrl§ Engine v10.8 · Grouped Maul arrivals',
                        '§wyrl§ Engine v10.9 · Animated story actions')
    return html
