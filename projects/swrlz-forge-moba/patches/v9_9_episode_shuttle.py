"""Add signed 2x/4x/8x shuttle controls to the native episode transport."""
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent
    anchor = "window.SWRLZ_FORGE_BUILD={version:'v9.8'"
    assert html.count(anchor) == 1
    js = (root / 'runtime/anime_transport.js').read_text(encoding='utf-8')
    css = (root / 'runtime/anime_transport.css').read_text(encoding='utf-8')
    html = html.replace(anchor, js + '\n' + anchor, 1)
    style_anchor = '\n<script type="module">\n'
    assert html.count(style_anchor) == 1
    html = html.replace(style_anchor,
                        '<style id="episodeTransportStyles">\n' + css + '\n</style>\n' + style_anchor, 1)
    assert html.count('V9_8_FULL_LENGTH_MAGE_STAFF') == 1
    html = html.replace('V9_8_FULL_LENGTH_MAGE_STAFF', 'V9_9_EPISODE_SHUTTLE_CONTROLS')
    html = html.replace('Maker v9.8', 'Maker v9.9').replace('MAKER v9.8', 'MAKER v9.9')
    html = html.replace("version:'v9.8'", "version:'v9.9'").replace('version:9.8', 'version:9.9')
    html = html.replace('§E v9.8 Tools', '§E v9.9 Tools')
    html = html.replace('v9.8 · FULL-LENGTH MAGE STAFF · PAPER THEATRE',
                        'v9.9 · EPISODE SHUTTLE CONTROLS · PAPER THEATRE')
    html = html.replace('§wyrl§ Engine v9.8 · full-length mage staff and animated paper theatre',
                        '§wyrl§ Engine v9.9 · episode shuttle controls and animated paper theatre')
    return html
