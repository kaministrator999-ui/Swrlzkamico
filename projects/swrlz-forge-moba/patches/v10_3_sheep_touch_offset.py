"""Lift touch construction previews above the finger while preserving screen-space placement."""
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Sheep touch offset anchor missing or ambiguous: ' + old[:90]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    js = (root / 'runtime' / 'sheep_touch_offset.js').read_text()
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, 'V10_2_SHEEP_TOUCH_PLACEMENT', 'V10_3_SHEEP_TOUCH_OFFSET')
    html = html.replace('Maker v10.2', 'Maker v10.3').replace('MAKER v10.2', 'MAKER v10.3')
    html = html.replace("version:'v10.2'", "version:'v10.3'").replace('version:10.2', 'version:10.3')
    html = html.replace('§E v10.2 Tools', '§E v10.3 Tools')
    html = html.replace('v10.2 · SHEEP TAG · TOUCH AND PLACEMENT',
                        'v10.3 · SHEEP TAG · TOUCH PLACEMENT OFFSET')
    html = html.replace('§wyrl§ Engine v10.2 · Sheep Tag touch selection and ground placement',
                        '§wyrl§ Engine v10.3 · Sheep Tag placement above the finger')
    return html
