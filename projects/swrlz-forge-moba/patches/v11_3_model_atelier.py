"""§wyrl§ Engine v11.3 — scoped native 3D Model Atelier and authored test model.

Append-only after sealed v11.2. Models are original editable data, not
proprietary extracted assets or a change to existing game starter identities.
"""
import json
from pathlib import Path


def once(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError("v11.3 model atelier integration anchor missing/ambiguous: " + old[:100])
    return source.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parent.parent
    project = json.loads((root / "scenes/model-atelier-prism-jester.swyrl.json").read_text(encoding="utf-8"))
    model = project["project"]["modelAtelier"]
    assert project["project"]["canonicalId"] == "model-atelier-prism-jester"
    assert project["project"]["kind"] == "model-atelier"
    assert model["schema"] == "swyrl-model-atelier-v1"
    assert 180 <= len(model["parts"]) <= 400
    assert len(set(p["id"] for p in model["parts"])) == len(model["parts"])
    assert {p["group"] for p in model["parts"]} >= {"Coral flare", "Azure frost", "Character"}
    js = ("const MODEL_ATELIER_CANONICAL_PROJECT="
          + json.dumps(project, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
          + ";\n"
          + (root / "runtime/model_atelier.js").read_text(encoding="utf-8"))
    css = (root / "runtime/model_atelier.css").read_text(encoding="utf-8")
    # The module opener also occurs in preserved demo/template strings; insert
    # the style before the first real module opener as the earlier patches do.
    assert '<script type="module">' in html
    html = html.replace('<script type="module">',
                        '<style id="modelAtelierStyles">' + css + '</style>\n<script type="module">', 1)
    html = once(html, 'window.SWRLZ_FORGE_BUILD=',
                '// MODEL_ATELIER_V11_3_BEGIN\n' + js + '\nwindow.SWRLZ_FORGE_BUILD=')
    card = ('<button class="project-card den" data-project-template="model-atelier">'
            '<span class="project-icon">🎭</span>'
            '<strong>Model Atelier · Prism Jester</strong>'
            '<span class="template-tag">EDITABLE 3D CHARACTER STARTER</span>'
            '<p>Original layered character study with coral and cyan ribbon forms. '
            'Edit individual 3D meshes, materials and transforms; export JSON or OBJ.</p>'
            '<span class="hint den-glow">Open Model Atelier</span></button>')
    anchor = '<span class="hint den-glow">Open Frostveil Maul</span></button>'
    html = once(html, anchor, anchor + card)
    html = once(html, 'V11_2_MAUL_FLIGHT_GLACIAL_ART', 'V11_3_MODEL_ATELIER_PRISM_JESTER')
    html = html.replace('Maker v11.2', 'Maker v11.3').replace('MAKER v11.2', 'MAKER v11.3')
    html = html.replace("version:'v11.2'", "version:'v11.3'").replace('version:11.2', 'version:11.3')
    html = html.replace('§E v11.2 Tools', '§E v11.3 Tools')
    html = html.replace('v11.2 · FLYING BUILDERS · GLACIAL ART',
                        'v11.3 · MODEL ATELIER · ORIGINAL CHARACTER')
    html = html.replace('§wyrl§ Engine v11.2 · Flying builders and glacial map art',
                        '§wyrl§ Engine v11.3 · Model Atelier and editable character study')
    return html
