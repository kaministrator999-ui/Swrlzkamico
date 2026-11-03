"""§E v11.242 · independent Particle Studio mobile chrome and compact controls.

Only display/mount changes; original game scene, renderer, VFX data,
host approval, native actions, Quest Play, and project persistence untouched.
"""
from pathlib import Path
import json


def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise AssertionError(("v11.242 single source anchor", label, count, old[:110]))
    return text.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parents[1]
    css = (root / "runtime/particle_studio_mobile_layout_v11_242.css").read_text(encoding="utf8")
    js = (root / "runtime/particle_studio_mobile_layout_v11_242.js").read_text(encoding="utf8")
    for key in (
        'function se223UISection(title)',
        'function se225Hide(clearRoute=false)',
        'window.SWYRL_ENGINE_PARTICLE_STAGE_240',
        'window.SWYRL_ENGINE_STUDIOS=Object.freeze',
        'window.SWRLZ_FORGE_BUILD=',
        'SWYRL_ENGINE_DEPLOY_MARKER: V11_241_SHEEP_GRASS_PBR',
    ):
        if key not in html:
            raise AssertionError(("v11.242 missing prerequisite", key))
    html = once(html, '</head>',
                '<style id="se242ParticleLayout">\n' + css + '\n</style>\n</head>',
                "mobile isolation CSS")
    html = once(html,
        'function se223UISection(title){\n const node=document.createElement(\'details\');node.className=\'se223-section\';node.open=true;',
        'function se223UISection(title){\n const node=document.createElement(\'details\');node.className=\'se223-section\';node.open=title===\'Emitter & spawn\';',
        "only first inspector section initially expanded")
    html = once(html,
        'function se225Hide(clearRoute=false){\n',
        'function se225Hide(clearRoute=false){\n delete document.body.dataset.se242InspectorOpen;\n',
        "reset inspector size after studio exit")
    html = once(html, 'window.SWRLZ_FORGE_BUILD=', js + '\nwindow.SWRLZ_FORGE_BUILD=',
                "mobile inspector button controller")

    before = " source.engine='§wyrl§ Engine · Maker v11.241';source.version=11.241;"
    if html.count(before) != 2:
        raise AssertionError(("v11.242 source provenance", html.count(before)))
    html = html.replace(before,
                        " source.engine='§wyrl§ Engine · Maker v11.242';source.version=11.242;")
    for previous, current in (
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_241_SHEEP_GRASS_PBR',
         'SWYRL_ENGINE_DEPLOY_MARKER: V11_242_PARTICLE_MOBILE_LAYOUT'),
        ('ENGINE · MAKER v11.241', 'ENGINE · MAKER v11.242'),
        ('v11.241 · Sheep Tag full grass material', 'v11.242 · Particle Studio mobile workspace cleanup'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.241'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.242'"),
        ('<title>§wyrl§ Engine · Maker v11.241</title>',
         '<title>§wyrl§ Engine · Maker v11.242</title>'),
    ):
        html = once(html, previous, current, "version marker")
    key = 'const SE_RELEASE_NOTES='
    at = html.index(key) + len(key)
    notes, width = json.JSONDecoder().raw_decode(html[at:])
    notes.update(
        title="Standalone Particle Studio mobile UI and tidy editor chrome",
        date="2026-11-03",
        changes=[
            "Hide the actual Game Engine .app > .workspace > .panel world outliner and secondary game controls while Particle or Material Studio is active. Keep the underlying project and renderer untouched.",
            "Use a mobile-height 3D effects preview plus a scrollable compact Particle Studio inspector. The inspector can expand for detailed editing and collapse back without losing state.",
            "Open only the basic Emitter & spawn section by default; retain the full motion, appearance, location, actor-attachment, import/export and native Undo controls in collapsible sections.",
            "Preserve v11.240 single-renderer test chamber, v11.241 ground visuals, native §C preview approval, Quest play mappings and saved scene data.",
            "Phone and Quest Browser owner acceptance remains outstanding."
        ])
    return html[:at] + json.dumps(notes, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + html[at + width:]
