"""Record native editor Play runs and export a portable spectator review."""
from pathlib import Path


def once(html, old, new):
    assert html.count(old) == 1, 'Play-run recorder anchor missing or ambiguous: ' + old[:90]
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    modules = '\n'.join((root / 'runtime' / name).read_text() for name in
                        ('sheep_run_recorder.js', 'sheep_run_review.js'))
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', modules + '\nwindow.SWRLZ_FORGE_BUILD=')
    html = once(html, 'storyEditorInstall();stInstallUI();stInstallCreator();refreshAssetList();',
                      'storyEditorInstall();stInstallUI();stInstallCreator();stRunInstallUI();refreshAssetList();')
    html = once(html, 'if(shouldRenderFrame(frameNow))renderer.render(scene,camera);',
                      'stRunAfterTick(dt);if(shouldRenderFrame(frameNow))renderer.render(scene,camera);')
    html = once(html, 'V10_4_SHEEP_LANES', 'V10_5_SHEEP_RUN_RECORDER')
    html = html.replace('Maker v10.4', 'Maker v10.5').replace('MAKER v10.4', 'MAKER v10.5')
    html = html.replace("version:'v10.4'", "version:'v10.5'").replace('version:10.4', 'version:10.5')
    html = html.replace('§E v10.4 Tools', '§E v10.5 Tools')
    html = html.replace('v10.4 · SHEEP TAG · HOUSE LANES AND UNIT TRAFFIC',
                        'v10.5 · SHEEP TAG · PLAY RUN RECORDER')
    html = html.replace('§wyrl§ Engine v10.4 · Sheep Tag house lanes and unit traffic',
                        '§wyrl§ Engine v10.5 · Sheep Tag play-run recorder')
    return html
