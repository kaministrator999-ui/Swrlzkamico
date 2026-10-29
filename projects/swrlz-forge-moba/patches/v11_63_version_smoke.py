"""§E v11.63 version-only smoke release atop the sealed v11.62 engine.

Keep every modeling/game/animation feature, the 283-part canonical scene,
and all 43 historical packaged assets unchanged.
"""
import json

OLD = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_62_MOBILE_ADAPTIVE_TOOL_SHEET'
NEW = 'SWYRL_ENGINE_DEPLOY_MARKER: V11_63_VERSION_SMOKE_TEST'
CANONICAL = 'const MODEL_ATELIER_CANONICAL_PROJECT='

def canonical_scene(html):
    assert html.count(CANONICAL) == 1
    data = html.split(CANONICAL, 1)[1]
    _, end = json.JSONDecoder().raw_decode(data)
    return data[:end]

def apply(html):
    original = canonical_scene(html)
    pairs = (
        (OLD, NEW),
        ('ENGINE · MAKER v11.62', 'ENGINE · MAKER v11.63'),
        ('v11.62 · mobile adaptive Model Atelier tools', 'v11.63 · mobile adaptive Model Atelier tools'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.62'", "window.SWRLZ_FORGE_BUILD={version:'v11.63'"),
        ('<title>§wyrl§ Engine · Maker v11.62</title>', '<title>§wyrl§ Engine · Maker v11.63</title>'),
    )
    for before, after in pairs:
        assert html.count(before) == 1, ('Missing or ambiguous label', before, html.count(before))
        html = html.replace(before, after, 1)
    assert canonical_scene(html) == original, 'Canonical model changed in version-only bump'
    assert html.count(NEW) == 1
    assert html.count(OLD) == 0
    return html
