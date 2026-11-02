"""§E v11.218: match the owner's glowing glove concept in native geometry.

Append-only, new-floating-hand-starter-only change; no saved-project migration,
VR controller, Sheep Tag, shared rendering, or unrelated project mutation.
"""
from pathlib import Path
import json


def once(html, old, new):
    count = html.count(old)
    if count != 1:
        raise AssertionError(("v11.218 anchored glove edit", old[:140], count))
    return html.replace(old, new, 1)


def apply(html):
    root = Path(__file__).resolve().parents[1]
    addon = (root / "runtime/model_atelier_hand_fidelity_v11_218.js").read_text(encoding="utf8")
    html = once(html, "const se212Id='floating-hand-glove';",
                addon + "\nconst se212Id='floating-hand-glove';")
    html = once(html, " const digit=se217FingerSpec;", " const digit=se218FingerSpec;")
    html = once(html,
                " se217HandAnatomicalTrim({digits:digit,wire,sphere,color});",
                " se217HandAnatomicalTrim({digits:digit,wire,sphere,color});\n"
                " se218HandDetails({digits:digit,wire,sphere,color});")

    # Replace old dangling purple thumb seam with the physically wrapped
    # helix. Existing native thumb anatomy and original joints are preserved.
    html = once(html,
                " wire('Thumb · luminescent seam',\n"
                "  [[-.72,1.64,-.235],[-.96,1.91,-.086],[-1.19,2.13,-.021]],.017,color.accent,'emissive','Thumb / armor');\n",
                " // Thumb line replaced by anchored native double helix in v11.218.\n")
    html = once(html,
                " const color={glove:'#181520',seam:'#383043',plate:'#4a425b',rim:'#b0a7bf',\n"
                "  accent:'#a439ec',light:'#e091ff',core:'#56217e',void:'#0b0b17'};",
                " const color={glove:'#0b1425',seam:'#303a54',plate:'#17253c',rim:'#a7b8d0',\n"
                "  accent:'#c348f3',light:'#f39bff',core:'#522280',void:'#0a1124'};")
    html = once(html,
                " source.engine='§wyrl§ Engine · Maker v11.212';source.version=11.212;",
                " source.engine='§wyrl§ Engine · Maker v11.218';source.version=11.218;")
    for old, new in [
        ('SWYRL_ENGINE_DEPLOY_MARKER: V11_217_HAND_FINGER_PALM_PROPORTIONS',
         'SWYRL_ENGINE_DEPLOY_MARKER: V11_218_ARCANE_GLOVE_FIDELITY'),
        ('ENGINE · MAKER v11.217', 'ENGINE · MAKER v11.218'),
        ('v11.217 · Floating Hand finger and outer-palm proportions',
         'v11.218 · Arcane Glove concept details and thumb helix'),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.217'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.218'"),
        ('<title>§wyrl§ Engine · Maker v11.217</title>',
         '<title>§wyrl§ Engine · Maker v11.218</title>')
    ]:
        html = once(html, old, new)
    key = 'const SE_RELEASE_NOTES='
    start = html.index(key) + len(key)
    notes, n = json.JSONDecoder().raw_decode(html[start:])
    notes.update(title='Arcane Glove: thumb double helix and anchored conduits',
                 date='2026-11-02', changes=[
        'Matched the owner-approved sci-fi glove concept using separately editable native geometry. Extended proportional index, middle, ring and pinky phalanges slightly while keeping anatomical length order and tapered tips.',
        'Replaced the floating purple thumb beam with a continuous two-turn XYZ spiral that wraps the curved thumb from the back of its dorsal saddle to a metallic glowing back-of-tip terminal. Mechanical retention bands and a real dorsal feed socket anchor it to the glove.',
        'Added per-finger metal retaining straps, fingertip settings, backhand cable harnesses and bolted connection points. Added a recessed diamond frame and subtle luminous wrist clasps. Refreshed glove palette to blue-black, silver and bright lilac.',
        'All parts are native editable Model Atelier topology meshes and components. No image plane, external download, fabricated rig or motion. Existing saved projects and VR/Sheep/editor behavior remain unchanged.',
        'Small build/syntax/source receipt checks; phone and Quest owner visual testing remain the acceptance gate.'
    ])
    return html[:start] + json.dumps(notes, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + html[start+n:]
