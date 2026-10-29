"""Refine the natural-grip mage staff with socket-attached ornamentation."""
from pathlib import Path


def apply(html):
    root = Path(__file__).resolve().parent.parent
    anchor = "window.SWRLZ_FORGE_BUILD={version:'v9.6'"
    assert html.count(anchor) == 1
    js = (root / 'runtime/anime_staff_ornament.js').read_text(encoding='utf-8')
    html = html.replace(anchor, js + '\n' + anchor, 1)
    assert html.count('V9_6_NATURAL_STAFF_PAINTED_FACES') == 1
    html = html.replace('V9_6_NATURAL_STAFF_PAINTED_FACES', 'V9_7_ORNATE_MAGE_STAFF')
    html = html.replace('Maker v9.6', 'Maker v9.7').replace('MAKER v9.6', 'MAKER v9.7')
    html = html.replace("version:'v9.6'", "version:'v9.7'").replace('version:9.6', 'version:9.7')
    html = html.replace('\u00a7E v9.6 Tools', '\u00a7E v9.7 Tools')
    html = html.replace('v9.6 \u00b7 NATURAL STAFF GRIP \u00b7 PAINTED FACES',
                        'v9.7 \u00b7 ORNATE MAGE STAFF \u00b7 PAPER THEATRE')
    html = html.replace('\u00a7wyrl\u00a7 Engine v9.6 \u00b7 natural staff grip and animated painted faces',
                        '\u00a7wyrl\u00a7 Engine v9.7 \u00b7 ornate mage staff and animated paper theatre')
    return html
