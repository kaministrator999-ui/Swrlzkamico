"""§E v11.219: fit each of four purple rails to finger dorsal links.

Append-only hand starter geometry correction. Thumb helix, glove anatomy,
backhand harness, saved projects and all game/XR controls are unchanged.
"""
from pathlib import Path
import json

def once(html, old, new):
    occurrences = html.count(old)
    if occurrences != 1:
        raise AssertionError(("v11.219 finger rail anchor", old[:155], occurrences))
    return html.replace(old, new, 1)

def apply(html):
    root = Path(__file__).resolve().parents[1]
    helper = (root / "runtime/model_atelier_finger_rails_v11_219.js").read_text(encoding="utf8")
    html = once(html, "const se212Id='floating-hand-glove';",
                helper + "\nconst se212Id='floating-hand-glove';")

    # Refit the existing SINGLE seam, rather than adding overlay duplicates.
    html = once(html,
        "  wire('Digit '+(i+1)+' · glowing dorsal seam',\n"
        "   [[f.x,f.from+.12,-.187],[f.x+f.splay*.52,(f.from+f.to)*.53,-.160],\n"
        "    [x,y,-.133]],.014,color.accent,'emissive','Fingers / runes');",
        "  wire('Digit '+(i+1)+' · glowing dorsal seam',\n"
        "   se219FingerRailPath(f),.014,color.accent,'emissive','Fingers / runes');")

    # Existing v11.218 retaining straps are placed via the *same* sampled
    # rail function. Their center bridges the purple rail, edges wrap down
    # onto the finger surface, avoiding the detached floating-bow appearance.
    html = once(html,
        "  for(const [j,t] of [.45,.69].entries()){\n"
        "   const h=f.to-f.from,y=f.from+h*t,x=f.x+f.splay*(t*.83);\n"
        "   const z=f.z-f.r*(t>.6?.83:.95)-.026;\n"
        "   wire('Digit '+(i+1)+' · rail retainer '+(j+1),\n"
        "    [[x-f.r*.80,y-.029,z+.019],[x-f.r*.52,y,z-.016],\n"
        "     [x,y+.018,z-.033],[x+f.r*.52,y,z-.016],[x+f.r*.80,y-.029,z+.019]],\n"
        "    .009,metal,'metal','Fingers / harness');\n"
        "   sphere('Digit '+(i+1)+' · retainer '+(j+1)+' center',[x,y+.014,z-.040],\n"
        "    [f.r*.28,.026,.020],color.plate,'metal','Fingers / harness');\n"
        "  }",
        "  for(const [j,t] of [.45,.77].entries()){\n"
        "   const [x,y,railZ]=se219FingerRailPoint(f,t),z=railZ-.010;\n"
        "   wire('Digit '+(i+1)+' · rail retainer '+(j+1),\n"
        "    [[x-f.r*.72,y-.026,z+.043],[x-f.r*.48,y,z-.003],\n"
        "     [x,y+.012,z-.022],[x+f.r*.48,y,z-.003],[x+f.r*.72,y-.026,z+.043]],\n"
        "    .009,metal,'metal','Fingers / harness');\n"
        "   sphere('Digit '+(i+1)+' · retainer '+(j+1)+' center',[x,y+.012,z-.028],\n"
        "    [f.r*.25,.024,.018],color.plate,'metal','Fingers / harness');\n"
        "  }")

    html = once(html,
        " source.engine='§wyrl§ Engine · Maker v11.218';source.version=11.218;",
        " source.engine='§wyrl§ Engine · Maker v11.219';source.version=11.219;")
    for old, new in [
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_218_ARCANE_GLOVE_FIDELITY",
         "SWYRL_ENGINE_DEPLOY_MARKER: V11_219_FINGER_RAIL_CONTACT"),
        ("ENGINE · MAKER v11.218", "ENGINE · MAKER v11.219"),
        ("v11.218 · Arcane Glove concept details and thumb helix",
         "v11.219 · Finger rail alignment under joint links"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.218'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.219'"),
        ("<title>§wyrl§ Engine · Maker v11.218</title>",
         "<title>§wyrl§ Engine · Maker v11.219</title>"),
    ]:
        html = once(html, old, new)

    tag = "const SE_RELEASE_NOTES="
    start = html.index(tag) + len(tag)
    notes, n = json.JSONDecoder().raw_decode(html[start:])
    notes.update(title="Arcane Glove: recessed finger circuits beneath metal links",
                 date="2026-11-02", changes=[
        "Adjusted only the four non-thumb purple finger rails to follow the back of each anatomical tapered finger, from just above the knuckle to the circular tip setting.",
        "Two metallic cross-links on each finger now sample the same rail path and sit over the purple energy conduit instead of being offset from it. Distal link is higher toward the fingertip; links wrap the sides of the finger.",
        "Preserved the thumb's continuous two-turn helix, backhand cables, sigil, palette, hand proportions, and native Model Atelier editing. No extra redundant rails, external texture planes or animations.",
        "Only fresh Floating Hand starter creation changes; no saved model rewrites, Quest controls or Sheep Tag changes. Physical phone visual acceptance by the owner remains pending."
    ])
    return html[:start] + json.dumps(notes, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + html[start+n:]
