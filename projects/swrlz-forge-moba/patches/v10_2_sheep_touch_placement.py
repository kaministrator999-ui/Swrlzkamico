"""Sheep building double-tap selection and a true ground placement footprint."""
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Sheep touch/placement anchor missing or ambiguous: ' + old[:90]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    modules = ['sheep_touch_selection.js', 'sheep_placement_grid.js']
    js = '\n'.join((root / 'runtime' / name).read_text() for name in modules)
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, 'V10_1_SHEEP_TAG_ARCHIVE', 'V10_2_SHEEP_TOUCH_PLACEMENT')
    html = html.replace('Maker v10.1', 'Maker v10.2').replace('MAKER v10.1', 'MAKER v10.2')
    html = html.replace("version:'v10.1'", "version:'v10.2'").replace('version:10.1', 'version:10.2')
    html = html.replace('§E v10.1 Tools', '§E v10.2 Tools')
    html = html.replace('v10.1 · SHEEP TAG ARCHIVE · MOONBELL MEADOW',
                        'v10.2 · SHEEP TAG · TOUCH AND PLACEMENT')
    html = html.replace('§wyrl§ Engine v10.1 · tactical Sheep Tag and native map creator',
                        '§wyrl§ Engine v10.2 · Sheep Tag touch selection and ground placement')
    return html
