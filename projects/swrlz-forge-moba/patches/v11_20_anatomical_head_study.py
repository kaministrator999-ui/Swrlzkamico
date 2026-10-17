"""Opt-in native anatomical head/ear study. Preserve predecessor assets and save schemas."""
from pathlib import Path
import json
import re

def once(html, before, after):
    count = html.count(before)
    assert count == 1, ("Expected unique v11.19 injection point", before[:100], count)
    return html.replace(before, after, 1)

def apply(html):
    root = Path(__file__).resolve().parent.parent
    scene = json.loads((root / "scenes/model-atelier-festival-anatomy-v11-20.swyrl.json").read_text(encoding="utf-8"))
    assert len(scene["project"]["modelAtelier"]["parts"]) == 283
    encoded = json.dumps(scene, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pattern = r'const MODEL_ATELIER_CANONICAL_PROJECT=(.*?);\n(?=// §wyrl§ Engine Model Atelier v11.3)'
    found = re.search(pattern, html, re.S)
    assert found, "Missing governed canonical Model Atelier source"
    html = html[:found.start()] + "const MODEL_ATELIER_CANONICAL_PROJECT=" + encoded + ";\n" + html[found.end():]

    module = (root / "runtime/model_atelier_anatomical_v11_20.js").read_text(encoding="utf-8")
    html = once(html, "  function refreshList(){", module + "\n  function refreshList(){")
    html = once(html, "function atelierHDGeometry(p){\n if(!p.hdFinish)return null;",
        "function atelierHDGeometry(p){\n if(p.anatomyStudy)return atelierAnatomicalHead(p);\n"
        " if(p.earStudy)return atelierAnatomicalEar(p);\n if(!p.hdFinish)return null;")
    html = once(html, "  function checkPart(p){", "  function checkPart(p){\n    if(!atelierAnatomyValid(p))return false;")
    html = once(html, "if(key==='kind'){delete p.portraitFinish;",
        "if(key==='kind'){delete p.anatomyStudy;delete p.earStudy;delete p.portraitFinish;")
    html = once(html, "if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head')values.portraitFinish=undefined;",
        "if(p.kind==='sphere'&&values.surfaceStyle!=='portrait-head'){values.portraitFinish=undefined;values.anatomyStudy=undefined;}")
    html = once(html, "atelierReferenceLegRefresh();atelierPortraitRefresh();",
        "atelierReferenceLegRefresh();atelierPortraitRefresh();atelierAnatomyRefresh();")
    html = once(html, "atelierReferenceLegInstall();atelierPortraitInstall();",
        "atelierReferenceLegInstall();atelierPortraitInstall();atelierAnatomyInstall();")
    keys = ("jaw", "malar", "orbit", "nose", "chin", "temple")
    labels = ("Jaw and mandible", "Zygomatic cheeks", "Orbital recesses",
              "Bridge and nose tip", "Soft chin plane", "Temporal contour")
    def input_line(k,label,value):
        return '<label>' + label + '<input id="modelAtelierAnatomy' + k + '" type="number" min="0" max="1" step=".05" value="' + value + '"></label>'
    head = ''.join(input_line(k, lab, ".5") for k,lab in zip(keys, labels))
    ear = ''.join(input_line(k,lab,".6") for k,lab in
                 zip(("helix","concha","lobe"),("Helix rim","Concha bowl","Lobule relief")))
    deck = ('<section id="modelAtelierAnatomyEditor" hidden><h3>Anatomical stylization</h3>'
            '<div id="modelAtelierAnatomyHead"><p>Saved continuous head anatomy, not default SphereGeometry.</p>'
            + head + '<button id="modelAtelierAnatomyHeadApply">Apply anatomical head</button></div>'
            '<div id="modelAtelierAnatomyEar" hidden><p>Shaped outer ear relief.</p>'
            + ear + '<button id="modelAtelierAnatomyEarApply">Apply anatomical ear</button></div>'
            '</section>')
    html = once(html, '<section id="modelAtelierPortraitFinish"', deck + '<section id="modelAtelierPortraitFinish"')
    html = once(html, "v11.19 · portrait & body polish", "v11.20 · anatomical face study")
    html = html.replace("Maker v11.19", "Maker v11.20").replace("MAKER v11.19", "MAKER v11.20")
    html = html.replace("version:'v11.19'", "version:'v11.20'").replace("version:11.19", "version:11.20")
    html = once(html, "SWYRL_ENGINE_DEPLOY_MARKER: V11_19_PORTRAIT_BODY_POLISH",
        "SWYRL_ENGINE_DEPLOY_MARKER: V11_20_ANATOMICAL_FACE_STUDY")
    return html
