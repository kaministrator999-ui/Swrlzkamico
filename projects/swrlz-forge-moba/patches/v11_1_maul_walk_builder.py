"""§E v11.1: scoped, walked builder construction on the current Frostveil map.

Append-only after v11.0. Published maps, rules, art, and earlier patches remain intact.
"""
from pathlib import Path


def once(source, old, new):
    assert source.count(old) == 1, 'Frostveil walk-build integration anchor missing or ambiguous: ' + old[:90]
    return source.replace(old, new, 1)


def apply(html):
    root=Path(__file__).resolve().parent.parent
    modules='\n'.join((root / 'runtime' / name).read_text(encoding='utf-8')
                      for name in ('maul_builder_core.js','maul_builder_integration.js'))
    html=once(html,'window.SWRLZ_FORGE_BUILD=','// MAUL_WALK_BUILDER_MODULE_BEGIN\n'+modules+'\nwindow.SWRLZ_FORGE_BUILD=')
    html=once(html,'V11_0_RUN_REPLAY_QUALITY','V11_1_MAUL_WALK_BUILDER')
    html=html.replace('Maker v11.0','Maker v11.1').replace('MAKER v11.0','MAKER v11.1')
    html=html.replace("version:'v11.0'","version:'v11.1'").replace('version:11.0','version:11.1')
    html=html.replace('§E v11.0 Tools','§E v11.1 Tools')
    html=html.replace('v11.0 · LOSSLESS RUN EXPORT · MAUL SPECTATOR','v11.1 · FROSTVEIL BUILDERS · PROTECTED ENTRANCES')
    html=html.replace('§wyrl§ Engine v11.0 · Recorder and Maul spectator improvements',
                      '§wyrl§ Engine v11.1 · Builder construction and protected spawns')
    return html
